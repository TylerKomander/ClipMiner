# ClipMiner — clip log index

Worked examples for future models. Rules live in `../skill.md`; the run files show them applied.
**Read this index, not the run files.** Open a run file only when its clips are relevant, and
pull 3–5 matching clips as examples, never the whole log. Kept clips show what good looks
like; rejected ones show what to avoid.
`[scorer]` lessons come from each run's **Scorer vs GURT** section: where the API model and GURT
disagreed and who was right. They're the fastest way to make the model pick like GURT.

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
| 3 | `run-03-jre-2187-sandler.md` | JRE #2187 (Adam Sandler) | 137m | 11–28 | multi-camera, no SPLIT; 18 clips; first scorer test |
| 4 | `run-04-ball-in-the-family-34-arenas.md` | Ball in the Family #34 (Gilbert Arenas) | 71m | 29–39 | athlete show under comedian rules; 6-person couch; first blind-pick diff |
| 5 | `run-05-this-past-weekend-489-druski.md` | This Past Weekend #489 (Druski, Roll Tide Willie) | 97m | 40–52 | race-heavy riffs skipped; real heatmap peak = best clip |
| 6 | `run-06-flagrant-shane-gillis-steve-gerben.md` | Flagrant (Shane Gillis, Steve Gerben) | 108m | 53–67 | every peak fake, 0 loudness spikes, hallucinated transcript |
| 7 | `run-07-soder-139-louis-ck.md` | Soder Podcast #139 (Louis C.K.) | 77m | 68–85 | first run through the app; splicing + audio endings built after it |
| 8 | `run-08-this-past-weekend-686-caleb-pressley.md` | This Past Weekend #686 (Caleb Pressley) | 125m | 86–117, 123–127 | Sonnet's 32 approved as-is; GURT's 5 as a second batch; first Sonnet splices |

## Shapes (universal), most seen first
Format: tally · shape · clips (score). Clip numbers match `Finished_Clips\` and the run files.
3+ = proven, listed in `skill.md` Part B "Proven shapes".
- `[........]` **Self-roast of the past self**: delusion then, blunt truth now · 14 (7), 15 (9), 25 (8), 27 (9), 38 (7), 53 (7), 83 (8), 124 (8)
- `[........]` **Scene → twist → reaction**: the reaction is the payoff · 06 (9), 11 (8), 20 (9), 22 (8), 35 (7), 58 (8), 77 (9), 78 (9)
- `[........]` **Observational take with a quotable capper** · 04 (7), 09 (7), 28 (7), 37 (7), 44 (8), 67 (7), 73 (8), 74 (9)
- `[.....]` **Plan meets reality**: naive expectation, then the obvious question or bad trade · 13 (8), 16 (7), 26 (8), 30 (8), 54 (8)
- `[....]` **Strange true fact, explained in one breath** · 08 (8), 18 (8), 42 (8), 55 (7)
- `[...]` **Shameless confession, told proudly** · 19 (9), 36 (8), 64 (9)
- `[...]` **Friend exposes the other's habit** · 57 (8), 66 (7), 67 (7)
- `[....]` **Insider rule revealed, pushed to absurd precision** · 07 (9), 29 (8), 80 (8), 123 (8)
- `[..]` **Self-justifying logic spiral** · 12 (8), 32 (7)
- `[..]` **Confession in the first sentence** · 02 (8), 33 (9)
- `[...]` **Behind-the-scenes reveal told straight** · 05 (6), 31 (9), 84 (8)
- `[....]` **Energy build or outrageous comparison, then a capper that tops it** · 01 (8), 17 (9), 69 (8), 76 (9)
- `[..]` **Proud reveal, instantly deflated** · 43 (9), 65 (8)
- `[..]` **Parent collides with the joke** · 21 (7), 61 (8)
- `[....]` **Absurd image → strong verdict** · 10 (8), 56 (8), 70 (8), 126 (9)
- `[..]` **Prank or bit backfires** · 60 (7), 63 (7)
- `[.]` **Unbreakable loyalty, broken in one question** · 52 (9)
- `[.]` **A con, and the mark finds out** · 127 (9)
- `[..]` **Made-up fact, caught live** · 48 (8), 95 (8)
- `[.]` **Embarrassing message read back live** · 59 (8)
- `[.]` **List game with a guest who never breaks** · 50 (8)
- `[.]` **A con presented as advice** · 47 (8)
- `[.]` **Absurd escalation of a crush** · 45 (8)
- `[.]` **Crude image, then someone finds the silver lining** · 41 (8)
- `[.]` **Steering toward the line everyone's thinking, called out** · 40 (7)
- `[.]` **Code of honor stated backwards** · 49 (7)
- `[.]` **Roast of a third party's look** · 46 (7)
- `[.]` **One-line policy, stated proudly** · 34 (8)
- `[.]` **Parent's proud setup, kid's absurd reality** · 39 (7)
- `[.]` **Backup plan justified by one absurd story** · 23 (8)
- `[.]` **Old doubters witness the success** · 24 (7)
- `[.]` **Vivid description → takeaway** · 03 (6)

Read so far: story shapes with a clear turn score 8–9; takes score 7 unless the capper is
quotable. Duo shows (Shane/Steve) run on "friend exposes the other"; one-guest shows on self-roast.

## Recurring lessons, most seen first
- `[.......]` `[universal]` The best version of a story needs more than 35s (runs 1–7). **Fixed after run 7: splicing** (`splice.py`; crematorium 77s → 32s). (in skill.md)
- `[.....]` `[universal]` The dry run of first/last 5 words catches cut-off words (runs 2–6). (in skill.md)
- `[.]` `[universal]` Whisper's word end times aren't where the sound stops; endings are cut from the audio now (run 7). (in skill.md)
- `[..]` `[universal]` Whisper drops curse words entirely ("shut the up", "I don't give a no"); restore them with a caption fix when the punchline needs it (runs 7, 8).
- `[.......]` `[universal]` Clips with zero signal support are as good as signalled ones (runs 1–8). (in skill.md)
- `[.....]` `[universal]` Heatmap peaks right after ad reads are skip landings (runs 1, 3, 5, 6, 7). (in skill.md)
- `[......]` `[universal]` Whisper drops to lowercase with no punctuation (runs 2–4, 6–8). (in skill.md)
- `[....]` `[universal]` A story fails the cold read when its subject is never named in the window (Post Malone, 16, 32, Sexy Red). (in skill.md)
- `[....]` `[universal]` The first framing try was wrong: center crop, mediapipe, tiny-face SPLIT, poster faces. Look at frames before rendering. (in skill.md)
- `[......]` `[scorer]` Model gives no-payoff, sincere or promotional talk a 6–7 instead of rejecting it (runs 3–8; run 8: 32 picks). (in skill.md, not biting yet)
- `[.]` `[scorer]` Model's splices are sensible but can drop the ending (run 8: Gronk), and often still run over 40s. (in skill.md)
- `[.]` `[scorer]` Model misses escalating riffs and takes a story's flat tail (run 7: 69, 76, 84).
- `[....]` `[universal]` GURT missed clips the model found (runs 3–7). Blind-pick, then diff, then accept finds after reading them. (in CONTEXT.md recipe)
- `[...]` `[theme]` A non-comedian guest is gold when the hosts poke at their world (rancher, Arenas, Roll Tide Willie). (in skill.md)
- `[..]` `[universal]` Loudness is useless on group or compressed shows (run 4: 21% spiked; run 6: 0 spikes). (in skill.md)
- `[..]` `[universal]` Fix misheard words in captions when sure (Katt, Tide man, balls); cut around them when not. (in skill.md)
- `[..]` `[universal]` Whisper hallucinations (repeat loops, word salad) sit next to good clips (runs 5, 6). Check the window's own captions. (in skill.md)
- `[..]` `[scorer]` Model picks the weaker version of a repeated story, or a different window of it (runs 3–5).
- `[..]` `[scorer]` Model scores race/N-word/religion bits on the payoff (runs 5, 6). Correct per Tko; it should still add a risk flag.
- `[..]` `[scorer]` Model and "build backwards from the payoff": wrong on run 4 (30, 35), right on run 6 (59) where GURT wasn't.
- `[.]` `[scorer]` Model under-scores "confession of incompetence told proudly" (run 6, 64: 6 vs 9).
- `[.]` `[scorer]` Small model loses the second half of a long episode; send it in pieces (run 3, Haiku).
- `[.]` `[universal]` Never clip a cold-open teaser (run 4). (in skill.md)
- `[.]` `[universal]` Caption the exact dry-run words, not words selected by time (run 4). Fixed in code.
- `[.]` `[universal]` Best story lost to transcript garbage (run 6, SNL firing). Idea: re-transcribe one stretch.
- `[.]` `[universal]` Evenly spaced heatmap peaks may be YouTube mid-roll breaks (run 3, guess).
- `[.]` `[theme]` N-word/race bits: GURT skipped them in run 5; Tko overruled: judge on the payoff, flag the risk. (in skill.md)
- `[.]` `[theme]` A guest walking in mid-episode is a clip farm; every question is a setup (run 5, Willie).
- `[.]` `[theme]` A guest plugging their own product is an ad in disguise; drop it (run 8). (in skill.md)
- `[.]` `[workflow]` Restart the app after code changes (run 7); a process keeps the API key it launched with, so it's now read fresh (run 8).
- `[.]` `[theme]` Two comedians ≈ 8 clips/hour (run 3); runs 4–6 ran 8–9/hour.
- `[.]` `[theme]` Athlete storytellers fit the comedian profile when the guest tells stories deadpan (run 4).
