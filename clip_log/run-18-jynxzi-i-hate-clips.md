## Run 18 — Jynxzi "I Hate Clips..." (Rainbow Six Siege clip review stream), 46m, 2026-10-07
**Theme:** `streamer` · **Posted:** _(pending)_ · **Layouts:** BLUR + GAME on all 10
**Second stream run, first solo streamer, first under the review budget.** Three blind pickers on Sonnet (rants and
roasts / chat and confessions / signals and gameplay) read `skill.md`, the index and the reading file without seeing
Sonnet's list. GURT grouped by payoff line and built the cuts with a dry run. No editor or skeptic pass; nobody listened.

**Episode read:** one man at a cut-out webcam reviewing Siege clips viewers sent him, rating each out of 10 and
talking to the sender and to chat. There is none of his own gameplay. Sparse: 4,300 words in 46 minutes (1.6/s).
Recurring bits: the viewer "Balls" who sends a clip every day, AI images of him as a fat man, a fan-mail question.
No ads, no heatmap. Loudness: 7 marked lines, all on callouts over a clip ("Close right!"), none on a payoff.

**Transcript:** healthy on the run 16 settings: cased and punctuated all the way, no same-timestamp runs. One repeat
(42:17, "I broke my headset… High fives" ×3–4, a loop or a donation message; not clipped) and one garbled read-aloud
(38:44, a viewer's poem). 1:43 without a word at 21:11–22:54 is him watching. Fixes: "Condom 5" → Copper 5 (326),
"First come today" → clip (322), "Both," → Balls, (330, a guess), "Jinxy," → Jynxzi, (322, 327).
**Camera:** a keyed cut-out bottom-left over the game, no border, so `reframe.cam_box` found nothing. Set by hand:
`"facecam": [0, 540, 720, 540]` (his face was inside it in 89 of 90 sampled frames). His face is 193px wide (up to
443 leaning in), over the 172px limit that told a boxed webcam from a full-screen camera, so `shows_cam` would have
sent every clip to TRACK: the limit now scales with a wide box (`reframe._boxed_face`). The voice labelling split
his one voice into three and left 48% of his words unsure: `"one_voice": true` in `review.json` (new) gives every
caption one colour.

**Clips** (all = blind pickers and Sonnet; n/3 = how many blind pickers had it)
- **322 · 9 · Zero point five, because he tried** (3:34, 24s, all 3/3). "Why not a zero out of ten? You know what,
  because he actually tried." Shape: *scene → twist → reaction*.
- **323 · 8 · Why am I fat in the AI image** (12:21, 26s, 1/3 and Sonnet). "Why am I like 600 pounds in that AI
  image?" / "It's because you have photos hidden?" / "Wait, do I actually?" The image is on screen in the lower
  panel. Shape: *bluff or rant, caught live*.
- **324 · 8 · Shake my booty** (19:56, 17s, 2/3 and Sonnet; recut). "The whole entire clip is you getting an
  impactless frag in a 4v2… Do you want me to shake my booty for that clip? I will." Shape: *roast in one line*.
- **325 · 8 · Half chub, proof** (22:53, 18s, 2/3 and Sonnet; code had dropped Sonnet's at 9.9s). "That would have
  been such a good clip and then you whiffed." / "I'm not showing you guys proof." **Risk:** crude from the first
  second. About 8s in the middle have no words. Shape: *shameless confession*.
- **326 · 8 · Burnt plastic 4** (28:56, 26s, 2/3 and Sonnet; recut). "Copper 5 lobby? I don't even know what rank you
  would call that… burnt plastic 4." Shape: *absurd image → strong verdict*.
- **327 · 9 · Fan mail in the dumpster** (29:44, 18s, 2/3 and Sonnet). "No, we threw it away and we'll be in contact
  with you." / "Do you know how many… we have right now in our dumpster?" **Risk:** a sex toy named in the first 3s.
  Shape: *embarrassing message read back live*.
- **328 · 8 · Throw your Xbox in the ocean** (30:39, 20s, 2/3 and Sonnet; shortened). "I will personally reach
  through my monitor, grab your Xbox, and throw it into the bottom of an ocean." Shape: *energy build, capped*.
- **329 · 9 · Peppa Pig thumbnail** (38:26, 15s, all 3/3). "You're crudely pasting the lowest point of my life, when
  I was bald with no eyebrows… onto a Peppa Pig logo." Shape: *absurd image → strong verdict*.
- **330 · 9 · Your clips get worse every time** (40:02, 18s, 3/3; **Sonnet missed it**). "I mean this with full
  respect. You have been sending me clips for three years. It actually gets worse every time." Shape: *roast in
  one line*.
- **331 · 8 · Are you playing through a Kinect** (44:00, 14s, 2/3 and Sonnet; shortened). "Do you not have a
  headset? Are you playing through a Kinect? How do you not hear Pulse stampeding behind you on a brick staircase?"
  Shape: *escalating riff, capped*.

**Rejected** (GURT)
- *Sonnet, unticked:* rating the clip 3.3 at 45:22 (9.7s, garbled credential line, a curse in the payoff).
- *Blind picks, dropped (one picker each):* meatball / the AI problem 23:33 (same sub-topic as 329) · jam it into a
  dumpster fire 37:02 · breathe on your… you would perish 33:42 (garbled setup).
- *Visual, not checked:* the emote bit 8:42 (a gesture, sexual payoff) · the poem 38:44 (garbled) · "Put the LMG
  down!" 41:03 · the bronze-player impression 9:54.

**Scorer vs GURT** (Sonnet 5.5, `streamer` profile)
- **Sonnet submitted 10; 9 of its moments are in the final 10 (90%), its best run.** Run 12, the first stream, was
  1 of 17. The bar and the profile were the same; this stream is one clear voice making verdicts in words.
- **Recut 5 of the 9:** it ran past the payoff into a second idea on three (booty, burnt plastic, Kinect), kept two
  extra lines on one (Xbox), and one was dropped by code at 9.9s.
- **Missed 1** that all three blind pickers had (330): a dry roast with no loudness and no jargon.
- **Scores:** all 8s but one 9; four finished at 9.
- **Post text was wrong on all 10:** the streamer's name was missing from the credit or spelled "Jinxy", every clip
  was tagged #jinxy or had no name tag, and one hook gave the punchline away. All rewritten.
- Blind pickers: 9, 6 and 10 picks. All 10 final clips were found by two or more of {three pickers, Sonnet}; the
  three found by one picker alone were dropped.

**What went wrong this run**
- **GURT has not listened to any clip.** Least sure: 325 (short, silent middle), 330 (the name "Balls"), 326 ("Copper").
- The app was on older code than the fixes, so the render ran from the command line (`--render`); the app's queue
  still shows this job at "review".
- The in-code TRACK/GAME check promised in the budget is still not written; one image sheet was looked at instead.

**Render check** (GURT looked at one sheet: 6 frames of each GAME file; nobody listened)
- All 10 came out as GAME: camera across the top (about 42% of the frame), the screen under it, captions on the seam,
  one colour throughout. The lower panel is the right 55% of the screen, so his cut-out isn't shown twice and the
  crosshair sits left of centre.
- BLUR files were not looked at this run.

**Lessons**
- `[theme]` A solo streamer rating viewers' clips is all verdicts in words: 10 clips in 46 minutes (13/hour), every
  payoff his own line, nothing needing the viewer's footage.
- `[scorer]` Sonnet is good on a single clear voice (9 of 10), and still runs past the payoff into the next idea.
- `[scorer]` Sonnet's post text gets the creator's name wrong when the title doesn't carry it; it should come from
  the channel field.
- `[universal]` A cut-out webcam has no border and a big face: the box has to be set by hand and the face-size limit
  has to scale with the box.
- `[universal]` One person on the mic comes out of the voice labelling as three voices and half unsure. Set `one_voice`.
- `[workflow]` Budget run: pickers on Sonnet, cuts built once, one image sheet. Agreement between pickers held again.
