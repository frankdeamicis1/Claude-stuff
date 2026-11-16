#!/usr/bin/env bash
# Renders the RTX 3080 vs RTX 5070 reel end to end.
#   ./build.sh [workers]            (WORK_DIR=... with REUSE_VIDEO=1 redoes only the audio,
#                                    REUSE_CAPTIONS=1 keeps the rendered caption layer)
# out/rtx-3080-vs-5070.mp4   read-along captions + quiet bed (~-30 LUFS): record your voice over this one
# Needs: node + playwright (Chromium), python3 + numpy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
WORKERS="${1:-4}"
WORK="${WORK_DIR:-$(mktemp -d)}"
mkdir -p out "$WORK/frames" "$WORK/capframes"

echo "1/5 exporting audio cues"
node render.js cues "$WORK/cues.json"

echo "2/5 synthesizing soundtrack"
python3 make_audio.py "$WORK/cues.json" "$WORK/full.wav"

ENC="-c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p -profile:v high -level 4.1 -r 30 -g 60 -an"
if [ "${REUSE_VIDEO:-0}" = 1 ] && [ -f "$WORK/video.mp4" ] && [ -f "$WORK/video_cap.mp4" ]; then
  echo "3/5 + 4/5 reusing $WORK/video.mp4 and video_cap.mp4"
else
  echo "3/5 rendering frames ($WORKERS workers)"
  rm -f "$WORK"/frames/*.png
  LAYER=base node render.js all "$WORK/frames" "$WORKERS"
  # shellcheck disable=SC2086
  ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$WORK/frames/%05d.png" $ENC "$WORK/video.mp4"
  echo "4/5 read-along captions (transparent layer), overlaid on the picture"
  if [ "${REUSE_CAPTIONS:-0}" = 1 ] && [ -f "$WORK/capframes/00000.png" ]; then
    echo "  reusing caption frames"
  else
    rm -f "$WORK"/capframes/*.png
    LAYER=captions node render.js all "$WORK/capframes" "$WORKERS"
  fi
  # shellcheck disable=SC2086
  ffmpeg -y -hide_banner -loglevel error -i "$WORK/video.mp4" -framerate 30 -i "$WORK/capframes/%05d.png" \
    -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $ENC "$WORK/video_cap.mp4"
fi

echo "5/5 muxing audio"
# About -30 LUFS with peaks capped at -12 dBFS, so a normal speaking voice (-16 to -14 LUFS)
# sits roughly 14 dB on top.
measured=$(ffmpeg -hide_banner -nostats -i "$WORK/full.wav" -af ebur128=framelog=quiet -f null - 2>&1 | awk '/I:/ {v=$2} END {print v}')
gain=$(awk -v m="$measured" 'BEGIN {printf "%.2f", -30 - m}')
ffmpeg -y -hide_banner -loglevel error -i "$WORK/video_cap.mp4" -i "$WORK/full.wav" \
  -map 0:v -map 1:a -c:v copy \
  -af "volume=${gain}dB,alimiter=limit=0.25:attack=1:release=50:level=disabled" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest out/rtx-3080-vs-5070.mp4
echo "  rtx-3080-vs-5070: -30 LUFS (gain $gain dB)"

LAYER=base node render.js stills "$WORK/cover" 5.6
cp "$WORK/cover/t005.60.png" out/cover.png
echo "done -> out/rtx-3080-vs-5070.mp4, out/cover.png"
