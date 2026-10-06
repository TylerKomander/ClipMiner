import json
import os
import re
import subprocess
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent / "fonts"
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Cap,Lilita One,{size},&H00FFFFFF,&H00000000,&H96000000,0,1,6,4,5,40,40,0

[Events]
Format: Layer, Start, End, Style, Text
"""
FONT_SIZE = 118
FIT_CHARS = 14    # the longest line that fits 1080px at FONT_SIZE through the pop; longer ones are scaled down
PAUSE = 0.6       # a gap this long between words ends the line
LINGER = 0.12     # a line stays this long after its last word
MIN_SHOWN, MAX_SHOWN = 0.18, 1.2  # Whisper stretches a word's end across the pause after it
# One colour per speaker, the one who talks most first (ASS writes colours as BGR). Unknown speakers stay white.
SPEAKER_COLOURS = ["&H0003FEFC&", "&H0054FB01&", "&H00FBFC56&", "&H00038FFC&"]
WHITE = "&H00FFFFFF&"


def pop(scale: int) -> str:
    """Each caption lands a little small, overshoots and settles in 0.15s (Tko's pick, 2026-10-06: style C)."""
    small, big = round(scale * 0.82), round(scale * 1.14)
    return rf"\fscx{small}\fscy{small}\t(0,70,\fscx{big}\fscy{big})\t(70,150,\fscx{scale}\fscy{scale})"

BLUR_FILL = (
    "[0:v]split[a][b];"
    "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
    "[b]scale=1080:-2[fg];"
    "[bg][fg]overlay=(W-w)/2:(H-h)/2"
)
# Where a caption sits: (ASS alignment, y of that anchor in the 1920-high frame).
CAPTIONS_LOW = (2, 1400)
CAPTIONS_SEAM = (5, 960)
CAPTIONS_MID = (5, 1100)


# Tko's rule: no curse word may be readable on screen. The audio stays; only the caption is masked.
CURSE = re.compile(
    r"(mother)?f+u+c*k+\w*|\w*shit\w*|\w*bitch\w*|(dumb|jack|bad|smart)?ass(es|hole|holes)?|"
    r"dick(s|head|heads)?|cock(s|sucker|suckers)?|puss(y|ies)|cunts?|nigg\w*|fag\w*|(god)?damn\w*|"
    r"bastards?|whores?|sluts?|retard\w*|twats?|piss\w*|hoes?",
    re.IGNORECASE,
)


def mask_curses(word: str) -> str:
    # Part by part: "grown-ass" and "bitch's" are one caption word since Whisper's split tokens are glued.
    def mask(part: str) -> str:
        core = part.strip(".,?!;:\"")
        return part.replace(core, "*" * len(core)) if core and CURSE.fullmatch(core) else part
    return "".join(mask(part) for part in re.split(r"([-'])", word))


def ass_time(t: float) -> str:
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def caption_lines(words: list[dict], start: float, max_words: int = 2, max_chars: int = 12) -> list[tuple[float, float, str, int | None]]:
    """(start, end, text, speaker): one or two words at a time, one after another, gone in pauses."""
    tokens = []
    for w in words:
        text = w["word"].strip()
        # Whisper writes "10 -year -old", "$3 ,000" and "50 %" as separate tokens (run 15: they reached the screen).
        if tokens and (text[:1] in "-,'" and len(text) > 1 or text in {"%", ".", ",", "?", "!"}):
            tokens[-1] = {**tokens[-1], "word": tokens[-1]["word"] + text, "end": w["end"]}
        elif text.strip("-"):
            tokens.append({**w, "word": text})
    lines, chunk = [], []
    for w in tokens:
        if chunk and (len(chunk) == max_words or len(" ".join(c["word"] for c in chunk)) + 1 + len(w["word"]) > max_chars
                      or chunk[-1]["word"].endswith((".", ",", "?", "!")) or w["start"] - chunk[-1]["end"] > PAUSE
                      or w.get("speaker") != chunk[-1].get("speaker")):
            lines.append(chunk)
            chunk = []
        chunk.append(w)
    if chunk:
        lines.append(chunk)
    out, free = [], 0.0
    for i, c in enumerate(lines):
        # Whisper gives runs of words one timestamp (run 15: lines that never showed, or sat on top of each other).
        a = max(c[0]["start"] - start, free)
        b = min(max(c[-1]["end"] - start + LINGER, a + MIN_SHOWN), a + MAX_SHOWN)
        if i + 1 < len(lines):
            b = max(min(b, lines[i + 1][0]["start"] - start), a + MIN_SHOWN)
        out.append((a, b, " ".join(mask_curses(w["word"]) for w in c).upper(), c[0].get("speaker")))
        free = b
    return out


def render(video: Path, work: Path, out: Path, start: float, end: float,
           video_filter: str = BLUR_FILL, captions: tuple[int, int] = CAPTIONS_LOW,
           words: list[dict] | None = None) -> Path:
    """`words` are the exact words to caption; the dry run picks them. Selecting by time instead
    pulls in neighbours that share a timestamp with the first word (run 4: a stray "ON.")."""
    if words is None:
        every = [w for s in json.loads((work / "transcript.json").read_text(encoding="utf-8"))["segments"] for w in s["words"]]
        words = [w for w in every if w["start"] >= start - 0.05 and w["end"] <= end + 0.05]
    ass = work / f"{out.stem}.ass"
    place = rf"\an{captions[0]}\pos(540,{captions[1]})"
    events = []
    for a, b, text, speaker in caption_lines(words, start):
        colour = SPEAKER_COLOURS[speaker] if speaker is not None and speaker < len(SPEAKER_COLOURS) else WHITE
        look = rf"{place}\c{colour}{pop(min(100, round(100 * FIT_CHARS / len(text))))}"
        events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,{{{look}}}{text}")
    ass.write_text(ASS_HEADER.format(size=FONT_SIZE) + "\n".join(events) + "\n", encoding="utf-8")

    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(video.resolve()),
            "-filter_complex", f"{video_filter},subtitles={ass.name}:fontsdir={Path(os.path.relpath(FONTS, work)).as_posix()}",
            "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "160k",
            str(out.resolve()),
        ],
        cwd=work, check=True,
    )
    return out
