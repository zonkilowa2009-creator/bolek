# Projekt: film ia — filmy TikTok/Reels + strony internetowe

Użytkownik pisze po polsku — odpowiadaj po polsku, krótko. Działaj samodzielnie, nie dopytuj o drobiazgi.

## Narzędzia (Windows, Git Bash)
- FFmpeg NIE jest w PATH → używaj `narzedzia/skrypty/ff.sh ffmpeg ...` / `ff.sh ffprobe ...`
- Python: `/c/Users/zonki/AppData/Local/Programs/Python/Python312/python.exe` (whisper, moviepy, pysubs2, scenedetect, opencv) — wywołuj przez `python -m`
- Node 24 + Remotion w `my-video/` (Studio: preview_start `remotion-studio`, port 3000)
- RIFE (interpolacja klatek / slow-motion): `narzedzia/rife-ncnn-vulkan-*.zip` (rozpakuj przy pierwszym użyciu)

## Skrypty pomocnicze (`narzedzia/skrypty/`)
| skrypt | co robi |
|---|---|
| `info.sh plik` | rozdzielczość, fps, długość, audio |
| `tiktok.sh in [out]` | → 1080x1920, 30fps, H.264 CRF18, rozmyte tło, głośność -14 LUFS |
| `napisy.sh wideo [model]` | Whisper PL → .srt (max 4 słowa/linia) |
| `klatki.sh wideo [N]` | N klatek podglądu → przeglądaj je narzędziem Read, żeby OCENIĆ film przed oddaniem |

## Standard filmów pionowych (TikTok/Reels/Shorts)
- 1080x1920, 30 fps, H.264 yuv420p, AAC 48 kHz, `-movflags +faststart`, głośność -14 LUFS
- Hook w pierwszych 1–2 s (tekst na ekranie + ruch); cięcie co 1,5–3 s; długość 15–45 s
- Napisy: duże, pogrubione, 2–4 słowa, podświetlanie aktualnego słowa, w strefie bezpiecznej
  (NIE w dolnych ~380 px i prawych ~140 px — tam jest UI TikToka; góra ~150 px też zajęta)
- Muzyka pod lektorem ściszona (ducking ~ -18 dB), lektor ElevenLabs
- Zdjęcia statyczne zawsze z ruchem (Ken Burns / zoom 1.0→1.1), przejścia krótkie (≤ 8 klatek)
- Po renderze ZAWSZE: `info.sh` + `klatki.sh` i obejrzyj klatki (ucięty tekst, czarne pasy, literówki)
- Gotowe pliki nazywaj opisowo: `temat_TIKTOK_vN.mp4`; wyniki Remotion → `my-video/out/`

## Remotion
- Przed pracą załaduj skill `remotion:remotion-best-practices` (i `remotion-captions` do napisów)
- Render: `cd my-video && npx remotion render <Kompozycja> out/nazwa.mp4 --codec h264 --crf 18`
- Transkrypcja do napisów Remotion: `node sub.mjs <plik>` (whisper.cpp)

## Strony internetowe
- Nowe strony w `strony/<nazwa>/` (statyczny HTML/CSS/JS, chyba że potrzebny framework)
- Przed projektowaniem załaduj skill `impeccable` lub `design-taste-frontend` (unikaj „szablonowego” wyglądu)
- Podgląd: preview_start `strona-statyczna` (serwuje `strony/` na porcie 5173), potem sprawdź
  konsolę, widok mobilny 375 px (resize_window) i tryb ciemny; zrób zrzut ekranu jako dowód
- Wymagania: responsywność (mobile-first), semantyczny HTML, alt w obrazach, kontrast WCAG AA,
  meta viewport + opis + og:image, obrazy WebP z `loading="lazy"`, brak poziomego scrolla
- Publikacja do podglądu dla użytkownika: narzędzie Artifact

## Git
- Duże pliki wideo/audio (>50 MB) nie do repo; `my-video/out/` i `node_modules/` są ignorowane
