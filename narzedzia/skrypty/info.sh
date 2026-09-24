#!/usr/bin/env bash
# Szybkie info o pliku: rozdzielczość, fps, długość, audio. Użycie: info.sh plik.mp4
D="$(dirname "$0")"
"$D/ff.sh" ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size,bit_rate -of default=nw=1 "$1"
