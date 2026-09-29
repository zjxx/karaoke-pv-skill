# Karaoke PV

A reusable Codex skill and small local toolset for making Japanese song PVs
singable: preserve the video, analyze vocal timing, correct lyrics and romaji,
split readable phrases around reviewed pauses, optionally create an instrumental
stem, and burn SRT/ASS subtitles into a preview or final MP4.

The skill is designed for **evidence-first drafts**. ASR word timestamps help find
entry points and candidate gaps, but they are not forced alignment. Japanese song
lyrics, kanji readings, elongated vowels, breath gaps and repeated choruses still
need listening review. The timeline records whether each cue came from ASR, an
estimate, or audio review.

## Install the skill

Copy `skills/karaoke-pv` into your Codex skills directory:

```powershell
Copy-Item -Recurse skills/karaoke-pv "$env:CODEX_HOME/skills/karaoke-pv"
```

Then invoke it with `$karaoke-pv`, or describe the PV/subtitle task naturally.

## Use the local helpers

The helpers use Python's standard library except for the optional transcription
dependency. FFmpeg with `libass` and `ffprobe` is required for rendering.

```powershell
python -m pip install faster-whisper
python skills/karaoke-pv/scripts/transcribe.py vocals.wav `
  --output work/asr.json --cache-dir work/models
python skills/karaoke-pv/scripts/subtitles.py examples/timeline.json `
  --output-dir work/subtitles --draft
python skills/karaoke-pv/scripts/render.py pv.mp4 work/subtitles/romaji.ass `
  work/preview.mp4 --start 80 --duration 25
```

Read `skills/karaoke-pv/references/timeline.md` before authoring a timeline and
`references/audio-analysis.md` when interpreting recognition or drift. Every
helper has `--help`. The example is synthetic and contains no copyrighted media.

## What belongs in a public repository

This repository contains the skill, scripts, documentation and synthetic test
data only. Do not commit a downloaded PV, separated stems, model caches, subtitle
exports, or a user's lyrics without permission. The `.gitignore` is deliberately
media-heavy; remove an ignore only for an original, distributable test fixture.

## Related tools

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for local ASR
- [FFmpeg ASS filter](https://ffmpeg.org/ffmpeg-filters.html#ass) for subtitle burn-in
- [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator) for optional stems

## License

The skill and original scripts are MIT licensed. Third-party models, codecs and
media have their own licenses. See [LICENSE](LICENSE).
