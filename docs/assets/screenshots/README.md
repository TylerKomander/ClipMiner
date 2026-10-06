# README screenshots — shot list & capture guide

The README's **Screenshots** section pulls PNGs from this folder. They are captures of the real app
(`clipminer/gui.py`) showing **made-up demo data**: the shows, guests, clips and the `@democlips` account are
fictional, so no real episode, pick or account appears in the repo.

## Capture settings

- **Window size:** 1600 × 860, the app's client area only (no Windows title bar).
- **Format:** PNG at native resolution; the README sizes them.
- **Content:** a queue with jobs at different stages, one episode waiting in Review with kept and dropped picks,
  and a Clips tree with both types, several shows and some posted clips. Empty pages photograph poorly.

## In the README now

| File | Page | Shows |
|---|---|---|
| `review.png` | Review | **Featured shot.** Nine picks for one episode, two dropped, one selected with its payoff, reason, splice and post text. |
| `queue.png` | Queue | Jobs done, waiting in review, running and queued, with clip counts and times. |
| `clips.png` | Clips | Clips by type and show, best score first, with a clip's description, post history and the Post buttons. |

To retake them after a UI change, fill `queue.json`, `work\<slug>\review.json`, `Finished_Clips\` and `posts.json`
with demo data, open the app, and capture each page at the size above.
