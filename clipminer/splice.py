"""Turn a reviewed pick into the stretches of video it keeps: story cuts removed, dead air shortened,
and an ending that waits for the last word to finish. More than one stretch means jump cuts."""
import json
import subprocess
from pathlib import Path

import numpy as np

PAD = 0.12           # kept either side of a spoken stretch; a trimmed pause ends up ~0.25s
DEAD_AIR = 0.6       # pauses longer than this get shortened...
LAUGH_LU = 6         # ...unless the room is laughing (loudness this far over the episode median)
MIN_TAIL, MAX_TAIL = 0.25, 0.8


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


def stretches(words: list[dict], first: int, last: int, cuts: list[list[int]],
              loud: dict | None = None) -> list[tuple[float, float]]:
    """Time spans to keep. Without loudness data every long pause counts as dead air (used for the
    review preview, which only needs an estimate)."""
    median = loud["median"] if loud else 0
    level = {p["t"]: p["m"] for p in loud["series"]} if loud else {}
    spans = []
    for a, b in kept_runs(first, last, cuts):
        start = words[a]["start"] - PAD
        for i in range(a, b):
            gap_from, gap_to = words[i]["end"], words[i + 1]["start"]
            laughing = any(level.get(t, -99) - median >= LAUGH_LU for t in range(int(gap_from), int(gap_to) + 1))
            if gap_to - gap_from > DEAD_AIR and not laughing:
                spans.append((start, gap_from + PAD))
                start = gap_to - PAD
        spans.append((start, words[b]["end"] + PAD))
    return spans


def seconds(words: list[dict], first: int, last: int, cuts: list[list[int]]) -> float:
    spans = stretches(words, first, last, cuts)
    return round(sum(b - a for a, b in spans) + MIN_TAIL, 1)


def tail_end(video: Path, t: float) -> float:
    """Whisper often ends the last word early (or at the next word's start), which clipped the final
    syllable on some clips. Listen instead, never cutting sooner than MIN_TAIL: stop where the voice
    drops for 120ms, or, when someone talks straight on, at the quietest seam before MAX_TAIL."""
    lead = 1.0
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{max(t - lead, 0):.3f}", "-t", f"{lead + MAX_TAIL + 0.1:.3f}",
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
            return t + (k - zero) * 0.02 + 0.06
    return t + (lo + int(np.argmin(db[lo:hi])) - zero) * 0.02 + 0.02


def build(video: Path, work: Path, words: list[dict], clip: dict, stem: str) -> tuple[Path, float, float, list[dict]]:
    """Source file, start, end and caption words (on that file's clock) for one clip."""
    loud = json.loads((work / "loudness.json").read_text(encoding="utf-8"))
    spans = stretches(words, clip["first"], clip["last"], clip.get("cuts", []), loud)
    spans[-1] = (spans[-1][0], tail_end(video, words[clip["last"]]["end"]))
    kept = [w for a, b in kept_runs(clip["first"], clip["last"], clip.get("cuts", [])) for w in words[a:b + 1]]
    if len(spans) == 1:
        return video, spans[0][0], spans[0][1], kept

    offset, shifted, filters, labels = 0.0, [], [], []
    base = max(spans[0][0] - 1, 0)  # seek close to the clip; trims are measured from here
    for n, (a, b) in enumerate(spans):
        length = b - a
        shifted += [{**w, "start": w["start"] - a + offset, "end": w["end"] - a + offset}
                    for w in kept if a <= w["start"] < b]
        filters.append(f"[0:v]trim={a - base:.3f}:{b - base:.3f},setpts=PTS-STARTPTS[v{n}];"
                       f"[0:a]atrim={a - base:.3f}:{b - base:.3f},asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.012,afade=t=out:st={max(length - 0.012, 0):.3f}:d=0.012[a{n}]")
        labels.append(f"[v{n}][a{n}]")
        offset += length
    cut = work / f"{stem}_spliced.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{base:.3f}", "-i", str(video.resolve()),
         "-filter_complex", ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(spans)}:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
         "-c:a", "aac", "-b:a", "192k", str(cut.resolve())],
        check=True)
    return cut, 0.0, offset, shifted
