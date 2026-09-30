import json
import re
import statistics
import subprocess
from pathlib import Path

MOMENTARY = re.compile(r"t:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?[\d.]+|-inf)")


def loudness(video: Path, work: Path) -> Path:
    out = work / "loudness.json"
    if out.exists():
        return out

    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn", "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    per_second: dict[int, list[float]] = {}
    for t, m in MOMENTARY.findall(proc.stderr):
        if m != "-inf":
            per_second.setdefault(int(float(t)), []).append(float(m))
    series = [{"t": s, "m": max(v)} for s, v in sorted(per_second.items())]
    median = statistics.median(p["m"] for p in series)
    out.write_text(json.dumps({"median": median, "series": series}), encoding="utf-8")
    return out
