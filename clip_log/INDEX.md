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
| 9 | `run-09-bad-friends-338-stavros.md` | Bad Friends Ep 338 (Stavros Halkias) | 69m | 128–146 | first half only; 19 clips (8 Sonnet, 11 GURT); length retry + cut-matching fixed after it |
| 10 | `run-10-this-past-weekend-687-mamdani.md` | This Past Weekend #687 (Zohran Mamdani, NYC mayor) | 77m | 147–159 | politician guest; Sonnet found 11 of GURT's 14 (79%); nothing dropped by code |
| 11 | `run-11-stavvys-world-200-kam-patterson.md` | Stavvy's World #200 (Kam Patterson) | 101m | 160–191 | app on stale code; fake speaker names in transcript; 12 rendered 7s failed recheck; bar raised to 8+ |
| 12 | `run-12-joe-bart-bigfoot.md` | Joe Bart Games "How Hard Is Finding Bigfoot?" (stream, 4 friends) | 65m | 192–193, 211–227 | first `streamer` run; Sonnet submitted 3, GURT found 17; GAME layout; Smart App Control blocked mediapipe |
| 13 | `run-13-we-might-be-drunk-paul-walter-hauser.md` | We Might Be Drunk (Paul Walter Hauser, Alex Moffat) | 77m | 228–247 | first run at the 20-clip cap; Sonnet 14 picks, 12 kept, found 12 of GURT's 25; guest merged with wall portraits (fixed); audio trimming live |
| 14 | `run-14-matt-shane-637-jeremiah-watkins.md` | Matt & Shane Ep 637 (Jeremiah Watkins) | 68m | 248–263 | three comedians, one wide shot; blind picks by three subagents + editor/skeptic pass; Sonnet 15 picks, 10 kept (all recut), found 10 of 16; render killed once (app launched by GURT); first run with clean post text |
| 15 | `run-15-are-you-garbage-joey-diaz.md` | Are You Garbage (Joey Diaz) | 69m | 264–283 | cleanest transcript yet; 41 moments, 30 passed at 8+, first run over the cap (10 logged "over the cap"); Sonnet 23 picks, 15 in the final 20, 5 rejected; multi-camera, no SPLIT |
| 16 | `run-16-matt-shane-542-druski.md` | Matt & Shane Ep 542 (Druski) | 67m | 284–301 | first whole job on style C; transcript lowercase for 44 min, fixed by re-transcribing (conditioning off + style hint); Sonnet 13 picks, 10 kept (all recut), found 10 of 18; one wide shot, TRACK on the wrong person |
| 17 | `run-17-this-past-weekend-661-kiriakou.md` | This Past Weekend #661 (John Kiriakou) | 139m | 302–321 | **not reviewed by GURT**: Tko approved Sonnet's 20 in the app; log written afterwards from `review.json` |
| 18 | `run-18-jynxzi-i-hate-clips.md` | Jynxzi "I Hate Clips..." (stream, solo, Siege clip review) | 46m | 322–331 | second `streamer` run, first on the review budget; Sonnet 10 picks, 9 kept (5 recut), missed 1; cut-out webcam set by hand; `one_voice` |

## Shapes (universal), most seen first
Format: tally · shape · clips (score). Clip numbers match `Finished_Clips\` and the run files.
3+ = proven, listed in `skill.md` Part B "Proven shapes".
- `[..........................]` **Scene → twist → reaction**: the reaction is the payoff · 06 (9), 11 (8), 20 (9), 22 (8), 35 (7), 58 (8), 77 (9), 78 (9), 138 (8), 148 (9), 164 (8), 166 (9), 175 (9), 224 (8), 227 (9), 228 (9), 244 (8), 249 (8), 254 (8), 255 (8), 262 (8), 268 (8), 276 (9), 284 (9), 300 (9), 301 (9)
- `[......................]` **Energy build or outrageous comparison, then a capper that tops it** · 01 (8), 17 (9), 69 (8), 76 (9), 130 (7), 134 (8), 137 (8), 141 (8), 152 (9), 161 (9), 163 (8), 167 (9), 221 (9), 231 (9), 235 (9), 236 (8), 246 (8), 248 (8), 256 (9), 269 (9), 280 (8), 282 (9) (in skill.md)
- `[.................]` **Absurd image → strong verdict** · 10 (8), 56 (8), 70 (8), 126 (9), 136 (8), 140 (7), 143 (8), 147 (7), 153 (8), 157 (9), 171 (9), 189 (9), 223 (8), 233 (8), 251 (8), 259 (8), 278 (9) (in skill.md)
- `[...............]` **Friend exposes the other's habit** · 57 (8), 66 (7), 67 (7), 128 (7), 132 (8), 133 (8), 139 (7), 145 (8), 149 (8), 169 (9), 192 (8), 215 (8), 222 (8), 237 (8), 263 (8)
- `[...............]` **Self-roast of the past self**: delusion then, blunt truth now · 14 (7), 15 (9), 25 (8), 27 (9), 38 (7), 53 (7), 83 (8), 124 (8), 142 (8), 154 (8), 176 (8), 177 (9), 234 (8), 241 (8), 279 (8)
- `[................]` **Observational take with a quotable capper** · 04 (7), 09 (7), 28 (7), 37 (7), 44 (8), 67 (7), 73 (8), 74 (9), 131 (7), 150 (8), 173 (8), 225 (8), 230 (8), 232 (8), 250 (9), 270 (8)
- `[..............]` **Shameless confession, told proudly** · 19 (9), 36 (8), 64 (9), 129 (8), 165 (9), 178 (8), 193 (8), 211 (8), 264 (9), 267 (9), 271 (9), 273 (9), 277 (8), 281 (9)
- `[..........]` **Strange true fact, explained in one breath** · 08 (8), 18 (8), 42 (8), 55 (7), 146 (7), 229 (8), 245 (9), 252 (8), 257 (8), 258 (9)
- `[........]` **Plan meets reality**: naive expectation, then the obvious question or bad trade · 13 (8), 16 (7), 26 (8), 30 (8), 54 (8), 218 (8), 265 (9), 275 (8)
- `[.......]` **Insider rule revealed, pushed to absurd precision** · 07 (9), 29 (8), 80 (8), 123 (8), 190 (9), 243 (8), 272 (9) (in skill.md)
- `[.........]` **Roast in one line**: the guest's single dry reply to the host's ramble · 155 (8), 158 (8), 213 (8), 214 (8), 239 (8), 261 (8), 266 (9), 297 (9), 299 (9) (in skill.md)
- `[......]` **Made-up fact or dodge, caught live** · 48 (8), 95 (8), 182 (9), 219 (8), 287 (9), 298 (8) (in skill.md)
- `[....]` **Behind-the-scenes reveal told straight** · 05 (6), 31 (9), 84 (8), 242 (8)
- `[.....]` **Proud reveal, instantly deflated** · 43 (9), 65 (8), 238 (8), 247 (8), 283 (8)
- `[....]` **Self-justifying logic spiral** · 12 (8), 32 (7), 240 (8), 253 (9)
- `[..]` **Confession in the first sentence** · 02 (8), 33 (9)
- `[..]` **Parent collides with the joke** · 21 (7), 61 (8)
- `[..]` **Prank or bit backfires** · 60 (7), 63 (7)
- `[..]` **List game with a guest who never breaks** · 50 (8), 144 (8)
- `[...]` **Steering toward the line everyone's thinking, called out** · 40 (7), 226 (8), 260 (8)
- `[.]` **Unbreakable loyalty, broken in one question** · 52 (9)
- `[.]` **A con, and the mark finds out** · 127 (9)
- `[.]` **Ironic PSA: "don't do it" while describing exactly how** · 135 (7)
- `[.]` **Embarrassing message read back live** · 59 (8)
- `[..]` **A con presented as advice** · 47 (8), 274 (8)
- `[.]` **Absurd escalation of a crush** · 45 (8)
- `[.]` **Crude image, then someone finds the silver lining** · 41 (8)
- `[.]` **Code of honor stated backwards** · 49 (7)
- `[.]` **Roast of a third party's look** · 46 (7)
- `[.]` **One-line policy, stated proudly** · 34 (8)
- `[.]` **Parent's proud setup, kid's absurd reality** · 39 (7)
- `[.]` **Backup plan justified by one absurd story** · 23 (8)
- `[.]` **Old doubters witness the success** · 24 (7)
- `[.]` **Vivid description → takeaway** · 03 (6)
- `[.]` **Calm, then the jump scare**: the payoff is on screen and in the scream, not the words (stream) · 212 (8)
- `[.]` **Absurd theory, and one of the group takes the credit** (Bigfoot is scared of women) · 217 (8)
- `[.]` **Tense guess, mundane reveal** ("grizzly bear" → "that was my tummy") · 216 (8)
- `[.]` **Callback that turns the group into the earlier villain** · 220 (8)

Read so far: story shapes with a clear turn score 8–9; takes score 7 unless the capper is
quotable. Duo shows (Shane/Steve) run on "friend exposes the other"; one-guest shows on self-roast.

## Recurring lessons, most seen first
- `[..........]` `[universal]` Clips with zero signal support are as good as signalled ones (runs 1–10). (in skill.md)
- `[............]` `[universal]` Whisper drops to lowercase with no punctuation (runs 2–4, 6–10). (in skill.md) Run 12: 47% of the lines. Run 13: 41:55–53:35. Run 14: most of the episode. Run 16: 0:00–44:09, with whole lines lost. **Fix found (run 16, one episode):** `condition_on_previous_text=False` plus a cased, punctuated style hint (`hotwords`): cased all the way, 234 curses instead of 104, no loops. In `transcribe.py`.
- `[............]` `[scorer]` Model scores the best clips one point low (runs 3–10, every run). Calibration added after run 9; run 10 still low (two 9s given 7–8). (in skill.md) Run 12 (first stream): with 7 = reject it submitted 3 clips; GURT found 17, and Sonnet's reject list named 7 of them as "a 7". Run 13: six strong one-liners it named were rejected as 7s or "light banter"; GURT kept all six. Run 15: of the 10 final 9s it had, 9 were 8s on its list. Run 16: 12 of its 13 were 8s; eight of the ten kept finished at 9.
- `[.........]` `[scorer]` Model gives no-payoff, sincere or promotional talk a 6–7 instead of rejecting it (runs 3–10). Run 9: 16 picks, 4 weak; run 10: 13 picks, 2 weak, every policy segment rejected. **Biting.** Run 11: 12 of 25 picks were 7s, all failed recheck; **bar raised to 8+** (Tko). (in skill.md) **Run 13: gone.** 14 picks, every one a real payoff, with the 8+ bar.
- `[.......]` `[universal]` The best version of a story needs more than 35s (runs 1–7). **Fixed after run 7: splicing** (`splice.py`; crematorium 77s → 32s). (in skill.md)
- `[.....]` `[universal]` The dry run of first/last 5 words catches cut-off words (runs 2–6). (in skill.md)
- `[.......]` `[universal]` Heatmap peaks right after ad reads are skip landings (runs 1, 3, 5, 6, 7). (in skill.md) Run 14: the 1.00 peak and a 0.70. Run 15: the 1.00, a 0.52 and a 0.42.
- `[.....]` `[universal]` GURT missed clips the model found (runs 3–7, 9: 130, 140). Blind-pick, then diff, then accept finds after reading them. (in CONTEXT.md recipe)
- `[.......]` `[universal]` The first framing try was wrong: center crop, mediapipe, tiny-face SPLIT, poster faces. Look at frames before rendering. Run 11: a pillow boxed as a face; SPLIT now needs landmarks. (in skill.md) Run 12: the webcam box from one dark clip was a shelf edge; it's found per video now. Run 13: the guest merged with the portraits on the wall beside him; grouping is 2D now and still pictures are dropped.
- `[....]` `[universal]` A story fails the cold read when its subject is never named in the window (Post Malone, 16, 32, Sexy Red). (in skill.md)
- `[.....]` `[universal]` Whisper drops curse words entirely ("shut the up", "I don't give a no", "who gives a has"); restore them with a caption fix when the punchline needs it (runs 7–9). A fix replaces a word everywhere in the clip, so a dropped word after "a" can't be restored that way. (in skill.md) Run 12 too. Run 14: most of them, several on payoff lines; a curse after "the" can go on the word after it when that word appears once ("would" → "**** would").
- `[...]` `[scorer]` Model's splices are sensible but often still run over 40s (runs 7–9: 10 finds dropped by code) and can drop the ending (run 8: Gronk). **Fixed after run 9:** the measured length goes back to it once and it splices harder; leftovers show in Review unticked. (in skill.md, in code)
- `[...]` `[theme]` A non-comedian guest is gold when the hosts poke at their world (rancher, Arenas, Roll Tide Willie). (in skill.md)
- `[...]` `[universal]` Fix misheard words in captions when sure (Katt, Tide man, balls, Xu, click-to-cancel); cut around them when not. (in skill.md)
- `[......]` `[universal]` Whisper hallucinations (repeat loops, word salad) sit next to good clips (runs 5, 6, 10: "Yeah" ×20 a few seconds before 148). Check the window's own captions. (in skill.md) Run 12: "A," ×100 at 46:59. Run 13: 42:47 and 53:30. Run 14: six loops; one sat on a clip's opener (rejected).
- `[...]` `[scorer]` Model picks the weaker version of a repeated story, or a different window of it (runs 3–5, 10: Barramundi over queefish). (selection rule 7 in skill.md; needs to reach the prompt harder)
- `[....]` `[scorer]` Model misses escalating riffs and takes a story's flat tail (run 7: 69, 76, 84; run 9: green room payoff alone, unfuckables). Shape promoted after run 9. (in skill.md) Run 14: ran 10–18s past the payoff on three of ten kept picks; missed the bad-apples riff. **3 sightings: promote.** Run 15: past the payoff on three kept picks and one over the cap (in skill.md).
- `[...]` `[universal]` Loudness is useless on group or compressed shows (run 4: 21% spiked; run 6: 0 spikes). (in skill.md) **Not on streams:** run 12, 14 of 19 clips on a spike; the first attack is the loudest stretch of the video (+21), the second peaks at +12. Run 15: 161 of 253 lines marked.
- `[..]` `[scorer]` Model scores race/N-word/religion bits on the payoff (runs 5, 6). Correct per Tko; it should still add a risk flag.
- `[..]` `[scorer]` Model and "build backwards from the payoff": wrong on run 4 (30, 35), right on run 6 (59) where GURT wasn't.
- `[...]` `[theme]` Two comedians ≈ 8 clips/hour (run 3); runs 4–6 ran 8–9/hour. Run 9 (three comedians, a costume birthday) ran 16/hour. Run 10 (comedian + politician) ran 10/hour, all from tangents. Run 14 (three comedians, no topic) ran 14/hour.
- `[...]` `[workflow]` Restart the app after code changes (run 7); a process keeps the API key it launched with, so it's now read fresh (run 8). Run 11: the app ran 10/1 code through runs 10–11; check the process start time. Run 14: a render inside an app GURT launched from its own shell was killed mid-file (ffmpeg `0xC000013A`). **Tko starts the app.**
- `[.]` `[universal]` Whisper's word end times aren't where the sound stops; endings are cut from the audio now (run 7). (in skill.md)
- `[..]` `[workflow]` Blind picks by three independent subagents, then an editor and a skeptic per moment (run 14). 16 of 20 moments found by two or more pickers survived; 0 of 3 found by one. Merge candidates by payoff line, not by overlapping time: an overlap merge hid the COVID-opener clip behind Prince Eric. Run 15: 29 of 32 moments found by two or more blind pickers passed at 8+; 1 of 5 found by one. Run 16: 17 of 21 against 1 of 5.
- `[.]` `[workflow]` GURT's wait loop for the render never matched the failed state and hid a dead render for two hours (run 14). Test the loop against failure first.
- `[.]` `[scorer]` Model picks third-party footage played on the show: a film clip and a whole interview video (run 13, its second 9). No movie clips; not theirs to clip.
- `[.]` `[scorer]` The overlap-minute instruction made it skip a clip that sat wholly inside the overlap (run 13: Katt Williams at 39:31).
- `[.]` `[theme]` Hosts workshopping new bits out loud is a clip farm: 7 of 20 clips from 10 minutes (run 13).
- `[..]` `[workflow]` The 20-clip cap left out 5 clips GURT had at 8 on its first run (run 13). Logged as "over the cap". Run 15: 30 passed, 10 over the cap; three judges on different lenses ranked them, nine of the ten dropped were the weaker of two on one sub-topic.
- `[.]` `[scorer]` Model rejects on transcript quality (run 12: the GTA RP janitor, "a 7: the transcript is garbled"; "are peeing" = RPing is one caption fix). Misheard words are fixes, not rejects.
- `[.]` `[scorer]` Model over-applies "needs the stream's history" to any callback (run 12: weeb line, pee story, both stood alone; the flare roast was "needs the game state").
- `[.]` `[theme]` A friend-group stream is a podcast with a game on screen: 16 of 19 clips were voice-chat banter (run 12).
- `[.]` `[workflow]` "Visual, check the frame" works: the scorer put both Bigfoot attacks in `rejected` with that note, GURT looked at a contact sheet, both are clips (run 12).
- `[.]` `[universal]` Gamer vocabulary is misheard constantly (RPing, mag dump, res, incel, flares): 1–3 caption fixes per stream clip (run 12).
- `[.]` `[workflow]` Windows Smart App Control blocked `libmediapipe.dll` mid-render (run 12). Streams no longer need it; podcast TRACK/SPLIT still do.
- `[.]` `[scorer]` Model rejects a payoff whose setup is minutes earlier, or clips the payoff alone (run 9: green room, freezer). Splice setup + payoff; span raised to 4 min. (in skill.md, in code)
- `[.]` `[scorer]` Chunk boundaries cut off stories that cross them (run 11: hide and seek, compression shirt). Fixed: parts overlap both sides. (in code)
- `[.]` `[universal]` Whisper wrote fake speaker names ("Rob Markman") as spoken words for 43 minutes (run 11). Grep for repeated names; blank them with caption fixes.
- `[.]` `[workflow]` GURT waved the scorer's 7s through without the three tests (run 11). Every pick gets checked.
- `[..]` `[scorer]` Model misses the guest's one-line dry burn after the host's ramble (run 10: queefish, right at home). Run 15: it missed the hosts' own lines when the guest is the star (266, 273).
- `[.]` `[theme]` A politician guest is mostly off-theme; clips come from the host's tangents and the guest playing straight man (run 10).
- `[.]` `[workflow]` Review window shows the copy loaded on click; GURT's chat edits appear only after clicking the episode again (run 10).
- `[.]` `[scorer]` Model calls quick back-and-forth "cross-talk" and rejects it (run 9: flock cameras, unfuckables). (in skill.md)
- `[.]` `[workflow]` Code lost the model's finds after it did its job: a 2-word cut quote matched the wrong "yeah" (run 9). Fixed: one miss allowed only in 4+ word quotes; a cut's end is searched after its start.
- `[.]` `[universal]` Poster faces at a third of the real face's size pass the size filter, but TRACK stays on the talker (run 9).
- `[.]` `[scorer]` Model under-scores "confession of incompetence told proudly" (run 6, 64: 6 vs 9).
- `[.]` `[scorer]` Small model loses the second half of a long episode; send it in pieces (run 3, Haiku).
- `[.]` `[universal]` Never clip a cold-open teaser (run 4). (in skill.md)
- `[.]` `[universal]` Caption the exact dry-run words, not words selected by time (run 4). Fixed in code.
- `[.]` `[universal]` Best story lost to transcript garbage (run 6, SNL firing). Idea: re-transcribe one stretch.
- `[.]` `[universal]` Evenly spaced heatmap peaks may be YouTube mid-roll breaks (run 3, guess).
- `[.]` `[theme]` N-word/race bits: GURT skipped them in run 5; Tko overruled: judge on the payoff, flag the risk. (in skill.md)
- `[.]` `[theme]` A guest walking in mid-episode is a clip farm; every question is a setup (run 5, Willie).
- `[.]` `[theme]` A guest plugging their own product is an ad in disguise; drop it (run 8). (in skill.md)
- `[.]` `[theme]` Athlete storytellers fit the comedian profile when the guest tells stories deadpan (run 4).
- `[.]` `[scorer]` Model clipped a payoff that is a sexual joke about the guest's 13-year-old and only flagged the risk (run 15). GURT ruled it out; without the line the clip is a 7. A joke like that about a child is a reject, not a flag.
- `[.]` `[scorer]` On a clean transcript with one dominant storyteller the model is good: 18 of 23 picks passed at 8+, 15 of the final 20 (run 15, Joey Diaz).
- `[.]` `[theme]` One legendary storyteller guest: 30 moments at 8+ in 69 minutes, 26/hour before the cap (run 15).
- `[.]` `[workflow]` A hook written by a subagent claimed a detail the transcript doesn't have ("8 a.m. game", run 15). Check each hook's facts against the clip.
- `[.]` `[universal]` TRACK sat on a laughing listener instead of the storyteller in 17 of 20 clips (run 15: three-person wide shot, mic over the talker's mouth). BLUR was fine. Check a frame strip of every render. Run 16 (style C, voice-following): a show with one wide shot and no close-ups has no faces to learn, falls back to jaw movement and parks on the middle seat.
- `[.]` `[scorer]` Model rejects a dodge caught live and a one-question roast as "no payoff" / "a mild answer" (run 16: 287, 299; both 9s for all three blind pickers).
- `[.]` `[scorer]` Three of the model's rejections were "garbled" clips that are clean on a good transcript (run 16: 286, 292, 297). A broken transcript costs picks, not just captions.
- `[..]` `[scorer]` Model's credit line drops the show's name when the video title has none (run 16: "From Ep 542 - Indulgences with Druski."). Run 18: no streamer name or "Jinxy", and #jinxy tags, on all 10. The name is in the channel field.
- `[.]` `[scorer]` On a solo streamer who delivers verdicts in words the model is good: 9 of 10 picks kept (run 18), against 1 of 17 on a four-friend stream (run 12). It still ran past the payoff on four.
- `[.]` `[universal]` A cut-out webcam (no border, big face) isn't found by `cam_box` and failed the face-size test for a boxed webcam (run 18). Set `facecam` by hand; the limit now scales with a wide box.
- `[.]` `[universal]` One person on the mic is labelled as three voices with half the words unsure (run 18). Set `one_voice` in `review.json`.
- `[.]` `[theme]` A solo streamer rating viewers' clips: 13 clips/hour, every payoff his own line (run 18).
- `[.]` `[universal]` Whisper's spaced tokens ("10 -year -old", "$3 ,000") and zero-length caption events reach the screen (run 15). Join and clamp them in code.
