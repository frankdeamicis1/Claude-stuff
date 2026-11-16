# RTX 3080 vs RTX 5070: voiceover script + captions

59.5 s, 1080×1920, for Reels and TikTok. Why a 2020 RTX 3080 and a 2025 RTX 5070
are close in raw raster, then the CTA: "In San Diego County? DM me."

## The file

`out/rtx-3080-vs-5070.mp4`: record over this one. Read-along captions + quiet background (about -30 LUFS).

## How to record

Same as the last one: read the captions, and say the word that lights up yellow. The CTA has no captions; "IN SAN DIEGO COUNTY?", "DM ME" and the lines under it pop up on the word you say them. You can also record one line at a time; start times are below.

| Starts | On screen | You say |
|---|---|---|
| 0:00 | RTX 3080 (2020) vs RTX 5070 (2025) | An RTX 3080 from 2020 is closer to a 5070 than you'd think. |
| 0:07 | Raw raster, 1440p: 82 FPS vs 96 FPS, "only +18%" | 4 and a half years newer, and it's only about 18 percent faster in raw raster. |
| 0:14 | More cores vs faster cores → 29.8 vs 30.9 TFLOPS | The 3080 has more cores. The 5070 has fewer, but runs them faster. Multiply it out, it's basically the same math. |
| 0:25 | Bandwidth vs cache: 760 vs 672 GB/s, 5 MB vs 48 MB | The 3080 even has more memory bandwidth. The 5070 makes up for it with almost 10 times the cache. |
| 0:34 | Chips to scale: 628 mm² vs 263 mm² | And the 5070 chip is less than half the size, on a newer process. |
| 0:40 | Where the 5070 pulls ahead: frame gen, +2 GB, -70 W | Where the 5070 pulls ahead is frame generation, 2 more gigs of VRAM, and 70 watts less power. |
| 0:49 | IN SAN DIEGO COUNTY? → DM ME → your budget + what you play | In San Diego County? DM me your budget and what you play. I'll tell you which one I'd go with. |

The background audio peaks are capped at -12 dBFS, so a normal speaking voice sits about 10 dB or more on top. Leave the original sound at 100% and talk normally.

## Instagram caption

```
In San Diego County and trying to decide between a used RTX 3080 and an RTX 5070? DM me.

The 5070 is 4.5 years newer, but in raw raster it's only about 18% faster (Tom's Hardware, 1440p Ultra, no upscaling or frame gen).

Why it's that close:
- Same math: 8,704 cores at 1.71 GHz vs 6,144 cores at 2.51 GHz. About 30 TFLOPS either way.
- The 3080 has more memory bandwidth (760 vs 672 GB/s). The 5070 has almost 10x the cache (48 MB vs 5 MB).
- The 5070's chip is less than half the size, on a newer process.

Where the 5070 wins: DLSS 4 multi frame gen, 12 GB of VRAM instead of 10, and 70 W less power.

DM me your budget and what you play, and I'll tell you which one I'd go with.

#sandiego #gamingpc #pcbuild #rtx3080 #rtx5070
```

Set the post's location tag to San Diego so it gets shown to people nearby.

## TikTok caption

```
In San Diego County? DM me your budget and what you play. A 3080 vs a 5070 is closer than you'd think.

#sandiego #gamingpc #rtx3080 #rtx5070
```

Check that your TikTok message settings let people who don't follow you send you a DM.

## Fact check

- **Raster gap:** Tom's Hardware GPU Benchmarks Hierarchy (2026 retest, rasterization, native, no upscaling or frame gen), 1440p Ultra: RTX 5070 96.4 fps, RTX 3080 82.0 fps, so 96.4 / 82.0 = 1.18, about 18%. At 1080p Ultra it's 132.6 vs 111.6 (about 19%), and at 4K Ultra 54.3 vs 43.9 (about 24%). Other reviews line up: TechPowerUp measured the 5070 22% faster than the RTX 4070 at 1440p, and launch roundups had the RTX 4070 on par with the RTX 3080 10GB.
- **Release dates:** RTX 3080 September 2020 ($699 launch price), RTX 5070 March 2025 ($549). That's about 4.5 years apart.
- **Cores x clock:** 3080 10GB: 8,704 CUDA cores, 1.71 GHz boost, 29.8 TFLOPS FP32. 5070: 6,144 CUDA cores, 2.51 GHz boost, 30.9 TFLOPS (6,144 × 2 × 2.512 GHz).
- **Memory:** 3080: 10 GB GDDR6X, 320-bit, 760 GB/s, about 5 MB L2. 5070: 12 GB GDDR7, 192-bit, 28 Gbps, 672 GB/s, 48 MB L2 (one source lists 41 MB, but 48 MB is the widely reported figure).
- **Chips:** GA102 (3080): 628 mm², 28.3B transistors, Samsung 8nm. GB205 (5070): 263 mm², 31.1B transistors, TSMC 4N. 263 / 628 = 42%, which is "less than half the size".
- **Power:** 320 W vs 250 W total graphics power, so 70 W less.
- **Frame gen:** DLSS 4 Multi Frame Generation is RTX 50-series only; RTX 30 cards don't get DLSS frame generation. NVIDIA's CES 2025 "RTX 5070 = 4090 performance" claim was made with multi frame gen on.
- **The 3080 in the video is the 10 GB model.** There's also a rarer 12 GB version with 8,960 cores and a 384-bit bus.
- **No prices on screen on purpose.** Used and new GPU prices moved a lot in 2026, so the video only compares specs and benchmarks.

## Notes

- To change a line, edit `VO` in `compare.html` (each line's start time + text). The captions and the on-screen timing follow it. Then run `./build.sh`.
- Cartoon you keeps his mouth shut. His arms stay at his sides, except a point-up when a key graphic lands (+18%, same math, 10x cache, DM ME).
