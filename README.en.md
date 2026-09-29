# Romaji Video Subtitles

[中文](README.md) | **English**

Add readable romaji subtitles to Japanese videos for people more comfortable
with Latin letters than hiragana or katakana. Follow dialogue, learning clips,
songs and KTV videos with short phrases and reviewed pauses.

This is a **Codex skill plus local helper scripts**. An assistant coordinates
recognition, text correction, alignment and export. The project began with song
PVs, so `karaoke-pv-skill` and `$karaoke-pv` remain for compatibility; the workflow
now covers general Japanese videos.

## Input: bring a local video

Download the video yourself and provide the local file or path.
**There is no built-in video downloader or automatic URL ingestion.**
The source is preserved; subtitles and rendered videos go into a separate folder.

## Two text modes

| Mode | Your input | Assistant workflow |
| --- | --- | --- |
| A: supplied text | Local video plus Japanese, romaji, or both; pasted text, UTF-8 files or existing subtitles | Organize text, draft romaji for Japanese input, align to this recording and split phrases |
| B: speech recognition | Local video without a transcript | Extract audio, transcribe Japanese with word timestamps, review it, draft romaji and align phrases |

- Romaji-only input works without inventing Japanese spelling. Japanese-only
  input gets a romaji draft with ambiguous readings checked against audio.
- Mode A may use recognition for alignment, but ASR does not automatically
  override supplied text.
- Both modes support **romaji only** or **Japanese plus romaji**. Users do not
  need to write JSON or supply timestamps.
- Original audio is kept by default. Instrumental separation is optional for
  KTV; ordinary dialogue does not require stem separation.

## Example requests

> Use $karaoke-pv on this local video and my romaji transcript. Keep the audio,
> split at reviewed pauses and show romaji only.

> Use $karaoke-pv to subtitle this Japanese dialogue clip. I have no transcript;
> transcribe the audio and make a short preview first.

> Use $karaoke-pv on this song PV and Japanese lyrics. Add Japanese and romaji,
> and export a practice video with the original singing.

## Install the skill

Clone the repository and enter it:

```sh
git clone https://github.com/zjxx/karaoke-pv-skill.git
cd karaoke-pv-skill
```

Windows PowerShell:

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
$skillTarget = Join-Path $skillRoot 'karaoke-pv'
if (Test-Path $skillTarget) { throw 'Skill already exists; compare before updating.' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -Recurse skills/karaoke-pv $skillTarget
```

macOS / Linux:

```sh
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skill_root"
if [ -e "$skill_root/karaoke-pv" ]; then
  echo 'Skill already exists; compare before updating.'
else
  cp -R skills/karaoke-pv "$skill_root/karaoke-pv"
fi
```

## Tools and outputs

Use Python 3.9+. Rendering needs FFmpeg with `libass` and ffprobe on PATH.
`faster-whisper` is optional, needed only for recognition, and may download a
model on first use. Subtitle export uses only Python's standard library.

Outputs can include raw ASR JSON, a phrase timeline, SRT, ASS, a timing report
and MP4. **There is no one-command raw-transcript-to-finished-video pipeline**:
the assistant coordinates transcript preparation, romaji readings, alignment
and review. Helpers can also run independently from the repository root:

```sh
# Mode B: create work first, then extract and transcribe.
python -m pip install faster-whisper
ffmpeg -n -i video.mp4 -vn -c:a pcm_s16le work/source.wav
python skills/karaoke-pv/scripts/transcribe.py work/source.wav --output work/asr.json --cache-dir work/models

# Synthetic format examples, not transcripts aligned to your video.
python skills/karaoke-pv/scripts/subtitles.py examples/timeline.json --output-dir work/bilingual --draft
python skills/karaoke-pv/scripts/subtitles.py examples/romaji-only.json --output-dir work/romaji --display romaji --draft

# After aligning your video and generating your own ASS, render a preview.
python skills/karaoke-pv/scripts/render.py video.mp4 work/romaji/romaji.ass work/preview.mp4 --start 0 --duration 8
```

`--display bilingual` (default) shows Japanese where available plus romaji,
falling back to romaji alone when Japanese is absent. `--display romaji` always
shows romaji only. Existing outputs are not overwritten. Mode A can skip ASR
when usable timing is available. See the [timeline format](skills/karaoke-pv/references/timeline.md)
and [audio analysis guide](skills/karaoke-pv/references/audio-analysis.md).
Every helper supports `--help`.

## Timing accuracy

ASR timestamps are alignment evidence, not precise forced alignment or a
guarantee of correct text. Each cue records `asr`, `estimated`, or `audio-reviewed`
timing. Unreviewed cues require `--draft`. Gaps between recognized words are not
necessarily silence; screenshots verify layout, not audio sync. Check long vowels,
names, unusual readings and overlapping dialogue. The exporter supports one
nonoverlapping cue stream; complex speaker overlaps need separate layout editing.

## Development checks

```sh
python -m unittest discover -s tests -v
```

## Dependencies and license

- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper): local recognition.
- [FFmpeg ASS filter](https://ffmpeg.org/ffmpeg-filters.html#ass): subtitle burn-in.
- [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator): optional music stem separation.

Code and original documentation use the [MIT license](LICENSE). Third-party
models, tools and media retain their own licenses. This repository contains only
general code, docs and original synthetic examples. User videos, transcripts,
audio, model caches and finished media stay local.
