# PC build story: "I handle it, start to finish"

An animated reel (1080×1920, 30 fps, 60 s) for Frank to voice over, with read-along captions so the voice lines up. Cartoon
Frank takes a gaming PC from plan to hand-off (plan, buy parts, build,
stress test, hand it to a happy customer) and ends on "In San Diego? DM me."

- `out/pc-build-story.mp4`: read-along captions + music bed + sound effects, mixed quiet (about -30 LUFS, peaks under -12 dBFS). Record over this one.
- `out/pc-build-story-sfx-only.mp4`: read-along captions + sound effects only
- `out/pc-build-story-clean.mp4`: no captions
- `out/cover.png`: cover frame
- `script.md`: word-for-word voiceover with timings, captions, DM reply

## How it's made

Same pipeline as `../pc-build-reel`, and the same avatar rig and PC art.

| File | What it does |
|---|---|
| `story.html` | The whole animation as one SVG scene. `renderFrame(t)` draws any moment. The `VO` list (each line's start time + words) drives the karaoke captions, the cartoon mouth and the on-screen pops. Open it in Chrome to preview (space = play/pause). `?layer=base` / `?layer=captions` render the two layers separately. |
| `render.js` | Captures every frame with headless Chromium (Playwright), in parallel. |
| `make_audio.py` | Synthesizes the music bed and sound effects with numpy from the page's cue list. No licensed audio. |
| `build.sh` | Renders the picture and the transparent caption layer, overlays them, and encodes all three MP4s with ffmpeg. |

```bash
./build.sh        # needs node + playwright, python3 + numpy, ffmpeg
```
