# ClipMiner

> Kind: `scripts`

## Goal
`clipminer <url-or-file>` turns a long comedian podcast or a stream into every clip worth posting
(variable count, scored 1–10), each 10–35s, 9:16, burned-in captions, in the layouts its type calls
for, with a one-line reason per clip. Tko picks the type (Podcast / Streaming) before pasting the link. Scoring moves from GURT-by-hand → Claude API → small local model.

## Constraints
- Language: Python 3.12
- Where it runs: manual, Windows, RTX 2080 Super (local Whisper on GPU)
- Deps: ffmpeg (winget), yt-dlp, faster-whisper, av (pinned), CUDA libs, mediapipe +
  opencv-contrib (layouts), `sherpa-onnx` (who is talking; Tko's yes 2026-10-06), `anthropic` (score),
  `playwright` (fills upload pages; drives installed Chrome). Model files live in `models\`, fonts in `fonts\`.
- **Downloads stay at 1080p** (Tko, 2026-10-06: "1080p is fine for shorts"). Don't raise `download.py`'s cap.
  Confirm before adding more.
- Inputs / outputs: YouTube URL or local file → `Finished_Clips\NN_<name>.mp4`
- Failure mode — each stage caches to `work/<slug>/`; a crash resumes, not restarts
- **Delete `work/<slug>/source.mp4` once the clips are rendered.** Tko's rule: no full videos kept.
  Keep the small text files (transcript, info, loudness); the `clip_log\` run files refer to them.
  Re-cutting a clip later means re-downloading.
- **Two video types** (`review.KINDS`, picked in the Queue dropdown or `--kind`; stored as `kind` on the
  job and in `review.json`): `podcast` → theme `comedian-podcast`, `stream` → theme `streamer` (added
  2026-10-04, all guesses until runs are logged). The type sets the theme profile the scorer uses, the
  layouts, and the clips folder. A new type = one line in `KINDS` + a profile in `skill.md` Part A.
  Posting: the app fills the upload page, Tko clicks Post (never auto-publish). No movie clips (copyright).
- **Stream layouts:** a gameplay clip renders BLUR + GAME (webcam on top, game under it, switching to a
  full-height crop on the face for shots where the editor cuts to the camera full screen); a clip with no gameplay
  renders BLUR + TRACK on the streamer. Decided per clip. The webcam box is found once per
  video; **GURT looks at `work\<slug>\facecam.jpg` before approving** and overrides a wrong box with
  `"facecam": [x, y, w, h]` in `review.json`. The scorer only reads the transcript: it can't see the game.
- **Clips folder:** `Finished_Clips\<Podcast|Streaming>\<show>\NN_s<score>_<name>_<layout>.mp4` (+ `.txt`).
  Show folders from before 2026-10-04 sit straight under `Finished_Clips\`; the app lists them under
  Podcast where they are (Tko may move them into `Podcast\`; nothing depends on the path).
  The app groups clips by type, then show, best score first, and tracks where each was posted in `posts.json`
  (asked when the posting browser closes, or "Mark posted"). `Used-Clips\` is optional now. **GURT never deletes,
  renames or moves anything in `Used-Clips\`, and never deletes finished clips.** Tko owns
  cleanup.
- **Clip limit (Tko, 2026-10-04): at most 20 clips per video, 30 for a video over 3 hours** (`review.clip_cap`).
  The scorer's extras land in Review unticked; the Review page refuses an approval over the limit, and a render
  with more than the limit ticked fails with a message. GURT's own picks count toward it.
- **Under the limit, clip count is variable** (quality decides, not a number). Every clip gets a 1–10 absolute
  score (rubric in `skill.md`); only 8+ are rendered (Tko, run 11). Videos over 1h are read in chunks.
- Run 1 (clips 01–05) stays BLUR-only. Tko decided not to re-render it.
- **Captions never show a curse word** (masked `****`; audio untouched). Clips 01–67 predate the rule
  and were deleted by Tko as test runs (2026-09-30); their reasoning stays in `clip_log\`. Clip numbers
  keep counting from the log (`review.next_number`), so new clips start at 68 even with an empty folder.
- **Post text is clean even when the clip isn't** (Tko, 2026-10-04): no curse word (masked or inside a hashtag)
  and nothing about sex, porn or drugs in the hook or hashtags. Rule in `skill.md` "Post description";
  `review.off_limits` refuses an approval, a render or a post with the plain words. Alcohol and toilet humor are
  allowed (GURT's reading, Tko hasn't ruled). File names are not covered.
- **Layouts per type:** Podcast = BLUR + TRACK, + SPLIT when both faces share the shot; Streaming = BLUR + GAME
  on gameplay clips, BLUR + TRACK when there is no gameplay. Tko posts the variants across platforms;
  performance decides which to keep.
- **No automatic judgment database.** GURT keeps the guidance by hand, and owns both files:
  `skill.md` = the rulebook, read in full every run (keep it tight).
  `clip_log\` = worked examples, one file per run (kept + rejected, with why), plus
  `clip_log\INDEX.md`: one line per run and every shape/lesson with a tally (`[...]`, one
  period per sighting; 3+ gets promoted into `skill.md`). Sessions read the index, never the
  whole log; code will pull 3–5 matching examples into prompts. **Commit after every run**:
  GitHub is the backup, the files stay where models can read them. This is what lets the API
  model, and later a small local model, pick like GURT does.
- Scorer roadmap: GURT by hand (now, building context) → Claude API → small local model.

## Pipeline
1. `download` — yt-dlp video + info JSON; keep `heatmap` ("Most replayed") when present
2. `transcribe` — faster-whisper, word-level timestamps
3. `signals` — loudness per second (ebur128) done; ad detection, heatmap peak filter next
4. `score` — picks clips by `skill.md` rules. Run 1 was judged by GURT by hand.
5. `render` — ffmpeg cut, burned word-timed captions coloured per speaker, layout BLUR / SPLIT / TRACK.
   First: `speakers.py` labels every word with its speaker from the audio (`speakers.json`, about 4 min per
   episode, once) and `reframe.known_faces` learns each voice's face from close-ups (`faces.json`, about 1 min).
   (`reframe.py`: YuNet face detection, SFace to match faces to voices, mediapipe jawOpen as the fallback;
   model files in `models\`)

`skill.md` is the source of truth for how clips get picked. Update it after every run.

## How a run is done now
**GUI:** `.\.venv\Scripts\python.exe -m clipminer.gui` (from `Projects\ClipMiner`). Paste URLs → the worker runs
download → transcribe → signals → score (Sonnet) one job at a time → stage **review**. Approve in the Review
window (double-click a row to drop it), or from chat. Approved jobs render, write the `.txt` post
descriptions, and delete `source.mp4`. `queue.json` / `profiles.json` are local (gitignored).
**CLI:** `python -m clipminer <url>` (or no URL = `queue.txt`) stops at review; `python -m clipminer --render <slug>`.
**GURT's part (teaching loop, Tko's rule):** before approving, GURT reads the transcript and picks blind, then
diffs against `review.json` (`by: sonnet` vs `by: gurt`), adds/edits clips with `review.entry(words, name, score,
first, last, "gurt", payoff, reason, fixes, description)` (word indices; `fixes` corrects misheard caption words),
sets `keep`, saves, sets `status: approved`. Logs the diff in the run file's "Scorer vs GURT", updates INDEX,
commits. Transcript health check and face check (look at frames) still come first.
Next clip number: **302** (counted from the logs automatically: write a run's log after it renders).

## Status
- [x] ffmpeg installed, `download` + `transcribe` produce a word-timed transcript
- [x] Run 1 end-to-end on Wild Ride #222 (73.5 min): 5 clips in `Finished_Clips\`
- [x] `render` 1080x1920 clips with captions
- [x] Tko reviewed run 1: all 5 kept. Reasoning in `clip_log\run-01-wild-ride-222.md`
- [x] 3 hand-judged runs on different shows (Wild Ride, Matt & Shane, JRE). Runs 1–2 all kept.
- [x] SPLIT + TRACK layouts ported from openshorts; 06–10 rendered in all three layouts
- [x] `skill.md` split into theme profile (A) + universal rules (B); log patterns tagged
- [ ] Tko posts variants; performance per layout/platform goes into each run file's "Posted" line
- [x] Run 3: JRE #2187 Sandler (2h17m) → 18 clips (11–28), BLUR + TRACK; SPLIT n/a
      (multi-camera). TRACK now shot-aware (ffmpeg scdet). Tko: spot-checked, all good.
- [x] `queue.txt`: batch download + transcribe + loudness, so episodes are ready to judge
- [x] Whisper's lowercase stretches: `transcribe.py` now runs with `condition_on_previous_text=False` and a cased,
      punctuated style hint (`hotwords`). Run 16, same audio: cased all the way, 234 curse words instead of 104, no
      loops, 6 min instead of 12. **One episode behind it**: check the next run's transcript before trusting it.
- [x] Splicing (`splice.py`): story cuts from review (`cuts`, Sonnet proposes them), dead air shortened only where the audio is quiet (2026-10-04; not on
      transcript gaps, no kept stretch under 1s; **untested on a podcast**, check run 13's cuts by ear),
      endings cut from the audio. Tested on run 7's crematorium story (77s → 32s)
- [x] Transcribe speed: 67 min in about 6 min with the run 16 settings (was 12; run 2 took 634s for 76 min).
- [ ] `signals` ad detection + heatmap ad-skip filter in code
- [x] `score.py` (Claude API): 20-min pieces, structured output, length/dedupe in code. Run 3:
      Haiku 4.5 found 9/18 (too small); Sonnet 5.5 found 16/18. Sonnet is the scorer.
- [x] `review.py`: review gate (`review.json`), dry-run preview, render with exact caption words,
      curse masking, per-clip `.txt` post description; numbering continues across Used-Clips
- [x] GUI (`gui.py`) per GUI_SPEC with a review stage. Runs 7 and 8 went through it end to end
- [x] Account `Comedian-House-TV` set up; posting works on YouTube + TikTok (4 clips, 2026-09-30 → 10-01)
- [ ] Facebook posting (added 2026-10-04: Accounts slot + `post.facebook`, opens the Reels composer). **Never run
      against the real page**: the button names are from memory. First post: watch where it stops and fix the selectors.
      It posts as whichever profile or Page that browser is switched to.
- [x] Second batches: picks added after a render render on their own (`--render <slug>` or the app);
      the source is re-downloaded. API key read fresh from the registry (`score.api_key`)
- [ ] Sonnet matches GURT's blind picks on new shows (GURT keeps logging the diffs)
      Run 4 (Arenas): agreed on 5 of 10; Sonnet found 2 GURT missed; Tko kept all 11.
      Run 5 (Theo Von): agreed 6 of 10, 3 finds kept. Run 6 (Flagrant): agreed 7 of 10, 5 finds kept.
      Run 9 (Bad Friends): found 9 of GURT's 18 (+2 lost in code, now fixed); 16 picks, only 4 weak.
      Run 10 (Theo/Mamdani): found 11 of GURT's 14 (79%); 13 picks, 2 weak. Missed the guest's dry one-liners.
      Run 11 (Stavvy's World): found 15 of GURT's 22 (68%, 5 lost to length on stale code, 3 lost at chunk
      boundaries); 12 of its 25 were 7s, all failed recheck. Bar raised to 8+.
      Run 13 (We Might Be Drunk): 14 picks, 12 kept, no filler; found 12 of GURT's 25 (48%). 2 picks were played footage.
      Run 14 (Matt & Shane 637): 15 picks, 10 kept and all 10 recut; found 10 of 16 (63%); its 3 solo picks failed.
      Run 15 (Are You Garbage / Joey Diaz): 23 picks, 18 passed at 8+; found 15 of the final 20 (75%); 12 of the 15 recut.
      Run 16 (Matt & Shane 542 / Druski): 13 picks on a broken transcript, 10 kept and all 10 recut; found 10 of 18 (56%).
- [ ] One local file (no heatmap) end-to-end
- [x] Streaming type: Queue dropdown, `streamer` theme, GAME layout, type folders, Clips tree by type.
      Run 12 (Joe Bart Games `VxPBaAT13gk`) went through it: 19 clips: 18 BLUR + GAME, 193 BLUR + TRACK
- [ ] Sonnet matches GURT on streams. Run 12: found 1 of GURT's 17; it rated 7 of the other 16 a 7, and a 7 is a reject.
- [ ] First 3 stream runs logged (1 of 3) (`**Theme:** \`streamer\`` in the run file) so the profile stops being guesses

**Cost plan (Tko 2026-09-30: fine for now, must get cheaper as it scales).** Today ~$1–1.50 per 2h
episode, mostly Sonnet's output (~9k tokens per 20-min piece, flat across runs; logs don't shrink it).
In order: (1) Message Batches API for queued episodes, −50% on everything, no quality risk; (2) lower
reasoning effort once Sonnet matches GURT's blind picks, tested against them; (3) drop the rejects list
from the output once it stops teaching; (4) cut ads/intro/outro from the transcript sent; (5) local model.
Prompt caching is already on (~90k cached input tokens saved per episode).

**Later (not v1):** gameplay/visual signals · local model · app/agent wrapper.

**Reference:** github.com/mutonby/openshorts (MIT). Worth taking: SPLIT layout (two speakers
stacked, captions on the seam; mediapipe), PySceneDetect to avoid cutting across shot changes,
LLM via OpenAI-compatible `base_url` so the local-model swap is config. Not taking: Docker, S3,
fal.ai/ElevenLabs, FastAPI dashboard. Their picker is transcript-only (no heatmap, no ad filter).

**Gotchas:**
- `av` pinned to 18.1.0: av 19 removed `metadata_errors`, which faster-whisper 1.2.1 still passes.
- yt-dlp warns it has no JS runtime (deno). Downloads work; install deno only if formats go missing.
- Heatmap peaks after ad reads are skip landings, not replays (see `skill.md`).
- Run: `.\.venv\Scripts\python.exe -m clipminer [<url-or-file>]` (download + transcribe + loudness;
  the rest is the manual recipe above)

## Next step
Left off 2026-10-07 after run 16 (Matt & Shane Ep 542 / Druski, 18 clips: 284–301, BLUR + TRACK, in
`Finished_Clips\Podcast\Matt and Shane's Secret Podcast`): the first whole job through the app on style C.
**What it showed:** captions and speaker colours work (one colour per voice, same voice across clips, masked curses,
no spaced tokens). **TRACK does not on this show**: one wide shot, no close-ups, so no faces were learned
(`faces.json` is empty) and the crop parked on the middle seat.
**Fixed the same day with seats** (Tko, 2026-10-07: "most the tracking clips don't track the correct person"):
`"seats"` in `review.json` maps each speaker number to where that voice sits (`reframe._seated`; how to fill it is
in `skill.md` "Render"). Run 16's are set: 0 Druski 0.105, 1 Shane 0.452, 2 Matt 0.863. Tested through the real
render code on four clips: the framed person matches the caption colour throughout. **GURT fills `seats` before
approving any show with no close-ups; this needs an app restart to take effect in the app.**
**All 18 `_track.mp4` files of run 16 were replaced with seated renders under the same numbers** (Tko's yes,
2026-10-07). 17 match the caption colour in every sampled frame; **297 opens with about 6s on Matt while Druski
talks** (those lines are mislabelled by `speakers.label`, so the caption colour is wrong there too): post 297 as
BLUR, or fix the labels and re-render it. Nobody has listened to them.
Also still to ask Tko: the white "unsure" lines (he has now a real run to look at), and run 15's TRACK re-render.
**Restart the app before the next job**: it is still running the old `transcribe.py`.
**Tko starts the app himself** (`.\.venv\Scripts\python.exe -m clipminer.gui`): a render inside an app GURT launched
from its own shell was killed mid-file (run 14). If GURT must render, use `--render <slug>` as a background task.

**Style C is built (2026-10-06), Tko's pick from six samples** (`Finished_Clips\_style_tests\`, sample C). Why:
YouTube's Shorts recommendation change (announced 2026-10-01: channels that mostly re-upload others' videos
without significant changes get less reach) and what other clip channels now post. Reference shorts:
`7nz19kyX164`, `mTJXBdaj8tk`, `nJsK00XAoz0`. What changed, all in code (`render.py`, `reframe.py`, `review.py`,
`fonts\`); the rule text is in `skill.md` "Render":
- **Captions, every layout:** Lilita One, 1-2 words, pop-in, gone in pauses. Run 15's caption bugs are fixed with
  it (split tokens like "10 -year -old", lines that never showed or sat on top of each other).
- **TRACK:** crop sized to the face, punch-in mid-hold and on the payoff, slow push-in, captions mid-frame.
- **Who is talking, from the audio** (same day, after Tko's yes to `sherpa-onnx`): captions are coloured per
  speaker and a wide shot follows the voice instead of jaw movement. How it works is in `skill.md` "Render".
- Tested through the real render code on two shows (Theo Von / Saban, and run 15's Joey Diaz episode: clips
  264-267, 273, 278, 281, 283), plus two throwaway picks through `review.render_approved` end to end. Two
  reviewer passes confirmed 35 defects; all fixed except the two listed under "Still open". On seven test clips
  the crop was on the wrong person for 0-3s each (was most of the clip). **Not yet run through the app on a
  whole job, and SPLIT, GAME and a stream were not rendered in the tests. Tko has seen sample C from the test
  script, not a render from this code. Nobody has listened to a test clip.** The next real run is the first.
- **Restart the app** before the next job, and expect the first render of a video to sit for about 5 minutes
  on `[speakers]` and `[faces]` before the first clip.

**Still open on style C**
1. **Run 15's TRACK files are still the old wrong ones.** A re-render would now follow Joey (tested on eight of
   its clips) but re-rendering 20 posted-or-postable files is Tko's call: it means deleting `rendered_as` in
   `work\oMjBYQCHMrk\review.json` and the new files take new numbers (284+). Until then post the BLUR files.
2. **Unsure lines are white**, so one speaker's captions can flip to white for a line (a last line under
   laughter, a short "Did you?"). Filling them in would paint real interjections in the wrong colour. Tko hasn't
   seen it yet; ask after the first real run.
3. **Hosts who never get a close-up** are matched by jaw movement among whoever is left over. Right on the test
   clips; **wrong on run 16**, where nobody gets a close-up (see Next step).
4. Labelling was tuned on two episodes. Unknown: a show with two similar voices, four or more people, music
   under speech, a stream (game audio may get its own colour).
5. **On-screen joke caption:** Tko's idea, in samples E and F, not in C. Not built.
6. `half-assed` and other compounds not in `render.CURSE` show unmasked (already so before style C).
7. The app shows one "render" stage for the whole job; the new first-render wait has no stage of its own.

**Tko's queue, newest first, then oldest first. GURT has listened to nothing; these need ears.**
00. **Run 16 clips (284–301).** "Listen:" notes are in each reason in `work\ByDpG7QzNTQ\review.json`. Most uncertain:
   286 (brand captioned "Karhus" is a guess), 290 (four cuts), 289 (ending), 285 and 288 (three cuts each), 297.
   Risk calls: 296 (opens on "Did you ever meet Diddy?", aimed at Druski), 288 (the N-word is audible), 290 (MLK
   voice), 284 (religion), 297 (race), 299 and 300 ("midget"), 292 (LA fire victims). No second reader checked this
   run: the editor and skeptic passes were skipped. "Good night to a guy" sits unticked in Review as a swap for 294.
0. **Run 15 clips (264–283).** Each clip's "Listen:" note is in its reason in `work\oMjBYQCHMrk
eview.json`; the
   short list is in the run file under "What went wrong". Most uncertain: 275 (six cuts), 279 ("hit a valve"), 265,
   267, 281, 283. Risk calls: 279 and 281 (crude sex lines), 282 (insults Elon Musk), 268 and 271 (drug use is the
   subject). **Ten more passed at 8 and sit unticked in Review** (over the cap): tick one only by unticking another;
   two of them (Brooklyn guy, Szechuan beef) need a recut first. Sonnet's daughter clip is rejected: its payoff is a
   sexual joke about his 13-year-old (GURT's call; overrule it if you disagree).
1. **Run 14 clips (248–263).** Guessed captions: "in Austin" (249), "Husky of a mustache" (251). Endings: 257 (last
   word missing from the transcript), 261. Splice seams: 248, 254, 263. Is TRACK on the person talking? (GURT saw
   stills of 248 and 250 only.) Risk calls: 251 (Hitler mustache), 252 (crude), 255 (drunk woman joke).
2. **Run 13 clips (228–247):** do pauses feel long with the audio-based trimming; clip 244 depends on a fart sound;
   228 is an age-of-consent joke (post at all?).
3. **Run 12 clips:** the 1/3 webcam + 2/3 game split; clips where the webcam only shows Joe listening; 212 and 218
   (picked from frames, never heard). **Stale files to delete (Tko):** the `_track.mp4` of 211, 219, 220, 221, 223,
   225, 226, 227 in `Finished_Clips\Streaming\Joe Bart Games`.
4. **Don't post the 12 ✗ clips** in `Finished_Clips\Stavvy's World` (160, 162, 168, 170, 172, 174, 179, 183–186, 188).
5. **Read four rewritten hooks before posting** (written from the log, not the transcript): 178, 182, 188, 191.

**Tko's open decisions**
- **Clean-text rule scope:** GURT allowed alcohol and toilet humor in post text. Ban those too?
- **File names with curses** (134, 143, 161, 170): rename only if a platform shows the upload's file name.
- **Recall:** should Sonnet also submit its 7s, shown unticked in Review? Run 14 says the cheaper answer may be
  GURT's blind pass: three independent pickers found 6 clips Sonnet missed, and agreement between pickers predicted
  survival (16 of 20 moments found by two or more survived; 0 of 3 found by one).
- **Facebook:** no username is needed to post. First real post will show whether `post.facebook`'s selectors match;
  switch the browser to the Page first.

**GURT's work, in order**
1. **Re-render clip 165** (family-so-big): "ROB MARKMAN" shows twice in its captions. In
   `work/MpjdkVCj5ys/review.json` delete `rendered_as` from the 165 entry, add the name-blanking fixes, untick the
   rest, `--render` (re-downloads). It renders as 302. Tko deletes the old 165 files himself.
2. **Scorer prompt fixes owed:** (a) played footage is not clippable (run 13); (b) a clip wholly inside the overlap
   minute belongs to the part it sits in (run 13); (c) credit only the people in the clip (run 13); (d) **stop on
   the payoff**: it ran 10–18s past it on three of ten kept picks (run 14; third sighting, promote into `skill.md`;
   run 15 again on four); (e) a sexual joke about a child is a reject, not a risk flag (run 15); (f) the hosts' own
   lines count when the guest is the star (run 15: it missed both host clips); (g) the credit line needs the show's
   name, taken from the channel when the title has none (run 16); (h) a dodge caught live or a one-question roast is
   a payoff (run 16: it rejected two 9s as "no payoff" and "a mild answer").
3. **Description cleanup the clean-text pass found:** `#stavvyshalkias` in 161–166, `#markNormand` in 236, 245–247,
   `#robmarkman` on 179–180, 20–22 hashtags on seven Joe Bart files, mixed credit lines in Bad Friends and We Might
   Be Drunk. Tko said "looks good" to the report; he has not asked for this cleanup yet.
4. **Review window can't edit a description.** A pick flagged by `review.off_limits` has to be reworded in
   `review.json` or by GURT in chat. Also still pending: the window doesn't reload after GURT's chat edits.
5. **Transcript quality:** fixed in `transcribe.py` during run 16 (see Status). Watch the next run's health numbers;
   if the style hint ever writes curses nobody said, drop the hint and keep conditioning off.
6. Smaller: the app could warn when `clipminer\*.py` is newer than its start time; drop fake-name tokens at
   transcription; webcam near the frame edge and face-bin splitting in `cam_box` (wait for a second streamer);
   `queue.json` job 6 (run 12) still says "failed" although its clips rendered from the command line.

**Review budget (Tko, 2026-10-07: run 16 "ran through a lot of tokens… that number can't stay that high").**
The scoring API is about $1 an episode; the spend was GURT's own session. Agreed for every run from now on:
1. Blind pickers run on Sonnet, not Opus (`model: "sonnet"` on the agent).
2. Transcript health check first; re-transcribe before anything is picked or cut, so cuts are built once.
3. TRACK is checked in code (is the crop's seat the speaker's seat, per shot), with one image sheet per run as a
   sanity check, not one per three clips. **The code check isn't written yet.**
4. Full blind review only on a show that hasn't been run before. On a repeat show GURT reviews Sonnet's picks
   directly. Known cost: Sonnet missed 8 of run 16's 18 clips. (Tko said "sounds good" to all four.)
No GPT subscription as the scorer: a ChatGPT plan has no API access, and the scorer isn't where the cost is.

**How run 14's and 15's review was done** (the full version, for a new show; see the budget above): write the reading file from
`score.reading_lines`; three blind picker agents (stories / one-liners / signals) plus a health-check agent; map
their quotes with `score.locate`; group with Sonnet's picks **by payoff line, not by overlapping time** (the overlap
merge hid a clip); an editor agent and then a skeptic agent per batch of five moments, working from word-indexed
transcript rows; GURT decides, applies with `review.entry`, checks every fix word appears once in the kept words,
runs `review.off_limits` on each description, approves. Run 15 added: a dry-run tool for the agents (prints kept
words with indices, so no index was off), three judges on different lenses to rank for the cap, and a frame-strip
check of every render. Curses in caption fixes are written as `****` directly.
**Write the run log only after the render finishes**: clip numbers are counted from the log.
Posting: every post so far is `track` on YouTube + TikTok. Post blur variants too and log views in each run file's
"Posted" line.
