# ClipMiner — clip log index

Worked examples for future models. Rules live in `../skill.md`; the run files show them applied.
**Read this index, not the run files.** Open a run file only when its clips are relevant, and
pull 3–5 matching clips as examples, never the whole log. Kept clips show what good looks
like; rejected ones show what to avoid.

Conventions used in the run files:
- Heat = heatmap bucket value(s) the clip overlaps (0–1, relative). Loud = seconds ≥ 6 LU over
  the episode median / max LU over median.
- Each run is tagged with its theme. Patterns are written twice. **Shape (universal)** is the
  structure that works in any niche. **Here (theme)** is how it showed up under that run's
  theme. Lessons are tagged `[universal]` or `[theme]`. When the theme changes, keep the shapes
  and universal lessons; re-derive the "Here" parts.
- **Posted:** per-clip performance by layout and platform, once Tko posts. That becomes the real
  signal for layout and pick quality.

**Tally marks `[....]`:** one period each time a shape or lesson shows up in a separate clip or
run. After every run, add a period to each one seen again, add new ones with `[.]`, and re-sort
by count. **3+ periods = proven**: promote it into `skill.md` (Part A if theme, Part B if
universal) and note "(in skill.md)" here.

---

## Runs
| Run | File | Show | Length | Clips | Notes |
|---|---|---|---|---|---|
| 1 | `run-01-wild-ride-222.md` | Wild Ride #222 (Steve-O, penguinz0) | 73m | 01–05 | heatmap mostly ad-skip; BLUR only |
| 2 | `run-02-matt-shane-638.md` | Matt & Shane #638 (rancher guest) | 77m | 06–10 | no heatmap, flat loudness, lowercase transcript |
| 3 | `run-03-jre-2187-sandler.md` | JRE #2187 (Adam Sandler) | 137m | 11–28 | multi-camera, no SPLIT; 18 clips |

## Shapes (universal), most seen first
Format: tally · shape · clips (score). Clip numbers match `Finished_Clips\` and the run files.
- `[....]` **Self-roast of the past self**: delusion then, blunt truth now · 14 (7), 15 (9), 25 (8), 27 (9)
- `[....]` **Scene → twist → reaction**: the reaction is the payoff · 06 (9), 11 (8), 20 (9), 22 (8)
- `[...]` **Plan meets reality**: naive expectation, then the obvious question or bad trade · 13 (8), 16 (7), 26 (8)
- `[...]` **Observational take**: name or reframe something everyone knows · 04 (7), 09 (7), 28 (7)
- `[..]` **Strange true fact / hidden origin, explained in one breath** · 08 (8), 18 (8)
- `[..]` **Energy build or outrageous comparison, then a capper that tops it** · 01 (8), 17 (9)
- `[.]` **Insider rule revealed live** · 07 (9)
- `[.]` **Self-justifying logic spiral** · 12 (8)
- `[.]` **Absurd image → strong verdict** · 10 (8)
- `[.]` **Confession in the first sentence** · 02 (8)
- `[.]` **Clever cowardice told proudly** · 19 (9)
- `[.]` **Backup plan justified by one absurd story** · 23 (8)
- `[.]` **Innocent enthusiasm misread by a parent** · 21 (7)
- `[.]` **Old doubters witness the success** · 24 (7)
- `[.]` **Behind-the-scenes reveal** · 05 (6)
- `[.]` **Vivid description → takeaway** · 03 (6)

Early read: the four-period shapes are all *story* shapes. The observational shape has three
sightings but every clip scored 7. Stories with a clear turn score higher than takes.

## Recurring lessons, most seen first
- `[....]` `[universal]` The best version of a story needs more than 35s of setup (run 1 clip 02, run 2 clip 10, run 3 clips 11, 26). Fix: jump cuts, not built yet.
- `[...]` `[universal]` The last word of a clip got dropped (run 2 once, run 3 twice by different causes). A dry run of the first and last 5 words catches it. (in skill.md)
- `[...]` `[universal]` Clips with zero signal support are as good as signalled ones (run 1 had 2, run 2 all 5, run 3 most). Always read the whole transcript. (in skill.md)
- `[..]` `[universal]` Heatmap peaks right after ad reads are skip landings (runs 1, 3). (in skill.md)
- `[..]` `[universal]` Whisper drops to lowercase with no punctuation (run 2 throughout, run 3 mid-episode). (in skill.md)
- `[..]` `[universal]` A story fails the cold read when its subject is never named in the window (run 2 Post Malone, run 3 clip 16).
- `[..]` `[universal]` The first try at framing was wrong (center crop in run 1, mediapipe detector in run 2). Always look at frames before rendering. (in skill.md)
- `[.]` `[universal]` Evenly spaced heatmap peaks may be YouTube mid-roll breaks (run 3, guess).
- `[.]` `[theme]` A non-comedian guest is gold when the hosts poke at their world (run 2).
- `[.]` `[theme]` Two comedians ≈ 8 clips/hour; dedupe by story type (run 3).
