import re
import statistics
import subprocess
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

MODELS = Path(__file__).resolve().parent.parent / "models"
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)


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
    return [float(t) for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", proc.stderr) if float(t) > 0.3]


def find_faces(video: Path, start: float, end: float) -> list[tuple[int, int, int]]:
    """Median (cx, cy, width) per person, left to right, within one camera shot."""
    W, H = frame_size(video)
    cap = cv2.VideoCapture(str(video))
    det = _detector(W, H)
    times = [start + 0.5 * k for k in range(int((end - start) / 0.5))] or [(start + end) / 2]
    hits = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        _, found = det.detect(frame)
        for x, y, w, h, *_ in (found if found is not None else []):
            hits.append((int(x + w / 2), int(y + h / 2), int(w)))
    cap.release()
    if not hits:
        return []
    # Faces on posters and book covers behind the hosts are real detections but tiny (run 5).
    biggest = max(w for _, _, w in hits)
    hits = sorted(h for h in hits if h[2] >= biggest / 3)
    people, current = [], [hits[0]]
    for h in hits[1:]:
        if h[0] - current[-1][0] > 0.15 * W:
            people.append(current)
            current = []
        current.append(h)
    people.append(current)
    people = [p for p in people if len(p) >= max(1, len(times) // 3)]
    return [tuple(int(statistics.median(v)) for v in zip(*p)) for p in people]


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


def plan(video: Path, start: float, end: float) -> tuple[list[tuple[float, int]], list | None]:
    """TRACK segments as (clip-relative time, face center x), plus the two faces for SPLIT, or None
    when SPLIT can't work (camera cuts, not exactly two people in the one shot, or faces too small)."""
    W, H = frame_size(video)
    bounds = [0.0, *shot_cuts(video, start, end), end - start]
    segments, shots = [], []
    for a, b in zip(bounds, bounds[1:]):
        faces = find_faces(video, start + a, start + b)
        shots.append(faces)
        if not faces:
            segments.append((a, W // 2))
        elif len(faces) == 1:
            segments.append((a, faces[0][0]))
        else:
            for t, i in speaker_segments(video, start + a, start + b, faces):
                segments.append((a + t, faces[i][0]))
    split = shots[0] if len(shots) == 1 and len(shots[0]) == 2 else None
    # A 960px panel is ~6 face-widths tall; below H*0.45 the upscale turns to mush (run 4 wide shot: 4x).
    if split and min(w for _, _, w in split) * 6 < H * 0.45:
        split = None
    return segments, split


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


def track_filter(segments, W: int, H: int) -> str:
    """9:16 full-height crop that follows the talking face, cutting when the camera or speaker changes."""
    cw = int(H * 9 / 16) // 2 * 2
    xs = [min(max(cx - cw // 2, 0), W - cw) for _, cx in segments]
    expr = str(xs[-1])
    for k in reversed(range(len(segments) - 1)):
        expr = f"if(lt(t\\,{segments[k + 1][0]:.2f})\\,{xs[k]}\\,{expr})"
    return f"[0:v]crop={cw}:{H}:{expr}:0,scale=1080:1920"
