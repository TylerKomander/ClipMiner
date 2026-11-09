## Run 20 — Atlanta S02E01 "Alligator Man" (TV episode, local 4K HDR file), 35m, 2026-11-05 → 11-09
**Theme:** `movie-recap` · **Posted:** 348 to The-Theatre-Goer (YouTube), 2026-11-09 · **Layout:** BAND, speaker-following
**Picked by:** GURT by hand, three versions; Tko judged each. The app's `recap()` (Sonnet) has never run on a film.
This is the only movie-recap run so far: every rule it taught is one data point.

**Inputs used:** `transcript.json` (Whisper) for exact quotes and times, `reading.txt` to scan, and the episode's own
SDH track `subs_sdh.srt` for **names and who is speaking** (it prints `WILLY:` before a line; Whisper doesn't).
Whisper under the film's audio missed 136 of ~3,240 subtitle words, all grunts and background lines. One line was
timed 5s early ("I'm the alligator man"): a moment that runs long for its few words means a timing slip, check it.

**The episode in one sentence (the main thread):** Earn, broke and homeless, is sent by his cousin Al to check on
Uncle Willy, who has an alligator and a police standoff on his hands; Earn gets Willy out of it, ends up holding
Willy's gun, and Willy gets away. Side plots in the same episode: Earn's storage unit, Tara/"Regina", Al's friend
Tracer just out of jail, Darius's philosophy. **None of them are in the recap that passed.**

### The three versions
- **346 · v1 · 55s, 16 moments · Tko: told the plot, flat.** Picked for plot coverage: mostly half-lines that move
  the story ("let that alligator loose", "probation. I can't go to jail") and few complete jokes. Fixed crop lost
  faces. Lesson: covering the plot is the floor, not the bar.
- **347 · v2 · 89s, 23 moments · Tko: "way better… actually tells the story", but cut what doesn't fit.** Added the
  laughs, but also the side plots (Tara/"Regina" ×2, storage unit "they coming", Florida Man set-up, Tracer and the
  landlord at the end) and serious beats. Lesson: **follow the main thread only; a funny side-plot line still goes;
  when a beat can be told by a laugh or by a straight line, take the laugh.** Lines were also clipped at the cut
  (now a 0.35s hold after every moment).
- **348 · v3 · 15 stretches (16 picks, two adjacent merged), 89s of speech, 97s rendered · Tko: "That's really
  good." The target shape.** Starts at the call that starts the main thread (13:50, the first 13 minutes are side
  plot), nearly every moment a laugh on the main thread.

Before v3, a 4-drafter / 3-judge panel's synthesis **failed a cold-stranger retell**: no hook in the first line, and
the gun appeared at the end with nothing setting it up. The fix was the line that hands it over (moment 12). That
panel and v1/v2's cost ~1.3M agent tokens: never again for one recap.

### 348 moment by moment (role · why it's in)
| # | At | Len | Lines | Role |
|---|---|---|---|---|
| 1 | 13:50 | 8.6s | "Yo, I need you to go over to Willie's. Man, Yvonne done called here screamin', sayin' he done kidnapped her and shit. She done call the police?" | **Hook + mission.** States the situation in the first line: where we're going and why. |
| 2 | 15:31 | 7.6s | "Y'all can't sleep here. We're not staying here. Where's Yvonne? Bitch, you better hope it ain't the police." | Arrival, laugh. Introduces Willy by his own voice. |
| 3 | 16:27 | 9.9s | "Well, I must have kidnapped that bitch in 1974 because she ain't been a kid in 45 years. She in there? No, and don't go in there. The alligator's in there. What?" | Laugh, then the **twist** that names the episode. |
| 4 | 17:02 | 7.6s | "I would say nice to meet you, but I don't believe in time as a concept, so I'll just say we always met." | Pure laugh (Darius meets Willy). Allowed: a stranger gets it with no scene before. |
| 5 | 18:04 | 4.7s | "Was that alligator here when I was staying here? Who, Coach? Yeah." | Laugh: the alligator has a name. |
| 6 | 18:32 | 5.0s | "No, that's the wrong house. We're not domestic. We're not even married. We didn't call, so we good." | **Escalation** (police at the door) told by a laugh. |
| 7–8 | 19:14 | 12.3s | "…then I'll let that alligator loose and see what they do about that. You don't have an alligator. Yes, he do. I'm the alligator man, okay?" | The threat; the **title line**. |
| 9 | 19:50 | 2.7s | "That's my uncle. He's a veteran. Please don't shoot him." | **Stakes**: guns drawn. The one straight line in the middle. |
| 10 | 20:31 | 4.1s | "This nigga got a full-grown caiman in here, surrounded by chicken carcasses." | Laugh. |
| 11 | 20:44 | 4.6s | "A shootout? Nigga, I'm not crazy. I'm not Florida, man." | Laugh: Willy refuses to come out. |
| 12 | 21:08 | 3.3s | "You homeless, Earn. You don't even have a mirror to look at yourself." | Roast; tells a stranger who Earn is in one line. |
| 13 | 24:25 | 3.9s | "You're gonna need this in the music business. Take it." | **Set-up for the ending**: Willy hands Earn the gun. Added after the cold retell failed. |
| 14 | 27:02 | 2.1s | "How Willie? Not in jail." | **Outcome**: Willy got away. |
| 15 | 27:34 | 7.3s | "It's a gun. Willie gave it to me. Nigga, you took it. Yeah, you told me to help him. I was helping him." | Payoff of 13, laugh. |
| 16 | 27:43 | 5.0s | "You're holding a gun for a nigga while 12 outside? That shit gold." | **Button**: the last line is a laugh. |

**Scene changes, each set up by the moment before:** Al's call sends us to Willy's (1→2); "The alligator's in
there" sets up every alligator line after it; the police at the door (6) are set up by "hope it ain't the police" (2)
and "She done call the police?" (1); the gun (15–16) is set up by 13; "How Willie?" (14) is back at Al's, set up by
1 (Al sent him).

**Post text:** "He only went to check on his uncle. Nobody mentioned the alligator." A teaser, not the ending.

### Lessons
- `[theme]` Start where the main thread starts, not at minute 0. Earlier scenes come in only if a stranger needs
  them to know who the main character is (Atlanta: no; moment 12 does it in one line).
- `[theme]` The funny lines carry the story: in 348 only moments 1, 9, 13 and 14 are straight lines; every other
  one is a laugh that also moves the plot.
- `[theme]` Anything that pays off at the end (an object, a person) needs a moment that sets it up.
- `[theme]` The first line must be the hook: a mission, a threat or a strange situation, stated in words.
- `[theme]` A cold-stranger retell (read only the quotes, retell who/what/how it ends) catches what reading the film
  doesn't: you know the scenes, a stranger doesn't.
- `[universal]` The SDH subtitle track is the best source for names and speakers; Whisper is the source for exact
  quote text and timing.

### Blind test of the method (2026-11-09)
Two Haiku drafters got only the movie-recap profile with every Atlanta detail stripped, the reading file and the SDH
subtitles; a fresh reader retold each draft from its quotes; a judge scored it against 348.
- **Round 1: 3/10, 3/10.** Moments cut at reading-file row wraps before the punchline; one speech split into two
  moments; the straight line taken over the funny reply beside it; the gun with no set-up; the ending from a side
  scene; weaknesses written in the notes and shipped. Also a pace bug (runtime, not speech) asked for ~40s.
- **Round 2 (method rewritten): 6/10, 5/10.** Both found the hook exchange and the gun hand-over unprompted. Left:
  moments opening on an answer, reactions counted as laughs, speakers borrowed from the wrong subtitle cue, a failed
  gate shipped as a "known gap". Root cause: the model grades itself. Fix in the process, not the wording: a fresh
  reader with the full text of every moment.
