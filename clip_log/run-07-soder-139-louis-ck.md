## Run 7 — Soder Podcast EP 139 (guest Louis C.K.), 1h17m, 2026-09-30
**Theme:** `comedian-podcast` · **Posted:** _(pending)_ · **Layouts:** BLUR + TRACK for all; SPLIT none
(single close-ups) · **First run through the app** (queue → Sonnet → review → render), folder `Dan Soder\`.

**Episode read:** two comedians on death and family: Louis's father in a home who doesn't know him,
his mother's death, Dan's grandmother at 97, dogs (alive, dead, nearly killed), Pootie Tang, and two
"I embarrassed myself in front of a legend" stories (Dan → Louis, Louis → Seinfeld). Dense: a clip
every few minutes. Ads: 16:23–18:58 (Square, Zocdoc), 33:52–34:43 (Babbel), tour plug at 0:00.

**What the signals did:**
- Heatmap: 18:31 (1.00) and 34:43 (0.79) both land right after ad reads. Ad-skips again. The real
  replay content right after them (the tissue story, the dog Buddy) was strong anyway.
- Loudness: 3 spikes in 77 minutes. Flat mix; useless.
- Transcript: lowercase almost throughout. Whisper loops at 15:30 ("who's that at the end") and 38:38
  (a whole line twice), and it **drops curse words**: "shut the up", "what the", "hope he's not my
  mother". Caption fixes restore them as `****` where the punchline needs the word (clip 85).

**Tko's verdict:** _(pending)_. Tko re-ticked Sonnet's Carlin pick in the app before approving.

**Clips** (Shape = universal structure)
- **68 · 7 · Carlin's first words** (2:04, Sonnet's pick, re-ticked by Tko). Louis quoting how George
  Carlin opened a special with a joke instead of a hello. GURT had rejected it as someone else's joke.
- **69 · 8 · Kill dad in a sword fight** (8:25, 39s). "That's what every man truly wants: to kill his
  father in a sword fight" → the Jamaican nurse: "pick up your sword, mashed potatoes tonight if you
  win." Shape: *energy build, then a capper that tops it*.
- **70 · 8 · Mom as a moving exhibit** (12:25). "We took turns having her at home" → "we skinned her
  and glazed her... we had her slam dunk." Shape: *absurd image → strong verdict*.
- **71 · 8 · The snotty tissue** (19:29). Said everything to his father, cried, dad fell asleep;
  "I dropped my tissue... he's just watching me pick it up. The most humiliating moment."
- **72 · 8 · Grandma died during Shane's SNL** (22:19). "My grandma died" and back to the TV. "She's 97."
- **73 · 8 · I got a coupon for that** (28:45). Her son predicts she'll laugh, then call later:
  "some people go, I get to be hurt, I got a coupon for that." Shape: *observational take, quotable capper*.
- **74 · 9 · He's there to die** (32:47). The home calls about hearing aids: "he's there to fucking
  die... do you put the boombox over the plot?" Shape: *observational take, quotable capper*.
- **75 · 7 · Mosquito Hitler** (36:15, Sonnet's find).
- **76 · 9 · Murder-suicide, I'm out the door** (39:28). Talking through putting down Grandma's blind
  dog, escalating to "she's dead by the end of the story... murder suicide, I'm out the door."
  Shape: *energy build, then a capper that tops it*.
- **77 · 9 · Ticket: we got to do it again** (41:13). Dreamed his dead dog crawled out of the pile:
  "Ticket, you made it!" → "we immediately were like, we got to do it again." Shape: *scene → twist*.
- **78 · 9 · The dog knew it had to go** (42:55). Mom: "the dog will find her way out." A month later,
  a pickup truck. "You broke up the home I lived in, I'm on my way out." Shape: *scene → twist*.
- **79 · 8 · Rosie: three shots, edit one** (49:24). The dog runs a stranger's photo shoot.
- **80 · 8 · Dave Attell wants out of the scene** (51:27). Most comics pitch for more lines; Attell
  pitched ways to leave. Shape: *insider rule revealed*. (Whisper hears "David Tell".)
- **81 · 7 · The studio explained the milk scene** (58:41, Sonnet's find).
- **82 · 9 · Pootie Tang is a stinker** (60:05). Fired from his own movie, flown out to watch the
  recut alone; the projectionist: "I heard that's a stinker." Shape: *scene → twist → reaction*.
- **83 · 8 · The village is working** (68:10). Dan as an open micer tries slang on Louis: "the village
  is working." "What?" "I don't know what I'm talking about." Shape: *self-roast of the past self*.
- **84 · 8 · The cow goes July 3rd** (72:13). Louis hands Seinfeld a tag in a hallway; it kills on
  Letterman. Shape: *behind-the-scenes reveal*.
- **85 · 8 · Lincoln's dad pushed him off** (76:04). Comics should be meaner to young comics; Lincoln's
  father knocked him off the fence: "shut the **** up." Caption fix restores the dropped word.

**Rejected** (and why)
- 26:08 the crematorium kid ("I really hope he's not ******* my mother"): needed 77s. **Now possible
  with splicing**: it became the 32s test clip for the splice feature (not rendered as a clip).
- 7:17 "hand soup": the joke needs context from a minute earlier (old-age homes). Fails cold.
- 24:42 "dead mom, no guilt" (Sonnet 7): sincere, no joke.
- 46:29 Kleenex on Fifth Avenue, 47:26 "mental games like a housewife" (Sonnet 6–7): weaker dog bits.
- 35:28 "why I didn't smother the dog: inconvenience" (Sonnet 7): same story as 76, smaller payoff.
- 74:48 "do you remember this cow?" (Sonnet 7): the tail of 84's story; the joke itself is the payoff.

**Scorer vs GURT** (Sonnet 5.5, 4 parts; usage 27k in, 60k cached, 53k out)
- Agreed on 10 of GURT's 15. It also found the coupon line but cut it to 8s (dropped by code).
- Missed 69 (sword fight), 71 (tissue), 76 (murder-suicide), 84 (picked the cow story's tail).
  Pattern: it skips the **escalating riff** shape and takes the flat tail of a story.
- Kept 2 of its 11 finds (75, 81); Tko kept a third (68). Its rejects are again sincere talk at 7.
- It scored the 9s as 8s. Consistent with runs 3–6: about one point low on the best clips.

**Fixes this run** (Tko's notes after watching)
1. Last words sometimes cut. Whisper ends 17 of 18 last words exactly where the next word starts, so a
   fixed +0.3s guessed wrong. `splice.tail_end` now reads the audio.
2. Splicing and dead-air trimming built (`clipminer\splice.py`); Sonnet can propose cuts.
3. Hashtags: 10–15 per clip (Tko), plus #xybca #fyp #blowthisup #viral on every post, added in code.
   The four were missing from 68–85 because the app wasn't restarted; appended by hand.

**Lessons**
1. `[universal]` Whisper word end times are not where the sound stops. Cut from the audio.
2. `[universal]` Whisper drops curse words entirely ("shut the up"). Restore with a caption fix when the
   punchline needs it.
3. `[universal]` Long stories are now splice candidates, not rejects (crematorium 77s → 32s).
4. `[scorer]` Model misses escalating riffs (69, 76) and takes a story's tail (84).
5. `[theme]` Two comics on family death: ~14 clips/hour. The darkest material was the best.
6. `[workflow]` Restart the app after code changes before approving, or the old code renders.
