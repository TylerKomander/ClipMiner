# ClipMiner — how we pick clips

The rulebook. Read it whole before picking. `clip_log\INDEX.md` tallies every shape and lesson; the run files in
`clip_log\` are worked examples (read only the ones you're given). **(guess)** = not yet checked on a real run.
**Part A** (theme profile) says *what* is a good clip and changes per video type; **Part B** (universal) says *how*
to find, cut and render one.

---

# Part A — Theme profile

Tko picks the type before pasting the link: Podcast → `comedian-podcast`, Streaming → `streamer`, Movie →
`movie-recap`. Use the profile the prompt names; ignore the others.

## Theme: `comedian-podcast`
Long-form podcasts hosted by or featuring stand-up comedians: riffs, bits, road stories, guests who are often not
comedians. **Audience:** people who scroll for laughs and "wait, what?" moments.

**Payoff:** **funny** (a joke or punchline lands inside the clip; often a riff that builds, capped by a one-liner;
laughter helps, isn't required) is the priority. **Whacky** (an absurd true story or fact) and **interesting** (a
take or vivid description someone would share) fill the mix.

**Where it hides:** road/tour stories; a host breaking an unwritten rule of the guest's world and getting corrected;
hosts riffing on a serious topic until someone lands a sarcastic capper; the guest's strangest true fact from their
job or past; hot takes on everyday things; **a guest from outside comedy the hosts can poke at** (a rancher, an NBA
player, a famous fan: every question is a setup); a guest walking in mid-episode; hosts workshopping new bits out
loud; a deadpan athlete storyteller. **The hosts' own lines count even when the guest is the star.**

**Off-theme:** sincere segments (charity, gratitude), technical explainers with no joke, business talk, tour-date
plugs, **a guest or host plugging their own product** (free advertising, even when riffy). A politician guest is
mostly off-theme: clips come from the host's tangents and the guest playing straight man.

**Tolerance:** profanity and crude topics are fine. Only flag profanity in the first 3s (reach), not the topic.

## Theme: `streamer`
A streamer at a webcam, usually playing a game, often with friends on voice chat. Two runs behind it. Same audience
and bar as the podcast theme: funny first.

**A friend-group stream is a podcast with a game on screen** (16 of 19 clips in run 12 were banter). Judge the
banter like podcast banter; the game is the backdrop, not a reason to reject.

**Payoff:** **funny** (a roast, comeback, confession or rant, often a friend's line, which is fine); **whacky**
(something goes absurdly wrong in the game and someone says it out loud); **interesting** (a story told to the group).

**Where it hides:** lulls (waiting, loading, walking) when the group talks; right after a failure (who caused it,
who ran); a story one friend refuses to tell and the others drag out; **loudness spikes, which work here** (read
around every one); full-screen "just chatting" stretches at the start and end **(guess)**.

**You only have the words.** A scream with few words around it goes in `rejected` with "visual, check the frame" so
the reviewer looks. Judge everything else on the words. **Don't reject for:** a garbled transcript (gamer words are
misheard constantly: "are peeing" = RPing, "mac dumped" = mag dumped, "insulin" = incel; these are caption fixes);
a callback (only if the clip makes no sense without it); several voices (that's the format).

**A streamer reviewing other people's clips:** a moment counts only when the payoff is his own line (a rating with a
reason, a roast of the sender, a rant) and it lands for someone who can't see what he's reacting to.

**Off-theme:** silent or mumbled gameplay, pure callouts ("he's on me"), menus, mod setup, sub/donation thank-yous,
sponsor reads, scheduling, sincere drama about another creator.

**Before approving, set in `review.json` when they apply:** `"facecam": [x, y, w, h]` when the camera is a cut-out
over the game with no border (`cam_box` finds nothing); `"one_voice": true` when one person is on the mic (otherwise
a shouting voice is split into several and caption colours flip). Not for friends on voice chat.

**Transcript traps:** every voice is one stream of words with no speaker; game characters are transcribed too;
screaming comes out as a few words or a loop ("A, A, A" ×100). **Tolerance:** as `comedian-podcast`.

## Theme: `movie-recap`
A whole film or episode from a local file → **one recap short** plus its **funny moments** (below). The recap tells
the main story as a supercut of the film's own dialogue, in film order, ending included (references `UTBAKThAmI4`, `ZY4qS0KewuI`). Worked examples:
`clip_log\run-20-atlanta-s02e01-recap.md` (348, the reference: 16 short exchanges, 89s) and
`run-21-curb-s12e03-recap.md` (7 whole scenes, 154s). Read the moment table before picking.

**The goal is the most entertaining short that still tells the story** (Tko). "I understood it" is the floor.
**Funny beats everything, including the budget.** It must carry, in order: who the main character is and what they
want, what stands in the way, the turn, how it ends.

**Let the funny lines tell the story.** Follow the main thread only; a side plot or a serious line goes even if it's
good. When a beat can be carried by a laugh or a straight line, take the laugh. Every funny line a stranger gets
without the scene before is a candidate. **Every scene change is set up:** a moment before it says why we're there.

**Where the good lines hide:** lines that *state* the situation, a relationship or a threat, and the last line of a
scene. A line that only works with the picture can't carry the story: one or two per recap at most.

**Off-theme:** side-plot exposition, jokes that need the scene before, songs, crowd noise, a character the recap
hasn't introduced.

**Score** (1–10, the whole recap): can a stranger tell what it's about, who it's about and how it ends from these
lines alone? 8+ = yes, with a hook in the first 3s.

### How to build a recap, step by step
Do these in order and write each step's result down before the next. Failures come from steps 5–7 done loosely.
**If your notes call anything a weakness, you are not done: fix it or swap the moment.**
1. **Read everything once before picking.** The SDH subtitles (`subs_sdh.srt`) for names and who speaks (`NAME:`
   names only the cue it starts; never borrow one); the reading file end to end for the story. **Quotes and times
   come from the reading file** (Whisper), never the subtitles. Otherwise a speaker is known only from the dialogue
   (a reply comes from the person addressed) or "unknown". Never drop a line over a guessed speaker.
2. **Write the main thread in one sentence:** "<main character> has to <goal>, but <obstacle>; <turn>; <ending>."
   Back each clause with a quoted line and its time. The ending is the line in the main thread's last scene that
   shows the result (read past any standoff: "Where's X?" / "Not in jail" means X got away); say in one clause how
   it resolved. For an episode, the main thread is the plot the title names. Everything else is a side plot and
   stays out, even its funniest line. Side plot means the *scene*: a line said inside a main-thread scene stays.
3. **Start where the main thread starts** (the call, the order, the arrival). Earlier scenes only if a stranger needs
   them to know who the main character is.
4. **List every laugh on the main thread before choosing any**, with times, tagged: **L** a laugh a stranger gets
   cold, one you can state in a sentence (a one-word reaction isn't one); **S** states the situation, stakes or a
   relationship; **T** the title line or the line everyone quotes; **E** the ending. Most good candidates are L+S.
5. **Fill the arc in film order:** **hook** (moment 1: a mission, threat or strange situation in words, with its
   reason in the same moment) → **set-up** → **escalation** → **stakes/turn** → **outcome** → **button** (the best
   laugh in the main thread's *last* scene; a warning or an order is not a button).
   **Both ends of every moment:** read the sentence before `first_words` and after `last_words`. Take the one before
   if yours answers or points back to it ("No", "Yeah", "You don't…", "that/this" for something not yet said); take
   the one after if it's the reply, the punchline, or names something used later.
   **A moment is one whole joke, however long:** its set-up, the punchline, and the reply or topper; stop at the
   first line after the last laugh. **Never trim inside a joke to save seconds; drop a whole weaker joke instead**
   (Tko: "You cut early on some dialogue and jokes again, remember funny over everything"). A rambling answer is
   often the joke itself: keep all of it. Two picks under 10s apart in one scene are one moment. **Take the reply:**
   read 30s either side of every beat. A straight S-only moment only for the hook, a set-up that pays off later, a
   who-is-who line or one stakes line.
6. **Bridge check, every pair of neighbours:** if the place or the people change, the moment before sends us there.
   **Set-up check:** for every person, object or animal in the last third, find where it first appears or changes
   hands; that line must be in the recap, earlier. A line explaining it after it appeared is a payoff, not a set-up.
   Note pairs as `set-up <time> → payoff <time>`. A payoff that states its own set-up needs none. A set-up far
   before the main thread costs the hook: drop it if the payoff stands alone. A punchline pointing back to an
   earlier scene gets the one line from the same speech that names it, spliced in.
7. **Cold-stranger retell, a gate:** from only what your quotes state, retell in three sentences (who, what
   happened, how it ended), then write the question a stranger would ask at each moment (who is this? who is X to Y?
   where are we? where did that come from?): an earlier moment or that one must answer it. **Fail** if by moment 3
   the main character and what he is to the others are unclear; if a plot-driving person is never tied to him by a
   quoted line; if a new place has no line sending us there; if anything in the last three moments is unexplained.
   On a fail, go back to 5–6. A who-is-who line always earns its seconds. **You will pass yourself:** hand this step
   to a fresh reader given the full spoken text of every moment, numbered, no times or notes. Every question it asks
   is a fix. **Never hand in notes that say fail, "known gap" or "can't fix within budget".**
8. **Budget: 50–155s of speech, 8–24 moments.** A Short must render under 3 minutes and the render runs ~12% over
   speech (164s of speech rendered at 3:03.6). Trim filler *around* jokes: an opener the next line makes clear, a
   repeated dare, a scene-ending line after the laugh. The prompt gives the film's own pace. **Too long:** drop a
   whole joke, weakest first (S-only before any L, side beats before main; of two scenes telling the same joke keep
   the funnier). **Too short:** add the next-best whole L on the main thread. At least two thirds of moments carry
   an L. A moment over 160 words splits into two back to back; they play as one.
9. **Quote exactly:** `first_words`/`last_words` word for word from the reading file (words matched, not
   punctuation; a missing word drops the moment). `first_words` opens a sentence, `last_words` closes one. Rows
   wrap mid-sentence: if `last_words` reach a row's end, read on. If they don't finish a sentence or the funny part
   comes after, extend. A word that makes no sense was misheard: check the SDH, and copy boundary words from outside
   the misheard stretch (the viewer hears the audio). A moment long for its few words is a Whisper timing slip.
10. **Write the post text** and a one-line `why` per moment naming its slot (hook, laugh, stakes, set-up…).

**Post text:** the hook is a teaser question or a quote twist ("An offer he can't refuse?"), never the ending.
Credit: "From <Film> (<year>)."; a TV episode credits the show and its year. Hashtags: the film, its stars, the
genre, #movie #movieclips. The clean-text rule applies.

**Transcript traps:** Whisper drops lines spoken over a score and writes song lyrics as speech.
**Tolerance:** films carry slurs and violence in context; captions are still masked. Score on the story.

### Funny moments (besides the recap)
Every film also gets standalone shorts of its best laughs (Tko, 2026-11-09), picked after the recap. Each is **one
whole joke a stranger laughs at cold**: set-up, punchline, and the reply or topper.
- **Side plots count here**, and a joke may also be in the recap.
- **1–4 pieces, back to back in film order.** One when the scene stands alone. Add a piece only when the joke
  needs it: who someone is, the line a callback points to, the set-up of a payoff minutes later. An extra piece is
  that one line or exchange, not its whole scene. Never trim inside the joke.
- **10–40s of speech** (Tko: shorter). Cut the walk-up and the middle, not the joke: start at the line that sets
  it up, splice out lines between laughs. The first 3s state the situation in words (not a greeting); stop at the
  first line after the last laugh.
- **Only 8+**, scored by Part B. Few is normal: a drama may have none, a sitcom episode 2–5. Never pad. Same joke
  twice: keep the better cut.
- **Off-theme:** a sight gag with no line, a callback whose set-up can't be spliced in, a reaction line alone.
- **Quotes** as recap step 9. **Post text** as the recap's, its hook about this joke's situation, never the punchline.

## Writing a new theme profile
Add the type to `review.KINDS`, then copy a block above and fill the same fields: content, audience, payoff (and
its priority), where it hides, off-theme, tolerance. The run files' universal lessons still apply.

---

# Part B — Universal rules

## The bar
A stranger scrolling past stops and watches to the end. *Would I send this to a friend?* "Pleasant conversation" is
not a clip.

## Clip shape
- **Length: 10–30s, up to ~35s when the payoff needs it** (Tko), measured on the **finished** clip after splicing.
  Stretch only for the payoff; never pad.
- **Tell the whole story; cut what isn't the story** (Tko: "don't be afraid to use larger stories and just clip non
  useful parts out"). Before rejecting or trimming a long story, splice it with `cuts` (word ranges): cut an
  unrelated interruption, a branch the teller comes back from, a repeated setup, cross-talk. A listener's line stays
  only when it adds (a question setting up the next beat, a reaction that is part of the payoff, a topper). "Three
  ideas in 35s" is usually one story with two cuts. The source window may span ~4 minutes if the kept part is 10–40s
  and reads cold. **A payoff whose setup came minutes earlier is a splice** (setup, then payoff), not a reject and
  not the payoff alone. Never cut the payoff, its setup line or a reaction that is part of it.
- **The ending stays:** splice the middle, never the end. Estimate ~2.5–3 words per second.
- Dead air is trimmed in code only where the audio is quiet over 0.6s, so clips with laughter, cross-talk or game
  sound keep their pauses: don't count on trimming to get under 40s. Endings are cut from the audio. Don't list either.
- **Opening line** makes sense alone and pulls you in: a claim, a surprising fact, a question. Never "And", "So
  yeah", "That's", "Like I said", or a pronoun with no name.
- **Closing line:** end on the payoff, +~0.3s. **Stop on the payoff**: don't trail into the next topic or "yeah".
- One idea per clip. Word boundaries from the word-level transcript, not segments.
- **Dry run before rendering:** print every clip's first and last 5 words; confirm opener and payoff are whole. The
  last word has been lost three different ways, caught only by the dry run.

## Proven shapes (3+ sightings in `clip_log\INDEX.md`)
Not a checklist: a clip needs a payoff whatever its shape. When a candidate fits one, build it to land the turn.
- **Scene → twist → reaction:** the reaction is the payoff.
- **Escalating riff, capped:** each line tops the last until one caps it. Take the whole build, never its flat tail.
  The scorer misses these most.
- **Absurd image → strong verdict:** "if you make Heat, you should get to kill 20 horses minimum".
- **Friend exposes the other's habit:** one host outs the other; the defence makes it worse. Duo shows run on it.
- **Self-roast of the past self:** delusion then, blunt truth now.
- **Observational take with a quotable capper:** a 7 unless the capper is quotable.
- **Shameless confession, told proudly** (the scorer under-scores these).
- **Strange true fact, explained in one breath:** "people kept stealing our balcony".
- **Plan meets reality:** a naive expectation, then the obvious question or the bad trade.
- **Insider rule revealed, pushed to absurd precision.**
- **Roast in one line:** a ramble or dumb move answered by one dry line. Take enough of what it answers. Missed often.
- **Made-up fact or dodge, caught live:** a bluff called on the spot. This is a payoff, not "a mild answer".
- **Proud reveal, instantly deflated.** · **Self-justifying logic spiral.** · **Behind-the-scenes reveal told
  straight.** · **Steering toward the line everyone's thinking, called out.**

**Build backwards from the payoff:** find the payoff line, then start at the *latest* line that still makes sense
cold. A 45s story often has a 20s clip inside it.

## The three tests (every candidate)
1. **Cold read:** only the clip's text. Does it make sense and land? **A subject never named in the window fails.**
2. **Retell:** one sentence. If you can't, it's too muddy.
3. **Payoff check:** point to the exact payoff line. None → drop it.

## Transcript quality — check before trusting it
- **Hallucinated repeats:** a sentence repeated with every word at one timestamp (15+ words, or repeating what was
  just said) makes the window unusable. 3–8 words at one timestamp is just fast speech.
- **Loops and word salad** sit right beside good clips. Read the clip's own captions.
- **Lowercase, unpunctuated stretches** also lose whole lines, so a "garbled" candidate may be clean in the audio.
  Judge sentences by meaning; **if a transcript comes out lowercase, re-transcribe before picking.** A broken
  transcript costs picks, not just captions.
- **Fake speaker names** written as speech (a name repeated for minutes): grep for them, blank them with fixes.
- **Misheard words:** fix the caption when sure (Cat → Katt Williams); misheard words are fixes, never rejects.
  When unsure about a payoff word, move the boundary rather than post a wrong caption.
- **Dropped curse words** ("who gives a has nothing to do with them"): if the punchline needs it, restore it with a
  fix on the word before (masked `****` anyway). A fix replaces that word everywhere in the clip, so skip it after
  "a"/"the", or put it on the word after when that word appears once.

## Ads and signals
**Ads first:** "promo code", "<brand> dot com slash", "use the code", "free shipping", "let's get back to it",
tour-date lists. The whole read is off-limits for clips, peaks and spikes.
**Heatmap** (yt-dlp `heatmap`, ~100 buckets, 0–1 relative to the video's own peak; often missing): ignore the first
~2 buckets. **A peak right after an ad read is a skip landing, not a replay: discard it.** Real peaks can be low;
rank relatively. A bucket is ~45–80s wide: "something in here", not where to cut. Evenly spaced peaks on ordinary
content may be mid-roll ad breaks **(guess)**.
**Loudness** (`ebur128` vs the episode median; spike ≥ 6 LU **(guess)**): clusters over 10–20s are a hint. Ignore it
on flat mixes, group shows that never go quiet and compressed mixes. Works on streams. Never selects a clip alone.
**The transcript decides.** Clips with no signal are as good as signalled ones. **Always read the whole transcript.**

**Drop on sight:** ads, cold-open teasers (the full moment is later), intros/outros, "subscribe", housekeeping,
rapid-fire Q&A, **third-party footage played on the show** (not theirs to clip), cross-talk captions can't follow
(people talking *over* each other; quick back-and-forth is fine), gestures the viewer can't see, setups whose
payoff is outside the length limit.

## Selection order
0. Check transcript health; mark ad reads off-limits.
1. List real heatmap peaks, if any.
2. Read the full transcript with peaks and loudness marked. Over ~1h: ~15–20 min chunks with ~1 min overlap. **A
   clip wholly inside the overlap minute belongs to the part it sits in.**
3. For each candidate, find the payoff; build backwards to a clean opener; splice before rejecting.
4. Run the three tests.
5. Score every survivor. **Render 8+ only** (Tko: 7s are filler).
6. Mix kinds. No overlaps, no two clips on one sub-topic. Two different stories may sit back to back.
7. **Same story told twice:** keep the bigger payoff, not the first found.
8. **No turn, no clip.** A take or story with no capper is a reject, not a 6.

## How many clips
**At most 20 per video, 30 over 3 hours** (Tko). Under that the episode decides (a dead episode gives 2; two
comedians trading stories ~8–15/hour). Never pad. Over the ceiling: keep the highest, log the rest "over the cap";
code leaves extras unticked and refuses a render with too many ticked. **Same-story dedupe:** keep the best one per
story type.

## Score (1–10, absolute)
Against the bar, not the other clips. **Calibration: the model scores the best clips one point low.** A clean
payoff, a cold opener and no flaw you can name is a 9; 8 is strong with one nameable flaw.
- **10:** would bet on it. **9:** strong on all three tests, one tiny nitpick. **8:** strong payoff, one real flaw
  (weak opener, slight overrun, a risk flag). **7:** good moment, flawed cut. **6:** postable filler.
- **≤7: don't render;** log as rejected with the reason. Score and one-line reason go in the run's `clip_log\` file.

## Post description (one per clip, written with the pick)
Saved as `NN_s<score>_<name>.txt`. Three lines:
1. **Hook** (under ~70 chars): the premise that makes someone stop, never the punchline. **Every fact in it must be
   in the clip.**
2. **Credit:** "From <show> <episode> with <guest>." Always. **Take the show's or streamer's name from the channel
   field when the title lacks it.** Credit only people in the clip.
3. **Hashtags: 10–15 on one line**, ordered by importance: who (show, host, guest) → this clip (2–4 on its subject)
   → theme (#comedy #standup #comedypodcast #podcast #funny…). **Don't write #xybca #fyp #blowthisup #viral: code
   adds them**; posting trims generic tags to stay at 15 (YouTube ignores all hashtags past 15).
No emoji walls, "wait for it" or "you won't believe".
**The post text is clean even when the clip isn't** (Tko): no curse or slur (a masked `****` counts, so does one in
a tag), nothing about sex, porn, nudity or drugs (weed included), even when that's the subject. Sell the situation,
not the word. Alcohol and toilet humor are fine. `review.off_limits` refuses the plain words; allusions are on you.

## Risk flags (mention, don't auto-reject; Tko decides)
- Rumors or accusations about named real people; drug-use rumors about a named celebrity → skip.
- **N-word, race, religion or trans bits: judge like any clip, then flag** (Tko: "if the clip is good I don't care
  if it has the N-word"). Captions mask it.
- **A sexual joke about a child is a reject, not a flag.**

## Render — what the picker and reviewer must do
Layouts: **Podcast** BLUR + TRACK (+ SPLIT when both faces share one shot the whole clip and are big enough);
**Streaming** BLUR + GAME on gameplay, BLUR + TRACK without; **Movie** BAND only. Output:
`Finished_Clips\<Podcast|Streaming|Movies>\<show>\NN_s<score>_<name>_<layout>.mp4`; NN counts up from the clip log.
All framing and captions are code (style C: 1–2 word pop-in captions coloured per speaker, curses masked; TRACK
follows the voice with no shot over 4.5s, Tko's Shorts-editing rule). What GURT does:
- **Faces:** a show filmed as one wide shot has no close-ups, so TRACK parks on one seat. Before approving it, put
  `"seats"` at the top of `review.json`: speaker number → x over the frame's width (`{"0": 0.105, "1": 0.452}`);
  numbers from `speakers.json` on lines whose speaker is certain, positions from one wide frame.
- **Streams:** look at `work\<slug>\facecam.jpg` before approving; fix a wrong box with `"facecam"`.
- **Movies:** `"crop_x"` (0 left, 1 right) pins a fixed BAND crop when the speaker-following fails.
- **Cartoons:** set `"cartoon": true` before approving. The face finder misses non-human faces (Rick), so the
  speaker-following framed whoever stood beside him. With it: the whole picture when characters share a shot, a
  crop only on one alone (Tko's pick, run 22; his favourites 373 and 374 were whole-picture throughout).
- **Look at a frame strip of every rendered TRACK, GAME and BAND file**, not one frame, and read the render line's
  shot count and longest shot. Add slipped curse words to `render.CURSE`.
- Delete `work\<slug>\source.mp4` after rendering.
