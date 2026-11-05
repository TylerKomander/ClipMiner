"""Turn a reviewed pick into the stretches of video it keeps: story cuts removed, dead air shortened,
and an ending that waits for the last word to finish. More than one stretch means jump cuts."""
import subprocess
from pathlib import Path

import numpy as np

PAD = 0.12           # kept either side of a spoken stretch; a trimmed pause ends up ~0.25s
DEAD_AIR = 0.6       # pauses longer than this get shortened, but only where the audio really is quiet
QUIET_DB = 18        # "quiet" = this far under the clip's speech level
MIN_KEEP = 1.0       # a kept stretch shorter than this is a flash on screen: leave the pause beside it alone
MIN_TAIL, MAX_TAIL = 0.25, 0.8
LONG_WINDOW = 600    # past this, the audio is read per kept run instead of for the whole window


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
    first, last, cuts = clip["first"], clip["last"], clip.get("cuts", [])
    runs = kept_runs(first, last, cuts)
    if words[last]["end"] - words[first]["start"] <= LONG_WINDOW:
        sound = envelope(video, max(words[first]["start"] - 1, 0), words[last]["end"] + 1)
        spans = stretches(words, first, last, cuts, sound)
    else:
        # A movie recap's moments sit up to two hours apart: read the audio around each one, not the whole film.
        spans = [s for a, b in runs
                 for s in stretches(words, a, b, [], envelope(video, max(words[a]["start"] - 1, 0), words[b]["end"] + 1))]
    spans[-1] = (spans[-1][0], tail_end(video, words[last]["end"]))
    kept = [w for a, b in runs for w in words[a:b + 1]]
    if len(spans) == 1:
        return video, spans[0][0], spans[0][1], kept

    offset, shifted, inputs, filters, labels = 0.0, [], [], [], []
    for n, (a, b) in enumerate(spans):
        length = b - a
        shifted += [{**w, "start": w["start"] - a + offset, "end": w["end"] - a + offset}
                    for w in kept if a <= w["start"] < b]
        # One seek per stretch: ffmpeg decodes only the stretches, however far apart they are.
        inputs += ["-ss", f"{a:.3f}", "-t", f"{length:.3f}", "-i", str(video.resolve())]
        filters.append(f"[{n}:v:0]setpts=PTS-STARTPTS[v{n}];"
                       f"[{n}:a:0]asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.012,afade=t=out:st={max(length - 0.012, 0):.3f}:d=0.012[a{n}]")
        labels.append(f"[v{n}][a{n}]")
        offset += length
    cut = work / f"{stem}_spliced.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(spans)}:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
         "-c:a", "aac", "-b:a", "192k", str(cut.resolve())],
        check=True)
    return cut, 0.0, offset, shifted
