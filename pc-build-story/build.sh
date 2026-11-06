#!/usr/bin/env bash
# Renders the PC build story end to end.
#   ./build.sh [workers]            (REUSE_VIDEO=1 WORK_DIR=... re-does only the audio)
# out/pc-build-story.mp4            read-along captions + quiet music bed + sound effects (record over this one)
# out/pc-build-story-sfx-only.mp4   read-along captions + sound effects only (add your own music)
# out/pc-build-story-clean.mp4      no captions + quiet music bed + sound effects
# Needs: node + playwright (Chromium), python3 + numpy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
WORKERS="${1:-4}"
WORK="${WORK_DIR:-$(mktemp -d)}"
mkdir -p out "$WORK/frames" "$WORK/capframes"

echo "1/5 exporting audio cues"
node render.js cues "$WORK/cues.json"

echo "2/5 synthesizing soundtrack"
python3 make_audio.py "$WORK/cues.json" "$WORK/full.wav" "$WORK/sfx.wav"

ENC="-c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p -profile:v high -level 4.1 -r 30 -g 60 -an"
if [ "${REUSE_VIDEO:-0}" = 1 ] && [ -f "$WORK/video.mp4" ] && [ -f "$WORK/video_cap.mp4" ]; then
  echo "3/5 + 4/5 reusing $WORK/video.mp4 and video_cap.mp4"
else
  echo "3/5 rendering frames ($WORKERS workers)"
  rm -f "$WORK"/frames/*.png "$WORK"/capframes/*.png
  LAYER=base node render.js all "$WORK/frames" "$WORKERS"
  # shellcheck disable=SC2086
  ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$WORK/frames/%05d.png" $ENC "$WORK/video.mp4"
  echo "4/5 rendering the read-along captions (transparent layer) and overlaying them"
  LAYER=captions node render.js all "$WORK/capframes" "$WORKERS"
  # shellcheck disable=SC2086
  ffmpeg -y -hide_banner -loglevel error -i "$WORK/video.mp4" -framerate 30 -i "$WORK/capframes/%05d.png" \
    -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $ENC "$WORK/video_cap.mp4"
fi

echo "5/5 muxing audio"
# Background audio for a voiceover: about -30 LUFS with peaks capped at -12 dBFS,
# so a voice recorded at normal level (-16 to -14 LUFS) sits roughly 14 dB on top.
TARGET_LUFS="${TARGET_LUFS:--30}"
for v in "video_cap:full:pc-build-story" "video_cap:sfx:pc-build-story-sfx-only" "video:full:pc-build-story-clean"; do
  IFS=: read -r vid src name <<< "$v"
  measured=$(ffmpeg -hide_banner -nostats -i "$WORK/$src.wav" -af ebur128=framelog=quiet -f null - 2>&1 | awk '/I:/ {v=$2} END {print v}')
  gain=$(awk -v t="$TARGET_LUFS" -v m="$measured" 'BEGIN {printf "%.2f", t - m}')
  ffmpeg -y -hide_banner -loglevel error -i "$WORK/$vid.mp4" -i "$WORK/$src.wav" \
    -map 0:v -map 1:a -c:v copy \
    -af "volume=${gain}dB,alimiter=limit=0.25:attack=1:release=50:level=disabled" \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "out/$name.mp4"
  echo "  $name: audio measured $measured LUFS, gain $gain dB"
done

LAYER=base node render.js stills "$WORK/cover" 9.0
cp "$WORK/cover/t009.00.png" out/cover.png
echo "done -> out/pc-build-story.mp4, out/pc-build-story-sfx-only.mp4, out/pc-build-story-clean.mp4, out/cover.png"
