# README brand assets

| File | Used by | How it's made |
|---|---|---|
| `clipminer-wordmark.png` | README hero | Generated — `openai/gpt-image-2.5-sunburst` via OpenRouter, 2304×768, high. Prompt below. |
| `pipeline.png` | README "What it does" banner | Generated, 1920×640, high. Text-free icons for download → transcribe → score → review → render. |
| `social-preview.png` | Repo **Settings → General → Social preview** (1280×640) | Generated. **Not** referenced by the README — upload it by hand. |

Brand tokens: phosphor green `#00FF88` (the app's own accent, `GREEN` in `clipminer/gui.py`), bright core
`#7DFFC0`, dim ink `#9BF5C4`, background `#000000`.

## Image-gen prompt — `clipminer-wordmark.png` (hero, wide, on black)

> Wide banner logotype reading "CLIPMINER" in a single line. Blocky pixelated bitmap typeface — chunky, low-resolution
> pixel letterforms like the VT323 / classic CRT-terminal / DOS-BIOS font, monospaced, uppercase, slightly wide
> letter-spacing. The letters glow in phosphor green (#00FF88) with a brighter #7DFFC0 core and a soft outer
> bloom/halo, like illuminated text on an old CRT monitor. Pure black (#000000) background. Subtle horizontal CRT
> scanlines across the whole image, very faint screen vignette in the corners, and a slight red/cyan
> chromatic-aberration fringe on the letter edges. Crisp, legible, centered, with generous padding around the word.
> Retro-futuristic terminal aesthetic, flat 2D (no 3D bevel, no perspective), no reflections, no extra text or
> icons. Aspect ratio 3:1 (wide). High resolution. Spell the single word exactly, letter for letter: C-L-I-P-M-I-N-E-R.

## Image-gen prompt — `pipeline.png` (banner, text-free)

> A wide, ultra-minimal retro-CRT banner illustration on a pure black (#000000) background, showing a left-to-right
> pipeline of five glowing phosphor green (#00FF88, with a brighter #7DFFC0 core) wireframe pixel-art icons connected by
> simple glowing arrows: (1) a wide landscape video frame with a play triangle in its center, (2) an audio waveform
> made of vertical bars, (3) a five-pointed star, (4) a checkbox with a check mark in it, (5) a tall vertical
> smartphone outline whose screen shows a small head-and-shoulders silhouette with two short horizontal bars beneath
> it. All icons rendered as flat 2D phosphor-glow line art with soft bloom, evenly spaced in a single horizontal row,
> centered vertically, generous padding. Faint horizontal CRT scanlines, subtle corner vignette, slight chromatic
> aberration. Absolutely no text, no words, no letters, no numbers anywhere. Aspect ratio about 3:1 wide.
> Retro-futuristic terminal aesthetic.

## GitHub social-preview card — `social-preview.png` (1280×640)

> A 1280×640 social card on a pure black (#000000) CRT screen. Centered, the blocky pixelated bitmap-font logotype
> "CLIPMINER" glowing in phosphor green (#00FF88) with a brighter #7DFFC0 core and soft bloom. Below it, in a smaller
> thin monospaced terminal font in dim green (#9BF5C4), one short tagline line reading exactly: "LONG VIDEO IN. CLIPS OUT.".
> Faint horizontal CRT scanlines, subtle corner vignette, slight red/cyan chromatic aberration on edges. Lots of
> negative space, balanced composition, flat 2D retro-terminal aesthetic, no other text, no logos, no icons. Spell
> the title exactly: C-L-I-P-M-I-N-E-R.

**This file is not referenced by the README.** The repo owner uploads it:
repo **Settings → General → Social preview → Upload an image…**
