import json
import re
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
LINE_SECONDS = 15
CHUNK_SECONDS = 20 * 60
OVERLAP_SECONDS = 60
MIN_LEN, MAX_LEN = 10, 40
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
    })},
    "rejected": {"type": "array", "items": _object({"approx_start": {"type": "string"}, "why": {"type": "string"}})},
})


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
        piece = [text for start, text in lines if t - OVERLAP_SECONDS <= start < min(t + CHUNK_SECONDS, span[1])]
        if piece:
            out.append((t, piece))
        t += CHUNK_SECONDS
    return out


def system_prompt(examples: list[str]) -> str:
    return "\n\n".join([
        "You pick short-form clips from long podcast episodes. Follow the rulebook exactly.",
        "# RULEBOOK\n" + (ROOT / "skill.md").read_text(encoding="utf-8"),
        "# CLIP LOG INDEX\n" + (ROOT / "clip_log" / "INDEX.md").read_text(encoding="utf-8"),
        *(f"# WORKED EXAMPLE RUN\n{(ROOT / 'clip_log' / name).read_text(encoding='utf-8')}" for name in examples),
    ])


def user_prompt(info: dict, begin: float, piece: list[str], part: int, parts: int, words_per_second: float) -> str:
    heat_note = "present" if info.get("heatmap") else "missing for this video"
    return (
        f"Episode: {info.get('title')}\nLength: {hms(info.get('duration') or 0)}\nHeatmap: {heat_note}\n"
        f"This is part {part} of {parts}. It starts at {hms(begin)}; earlier lines are context only. "
        "Only pick clips that start at or after it.\n\n"
        f"Reading file: one line per ~{LINE_SECONDS}s as `h:mm:ss text`. <Ln/+x> = n seconds at least "
        f"{SPIKE_LU} LU over the episode median, max +x. <H0.xx> = heatmap value of the overlapping bucket.\n\n"
        f"Speech here runs ~{words_per_second:.1f} words/s, so a 10–35s clip is about "
        f"{10 * words_per_second:.0f}–{35 * words_per_second:.0f} words. Count before you submit.\n"
        "Before submitting a clip, quote its payoff: the line a stranger laughs at or says 'wait, what?' to. "
        "Warm conversation, praise, or a story with no turn is not a payoff. No payoff, no clip.\n"
        "Submit every clip scoring 6+ and the notable rejects. "
        "first_words and last_words must be copied exactly from the text.\n\n"
        + "\n".join(piece)
    )


def snap(words: list[dict], norm: list[str], near: float, quote: list[str], window: float) -> int | None:
    best = None
    for i, w in enumerate(words):
        if abs(w["start"] - near) > window:
            continue
        # Allow one miscopied word: lowercase stretches and fillers trip up exact quotes.
        if sum(a == b for a, b in zip(norm[i:i + len(quote)], quote)) >= len(quote) - 1:
            if best is None or abs(w["start"] - near) < abs(words[best]["start"] - near):
                best = i
    return best


def locate(clip: dict, words: list[dict], norm: list[str]) -> str | None:
    first = re.findall(r"[a-z0-9']+", clip["first_words"].lower())[:4]
    last = re.findall(r"[a-z0-9']+", clip["last_words"].lower())[-4:]
    i = snap(words, norm, seconds(clip["approx_start"]), first, 60)
    j = snap(words, norm, seconds(clip["approx_end"]), last, 90)
    if i is None or j is None:
        return "first or last words not found in the transcript"
    clip["start"], clip["end"] = words[i]["start"], words[j + len(last) - 1]["end"]
    length = clip["end"] - clip["start"]
    if not MIN_LEN <= length <= MAX_LEN:
        return f"{length:.0f}s long, outside {MIN_LEN}-{MAX_LEN}s"
    return None


def score(work: Path, model: str, examples: list[str], span: tuple[float, float] | None = None) -> Path:
    info = json.loads((work / "info.json").read_text(encoding="utf-8"))
    transcript = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    words = [w for s in transcript["segments"] for w in s["words"]]
    norm = [re.sub(r"[^a-z0-9']", "", w["word"].lower()) for w in words]
    span = span or (0, transcript["duration"])
    pieces = chunks(reading_lines(work), span)
    words_per_second = len(words) / transcript["duration"]

    client = anthropic.Anthropic()
    system = [{"type": "text", "text": system_prompt(examples), "cache_control": {"type": "ephemeral"}}]
    clips, rejected, dropped, usage = [], [], [], {"input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
    parts_dir = work / f"parts-{model}"
    parts_dir.mkdir(exist_ok=True)
    for n, (begin, piece) in enumerate(pieces, 1):
        cached = parts_dir / f"{int(begin)}.json"
        if cached.exists():
            picks = json.loads(cached.read_text(encoding="utf-8"))
        else:
            with client.messages.stream(
                model=model,
                max_tokens=64000,
                system=system,
                output_config={"format": {"type": "json_schema", "schema": CLIP_SCHEMA}},
                messages=[{"role": "user", "content": user_prompt(info, begin, piece, n, len(pieces), words_per_second)}],
            ) as stream:
                response = stream.get_final_message()
            if response.stop_reason == "max_tokens":
                raise RuntimeError(f"part {n} hit max_tokens")
            picks = json.loads(next(b.text for b in response.content if b.type == "text"))
            picks["usage"] = {key: getattr(response.usage, key) or 0 for key in usage}
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
    return out
