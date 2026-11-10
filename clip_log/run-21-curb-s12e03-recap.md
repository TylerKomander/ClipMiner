## Run 21 — Curb Your Enthusiasm S12E03 (TV episode, local file), 40m, 2026-11-09
**Theme:** `movie-recap` · **Posted:** not yet · 349 (v4) rejected by Tko; 350 (v6) too long; v7 waiting in Review
**Picked by:** GURT by hand in one lean pass, following the skill.md method step by step: the method's first test on a
film other than the one it was written from. A fresh Haiku reader did the retell gate (one call, ~39k tokens). After Tko's verdict on v4, two workflows
(~1.2M subagent tokens: per-moment cut checks plus a laugh sweep, then a re-check) rebuilt it as v6.

**Inputs used:** `transcript.json`, a fresh `reading.txt`, `subs_sdh.srt`. Whisper missed or misheard several things
the SDH has:
- "horizontal tug" in the confession, which calls back the title line;
- "Can do, Mr. T" came out as "Can do it";
- the bagel toss's "No! No, no, no" is missing.

None of them dropped a moment, because the boundary words were taken from outside them. Pace was 3.97 words per
second of speech, against Atlanta's 2.63: Larry's people talk fast.

**The episode in one sentence (the main thread):** Larry overhears a golf pro's lesson from a bench and copies it,
hits the actor Troy with a drive on a dare, is warned by the club owner Takahashi, is caught stealing another lesson
and confesses to the bench in his own defence, so Takahashi throws him out. Side plots: Sienna Miller, the Wordle
fight, Tubman's father-in-law, the lemon tree, Leon and Lydia. **None are in.**

### Versions
- **v2 · 14 moments, 117.9s:** over the 90s cap. Cold-open bagel as moment 1, two moments on one lesson beat.
- **v3 · 86.5s:** dropped the repeat, split the warning around the "Kusai/Stinky" aside, trimmed the bagel. Fresh
  reader: no hook, "vertical drop" at the end meant nothing.
- **349 · v4 · 14 moments, 85.3s · Tko: "You cut early on some dialogue and jokes again, remember funny over
  everything."** Bagel dropped, bench bridge added. Every moment had been trimmed to fit 90s: per-moment checkers
  found 13 of 14 ending before the reply or topper ("You hit him!" alone was 0.5s; the dare stopped mid-bicker; the
  office lost the fish-dream defence, its biggest laugh). Root cause in the rules, not only the pick: the method said
  "3–12s" per moment and a 90s cap, and the matcher gave up after 80 words.
- **v6 · 6 whole scenes, 163.8s, 555 words (in Review):** fewer jokes, each whole. Dropped whole: the "fore" argument
  (Takahashi's "Wave means what? Hello, goodbye" tells the same joke funnier), "I'm watching you", the Postmates
  apology, the roped-off bench, the bathroom catch, the summons. Fresh reader: story clear; confused only by names
  (Jimmy, Troy, "Mr. T"), which the picture answers.

- **350 · v6 · rendered 3:03.6, and the player showed 27 minutes · Tko: "It came out way too long".** Two bugs.
  (1) ffmpeg copies the source's chapters by default, so every recap cut from an .mkv carried the film's chapter track
  (38 min); 349 had it too. Fixed with `-map_chapters -1` in `splice.py` and `render.py`. (2) The render runs ~12%
  over the speech count (pauses inside moments, the 0.35s hold, the end tail): 163.8s of speech made 183.6s.
  `scratchpad/curb_render_len.py` measures the real length from the same `splice` calls and matched to 0.1s.
- **v7 · 7 stretches, 154.3s of speech, 174.7s rendered (in Review):** v6 minus filler only: the pro's "back to the
  lesson… Please", the repeated "Come on. Really? Yeah…", "You are in big trouble", "And so I'm exhausted". No joke
  touched.

| # | At | Lines (start … end) | Joke |
|---|---|---|---|
| 1 | 11:12 | "Nah, I'm good. I'm just sitting here… if you don't mind. Please." | Caught lingering: "an aesthetic bench" / "benches are for sitting" |
| 2 | 12:06 | "What is this all about?… how to tug. This is fantastic." | Two minutes on a bench; the tug chant; "I've never tugged"; "teach me how to tug" |
| 3 | 13:19 | "What are you doing?… I shouldn't have fucking hit you." | The dare, the shut-ups, the drive (13s of ball flight), Troy hit |
| 4 | 24:40 | "Hey, funny guy. Kusai, when… and you're out. Enjoy." | Wave = hello/goodbye, he's deaf, golf so terrible, Kusai = Stinky, last warning |
| 5–6 | 36:41 | "You are in big trouble.… Go. Arigato. Baka!" | Cheap and violent guy, the fish-dream defence, confesses to the bench, thrown out |

Captions: Whisper misheard "fore" (×3, as "four"), "benches are" (as "bench isn't") and "Baka!" (as "Fuck."). The
words were corrected in `transcript.json` (original kept in GURT's scratchpad) so the captions say what's heard.

**Post text:** "Two minutes on a bench changed his golf game. It also cost him the club."

### What the method got right and wrong on a new film
- `[theme]` **Funny beats the budget.** The 90s cap and "3–12s" moments made GURT trim inside jokes, the second time
  Tko flagged cut jokes. Now: a moment is a whole joke however long; drop whole weaker jokes; up to 165s of speech
  (under a Short's 3 minutes). (In skill.md steps 5 and 8, and `score.py` limits and prompt.)
- `[theme]` When two scenes tell the same joke, keep the funnier telling and spend the seconds elsewhere.
- `[theme]` A rambling defence is the joke (the fish dream); a stranger doesn't need it to connect, Takahashi's
  groans are the reply.
- `[universal]` A recap's rendered length is ~12% over its speech count: measure with the `splice` calls, not
  speech seconds. Cap is now 155s of speech. And `-map_chapters -1`, or an .mkv's chapters make the player lie.
- `[scorer]` `place_moments` matches the last four words loosely: "I'll teach you how to tug" stopped on "Can you
  teach me how to tug?" a second earlier. End on words that occur once.
- `[theme]` Steps 2–5 found the main thread and dropped five side plots without doubt.
- `[theme]` The set-up rule over-fired on v2: a payoff that states its own set-up ("then you hit him with bagel")
  needs none, and a cold-open set-up costs the hook. (In skill.md step 6.)
- `[universal]` Picture gags (the bagel toss, the ball flight) are laughs with no words; Whisper shows them as gaps.
  Keep them inside a moment.
- `[theme]` A fresh reader catches what the picker's own retell passes; per-moment checkers catch cut jokes, but they
  judge split moments as if alone: tell them which moments play back to back.
