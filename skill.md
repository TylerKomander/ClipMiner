# ClipMiner — how we pick clips

The rulebook. Read this whole file before picking clips. Worked examples live in `clip_log\`,
one file per run; `clip_log\INDEX.md` lists every shape and lesson with a tally of how often it
has been seen. Read the index, then only the run entries you're given. Tko + GURT tune both after every run.
Anything marked **(guess)** hasn't been checked against a real run yet.

Two parts:
- **Part A: Theme profile.** *What* counts as a good clip. Swappable: a different niche
  gets a different profile. Only Part A changes when the theme changes.
- **Part B: Universal rules.** *How* to find, cut and render a clip. True for any theme.

---

# Part A — Theme profile

## Active theme: `comedian-podcast`
Long-form podcasts hosted by (or featuring) stand-up comedians. Hosts riff, commit to bits,
tell road/tour stories, and interview guests who are often *not* comedians (run 2: a rancher).

**Audience:** people who scroll for laughs and "wait, what?" moments, and follow comedians.

**What the payoff looks like in this theme** (the "payoff" Part B keeps referring to):
- **Funny:** a joke or punchline lands *inside* the clip. Often a riff that builds, then a
  one-liner caps it. Laughter helps but is not required.
- **Whacky:** an absurd true story or fact. Reaction: "wait, what?"
- **Interesting:** a take, insight or vivid description someone would share or nod along to.
Funny is the priority for this theme; whacky and interesting fill the mix.

**Where it hides in this theme:**
- Road/tour stories (venues, crowds, weird cities). Run 2 clip 06.
- A host breaking an unwritten rule of the guest's world and getting corrected. Run 2 clip 07.
- Hosts riffing on a serious topic until someone lands a sarcastic capper. Run 1 clip 01.
- The guest's strangest true fact from their job or past. Run 1 clip 02, run 2 clip 08.
- Hot takes on everyday things (malls, drugs, the internet). Run 1 clip 04, run 2 clips 09, 10.

**Off-theme here:** sincere/earnest segments (charity, gratitude), technical explainers
without a joke, business talk, tour-date plugs.

**Theme-specific tolerance:** profanity and crude topics are normal and fine. Only flag
profanity in the first 3s (reach), not the topic.

## Writing a new theme profile (when Tko changes the niche)
Copy the block above and fill the same fields: name, what the content is, audience, what the
payoff looks like (and which kind is the priority), where it hides, what's off-theme,
tolerance. Keep the `clip_log\` run files. Their *universal* lessons still apply, and their
*theme* lessons show the new profile what "specific enough" looks like.

---

# Part B — Universal rules

## The bar
A stranger scrolling past stops and watches to the end. A clip that is only "pleasant
conversation" is not a clip. Ask: *would I send this to a friend?*

## Clip shape
- Length: **10–30s target, up to ~35s when the payoff needs it** (Tko's ruling after run 2).
  Only stretch for the payoff, never for trailing chatter. Shorter is fine if it's complete.
  Never pad. Run 3 went to 37–38s twice because the setup couldn't be cut without losing the
  cold read. That costs a point. The real fix is jump cuts (splicing out a rambling middle),
  which aren't built yet.
- **Opening line:** must make sense on its own and pull you in: a claim, a surprising fact,
  or a question. Never open on "And", "So yeah", "That's", "Like I said", or a pronoun with
  no name ("he did...").
- **Closing line:** end on the payoff (see the active theme for what that is). Cut right
  after it + ~0.3s. Don't trail into the next topic or "yeah, yeah".
- One idea per clip. If it needs a second idea to land, it's two clips or none.
- Start and end on word boundaries from the word-level transcript, not segment boundaries.
  Whisper segments often begin mid-thought.
- **Pick words by start time with ±0.05s tolerance**, then do a dry run that prints every clip's
  first 5 and last 5 words *before rendering anything*. Confirm the opener and payoff are
  whole. The last word got dropped three different ways: filtering by end time (run 2),
  a rounded bound 0.01s short (run 3, "stick with that ~~place~~"), and an end point typed
  one word early (run 3: "I got to stop," / "crush" / "murder why"). All were caught by the
  dry run, none by eye.

## The three tests (run all three on every candidate)
1. **Cold read:** read only the clip's text, nothing before it. Does it make sense? Does it land?
2. **Retell:** can you say what happens in one sentence? If not, it's too muddy.
3. **Payoff check:** point to the exact line that is the payoff. If there isn't one, drop it.

**Missing name = failed cold read.** A story about "this kid from Dallas" who is actually
Post Malone doesn't work if the name is never said in the window. (Later: a title overlay.)

## Transcript quality — check before trusting it
- **Hallucinated repeats:** Whisper sometimes repeats a whole sentence with every repeated
  word at the *same timestamp* (run 2 at 31:48, ~30 words). That window is unusable.
  **But short runs (3–8 words) at one timestamp are just squashed timing on fast speech** (run 3
  had ~100, all real words). Only treat it as a hallucination if the run is 15+ words or
  repeats text that was just said.
- **No punctuation/casing:** Whisper can drop into all-lowercase, unpunctuated output and
  stay there. Run 2 was like that throughout; run 3 switched at 1:28:52 and recovered at
  1:47:42. Judge sentence boundaries by meaning there. Fix to try: `condition_on_previous_text
  =False` in `transcribe.py` so one bad stretch can't carry forward **(guess)**.
- **Misheard payoff words:** if Whisper gets a key word wrong ("we have a *shot* in an hour"),
  move the boundary to avoid captioning it rather than posting a wrong caption.

## Ads — detect first, exclude everywhere
Sponsor language: "promo code", "<brand> dot com slash", "use the code", "free shipping",
"let's get back to it", "shout out ... if you've got", tour-date lists. Mark the whole read
as off-limits for clips, heatmap peaks and loudness spikes.

## Signal 1 — Heatmap ("Most replayed")
- yt-dlp `heatmap`: ~100 buckets, `value` 0–1, **relative to the video's own peak**.
- Often missing (run 2). Then skip it.
- Ignore the first ~2 buckets (people scrubbing at the start).
- **Ad-skip peaks are fake.** Viewers skip a sponsor read and land right after it (run 1: 4 of
  the top 5 peaks). If the ~60s before a peak is an ad read, discard the peak.
- Real content peaks can be low (run 1: 0.30–0.59). Rank relatively.
- A bucket is ~44s wide on a 73-min video (~82s on 2h17m). A peak says "something in here",
  not where to cut.
- **Evenly spaced peaks with ordinary content** (run 3: 9:38, 28:55, 48:11, every ~19 min)
  are suspect. Likely YouTube-inserted mid-roll ad breaks, not replays **(guess)**. Treat
  them like ad-skip peaks unless the content itself is strong.
- Real peaks did land on good material in run 3 (35:48, 1:25:22, 2:05:18: all picked clips).

## Signal 2 — Loudness
- ffmpeg `ebur128` momentary loudness per second vs the episode's own median.
- Spike = **≥ 6 LU above median (guess)**: laughter, raised voice, reaction. Clusters over
  10–20s are the useful hint (run 1 clip 01).
- Ad reads run hot; ignore spikes inside them.
- Some shows are mixed flat (run 2: 5 spikes in 76 min). If spikes are that rare, ignore it.
- Loudness alone never selects a clip.

## Signal 3 — Transcript (the decider)
Signals point you to places; the transcript decides. A strong moment with no signal beats a
peak with no payoff. Run 1: 2 of 5 kept clips had no signal. Run 2: all 5. **Always read the
whole transcript.**

Drop on sight (any theme): ads, intros/outros, "subscribe", housekeeping, rapid-fire Q&A lists,
cross-talk captions can't follow, gestures the viewer can't see ("they were like *this*"),
setups whose payoff is outside the length limit.

## Selection order
0. Check transcript health. Mark ad reads off-limits.
1. List real heatmap peaks, if any.
2. Read the full transcript with peaks and loudness clusters marked. Episodes over ~1h:
   read in ~15-min chunks with ~1 min of overlap so no clip gets split across a boundary.
3. For each candidate, find the payoff line; build the window backwards to a clean opener.
4. Run the three tests. Drop failures.
5. Score every survivor (rubric below). Render everything scoring **6+**.
6. Mix kinds. No overlaps, 30s+ apart, no two clips on the same sub-topic.

## How many clips
**No fixed number.** The episode decides. A dead 2-hour episode might give 2; a great one
might give 15. Never pad the count with 5s to hit a number, and never cap strong clips to
stay under one. Density so far: ~4/hr (runs 1–2, host + non-comedian guest) to ~8/hr (run 3,
two comedians trading road stories).

**Same-story dedupe:** comedians tell many versions of one story type (run 3 had 5+ "I
bombed" stories). Keep the best one per story type, not every one that passes.

## Score (1–10, absolute, not relative)
Each clip is scored against the bar, **not against the other clips in the episode**. If
all five are great, all five are 9–10. If none are, none are.
- **10:** would bet on it. Instant hook, clean payoff, perfect cold read, no weaknesses.
- **9:** strong on all three tests; one tiny nitpick.
- **8:** strong payoff; one real flaw (weak opener, slight overrun, a risk flag).
- **7:** good moment, noticeably flawed cut (filler opener, runs long past the payoff).
- **6:** postable filler. Passes the tests, but nobody shares it.
- **≤5:** don't render. Log it as rejected with the reason.
Write the score and a one-line reason in the run's `clip_log\` file. The score goes in the filename.

## Risk flags (mention, don't auto-reject; Tko decides)
- Rumors or accusations about named real people. Drug-use rumors about named celebrities →
  skip; there's usually a safer clip on the same topic nearby.

## Render — every clip in all three layouts
Tko posts all three variants across platforms and lets performance decide. **No layout
rule yet: always render all three.** Output:
`Finished_Clips\NN_s<score>_<name>_{blur,split,track}.mp4` (e.g. `07_s9_dont-ask-head-count_split.mp4`).
NN keeps counting up across runs.
- **BLUR:** full 16:9 frame centered, blurred copy fills top and bottom. Never cuts anyone out.
- **SPLIT:** two faces stacked (1080x960 each), captions on the seam. Top = left person.
  Needs both people *in the same shot for the whole clip*. Multi-camera shows that cut
  between single close-ups (run 3, JRE) can't do SPLIT. Skip it and say so; don't fake it.
- **TRACK:** 9:16 full-height crop. The clip is split into camera shots first (ffmpeg `scdet`,
  threshold 10; real cuts score ~22–24). Per shot: 1 face → center on it; 2+ faces → follow
  the talker by mediapipe `jawOpen` (switch only if clearly higher, hold ≥ 1.5s); 0 faces →
  center of frame.
- **No plain center crop:** wide shots put people at the edges.
- Face detection is OpenCV YuNet. mediapipe's short-range detector failed on wide shots
  (boxed hands, a plant pot, a belt buckle). **Draw boxes on one frame per show and look
  before rendering.**
- Captions: burned in, up to 3 words per line, word-timed. BLUR/TRACK low third; SPLIT on the seam.
- Delete `work\<slug>\source.mp4` after rendering.
