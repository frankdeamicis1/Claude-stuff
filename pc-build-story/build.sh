#!/usr/bin/env bash
# Renders the PC build story end to end: frames -> soundtrack -> two MP4s (+ cover).
#   ./build.sh [workers]            (REUSE_VIDEO=1 WORK_DIR=... re-does only the audio)
# out/pc-build-story.mp4          music bed + sound effects, kept quiet (~-30 LUFS) for a voiceover
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

if [ "${REUSE_VIDEO:-0}" = 1 ] && [ -f "$WORK/video.mp4" ]; then
  echo "3/4 reusing $WORK/video.mp4"
else
  echo "3/4 rendering frames ($WORKERS workers)"
  node render.js all "$WORK/frames" "$WORKERS"
  ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$WORK/frames/%05d.png" \
    -c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p \
    -profile:v high -level 4.1 -r 30 -g 60 -an "$WORK/video.mp4"
fi

echo "4/4 muxing audio"
# Background audio for a voiceover: about -30 LUFS with peaks capped at -12 dBFS,
# so a voice recorded at normal level (-16 to -14 LUFS) sits roughly 14 dB on top.
TARGET_LUFS="${TARGET_LUFS:--30}"
for v in "full:pc-build-story" "sfx:pc-build-story-sfx-only"; do
  IFS=: read -r src name <<< "$v"
  measured=$(ffmpeg -hide_banner -nostats -i "$WORK/$src.wav" -af ebur128=framelog=quiet -f null - 2>&1 | awk '/I:/ {v=$2} END {print v}')
  gain=$(awk -v t="$TARGET_LUFS" -v m="$measured" 'BEGIN {printf "%.2f", t - m}')
  ffmpeg -y -hide_banner -loglevel error -i "$WORK/video.mp4" -i "$WORK/$src.wav" \
    -map 0:v -map 1:a -c:v copy \
    -af "volume=${gain}dB,alimiter=limit=0.25:attack=1:release=50:level=disabled" \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "out/$name.mp4"
  echo "  $name: measured $measured LUFS, gain $gain dB"
done

node render.js stills "$WORK/cover" 9.0
cp "$WORK/cover/t009.00.png" out/cover.png
echo "done -> out/pc-build-story.mp4, out/pc-build-story-sfx-only.mp4, out/cover.png"
