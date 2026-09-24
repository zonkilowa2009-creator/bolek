#!/usr/bin/env bash
# Wyciąga N klatek podglądowych (do sprawdzenia filmu przez Claude'a Read-em). Użycie: klatki.sh wideo.mp4 [N=6]
D="$(dirname "$0")"; IN="$1"; N="${2:-6}"; OUTD="${TMPDIR:-/tmp}/klatki_$(basename "${IN%.*}")"; mkdir -p "$OUTD"
DUR=$("$D/ff.sh" ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
for i in $(seq 1 "$N"); do
  T=$(awk "BEGIN{print $DUR*($i-0.5)/$N}")
  "$D/ff.sh" ffmpeg -v error -y -ss "$T" -i "$IN" -frames:v 1 -vf scale=540:-1 "$OUTD/k$i.jpg"
done
echo "$OUTD"
