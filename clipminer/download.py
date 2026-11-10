import json
import re
import subprocess
from pathlib import Path

from yt_dlp import YoutubeDL


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_")[:60]


def english_audio(local: Path, work: Path) -> Path:
    """Tko's file as every stage hears it. Whisper, ffmpeg and the render all take the first audio track, so a file
    whose first track is a dub or a narrated one is copied (no re-encode) into work/ with only its plain English
    track: Rick and Morty S03E01's BDRip has Russian first, and its WEB copy only an audio-described English track.
    The copy is ClipMiner's own and is deleted after rendering; Tko's file is never touched."""
    tracks = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                        "stream=index:stream_tags=language,title", "-of", "json", str(local)],
                                       capture_output=True, text=True, check=True).stdout)["streams"]
    plain = lambda t: (t.get("tags", {}).get("language") in ("eng", "en")
                       and not re.search(r"descript|commentary|\bAD\b|\bDVS\b", t.get("tags", {}).get("title", ""), re.I))
    pick = next((t for t in tracks if plain(t)), None)
    if not tracks or pick is None or pick is tracks[0]:
        return local
    copy = work / "source.mkv"
    if not copy.exists():
        part = work / "source.part.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(local), "-map", "0:v:0", "-map", f"0:{pick['index']}",
                        "-map", "0:s?", "-c", "copy", str(part)], check=True)
        part.replace(copy)
    return copy


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
        return work, english_audio(local, work)

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


def subtitles(video: Path, work: Path) -> None:
    """A film's own English subtitles, SDH first: they name who is speaking, which Whisper can't. None is fine."""
    out = work / "subs_sdh.srt"
    if out.exists():
        return
    streams = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "s", "-show_entries",
                                         "stream=index:stream_tags=language,title", "-of", "json", str(video)],
                                        capture_output=True, text=True, check=True).stdout)["streams"]
    english = [s for s in streams if s.get("tags", {}).get("language") in ("eng", "en")]
    pick = next((s for s in english if "SDH" in s["tags"].get("title", "")), english[0] if english else None)
    if pick:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-map", f"0:{pick['index']}", str(out)], check=True)
