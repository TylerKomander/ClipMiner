"""The review gate between score and render. `work/<slug>/review.json` holds the picks; the GUI
and GURT (in chat) both edit it, then it's approved and rendered."""
import json
import re
from pathlib import Path

from . import reframe
from .render import BLUR_FILL, CAPTIONS_LOW, CAPTIONS_SEAM, mask_curses, render


def transcript_words(work: Path) -> list[dict]:
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    return [w for s in transcript["segments"] for w in s["words"]]


def entry(words: list[dict], name: str, score: int, first: int, last: int, by: str,
          payoff: str = "", reason: str = "", fixes: dict | None = None, description: str = "") -> dict:
    clip = {"name": name, "score": score, "first": first, "last": last, "by": by, "keep": True,
            "payoff": payoff, "reason": reason, "fixes": fixes or {}, "description": description}
    return preview(clip, words)


def preview(clip: dict, words: list[dict]) -> dict:
    """The dry run: a reviewer reads these before approving, so a clipped opener or payoff shows."""
    span = words[clip["first"]:clip["last"] + 1]
    clip["opens"] = " ".join(w["word"].strip() for w in span[:5])
    clip["closes"] = " ".join(w["word"].strip() for w in span[-5:])
    clip["seconds"] = round(span[-1]["end"] - span[0]["start"] + 0.45, 1)
    return clip


def load(work: Path) -> dict:
    return json.loads((work / "review.json").read_text(encoding="utf-8"))


def save(work: Path, review: dict) -> None:
    words = transcript_words(work)
    review["clips"] = sorted((preview(c, words) for c in review["clips"]), key=lambda c: c["first"])
    (work / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")


def next_number(out_dir: Path) -> int:
    # Used-Clips counts too: numbers never repeat, even after Tko moves posted clips.
    numbers = [int(m.group(1)) for f in out_dir.rglob("*.mp4") if (m := re.match(r"(\d+)_", f.name))]
    return max(numbers, default=0) + 1


def render_approved(work: Path, video: Path, out_dir: Path) -> list[Path]:
    review = load(work)
    if review["status"] == "rendered":
        raise RuntimeError(f"{work.name} is already rendered")
    words = transcript_words(work)
    W, H = reframe.frame_size(video)
    number = next_number(out_dir)
    done = []
    for clip in (c for c in review["clips"] if c["keep"]):
        fixes = clip["fixes"]
        caption = [{**w, "word": " ".join(fixes.get(x, x) for x in w["word"].split())}
                   for w in words[clip["first"]:clip["last"] + 1]]
        start, end = caption[0]["start"] - 0.15, caption[-1]["end"] + 0.3
        stem = f"{number:02d}_s{clip['score']}_{clip['name']}"
        segments, split = reframe.plan(video, start, end)
        done.append(render(video, work, out_dir / f"{stem}_blur.mp4", start, end, BLUR_FILL, CAPTIONS_LOW, caption))
        done.append(render(video, work, out_dir / f"{stem}_track.mp4", start, end,
                           reframe.track_filter(segments, W, H), CAPTIONS_LOW, caption))
        if split:
            done.append(render(video, work, out_dir / f"{stem}_split.mp4", start, end,
                               reframe.split_filter(split, W, H), CAPTIONS_SEAM, caption))
        text = "\n".join(" ".join(mask_curses(word) for word in line.split(" ")) for line in clip["description"].splitlines())
        (out_dir / f"{stem}.txt").write_text(text + "\n", encoding="utf-8")
        clip["rendered_as"] = stem
        print(f"[render]     {stem}  ({end - start:.1f}s, split {'yes' if split else 'no'})", flush=True)
        number += 1
    review["status"] = "rendered"
    save(work, review)
    return done
