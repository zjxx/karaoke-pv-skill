# Vocal analysis and alignment

In supplied-text mode, start with the user's Japanese or romaji and use recognition
to help alignment or resolve a disputed reading. In recognition mode,
produce a Japanese draft first, then romaji. A plain dialogue clip can use extracted
audio directly; stem separation is optional for music or difficult background sound.
When the source is romaji-only, keep Japanese as an optional display layer.

## Extract and optionally separate

Use FFmpeg to extract the original audio while preserving its timeline:

```sh
ffmpeg -n -i work/pv.mp4 -vn -c:a pcm_s16le work/source.wav
```

If installed, `audio-separator` can generate vocal and instrumental stems. Inspect
its local `--help` and available models before choosing a model; model filenames,
hardware requirements and output names vary. Reuse existing stems if suitable.
Compare each stem's onset and duration to the original and listen for separation
artifacts. Compare vocal onsets with the original mix and the lyric phrasing.

## Get recognition evidence

```sh
python -m pip install faster-whisper
python skills/karaoke-pv/scripts/transcribe.py work/vocals.wav --output work/asr.json --cache-dir work/models
python skills/karaoke-pv/scripts/transcribe.py work/vocals.wav --output work/asr-section.json --cache-dir work/models --start 80 --duration 30
```

The default is `small`, CPU and int8 for an efficient initial pass. A local model
path may be supplied through `--model`. Optional
`--prompt-file` supplies a short UTF-8 Japanese context prompt. Prompted recognition
is guided by that text, so keep prompt usage in the metadata and pair it with
audio review when confirming supplied lyrics.

Raw words include probabilities; `gap_candidates` lists intervals of at least
`--gap` seconds between nonzero-duration ASR words. These are **ASR gaps**, not
measured acoustic silence. Missing words, swallowed particles and long vowels
can create false gaps. Zero-length words and phrase ends require special care.

## Correct the timing

- Keep the known first vocal entry as a check and recheck the problematic
  transition itself.
- For a lost verse or doubtful boundary, analyze a bounded crop with enough
  musical context. Add the exact crop offset back once.
- Compare words to supplied lyrics, then inspect vocal waveforms/spectrograms
  and replay short intervals. Record `asr`/`estimated` flags until the interval
  receives audio review, then mark it `audio-reviewed`.
- A pause in the isolated vocal is stronger evidence than a token boundary but
  source separation can erase consonants and leave reverb. Check the original mix.
- Phrase segmentation supports reading. A gap-free clause may still be split for
  readability and labeled as phrasing.
- Prefer a short preview of the reported trouble spot when refining alignment.
  Repeated ASR failures become clearly marked cues for listening or manual editing.

## Romaji

Generate readings from corrected Japanese, then compare with the sung pronunciation
and the user's reference. Check literary and song-specific readings with the
recording. For singing, keep readable words and consistent long
vowels (`ou`, `uu`, `aa`, etc.) or the user's preferred convention. Written particles
and pronounced particles may differ; choose and document a convention. Keep the
reviewed lyric as the text source while recognition supplies timing evidence.

## Primary references

- [Faster Whisper usage and word timestamps](https://github.com/SYSTRAN/faster-whisper)
- [FFmpeg ASS filter](https://ffmpeg.org/ffmpeg-filters.html#ass)
- [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator)

Tool versions and model licenses are separate from this skill's MIT license.
