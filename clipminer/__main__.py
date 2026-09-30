import argparse
import time
from pathlib import Path

from .download import fetch
from .transcribe import transcribe

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(prog="clipminer")
    parser.add_argument("source", help="YouTube URL or local media file")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    args = parser.parse_args()

    t0 = time.perf_counter()
    work, video = fetch(args.source, ROOT / "work")
    print(f"[download]   {video}  ({time.perf_counter() - t0:.1f}s)")

    t0 = time.perf_counter()
    transcript = transcribe(video, work, args.model)
    print(f"[transcribe] {transcript}  ({time.perf_counter() - t0:.1f}s)")


if __name__ == "__main__":
    main()
