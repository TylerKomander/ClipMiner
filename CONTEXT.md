# ClipMiner

> Kind: `scripts`

## Goal
`clipminer <url-or-file>` turns a long comedian podcast or a stream into every clip worth posting (variable count,
scored 1–10), each 10–35s, 9:16, burned-in captions, in the layouts its type calls for, with a one-line reason per
clip. Tko picks the type (Podcast / Streaming / Movie) before pasting the link. A **movie** is a local film file in →
**one recap short** that tells the main story as a supercut of whole jokes (style of `UTBAKThAmI4`, `ZY4qS0KewuI`),
plus **funny moments**: standalone shorts of single jokes, 1–4 spliced pieces each, only 8+ (none is fine).
Scoring moves from GURT-by-hand → Claude API → small local model.

## Constraints
- Python 3.12, manual, Windows, RTX 2080 Super (local Whisper on GPU). Deps: ffmpeg (winget), yt-dlp,
  faster-whisper, av (pinned 18.1.0), CUDA libs, mediapipe + opencv-contrib, `sherpa-onnx`, `anthropic`,
  `playwright` (drives installed Chrome). Models in `models\`, fonts in `fonts\`. Confirm before adding deps.
- **Downloads stay at 1080p** (Tko, 2026-10-06). Don't raise `download.py`'s cap.
- Each stage caches to `work/<slug>/`; a crash resumes, not restarts.
- **Delete `work/<slug>/source.mp4` once the clips are rendered** (no full videos kept); keep the text files.
  A movie's input is Tko's own file: **ClipMiner never deletes or moves it** (`info.json` `path`).
- **Types** (`review.KINDS`): `podcast` → `comedian-podcast`, `stream` → `streamer`, `movie` → `movie-recap`. The type
  sets the theme profile, layouts and clips folder. A new type = one line in `KINDS` + a profile in `skill.md` Part A.
- **Layouts:** Podcast = BLUR + TRACK (+ SPLIT when both faces share the shot). Streaming = BLUR + GAME on gameplay,
  BLUR + TRACK without; **GURT checks `work\<slug>\facecam.jpg` before approving** (override: `"facecam": [x,y,w,h]`).
  Movie = BAND only (follows the speaker; `crop_x` pins a fixed crop). Show with no close-ups: fill `"seats"` in
  `review.json` before approving (recipe in `skill.md` "Render").
- **Clips folder:** `Finished_Clips\<Podcast|Streaming|Movies>\<show>\NN_s<score>_<name>_<layout>.mp4` (+ `.txt`).
  Older show folders sit straight under `Finished_Clips\` (listed as Podcast). Clip numbers count from `clip_log\`
  (`review.next_number`): **write a run's log only after its render finishes.**
- **GURT never deletes, renames or moves anything in `Used-Clips\`, and never deletes finished clips.** Tko owns cleanup.
- **Clip limit:** 20 per video, 30 over 3 hours (`review.clip_cap`). Under it, quality decides; only 8+ render.
- **Captions never show a curse word** (`****`, audio untouched). **Post text is clean**: no curses, nothing about
  sex, porn or drugs (`review.off_limits` enforces it). Alcohol and toilet humor allowed. File names not covered.
- **Posting:** YouTube only for now. The app fills the upload page; a manual Post stops before Publish. **Auto-post**
  (2026-11-09) opens, fills and **clicks Publish** on a schedule, Movies included: the Ready tick (`ready.json`) is
  Tko's OK after watching. Only while the app is open; schedules off at every start. Posts tracked in `posts.json`.
- **Movies post only to The-Theatre-Goer** (an account ticked "Movie channel"), never Comedian-House-TV. Expect
  Content ID claims on most recaps.
- **Judgment lives in two files GURT owns:** `skill.md` (the rulebook, read in full every run, keep it tight) and
  `clip_log\` (one file per run + `INDEX.md` with tallied lessons; 3+ sightings get promoted to `skill.md`). Sessions
  read the index, never the whole log. **Commit after every run.**
- **Review budget** (Tko, 2026-10-07: token spend "can't stay that high"): GURT picks by hand in one lean pass; no
  panels or multi-agent workflows on a routine run. Blind pickers, if ever used, run on Sonnet.

## How a run is done
**App:** `.\.venv\Scripts\python.exe -m clipminer.gui` from the project root. Tko normally starts it. When he asks
GURT to, start `.venv\Scripts\pythonw.exe -m clipminer.gui` via `Invoke-CimMethod Win32_Process Create`
(CurrentDirectory = project root): an app started as a child of GURT's shell died mid-render (run 14). If GURT must
render, use `--render <slug>` as a background task.
**CLI:** `python -m clipminer <url>` (no URL = `queue.txt`) stops at review; `python -m clipminer --render <slug>`.
**Picks (GURT by hand, default since 2026-11-09):** a job downloads, transcribes, measures loudness and parks as
**for GURT** ("Send to Sonnet" hands one to the API). When Tko says "pick it": write the reading file fresh from
`score.reading_lines(work)`, read it (+ `subs_sdh.srt` for a film) and the theme profile in `skill.md`; write the
picks as the Sonnet cache (`parts-claude-sonnet-5-5/<begin>.json` per `score.chunks(...)` piece, or
`recap-claude-sonnet-5-5.json` **and** `funny-claude-sonnet-5-5.json` for a movie, `{"clips": [], "rejected": []}`
if none, or the API is called); run `score(work, kind=...)`; set each clip's `by`/`model` to
`gurt-by-hand`. The app moves the job to Review. Edits: `review.entry(...)`, check `review.off_limits`, approve.
**Movies:** follow `skill.md` movie-recap "How to build a recap" step by step. Worked examples:
`clip_log\run-20-atlanta-s02e01-recap.md` (348, the reference) and `run-21-curb-s12e03-recap.md`. The retell gate
needs a fresh reader given the full spoken text of each moment; the picker passes its own gates.

## Status
- [x] Pipeline: download → transcribe (word timestamps, cased via `hotwords`) → loudness → score → review → render
- [x] Layouts BLUR / TRACK / SPLIT / GAME / BAND; style C captions (Lilita One, per-speaker colour from `sherpa-onnx`)
- [x] Splicing (`splice.py`): story cuts, quiet-only dead-air trims, whole-frame stretches, HDR tone-mapped
- [x] TRACK never holds a shot past 4.5s (Shorts editing rule)
- [x] App: queue, review, clips by type/show, accounts, auto-post schedules, YouTube tab closes and records itself
- [x] Movie type: recap from a local file, SDH subtitles saved, BAND follows the speaker. Atlanta 348: "really good"
- [x] Recap rules after Curb v4 was rejected: a moment is a whole joke, cap 155s of speech, no source chapters
- [x] Movie funny moments (`score.funny`, skill.md "Funny moments"): code done, dry-run on a copy of Curb
- [ ] Funny moments picked, rendered and passed by Tko on a real episode
- [ ] Auto-publish confirmed live (see Next step)
- [ ] Curb recap v7 rendered and passed by Tko
- [ ] A real film (not a TV episode) through the recap recipe
- [ ] Sonnet matches GURT's blind picks (best so far 79%, run 10; streams: 1 of 17, run 12)
- [ ] First 3 stream runs logged (2 of 3)
- [ ] In-code TRACK/GAME seat check (budget rule; not written)
- [ ] `signals` ad detection + heatmap ad-skip filter
- [ ] One local podcast file (no heatmap) end to end
- [ ] Facebook posting (selectors never run against the real page; parked: YouTube only)

## Next step
**Watch the first scheduled auto-publish:** `#done-button` clicked, tab closes itself, `posts.json` records it
without the Posted? question. Stuck at "YouTube: publishing" = the button id changed.
Then: Tko watches Curb v7 (351); his verdict goes in run 21. 349 and 350 in
`Finished_Clips\Movies\Curb.Your.Enthusiasm.S12E03\` are rejected cuts.
**Funny moments, first real run:** when Tko says "pick it" on Curb S12E03, GURT writes
`funny-claude-sonnet-5-5.json` by hand and runs `score(work, kind="movie")`: the picks are added to the existing
review (8+ ticked), the rendered recap is untouched, and the job shows in Review again. Atlanta's source is gone
(`info.json` points at a missing `Movies\Atlanta...mkv_`): it needs the file back before any funny-moments render.

## Open items
**Tko's queue (nobody has listened to these; don't tick unwatched clips Ready):**
- Run 19 (332–345): re-rendered TRACK files (≤4.5s shots) are waiting on Tko's yes to overwrite; if that scratchpad
  is gone, re-render. 334 is unsure on TRACK: post BLUR. Its "slow child" pick sits unticked.
- Run 18 (322–331): least sure 325, 330, 326; risk calls 327, 325.
- Run 17 (302–321): Sonnet's 20, never reviewed by GURT.
- Run 16 (284–301): "Listen:" notes in `work\ByDpG7QzNTQ\review.json`. 297 opens on the wrong face: post BLUR.
  Risk calls 296, 288, 290, 284, 297, 299, 300, 292.
- Run 15 (264–283): TRACK files are the old wrong ones, post BLUR (re-render is Tko's call). Risk calls 279, 281,
  282, 268, 271. Ten 8s sit unticked over the cap.
- Run 14 (248–263): guessed captions 249, 251; endings 257, 261; risk calls 251, 252, 255.
- Run 13 (228–247): 244 needs its fart sound; 228 is an age-of-consent joke (post at all?).
- Run 12: stale `_track.mp4` of 211, 219–221, 223, 225–227 in `Joe Bart Games` for Tko to delete.
- Don't post the 12 ✗ clips in `Stavvy's World` (160, 162, 168, 170, 172, 174, 179, 183–186, 188); read hooks 178,
  182, 188, 191 first. Don't tick recaps 346/347 Ready.

**Tko's open decisions:** ban alcohol/toilet humor in post text too? · rename the curse file names (134, 143, 161,
170) only if a platform shows them? · may a strong story pass 40s (`score.locate` refuses today)? · BLUR/GAME get
the 4.5s shot rule too? · white "unsure" caption lines: fill them? · a better face detector for dark shots (new model)?

**GURT's work, in order:**
1. Re-render 165 (ROB MARKMAN shows twice): delete its `rendered_as` in `work/MpjdkVCj5ys/review.json`, add the
   name-blanking fixes, `--render`. Tko deletes the old files.
2. Voice labels behind 297's first 6 seconds.
3. Description cleanup (Tko hasn't asked yet): `#stavvyshalkias` 161–166, `#markNormand` 236, 245–247, `#robmarkman`
   179–180, 20–22 hashtags on seven Joe Bart files, mixed credit lines in Bad Friends / We Might Be Drunk.
4. Review window can't edit a description or reload after GURT's chat edits.
5. Smaller: warn when code is newer than the app's start; `queue.json` job 6 says "failed"; webcam near the frame
   edge in `cam_box`; compounds like `half-assed` not in `render.CURSE`.

**Cost plan (Tko: fine now, must get cheaper):** Message Batches API (−50%) → lower reasoning effort once Sonnet
matches GURT → drop the rejects list → cut ads/intro from the transcript → local model. **Sonnet 5.5 refused recap
drafts on an R-rated episode's language**: the app's Sonnet recap path may hit that.

**Gotchas:** `av` 19 breaks faster-whisper 1.2.1 (`metadata_errors`). yt-dlp's no-JS-runtime warning is harmless.
Heatmap peaks after ad reads are skip landings. Hand fixes to a `transcript.json` shift word indices, so older
`review_v*.json` files can't be re-rendered as they are.
