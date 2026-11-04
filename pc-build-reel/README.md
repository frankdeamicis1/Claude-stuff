# PC build reel: "Your GPU draws a billion pixels a second"

An animated sales-funnel reel (1080×1920, 30 fps, 42.5 s) of cartoon Frank
building a PC, with a fun fact about GPU performance and FPS and a call to
action for San Diego locals at the end ("In San Diego? DM me FPS").

- `out/gpu-fps-reel.mp4`: the finished reel (H.264 + AAC, ready for Reels / TikTok / Shorts)
- `out/cover.png`: cover frame
- `script.md`: beat sheet, optional voiceover, post caption, DM reply, fact check

## How it's made

| File | What it does |
|---|---|
| `reel.html` | The whole animation as one SVG scene: character rig, PC case, GPU, the info graphics, and the timeline. `renderFrame(t)` draws any moment in time. Open it in Chrome to preview (space = play/pause). |
| `render.js` | Drives headless Chromium (Playwright) to capture every frame, in parallel. |
| `make_audio.py` | Synthesizes the music and sound effects with numpy, timed from the cue list the page exports. No licensed audio. |
| `build.sh` | Runs everything and encodes the MP4 with ffmpeg. |

```bash
./build.sh        # needs node + playwright, python3 + numpy, ffmpeg
```

To change text, timing, or the CTA keyword, edit `reel.html` and re-run `./build.sh`.
