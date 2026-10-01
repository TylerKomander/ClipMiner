## Run 8 — This Past Weekend w/ Theo Von #686 (guest Caleb Pressley), 2h05m, 2026-10-01
**Theme:** `comedian-podcast` · **Posted:** _(pending)_ · **Layouts:** BLUR + TRACK; SPLIT none
**First run where Tko approved before GURT's pass**, and the first with Sonnet proposing splices (13 picks).

**Episode read:** two deadpan absurdists riffing: Caleb's retirement-building years, street interviews,
his tequila and shoe brands, a fake William Morris head at the World Cup, the Stagecoach DJ set, and
Theo's long run on Tommy Tuberville's "furry pilots" claim (pilot announcements, Alabama mascots,
flight attendants' code words). Darker run late: circumcision/autism, "the elite" eating baby foreskin,
zoo meat. Ads: 21:56–24:47 (PrizePicks, Quo). No heatmap. Loudness: 8 spikes in 125 minutes.

**What went wrong outside the picks:**
- The API key died; scoring failed with 401. After `setx`, the app still had the old key: a process
  keeps the environment it launched with. **Fixed:** `score.api_key()` reads the stored key from the
  Windows registry on every run.
- Whisper dropped curse words again ("I don't give a no", "who gives a tommy") and heard "window" as
  "winter". Caption fixes on 126.
- Lowercase for most of 16:41–1:44:43; loops at 1:30:11 ("I'm going to end up with autism" ×4) and
  1:47:16 (word salad, 43 words).

**Tko's verdict:** approved all 32 of Sonnet's picks before GURT's pass. Clip review pending.

**Clips**
Batch 1 (86–117): Sonnet's 32, as approved. Batch 2 (123–127; 118–122 skipped by a numbering slip): GURT's, after the diff.
- **123 · 8 · "I got to ask"** (10:31, 28s). Caleb's street-interview trick: say "I got to ask" and
  people stop, "curious about themselves." Shape: *insider rule revealed*.
- **124 · 8 · "You seem so confident"** (11:44, 20s). "I'm not doing that great, but I am headed to the
  gym." Shape: *self-roast*.
- **125 · 8 · Missing posters: they moved** (25:04, 37s, 1 cut). "They didn't get kidnapped, they
  moved... people that got too good looking had to move out of town." **Risk flag:** missing women.
- **126 · 9 · Furry pilot, captain speaking** (39:31, 22s). "If you look out the window to the left
  you'll see a sanctuary where I was rescued from... shout out dander gang." Shape: *absurd image,
  played out*. Sonnet had it but at 47s; code dropped it.
- **127 · 9 · Gronk and the fake William Morris head, full** (50:18, 38s, **7 cuts** from 2m09s).
  Sonnet's 101 ends before the payoff. This one ends on "Rob goes: somebody told me that was the
  head of William Morris." Shape: *a con, and the mark finds out*.
- Best of Sonnet's batch by GURT's read: 91 (old lady: "I'm white"), 90 (Backflip Taxi), 95 (brain in
  your stomach: "the fact's not even true"), 112 (pulling the pipeline), 103 (crowd surfer), 107
  (furry flight attendants).

**Would have rejected from batch 1** (GURT's read, for the log; Tko decides what posts)
- 116, 117 shoe reviews; 92, 93 Chica Cheetah taglines: **Caleb plugging his own brands.** Posting is
  free advertising for him. Promotional segments are off-theme (skill.md: tour plugs, business talk).
- 99, 108, 114, 115: 6s. Filler.
- 100 "melt the TV down", 109 "zoo is the last grocery store": dark politics, weak payoff.
- 86 trafficked-woman cold open, 88 "God made three of them" (fat joke at a named friend): mean, no turn.

**Scorer vs GURT** (Sonnet 5.5, 7 parts, 44k in / 124k cached / **80k out**: most output yet)
- Agreed on 12 of GURT's ~17 candidates.
- **Splicing worked:** sensible cuts on 10 rendered clips (removed Theo's mid-show re-intro from 95,
  tangents from 111 and 112). But it **cut 101 before the payoff**, and 6 picks still failed the
  length check after its cuts (furry captain at 47s, missing posters at 42s).
- It picked 32. Too many: promotional segments and 6s again. The no-payoff/sincere lesson still
  isn't biting, and it has no rule against plugs.

**Lessons**
1. `[universal]` A process keeps the environment it launched with; read secrets fresh (`api_key()`).
2. `[universal]` Promotional segments (a guest's own brand) are ads in disguise. Drop them.
3. `[scorer]` Model splices sensibly but can cut before the payoff (101). Check that the last kept
   line is the payoff.
4. `[scorer]` Model's cuts often still leave the clip over 40s; it underestimates spoken length.
5. `[workflow]` Approving before GURT's pass works with a second batch (`render_approved` now
   renders only new picks; the source is re-downloaded).
