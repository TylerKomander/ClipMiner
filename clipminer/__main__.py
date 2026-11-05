import argparse
import json
import time
from pathlib import Path

from . import review
from .download import fetch
from .score import score
from .signals import loudness
from .transcribe import transcribe

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue.txt"
FINISHED = ROOT / "Finished_Clips"


def prepare(source: str, model: str, kind: str) -> Path:
    t0 = time.perf_counter()
    work, video = fetch(source, ROOT / "work")
    print(f"[download]   {video}  ({time.perf_counter() - t0:.1f}s)")

    t0 = time.perf_counter()
    transcript = transcribe(video, work, model)
    print(f"[transcribe] {transcript}  ({time.perf_counter() - t0:.1f}s)")

    t0 = time.perf_counter()
    print(f"[loudness]   {loudness(video, work)}  ({time.perf_counter() - t0:.1f}s)")

    t0 = time.perf_counter()
    score(work, kind=kind)
    print(f"[score]      {work / 'review.json'} awaiting review  ({time.perf_counter() - t0:.1f}s)")
    return work


def finish(work: Path) -> list[Path]:
    """Render the approved picks, then drop a downloaded source: Tko's rule is no full videos kept.
    A local file is Tko's own and stays where it is."""
    info = json.loads((work / "info.json").read_text(encoding="utf-8"))
    local = info.get("path")
    video = Path(local) if local else work / "source.mp4"
    review.to_render(review.load(work), work)
    if local and not video.exists():
        raise RuntimeError(f"{local} has moved or been deleted: put it back to render")
    if not video.exists():
        # A second batch after the source was deleted: fetch it again (info.json has the id).
        fetch(f"https://www.youtube.com/watch?v={info['id']}", ROOT / "work")
    clips = review.render_approved(work, video, FINISHED)
    if not local:
        video.unlink()
    return clips


def run_queue(model: str, kind: str) -> None:
    while True:
        lines = QUEUE.read_text(encoding="utf-8").splitlines()
        pending = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        if not pending:
            print("[queue]      empty")
            return
        source = pending[0]
        print(f"[queue]      {source}  ({len(pending) - 1} after this)")
        # A dead link shouldn't stall a night's batch; it's kept in the file, commented, for a look later.
        try:
            prepare(source, model, kind)
            status = None
        except Exception as e:
            status = f"# failed: {type(e).__name__}: {e}".splitlines()[0]
            print(f"[queue]      {status}")
        # Done lines leave the file: once the source is deleted after rendering, a rerun would download it again.
        lines = QUEUE.read_text(encoding="utf-8").splitlines()
        i = next(i for i, line in enumerate(lines) if line.strip() == source)
        lines[i:i + 1] = [status, f"# {source}"] if status else []
        QUEUE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(prog="clipminer")
    parser.add_argument("source", nargs="?", help="YouTube URL or local media file; omit to work through queue.txt")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    parser.add_argument("--kind", choices=list(review.KINDS), default="podcast",
                        help="what the video is: sets the theme profile and the layouts")
    parser.add_argument("--render", metavar="SLUG", help="render the approved picks in work/SLUG/review.json")
    args = parser.parse_args()

    if args.render:
        finish(ROOT / "work" / args.render)
    elif args.source:
        prepare(args.source, args.model, args.kind)
    else:
        run_queue(args.model, args.kind)


if __name__ == "__main__":
    main()
