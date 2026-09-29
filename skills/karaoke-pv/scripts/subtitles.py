"""Validate a phrase timeline and export SRT + ASS. Standard library only."""
import argparse
import json
import math
from pathlib import Path


def ticks(seconds, scale):
    return int(math.floor(seconds * scale + 0.5))


def timestamp(seconds, ass=False):
    scale = 100 if ass else 1000
    whole, frac = divmod(ticks(seconds, scale), scale)
    minutes, sec = divmod(whole, 60)
    hour, minute = divmod(minutes, 60)
    if ass:
        return f"{hour}:{minute:02}:{sec:02}.{frac:02}"
    return f"{hour:02}:{minute:02}:{sec:02},{frac:03}"


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def plain_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty plain text")
    if any(ord(c) < 32 or ord(c) == 127 or c in '{}\\' or c in '\u2028\u2029' for c in value):
        raise ValueError(f"{label}: control characters, newlines and ASS overrides are not supported")
    return value


def validate(data, draft=False):
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Expected a version 1 timeline object')
    duration = number(data.get('duration'), 'duration')
    if duration <= 0:
        raise ValueError('duration must be positive')
    for key in ('width', 'height'):
        v = data.get(key)
        if type(v) is not int or v < 2:
            raise ValueError(f'{key} must be an integer >= 2')
    cues = data.get('cues')
    if not isinstance(cues, list) or not cues:
        raise ValueError('cues must be a nonempty list')
    previous_end = 0
    warnings = []
    for i, cue in enumerate(cues, 1):
        if not isinstance(cue, dict):
            raise ValueError(f'cue {i} must be an object')
        a, b = (number(cue.get(k), f'cue {i} {k}') for k in ('start', 'end'))
        if not 0 <= a < b <= duration:
            raise ValueError(f'cue {i}: require 0 <= start < end <= duration')
        if a < previous_end:
            raise ValueError(f'cue {i}: out of order or overlapping')
        if ticks(a, 100) >= ticks(b, 100):
            raise ValueError(f'cue {i}: collapses at ASS centisecond precision')
        previous_end = b
        plain_text(cue.get('romaji'), f'cue {i} romaji')
        # Romaji-only source text does not imply recoverable Japanese spelling.
        if 'ja' in cue and cue['ja'] != '':
            plain_text(cue['ja'], f'cue {i} ja')
        source = cue.get('timing_source')
        if source not in ('asr', 'estimated', 'audio-reviewed'):
            raise ValueError(f'cue {i}: missing/invalid timing_source')
        if source != 'audio-reviewed' and not draft:
            raise ValueError(f'cue {i}: unreviewed timing; review audio or export with --draft')
        if b - a < 0.7:
            warnings.append(f'cue {i}: shorter than 0.7 seconds; check readability')
        if len(cue['romaji']) > 65:
            warnings.append(f'cue {i}: long romaji phrase; check wrapping in rendered video')
    return warnings


def export(data, output_dir, draft=False, jp_font='sans-serif', romaji_font='Arial', display='bilingual'):
    warnings = validate(data, draft)
    if display not in ('bilingual', 'romaji'):
        raise ValueError('display must be bilingual or romaji')
    for font in (jp_font, romaji_font):
        plain_text(font, 'font name')
        if ',' in font:
            raise ValueError('font names cannot contain commas')
    dest = Path(output_dir)
    paths = [dest / 'romaji.srt', dest / 'romaji.ass', dest / 'timing-report.json']
    if any(p.exists() for p in paths):
        raise ValueError('Output files already exist; choose a new output directory')
    scale = data['height'] / 480
    jp_size, rom_size = 22 * scale, 21 * scale
    srt, events = [], []
    for i, cue in enumerate(data['cues'], 1):
        a, b, rom = (cue[k] for k in ('start', 'end', 'romaji'))
        ja = cue.get('ja', '') if display == 'bilingual' else ''
        lines = f'{ja}\n{rom}' if ja else rom
        srt.append(f'{i}\n{timestamp(a)} --> {timestamp(b)}\n{lines}\n')
        parts = [(0, 'JP', ja)] if ja else []
        parts.append((1, 'ROMA', rom))
        for layer, style, text in parts:
            events.append(f'Dialogue: {layer},{timestamp(a, True)},{timestamp(b, True)},{style},,0,0,0,,{text}')
    header = f'''[Script Info]
Title: Romaji phrases{' - DRAFT' if draft else ''}
ScriptType: v4.00+
PlayResX: {data['width']}
PlayResY: {data['height']}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: JP,{jp_font},{jp_size:.2f},&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,{2*scale:.2f},0,2,{round(24*scale)},{round(24*scale)},{round(44*scale)},1
Style: ROMA,{romaji_font},{rom_size:.2f},&H0000FFFF,&H0000FFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,{2*scale:.2f},0,2,{round(24*scale)},{round(24*scale)},{round(18*scale)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    report = {
        'draft': draft, 'display': display, 'cue_count': len(data['cues']),
        'unreviewed': [i for i, c in enumerate(data['cues'], 1) if c['timing_source'] != 'audio-reviewed'],
        'warnings': warnings,
        'limitation': 'Schema validation is not audio synchronization or visual verification.'
    }
    dest.mkdir(parents=True, exist_ok=True)
    for path, content in zip(paths, ('\n'.join(srt), header + '\n'.join(events) + '\n', json.dumps(report, ensure_ascii=False, indent=2))):
        with path.open('x', encoding='utf-8', newline='\n') as f:
            f.write(content)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('timeline', type=Path)
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--draft', action='store_true', help='Allow asr/estimated timings, recorded in report')
    p.add_argument('--jp-font', default='sans-serif')
    p.add_argument('--romaji-font', default='Arial')
    p.add_argument('--display', choices=('bilingual', 'romaji'), default='bilingual',
                   help='Show Japanese where available, or romaji only')
    a = p.parse_args()
    try:
        report = export(json.loads(a.timeline.read_text(encoding='utf-8-sig')), a.output_dir, a.draft, a.jp_font, a.romaji_font, a.display)
    except (ValueError, OSError) as e:
        p.exit(1, f'Error: {e}\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
