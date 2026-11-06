#!/usr/bin/env bash
# Renders the PC build story end to end: frames -> soundtrack -> two MP4s (+ cover).
#   ./build.sh [workers]
# out/pc-build-story.mp4          music bed + sound effects (made to sit under a voiceover)
# out/pc-build-story-sfx-only.mp4 sound effects only, for adding your own music
# Needs: node + playwright (Chromium), python3 + numpy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
WORKERS="${1:-4}"
WORK="${WORK_DIR:-$(mktemp -d)}"
mkdir -p out "$WORK/frames"

echo "1/4 exporting audio cues"
node render.js cues "$WORK/cues.json"

echo "2/4 synthesizing soundtrack"
python3 make_audio.py "$WORK/cues.json" "$WORK/full.wav" "$WORK/sfx.wav"

echo "3/4 rendering frames ($WORKERS workers)"
node render.js all "$WORK/frames" "$WORKERS"

echo "4/4 encoding"
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$WORK/frames/%05d.png" \
  -c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p \
  -profile:v high -level 4.1 -r 30 -g 60 -an "$WORK/video.mp4"
# quieter than a finished reel on purpose: room for your voice on top
for v in "full:pc-build-story:-20" "sfx:pc-build-story-sfx-only:-22"; do
  IFS=: read -r src name lufs <<< "$v"
  ffmpeg -y -hide_banner -loglevel error -i "$WORK/video.mp4" -i "$WORK/$src.wav" \
    -map 0:v -map 1:a -c:v copy \
    -af "loudnorm=I=$lufs:TP=-2:LRA=11,alimiter=limit=0.79:attack=2:release=60:level=disabled" \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "out/$name.mp4"
done

node render.js stills "$WORK/cover" 9.0
cp "$WORK/cover/t009.00.png" out/cover.png
echo "done -> out/pc-build-story.mp4, out/pc-build-story-sfx-only.mp4, out/cover.png"
