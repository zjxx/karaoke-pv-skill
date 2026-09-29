---
name: karaoke-pv
description: Add readable romaji subtitles to user-supplied Japanese videos for people who cannot comfortably read kana. Use supplied Japanese or romaji text, or transcribe audio, then align phrases and pauses for dialogue, learning clips, songs and KTV.
---

# Romaji Video Subtitles

Help people who read romaji more comfortably than hiragana or katakana follow
Japanese speech or singing. Support dialogue, learning clips, music videos and
KTV. Keep the existing `karaoke-pv` identifier for compatibility.

## Input and mode selection

Start from a local video the user supplies after downloading it themselves. This
skill has no built-in video downloader. If only a URL is supplied, ask for the
local video; do not imply that an inaccessible link was processed. An explicit
request to download may be handled separately with available tools.

Infer the text mode from the material already supplied; do not ask again when
the choice is clear. The user need not author JSON or supply timestamps.

**Mode A — supplied text:** Accept pasted text, UTF-8 text files or subtitles
containing Japanese, romaji, or both. Preserve existing line breaks and valid
timestamps as starting evidence, then check them against this specific video.
For Japanese-only input, generate a romaji draft and check readings against audio.
For romaji-only input, keep romaji as the source and leave Japanese absent; do not
invent kanji by reverse transliteration. When both are supplied, resolve conflicts
against audio and explain uncertain edits. Align the text to audio; optional ASR
can help locate phrases but must not silently replace the supplied wording.

**Mode B — audio recognition:** When no text is supplied, extract speech/vocals,
transcribe Japanese with word timestamps, review the recognition and generate
romaji from that draft. Preserve the raw recognition separately. Unknown names,
ambiguous readings and overlapping voices remain uncertain until checked.

Both modes converge on a phrase timeline and a short preview. Romaji is the main
reading aid; offer romaji-only output or Japanese plus romaji as appropriate.
Preserve original audio by default. Accompaniment extraction is an optional music
branch, not a prerequisite for dialogue. Upscaling is a separate request.

## Work from evidence

1. Inspect the supplied video and existing subtitles. Check duration, streams,
   first vocal entry, fonts, disk space and available FFmpeg/Python dependencies.
   Keep original media and earlier outputs intact. Work in a separate output folder.
2. Extract audio at the video's original timeline. If separation improves analysis
   or the user needs accompaniment, use an available separator. Check the stem's
   duration and offset against the original. A residual vocal is not a clean
   official instrumental. See [audio-analysis.md](references/audio-analysis.md).
3. In Mode B (or if useful for alignment in Mode A), transcribe with word timestamps.
   Save raw text, probabilities, model,
   crop offset and prompt usage. The bundled `scripts/transcribe.py` supports
   bounded retries on difficult sections. Consume the segment generator and save
   results; a launched command or empty log is not a successful transcription.
4. Compare recognition with any supplied text. ASR is evidence, not the text
   authority: singing, archaic readings, repeated choruses and elongated vowels
   cause errors. When Japanese is available, correct it first, then romaji; keep
   romaji-only input usable without reconstructing Japanese. Automatic transliteration
   is a draft and must not decide ambiguous kanji readings on its own. Preserve
   intentional sung readings. Explain actual discrepancies rather than asserting
   that either source is always more accurate.
5. Build explicit phrase cues in the [timeline schema](references/timeline.md).
   Mark machine boundaries `asr`, hand estimates `estimated`, and only reviewed
   audio boundaries `audio-reviewed`. Do not replace missing timestamps with
   equal-duration slots or silently stretch a verse to fit. A global offset fixes
   a constant shift, not changing drift. Treat repeated sections independently.
6. Match the display to the request. For speech, respect utterances and speaker
   changes; do not merge overlapping speakers into a single invented sequence.
   The helper supports one nonoverlapping cue stream; unresolved overlaps need
   manual editing or a different subtitle layout. For visible breathing points, split at
   supported phrase boundaries and preserve real gaps. Whitespace or punctuation
   in ASR text alone is not evidence of silence. A musical phrase boundary can
   be useful even without silence; label it as phrasing, not a detected breath.
   Keep phrases long enough to read and do not split Japanese words arbitrarily.
   If users need advance reading, retain a whole line with visible phrase dividers
   or use a next-phrase preview rather than surprising them with rapid replacement.
7. Export editable SRT and styled ASS with `scripts/subtitles.py`. Use
   `--display romaji` for romaji-only output or the default `bilingual` to show
   Japanese where available. For a draft use
   `--draft`; final export requires all cues marked `audio-reviewed`. Never mark
   them reviewed just to pass this check. Render from the original PV using
   `scripts/render.py`; its optional replacement audio preserves the video length.
   Keep the source resolution unless enhancement was requested.
8. Check the resulting artifact: streams/duration, subtitle clipping, first spoken
   or sung entry, pauses, a pace or speaker change, and the ending. For songs,
   also check an interlude and a repeated chorus. Screenshots establish
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
