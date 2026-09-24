#!/usr/bin/env bash
# Wrapper: ffmpeg/ffprobe z winget (nie ma ich w PATH). Użycie: ff.sh ffmpeg ... | ff.sh ffprobe ...
BIN="/c/Users/zonki/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin"
tool="$1"; shift
exec "$BIN/$tool.exe" "$@"
