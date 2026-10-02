# ClipMiner

> Kind: `scripts`

## Goal
`clipminer <url-or-file>` turns a long comedian podcast into every clip worth posting
(variable count, scored 1–10), each 10–35s, 9:16, burned-in captions, in all 3 layouts, with a
one-line reason per clip. Scoring moves from GURT-by-hand → Claude API → small local model.

## Constraints
- Language: Python 3.12
- Where it runs: manual, Windows, RTX 2080 Super (local Whisper on GPU)
- Deps: ffmpeg (winget), yt-dlp, faster-whisper, av (pinned), CUDA libs, mediapipe +
  opencv-contrib (layouts), `anthropic` (score), `playwright` (fills upload pages; drives installed Chrome).
  Confirm before adding more.
- Inputs / outputs: YouTube URL or local file → `Finished_Clips\NN_<name>.mp4`
- Failure mode — each stage caches to `work/<slug>/`; a crash resumes, not restarts
- **Delete `work/<slug>/source.mp4` once the clips are rendered.** Tko's rule: no full videos kept.
  Keep the small text files (transcript, info, loudness); the `clip_log\` run files refer to them.
  Re-cutting a clip later means re-downloading.
- v1 scope: **comedian podcasts** (active theme `comedian-podcast` in `skill.md` Part A).
  Themes will be swappable later; no implementation yet, but rules and log are split into
  universal vs theme so a new profile is all that's needed. Posting: the app fills the upload page,
  Tko clicks Post (never auto-publish). No movie clips (copyright).
- **Clips folder:** `Finished_Clips\<podcast>\NN_s<score>_<name>_<layout>.mp4` (+ `.txt` description).
  The app groups clips by podcast, best score first, and tracks where each was posted in `posts.json`
  (asked when the posting browser closes, or "Mark posted"). `Used-Clips\` is optional now. **GURT never deletes,
  renames or moves anything in `Used-Clips\`, and never deletes finished clips.** Tko owns
  cleanup.
- **Clip count is variable** (quality decides, not a number). Every clip gets a 1–10 absolute
  score (rubric in `skill.md`); only 6+ are rendered. Videos over 1h are read in chunks.
- Run 1 (clips 01–05) stays BLUR-only. Tko decided not to re-render it.
- **Captions never show a curse word** (masked `****`; audio untouched). Clips 01–67 predate the rule
  and were deleted by Tko as test runs (2026-09-30); their reasoning stays in `clip_log\`. Clip numbers
  keep counting from the log (`review.next_number`), so new clips start at 68 even with an empty folder.
- **Every clip is rendered in all 3 layouts** (blur/split/track). Tko posts variations across
  platforms; performance decides. No layout rule until the numbers say so.
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
5. `render` — ffmpeg cut, burned word-timed captions, layout BLUR / SPLIT / TRACK
   (`reframe.py`: YuNet face detection + mediapipe jawOpen for active speaker;
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
Next clip number: **147** (counted from the logs automatically: write a run's log after it renders).

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
- [ ] Try `condition_on_previous_text=False` in `transcribe.py` (Whisper went lowercase
      mid-episode in runs 2 and 3)
- [x] Splicing (`splice.py`): story cuts from review (`cuts`, Sonnet proposes them), dead air shortened
      unless laughing, endings cut from the audio. Tested on run 7's crematorium story (77s → 32s)
- [ ] Transcribe speed: run 2 took 634s for 76 min (goal ~5 min). Degraded output (no
      punctuation, a hallucinated repeat) may be related. Investigate before automating.
- [ ] `signals` ad detection + heatmap ad-skip filter in code
- [x] `score.py` (Claude API): 20-min pieces, structured output, length/dedupe in code. Run 3:
      Haiku 4.5 found 9/18 (too small); Sonnet 5.5 found 16/18. Sonnet is the scorer.
- [x] `review.py`: review gate (`review.json`), dry-run preview, render with exact caption words,
      curse masking, per-clip `.txt` post description; numbering continues across Used-Clips
- [x] GUI (`gui.py`) per GUI_SPEC with a review stage. Runs 7 and 8 went through it end to end
- [x] Account `Comedian-House-TV` set up; posting works on YouTube + TikTok (4 clips, 2026-09-30 → 10-01)
- [x] Second batches: picks added after a render render on their own (`--render <slug>` or the app);
      the source is re-downloaded. API key read fresh from the registry (`score.api_key`)
- [ ] Sonnet matches GURT's blind picks on new shows (GURT keeps logging the diffs)
      Run 4 (Arenas): agreed on 5 of 10; Sonnet found 2 GURT missed; Tko kept all 11.
      Run 5 (Theo Von): agreed 6 of 10, 3 finds kept. Run 6 (Flagrant): agreed 7 of 10, 5 finds kept.
      Run 9 (Bad Friends): found 9 of GURT's 18 (+2 lost in code, now fixed); 16 picks, only 4 weak.
- [ ] One local file (no heatmap) end-to-end

**Cost plan (Tko 2026-09-30: fine for now, must get cheaper as it scales).** Today ~$1–1.50 per 2h
episode, mostly Sonnet's output (~9k tokens per 20-min piece, flat across runs; logs don't shrink it).
In order: (1) Message Batches API for queued episodes, −50% on everything, no quality risk; (2) lower
reasoning effort once Sonnet matches GURT's blind picks, tested against them; (3) drop the rejects list
from the output once it stops teaching; (4) cut ads/intro/outro from the transcript sent; (5) local model.
Prompt caching is already on (~90k cached input tokens saved per episode).

**Later (not v1):** face-tracked crop · gameplay/visual signals · local model · app/agent wrapper.

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
Run 10 through the app. First run with the length retry and the new rules (splice setup + payoff,
cross-talk, score calibration, escalating riff): check whether Sonnet's share of GURT's blind picks rises
above ~65% and whether picks marked "Dropped by code" show up unticked in Review.
Posting: every post so far is the `track` layout on YouTube + TikTok. Post blur variants too and log views
in each run file's "Posted" line, or the layout question never gets answered.
