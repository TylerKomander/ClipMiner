"""Turn a reviewed pick into the stretches of video it keeps: story cuts removed, dead air shortened,
and an ending that waits for the last word to finish. More than one stretch means jump cuts."""
import re
import subprocess
from pathlib import Path

import numpy as np

PAD = 0.12           # kept either side of a spoken stretch; a trimmed pause ends up ~0.25s
DEAD_AIR = 0.6       # pauses longer than this get shortened, but only where the audio really is quiet
QUIET_DB = 18        # "quiet" = this far under the clip's speech level
MIN_KEEP = 1.0       # a kept stretch shorter than this is a flash on screen: leave the pause beside it alone
MIN_TAIL, MAX_TAIL = 0.25, 0.8
LONG_WINDOW = 600    # past this, the audio is read per kept run instead of for the whole window
RECAP_HOLD = 0.35    # a recap moment stays this long on the quiet after its last line, so a cut doesn't clip it
SLIVER = 0.7         # a film's camera cut this close inside a stretch's start or end leaves a flash of the other shot
MIN_SHOT = 0.5       # what a sliver is grown to when the line runs across the camera cut
WORD_SLOP = 0.2      # Whisper puts a word's start up to this much early
# An HDR film (PQ, BT.2020) played as plain video is grey and washed out: map it to SDR, at 1080p since the
# short is 1080 wide anyway and tone mapping 4K frames in float is slow. Mobius, not hable: hable crushed dark
# faces on Atlanta S02E01 (2026-11-09).
TO_SDR = ("scale=1920:-2,zscale=tin=smpte2084:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
          "zscale=p=bt709,tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")


def is_hdr(video: Path) -> bool:
    transfer = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=color_transfer", "-of", "csv=p=0", str(video)],
                              capture_output=True, text=True, check=True).stdout.strip()
    return transfer in {"smpte2084", "arib-std-b67"}


def kept_runs(first: int, last: int, cuts: list[list[int]]) -> list[tuple[int, int]]:
    dropped = {i for a, b in cuts for i in range(a, b + 1)}
    runs, start = [], None
    for i in range(first, last + 1):
        if i in dropped:
            if start is not None:
                runs.append((start, i - 1))
                start = None
        elif start is None:
            start = i
    if start is not None:
        runs.append((start, last))
    return runs


def envelope(video: Path, start: float, end: float) -> tuple[float, np.ndarray]:
    """Loudness in dB every 20ms, from `start`."""
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
         "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    frames = samples[: len(samples) // 320 * 320].reshape(-1, 320)
    return start, np.convolve(20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1), np.ones(3) / 3, mode="same")


def quiet_part(sound: tuple[float, np.ndarray], level: float, gap_from: float, gap_to: float) -> tuple[float, float]:
    """The longest truly quiet run inside a gap between two words. Whisper's word times are loose and it
    leaves out whoever talks over the gap, so a gap in the transcript is not a silence (Tko, run 12: cuts
    landed mid-word and between two people talking)."""
    t0, db = sound
    lo, hi = max(int((gap_from - t0) / 0.02), 0), int((gap_to - t0) / 0.02)
    below = db[lo:hi] < level - QUIET_DB
    best, begin, run = 0, 0, 0
    for k, quiet in enumerate(below):
        run = run + 1 if quiet else 0
        if run > best:
            best, begin = run, k - run + 1
    return t0 + (lo + begin) * 0.02, t0 + (lo + begin + best) * 0.02


def stretches(words: list[dict], first: int, last: int, cuts: list[list[int]],
              sound: tuple[float, np.ndarray] | None = None) -> list[tuple[float, float]]:
    """Time spans to keep. Without the audio every long gap between words counts as dead air (used for
    the review preview, which only needs an estimate; the render trims less, so it can run a little longer)."""
    runs = kept_runs(first, last, cuts)
    if sound:
        t0, db = sound
        level = np.percentile(np.concatenate(
            [db[max(int((words[a]["start"] - t0) / 0.02), 0):int((words[b]["end"] - t0) / 0.02)] for a, b in runs]), 90)
    spans = []
    for a, b in runs:
        run = [(words[a]["start"] - PAD, None)]
        for i in range(a, b):
            quiet_from, quiet_to = words[i]["end"], words[i + 1]["start"]
            if sound and quiet_to - quiet_from > DEAD_AIR:
                quiet_from, quiet_to = quiet_part(sound, level, quiet_from, quiet_to)
            if quiet_to - quiet_from > DEAD_AIR:
                run[-1] = (run[-1][0], quiet_from + PAD)
                run.append((quiet_to - PAD, None))
        run[-1] = (run[-1][0], words[b]["end"] + PAD)
        for span in run:
            if span is not run[0] and min(span[1] - span[0], spans[-1][1] - spans[-1][0]) < MIN_KEEP:
                spans[-1] = (spans[-1][0], span[1])
            else:
                spans.append((max(span[0], spans[-1][1]) if spans else span[0], span[1]))
    return spans


def seconds(words: list[dict], first: int, last: int, cuts: list[list[int]]) -> float:
    spans = stretches(words, first, last, cuts)
    return round(sum(b - a for a, b in spans) + MIN_TAIL, 1)


def tail_end(video: Path, t: float, hold: float = 0.0) -> float:
    """Whisper often ends the last word early (or at the next word's start), which clipped the final
    syllable on some clips. Listen instead, never cutting sooner than MIN_TAIL: stop where the voice
    drops for 120ms, or, when someone talks straight on, at the quietest seam before MAX_TAIL.
    `hold` stays that much longer on the quiet after the voice drops, ending early if anyone speaks."""
    lead = 1.0
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{max(t - lead, 0):.3f}", "-t", f"{lead + MAX_TAIL + hold + 0.1:.3f}",
         "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    frames = samples[: len(samples) // 320 * 320].reshape(-1, 320)  # 20ms frames
    db = np.convolve(20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1), np.ones(3) / 3, mode="same")
    zero = int(min(lead, t) / 0.02)
    lo, hi = zero + int(MIN_TAIL / 0.02), min(zero + int(MAX_TAIL / 0.02), len(db))
    if zero == 0 or hi <= lo:
        return t + MIN_TAIL
    quiet = np.percentile(db[:zero], 90) - 18
    for k in range(lo, hi - 5):
        if (db[k:k + 6] < quiet).all():
            j = k + 3
            while j < min(k + 3 + int(hold / 0.02), len(db)) and db[j] < quiet:
                j += 1
            return t + (j - zero) * 0.02
    return t + (lo + int(np.argmin(db[lo:hi])) - zero) * 0.02 + 0.02


def frame_rate(video: Path) -> float:
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                           "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout.strip()
    num, den = rate.split("/")
    return int(num) / int(den)


def camera_cuts(video: Path, start: float, end: float) -> list[float]:
    """Times (on the source's clock) where the camera cuts between `start` and `end`."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{max(start, 0):.3f}", "-to", f"{end:.3f}", "-i", str(video),
         "-vf", "scdet=threshold=10", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [max(start, 0) + float(t) for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", proc.stderr)]


def unsliver(video: Path, spans: list[tuple[float, float]], words: list[dict], kept: list[int]) -> list[tuple[float, float]]:
    """A film stretch that starts or ends a few frames from a camera cut flashes the other shot, and the BAND
    window jumps to it and back (Tko on 352-361: "no flicker", "doesn't seem super clipped"). Start or end on
    the cut when the clip's own line is clear of it; when the line runs across it, grow the sliver into the quiet
    beside it. `kept` is the clip's word indices: the beat held after a line often reaches the next one's start."""
    out = []
    for a, b in spans:
        said = [i for i in kept if a - SLIVER <= words[i]["start"] < b]
        said = [i for i in said if words[i]["end"] > a] or said
        near = camera_cuts(video, a - SLIVER, a + SLIVER)
        head = [c for c in near if a < c <= a + SLIVER]
        if head and said:
            c = max(head)
            # Whisper starts a word up to ~0.2s early: a line that "starts" that close before the cut starts on it.
            if words[said[0]]["start"] >= c - WORD_SLOP:
                a = c
            else:
                floor = max(words[said[0] - 1]["end"] + PAD if said[0] else 0.0, out[-1][1] if out else 0.0)
                a = max(min(a, c - MIN_SHOT), floor, max((x for x in near if x <= a), default=a - SLIVER))
        near = camera_cuts(video, b - SLIVER, b + SLIVER)
        tail = [c for c in near if b - SLIVER <= c < b and c > a + MIN_SHOT]
        if tail and said:
            c = min(tail)
            if words[said[-1]]["end"] <= c + 0.05:
                b = c
            else:
                after = words[said[-1] + 1]["start"] - PAD if said[-1] + 1 < len(words) else b + SLIVER
                b = min(max(b, c + MIN_SHOT), max(after, b), min((x for x in near if x >= b), default=b + SLIVER))
        out.append((a, b))
    return out


def build(video: Path, work: Path, words: list[dict], clip: dict, stem: str, film: bool = False) -> tuple[Path, float, float, list[dict], list[float]]:
    """Source file, start, end, caption words (on that file's clock) and where one moment cuts to the next (recaps), for one clip."""
    first, last, cuts = clip["first"], clip["last"], clip.get("cuts", [])
    runs = kept_runs(first, last, cuts)
    # A film clip of several pieces always takes the per-piece path below, however close they sit: each piece
    # needs its own beat of quiet, or a line runs chopped into the next piece (Tko on clip 347).
    if (not film or len(runs) == 1) and words[last]["end"] - words[first]["start"] <= LONG_WINDOW:
        sound = envelope(video, max(words[first]["start"] - 1, 0), words[last]["end"] + 1)
        spans = stretches(words, first, last, cuts, sound)
        spans[-1] = (spans[-1][0], tail_end(video, words[last]["end"]))
        ends = set(range(len(spans)))
    else:
        # A movie recap's moments sit up to two hours apart: read the audio around each one, not the whole film.
        # Every moment ends on a beat of quiet after its last word, not just the last one: cut 0.12s after
        # Whisper's last word, lines sounded chopped into the next moment (Tko on clip 347).
        spans, ends = [], set()
        for a, b in runs:
            spans += stretches(words, a, b, [], envelope(video, max(words[a]["start"] - 1, 0), words[b]["end"] + 1))
            spans[-1] = (spans[-1][0], tail_end(video, words[b]["end"], RECAP_HOLD))
            ends.add(len(spans) - 1)
    kept = [w for a, b in runs for w in words[a:b + 1]]
    if film:
        spans = unsliver(video, spans, words, [i for a, b in runs for i in range(a, b + 1)])
        # A stretch moved onto a camera cut may start just after its first word's (early) start: keep the caption.
        kept = [next(({**w, "start": a} for a, b in spans if a - WORD_SLOP <= w["start"] < a < w["end"]), w) for w in kept]
    fps = frame_rate(video)
    if len(spans) == 1:
        first, last = round(spans[0][0] * fps), round(spans[0][1] * fps)
        return video, (first - 0.5) / fps, (last - 1) / fps, kept, []

    offset, shifted, inputs, filters, labels, joins = 0.0, [], [], [], [], []
    sdr = TO_SDR if is_hdr(video) else ""
    for n, (a, b) in enumerate(spans):
        # Whole frames only: a stretch ends on a frame, so a length in between came out up to a frame long
        # each time and the captions and BAND moves ran 0.37s early by the end of a 16-moment recap (348).
        first, frames = round(a * fps), max(round(b * fps) - round(a * fps), 1)
        a, length = first / fps, frames / fps
        shifted += [{**w, "start": w["start"] - a + offset, "end": w["end"] - a + offset}
                    for w in kept if a <= w["start"] < b]
        # One seek per stretch: ffmpeg decodes only the stretches, however far apart they are.
        # Half a frame early, so the seek lands on frame `first` whatever the rounding. ffmpeg times `-t` from that
        # frame, not the seek point: a full `length` let one more frame in, the next shot's when a stretch ended on
        # a camera cut (one-frame flashes in 372, run 22).
        inputs += ["-ss", f"{a - 0.5 / fps:.6f}", "-t", f"{length - 0.5 / fps:.6f}", "-i", str(video.resolve())]
        filters.append(f"[{n}:v:0]{sdr}setpts=PTS-STARTPTS[v{n}];"
                       f"[{n}:a:0]asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.012,afade=t=out:st={max(length - 0.012, 0):.3f}:d=0.012[a{n}]")
        labels.append(f"[v{n}][a{n}]")
        offset += length
        if n in ends:
            joins.append(offset)
    cut = work / f"{stem}_spliced.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(spans)}:v=1:a=1[v][a]",
         # ffmpeg copies the source's chapters by default: a recap cut from an .mkv carried the film's 38-minute
         # chapter track, and the player showed 27 minutes (Tko, run 21).
         "-map", "[v]", "-map", "[a]", "-map_chapters", "-1", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
         "-c:a", "aac", "-b:a", "192k", str(cut.resolve())],
        check=True)
    return cut, 0.0, offset, shifted, [t for t in joins if t < offset]
