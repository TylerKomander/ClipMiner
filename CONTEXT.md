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
  opencv-contrib (layouts). `anthropic` when `score` is automated. Confirm before adding more.
- Inputs / outputs: YouTube URL or local file → `Finished_Clips\NN_<name>.mp4`
- Failure mode — each stage caches to `work/<slug>/`; a crash resumes, not restarts
- **Delete `work/<slug>/source.mp4` once the clips are rendered.** Tko's rule: no full videos kept.
  Keep the small text files (transcript, info, loudness); `clip_log.md` refers to them.
  Re-cutting a clip later means re-downloading.
- v1 scope: **comedian podcasts** (active theme `comedian-podcast` in `skill.md` Part A).
  Themes will be swappable later; no implementation yet, but rules and log are split into
  universal vs theme so a new profile is all that's needed. Posting stays manual. No movie
  clips (copyright).
- **Clips folder:** `Finished_Clips\NN_s<score>_<name>_<layout>.mp4`. Tko moves posted clips
  into `Finished_Clips\Used-Clips\` so he knows what's safe to delete. **GURT never deletes,
  renames or moves anything in `Used-Clips\`, and never deletes finished clips.** Tko owns
  cleanup.
- **Clip count is variable** (quality decides, not a number). Every clip gets a 1–10 absolute
  score (rubric in `skill.md`); only 6+ are rendered. Videos over 1h are read in chunks.
- Run 1 (clips 01–05) stays BLUR-only. Tko decided not to re-render it.
- **Every clip is rendered in all 3 layouts** (blur/split/track). Tko posts variations across
  platforms; performance decides. No layout rule until the numbers say so.
- **No automatic judgment database.** GURT keeps the guidance by hand, and owns both files:
  `skill.md` = the rulebook, read in full every run (keep it tight).
  `clip_log.md` = worked examples per run (kept + rejected, with why). Grows; code will pull
  a few relevant entries into prompts. This is what lets the API model, and later a small local
  model, pick like GURT does.
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

## How a run is done today (manual; the helper scripts were throwaway, this is the recipe)
All commands from `Projects\ClipMiner`, with `PYTHONPATH` = project dir and the PATH refreshed
(`$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
[Environment]::GetEnvironmentVariable('Path','User')`), since old shells don't see ffmpeg.
1. `.\.venv\Scripts\python.exe -m clipminer <url>` (background it; ~5 min download +
   ~7 min/hr transcribe) → `work\<id>\{source.mp4, info.json, transcript.json}`.
2. `clipminer.signals.loudness(video, work)` → `loudness.json` (~10s).
3. Transcript health check: identical-start word runs (only 15+ = hallucination), lowercase
   stretches. Print the heatmap as text bars.
4. Write a reading file: transcript merged into ~15s lines as `h:mm:ss text <L+n> <H0.xx>`
   (loudness ≥ 6 LU over median, heatmap ≥ 0.3). Read ALL of it in chunks.
5. Shortlist → print word-level `word@start` for each window → choose first/last word starts.
6. **Dry run:** select words with `a-0.05 <= start <= b+0.05`, print first 5 / last 5 words
   and length for every clip. Fix before rendering.
7. Render per clip: `start = first.start - 0.15`, `end = last.end + 0.3`;
   `segs, split = reframe.plan(video, start, end)`; `render(... _blur)`;
   `render(..., track_filter(segs, W, H), CAPTIONS_LOW)` → `_track`; if `split`:
   `render(..., split_filter(split, W, H), CAPTIONS_SEAM)` → `_split`. ~2 min per clip.
8. Spot-check frames from a few outputs (contact sheet), then delete `source.mp4`.
9. Log the run in `clip_log.md` (same format as run 3) and fold lessons into `skill.md`.
Next clip number: **29**.

## Status
- [x] ffmpeg installed, `download` + `transcribe` produce a word-timed transcript
- [x] Run 1 end-to-end on Wild Ride #222 (73.5 min): 5 clips in `Finished_Clips\`
- [x] `render` 1080x1920 clips with captions
- [x] Tko reviewed run 1: all 5 kept. Reasoning written up in `clip_log.md`
- [x] 3 hand-judged runs on different shows (Wild Ride, Matt & Shane, JRE). Runs 1–2 all kept.
- [x] SPLIT + TRACK layouts ported from openshorts; 06–10 rendered in all three layouts
- [x] `skill.md` split into theme profile (A) + universal rules (B); log patterns tagged
- [ ] Tko posts variants; performance per layout/platform goes into `clip_log.md` "Posted"
- [x] Run 3: JRE #2187 Sandler (2h17m) → 18 clips (11–28), BLUR + TRACK; SPLIT n/a
      (multi-camera). TRACK now shot-aware (ffmpeg scdet). Verdict pending.
- [ ] Try `condition_on_previous_text=False` in `transcribe.py` (Whisper went lowercase
      mid-episode in runs 2 and 3)
- [ ] Jump cuts: splice out a rambling middle so 37–38s stories fit ~30s
- [ ] Transcribe speed: run 2 took 634s for 76 min (goal ~5 min). Degraded output (no
      punctuation, a hallucinated repeat) may be related. Investigate before automating.
- [ ] `signals` ad detection + heatmap ad-skip filter in code
- [ ] `score` automated from `skill.md` rules (Claude API)
- [ ] One local file (no heatmap) end-to-end

**Later (not v1):** face-tracked crop · gameplay/visual signals · local model · app/agent wrapper.

**Reference:** github.com/mutonby/openshorts (MIT). Worth taking: SPLIT layout (two speakers
stacked, captions on the seam; mediapipe), PySceneDetect to avoid cutting across shot changes,
LLM via OpenAI-compatible `base_url` so the local-model swap is config. Not taking: Docker, S3,
fal.ai/ElevenLabs, FastAPI dashboard. Their picker is transcript-only (no heatmap, no ad filter).

**Gotchas:**
- `av` pinned to 18.1.0: av 19 removed `metadata_errors`, which faster-whisper 1.2.1 still passes.
- yt-dlp warns it has no JS runtime (deno). Downloads work; install deno only if formats go missing.
- Heatmap peaks after ad reads are skip landings, not replays (see `skill.md`).
- Run: `.\.venv\Scripts\python.exe -m clipminer <url-or-file>` (download + transcribe only so far;
  the rest is the manual recipe above)

## Next step
Tko reviews clips 11–28 (keep/reject, and does the score order match his taste?). Then:
code the ad filter + automate `score` via the API, using `skill.md` + `clip_log.md` as the
prompt, and compare its picks on run 3 against the hand-picked 18.
