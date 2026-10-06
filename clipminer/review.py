"""The review gate between score and render. `work/<slug>/review.json` holds the picks; the GUI
and GURT (in chat) both edit it, then it's approved and rendered."""
import json
import re
from pathlib import Path

from . import reframe, splice
from .render import BLUR_FILL, CAPTIONS_LOW, CAPTIONS_MID, CAPTIONS_SEAM, CURSE, render

# What Tko picks before pasting a link: kind -> (Finished_Clips folder, theme profile in skill.md).
KINDS = {"podcast": ("Podcast", "comedian-podcast"), "stream": ("Streaming", "streamer")}


def clip_cap(work: Path) -> int:
    """Tko's rule: at most 20 clips per video, 30 for a video over 3 hours."""
    duration = json.loads((work / "transcript.json").read_text(encoding="utf-8"))["duration"]
    return 30 if duration > 3 * 3600 else 20


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


def mark_overlaps(clips: list[dict], words: list[dict]) -> None:
    """GURT's and Sonnet's picks can land on the same moment; flag ticked pairs so it can't render twice
    by accident (run 8 shipped two cuts of the Gronk story)."""
    kept = [c for c in clips if c["keep"]]
    for c in clips:
        a, b = words[c["first"]]["start"], words[c["last"]]["end"]
        c["overlaps"] = [o["name"] for o in kept if o is not c and c["keep"]
                         and min(b, words[o["last"]]["end"]) - max(a, words[o["first"]]["start"]) > 5]


def save(work: Path, review: dict) -> None:
    words = transcript_words(work)
    review["clips"] = sorted((preview(c, words) for c in review["clips"]), key=lambda c: c["first"])
    mark_overlaps(review["clips"], words)
    (work / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")


# Tko's rule: these go on every post, on top of the clip's own hashtags.
REQUIRED_TAGS = ["#xybca", "#fyp", "#blowthisup", "#viral"]


def with_required_tags(description: str) -> str:
    lines = description.strip().splitlines() or [""]
    tagged = lines[-1].lstrip().startswith("#")
    tags = lines[-1].split() if tagged else []
    tags += [t for t in REQUIRED_TAGS if t not in tags]
    return "\n".join((lines[:-1] if tagged else lines) + [" ".join(tags)])


# Tko's rule: a post's text is clean even when the clip isn't. No curse word, nothing about sex or drugs,
# in the hook or in a hashtag. The rulebook carries the judgment; this only catches the plain words.
OFF_LIMITS = re.compile(
    r"porn\w*|sex\w*|nudes?|naked|horny|boobs?|tits?|penis\w*|vagina\w*|orgasm\w*|masturbat\w*|strippers?|"
    r"hookers?|onlyfans|fetish\w*|kink\w*|cum|blowjobs?|handjobs?|dildos?|threesomes?|orgy|orgies|"
    r"weed|stoned|stoners?|marijuana|cannabis|blunts?|bongs?|edibles?|cocaine|meth|heroin|shrooms|lsd|drugs?",
    re.IGNORECASE,
)
# Hashtags run words together (#tightshit), so these are searched for inside a word as well.
OFF_LIMITS_INSIDE = re.compile(r"fuck|shit|bitch|cunt|nigg|pussy|whore|slut|porn|(?<!sea)(?<!t)(?<!tumble)weed", re.IGNORECASE)


def off_limits(description: str) -> list[str]:
    words = re.findall(r"[A-Za-z']+|\*{2,}", description)
    return sorted({w for w in words if w[0] == "*" or CURSE.fullmatch(w) or OFF_LIMITS.fullmatch(w) or OFF_LIMITS_INSIDE.search(w)})


def next_number(out_dir: Path) -> int:
    # Numbers never repeat: the clip log refers to clips by number long after Tko moves or deletes the files.
    numbers = [int(m.group(1)) for f in out_dir.rglob("*.mp4") if (m := re.match(r"(\d+)_", f.name))]
    for run in (out_dir.parent / "clip_log").glob("run-*.md"):
        numbers += [int(n) for n in re.findall(r"^- \*\*(\d+) · ", run.read_text(encoding="utf-8"), re.M)]
    return max(numbers, default=0) + 1


def to_render(review: dict, work: Path) -> list[dict]:
    """The refusals come first so a second batch is turned down before its source is re-downloaded."""
    # Picks added after a render (a second batch) render on their own; finished ones are never redone.
    todo = [c for c in review["clips"] if c["keep"] and not c.get("rendered_as")]
    if not todo:
        raise RuntimeError(f"{work.name} has nothing new to render")
    kept, cap = sum(c["keep"] for c in review["clips"]), clip_cap(work)
    if kept > cap:
        raise RuntimeError(f"{kept} clips ticked, the limit for this video is {cap}: untick {kept - cap} in Review")
    unclean = [f"{c['name']} ({', '.join(off_limits(c['description']))})" for c in todo if off_limits(c["description"])]
    if unclean:
        raise RuntimeError("post descriptions can't swear or mention sex or drugs; reword in review.json: " + "; ".join(unclean))
    return todo


def render_approved(work: Path, video: Path, out_dir: Path) -> list[Path]:
    review = load(work)
    todo = to_render(review, work)
    words = transcript_words(work)
    W, H = reframe.frame_size(video)
    # A clip that died before its first file was written holds its number in review.json only.
    number = max([next_number(out_dir)] + [int(c["rendering_as"].split("_")[0]) + 1 for c in review["clips"] if "rendering_as" in c])
    info = json.loads((work / "info.json").read_text(encoding="utf-8")) if (work / "info.json").exists() else {}
    show = re.sub(r'[<>:"/\\|?*]+', "", info.get("channel") or info.get("title") or "").strip()[:60] or "Local files"
    kind = review.get("kind", "podcast")
    out_dir = out_dir / KINDS[kind][0] / show
    out_dir.mkdir(parents=True, exist_ok=True)
    # `facecam` in review.json overrides a wrong box; check work/<slug>/facecam.jpg before approving.
    cam = review.get("facecam") or (reframe.cam_box(video, work) if kind == "stream" else None)
    done = []
    for clip in todo:
        # A render that died partway (run 12: a blocked DLL) resumes under the number it was given, not a
        # new one; the stem is written down first because another clip can share the name and score.
        partial = "rendering_as" in clip
        stem = clip.get("rendering_as") or f"{number:02d}_s{clip['score']}_{clip['name']}"
        clip["rendering_as"] = stem
        save(work, review)
        source, start, end, kept = splice.build(video, work, words, clip, stem)
        fixes = clip["fixes"]
        # A fix to "" drops the word: Whisper wrote fake speaker names as spoken words in run 11.
        caption = [{**w, "word": " ".join(fixes.get(x, x) for x in w["word"].split())} for w in kept]
        caption = [w for w in caption if w["word"].strip()]
        done.append(render(source, work, out_dir / f"{stem}_blur.mp4", start, end, BLUR_FILL, CAPTIONS_LOW, caption))
        # A stream switches between gameplay and talking to the camera, so the layout is decided per clip.
        split, game = None, False
        if cam and reframe.shows_cam(source, start, end, cam):
            game = True
            zoomed = reframe.zooms(source, start, end, cam)
            # On the seam the caption would sit across the streamer's face once the camera goes full screen.
            where = CAPTIONS_LOW if zoomed else (5, reframe.cam_height(cam))
            done.append(render(source, work, out_dir / f"{stem}_game.mp4", start, end,
                               reframe.game_filter(cam, W, H, zoomed), where, caption))
        else:
            segments, split = reframe.plan(source, start, end, solo=kind == "stream")
            breaks = [w["end"] - start for w in caption if w["word"].rstrip().endswith((".", ",", "?", "!"))]
            shots = reframe.track_shots(segments, W, H, end - start, breaks)
            where = (CAPTIONS_MID[0], reframe.track_caption_y(shots, W, H, CAPTIONS_MID[1], CAPTIONS_LOW[1]))
            done.append(render(source, work, out_dir / f"{stem}_track.mp4", start, end,
                               reframe.track_filter(shots, W, H), where, caption))
        if split:
            done.append(render(source, work, out_dir / f"{stem}_split.mp4", start, end,
                               reframe.split_filter(split, W, H), CAPTIONS_SEAM, caption))
        if source != video:
            source.unlink()
        (out_dir / f"{stem}.txt").write_text(with_required_tags(clip["description"]) + "\n", encoding="utf-8")
        clip["rendered_as"] = clip.pop("rendering_as")
        save(work, review)
        print(f"[render]     {stem}  ({end - start:.1f}s, {'split' if split else 'game' if game else 'no split'})", flush=True)
        number += not partial
    review["status"] = "rendered"
    save(work, review)
    return done
