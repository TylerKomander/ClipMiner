import json
import os
import re
import winreg
from pathlib import Path

import anthropic

from . import review, splice

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-sonnet-5-5"
LINE_SECONDS = 15
CHUNK_SECONDS = 20 * 60
OVERLAP_SECONDS = 60
MIN_LEN, MAX_LEN = 10, 40
MAX_SPAN = 240  # a spliced story may cover this much of the episode (run 9: green-room setup sat 3 min before its payoff)
SPIKE_LU = 6

def _object(properties: dict) -> dict:
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


CLIP_SCHEMA = _object({
    "clips": {"type": "array", "items": _object({
        "name": {"type": "string", "description": "short kebab-case name"},
        "approx_start": {"type": "string", "description": "h:mm:ss of the reading line the clip starts in"},
        "approx_end": {"type": "string", "description": "h:mm:ss of the reading line the clip ends in"},
        "first_words": {"type": "string", "description": "the clip's first 5+ words, copied exactly"},
        "last_words": {"type": "string", "description": "the clip's last 5+ words, ending on the payoff, copied exactly"},
        "payoff": {"type": "string", "description": "the exact line a stranger would laugh at or say 'wait, what?' to, copied from the text"},
        "shape": {"type": "string"},
        "score": {"type": "integer", "description": "1-10 per the rubric"},
        "reason": {"type": "string", "description": "one line: why this score"},
        "description": {"type": "string", "description": "the post text, following the rulebook's 'Post description' section"},
        "cuts": {"type": "array", "description": "stretches inside the clip to splice out (a tangent, a repeated setup, cross-talk); empty if none",
                 "items": _object({"from_words": {"type": "string", "description": "first 5+ words of the stretch to remove, copied exactly"},
                                   "to_words": {"type": "string", "description": "last 5+ words of the stretch to remove, copied exactly"}})},
    })},
    "rejected": {"type": "array", "items": _object({"approx_start": {"type": "string"}, "why": {"type": "string"}})},
})


RECAP_SCHEMA = _object({
    "name": {"type": "string", "description": "short kebab-case name for the file"},
    "score": {"type": "integer", "description": "1-10: how well these moments tell the film to someone who hasn't seen it"},
    "reason": {"type": "string", "description": "one line: why this score"},
    "description": {"type": "string", "description": "the post text, following the rulebook's movie-recap profile"},
    "moments": {"type": "array", "items": _object({
        "approx_start": {"type": "string", "description": "h:mm:ss of the reading line the moment is in"},
        "first_words": {"type": "string", "description": "the moment's first 4+ words, copied exactly"},
        "last_words": {"type": "string", "description": "the moment's last 4+ words, copied exactly"},
        "why": {"type": "string", "description": "which beat of the story this carries"},
    })},
})
# Run 21: a 90s cap made jokes lose their replies (Tko: "funny over everything"). A Short must render under 3
# minutes, and the render runs ~12% over speech (pauses, holds): 164s of speech came out 183.6s.
RECAP_LEN = (50, 155)
RECAP_MOMENTS = (8, 24)
MOMENT_WORDS = 160

# Besides the recap, a film's standalone laughs (Tko, 2026-11-09): one joke each, spliced from up to four pieces
# when its set-up sits elsewhere in the film. 40s at most, as a podcast clip (Tko: the 45-60s cuts ran long).
FUNNY_SCHEMA = _object({
    "clips": {"type": "array", "items": _object({
        "name": {"type": "string", "description": "short kebab-case name"},
        "score": {"type": "integer", "description": "1-10 per the rubric"},
        "reason": {"type": "string", "description": "one line: why this score"},
        "payoff": {"type": "string", "description": "the exact line a stranger laughs at, copied from the text"},
        "description": {"type": "string", "description": "the post text, following the movie-recap profile's funny-moment rules"},
        "moments": {"type": "array", "description": "1-4 pieces played back to back in film order",
                    "items": RECAP_SCHEMA["properties"]["moments"]["items"]},
    })},
    "rejected": {"type": "array", "items": _object({"approx_start": {"type": "string"}, "why": {"type": "string"}})},
})
FUNNY_LEN = (10, 40)
FUNNY_PIECES = 4
FUNNY_WORDS = 400  # a one-piece joke may run its whole 40s, past the recap moment's 160 words


def hms(t: float) -> str:
    t = int(t)
    return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}"


def seconds(stamp: str) -> float:
    total = 0.0
    for part in stamp.strip().split(":"):
        total = total * 60 + float(part)
    return total


def reading_lines(work: Path) -> list[tuple[float, str]]:
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    info = json.loads((work / "info.json").read_text(encoding="utf-8"))
    loud = json.loads((work / "loudness.json").read_text(encoding="utf-8"))
    over = {p["t"]: p["m"] - loud["median"] for p in loud["series"]}
    heatmap = info.get("heatmap") or []

    lines, words, line_start = [], [], None
    for seg in transcript["segments"]:
        for w in seg["words"]:
            if line_start is None:
                line_start = w["start"]
            words.append(w["word"].strip())
            elapsed = w["end"] - line_start
            # Whisper's lowercase stretches have no punctuation to break on.
            if elapsed >= LINE_SECONDS * 1.7 or (elapsed >= LINE_SECONDS and w["word"].rstrip()[-1:] in ".?!,"):
                lines.append((line_start, w["end"], " ".join(words)))
                words, line_start = [], None
    if words:
        lines.append((line_start, transcript["duration"], " ".join(words)))

    out = []
    for start, end, text in lines:
        marks = ""
        spikes = [over[t] for t in range(int(start), int(end) + 1) if over.get(t, -99) >= SPIKE_LU]
        if spikes:
            marks += f" <L{len(spikes)}/+{max(spikes):.0f}>"
        heat = max((b["value"] for b in heatmap if b["start_time"] < end and b["end_time"] > start), default=0)
        if heat >= 0.3:
            marks += f" <H{heat:.2f}>"
        out.append((start, f"{hms(start)} {text}{marks}"))
    return out


def chunks(lines: list[tuple[float, str]], span: tuple[float, float]) -> list[tuple[float, list[str]]]:
    out, t = [], span[0]
    while t < span[1]:
        # Overlap on both sides: a story that crosses a boundary must be whole in one part (run 11 lost
        # hide-and-seek and the compression shirt at 20:00 and 40:00). Twins are deduped after scoring.
        piece = [text for start, text in lines
                 if t - OVERLAP_SECONDS <= start < min(t + CHUNK_SECONDS + OVERLAP_SECONDS, span[1])]
        if piece:
            out.append((t, piece))
        t += CHUNK_SECONDS
    return out


# Sections of a run file about running it, not picking: they cost tokens in every call and teach the scorer nothing.
OFF_PROMPT = ("Picked by", "Inputs used", "Transcript", "Faces", "Camera", "Render check", "What went wrong",
              "Fixes this run", "Blind test")


def example_text(name: str) -> str:
    keep, out = True, []
    for line in (ROOT / "clip_log" / name).read_text(encoding="utf-8").splitlines():
        label = re.match(r"(?:\*\*|###\s+)([^*:(]+)", line)
        if label:
            keep = not label.group(1).strip().startswith(OFF_PROMPT)
        if keep:
            out.append(line)
    return "\n".join(out)


def system_prompt(examples: list[str], theme: str) -> str:
    return "\n\n".join([
        "You pick short-form clips from long videos. Follow the rulebook exactly.",
        f"The theme for this video is `{theme}`: use that profile in Part A and ignore the other profiles. "
        "Part B applies to every theme.",
        "# RULEBOOK\n" + (ROOT / "skill.md").read_text(encoding="utf-8"),
        "# CLIP LOG INDEX\n" + (ROOT / "clip_log" / "INDEX.md").read_text(encoding="utf-8"),
        *(f"# WORKED EXAMPLE RUN\n{example_text(name)}" for name in examples),
    ])


def user_prompt(info: dict, begin: float, piece: list[str], part: int, parts: int, words_per_second: float) -> str:
    heat_note = "present" if info.get("heatmap") else "missing for this video"
    return (
        f"Video: {info.get('title')}\nLength: {hms(info.get('duration') or 0)}\nHeatmap: {heat_note}\n"
        f"This is part {part} of {parts}, covering {hms(begin)} to {hms(begin + CHUNK_SECONDS)}. The minute before "
        "and after overlaps the neighbouring parts: pick a clip there only if it crosses the boundary, so no story "
        "is cut off by it. Duplicates are removed in code.\n\n"
        f"Reading file: one line per ~{LINE_SECONDS}s as `h:mm:ss text`. <Ln/+x> = n seconds at least "
        f"{SPIKE_LU} LU over the episode median, max +x. <H0.xx> = heatmap value of the overlapping bucket.\n\n"
        f"Speech here runs ~{words_per_second:.1f} words/s, so a 10–35s clip is about "
        f"{10 * words_per_second:.0f}–{35 * words_per_second:.0f} words. Count before you submit.\n"
        "Before submitting a clip, quote its payoff: the line a stranger laughs at or says 'wait, what?' to. "
        "Warm conversation, praise, or a story with no turn is not a payoff. No payoff, no clip.\n"
        "Long stories: you may splice. List `cuts` (a tangent, a repeated setup, cross-talk) and the clip is "
        "joined with hard jump cuts; dead air is trimmed only where the audio really goes quiet, so do not count on "
        "it: the kept words themselves must run 10–40s, still make "
        f"sense cold, and the whole window may span up to {MAX_SPAN // 60} minutes. Never cut the payoff "
        "or the line that sets it up. A payoff whose setup came minutes earlier is a splice (setup, then payoff), "
        "not a reject and not a clip of the payoff alone.\n"
        "Submit every clip scoring 8+ and the notable rejects; a 7 is a reject. "
        "first_words and last_words must be copied exactly from the text.\n\n"
        + "\n".join(piece)
    )


def matches(norm: list[str], i: int, quote: list[str]) -> bool:
    # Allow one miscopied word in a 4-word quote (lowercase stretches and fillers trip up exact quotes),
    # never in a shorter one: "Yeah, yeah." with one miss matches any "yeah" (run 9).
    need = len(quote) - 1 if len(quote) >= 4 else len(quote)
    return sum(a == b for a, b in zip(norm[i:i + len(quote)], quote)) >= need


def snap(words: list[dict], norm: list[str], near: float, quote: list[str], window: float) -> int | None:
    best = None
    for i, w in enumerate(words):
        if abs(w["start"] - near) <= window and matches(norm, i, quote):
            if best is None or abs(w["start"] - near) < abs(words[best]["start"] - near):
                best = i
    return best


def first_after(norm: list[str], quote: list[str], lo: int, hi: int) -> int | None:
    return next((i for i in range(lo, hi + 1) if matches(norm, i, quote)), None)


def locate(clip: dict, words: list[dict], norm: list[str]) -> str | None:
    first = re.findall(r"[a-z0-9']+", clip["first_words"].lower())[:4]
    last = re.findall(r"[a-z0-9']+", clip["last_words"].lower())[-4:]
    i = snap(words, norm, seconds(clip["approx_start"]), first, 60)
    j = snap(words, norm, seconds(clip["approx_end"]), last, 90)
    if i is None or j is None:
        return "first or last words not found in the transcript"
    clip["first"], clip["last"] = i, j + len(last) - 1
    clip["start"], clip["end"] = words[i]["start"], words[clip["last"]]["end"]
    if clip["end"] - clip["start"] > MAX_SPAN:
        return f"spans {clip['end'] - clip['start']:.0f}s of the episode, over {MAX_SPAN}s"
    clip["cut_ranges"] = []
    for cut in clip.get("cuts", []):
        head = re.findall(r"[a-z0-9']+", cut["from_words"].lower())[:4]
        tail = re.findall(r"[a-z0-9']+", cut["to_words"].lower())[-4:]
        # Cuts come in order; each one starts after the last and ends after its own start.
        lo = clip["cut_ranges"][-1][1] + 1 if clip["cut_ranges"] else clip["first"] + 1
        a = first_after(norm, head, lo, clip["last"] - 1)
        b = None if a is None else first_after(norm, tail, a, clip["last"] - len(tail))
        if b is None:
            return f"cut \"{cut['from_words']}\" … \"{cut['to_words']}\" not found inside the clip"
        clip["cut_ranges"].append([a, b + len(tail) - 1])
    length = splice.seconds(words, clip["first"], clip["last"], clip["cut_ranges"])
    if not MIN_LEN <= length <= MAX_LEN:
        return f"{length:.0f}s after cuts, outside {MIN_LEN}-{MAX_LEN}s"
    return None


def api_key() -> str | None:
    # A process keeps the environment it was launched with, so a key changed with setx while the app
    # is open (or from a terminal opened earlier) never reaches it. Read the stored value each time.
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as env:
            return winreg.QueryValueEx(env, "ANTHROPIC_API_KEY")[0]
    except OSError:
        return os.environ.get("ANTHROPIC_API_KEY")


def ask(client, model: str, system: list, messages: list, part: int, schema: dict = CLIP_SCHEMA) -> tuple[str, dict]:
    with client.messages.stream(
        model=model,
        max_tokens=64000,
        system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=messages,
    ) as stream:
        response = stream.get_final_message()
    if response.stop_reason == "max_tokens":
        raise RuntimeError(f"part {part} hit max_tokens")
    usage = {key: getattr(response.usage, key) or 0 for key in ("input_tokens", "cache_read_input_tokens", "output_tokens")}
    return next(b.text for b in response.content if b.type == "text"), usage


def retry_prompt(long: list[tuple[dict, str]], words_per_second: float) -> str:
    listed = "\n".join(f"- {c['name']}: {problem}" for c, problem in long)
    return (
        f"Measured from the word timestamps, these picks run too long:\n{listed}\n\n"
        f"The kept part must be 10–40s, about {40 * words_per_second:.0f} words at this show's pace. For each one, "
        "splice harder: cut more of the middle (tangents, repeats, a host's interjection), start at the latest line "
        "that still makes sense, and keep the ending and its payoff. If it can't fit without losing the payoff, "
        "leave it out. Return only these clips, revised, with the same names; `rejected` may be empty."
    )


def recent_runs(theme: str, count: int = 3, fallback: bool = True) -> list[str]:
    runs = sorted((ROOT / "clip_log").glob("run-*.md"))
    # A new theme has no runs yet: the other theme's runs still show the universal rules applied.
    # An unreviewed run is Sonnet's own picks: showing them as examples would teach it from itself.
    own = [p for p in runs if f"**Theme:** `{theme}`" in (text := p.read_text(encoding="utf-8"))
           and "**No review by GURT.**" not in text]
    return [p.name for p in (own or (runs if fallback else []))[-count:]]


def recap_prompt(info: dict, lines: list[str], words_per_second: float, subs: str) -> str:
    return (
        f"Film: {info.get('title')}\nLength: {hms(info.get('duration') or 0)}\n\n"
        "Make ONE recap short that tells this whole film's story as a supercut of its own dialogue, in film order: "
        "who the main character is and what they want, the conflict, the turn, and how it ends. Follow the "
        "movie-recap profile's step-by-step method and write down each step before the next: the main thread only, "
        "funny lines carry the story, every scene change and every pay-off set up, a cold-stranger retell before you "
        f"submit. Pick {RECAP_MOMENTS[0]}-{RECAP_MOMENTS[1]} moments, each one a whole joke: its set-up, the punchline and the "
        "reply or topper after it, however long that runs. Never trim inside a joke to save time; drop a whole weaker "
        f"joke instead. A moment over {MOMENT_WORDS} words splits into two back to back, which play as one. The "
        "ending may be spoiled. "
        f"Together they must run {RECAP_LEN[0]}-{RECAP_LEN[1]}s of speech: about "
        f"{RECAP_LEN[0] * words_per_second:.0f}-{RECAP_LEN[1] * words_per_second:.0f} words at this film's pace. "
        "Count before you submit. first_words and last_words must be copied exactly from the text; a moment never "
        "ends before its joke's reply.\n\n"
        f"Reading file: one line per ~{LINE_SECONDS}s as `h:mm:ss text`.\n\n" + "\n".join(lines)
        + (f"\n\nThe film's own subtitles, for names and who speaks only (quote from the reading file):\n\n{subs}" if subs else "")
    )


def funny_prompt(info: dict, lines: list[str], words_per_second: float, subs: str) -> str:
    return (
        f"Film: {info.get('title')}\nLength: {hms(info.get('duration') or 0)}\n\n"
        "The recap is made separately. Here, find the film's FUNNY MOMENTS: each one a standalone short of one whole "
        "joke a stranger laughs at without having seen the film, following the movie-recap profile's funny-moment "
        "rules. Side plots count here. A clip is 1-4 pieces of dialogue played back to back in film order: one piece "
        f"when the scene stands alone; more when the joke needs a set-up from elsewhere (who someone is, an earlier "
        f"line it calls back to). Each clip runs {FUNNY_LEN[0]}-{FUNNY_LEN[1]}s of speech: about "
        f"{FUNNY_LEN[0] * words_per_second:.0f}-{FUNNY_LEN[1] * words_per_second:.0f} words at this film's pace. Count "
        "before you submit. Submit only clips scoring 8+; a film may have none, and an empty list is a fine answer. "
        "Never pad. first_words and last_words must be copied exactly from the text; a piece never ends before its "
        "joke's reply.\n\n"
        f"Reading file: one line per ~{LINE_SECONDS}s as `h:mm:ss text`.\n\n" + "\n".join(lines)
        + (f"\n\nThe film's own subtitles, for names and who speaks only (quote from the reading file):\n\n{subs}" if subs else "")
    )


def place_moments(picks: dict, words: list[dict], norm: list[str],
                  count: tuple[int, int] = (RECAP_MOMENTS[0] - 2, RECAP_MOMENTS[1] + 2),
                  reach: int = MOMENT_WORDS) -> tuple[list[list[int]], str | None]:
    """Word ranges for each moment, in film order, and what is wrong with them (None if nothing)."""
    ranges = []
    for m in picks["moments"]:
        head = re.findall(r"[a-z0-9']+", m["first_words"].lower())[:4]
        tail = re.findall(r"[a-z0-9']+", m["last_words"].lower())[-4:]
        i = snap(words, norm, seconds(m["approx_start"]), head, 60)
        j = None if i is None else first_after(norm, tail, i, min(i + reach, len(words) - len(tail)))
        if j is None:
            return [], f"moment \"{m['first_words']}\" … \"{m['last_words']}\" not found near {m['approx_start']}"
        ranges.append([i, j + len(tail) - 1])
    ranges.sort()
    if any(b[0] <= a[1] for a, b in zip(ranges, ranges[1:])):
        return [], "two moments overlap"
    if not count[0] <= len(ranges) <= count[1]:
        return ranges, f"{len(ranges)} moments, asked for {count[0]}-{count[1]}"
    # The blind test's small models stopped moments at reading-file row wraps, before the punchline.
    cut_short = [words[j]["word"].strip() for _, j in ranges if words[j]["word"].rstrip()[-1:] not in ".?!"]
    if cut_short:
        return ranges, f"{len(cut_short)} moment(s) stop mid-sentence (on: {', '.join(cut_short)})"
    return ranges, None


def as_cuts(ranges: list[list[int]]) -> list[list[int]]:
    return [[a[1] + 1, b[0] - 1] for a, b in zip(ranges, ranges[1:]) if b[0] - 1 >= a[1] + 1]


def recap(work: Path, model: str, theme: str) -> Path:
    """A movie: one call over the whole film, since the story arc has to be seen at once. The moments land in
    review.json as one clip whose cuts are everything between them."""
    info = json.loads((work / "info.json").read_text(encoding="utf-8"))
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    words = [w for s in transcript["segments"] for w in s["words"]]
    norm = [re.sub(r"[^a-z0-9']", "", w["word"].lower()) for w in words]
    # Over speech only: a film is half silence, and the runtime pace (Atlanta 1.3 w/s against 2.9 in the
    # recap) asked for 40s recaps.
    words_per_second = len(words) / sum(s["end"] - s["start"] for s in transcript["segments"])
    lines = [text for _, text in reading_lines(work)]
    subs = (work / "subs_sdh.srt").read_text(encoding="utf-8") if (work / "subs_sdh.srt").exists() else ""
    # Only movie runs teach a recap; podcast runs would cost tokens and teach the wrong shape. Cached: the
    # funny-moments call sends the same system prompt right after.
    system = [{"type": "text", "text": system_prompt(recent_runs(theme, fallback=False), theme),
               "cache_control": {"type": "ephemeral"}}]
    out = work / f"recap-{model}.json"
    if out.exists():
        picks = json.loads(out.read_text(encoding="utf-8"))
    else:
        client = anthropic.Anthropic(api_key=api_key())
        messages = [{"role": "user", "content": recap_prompt(info, lines, words_per_second, subs)}]
        text, usage = ask(client, model, system, messages, 1, RECAP_SCHEMA)
        picks = json.loads(text)
        ranges, problem = place_moments(picks, words, norm)
        length = splice.seconds(words, ranges[0][0], ranges[-1][1], as_cuts(ranges)) if ranges else 0
        if problem or not RECAP_LEN[0] <= length <= RECAP_LEN[1]:
            # Same as the clip retry: show it what was measured once, instead of code throwing the recap away.
            messages += [{"role": "assistant", "content": text}, {"role": "user", "content": (
                f"Measured from the word timestamps: {problem or f'the moments run {length:.0f}s'}. Revise and "
                f"resubmit the whole recap: {RECAP_LEN[0]}-{RECAP_LEN[1]}s of speech, quotes copied exactly.")}]
            text, retry = ask(client, model, system, messages, 1, RECAP_SCHEMA)
            picks = json.loads(text)
            usage = {key: usage[key] + retry[key] for key in usage}
        picks["usage"] = usage
        out.write_text(json.dumps(picks, indent=2, ensure_ascii=False), encoding="utf-8")

    ranges, problem = place_moments(picks, words, norm)
    if not ranges:
        raise RuntimeError(f"recap unusable: {problem}; delete {out.name} to ask again")
    entry = review.entry(words, picks["name"], picks["score"], ranges[0][0], ranges[-1][1], model, "",
                         picks["reason"] + (f" Check: {problem}." if problem else ""),
                         description=picks["description"], cuts=as_cuts(ranges))
    entry["recap"] = True
    print(f"[score]      recap: {len(ranges)} moments, {entry['seconds']:.0f}s")
    # Saved first: a failed funny-moments call must not cost the recap its place in Review.
    if not (work / "review.json").exists():
        review.save(work, {"status": "awaiting", "model": model, "kind": "movie", "clips": [entry]})
    funnies = funny(work, model, system, info, lines, words_per_second, subs, words, norm)
    # Added to whatever is in Review, nothing there touched: a film recapped before funny moments existed
    # held only its recap, so a clip without the flag is that recap.
    data = review.load(work)
    for c in data["clips"]:
        c.setdefault("recap", True)
    names = {c["name"] for c in data["clips"]}
    added = [f for f in funnies if f["name"] not in names]
    if added:
        data["clips"] += added
        # Reopened only for something to render: an all-unticked batch would sit in Review with no way out.
        if any(f["keep"] for f in added):
            data["status"] = "awaiting"
        review.save(work, data)
    return out


def funny(work: Path, model: str, system: list, info: dict, lines: list[str], words_per_second: float, subs: str,
          words: list[dict], norm: list[str]) -> list[dict]:
    """A film's standalone laughs, as Review entries. Picks under 8, or the wrong length, show unticked; a
    pick whose quotes aren't found is dropped (printed)."""
    out = work / f"funny-{model}.json"
    if out.exists():
        picks = json.loads(out.read_text(encoding="utf-8"))
    else:
        client = anthropic.Anthropic(api_key=api_key())
        messages = [{"role": "user", "content": funny_prompt(info, lines, words_per_second, subs)}]
        text, usage = ask(client, model, system, messages, 1, FUNNY_SCHEMA)
        picks = unique(json.loads(text))
        wrong = [(c, p) for c in picks["clips"] if (p := funny_problem(c, words, norm))]
        if wrong:
            listed = "\n".join(f"- {c['name']}: {p}" for c, p in wrong)
            messages += [{"role": "assistant", "content": text}, {"role": "user", "content": (
                f"Measured from the word timestamps:\n{listed}\n\nFix each one: {FUNNY_LEN[0]}-{FUNNY_LEN[1]}s of "
                f"speech, 1-{FUNNY_PIECES} pieces, quotes copied exactly. Drop a whole piece rather than trim inside "
                "a joke; leave a clip out if it can't fit without losing its payoff. Return only these clips, "
                "revised; `rejected` may be empty.")}]
            text, retry = ask(client, model, system, messages, 1, FUNNY_SCHEMA)
            # Replies can rename a clip: keep the ones that passed and take every revision as it comes.
            picks["clips"] = [c for c in picks["clips"] if not funny_problem(c, words, norm)] + json.loads(text)["clips"]
            picks = unique(picks)
            usage = {key: usage[key] + retry[key] for key in usage}
        picks["usage"] = usage
        out.write_text(json.dumps(picks, indent=2, ensure_ascii=False), encoding="utf-8")

    entries = []
    for c in picks["clips"]:
        ranges, problem = place_moments(c, words, norm, (1, FUNNY_PIECES), FUNNY_WORDS)
        if not ranges:
            print(f"[score]      funny: dropped {c['name']}: {problem}")
            continue
        problem = funny_problem(c, words, norm)
        e = review.entry(words, c["name"], c["score"], ranges[0][0], ranges[-1][1], model, c["payoff"],
                         (f"Dropped by code: {problem}. " if problem else "") + c["reason"],
                         description=c["description"], cuts=as_cuts(ranges))
        e["keep"] = not problem and c["score"] >= 8
        e["recap"] = False
        entries.append(e)
    print(f"[score]      funny: {len(entries)} moments, {sum(e['keep'] for e in entries)} ticked")
    return entries


def unique(picks: dict) -> dict:
    # Two clips with one name would render to one file stem.
    seen: dict[str, int] = {}
    for c in picks["clips"]:
        seen[c["name"]] = seen.get(c["name"], 0) + 1
        if seen[c["name"]] > 1:
            c["name"] += f"-{seen[c['name']]}"
    return picks


def funny_problem(clip: dict, words: list[dict], norm: list[str]) -> str | None:
    ranges, problem = place_moments(clip, words, norm, (1, FUNNY_PIECES), FUNNY_WORDS)
    if problem:
        return problem
    length = splice.seconds(words, ranges[0][0], ranges[-1][1], as_cuts(ranges))
    return None if FUNNY_LEN[0] <= length <= FUNNY_LEN[1] else f"{length:.0f}s of speech, outside {FUNNY_LEN[0]}-{FUNNY_LEN[1]}s"


def score(work: Path, model: str = MODEL, examples: list[str] | None = None,
          span: tuple[float, float] | None = None, kind: str = "podcast") -> Path:
    theme = review.KINDS[kind][1]
    if (work / "review.json").exists():
        scored_as = review.load(work).get("kind", "podcast")
        if scored_as != kind:
            raise RuntimeError(f"{work.name} was scored as {scored_as}; remove work/{work.name}/review.json "
                               f"to rescore it as {kind}")
    if kind == "movie":
        return recap(work, model, theme)
    examples = examples or recent_runs(theme)
    info = json.loads((work / "info.json").read_text(encoding="utf-8"))
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    words = [w for s in transcript["segments"] for w in s["words"]]
    norm = [re.sub(r"[^a-z0-9']", "", w["word"].lower()) for w in words]
    span = span or (0, transcript["duration"])
    pieces = chunks(reading_lines(work), span)
    words_per_second = len(words) / transcript["duration"]

    client = anthropic.Anthropic(api_key=api_key())
    system = [{"type": "text", "text": system_prompt(examples, theme), "cache_control": {"type": "ephemeral"}}]
    clips, rejected, dropped, usage = [], [], [], {"input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
    # Runs before the Streaming type cached under parts-<model>; those are all comedian-podcast.
    parts_dir = work / (f"parts-{model}" if theme == "comedian-podcast" else f"parts-{model}-{theme}")
    parts_dir.mkdir(exist_ok=True)
    for n, (begin, piece) in enumerate(pieces, 1):
        cached = parts_dir / f"{int(begin)}.json"
        if cached.exists():
            picks = json.loads(cached.read_text(encoding="utf-8"))
        else:
            messages = [{"role": "user", "content": user_prompt(info, begin, piece, n, len(pieces), words_per_second)}]
            text, picks_usage = ask(client, model, system, messages, n)
            picks = json.loads(text)
            # It misjudges spoken length (10 finds over 40s in runs 7-9). Show it the measured length once
            # and let it splice harder, instead of code dropping the find.
            long = [(c, locate(dict(c), words, norm)) for c in picks["clips"]]
            long = [(c, p) for c, p in long if p and "after cuts" in p and float(p.split("s")[0]) > MAX_LEN]
            if long:
                messages += [{"role": "assistant", "content": text},
                             {"role": "user", "content": retry_prompt(long, words_per_second)}]
                text, retry_usage = ask(client, model, system, messages, n)
                revised = {c["name"]: c for c in json.loads(text)["clips"]}
                picks["clips"] = [revised.get(c["name"], c) for c in picks["clips"]]
                picks_usage = {key: picks_usage[key] + retry_usage[key] for key in usage}
            picks["usage"] = picks_usage
            cached.write_text(json.dumps(picks, indent=2, ensure_ascii=False), encoding="utf-8")
        for key in usage:
            usage[key] += picks["usage"][key]
        rejected += picks["rejected"]
        for clip in picks["clips"]:
            problem = locate(clip, words, norm)
            if problem:
                dropped.append({**clip, "dropped": problem})
            else:
                clips.append(clip)
        print(f"[score]      part {n}/{len(pieces)}: {len(picks['clips'])} picked")

    # Overlapping parts can pick the same moment twice; keep the higher score.
    kept = []
    for clip in sorted(clips, key=lambda c: -c["score"]):
        twin = next((k for k in kept if min(clip["end"], k["end"]) - max(clip["start"], k["start"]) > 5), None)
        if twin:
            dropped.append({**clip, "dropped": f"overlaps {twin['name']}"})
        else:
            kept.append(clip)
    kept.sort(key=lambda c: c["start"])

    out = work / f"picks-{model}.json"
    out.write_text(json.dumps({"model": model, "span": span, "usage": usage, "clips": kept,
                               "dropped": dropped, "rejected": rejected}, indent=2, ensure_ascii=False), encoding="utf-8")
    # Never overwrite a review in progress: GURT or Tko may already have edited it.
    if not (work / "review.json").exists():
        entries = [review.entry(words, c["name"], c["score"], c["first"], c["last"], model, c["payoff"], c["reason"],
                                description=c["description"], cuts=c["cut_ranges"]) for c in kept]
        # A find that failed a length or cut check still shows in Review, unticked, so a reviewer can fix
        # the window instead of never seeing it (run 9 lost two this way).
        for c in dropped:
            if "first" in c and not c["dropped"].startswith("overlaps"):
                entry = review.entry(words, c["name"], c["score"], c["first"], c["last"], model, c["payoff"],
                                     f"Dropped by code: {c['dropped']}. {c['reason']}",
                                     description=c["description"], cuts=c.get("cut_ranges", []))
                entry["keep"] = False
                entries.append(entry)
        # Over the limit, the lowest scores stay visible in Review but unticked.
        for entry in sorted((e for e in entries if e["keep"]), key=lambda e: -e["score"])[review.clip_cap(work):]:
            entry["keep"] = False
            entry["reason"] = f"Over the cap of {review.clip_cap(work)} clips. {entry['reason']}"
        review.save(work, {"status": "awaiting", "model": model, "kind": kind, "clips": entries})
    return out
