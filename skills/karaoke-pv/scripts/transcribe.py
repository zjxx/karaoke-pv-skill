"""Transcribe vocals locally; save ASR words and candidate gaps, not verified timing."""
import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path


def gap_candidates(words, threshold):
    result = []
    previous_end = None
    for w in words:
        if w['end'] <= w['start']:
            continue
        if previous_end is not None and w['start'] - previous_end >= threshold:
            result.append({'start': previous_end, 'end': w['start'], 'source': 'asr-gap-unverified'})
        previous_end = max(previous_end or 0, w['end'])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('audio', type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--cache-dir', required=True, type=Path)
    p.add_argument('--model', default='small', help='Whisper model name or local directory')
    p.add_argument('--language', default='ja')
    p.add_argument('--device', default='cpu')
    p.add_argument('--compute-type', default='int8')
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--duration', type=float)
    p.add_argument('--gap', type=float, default=0.25)
    p.add_argument('--prompt-file', type=Path)
    a = p.parse_args()
    if not a.audio.is_file() or a.output.exists():
        p.error('Input must exist and output must not already exist')
    if not math.isfinite(a.start) or a.start < 0 or not math.isfinite(a.gap) or a.gap <= 0:
        p.error('--start must be finite and nonnegative; --gap must be finite and positive')
    if a.duration is not None and (not math.isfinite(a.duration) or a.duration <= 0):
        p.error('--duration must be finite and positive')
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        p.exit(1, 'Install optional dependency: python -m pip install faster-whisper\n')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.cache_dir.mkdir(parents=True, exist_ok=True)
    prompt = a.prompt_file.read_text(encoding='utf-8-sig') if a.prompt_file else None
    try:
        with tempfile.TemporaryDirectory(prefix='asr-', dir=a.output.parent) as temp:
            source = a.audio.resolve()
            if a.start or a.duration is not None:
                crop = Path(temp) / 'crop.wav'
                cmd = ['ffmpeg', '-v', 'error', '-nostdin', '-n', '-i', str(source), '-ss', str(a.start)]
                if a.duration is not None:
                    cmd += ['-t', str(a.duration)]
                subprocess.run(cmd + ['-vn', '-ac', '1', '-ar', '16000', str(crop)], check=True)
                source = crop
            model = WhisperModel(a.model, device=a.device, compute_type=a.compute_type, download_root=str(a.cache_dir.resolve()))
            segments, info = model.transcribe(str(source), language=a.language, beam_size=5,
                word_timestamps=True, vad_filter=False, condition_on_previous_text=False, initial_prompt=prompt)
            rows = []
            for seg in segments:
                rows.append({'start': seg.start+a.start, 'end': seg.end+a.start, 'text': seg.text,
                    'words': [{'start': w.start+a.start, 'end': w.end+a.start, 'word': w.word,
                               'probability': w.probability} for w in (seg.words or [])]})
                print(f'Analyzed {seg.end+a.start:.2f}s', flush=True)
            if not rows:
                raise ValueError('No segments recognized; output was not written')
            words = [w for seg in rows for w in seg['words']]
            result = {'version': 1, 'model': a.model, 'language': info.language,
                'offset_seconds': a.start, 'requested_duration': a.duration,
                'prompt_used': prompt is not None, 'timing_status': 'asr-unreviewed',
                'segments': rows, 'gap_candidates': gap_candidates(words, a.gap)}
            with a.output.open('x', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as e:
        p.exit(1, f'Error: {e}\n')
    print(f'Saved {len(rows)} segments to {a.output}')


if __name__ == '__main__':
    main()
