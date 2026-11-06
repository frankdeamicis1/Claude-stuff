# PC build story: "I handle it, start to finish"

An animated reel (1080×1920, 30 fps, 59 s) for Frank to voice over. Cartoon
Frank takes a gaming PC from plan to hand-off (plan, buy parts, build,
stress test, hand it to a happy customer) and ends on "In San Diego? DM me."

- `out/pc-build-story.mp4`: music bed + sound effects, mixed quiet for a voiceover
- `out/pc-build-story-sfx-only.mp4`: sound effects only
- `out/cover.png`: cover frame
- `script.md`: word-for-word voiceover with timings, captions, DM reply

## How it's made

Same pipeline as `../pc-build-reel`, and the same avatar rig and PC art.

| File | What it does |
|---|---|
| `story.html` | The whole animation as one SVG scene. `renderFrame(t)` draws any moment. Open it in Chrome to preview (space = play/pause). |
| `render.js` | Captures every frame with headless Chromium (Playwright), in parallel. |
| `make_audio.py` | Synthesizes the music bed and sound effects with numpy from the page's cue list. No licensed audio. |
| `build.sh` | Runs everything and encodes both MP4s with ffmpeg. |

```bash
./build.sh        # needs node + playwright, python3 + numpy, ffmpeg
```
