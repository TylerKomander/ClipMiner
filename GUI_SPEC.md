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
- GUI **Clips** section (reworked 2026-09-30): a tree grouped by podcast folder, best score first, with a Posted
  column. Selecting a clip shows its description and post history (`posts.json`: platform, account, layout, date).
  The app asks "Did you post it?" when the posting browser closes; "Mark posted" covers posts made elsewhere.
  Buttons: **Copy description**, **Play**, **Open folder**.

## 3. Accounts and posting (reworked 2026-09-30, Tko's call)
- `profiles.json`: each account has a name, a fixed browser folder (`browsers\<name>\`, gitignored) and one
  slot per platform (TikTok, YouTube, Instagram): username + profile link. **No passwords stored**: Tko signs in
  once inside that browser ("Log in" opens plain Chrome on that folder; Google blocks sign-in under automation).
- Clips → Post: pick clip, layout and account, click "Post to <platform>", confirm. `clipminer\post.py` drives
  the account's browser with Playwright (installed Chrome, not a downloaded one): opens the upload page, attaches
  the clip, fills the caption (YouTube: title = hook, description = the rest, "not made for kids"), and stops.
  **Tko clicks Post.** If a step fails the browser stays where it stopped and the caption is on the clipboard.
- Risk Tko accepted: platform pages change and break selectors; TikTok/Instagram watch for automated browsers.
- Your everyday Chrome profiles can't be used: since Chrome 136 automation is refused on the default user data dir.

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
