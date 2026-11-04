#!/usr/bin/env bash
# Renders the reel end to end: frames -> soundtrack -> MP4 (+ cover image).
#   ./build.sh [workers]
# Needs: node + playwright (Chromium), python3 + numpy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
WORKERS="${1:-4}"
WORK="${WORK_DIR:-$(mktemp -d)}"
mkdir -p out "$WORK/frames"

echo "1/4 exporting audio cues"
node render.js cues "$WORK/cues.json"

echo "2/4 synthesizing soundtrack"
python3 make_audio.py "$WORK/cues.json" "$WORK/audio.wav"

echo "3/4 rendering frames ($WORKERS workers)"
node render.js all "$WORK/frames" "$WORKERS"

echo "4/4 encoding"
ffmpeg -y -hide_banner -loglevel error \
  -framerate 30 -i "$WORK/frames/%05d.png" -i "$WORK/audio.wav" \
  -c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p \
  -profile:v high -level 4.1 -r 30 -g 60 -movflags +faststart \
  -af "loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.79:attack=2:release=60:level=disabled" -c:a aac -b:a 192k -ar 48000 \
  -shortest out/gpu-fps-reel.mp4

# cover frame (hook fully on screen)
node render.js stills "$WORK/cover" 2.4
cp "$WORK/cover/t002.40.png" out/cover.png

echo "done -> out/gpu-fps-reel.mp4, out/cover.png"
