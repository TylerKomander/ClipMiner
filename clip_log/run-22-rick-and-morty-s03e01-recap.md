## Run 22 — Rick and Morty S03E01 "The Rickshank Rickdemption" (TV episode, local BDRip), 23m, 2026-11-09
**Theme:** `movie-recap` + funny moments · **Posted:** not yet · 372–381 deleted (Tko); v2 in Review
**Picked by:** GURT by hand. Fresh readers did the retell gate: one reader for v1, then 9 and 5 (one per clip) for v2.

**Inputs used:** `transcript.json`, `reading.txt`, `subs_sdh.srt` (plain English SRT, not SDH). The BDRip's first
audio track is a Russian dub, and the WEB copy Tko tried first only had an audio-described English track:
`download.english_audio` now copies the plain English track into `work/` before anything listens to it.

### 372–381 · v1 · deleted · Tko: "Its a little all over the place and doesnt make alot of sense also the cuts are really bad"
- **372 recap:** 19 moments, 153s, three plotlines (brain probe, Citadel hostage, home). The cold reader followed
  the main line and lost the Citadel part (pieces 9–13). Too many hops for one viewing.
- **373–381 funny:** jerry-paid-in-pills, rick-szechuan-sauce, rick-wicker-furniture, bug-level-9-bathroom,
  rick-takes-the-citadel, summer-trial-morty-lawyer, morty-shoots-rick, who-pays-me-to-yell, jerry-foot-down.
- **The bad cuts, measured:** every spliced piece rendered one frame too many. When a piece ended on a camera cut,
  that frame was the next shot (372: a purple-room frame after "Yes, we got it!" and another after "brain-alizer").
  The cause was `-t length` after `-ss (first - 0.5)/fps`: ffmpeg counts `-t` from the first decoded frame, so the
  half-frame lead went onto the end. Fixed: `-t length - 0.5/fps`. The one-piece path now trims to whole frames too.
  A test splice came out at exactly the 783 frames asked for.
- **Head slivers:** 379 opened on 0.38s of the Summer hostage shot, and 372's "dumbass bug" piece on 0.46s of the
  glowing-Rick shot. The line started before the cut and the previous line stopped `unsliver` from growing back.
  Caught at pick time now by a scratch check (not in the repo yet), which lists every stretch whose first or last shot is under 0.5s,
  before anything renders.

Numbers used (never reuse):
- **372 · rick-szechuan-prison-break** · deleted (Tko, v1)
- **373 · jerry-paid-in-pills** · deleted (Tko, v1)
- **374 · rick-szechuan-sauce** · deleted (Tko, v1)
- **375 · rick-wicker-furniture** · deleted (Tko, v1)
- **376 · bug-level-9-bathroom** · deleted (Tko, v1)
- **377 · rick-takes-the-citadel** · deleted (Tko, v1)
- **378 · summer-trial-morty-lawyer** · deleted (Tko, v1)
- **379 · morty-shoots-rick** · deleted (Tko, v1)
- **380 · who-pays-me-to-yell** · deleted (Tko, v1)
- **381 · jerry-foot-down** · deleted (Tko, v1)

### v2 (in Review)
- **Recap · 15 moments, 153s, one line:** cold-open fake escape → bugs probe his brain → the portal-gun memory →
  the Szechuan order → the formula, uploaded → the virus and fabricated-memory twist → the body swap → Rick-as-bug
  gets the Level 9 code → one to a zero ("who's paying me to yell at this guy?") → home → "him or me" → divorce →
  the sauce rant. The Citadel, the kids' capture, the trial and the hostage standoff are out.
- **Funny (7):** rick-szechuan-sauce, rick-wicker-furniture (now set up by the portal-gun memory and the formula),
  bug-level-9-bathroom, summer-trial-morty-lawyer, morty-shoots-rick (now opens on the bluff), who-pays-me-to-yell
  (now opens on "destroying the galactic government"), jerry-foot-down (now opens on Rick's homecoming).
- **Rejected:**
  - rick-takes-the-citadel: needs the body-swap set-up.
  - jerry-paid-in-pills: needs too much lead-in for 40s; the reader gave it 4/10.
  - flappy doodles: sexual.
  - "super fucked up god" speech: crude, and needs the trial.
  - ghoulish overkill: no laugh line.
  - Phoenix Person: needs earlier seasons.
- **Every edge is clean** except the rant's opening: Rick's freak-out changes picture every frame in the episode
  itself.

### Lessons
- **A text-only reader can't see who is speaking.** Count a retell that gets the story right as a pass, even when it
  asks "who is Beth". Fix the gaps it names in the story, not the speaker labels.
- **A cold reader may lose a recap that hops across three plotlines in 19 pieces. Tko lost it.** Pick one line,
  drop the side plots whole, and give each beat its set-up line.
- **Measure the render against the source, frame by frame, before saying the cuts are clean.** Shot lengths alone
  can't tell a join's flash from the show's own fast animation; map each short shot to the stretch edges.
