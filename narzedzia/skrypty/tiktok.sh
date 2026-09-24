#!/usr/bin/env bash
# Konwersja dowolnego wideo do formatu TikTok/Reels/Shorts: 1080x1920, 30fps, H.264, AAC, -14 LUFS.
# Tło: rozmyta wersja kadru (bez czarnych pasów). Użycie: tiktok.sh wejscie.mp4 [wyjscie.mp4]
D="$(dirname "$0")"; IN="$1"; OUT="${2:-${1%.*}_tiktok.mp4}"
"$D/ff.sh" ffmpeg -y -i "$IN" -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,format=yuv420p[v]" \
-map "[v]" -map 0:a? -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
-c:a aac -b:a 192k -ar 48000 -af loudnorm=I=-14:TP=-1:LRA=11 "$OUT"
echo "Gotowe: $OUT"
