## Run 10 — This Past Weekend #687 (guest Zohran Mamdani, NYC mayor), 77m, 2026-10-02
**Theme:** `comedian-podcast` · **Posted:** _(pending)_ · **Layouts:** BLUR + TRACK; SPLIT none
GURT picked blind before reading Sonnet's list. First run with the length retry and the run 9 rules.

**Episode read:** a sitting politician on a comedian's show. Most of the 77 minutes is sincere policy talk (budget,
rent, childcare, nurses' strike, socialism, Trump meetings) and a long Gaza/Netanyahu stretch at the end; all of it
off-theme. The clips live in Theo's tangents and in the mayor playing straight man: a fish name that turns into
"Queefish", a "tight shit" day he's "here to announce", word lifeguards, the DoorDash settlement riffs. Ad: Acorns
27:56–29:28. No heatmap. Loudness not used.

**Transcript:** lowercase with no punctuation 0:00–11:36; word salad 11:16–11:36; "I wake up in the morning" repeat at
1:41; "Yeah" ×20 at 17:52 (hallucinated); one sentence repeated three times at 47:53; "TSTS" loop on the outro.
Misheard names fixed in captions: Hsu → Xu (DoorDash CEO), click-to-care → click-to-cancel, Creamers → Creamery.
**Faces:** one camera per person (single close-ups), so no SPLIT. YuNet boxes were right on both men.

**Tko's verdict:** approved the merged list in the app as GURT left it (13 of 15).

**Clips** (GURT = picked blind by GURT; Sonnet = Sonnet's pick or Sonnet's version of a shared moment)
- **147 · 7 · Where are my crumbs** (10:21, 23s, Sonnet). An Adams aide's bribe line; "that sounds like a bar... poetic at
  being corrupt." Opens on "he", never names Eric Adams (cold read −1). Shape: *absurd image → strong verdict*.
- **148 · 9 · Queefish** (18:22, 26s, 2 cuts, GURT). Theo spells a fish into "Queefish? Queef?"; the mayor: "that's not the
  clip we need out there... never repeat after me, sir." Shape: *scene → twist → reaction*.
- **149 · 8 · Cold Stone, cold-armed Danny** (26:27, 31s, 6 cuts, Sonnet + GURT). "I did lie, seven months" (GURT added it
  back) to "you little fricking cold-armed monkey." Shape: *friend exposes the other* (here: an ex-coworker).
- **150 · 8 · DoorDash "oops" apology** (30:44, 27s, both). "We just mistreated some dashers to the tune of $131.5 million.
  Oops." Theo: "sounds like the reindeers." Shape: *observational take, quotable capper*.
- **151 · 8 · Tony Xu, allegedly** (32:39, 33s, both). "And that's allegedly how you even pronounce his name." **Risk:**
  jokes about a named CEO (light, tied to a public settlement).
- **152 · 9 · Tight shit day** (33:38, 25s, 2 cuts, both). "We should have a tight shit day for the entire country" /
  "That's actually what I'm here to announce" / parents high-fiving with a T-S. Shape: *escalating riff, capped*.
- **153 · 8 · Cancel under a bridge** (39:57, 29s, 1 cut, both; GURT moved the opener to the program itself). "Meet me
  under a bridge if you want to cancel... our town doesn't even have a river in it." Shape: *absurd image → verdict*.
- **154 · 8 · Not on the apps** (41:02, 26s, 3 cuts, both). "You've looked in the window, you've been like, dear God...
  it's a bit of a sail rack over here." Shape: *self-roast*.
- **155 · 8 · Right at home in politics** (45:18, 11s, GURT). Theo admits he knows nothing about socialism, democracy,
  communism; the mayor: "You'd be right at home in politics." Shape: *roast in one line* (new).
- **156 · 7 · Fantasy team, Mitch McConnell** (48:07, 11s, both). "One guy's Mitch McConnell, who doesn't even know he's a guy
  anymore." **Risk:** named politician's age.
- **157 · 9 · Word lifeguards** (54:51, 15s, both). "Put a little buoy on you and help you get to the end of the sentence.
  Don't worry, brother. This is how it ends." Shape: *absurd image → strong verdict*.
- **158 · 8 · Pigeonhole: hope it's not sexual** (58:45, 16s, both; GURT's ending). "If it is, it's someone in your line of
  work who's been involved in it." Shape: *roast in one line*.
- **159 · 6 · PS41: gooners didn't vote** (1:02:03, 20s, both). The crew answers the wrong question. Filler.

**Rejected** (GURT): snow "structural problem" (Sonnet's, no payoff; the budget fact after it is misheard), Barramundi
(Sonnet's; same fish story as 148, smaller payoff), Branzino in the mob (same story), nurse put on her own chart
(unverified claim told as fact, no turn), Eric Adams care-bear stroller (rambling, accusation), "Trump to New York,
let's build" mock-up (interesting, no laugh), Netherlands PM "very handsome" (thin, inside the Gaza stretch),
lottery take (earnest).

**Scorer vs GURT** (Sonnet 5.5, 4 parts, 30k in / 65k cached / 34k out)
- **Found 11 of GURT's 14 blind picks (79%)**, up from ~65% in runs 4–9. Missed: queefish, the Cold Stone "seven months"
  line (cut out of its own splice), "right at home in politics".
- **Wrong reject:** queefish, called the "same fish sub-topic" as its Barramundi pick. Right dedupe, wrong winner: keep the
  bigger payoff (skill.md selection rule 7). Second time (runs 3–5 had the same pattern).
- **Same moment, better version:** Sonnet's won 3 (tight-shit day opened later and tighter, word lifeguards shorter,
  dating apps cut cleaner); GURT's won 3 (bridge opener on the program, pigeonhole ended on the burn not the Google
  tangent, Cold Stone kept the lie).
- **Precision:** 13 picks, 2 weak (snow, Barramundi). Rejected all policy and Gaza talk correctly.
- **Scores:** tight-shit day 7 (GURT 9), word lifeguards 8 (9), Tony/pigeonhole/bridge 7 (8). One point low again.
- **Dropped by code: none**, so the "unticked in Review" path is still untested.
- Mayor-as-straight-man picks (queefish, right at home) were the ones it missed: the joke is the guest's one dry line.

**Fixes this run**
1. None in code. Found: the Review window shows the copy loaded when the episode was clicked; GURT's chat edits only
   appear after clicking the episode again (`gui.py` `ReviewPage.open`). Toggle and approve re-read the file, so
   nothing was lost.

**Lessons**
1. `[theme]` A politician guest is mostly off-theme; the clips are the host's tangents and the guest's deadpan replies.
   Density dropped to ~10/hr anyway because Theo riffs constantly.
2. `[scorer]` Model misses a guest's one-line dry burn when the setup is the host's ramble (queefish, right at home).
3. `[scorer]` Model picks the weaker version of the same story (run 10: Barramundi over queefish).
