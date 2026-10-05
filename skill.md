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

One profile per video type. Tko picks the type in the app before pasting the link (Podcast →
`comedian-podcast`, Streaming → `streamer`); the prompt names the profile in force. Ignore the others.

## Theme: `comedian-podcast`
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
- A guest from outside comedy the hosts can poke at (a rancher, an NBA player, an internet-famous
  Alabama fan). Every question to them is a setup. Runs 2, 4, 5.

**Off-theme here:** sincere/earnest segments (charity, gratitude), technical explainers
without a joke, business talk, tour-date plugs, and **a guest or host plugging their own product**
(run 8: Caleb's tequila taglines and shoe "review" — even when it's riffy, a clip of it is free
advertising for them).

**Theme-specific tolerance:** profanity and crude topics are normal and fine. Only flag
profanity in the first 3s (reach), not the topic.

## Theme: `streamer`
Livestreams and stream uploads: a streamer at a webcam, usually playing a game, often with friends
on voice chat. One run behind it (run 12, Joe Bart Games); lines marked **(guess)** are untested.

**Audience:** people who scroll for laughs and follow streamers. Same bar as the podcast theme: funny first.

**A friend-group stream is a podcast with a game on screen.** Run 12: 16 of 19 clips were friends
roasting each other and telling stories over the game, and would have passed as podcast clips. Judge
the banter exactly like `comedian-podcast` banter. The game is the backdrop, not the reason to reject.

**What the payoff looks like in this theme:**
- **Funny:** a roast, a comeback, a confession or a rant that lands inside the clip (GTA RP janitor,
  "because they give you gifts and stuff"). The line is often a friend's, not the streamer's. Fine.
- **Whacky:** something goes absurdly wrong in the game and someone says it out loud ("that wolf
  didn't have a weapon on him").
- **Interesting:** a story or take told to the group, same as a podcast clip.

**Where it hides in this theme:**
- Lulls in the game: waiting for the monster, loading, walking. That's when the group talks.
- Right after a failure: who caused it, who ran away, who didn't help.
- A story one friend refuses to tell and the others drag out of them.
- Loudness spikes. Unlike group podcasts, they work here (run 12: 14 of 19 clips on a spike; the first
  attack is the loudest stretch of the video, +21, the second peaks at +12). Read around every spike.
- Full-screen "just chatting" stretches (usually the start and end) **(guess)**.

**You only have the words.** The scorer can't see the game. A scream with few words around it is not a
clip on the transcript alone: put it in `rejected` with "visual, check the frame" so the reviewer looks
(run 12: both of those were clips once the frames were checked). Everything else, judge on the words.

**Do not reject for these (run 12, all wrong):**
- **A garbled transcript.** Gamer words are misheard constantly ("are peeing" = RPing, "mac dumped the
  wall" = mag dumped the wolf, "insulin" = incel). They are caption fixes. Read through them.
- **A callback.** "Needs the stream's history" applies only when the clip makes no sense without it.
- **Several voices.** Four friends trading lines is the format, not cross-talk.

**Off-theme here:** silent or mumbled gameplay, pure callouts ("he's on me", "I need ammo"), menus and
mod setup, sub/donation thank-yous, sponsor reads, stream scheduling, and sincere drama about another
creator (run 12: the debate rant; named person, no joke).

**Transcript traps:** every voice is one stream of words, with nothing to say who spoke; game
characters' lines are transcribed too. Long screaming stretches come out as a few words or a
hallucinated loop ("A, A, A" ×100).

**Theme-specific tolerance:** same as `comedian-podcast`.

## Writing a new theme profile (when Tko adds a video type)
Add the type to `review.KINDS` (app label, folder, profile name), then copy a block above and fill the same fields: name, what the content is, audience, what the
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
  Never pad. Length means the **finished** clip, after splicing.
- **Splicing (built after run 7; Tko: "good clipping accounts cut out empty space").** A story whose
  best version runs long can be spliced with hard jump cuts: list `cuts` (word ranges) for a tangent,
  a repeated setup or cross-talk. The source window may span up to ~4 minutes as long as the kept
  part is 10–40s and still reads cold. **A payoff whose setup came minutes earlier is a splice** (setup line,
  then payoff), not a reject and not a clip of the payoff alone (run 9: the green-room game's setup sat 2.5
  minutes before "who's this necromancer that brought Richard Pryor back from the dead?"). Never cut the payoff, the line that sets it up, or a reaction
  that is part of the payoff. Dead air is shortened automatically; don't list it.
  It is cut only where the **audio** is quiet for over 0.6s, never on a gap in the transcript alone, and never
  leaving a stretch under 1s (Tko after run 12: cuts landed mid-word, between two people talking, and left
  flashes). So a clip with laughter, cross-talk or game sound keeps its pauses: don't count on trimming to
  get under 40s. Example: run 7's crematorium story, 77s → 32s with two cuts.
  **The story's ending stays.** Splice the middle, never the end: run 8's Gronk story was cut to 34s
  but stopped before "somebody told me that was the head of William Morris". Cut more of the middle
  instead (the fixed version kept 38s of 2m09s with 7 cuts). Estimate ~2.5–3 words per second.
- **Endings** are set from the audio (`splice.tail_end`), not Whisper's word end: it waits for the
  voice to drop, or cuts at the quietest seam 0.25–0.8s after the last word.
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

## Proven shapes (seen 3+ times, from `clip_log\INDEX.md`)
Structures that keep producing 8s and 9s. Not a checklist: a clip needs a payoff whatever its
shape. But when a candidate fits one of these, build it to land the turn.
- **Self-roast of the past self:** delusion then, blunt truth now.
- **Scene → twist → reaction:** the reaction is the payoff.
- **Plan meets reality:** a naive expectation, then the obvious question or the bad trade.
- **Observational take with a quotable capper:** scores 7 unless the capper is quotable.
- **Strange true fact, explained in one breath:** "people kept stealing our balcony."
- **Shameless confession, told proudly:** the teller is proud of the thing they should hide
  ("I didn't turn down one ID... their Westchester Rams card, I'd be like, that works").
- **Friend exposes the other's habit:** duo shows. One host outs the other; the defence makes it worse.
- **Escalating riff, capped:** a premise gets built on line after line, each topping the last, until one line
  caps it ("we're in an insane asylum... we let them dress up on Saturday... double his meds"). Take the whole
  build, never just its flat tail. The scorer misses these most (runs 7, 9).
- **Absurd image → strong verdict:** someone paints a ridiculous picture and lands a flat judgment on it
  ("if you make Heat, you should get to kill 20 horses minimum").
- **Insider rule revealed, pushed to absurd precision:** how a job or scene really works, taken one step too far.
- **Roast in one line:** a long ramble or a dumb move, answered by one dry line ("that wolf didn't have a weapon on
  him, bro"). The line is short, so take enough of what it answers. The scorer misses these (runs 10, 12).
- **Made-up fact or dodge, caught live:** someone bluffs or dodges and the room calls it on the spot ("who would you
  consider a friend?" / "you pulled the Bill Clinton: what is is?").

**Build backwards from the payoff.** Find the payoff line, then start at the *latest* line that
still makes sense cold. A story told over 45s often has a 20s clip inside it (run 4: "I spent
three, four hundred thousand coming into the draft. And my check was three hundred thousand").

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
- **Hallucinated loops and word salad** can sit right beside a good clip (run 6: "he's in the
  neighborhood" x40 at 1:11:34, clip 61 starts 20s later). Read the clip's own captions.
- **Misheard names:** fix the caption when you're sure (Cat → Katt Williams); otherwise cut around it.
- **Dropped curse words:** Whisper often leaves the curse out entirely ("who gives a has nothing to do with
  them"). If the punchline needs it, restore it with a caption fix on the word before (the caption masks it as
  `****` anyway). A fix replaces that word everywhere in the clip, so skip it when the word before is "a" or "the".
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
- Group shows never go quiet (run 4, six people: 21% of seconds spiked). Ignore it there too.
- Compressed studio mixes can show zero spikes (run 6, Flagrant). Ignore it there too.
- Loudness alone never selects a clip.

## Signal 3 — Transcript (the decider)
Signals point you to places; the transcript decides. A strong moment with no signal beats a
peak with no payoff. Run 1: 2 of 5 kept clips had no signal. Run 2: all 5. **Always read the
whole transcript.**

Drop on sight (any theme): ads, cold-open teasers (the full moment is later), intros/outros, "subscribe", housekeeping, rapid-fire Q&A lists,
cross-talk captions can't follow (people talking *over* each other; quick back-and-forth lines are fine, and so is
one voice with "yeah"s under it), gestures the viewer can't see ("they were like *this*"),
setups whose payoff is outside the length limit.

## Selection order
0. Check transcript health. Mark ad reads off-limits.
1. List real heatmap peaks, if any.
2. Read the full transcript with peaks and loudness clusters marked. Episodes over ~1h:
   read in ~15-min chunks with ~1 min of overlap so no clip gets split across a boundary.
3. For each candidate, find the payoff line; build the window backwards to a clean opener.
4. Run the three tests. Drop failures.
5. Score every survivor (rubric below). Render everything scoring **8+** (Tko's rule after run 11: 7s are filler; every 7 re-checked in run 11 failed).
6. Mix kinds. No overlaps and no two clips on the same sub-topic. Two different stories may
   sit back to back (run 3: "no-shirt overalls" was dropped for ending 11s before clip 18; wrong).
7. **Same story type twice:** keep the version with the bigger payoff, not the first one found.
8. **No turn, no clip.** A take or story with no capper is not a 6, it's a reject.

## How many clips
**No fixed number, but a ceiling** (Tko's rule, 2026-10-04): **at most 20 clips per video, 30 for
a video over 3 hours.** Under the ceiling the episode decides. A dead 2-hour episode might give 2;
a great one might give 15. Never pad the count with 5s to hit a number. When more than the ceiling
pass the bar, keep the highest scores and log the rest as rejected with "over the cap". Code holds
the line: the scorer's extras land in Review unticked, and a render with too many ticked is refused
(`review.clip_cap`). Density so far: ~4/hr (runs 1–2, host + non-comedian guest) to ~8/hr (run 3,
two comedians trading road stories).

**Same-story dedupe:** comedians tell many versions of one story type (run 3 had 5+ "I
bombed" stories). Keep the best one per story type, not every one that passes.

## Score (1–10, absolute, not relative)
Each clip is scored against the bar, **not against the other clips in the episode**. If
all five are great, all five are 9–10. If none are, none are.
**Calibration (runs 3–9, every run):** the model scorer rates the best clips one point low. A clip with a clean
payoff, a cold opener and no flaw you can name is a 9. Save 8 for a strong clip with one flaw you can name.
- **10:** would bet on it. Instant hook, clean payoff, perfect cold read, no weaknesses.
- **9:** strong on all three tests; one tiny nitpick.
- **8:** strong payoff; one real flaw (weak opener, slight overrun, a risk flag).
- **7:** good moment, noticeably flawed cut (filler opener, runs long past the payoff).
- **6:** postable filler. Passes the tests, but nobody shares it.
- **≤7:** don't render. Log it as rejected with the reason.
Write the score and a one-line reason in the run's `clip_log\` file. The score goes in the filename.

## Post description (one per clip, written with the pick)
Saved next to the clip as `NN_s<score>_<name>.txt`; Tko copies it into the post. Three parts, each on
its own line:
1. **Hook** (under ~70 characters): the premise that makes someone stop, in plain words. Never
   the punchline; the clip delivers that. "He paid for his first rookie year before he got paid."
2. **Credit:** show and guest, always. "From <show> <episode> with <guest>." Clips are someone
   else's work; the credit stays.
3. **Hashtags: 10–15, all on one line** (Tko's rule: at least 10). Never more than 15: YouTube ignores
   every hashtag on a video that has 16 or more. Mix three kinds, each tag related to the clip or theme:
   - **Who:** the show, host and guest (#soderpodcast #dansoder #louisck).
   - **Theme:** #comedy #standup #standupcomedy #comedypodcast #podcast #funny #comedian.
   - **This clip:** 2–4 tags on its subject (#nursinghome #dogsoftiktok #seinfeld #pootietang).
   No tags for things the clip isn't about. **Don't write these four; code adds them to every post**
   (Tko's rule): #xybca #fyp #blowthisup #viral. That makes 14–19 in the file; YouTube posting trims
   the most generic ones (#funny, #podcast, …) first, then tags from the end of the line, to stay at 15,
   and never drops the required four. **So order the line by importance: who, then this clip, then theme.**
No emoji walls, no "wait for it", no "you won't believe".
**The post text is clean even when the clip isn't** (Tko's rule, 2026-10-04). Nowhere in the hook or the
hashtags: a curse word or slur (a masked `****` counts, so does one inside a tag like `#tightshit`), or
anything about sex, porn, nudity or drugs (weed included), even when that is the clip's whole subject.
Write around it: sell the situation, not the off-limits word ("His roommate's hobby cleared the room",
not "His roommate watched porn at dinner"). Pick clip tags from the clean parts of the subject. Alcohol
and toilet humor are fine. `review.off_limits` refuses a render or a post that has the plain words; the
allusions are on the writer.

## Risk flags (mention, don't auto-reject; Tko decides)
- Rumors or accusations about named real people. Drug-use rumors about named celebrities →
  skip; there's usually a safer clip on the same topic nearby.
- **N-word, race, religion or trans bits: judge them like any other clip.** Tko's ruling after
  run 5: "if the clip is good I don't care if it has the N-word." Score on the payoff, then add a
  risk flag so Tko knows. The caption shows `****`, never the word (see Render).

## Render — the layouts a clip's type calls for
**Podcast: BLUR + TRACK, + SPLIT when both faces share the shot. Streaming: BLUR + GAME on
gameplay clips, BLUR + TRACK when there is no gameplay.** Tko posts the variants across
platforms and lets performance decide. Output:
`Finished_Clips\<Podcast|Streaming>\<show>\NN_s<score>_<name>_{blur,split,track,game}.mp4`
(e.g. `Podcast\Flagrant\64_s9_bouncer-every-id-works_track.mp4`).
NN keeps counting up across runs, from the clip log, even after clips are deleted.
- **BLUR:** full 16:9 frame centered, blurred copy fills top and bottom. Never cuts anyone out.
- **SPLIT:** two faces stacked (1080x960 each), captions on the seam. Top = left person.
  Needs both people *in the same shot for the whole clip*. Multi-camera shows that cut
  between single close-ups (run 3, JRE) can't do SPLIT. Skip it and say so; don't fake it.
  Faces must also be big enough: a wide couch shot with ~40px faces would be a 4x upscale
  (run 4). `reframe.plan` skips SPLIT when a face is under ~H/13.
- **TRACK:** 9:16 full-height crop. The clip is split into camera shots first (ffmpeg `scdet`,
  threshold 10; real cuts score ~22–24). Per shot: 1 face → center on it; 2+ faces → follow
  the talker by mediapipe `jawOpen` (switch only if clearly higher, hold ≥ 1.5s); 0 faces →
  center of frame.
- **GAME** (Streaming only): webcam across the top at full width (~1/3 of the frame for a 16:9
  cam), gameplay under it, captions on the seam. Replaces TRACK and SPLIT on gameplay clips, so
  those render BLUR + GAME. Decided per clip: a stream clip with no gameplay gets BLUR + TRACK on the
  streamer. Edited uploads cut to the camera full screen mid-clip (run 12: zoom stretches in 11 of the 18
  gameplay clips, and 193 is camera-only); GAME switches to a full-height crop on the face for those
  shots and its captions drop to the low third.
  **Look at a strip of frames across each rendered clip**, not one frame. The webcam box is found once per video (`reframe.cam_box`, cached in
  `work\<slug>\facecam.json`). **Look at `work\<slug>\facecam.jpg` before approving**; a wrong
  box is fixed by putting `"facecam": [x, y, w, h]` at the top of `review.json`.
- **No plain center crop:** wide shots put people at the edges.
- Face detection is OpenCV YuNet. mediapipe's short-range detector failed on wide shots
  (boxed hands, a plant pot, a belt buckle). **Draw boxes on one frame per show and look
  before rendering.**
- Captions: burned in, up to 3 words per line, word-timed. BLUR/TRACK low third; SPLIT on the seam.
- **No curse word readable on screen** (Tko's rule). `render.mask_curses` turns it into `****`;
  the audio stays as spoken. Includes slurs. Add words to `render.CURSE` if one slips through.
- Delete `work\<slug>\source.mp4` after rendering.
