---
name: karaoke-pv
description: Prepare Japanese song PVs for singing with romaji subtitles, vocal or instrumental audio, and phrase timing informed by audio analysis. Use for KTV projection videos, correcting lyric drift, and showing singing pauses; not general video upscaling.
---

# Karaoke PV

Preserve the user's PV and produce readable singing cues. Keep a vocal practice
version when requested; accompaniment extraction and video enhancement are
separate, optional operations.

## Work from evidence

1. Inspect the supplied video and existing subtitles. Check duration, streams,
   first vocal entry, fonts, disk space and available FFmpeg/Python dependencies.
   Keep original media and earlier outputs intact. Work in a separate output folder.
2. Extract audio at the video's original timeline. If separation improves analysis
   or the user needs accompaniment, use an available separator. Check the stem's
   duration and offset against the original. A residual vocal is not a clean
   official instrumental. See [audio-analysis.md](references/audio-analysis.md).
3. Transcribe vocals with word timestamps. Save raw text, probabilities, model,
   crop offset and prompt usage. The bundled `scripts/transcribe.py` supports
   bounded retries on difficult sections. Consume the segment generator and save
   results; a launched command or empty log is not a successful transcription.
4. Compare recognition with the provided lyrics. ASR is evidence, not the lyric
   authority: singing, archaic readings, repeated choruses and elongated vowels
   cause errors. Correct Japanese first, then romaji. Automatic transliteration
   is a draft and must not decide ambiguous kanji readings on its own. Preserve
   intentional sung readings. Explain actual discrepancies rather than asserting
   that either source is always more accurate.
5. Build explicit phrase cues in the [timeline schema](references/timeline.md).
   Mark machine boundaries `asr`, hand estimates `estimated`, and only reviewed
   audio boundaries `audio-reviewed`. Do not replace missing timestamps with
   equal-duration slots or silently stretch a verse to fit. A global offset fixes
   a constant shift, not changing drift. Treat repeated sections independently.
6. Match the display to the request. For visible breathing points, split at
   supported phrase boundaries and preserve real gaps. Whitespace or punctuation
   in ASR text alone is not evidence of silence. A musical phrase boundary can
   be useful even without silence; label it as phrasing, not a detected breath.
   Keep phrases long enough to read and do not split Japanese words arbitrarily.
   If users need advance reading, retain a whole line with visible phrase dividers
   or use a next-phrase preview rather than surprising them with rapid replacement.
7. Export editable SRT and styled ASS with `scripts/subtitles.py`. For a draft use
   `--draft`; final export requires all cues marked `audio-reviewed`. Never mark
   them reviewed just to pass this check. Render from the original PV using
   `scripts/render.py`; its optional replacement audio preserves the video length.
   Keep the source resolution unless enhancement was requested.
8. Check the resulting artifact: streams/duration, subtitle clipping, first vocal
   entry, a tempo change, an interlude and the final chorus. Screenshots establish
   text placement only; synchronization requires audio playback or waveform and
   alignment evidence. Prefer a short vocal preview before a long re-render when
   the reading format is still being decided. Report what was and wasn't checked.

## Practical boundaries

- Never describe ASR word times as sample-accurate forced alignment. Recognition
  probabilities do not measure timing accuracy. Pause candidates need review.
- Use a consistent romaji convention with readable word spacing; don't silently
  claim mora-by-mora highlighting when only phrase timing exists.
- Reuse installed tools and models. Use a workspace cache for large downloads;
  dependencies are optional and the export scripts use Python's standard library.
- Publishing the skill does not publish users' media. Only include code, docs and
  original/synthetic examples in a source repository. Inspect the staged files.

## Bundled helpers

- `scripts/transcribe.py`: local Faster Whisper transcription, optional time crop,
  raw word timings and gap candidates. Requires `faster-whisper` and FFmpeg for crops.
- `scripts/subtitles.py`: validate provenance and cue order; export UTF-8 SRT/ASS.
- `scripts/render.py`: burn ASS into the PV with vocal or replacement audio,
  including a `--start`/`--duration` preview. Requires FFmpeg with libass and ffprobe.

Read [timeline.md](references/timeline.md) before creating cues, and
[audio-analysis.md](references/audio-analysis.md) when analyzing vocals or
troubleshooting drift. Each helper accepts `--help`.
