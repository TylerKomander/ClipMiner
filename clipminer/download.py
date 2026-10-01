import json
import re
from pathlib import Path

from yt_dlp import YoutubeDL


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_")[:60]


def fetch(source: str, work_root: Path) -> tuple[Path, Path]:
    local = Path(source)
    if local.is_file():
        work = work_root / slugify(local.stem)
        work.mkdir(parents=True, exist_ok=True)
        return work, local

    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(source, download=False)
    work = work_root / slugify(info["id"])
    work.mkdir(parents=True, exist_ok=True)
    video = work / "source.mp4"
    meta = work / "info.json"
    if video.exists() and meta.exists():
        return work, video

    opts = {
        "quiet": True,
        "noprogress": True,
        "format": "bv*[height<=1080]+ba/b[height<=1080]",
        "merge_output_format": "mp4",
        "outtmpl": str(video),
    }
    with YoutubeDL(opts) as ydl:
        ydl.process_ie_result(info, download=True)
    meta.write_text(json.dumps({
        "id": info["id"],
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "duration": info.get("duration"),
        "heatmap": info.get("heatmap"),
    }, indent=2), encoding="utf-8")
    return work, video
