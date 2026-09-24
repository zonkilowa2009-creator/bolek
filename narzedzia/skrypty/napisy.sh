#!/usr/bin/env bash
# Transkrypcja (Whisper, polski) -> plik .srt obok wideo. Użycie: napisy.sh wideo.mp4 [model=medium]
PY="/c/Users/zonki/AppData/Local/Programs/Python/Python312/python.exe"
FFBIN="/c/Users/zonki/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin"
export PATH="$FFBIN:$PATH"
"$PY" -m whisper "$1" --language pl --model "${2:-medium}" --output_format srt --output_dir "$(dirname "$1")" --word_timestamps True --max_words_per_line 4
