# Vocal analysis and alignment

## Extract and optionally separate

Use FFmpeg to extract the original audio without moving its timeline:

```sh
ffmpeg -n -i work/pv.mp4 -vn -c:a pcm_s16le work/source.wav
```

If installed, `audio-separator` can generate vocal and instrumental stems. Inspect
its local `--help` and available models before choosing a model; model filenames,
hardware requirements and output names vary. Reuse existing stems if suitable.
Compare each stem's onset and duration to the original and listen for separation
artifacts. Do not treat background music energy as a vocal onset.

## Get recognition evidence

```sh
python -m pip install faster-whisper
python skills/karaoke-pv/scripts/transcribe.py work/vocals.wav --output work/asr.json --cache-dir work/models
python skills/karaoke-pv/scripts/transcribe.py work/vocals.wav --output work/asr-section.json --cache-dir work/models --start 80 --duration 30
```

The default is `small`, CPU and int8; these are a modest initial pass, not a
quality guarantee. A local model path may be supplied through `--model`. Optional
`--prompt-file` supplies a short UTF-8 Japanese context prompt. Prompted recognition
is biased by that text, so keep prompt usage in the metadata and do not count it
as independent confirmation of the supplied lyrics.

Raw words include probabilities; `gap_candidates` lists intervals of at least
`--gap` seconds between nonzero-duration ASR words. These are **ASR gaps**, not
measured acoustic silence. Missing words, swallowed particles and long vowels
can create false gaps. Zero-length words and phrase ends require special care.

## Correct the timing

- Keep the known first vocal entry as a check, not an excuse to uniformly shift
  every line. Recheck the problematic transition itself.
- For a lost verse or doubtful boundary, analyze a bounded crop with enough
  musical context. Add the exact crop offset back once, never twice.
- Compare words to supplied lyrics, then inspect vocal waveforms/spectrograms
  and replay short intervals. If no playback tool is available, report that and
  leave `asr`/`estimated` flags; deliver an explicitly labeled draft.
- A pause in the isolated vocal is stronger evidence than a token boundary but
  source separation can erase consonants and leave reverb. Check the original mix.
- Phrase segmentation supports reading. A gap-free clause may still be split for
  readability; do not call that split a detected silence or breath.
- Prefer a short preview of the reported trouble spot when uncertain. If ASR
  repeatedly fails, stop claiming progress toward automatic precision and expose
  the unresolved cues for listening or manual editing.

## Romaji

Generate readings from corrected Japanese, then compare with the sung pronunciation
and the user's reference. Generic kanji converters cannot resolve every literary
or song-specific reading. For singing, keep readable words and consistent long
vowels (`ou`, `uu`, `aa`, etc.) or the user's preferred convention. Written particles
and pronounced particles may differ; choose and document a convention. Do not
substitute recognition's hallucinated lyric just because its timestamp looks neat.

## Primary references

- [Faster Whisper usage and word timestamps](https://github.com/SYSTRAN/faster-whisper)
- [FFmpeg ASS filter](https://ffmpeg.org/ffmpeg-filters.html#ass)
- [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator)

Tool versions and model licenses are separate from this skill's MIT license.
