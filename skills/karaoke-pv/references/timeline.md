# Timeline format

UTF-8 JSON, version 1. Times are seconds on the **original full video**.
`duration` describes the full video timeline. A crop beginning at 80 seconds uses
80 seconds as its timeline offset when its word times are returned.

```json
{
  "version": 1,
  "duration": 8,
  "width": 852,
  "height": 480,
  "cues": [
    {
      "start": 1.25,
      "end": 3.5,
      "ja": "青い空",
      "romaji": "Aoi sora",
      "timing_source": "estimated",
      "note": "Original demo phrase with synthetic timing."
    }
  ]
}
```

`romaji` is required. `ja` is optional and may be omitted or an empty string when
the source uses romaji alone. The schema keeps Japanese and romaji independent.
The default `--display bilingual` emits Japanese where available and always
romaji. `--display romaji` hides Japanese even when present in the source timeline.
The agent prepares this JSON from supplied text (Mode A) or reviewed ASR (Mode B);
the assistant prepares alignment and readings before passing the timeline to these
export scripts.

`timing_source` is `asr`, `estimated`, or `audio-reviewed`. Use `note` to record
uncertainty or how a boundary was checked. Review flags describe timing. The
exporter uses `--draft` for `asr` and `estimated` cues and the reviewed flag for
final output.

Cues must be nonempty, ordered, nonoverlapping and inside the video. All times
must be finite. Consecutive cues may touch. Preserve real silent gaps rather than
extending the preceding cue to the next start. The exporter uses integer
milliseconds for SRT and integer centiseconds for ASS (with proper carry).
Boundaries that collapse at ASS precision are rejected.

Text is plain text: ASS override syntax, newlines and control characters are
rejected. Use separate cues for phrases. Font sizes scale with frame height;
font names are configurable because Japanese fonts differ between systems.
Long lines still need a rendered visual check; length in characters isn't width.

Examples (from repository root):

```sh
python skills/karaoke-pv/scripts/subtitles.py examples/timeline.json --output-dir work/subtitles --draft
python skills/karaoke-pv/scripts/subtitles.py examples/romaji-only.json --output-dir work/romaji-only --display romaji --draft
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/preview.mp4 --start 80 --duration 25
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/vocal.mp4
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/instrumental.mp4 --audio work/instrumental.wav
```

Preview rendering burns subtitles on the full timeline before trimming, so cue
timestamps stay on the original timeline. Output audio is padded or trimmed to
the selected video interval. Replacement stems are prepared on the same timeline
before rendering.
