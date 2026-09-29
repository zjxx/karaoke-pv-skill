---
name: karaoke-pv
description: Add readable romaji subtitles to user-supplied Japanese videos for romaji readers. Use supplied Japanese or romaji text, or transcribe audio, then align phrases and pauses for dialogue, learning clips, songs and KTV.
---

# Romaji Video Subtitles

Help people who read romaji more comfortably than hiragana or katakana follow
Japanese speech or singing. Support dialogue, learning clips, music videos and
KTV. Keep the existing `karaoke-pv` identifier for compatibility.

## Input and mode selection

Start from a local video file supplied by the user. Video acquisition is a
separate preparation step; the processing workflow begins with the local file.

Infer the text mode from the supplied material. The user provides video and text;
the skill prepares the timeline and subtitle files.

**Mode A — supplied text:** Accept pasted text, UTF-8 text files or subtitles
containing Japanese, romaji, or both. Preserve existing line breaks and valid
timestamps as starting evidence, then check them against this specific video.
For Japanese-only input, generate a romaji draft and check readings against audio.
For romaji-only input, keep romaji as the source and leave Japanese optional. When
both are supplied, resolve conflicts against audio and explain reading choices.
Align the text to audio; optional ASR helps locate phrases while supplied text
remains the review baseline.

**Mode B — audio recognition:** With audio as the text source, extract speech/vocals,
transcribe Japanese with word timestamps, review the recognition and generate
romaji from that draft. Preserve the raw recognition separately. Unknown names,
ambiguous readings and overlapping voices remain uncertain until checked.

Both modes converge on a phrase timeline and a short preview. Romaji is the main
reading aid; offer romaji-only output or Japanese plus romaji as appropriate.
Preserve original audio by default. Add accompaniment extraction for music and
apply video enhancement as an additional output when requested.

## Work from evidence

1. Inspect the supplied video and existing subtitles. Check duration, streams,
   first vocal entry, fonts, disk space and available FFmpeg/Python dependencies.
   Keep original media and earlier outputs intact. Work in a separate output folder.
2. Extract audio at the video's original timeline. If separation improves analysis
   or the user needs accompaniment, use an available separator. Check the stem's
   duration and offset against the original. Record stem quality in the output
   notes. See [audio-analysis.md](references/audio-analysis.md).
3. In Mode B (or if useful for alignment in Mode A), transcribe with word timestamps.
   Save raw text, probabilities, model,
   crop offset and prompt usage. The bundled `scripts/transcribe.py` supports
   bounded retries on difficult sections. Consume the segment generator and save
   results and confirm that segments were written before moving to alignment.
4. Compare recognition with any supplied text. Use the supplied wording as the
   primary source in Mode A and the reviewed recognition as the primary source in
   Mode B. Check singing, archaic readings, repeated choruses and elongated vowels.
   When Japanese is available, correct it first, then romaji; keep romaji-only
   input as a complete display mode. Explain reading choices and preserve sung
   pronunciation.
5. Build explicit phrase cues in the [timeline schema](references/timeline.md).
   Mark machine boundaries `asr`, hand estimates `estimated`, and only reviewed
   audio boundaries `audio-reviewed`. Use local audio evidence for missing
   timestamps, and handle each repeated section independently. Apply a global
   offset for a constant shift and local corrections for changing drift.
6. Match the display to the request. For speech, respect utterances and speaker
   changes and preserve speaker turns. The default helper exports one continuous
   cue stream; use separate tracks for overlapping speakers. For visible breathing points, split at
   supported phrase boundaries and preserve real gaps. Whitespace or punctuation
   in ASR text alone is a phrase candidate; verify it against audio. A musical
   phrase boundary can guide reading; label it as phrasing when the measured gap is absent.
   Keep phrases long enough to read and split at natural Japanese word boundaries.
   If users need advance reading, retain a whole line with visible phrase dividers
   or use a next-phrase preview rather than surprising them with rapid replacement.
7. Export editable SRT and styled ASS with `scripts/subtitles.py`. Use
   `--display romaji` for romaji-only output or the default `bilingual` to show
   Japanese where available. For a draft use
   `--draft`; final export uses cues marked `audio-reviewed`. Render from the original PV using
   `scripts/render.py`; its optional replacement audio preserves the video length.
   Keep the source resolution unless enhancement was requested.
8. Check the resulting artifact: streams/duration, subtitle clipping, first spoken
   or sung entry, pauses, a pace or speaker change, and the ending. For songs,
   also check an interlude and a repeated chorus. Screenshots establish
   text placement; pair it with audio playback or waveform review for
   synchronization. Prefer a short vocal preview before a long re-render when
   the reading format is still being decided. Report the checks performed.

## Quality conventions

- Describe ASR word times as alignment drafts and use audio review for final cues.
- Use a consistent romaji convention with readable word spacing; phrase timing and
  mora-level highlighting are separate display choices.
- Reuse installed tools and models. Use a workspace cache for large downloads;
  dependencies are optional and the export scripts use Python's standard library.
- Publishing the skill includes reusable code, docs and original/synthetic examples;
  keep project media in the user's workspace.

## Bundled helpers

- `scripts/transcribe.py`: local Faster Whisper transcription, optional time crop,
  raw word timings and gap candidates. Requires `faster-whisper` and FFmpeg for crops.
- `scripts/subtitles.py`: validate provenance and cue order; export UTF-8 SRT/ASS.
- `scripts/render.py`: burn ASS into the PV with vocal or replacement audio,
  including a `--start`/`--duration` preview. Requires FFmpeg with libass and ffprobe.

Read [timeline.md](references/timeline.md) before creating cues, and
[audio-analysis.md](references/audio-analysis.md) when analyzing vocals or
troubleshooting drift. Each helper accepts `--help`.
