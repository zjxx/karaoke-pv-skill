# Timeline format

UTF-8 JSON, version 1. Times are seconds on the **original full video**, never
relative to a cropped vocal file. `duration` describes that video, not an ASR
segment. A crop beginning at 80 seconds needs 80 added to every local word time.

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
      "note": "Original demo phrase; synthetic timing, no recording."
    }
  ]
}
```

`timing_source` is `asr`, `estimated`, or `audio-reviewed`. Use `note` to record
uncertainty or how a boundary was checked. Review flags describe timing, not a
guarantee that lyrics or readings are correct. The exporter refuses unreviewed
cues unless `--draft` is passed. Do not change flags just to enable export.

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
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/preview.mp4 --start 80 --duration 25
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/vocal.mp4
python skills/karaoke-pv/scripts/render.py work/pv.mp4 work/subtitles/romaji.ass work/instrumental.mp4 --audio work/instrumental.wav
```

Preview rendering burns subtitles on the full timeline before trimming, so
original cue timestamps do not need manual offsets. Output audio is padded or
trimmed to the selected video interval. A replacement stem must already share
the original timeline; duration equality cannot prove synchronization.
