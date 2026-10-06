import json
import re
import statistics
import subprocess
from collections import Counter
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

MODELS = Path(__file__).resolve().parent.parent / "models"
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
# Sobel gradient a drawn webcam border clears and game texture mostly doesn't.
EDGE = 25
# Full-screen camera (talking to chat): the face is ~12% of the frame wide; in a webcam box ~4%.
CAM_FACE = 0.09


def _detector(W: int, H: int):
    # YuNet, not mediapipe's detector: mediapipe's short-range model misses ~90px faces in wide
    # shots and fires on hands, plant pots, belt buckles.
    return cv2.FaceDetectorYN.create(str(MODELS / "face_detection_yunet_2023mar.onnx"), "", (W, H), 0.7)


def _landmarker():
    return vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODELS / "face_landmarker.task")),
        output_face_blendshapes=True,
    ))


def _rgb(frame):
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def frame_size(video: Path) -> tuple[int, int]:
    cap = cv2.VideoCapture(str(video))
    size = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return size


def shot_cuts(video: Path, start: float, end: float) -> list[float]:
    """Clip-relative times where the camera cuts."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(video),
         "-vf", "scdet=threshold=10", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    # The time is the new shot's first frame. A hair earlier, so rounding it for a filter can't leave that
    # frame in the shot before (2026-10-06 test: one frame of the next camera in the old crop at every cut).
    return [float(t) - 0.01 for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", proc.stderr) if float(t) > 0.3]


def _frames(video: Path, start: float, end: float, fps: float, keyframes: bool = False):
    """Frames at a steady rate from one ffmpeg pass. Seeking to each one took 85s for a 25s clip of 60fps AV1.
    `keyframes` decodes only those, which is what makes sampling a whole video quick."""
    W, H = frame_size(video)
    proc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", *(["-skip_frame", "nokey"] if keyframes else []),
         "-ss", f"{start:.2f}", "-t", f"{end - start:.2f}", "-i", str(video), "-vf", f"fps={fps}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while len(raw := proc.stdout.read(W * H * 3)) == W * H * 3:
        yield np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    proc.wait()


def find_faces(video: Path, start: float, end: float) -> list[tuple[int, int, int]]:
    """Median (cx, cy, width) per person, left to right, within one camera shot."""
    W, H = frame_size(video)
    det = _detector(W, H)
    hits, seen = [], 0
    for frame in _frames(video, start, end, max(2, 1 / (end - start))):
        seen += 1
        _, found = det.detect(frame)
        for x, y, w, h, *_ in (found if found is not None else []):
            hits.append((int(x + w / 2), int(y + h / 2), int(w)))
    if not hits:
        return []
    # Faces on posters and book covers behind the hosts are real detections but tiny (run 5).
    # Not the max: one false hit in the gameplay (3x a webcam face) threw out every real one.
    biggest = sorted(w for _, _, w in hits)[int(len(hits) * 0.9)]
    # One person = hits within a face-width of each other, in x and y. Grouping by x alone merged the guest
    # with the framed portraits on the wall beside him and TRACK cropped to the wall (run 13).
    people = []
    for h in sorted(h for h in hits if h[2] >= biggest / 3):
        near = next((p for p in people if abs(h[0] - p[-1][0]) < h[2] and abs(h[1] - p[-1][1]) < h[2]), None)
        if near:
            near.append(h)
        else:
            people.append([h])
    people = [p for p in people if len(p) >= max(1, seen // 3)]
    # A face that doesn't move a pixel for three seconds is a picture, however big it is.
    people = [p for p in people if len(p) < 6 or max(max(v) - min(v) for v in list(zip(*p))[:2]) > 2]
    return sorted(tuple(int(statistics.median(v)) for v in zip(*p)) for p in people)


def speaker_segments(video: Path, start: float, end: float, faces, hold: float = 1.5) -> list[tuple[float, int]]:
    """(clip-relative time, face index) whenever the active speaker changes, by jaw movement."""
    cap = cv2.VideoCapture(str(video))
    lm = _landmarker()
    step = 0.2
    jaw = [[] for _ in faces]
    t = start
    while t < end:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        for i, (cx, cy, w) in enumerate(faces):
            s = int(w * 1.8)
            crop = cv2.resize(frame[max(0, cy - s):cy + s, max(0, cx - s):cx + s], (320, 320))
            r = lm.detect(_rgb(crop))
            score = next((b.score for b in r.face_blendshapes[0] if b.category_name == "jawOpen"), 0.0) \
                if r.face_blendshapes else 0.0
            jaw[i].append(score)
        t += step
    cap.release()

    window = int(1.0 / step)
    segments = [(0.0, 0)]
    for k in range(len(jaw[0])):
        lo = max(0, k - window // 2)
        spread = [statistics.pstdev(j[lo:k + window // 2 + 1]) for j in jaw]
        best = max(range(len(faces)), key=spread.__getitem__)
        current = segments[-1][1]
        now = k * step
        if best != current and spread[best] > 1.5 * spread[current] + 0.005:
            if now - segments[-1][0] >= hold or len(segments) == 1:
                segments.append((now, best))
    if len(segments) > 1 and segments[1][0] < hold:
        segments = [(0.0, segments[1][1])] + segments[2:]
    return segments


LOOK_EVERY = 4.0   # seconds between the frames an episode is searched for close-ups
CLOSE_UP = 0.08    # a face this wide (of the frame) alone in the shot is a close-up; a wide shot's are 0.05-0.07
SAME_FACE = 0.45   # SFace cosine: the same person scores 0.9, different people under 0.2 (2026-10-06 trial)
MIN_LOOKS = 5      # close-up samples needed before a voice gets a face
BACKGROUND = 3     # a face this many times smaller than the one beside it is a photo on the wall
MIN_TURN = 1.0     # a line shorter than this is an interjection: the picture stays where it is
LEAD = 0.12        # the cut lands just before a turn's first word


def _faceprints(detector, recognizer, frame) -> list[tuple[int, int, int, np.ndarray]]:
    """(cx, cy, width, SFace embedding) for every face in a frame."""
    _, found = detector.detect(frame)
    prints = []
    for row in (found if found is not None else []):
        v = recognizer.feature(recognizer.alignCrop(frame, row)).flatten()
        prints.append((int(row[0] + row[2] / 2), int(row[1] + row[3] / 2), int(row[2]), v / np.linalg.norm(v)))
    return prints


def known_faces(video: Path, work: Path, words: list[dict]) -> dict[int, np.ndarray]:
    """Whose face goes with which voice (`speakers.label` numbers), learned from the show's own close-ups: a
    shot of one person while one voice talks is that voice's face. Mouth movement can't make the match, a mic
    hides the talker's mouth (2026-10-06 trial: it put the guest's voice on a laughing host). A voice that
    never gets a close-up has no face here. Worked out once per episode and kept in `faces.json`."""
    cache = work / "faces.json"
    if cache.exists():
        return {int(k): np.array(v) for k, v in json.loads(cache.read_text(encoding="utf-8")).items()}
    W, H = frame_size(video)
    detector = _detector(W, H)
    recognizer = cv2.FaceRecognizerSF.create(str(MODELS / "face_recognition_sface_2021dec.onnx"), "")
    spoken = [w for w in words if w.get("speaker") is not None]
    looks, k = {}, 0
    for n, frame in enumerate(_frames(video, 0, words[-1]["end"], 1 / LOOK_EVERY)):
        t = n * LOOK_EVERY + LOOK_EVERY / 2  # ffmpeg's fps filter hands back the frame from the middle of each step
        while k < len(spoken) and spoken[k]["end"] < t:
            k += 1
        if k == len(spoken):
            break
        if spoken[k]["start"] > t:
            continue
        prints = _faceprints(detector, recognizer, frame)
        big = [p for p in prints if p[2] * BACKGROUND >= max(q[2] for q in prints)]
        if len(big) == 1 and big[0][2] >= W * CLOSE_UP:
            looks.setdefault(spoken[k]["speaker"], []).append(big[0][3])
    faces = {}
    # A close-up sometimes shows a listener, so a voice's face is the one most of its close-ups show: the
    # print with the most look-alikes, and those look-alikes. An average of all of them is a blend of two
    # people once the listener is a third of the shots. And one face can't belong to two voices: it goes to
    # the voice seen with it most.
    for who, seen in sorted(looks.items(), key=lambda item: -len(item[1])):
        seen = np.array(seen)
        alike = seen @ seen.T >= SAME_FACE
        agree = seen[alike[alike.sum(axis=1).argmax()]]
        if len(agree) >= MIN_LOOKS and len(agree) * 2 > len(seen):
            face = agree.mean(axis=0)
            face /= np.linalg.norm(face)
            if all(float(face @ other) < SAME_FACE for other in faces.values()):
                faces[who] = face
    cache.write_text(json.dumps({who: face.tolist() for who, face in faces.items()}), encoding="utf-8")
    return faces


def _who(video: Path, start: float, end: float, faces, known: dict[int, np.ndarray]) -> dict[int, int]:
    """Speaker number -> index into `faces`, for the people in this shot whose face is known."""
    W, H = frame_size(video)
    detector = _detector(W, H)
    recognizer = cv2.FaceRecognizerSF.create(str(MODELS / "face_recognition_sface_2021dec.onnx"), "")
    seen = [[] for _ in faces]
    cap = cv2.VideoCapture(str(video))
    for part in (0.25, 0.5, 0.75):
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + (end - start) * part) * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        for cx, cy, w, v in _faceprints(detector, recognizer, frame):
            near = min(range(len(faces)), key=lambda i: abs(faces[i][0] - cx) + abs(faces[i][1] - cy))
            # Same place and about the same size: a framed photo beside the guest's head is neither.
            if abs(faces[near][0] - cx) < faces[near][2] and abs(faces[near][1] - cy) < faces[near][2] and w * BACKGROUND >= faces[near][2]:
                seen[near].append(v)
    cap.release()
    alike = sorted(((float(np.mean(vs, axis=0) @ face), who, i) for i, vs in enumerate(seen) if vs for who, face in known.items()), reverse=True)
    who_is, taken = {}, set()
    for score, who, i in alike:
        if score >= SAME_FACE and who not in who_is and i not in taken:
            who_is[who] = i
            taken.add(i)
    return who_is


def _follow(video: Path, start: float, a: float, b: float, faces, said, known: dict[int, np.ndarray]) -> list[tuple[float, int]]:
    """(clip time, face index) through one shot of several people: the picture goes to whoever starts a real
    turn and stays put through interjections. A voice that has no face on record is one of the people left
    over: whichever of them moves their jaw most while it talks, one person per voice for the whole shot.
    Empty when no one in the shot is known."""
    who_is = _who(video, start + a, start + b, faces, known)
    if not who_is:
        return []
    turns = []
    for began, ended, who in said:
        if ended <= a or began >= b:
            continue
        if turns and (who is None or who == turns[-1][2]):
            turns[-1][1] = min(ended, b)
        elif who is not None:
            turns.append([max(began, a), min(ended, b), who])
    turns = [turn for turn in turns if turn[1] - turn[0] >= MIN_TURN]
    spare = [i for i in range(len(faces)) if i not in who_is.values()]
    # A voice whose face is on record but not in this shot is off camera; it doesn't get someone else's face.
    faceless = {who for _, _, who in turns if who not in known}
    if len(spare) == 1:
        who_is.update({who: spare[0] for who in faceless})
    elif spare:
        moved = {}
        for began, ended, who in turns:
            if who in faceless:
                held = speaker_segments(video, start + began, start + ended, [faces[i] for i in spare])
                for (since, i), until in zip(held, [since for since, _ in held[1:]] + [ended - began]):
                    moved[who, spare[i]] = moved.get((who, spare[i]), 0) + until - since
        for (who, i), _ in sorted(moved.items(), key=lambda item: -item[1]):
            if who not in who_is and i not in who_is.values():
                who_is[who] = i
    cuts = []
    for began, _, who in turns:
        if who in who_is and (not cuts or cuts[-1][1] != who_is[who]):
            cuts.append((max(began - LEAD, a) if cuts else a, who_is[who]))
    # Nobody with a face here has a real turn in the shot: hold on someone known rather than guess by jaw.
    return cuts or [(a, min(who_is.values()))]


def plan(video: Path, start: float, end: float, solo: bool = False, said: list[tuple] = (),
         known: dict[int, np.ndarray] | None = None) -> tuple[list[tuple[float, tuple | None]], list | None]:
    """TRACK segments as (clip-relative time, face as (cx, cy, width) or None), plus the two faces for SPLIT, or None
    when SPLIT can't work (camera cuts, not exactly two people in the one shot, or faces too small).
    `solo`: one person on camera (a streamer), so TRACK stays on the biggest face; anything else is a poster.
    `said` is (start, end, speaker) per caption word on the clip's clock and `known` is `known_faces`: with
    them a shot of several people follows the voice; without, or when nobody talking has a known face, it
    falls back to jaw movement."""
    W, H = frame_size(video)
    bounds = [0.0, *shot_cuts(video, start, end), end - start]
    segments, shots = [], []
    for a, b in zip(bounds, bounds[1:]):
        faces = find_faces(video, start + a, start + b)
        if solo:
            faces = sorted(faces, key=lambda f: -f[2])[:1]
        # YuNet boxed a guest's clasped hands as a second face and TRACK cut to them on the payoff (2026-10-06
        # test). A box straight under a face is that person's hands or lap. Not a landmark check: it failed
        # on a real face behind a microphone.
        faces = [f for f in faces if not any(abs(f[0] - o[0]) < 1.5 * o[2] and f[1] - o[1] > 1.5 * o[2] for o in faces)]
        shots.append(faces)
        if not faces:
            segments.append((a, None))
        elif len(faces) == 1:
            segments.append((a, faces[0]))
        else:
            heard = _follow(video, start, a, b, faces, said, known) if known else []
            for t, i in heard or [(a + t, i) for t, i in speaker_segments(video, start + a, start + b, faces)]:
                segments.append((t, faces[i]))
    split = shots[0] if len(shots) == 1 and len(shots[0]) == 2 else None
    # A 960px panel is ~6 face-widths tall; below H*0.45 the upscale turns to mush (run 4 wide shot: 4x).
    if split and min(w for _, _, w in split) * 6 < H * 0.45:
        split = None
    # YuNet boxed a patterned pillow bigger than the guest's face (run 11); a SPLIT panel needs a real face.
    if split and not all(_has_landmarks(video, start + (end - start) / 2, f) for f in split):
        split = None
    return segments, split


def _has_landmarks(video: Path, t: float, face: tuple[int, int, int]) -> bool:
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return False
    cx, cy, w = face
    s = int(w * 1.8)
    crop = cv2.resize(frame[max(0, cy - s):cy + s, max(0, cx - s):cx + s], (320, 320))
    return bool(_landmarker().detect(_rgb(crop)).face_landmarks)


def _lines(strength, lo: int, hi: int, edge: int) -> list[int]:
    """The strongest persistent lines between lo and hi, plus the frame edge when it is in reach."""
    span = range(max(lo, 4), min(hi, len(strength) - 4))
    # Peaks only: an edge is a few pixels thick, and one thick line used up every slot.
    peaks = [i for i in span if strength[i] >= 0.5 and strength[i] == max(strength[i - 4:i + 5])]
    return sorted(peaks, key=lambda i: -strength[i])[:16] + ([edge] if lo <= edge <= hi else [])


def cam_box(video: Path, work: Path) -> list[int] | None:
    """The streamer's webcam overlay [x, y, w, h], or None when the video has none. Found once per video
    and cached: the border is the line that stays put while the game changes under it, and one dark
    scene doesn't show it (a 25s night clip picked a shelf edge inside the webcam instead)."""
    cache = work / "facecam.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    W, H = frame_size(video)
    cap = cv2.VideoCapture(str(video))
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    det = _detector(W, H)
    seen = []
    for frame in _frames(video, 0, duration, 240 / duration, keyframes=True):
        _, found = det.detect(frame)
        small = [(int(x + w / 2), int(y + h / 2), int(w)) for x, y, w, h, *_ in (found if found is not None else [])
                 if w < W * CAM_FACE]
        seen.append((small, cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (W // 2, H // 2))))

    # Faces in the game come and go; the streamer's sits in one spot.
    spots = Counter((cx // 96, cy // 96) for small, _ in seen for cx, cy, _ in small)
    box, rank = None, (0, 0.0)
    if spots and spots.most_common(1)[0][1] >= len(seen) / 5:
        spot = spots.most_common(1)[0][0]
        here = [(f, gray) for small, gray in seen for f in small if (f[0] // 96, f[1] // 96) == spot]
        cx, cy, w = (int(statistics.median(v)) // 2 for v in zip(*(f for f, _ in here)))
        upright, level = np.zeros((H // 2, W // 2)), np.zeros((H // 2, W // 2))
        for _, gray in here:
            upright += cv2.dilate((np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0)) > EDGE).astype(np.uint8), np.ones((1, 3)))
            level += cv2.dilate((np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1)) > EDGE).astype(np.uint8), np.ones((3, 1)))
        upright, level = upright / len(here), level / len(here)
        rows, cols = slice(max(cy - w, 0), cy + w), slice(max(cx - w, 0), cx + w)
        across, down = upright[rows].mean(axis=0), level[:, cols].mean(axis=1)
        lefts, rights = _lines(across, cx - 10 * w, cx - w, 0), _lines(across, cx + w, cx + 10 * w, W // 2)
        tops, bottoms = _lines(down, cy - 6 * w, cy - w, 0), _lines(down, cy + w, cy + 8 * w, H // 2)
        for l in lefts:
            for r in rights:
                for t in tops:
                    for b in bottoms:
                        sides = [1.0 if l == 0 else upright[t:b, l].mean(), 1.0 if r == W // 2 else upright[t:b, r - 1].mean(),
                                 1.0 if t == 0 else level[t, l:r].mean(), 1.0 if b == H // 2 else level[b - 1, l:r].mean()]
                        # Lines inside the webcam (a shelf, a door frame) persist too: of the boxes that hold,
                        # take the widest, then the one whose weakest side holds best (chat rows under it are lines too).
                        # The aspect window is 4:3 to 16:9 webcams with slack.
                        if 1.2 <= (r - l) / (b - t) <= 1.9 and min(sides) >= 0.5 and (r - l, min(sides)) > rank:
                            box, rank = [l, t, r - l, b - t], (r - l, min(sides))
        if box:
            # Step inside the border line itself, or a sliver of gameplay shows down the webcam's edge.
            l, t, r, b = box[0], box[1], box[0] + box[2], box[1] + box[3]
            l, t, r, b = l + 2 * (l > 0), t + 2 * (t > 0), r - 2 * (r < W // 2), b - 2 * (b < H // 2)
            box = [l, t, r - l, b - t]
            l, t, w, h = box
            cv2.imwrite(str(work / "facecam.jpg"), cv2.rectangle(here[-1][1].copy(), (l, t), (l + w, t + h), 255, 2))
            box = [v * 2 for v in box]
    cache.write_text(json.dumps(box), encoding="utf-8")
    return box


def shows_cam(video: Path, start: float, end: float, box: list[int]) -> bool:
    """True when this clip is gameplay with the webcam in its box (not the camera cut to full screen)."""
    # Counted straight from the detections: `find_faces` groups people by x alone, and a character portrait
    # in the game's HUD right under the webcam merged with the streamer's face (run 12: four clips got TRACK).
    x, y, w, h = box
    W, H = frame_size(video)
    det = _detector(W, H)
    seen = inside = 0
    for frame in _frames(video, start, end, 2):
        _, found = det.detect(frame)
        seen += 1
        inside += any(x < fx + fw / 2 < x + w and y < fy + fh / 2 < y + h and fw < W * CAM_FACE
                      for fx, fy, fw, fh, *_ in (found if found is not None else []))
    return inside >= max(1, seen // 4)


def zooms(video: Path, start: float, end: float, box: list[int]) -> list[tuple[float, float, int]]:
    """Stretches where the streamer's camera fills the frame, as (from, to, face x) on the clip's clock. An edited
    stream upload cuts to the camera for the punchline, often mid-clip (run 12: 11 of the 18 gameplay clips), at more than
    one zoom level, so "zoomed" is any face clearly bigger than it is inside the webcam box."""
    W, H = frame_size(video)
    det = _detector(W, H)
    faces = []
    for frame in _frames(video, start, end, 2):
        _, found = det.detect(frame)
        found = [(int(x + w / 2), int(y + h / 2), int(w)) for x, y, w, h, *_ in (found if found is not None else [])]
        big = [(w, cx) for cx, cy, w in found if w >= box[2] / 4]
        # A big face in the game (a character select screen) isn't a zoom: the webcam is still in its box then.
        boxed = any(box[0] < cx < box[0] + box[2] and box[1] < cy < box[1] + box[3] and w < W * CAM_FACE for cx, cy, w in found)
        faces.append(max(big)[1] if big and not boxed else None)
    # One stray sample (a face in the game, a missed detection) doesn't make or break a stretch.
    for k in range(1, len(faces) - 1):
        if (faces[k] is None) != (faces[k - 1] is None) and (faces[k - 1] is None) == (faces[k + 1] is None):
            faces[k] = faces[k - 1]
    cuts = shot_cuts(video, start, end)

    def snap(t: float) -> float:
        # Samples are half a second apart; the editor's cut is exact.
        near = min(cuts, key=lambda c: abs(c - t), default=None)
        return near if near is not None and abs(near - t) <= 0.6 else t

    out, k = [], 0
    while k < len(faces):
        if faces[k] is None:
            k += 1
            continue
        first = k
        while k < len(faces) and faces[k] is not None:
            k += 1
        if k - first >= 2:
            a = 0.0 if first == 0 else snap(first / 2 - 0.25)
            b = end - start if k == len(faces) else snap(k / 2 - 0.25)
            if b > a:
                out.append((a, b, int(statistics.median(faces[first:k]))))
    return out


def cam_height(cam: list[int]) -> int:
    return int(1080 * cam[3] / cam[2]) // 2 * 2


def game_filter(cam: list[int], W: int, H: int, zoomed: list[tuple[float, float, int]] = ()) -> str:
    """Webcam across the top at full width, gameplay under it. Captions go on the seam.
    During `zoomed` shots the camera already fills the frame, so a full-height crop on the face covers both."""
    x, y, w, h = cam
    top = cam_height(cam)
    gw = min(int(H * 1080 / (1920 - top)) // 2 * 2, W)
    # Slide the gameplay crop off the webcam where there is room, so the streamer isn't shown twice.
    gx = min((W - gw) // 2, max(0, x - gw)) if x + w / 2 > W / 2 else max((W - gw) // 2, min(W - gw, x + w))
    stacked = (f"[c]crop={w}:{h}:{x}:{y},scale=1080:{top}[cs];"
               f"[g]crop={gw}:{H}:{gx}:0,scale=1080:{1920 - top}[gs];[cs][gs]vstack")
    if not zoomed:
        return f"[0:v]split[c][g];{stacked}"
    cw = int(H * 9 / 16) // 2 * 2
    zx = "+".join(f"{min(max(fx - cw // 2, 0), W - cw)}*gte(t\\,{a:.2f})*lt(t\\,{b:.2f})" for a, b, fx in zoomed)
    during = "+".join(f"gte(t\\,{a:.2f})*lt(t\\,{b:.2f})" for a, b, _ in zoomed)
    return (f"[0:v]split=3[c][g][z];{stacked}[gm];[z]crop={cw}:{H}:{zx}:0,scale=1080:1920[zz];"
            f"[gm][zz]overlay=enable={during}")


def split_filter(faces, W: int, H: int) -> str:
    """Two faces stacked, each in a 1080x960 panel. Captions go on the seam."""
    panels = []
    for i, (cx, cy, w) in enumerate(faces[:2]):
        ph = min(int(w * 6.0), H)
        pw = min(int(ph * 1080 / 960), W)
        x = min(max(cx - pw // 2, 0), W - pw)
        y = min(max(cy - int(ph * 0.4), 0), H - ph)
        panels.append(f"[p{i}]crop={pw}:{ph}:{x}:{y},scale=1080:960[s{i}]")
    return "[0:v]split[p0][p1];" + ";".join(panels) + ";[s0][s1]vstack"


# TRACK framing (Tko's pick, 2026-10-06: style C).
FACE = 0.205        # a face fills this much of the crop's height; YuNet boxes run about FACE_ASPECT taller than wide
FACE_ASPECT = 1.3
EYE_LINE = 0.36     # the face's centre sits this far down the crop
PUNCH = 0.8         # a punch-in crops to this much of the shot's normal crop
MAX_ZOOM = 1.6      # never crop tighter than this from the source height: a 1080p source is already upscaled 1.8x
PUSH = 0.05         # slow push-in over a shot
MIN_PUSH = 1.2      # shots shorter than this are over before a push-in reads
LONG_HOLD = 4.5     # a shot held longer than this gets a punch-in at a sentence break near its middle
BREAK_MARGIN = 1.8  # a punch-in leaves at least this much of the hold on either side
FLASH = 0.04        # a shot this short is one frame: it joins the shot before it


def _crop(face, punch: float, W: int, H: int) -> tuple[int, int, int, int]:
    """The 9:16 window (w, h, x, y) for one face, or the full-height centre when there is none."""
    if face is None:
        cw = int(H * 9 / 16) // 2 * 2
        return cw, H, (W - cw) // 2, 0
    cx, cy, w = face
    ch = max(min(H, w * FACE_ASPECT / FACE) * punch, H / MAX_ZOOM)
    cw = ch * 9 / 16
    return int(cw) // 2 * 2, int(ch) // 2 * 2, int(min(max(cx - cw / 2, 0), W - cw)), int(min(max(cy - ch * EYE_LINE, 0), H - ch))


def _punches(face, W: int, H: int) -> bool:
    # A small face is already at MAX_ZOOM: a "punch-in" there would only restart the push-in, a jump outwards.
    return face is not None and _crop(face, PUNCH, W, H)[1] < 0.9 * _crop(face, 1, W, H)[1]


def track_shots(segments, W: int, H: int, length: float, breaks: list[float] = ()) -> list[tuple]:
    """(start, end, face, punch) per output shot: a cut when the camera or the speaker changes, a punch-in
    partway through a long hold and on the last shot (the payoff). `breaks` are clip-relative times where a
    sentence or clause ends; punch-ins land on those."""
    held = []
    for (a, face), b in zip(segments, [t for t, _ in segments[1:]] + [length]):
        if held and b - a <= FLASH:
            held[-1] = (held[-1][0], b, held[-1][2])
        else:
            held.append((a, b, face))
    shots = []
    for a, b, face in held:
        marks = [m for m in breaks if a + BREAK_MARGIN < m < b - BREAK_MARGIN]
        if b - a > LONG_HOLD and marks and _punches(face, W, H):
            mid = min(marks, key=lambda m: abs(m - (a + b) / 2))
            shots += [(a, mid, face, 1), (mid, b, face, PUNCH)]
        else:
            shots.append((a, b, face, 1))
    if len(shots) > 1 and _punches(shots[-1][2], W, H):
        shots[-1] = (*shots[-1][:3], PUNCH)
    return shots


def track_filter(shots, W: int, H: int) -> str:
    """9:16 crops, one per shot from `track_shots`, each with a slow push-in."""
    parts = []
    for n, (a, b, face, punch) in enumerate(shots):
        cw, ch, x, y = _crop(face, punch, W, H)
        crop = f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,crop={cw}:{ch}:{x}:{y}"
        if b - a > MIN_PUSH:
            k = PUSH / (b - a)
            grow = f"(1+{k:.5f}*t)"
            # crop centres on the first frame's size unless told otherwise, so the offsets grow with the frame.
            parts.append(f"{crop},scale=w='trunc(1080*{grow}/2)*2':h='trunc(1920*{grow}/2)*2':eval=frame,"
                         f"crop=1080:1920:'{540 * k:.5f}*t':'{960 * k:.5f}*t',setsar=1[t{n}]")
        else:
            parts.append(f"{crop},scale=1080:1920,setsar=1[t{n}]")
    return ";".join(parts) + ";" + "".join(f"[t{n}]" for n in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0"


def track_caption_y(shots, W: int, H: int, least: int, most: int) -> int:
    """Where captions clear every chin in the clip: a close-up fills the frame and its mouth sits lower."""
    chins = [(cy + FACE_ASPECT * w / 2 - y) / ch * 1920
             for _, _, face, punch in shots if face for cx, cy, w in [face] for _, ch, _, y in [_crop(face, punch, W, H)]]
    return int(min(max([least] + [c + 150 for c in chins]), most))
