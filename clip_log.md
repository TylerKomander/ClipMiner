# ClipMiner — clip log

Worked examples for future models. Rules live in `skill.md`; this file shows them applied.
Every entry uses the same fields so code can pull a few relevant ones into a prompt.
Kept entries show what good looks like. Rejected entries show what to avoid. Both matter.

Heat = heatmap bucket value(s) the clip overlaps (0–1, relative). Loud = seconds ≥ 6 LU above
the episode median / max LU above median.

**Built to outlive the theme.** Each run is tagged with the theme it was judged under. Patterns
are written twice:
- **Shape (universal):** the structure that makes the clip work in *any* niche.
- **Here (theme):** how that shape showed up under this run's theme.
Lessons are tagged `[universal]` or `[theme]`. When the theme changes, keep the shapes and
universal lessons and re-derive the "Here" parts for the new niche.

**Posted:** per-clip performance by layout (blur/split/track) and platform, filled in once Tko
posts. That will become the real signal for layout and pick quality.

---

## Run 3 — Joe Rogan Experience #2187 (guest Adam Sandler), 2h17m, 2026-09-30
**Theme:** `comedian-podcast` · **Posted:** _(pending)_ · **Layouts:** BLUR + TRACK for all;
SPLIT skipped (see Layouts below)

**Episode read:** two famous comedians trading career war stories: early bombs, youthful
delusion, road life, SNL, first movies. Multi-camera: hard cuts between single close-ups of
each, almost never both in frame. One host-read ad (ZipRecruiter, 8:33–9:57).

**What the signals did:**
- Heatmap top peak 9:38 (1.00) = ZipRecruiter ad-skip landing again. Evenly spaced peaks
  at 28:55 (0.69) and 48:11 (0.66), ~19 min apart, over ordinary talk. Suspected YouTube
  mid-roll breaks, unconfirmed.
- Real peaks landed on picked clips: 35:48 (0.42) → clip 15, 1:25:22 (0.40) → clip 20,
  2:05:18 (0.38) → clips 26–27.
- Loudness: 216 spikes. Useful as "they're laughing here" but too common to rank by.
- Transcript: punctuated, except 1:28:52–1:47:42 where Whisper dropped to lowercase and
  recovered. ~100 short same-timestamp runs were timing collapse, not hallucination.
- Transcribe 925s for 137 min (~6.7 min per hour). Download 544s.

**Tko's verdict:** _(pending)_

**Clips** (all: Shape = universal structure, Here = comedian-podcast form)
- **11 · 8 · Class clown, stick with that** (5:23, 38.9s). Opens "I did a Boston club, Comedy
  Connection, when I was 17. I ate it." Payoff: MC says "class clown... maybe stick with that
  place." −1: 39s, the setup can't be trimmed. Shape: *failure → a stranger's verdict*.
  Here: a humiliating put-down the teller now finds funny.
- **12 · 8 · Skinny Cow math** (13:12, 29.5s). Opens "The grapes lead to waffles." Payoff: "if I
  have a third, it's still in the threes... I got to stop, man." Shape: *self-justifying logic
  spiral*: each step sounds reasonable, the total is absurd. Here: a food confession.
- **13 · 8 · Kickboxing reality check** (19:16, 34.5s). Opens "I was like, let me take
  kickboxing just in case." Payoff: "15 guys from school already advanced... that guy can crush
  me too." Shape: *plan meets reality*. Here: the teller's tough-guy fantasy dies on day one.
- **14 · 7 · Lied to friends, Robin Williams** (33:42, 28.6s). Opens "I remember being on pay
  phones..." Payoff: "I ate it in front of Robin Williams. But I changed the story: yeah, he
  liked that shit." −2: the setup ("I told my friends I'd be big") had to be cut for length,
  and "them" is inferred. Shape: *fake it till you make it, caught in the lie*.
- **15 · 9 · Dad: you don't look great** (35:26, 27.5s). Opens "I fucking thought I was
  phenomenal..." Payoff: "Just so you know, you don't look great." / "You are so off on that,
  dad." Heatmap real peak. Shape: *delusion vs. blunt outside truth*. Here: the dad is the
  deadpan straight man.
- **16 · 7 · Paul McCartney corporate gig** (43:08, 26.2s). Opens "The only fucking reason I did
  it was Paul McCartney did it the year before." Payoff: "What the fuck is wrong with you
  people?" −2: "did it" = a corporate gig, never said in the window. Borderline cold read.
  Shape: *prestige bait → a bad trade*.
- **17 · 9 · Bombing is like...** (44:15, 23.2s). Opens "I say bombing on stage is like sucking
  a thousand dicks in front of your mother." Payoff (guest's topper): "My mother would 100%
  at the end say, you could've done it better." Shape: *outrageous comparison → someone tops
  it*. Here: a stand-up bit plus the guest's escalation. Risk: crude in the first 3s (reach),
  fine for the theme.
- **18 · 8 · Rob Halford's gay biker trick** (59:35, 30.3s). Opens "If you look back at the
  metal days..." Payoff: "they didn't even understand they'd been tricked into dressing like a
  gay biker." Shape: *hidden-origin reveal*: a familiar thing turns out to come from somewhere
  unexpected.
- **19 · 9 · Security hoodie escape** (1:12:44, 18.6s). Opens "I always knew that this job was
  like, what do you get paid? 20 bucks an hour?" Payoff: "I put the hoodie on. Like, I'm out of
  here. Oh, I'm with you guys." Shape: *clever cowardice*: a practical dodge told proudly.
  Short, fully self-contained. The model of a tight clip.
- **20 · 9 · Podcast pitch during Chris Rock** (1:25:52, 28.0s). Opens "When I used to see
  Chris at the Store..." Payoff: "That guy's never been on my podcast to this day." Heatmap
  real peak. Shape: *wrong moment → a consequence that lasts to today*.
- **21 · 7 · Is my son a murderer** (1:39:12, 24.4s). Opens "Quinn read a lot of..." Payoff: dad
  wondering "is my son a murderer, why is he talking so much about murder." −2: opens mid-
  context ("Quinn" = Colin Quinn, unexplained), lowercase captions. Shape: *innocent
  enthusiasm, misread by a parent*.
- **22 · 8 · Malibu fires before a set** (1:41:08, 35.6s). Opens "i sit down and i'm watching
  this documentary on the malibu fires." Payoff: crying over "rusty where are you," then "jb's
  not here yet so we're gonna have you open." Shape: *worst possible headspace → called up
  right then*. −1: length, lowercase.
- **23 · 8 · Joey Diaz doesn't do Sundays** (1:45:20, 33.6s). Opens "i brought a second opening
  act in case joey didn't show up." Payoff: "i told you joe rogan, i don't do sundays" / "you
  never told me!" Ended before the misheard "shot in an hour". Shape: *backup plan justified by
  one absurd story*. Here: an impression of a famous friend.
- **24 · 7 · That loser's killing?** (1:54:06, 33.8s). Opens "I got on Saturday Night Live."
  Payoff: the old peers watching: "that fucking loser's killing? What the fuck did that have?"
  Shape: *old doubters witness the success*.
- **25 · 8 · Thought I was a stud** (1:55:22, 23.7s). Opens "I wanted to be a movie star." Payoff:
  "I thought there was something fucking attractive about me... that's a fucking stud right
  there." Shape: *self-roast of past delusion*.
- **26 · 8 · Babes Ahoy, no script** (2:04:31, 37.6s). Opens "I get off stage..." Payoff: "do
  they have a script? ... I didn't even know there were scripts." −1: 38s. Shape: *naive
  yes → an insider asks the obvious question*. Heatmap real peak.
- **27 · 9 · Acting class dumb voice** (2:06:22, 21.7s). Opens "I was in acting class at school
  and I did a scene. I thought I did great." Payoff: "I watched the shit back. That kid was
  right, man. Fucking pathetic." Shape: *defensive at the time → concedes years later*.
  Heatmap real peak.
- **28 · 7 · Psycho, watch me for an hour** (2:14:06, 27.1s). Opens "What a fucking odd feeling..."
  Payoff: "What a psycho of a human being to just go, let me come look at this." Shape: *reframe
  something normal as insane*. −2: observational, no story, mild payoff.

**Rejected** (and why)
- 9:38 heatmap 1.00: ad-skip landing (ZipRecruiter).
- 28:55 / 48:11 heatmap 0.69 / 0.66: evenly spaced; Bill Maher's music stand, show-order
  talk. Nothing to clip.
- 1:37:46 JFK book, then bombed: good, but the same story type as clip 22 (bad headspace
  before a set). Clip 22 is funnier. Dedupe.
- 58:48 tie-dyed overalls at a battle of the bands: funny, but it ends 21s before clip 18
  starts.
- 1:31:55 MTV tape → "don't answer your phone, go to the pool hall": needs 40s+ of deal context.
- 17:49 Farley "gray like wet cardboard": a sad addiction story about a dead person. Off-theme.
- 1:25:01 Will Smith slap discussion: commentary, no single payoff, 60s+.
- 2:05:34 Milton Berle: relies on the photo being shown on stream.
- 2:08:01 Chappelle "best New York boobs" medals: relies on the clip shown on screen.
- 1:59:24 Dunbar's number / "your brain's not designed to be famous": interesting, but a
  1-min explainer with no capper.

**Layouts:** SPLIT needs both people in one shot for the whole clip; JRE never holds a
two-shot. TRACK follows each camera shot (ffmpeg scene detection, then center on the face).
Result: SPLIT available for 0 of 18. TRACK shot counts: 1 shot for 11 clips (the storyteller
held the camera), up to 10 shots for clip 16 (26s). Spot-checked 12, 16, 20: every shot centered
on the right face, and cuts line up with who's talking.

**Lessons**
1. `[universal]` Ad-skip peaks again. Evenly spaced peaks are a second fake-peak pattern (guess).
2. `[universal]` Whisper can go lowercase *mid-episode* and recover. Check the whole transcript,
   not just the start.
3. `[universal]` Short same-timestamp word runs ≠ hallucination. Only long or repeated runs.
4. `[universal]` Dry-run first/last 5 words for every clip before rendering. It caught 4 cut-off
   payoffs this run.
5. `[universal]` Multi-camera shows: detect shots first. SPLIT only works for shared-frame shots.
6. `[universal]` When a storyteller needs 37–38s, the missing tool is jump cuts, not a looser cap.
7. `[theme]` Two comedians = ~8 clips/hour, mostly war stories (bombs, delusion, road, first
   breaks). Dedupe by story type: they'll tell five "I bombed" stories.
8. `[theme]` The guest roasting his younger self (15, 25, 27) was the richest vein; each has a
   clean "then vs. now" payoff.

---

## Run 2 — Matt and Shane's Secret Podcast Ep 638 "Beef Raised Right" (guest Mason "Bric" LaDue), 76.5 min, 2026-09-30
**Theme:** `comedian-podcast` · **Posted:** _(pending)_

**Episode read:** two hosts + a rancher guest who used to be a rap-industry fixer (weed,
lean, touring with Wiz Khalifa, early Post Malone), now raises Akaushi cattle. Crude, loose,
lots of tangents. One static wide shot the whole episode. One ad + tour-date block at 35:40.

**What the signals did:** nothing. No heatmap (not exposed for this video), and loudness was
flat (5 spikes ≥ 6 LU in 76 min). Every pick came from reading the full transcript.
Transcript came back all lowercase, no punctuation, with one hallucinated repeat at 31:48.
Transcribe took 634s (vs 405s for a similar length in run 1), probably related to the
degraded output. Unconfirmed.

**Tko's verdict:** all 5 kept, "funny and they clip well". Ruled the cap can stretch a little
past 30s for the capper, so clips 02 and 10 could now include their full endings.

### PICKED 06 — "Rather be gay than coke" · funny
- **Score:** 9/10 · clean anecdote shape, zero context needed; nitpick: reaction line is a little mumbled
- **Time:** 27:59–28:19 (20.5s) · Heat n/a · Loud 0
- **Opens:** "i was sitting outside of the venue in spokane and two dudes got kicked out"
- **Payoff:** "that's a crazy pivot, like you'd rather be gay than coke"
- **Why:** the textbook anecdote shape: a scene is set in one line, the twist is the excuse
  ("we weren't doing coke, we're gay, we were having sex"), and the teller's reaction lands
  the joke. Needs zero context.
- **Shape (universal):** *scene in one line → twist → the teller's reaction.* The reaction
  is the payoff, not the twist. It tells the viewer how to feel.
- **Here (theme):** someone caught → absurd excuse → deadpan "you'd rather be X than Y".

### PICKED 07 — Don't ask a rancher how many head · funny / interesting
- **Score:** 9/10 · insider rule + self-own capper; nitpick: 5s silent beat mid-clip
- **Time:** 45:52–46:18 (25.3s) · Heat n/a · Loud 0
- **Opens:** "how many head of cattle you got"
- **Payoff:** "God damn, I try to be a cowboy for 30 seconds"
- **Why:** an insider rule outsiders don't know (asking herd size = asking someone's bank
  balance), revealed live when the host breaks it. The host's self-own is the capper. A ~5s
  silence (laughter off-mic) sits in the middle; kept it, it plays as a beat.
- **Shape (universal):** *an insider rule revealed live.* Outsider breaks an unwritten rule
  of a world → insider explains it → the moment resolves. Viewers love learning the rule.
- **Here (theme):** the resolution is the host's self-own ("I try to be a cowboy for 30
  seconds"). In a non-comedy theme the resolution might be the explanation itself.

### PICKED 08 — The horse thinks you saved its life · whacky / interesting
- **Score:** 8/10 · great fact, clear; flaw: no laugh, relies on "wait, what?" alone
- **Time:** 53:26–53:49 (22.5s) · Heat n/a · Loud 0
- **Opens:** "there's a psychological thing that you do where you get a horse and you lay it down"
- **Payoff:** "he's already saved my life, I'll do whatever he says"
- **Why:** a strange true fact explained clearly in one breath. The "wait, what?" reaction.
  No jokes needed.
- **Shape (universal):** *strange true fact → how it works → what it means, in one breath.*
  Works in almost any theme (science, history, trades, sports).
- **Here (theme):** the ending is phrased from the horse's point of view, which makes it funny
  as well as interesting.
- **Cut off:** "that's the theory, sometimes it works" follows. Good nuance, but it deflates
  the payoff. End on the strong line.

### PICKED 09 — Malls are retail hospice · funny / relatable
- **Score:** 7/10 · best line at 9s, then 18s of riffing past it
- **Time:** 21:21–21:49 (27.9s) · Heat n/a · Loud 0
- **Opens:** "i went to a mall recently and it's dastardly in there these days"
- **Payoff:** "it's like retail hospice... the kiosk guys aren't even passionate no more"
- **Why:** universal observation plus two quotable phrases ("retail hospice", kiosk guys
  have lost their heart). Anyone who's been to a mall recently gets it instantly.
- **Shape (universal):** *shared experience + a phrase that names it.* Relatability does
  the hook; one coined phrase ("retail hospice") makes it quotable.
- **Here (theme):** delivered as a riff with exaggeration.
- **Weakness:** the best line lands at 9s, then it runs 18 more seconds of riffing. A tighter
  cut ending at "no more" (≈14s) might be stronger. Worth testing against Tko's taste.

### PICKED 10 — Lean is the most asinine drug · funny
- **Score:** 8/10 · strong image + verdict; split/track run to the real capper, blur stops early
- **Time:** 18:47–19:10 (23.2s) · Heat n/a · Loud 0
- **Opens:** "the lean, it's just such a funny... it was so expensive you put it in a baby bottle"
- **Payoff:** "the funniest drug of all time... it's got to be the most asinine"
- **Why:** the absurd image (grown millionaires sipping from baby bottles in the club) plus a
  strong verdict line. Drug topic, but a take on it, not glorifying.
- **Shape (universal):** *absurd image → strong verdict.* Paint one picture the viewer can
  see, then give a confident one-line judgment of it.
- **Here (theme):** the verdict is a superlative insult ("the most asinine drug").
- **Trade-off:** the true capper ("i can understand coke and molly but i'm going to sedate
  myself") ends at 19:16. Including it pushes past 30s. Same open question as run 1 clip 02.

### REJECTED candidates (and why)
- **31:14 Post Malone "White Iverson" discovery** (Wiz: "I'm not playing it because it's your
  friend" → plays it → Mac Miller calls) — best story in the episode, but: (1) Whisper
  hallucinated a repeated sentence inside it, (2) Post Malone is never named in any 30s window.
  Fails cold read. Revisit when title overlays exist.
- **15:19 Bieber and lean** — funny line ("the lean industry didn't have the bandwidth for the
  Bieber rub") but it's a drug rumor about a named celebrity. The guest even says "this is all
  rumoring". Took the lean take at 18:47 instead.
- **26:46 Spokane bus-hub city** — funny and clear, but only 45s from clip 06 and the same
  city. Took one Spokane clip, kept variety.
- **17:58 friend drank the pint and crashed into a hill** — whacky, but too close to clip 10
  and weaker.
- **33:57 Charlamagne / DJ Akademiks elevator** — implied threat toward named people. Risk.
- **64:57 Trump + Argentine "ground beef product"** — genuinely interesting insider
  explanation, but ~90s long, political, and no single payoff line.
- **0:00 cold open, sound guys with arms crossed** — relies on a gesture ("they were like
  this"). Captions and viewers can't see what "this" is.
- **35:40 ad + tour dates** — off-limits.

### Layout re-render (same day, after Tko asked for openshorts-style vertical)
- Re-rendered 06–10 as `_split` and `_track` next to the BLUR originals. Clip 10 extended to its
  real capper ("i'm going to sedate myself", 30.5s) under the new length ruling.
- Face positions (YuNet, 2 per clip, ~90px wide): left ≈ x 470, right ≈ x 1620 of 1920.
- TRACK spot-check on 07: 2s host asking ✓, 6s guest answering ✓, 11s host laughing at the
  capper ✓. Switch rate is high in back-and-forth clips (every ~1.6s in 07/09/10). Watch
  whether that feels jumpy.
- First attempt used mediapipe's face detector and was wrong in every clip (a plant pot was
  "face #2" so SPLIT framed the pot). Caught by drawing boxes on one frame. **Lesson: verify
  detections visually once per show before rendering.**
- Tko's ruling: no layout rule. Every clip gets all three; performance decides.

### Lessons from run 2 (folded into `skill.md`)
1. `[universal]` No heatmap + flat loudness is normal. The transcript pass is the real scorer.
2. `[universal]` Check transcript health first: identical-timestamp runs = hallucination.
3. `[universal]` Select words by start time and eyeball the last 4 words. Losing the payoff
   word is the worst possible cut.
4. `[universal]` A story whose subject is never named in the window fails, however good it is.
5. `[universal]` Two near-misses where the best capper sat just past 30s → Tko ruled up to
   ~35s is fine for the payoff.
6. `[theme]` Guests who aren't comedians (the rancher) are gold when the hosts poke at their
   world: the comedy comes from the collision, not from the guest being funny.
7. `[universal]` Verify face detections on one frame per show before rendering.

---

## Run 1 — Wild Ride #222 (Steve-O hosts, penguinz0 guest), 73.5 min, 2026-09-30
**Theme:** `comedian-podcast` (judged before themes existed; fits) · **Posted:** _(pending)_ ·
**Layouts:** BLUR only. The source was deleted before SPLIT/TRACK existed.

**Episode read:** two-person sit-down, casual and jokey, frequent wide shots. Three sponsor
reads (13:00, 23:15, 35:40) plus an intro ad. The episode title (Dr. Disrespect) is a passing
mention at 14:07, not a segment. **Never trust the title to tell you where the good part is.**

**What the signals did:** heatmap top peaks (1:28 = 1.00, 23:31 = 0.90, 36:00 = 0.77,
13:13 = 0.70) were all viewers skipping ads and landing on "let's get back to it". Real content
peaks were 2:56 (0.59), 43:21 (0.31), 49:58–50:42 (0.30–0.31). Two of five kept clips had no
signal at all and came from reading the transcript.

**Tko's verdict:** all 5 kept. "Funny, whacky and interesting moments" is the target.

### KEPT 01 — Vitaly paid actors · funny
- **Score:** 8/10 · energy build + great capper; flaw: rumor about a named creator
- **Time:** 49:41–50:10 (29.3s) · Heat 0.25–0.30 · Loud 15s / +9.4
- **Opens:** "So there's word on the streets that Vitaly has been paying these actors to play
  these pedophiles."
- **Payoff:** "Won't someone think of the predator's feelings, please?"
- **Why:** opens on a juicy claim (hook in first 3s). Then it turns into a bit: they worry about
  saying the word on YouTube, switch to "predator", "let's use the right nomenclature",
  "have some respect", and it's capped with a sarcastic one-liner. A dense loudness cluster
  (15 of 29 seconds spiking) confirmed the energy. Cut right after the payoff.
- **Shape (universal):** *energy build → capper.* A run of short back-and-forth lines where
  intensity rises, closed by one line that sums it up. Look for loudness clusters; the capper
  is usually the last short line before the energy drops.
- **Here (theme):** a serious topic turns into a bit, capped by a sarcastic one-liner.
- **Risk flag:** repeats a rumor about a named creator. Tko kept it; still flag these.

### KEPT 02 — Softcore re-upload origin · whacky
- **Score:** 8/10 · elite first line; flaw: stops before the real capper ("this is the grind")
- **Time:** 3:04–3:26 (21.8s) · Heat 0.59 (strongest real peak) · Loud 3s / +7.2
- **Opens:** "So I actually had a channel before this one in 06, where I used to re-upload
  softcore porn."
- **Payoff:** "...I noticed there was a hole in the market." / "I was like, all right, I could
  do that."
- **Why:** an absurd, true confession from a huge creator. The first sentence alone is enough
  to stop a scroll. The heatmap agreed.
- **Shape (universal):** *first-sentence confession.* A surprising admission about the
  speaker's own past, stated plainly in line one. Everything after is detail.
- **Here (theme):** the confession is embarrassing, and the teller treats it as a hustle.
- **Mistake made and fixed:** first cut started at the Whisper segment start, "That's on this
  channel.", which means nothing without the previous line. Moved the start to "So I actually".
  **Always check the first 3 words of a clip against the cold-read test.**
- **Trade-off:** the stronger capper ("I was 11, and I was like, this is the grind.", 3:34)
  would have pushed it to 31s, over the limit. Stopped at "I could do that." instead.
  Open question for Tko: is 31s okay when the capper is that good?

### KEPT 03 — Photoreal shotgun · interesting / whacky
- **Score:** 6/10 · vivid but borderline cold read ("when you see it")
- **Time:** 43:25–43:42 (17.5s) · Heat 0.31 · Loud 0
- **Opens:** "When you see it, they have like animations that will reflect where you shot them."
- **Payoff:** "He falls over, starts gripping his legs, fucking screaming, and it looks so real."
- **Why:** a vivid, visual story: you can picture it without seeing the game. Ends on a clean
  takeaway line ("impressive what games are going to be looking like").
- **Shape (universal):** *vivid description → takeaway.* Words alone make you see it, then
  one line zooms out to why it matters.
- **Here (theme):** graphic and a bit crude ("fucking screaming").
- **Weakness:** "When you see it" leans on the prior sentence ("it" = someone dying in the
  game). It passed because the next sentence explains it fast. Borderline cold read.

### KEPT 04 — MrBeast "Antichrist" · interesting
- **Score:** 7/10 · good contrast take; filler opener
- **Time:** 15:31–15:48 (17.1s) · Heat 0.11 (no signal) · Loud 0
- **Opens:** "I mean, that's just kind of the nature of the world."
- **Payoff:** "here's why Mr. Beast is actually like the Antichrist."
- **Why:** a relatable take with a built-in contrast (thousands of wells vs. "Antichrist"). A
  well-known name helps. Found by reading the transcript, not signals.
- **Shape (universal):** *contrast take.* Put two things side by side that shouldn't coexist
  (thousands of wells / "Antichrist"). The gap between them is the payoff.
- **Here (theme):** the contrast mocks internet outrage.
- **Should have done better:** the opener is filler. Starting at "Unfortunately, Mr. Beast
  builds thousands of wells..." (15:33) is a stronger hook and still 15s. **Cut filler openers
  ("I mean", "yeah so") when the next sentence is the real start.**

### KEPT 05 — Gobbledygook process · interesting / funny
- **Score:** 6/10 · quotable but opens on "And"; weakest of run 1
- **Time:** 25:22–25:37 (14.4s) · Heat 0.17 (no signal) · Loud 0
- **Opens:** "And the process is super quick because I'm just yapping at a camera."
- **Payoff:** "I'll just start spitting absolute gobbledygook. And then maybe like 45 minutes
  later, I'm like, run it."
- **Why:** self-deprecating behind-the-scenes from a big creator; "gobbledygook" and "run it"
  are quotable. Short and complete.
- **Shape (universal):** *behind-the-scenes reveal.* How someone known for X actually makes
  X, when the answer is simpler or messier than expected.
- **Here (theme):** self-deprecating ("spitting absolute gobbledygook").
- **Should have done better:** opens on "And". Dropping it would be cleaner. Weakest of the five.

### REJECTED candidates (and why)
- **1:28 "bonafide unicorn" intro** — heatmap 1.00, loud +13. Ad-skip landing after the intro
  sponsor; the content is a polite welcome with no payoff.
- **13:13 / 23:31 / 36:00 peaks** — all sponsor-read endings. Discarded before reading further.
- **14:07 Dr. Disrespect (the title topic)** — a one-line mention inside a question; the answer
  drifts into general "people will hate you". Nothing to clip.
- **36:27 Terrence Howard "1×1=2"** — funny idea but the clip opens "people are trying to prove
  how I'm wrong about...": the viewer doesn't know what he said. Fails cold read. The setup
  lives in an earlier part of the conversation, too far back to include.
- **32:20 "Y Files" desert-island picks** — heat 0.27, but it's list talk ("I'd pick this
  channel") with no payoff line.
- **64:40 "Twitter is so dark" / fish smashing** — heat 0.34–0.38, loud spikes, but it's
  fragmented cross-talk; half-sentences, no clear subject. Captions would be unreadable.
- **67:37 rapid-fire favorites** ("favorite console? favorite game?") — heat 0.27. Q&A lists
  never have a payoff on their own.
- **65:55 Cure Rare Disease charity** — sincere, clear, but flat. Not funny, whacky, or
  surprising.

### Lessons from run 1 (already folded into `skill.md`)
1. `[universal]` Filter ads before reading any signal.
2. `[universal]` Low real peaks (0.3) can still be the best clips; rank relatively.
3. `[universal]` 2 of 5 kept clips had zero signal. Always do a full transcript pass.
4. `[universal]` Start on the sentence that carries the thought, not the Whisper segment start
   or a filler word.
5. `[universal]` Center crop fails on wide shots.
6. `[universal]` The episode title doesn't tell you where the good part is.
