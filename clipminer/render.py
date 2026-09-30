import json
import subprocess
from pathlib import Path

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Cap,Arial Black,84,&H00FFFFFF,&H00000000,&H80000000,1,1,6,2,{alignment},60,60,{margin_v}

[Events]
Format: Layer, Start, End, Style, Text
"""

BLUR_FILL = (
    "[0:v]split[a][b];"
    "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
    "[b]scale=1080:-2[fg];"
    "[bg][fg]overlay=(W-w)/2:(H-h)/2"
)
CAPTIONS_LOW = (2, 520)
CAPTIONS_SEAM = (5, 0)


def ass_time(t: float) -> str:
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def caption_lines(words: list[dict], start: float, end: float, max_words: int = 3) -> list[tuple[float, float, str]]:
    inside = [w for w in words if w["start"] >= start - 0.05 and w["end"] <= end + 0.05]
    lines, chunk = [], []
    for w in inside:
        chunk.append(w)
        if len(chunk) == max_words or w["word"].rstrip().endswith((".", ",", "?", "!")):
            lines.append(chunk)
            chunk = []
    if chunk:
        lines.append(chunk)
    return [
        (c[0]["start"] - start, c[-1]["end"] - start, " ".join(w["word"].strip() for w in c).upper())
        for c in lines
    ]


def render(video: Path, work: Path, out: Path, start: float, end: float,
           video_filter: str = BLUR_FILL, captions: tuple[int, int] = CAPTIONS_LOW) -> Path:
    words = [w for s in json.loads((work / "transcript.json").read_text(encoding="utf-8"))["segments"] for w in s["words"]]
    ass = work / f"{out.stem}.ass"
    events = [f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,{text}" for a, b, text in caption_lines(words, start, end)]
    header = ASS_HEADER.format(alignment=captions[0], margin_v=captions[1])
    ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")

    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(video.resolve()),
            "-filter_complex", f"{video_filter},subtitles={ass.name}",
            "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "160k",
            str(out.resolve()),
        ],
        cwd=work, check=True,
    )
    return out
