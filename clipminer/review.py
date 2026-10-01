"""The review gate between score and render. `work/<slug>/review.json` holds the picks; the GUI
and GURT (in chat) both edit it, then it's approved and rendered."""
import json
import re
from pathlib import Path

from . import reframe, splice
from .render import BLUR_FILL, CAPTIONS_LOW, CAPTIONS_SEAM, mask_curses, render


def transcript_words(work: Path) -> list[dict]:
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    return [w for s in transcript["segments"] for w in s["words"]]


def entry(words: list[dict], name: str, score: int, first: int, last: int, by: str,
          payoff: str = "", reason: str = "", fixes: dict | None = None, description: str = "",
          cuts: list[list[int]] | None = None) -> dict:
    clip = {"name": name, "score": score, "first": first, "last": last, "by": by, "keep": True,
            "payoff": payoff, "reason": reason, "fixes": fixes or {}, "description": description, "cuts": cuts or []}
    return preview(clip, words)


def preview(clip: dict, words: list[dict]) -> dict:
    """The dry run: a reviewer reads these before approving, so a clipped opener or payoff shows."""
    clip.setdefault("cuts", [])
    span = words[clip["first"]:clip["last"] + 1]
    clip["opens"] = " ".join(w["word"].strip() for w in span[:5])
    clip["closes"] = " ".join(w["word"].strip() for w in span[-5:])
    clip["seconds"] = splice.seconds(words, clip["first"], clip["last"], clip["cuts"])
    clip["spliced_out"] = [f"{' '.join(w['word'].strip() for w in words[a:b + 1][:6])}… "
                           f"({words[b]['end'] - words[a]['start']:.0f}s)" for a, b in clip["cuts"]]
    return clip


def load(work: Path) -> dict:
    return json.loads((work / "review.json").read_text(encoding="utf-8"))


def save(work: Path, review: dict) -> None:
    words = transcript_words(work)
    review["clips"] = sorted((preview(c, words) for c in review["clips"]), key=lambda c: c["first"])
    (work / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")


# Tko's rule: these go on every post, on top of the clip's own hashtags.
REQUIRED_TAGS = ["#xybca", "#fyp", "#blowthisup", "#viral"]


def with_required_tags(description: str) -> str:
    lines = description.strip().splitlines() or [""]
    tagged = lines[-1].lstrip().startswith("#")
    tags = lines[-1].split() if tagged else []
    tags += [t for t in REQUIRED_TAGS if t not in tags]
    return "\n".join((lines[:-1] if tagged else lines) + [" ".join(tags)])


def next_number(out_dir: Path) -> int:
    # Numbers never repeat: the clip log refers to clips by number long after Tko moves or deletes the files.
    numbers = [int(m.group(1)) for f in out_dir.rglob("*.mp4") if (m := re.match(r"(\d+)_", f.name))]
    for run in (out_dir.parent / "clip_log").glob("run-*.md"):
        numbers += [int(n) for n in re.findall(r"^- \*\*(\d+) · ", run.read_text(encoding="utf-8"), re.M)]
    return max(numbers, default=0) + 1


def render_approved(work: Path, video: Path, out_dir: Path) -> list[Path]:
    review = load(work)
    if review["status"] == "rendered":
        raise RuntimeError(f"{work.name} is already rendered")
    words = transcript_words(work)
    W, H = reframe.frame_size(video)
    number = next_number(out_dir)
    info = json.loads((work / "info.json").read_text(encoding="utf-8")) if (work / "info.json").exists() else {}
    show = re.sub(r'[<>:"/\\|?*]+', "", info.get("channel") or info.get("title") or "").strip()[:60] or "Local files"
    out_dir = out_dir / show
    out_dir.mkdir(parents=True, exist_ok=True)
    done = []
    for clip in (c for c in review["clips"] if c["keep"]):
        stem = f"{number:02d}_s{clip['score']}_{clip['name']}"
        source, start, end, kept = splice.build(video, work, words, clip, stem)
        fixes = clip["fixes"]
        caption = [{**w, "word": " ".join(fixes.get(x, x) for x in w["word"].split())} for w in kept]
        segments, split = reframe.plan(source, start, end)
        done.append(render(source, work, out_dir / f"{stem}_blur.mp4", start, end, BLUR_FILL, CAPTIONS_LOW, caption))
        done.append(render(source, work, out_dir / f"{stem}_track.mp4", start, end,
                           reframe.track_filter(segments, W, H), CAPTIONS_LOW, caption))
        if split:
            done.append(render(source, work, out_dir / f"{stem}_split.mp4", start, end,
                               reframe.split_filter(split, W, H), CAPTIONS_SEAM, caption))
        if source != video:
            source.unlink()
        text = "\n".join(" ".join(mask_curses(word) for word in line.split(" ")) for line in with_required_tags(clip["description"]).splitlines())
        (out_dir / f"{stem}.txt").write_text(text + "\n", encoding="utf-8")
        clip["rendered_as"] = stem
        print(f"[render]     {stem}  ({end - start:.1f}s, split {'yes' if split else 'no'})", flush=True)
        number += 1
    review["status"] = "rendered"
    save(work, review)
    return done
