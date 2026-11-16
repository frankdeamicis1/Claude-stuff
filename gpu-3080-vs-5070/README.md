# RTX 3080 vs RTX 5070: "closer than you'd think"

An animated reel (1080×1920, 30 fps, 80.9 s) for Frank to voice over, with
read-along captions. It explains why a 2020 RTX 3080 and a 2025 RTX 5070 are
close in raw raster (about 18% apart at 1440p), shows that a used 3080 is about
half the price of a new 5070 ($469 on eBay vs $909 on Amazon, mid-November 2026)
and the price per FPS ($5.72 vs $9.47), then ends on "In San Diego County? DM me."

- `out/rtx-3080-vs-5070.mp4`: read-along captions + quiet background (about -30 LUFS). Record over this one.
- `out/cover.png`: cover frame
- `script.md`: word-for-word voiceover with start times, captions, and a fact check with sources

## How it's made

Same pipeline and avatar rig as `../pc-build-story`.

| File | What it does |
|---|---|
| `compare.html` | The whole animation as one SVG scene. The `VO` list (each line's start time + words) drives the karaoke captions and when the graphics pop. `PRICE_OLD` / `PRICE_NEW` set the prices in the voiceover, the bars and the price-per-FPS math. Open it in Chrome to preview (space = play/pause). `?layer=base` / `?layer=captions` render the two layers separately. |
| `render.js` | Captures every frame with headless Chromium (Playwright), in parallel. |
| `make_audio.py` | Synthesizes the music bed and sound effects with numpy. No licensed audio. |
| `build.sh` | Renders the picture and the caption layer, overlays them, and encodes the MP4 with ffmpeg. |

```bash
./build.sh        # needs node + playwright, python3 + numpy, ffmpeg
```
