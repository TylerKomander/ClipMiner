import json
import re
import subprocess
from pathlib import Path

from yt_dlp import YoutubeDL


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_")[:60]


def fetch(source: str, work_root: Path) -> tuple[Path, Path]:
    local = Path(source)
    if local.is_file():
        work = work_root / slugify(local.stem)
        work.mkdir(parents=True, exist_ok=True)
        meta = work / "info.json"
        if not meta.exists():
            duration = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       str(local)], capture_output=True, text=True, check=True).stdout
            # `path` marks Tko's own file: the render reads it in place and never deletes it.
            meta.write_text(json.dumps({"id": work.name, "title": local.stem, "channel": "",
                                        "duration": float(duration), "path": str(local.resolve())}, indent=2), encoding="utf-8")
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
