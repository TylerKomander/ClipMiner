# ClipMiner GUI — Build Spec (handoff)

**Project:** `D:\ClaudeHub\Projects\ClipMiner\`. Read its `CONTEXT.md` first.
**Status:** Built 2026-09-30 (`clipminer\gui.py`). Changed from this spec by Tko's decision: the pipeline stops at a **review** stage before render. Sonnet's picks land in `work/<slug>/review.json`; Tko approves in the GUI's Review window, or GURT edits and approves the same file from chat. The worker renders anything approved, from either side.

---

## What Tko wants
1. **URL queue:** drop in many URLs; they process in the background, so he doesn't wait for each one to finish.
2. **Post-ready output:** each clip file comes with a written post description he can copy and paste. Nothing posts automatically.
3. **Account profiles:** each profile lists the social accounts connected to it. Tko picks a profile and clicks a platform button, and the browser opens that account.

---

## Stack
- **Python 3.12, tkinter** (stdlib). No new dependencies. Adding one requires Tko's OK (see `CONTEXT.md`).
- Lives inside the existing package: `clipminer\gui.py`, launched with `.\.venv\Scripts\python.exe -m clipminer.gui`.
- Reuse the pipeline functions (`download.fetch`, `transcribe.transcribe`, `render.render`, `score`, …) directly. Don't shell out to the CLI.

---

## 1. Queue
- A text box where you paste one or more URLs (or local file paths), one per line, then click **Add**.
- A list view with columns: URL/title · stage (queued / download / transcribe / signals / score / render / done / failed) · clip count · elapsed time.
- **One worker thread, one job at a time.** There's only one GPU (RTX 2080 Super) running Whisper and rendering, so running jobs in parallel would just slow them all down. The point of the queue is that Tko doesn't have to wait.
- The worker pushes progress to the UI through `queue.Queue` plus `root.after()` polling. Never touch tkinter widgets from the worker thread.
- A failed job shows the error and the queue moves on to the next job. **Retry** re-runs the job, and each stage resumes from its `work/<slug>/` cache.
- The queue is saved to `queue.json` so it survives closing the app. Anything that was mid-run goes back to `queued` on restart.
- Each finished job runs the existing "delete `work/<slug>/source.mp4` once the clips are rendered" rule.

## 2. Post descriptions
- **These are written by `score`, not by the GUI.** The same Claude API call that picks a clip returns a post description, saved as a `.txt` with the same name as the clip: `Finished_Clips\NN_s<score>_<name>_<layout>.mp4` → `NN_s<score>_<name>.txt` (one per clip, shared by all 3 layouts).
- Contents: hook line + short caption + hashtags. Style rules go in `skill.md`.
- GUI **Clips** panel: lists the finished clips, most recent first. Selecting one shows its description. Buttons: **Copy description** (clipboard), **Open folder** (Explorer with the file selected), **Play**.
- Nothing calls a social media API. Posting stays manual.

## 3. Account profiles
- Stored in `profiles.json` at the project root. Tko edits it through the GUI; it can also be edited by hand.
  ```json
  [
    {
      "name": "Comedy Main",
      "browser_profile": "Profile 2",
      "socials": [
        {"platform": "TikTok",    "url": "https://www.tiktok.com/@handle"},
        {"platform": "YouTube",   "url": "https://studio.youtube.com/channel/UC..."},
        {"platform": "Instagram", "url": "https://www.instagram.com/handle/"}
      ]
    }
  ]
  ```
- GUI: a dropdown to pick the active profile, then one button per social in that profile. Add, edit and delete profiles and socials from a simple dialog.
- **Button action:** `chrome.exe --profile-directory="<browser_profile>" <url>`.
  - **Why the browser profile matters:** opening a URL alone lands you on the page as whichever account that browser is already logged into. Each ClipMiner profile gets its own Chrome profile that is permanently logged into that account's socials. That's how "click, and I'm in the right account" works.
  - Find `chrome.exe` in the standard install paths. If Chrome isn't there, fall back to `webbrowser.open(url)` and show a warning that account selection won't apply.
  - Profile directory names (`Default`, `Profile 1`, …) are listed at `chrome://version` → Profile Path. Put that tip next to the field.
- Optional: show the active profile next to the Clips panel so the description and the account buttons are on screen together.

---

## Layout (one window)
```
┌ Queue ─────────────────────────┐┌ Profile: [Comedy Main ▼] ┐
│ [paste URLs……………] [Add]       ││ [TikTok] [YouTube] [IG]  │
│ title        stage     clips t ││ [Edit profiles]          │
│ Ep 640       render    3   6m  │└──────────────────────────┘
│ Ep 641       queued            │┌ Clips ───────────────────┐
│ [Retry] [Remove]               ││ 11_s8_...  (select)       │
└────────────────────────────────┘│ description text…         │
                                  │ [Copy] [Open folder][Play]│
                                  └───────────────────────────┘
```

---

## Rules (from Tko's `CLAUDE.md`)
- No comments unless they explain *why*. No dead code. No premature abstraction.
- Match the existing style in `clipminer\*.py`: small functions, `pathlib`, `subprocess.run(check=True)`.
- **Never delete, rename or move anything in `Finished_Clips\` or `Finished_Clips\Used-Clips\`.** Tko owns cleanup.
- Update `ClipMiner\CONTEXT.md` Status and Next step when done.

## Done when
- [ ] Paste 3 URLs, close nothing: all 3 finish one after another with clips and `.txt` descriptions.
- [ ] Kill the app mid-job, reopen it: the job resumes from cache and doesn't start over.
- [ ] A bad URL fails with a visible error and the next job still runs.
- [ ] Copy description puts the text on the clipboard.
- [ ] With 2 profiles set up on different Chrome profiles, each platform button opens the right logged-in account.
