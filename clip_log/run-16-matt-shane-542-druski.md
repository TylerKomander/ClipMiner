## Run 16 — Matt and Shane's Secret Podcast "Ep 542 - Indulgences (feat. Druski)" (Matt McCusker, Shane Gillis; guest Druski), 67m, 2026-10-07
**Theme:** `comedian-podcast` · **Posted:** _(pending)_ · **Layouts:** BLUR + TRACK on all 18; no SPLIT (three people in one wide shot)
**First whole job through the app on style C** (captions, speaker colours, voice-following TRACK).
**GURT did not pick blind this run.** Three subagents that never saw Sonnet's list read `skill.md`, the index and the
whole reading file (duties: stories, one-liners, signals). GURT grouped their picks with Sonnet's by payoff line into
30 moments and built the cuts itself with a dry run of every clip. **No editor, skeptic or judge agents this run**,
and nobody listened to anything.

**Episode read:** Druski's dating show and its house (0:00–8:00), Lemaire's old room (8:09), the hosts' shoes and
money (10:17–13:40), Shane's drone and UFO witnesses (13:42–17:40), the inauguration, the MLK-voice speaker and Musk
(18:05–23:10), CTE and gambling promos (24:57–28:40), Notre Dame's loss and the LA fire benefit (28:45–33:15), the
Shannon Sharpe audio (33:30–37:30), Matt's Kinsey statistic and his brother (37:49–44:08), trains and the Diddy
parties (44:09–47:15), the smell of the house and the mics (56:40–59:10), Druski's auditions and little people
(59:36–1:04:55), Matt at the grocery store (1:04:57).
Ad 47:16–49:30 (PrizePicks, read in character); outro and plugs from 1:06:08.
Heatmap present: 0.78 at 49:11, 0.74 at 49:51 and 0.48 at 50:32 are ad-skip landings. Real: 1.00 at 1:01:59 (the
barbarian riff, 300), 0.63 at 45:08 (the Diddy question), 0.40 at 12:07 (girlfriend, 287), 0.36 at 1:04:00 (cannon,
299), 0.34 at 45:49 (296), 0.33 at 35:02 (earplugs, 293). Loudness usable here: 24 of 188 lines marked, nearly all
on real laughs.

**Transcript:** the app's transcript was lowercase with no punctuation from 0:00 to 44:09 (clean after), kept 104
curse words and had seven same-timestamp mash-ups (35:55, five between 41:46 and 44:08, 57:58). It had also dropped
whole spoken lines, not just curses. Two tests on the same audio:
| | as transcribed | `condition_on_previous_text=False` | + style hint (`hotwords`) |
|---|---|---|---|
| cased and punctuated | 44:09 onward only | patchy all the way | all the way |
| curse words kept | 104 | 143 | 234 |
| loops / mash-ups | 7 | 0 | 0 |
| time | ~12 min | 5m37s | ~6 min |
In the stretch the first transcript got right (45:00 on) the third one keeps the same number of curses (72 vs 74),
so the hint is not inventing them. **The third transcript replaced the job's `transcript.json` before the cuts were
built**, and `transcribe.py` now has both settings. Sonnet scored the first transcript; its picks were carried over
by time. Caption fixes: "versions" → virgins (284), "Kahurus" → Karhus (286, a guess from the M logo), "have." →
have Panama one day (290), "believe" → believe everything (289), "chomping" → jumping (300), "car/card" → cart (301).
**Faces:** one locked-off wide shot of three people for the whole episode (1920×1012; the ad is a separate two-shot).
No close-ups, so `faces.json` came out empty and TRACK fell back to jaw movement.

**Clips** (all = blind pickers and Sonnet; blind = blind pickers only; n/3 = how many blind pickers had it)
- **284 · 9 · 72 virgins, brand risk** (5:59, 35s, 2 cuts, all). "And you lived it." / "This podcast is a brand
  risk waiting to happen." **Risk:** religion. Shape: *scene → twist → reaction*.
- **285 · 8 · Roommate cracked the seal** (8:24, 24s, 3 cuts, all). "That's like when a cat pees in the basement…
  He cracked the seal on that room." Sonnet ran on to an in-joke. Shape: *friend exposes the other's habit*.
- **286 · 8 · Shoes: the whites dictate the culture** (10:19, 32s, blind 2/3). "You guys are going to be wearing
  Karhus in about 10 years. We the whites are dictating the culture these days." Shape: *observational take, capper*.
- **287 · 9 · Girlfriend must be here** (12:05, 38s, 2 cuts, blind 3/3). "What's your… girlfriend must be here. I
  always know when a girl's around." / "Naked girls dancing? No, I hate it." Shape: *dodge, caught live*.
- **288 · 9 · Drone is a plane** (13:43, 26s, 3 cuts, all). "This is a ******* plane." / "No, it's not. I knew this
  was going to happen." **Risk:** the N-word is audible after "plane". Shape: *proud reveal, instantly deflated*.
- **289 · 8 · Female UFO witness nullified** (17:00, 16s, 1 cut, all). "The prosecutor just hits him with their
  horoscope in the stand. Like, yes, I believe everything." Shape: *escalating riff, capped*.
- **290 · 8 · MLK voice at Chipotle** (19:59, 38s, 4 cuts, all; Sonnet stopped at "Panama one day"). "He says, yeah,
  no problem. One day the portions will be bigger." **Risk:** race. Shape: *escalating riff, capped*.
- **291 · 8 · CTE: once you get over the fear** (25:48, 19s, 1 cut, blind 1/3; GURT's call). "Gamble whenever you
  feel like it. ******* smash everything in your house." Shape: *absurd image → strong verdict*.
- **292 · 9 · Notre Dame over the fires** (29:20, 34s, blind 3/3). "Actually, Bill, I'll donate my own half to Notre
  Dame. **** the L.A. fire… Notre Dame needs a D-tackle." **Risk:** fire victims. Shape: *shameless confession*.
- **293 · 8 · I wear earplugs** (34:58, 16s, 1 cut, blind 2/3 and Sonnet). "A girl makes one noise. I go, shut the
  **** up… I wear earplugs." Shape: *shameless confession*.
- **294 · 9 · Jacking off to the research** (38:12, 34s, 2 cuts, blind 3/3). "What made you ******* look this up?" /
  "He stopped watching porn, now you're jacking off to ******* research." Shape: *friend exposes the other's habit*.
- **295 · 9 · Only straight guys in the world** (42:28, 16s, blind 1/3 and Sonnet). "We are Neo." / "I might be out.
  I've been in the room when dudes have jizzed." Shape: *self-justifying logic spiral*.
- **296 · 9 · Everyone left the party at 2 AM** (45:31, 20s, 1 cut, all). "I always left at 2 a.m. At 3 a.m. everyone
  busts their ***** out. It's like, how do you know?" **Risk:** opens on "Did you ever meet Diddy?", aimed at the
  guest. Shape: *observational take, quotable capper*.
- **297 · 9 · White part of the press tour** (57:10, 24s, 1 cut, blind 3/3). "This is the white part of your press
  tour, and you're going to come in and say we stink like dogs?" **Risk:** race. Shape: *roast in one line*.
- **298 · 8 · Walmart parking lot president** (59:55, 19s, blind 1/3 and Sonnet). "His dad was the president of the
  ******* Walmart parking lot." Sonnet ran 22s past it. Shape: *made-up fact, caught live*.
- **299 · 9 · Uber home or giant cannon** (1:00:57, 34s, 1 cut of 2m45s, blind 3/3). "Do you, like, get them an Uber
  home, or do you fire them out of a giant cannon?" **Risk:** "midget". Shape: *roast in one line*.
- **300 · 9 · Prince needs an entourage** (1:01:41, 19s, 1 cut, all). "You just see a midget under a bench…
  You're part of the squad now." / "They're actual people, guys." **Risk:** "midget". Shape: *scene → twist → reaction*.
- **301 · 9 · Grocery store tall guy** (1:04:57, 21s, 2 cuts, all). "I would have had to have left my family. I'm
  like, bro, they're yours now." Shape: *scene → twist → reaction*.

**Rejected** (GURT)
- *Sonnet picks, unticked:* good night to a guy 37:59 (a real 8; same stat as 294, which two of three blind pickers
  ranked higher; in Review unticked) · CTE spreads to your girlfriends 25:11 (replaced by 291: a domestic-violence
  joke with Tyson named).
- *Blind picks, dropped:* abstain / Epstein 2:09 (7: 3/3 found it, but the Epstein line is garbled and the tag is an
  under-21 joke) · o-line was hyped to see me 32:40 (7: the team is never named, capper garbled) · blind study,
  close your eyes 41:40 (the worst of the transcript, a sight gag, fourth on the Kinsey stat) · did you miss that
  train 45:01 (**risk:** puts the guest at the Diddy parties; 296 covers the topic) · horseplay / nut check 50:13
  (a named person and a specific allegation from testimony) · fake edit after the ad 47:00 (crosses the ad read) ·
  butt mic 58:35 (second on the mic smell, partly visual) · found by one picker only: what are you doing to help
  30:58, handjobs 51:50, not after they see this podcast 55:56, sip of water 1:05:49.

**Scorer vs GURT** (Sonnet 5.5, on the damaged first transcript)
- **Sonnet submitted 13.** 10 of its moments are in the final 18 (56%), **all 10 recut**; 1 more is a real 8 left
  unticked for the sub-topic; 1 was replaced by the other half of the same talk; 1 (Panama) was the first half of 290.
- **The 8 it missed or rejected:** girlfriend ("no payoff"), Notre Dame ("garbled"), press tour ("garbled"), shoes
  ("muddled"), cannon ("a setup with only a mild answer"), research (it built the other clip on that stat), the
  Chipotle capper (it stopped one beat early), CTE's second half. Five of the eight were found by all three blind
  pickers. Three of its rejections blame the transcript, on a transcript that really was broken.
- **Ran past the payoff** on four (roommate, Walmart by 22s, neo, drone); **never named the party** on 296.
- **Scored one point low again:** all 13 came in as 8 except one 9; eight of its ten kept picks finished at 9.
- Its credit line read "From Ep 542 - Indulgences with Druski.": the show's name was missing on all 13.
- Blind pickers: 22, 25 and 21 picks. **17 of 21 moments found by two or more blind pickers were kept or are a
  real 8**; of the 5 found by one alone, 1 was kept (291).

**What went wrong this run**
- **GURT has not listened to any clip.** Each reason in `review.json` carries a "Listen:" note. Most uncertain: 286
  (the brand name), 290 (four cuts, laughter gaps), 289 (ending, "everything" added by a fix), 285 and 288 (three
  cuts each), 297 (one cut of 55s).
- The editor, skeptic and judge passes of runs 14–15 were skipped. Nothing was checked by a second reader.
- 299 and 300 show as overlapping in Review (300 sits inside 299's cut-out stretch). No footage is shared.
- `picks-claude-sonnet-5-5.json` still indexes the first transcript; `review.json` is on the new one.

**Render check** (GURT looked at 8-frame strips of every TRACK file and one BLUR sheet; nobody listened)
- **TRACK is on the wrong person in a large share of frames, in most clips.** With no close-ups there were no faces
  to match to voices, and jaw movement parks the crop on Shane in the middle seat: Druski's lines play over Shane in
  286, 291 and 299, Matt's over Shane in 284 and 291 and over Druski in 300. 289 and 292 (Shane talking throughout)
  and 301 (Matt's story) look right. Judged from caption colour against who is framed, not from audio.
- **Fixed the same day with `seats`** (speaker 0 Druski 0.105, 1 Shane 0.452, 2 Matt 0.863 in `review.json`). All
  18 TRACK files were re-rendered through the real render code and replaced under the same numbers (Tko's yes). In
  10-frame strips, 17 show the person whose colour the caption has in every frame; 297 opens with about 6s on Matt
  while Druski talks, because `speakers.label` got those lines wrong. The voice labels themselves were right on all
  ten lines checked against the text.
- **Captions (style C) look right in both layouts:** Lilita One, 1–2 words, masked curses, one colour per voice that
  stays the same voice across clips (yellow Druski, green Shane, cyan Matt), white on short interjections. The spaced
  tokens of run 15 are gone ("37% OF").
- **BLUR is fine**, but three people in one wide shot are small in a 9:16 frame.
- Rendered lengths run 1–6s over the dry-run figure (287: 32s → 38.5s; 290: 33s → 38s). None passed 40s.

**Lessons**
- `[universal]` Whisper's lowercase stretches come from conditioning on the previous window; a short cased, punctuated
  style hint with conditioning off fixed casing, curses and loops on this episode, in half the time. One episode.
- `[universal]` A lowercase transcript has also lost whole lines, not only curses (the Karhus brand, "Panama one
  day", most of 38:45–38:58). Three of Sonnet's rejections were for "garbled" clips that are clean on a good transcript.
- `[universal]` On a show with one wide shot and no close-ups, voice-following TRACK has no faces to learn and falls
  back to jaw movement, which is wrong most of the time. Needs seats, not faces.
- `[scorer]` Sonnet rejects short dodge-caught-live and one-question roasts as "no payoff" / "mild answer" (287,
  299): both were 9s for all three blind pickers.
- `[scorer]` Sonnet's credit line drops the show's name when the video title has none.
- `[workflow]` Agreement between blind pickers held a third time (17 of 21 vs 1 of 5).
- `[theme]` Three comedians, no topic, a guest who plays straight man to the hosts: 16 clips/hour.
