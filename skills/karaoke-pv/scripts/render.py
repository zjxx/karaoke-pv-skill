"""Burn ASS on the original video timeline; optionally replace audio or export a crop."""
import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                       check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(r.stdout)


def render(video, ass, output, audio=None, start=0, duration=None):
    video, ass, output = (Path(p).resolve() for p in (video, ass, output))
    audio = Path(audio).resolve() if audio else None
    if not video.is_file() or not ass.is_file() or (audio and not audio.is_file()):
        raise ValueError('Input file is missing')
    if output.exists():
        raise ValueError('Output already exists; choose a new filename')
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must use .mp4')
    metadata = probe(video)
    v = next((s for s in metadata['streams'] if s['codec_type'] == 'video'), None)
    if v is None:
        raise ValueError('No video stream')
    total = float(v.get('duration') or metadata['format']['duration'])
    if not math.isfinite(start) or not 0 <= start < total:
        raise ValueError('Preview start must lie inside video')
    length = total-start if duration is None else duration
    if not math.isfinite(length) or not 0 < length <= total-start+0.001:
        raise ValueError('Preview duration must be positive and fit inside video')
    ameta = probe(audio) if audio else metadata
    if not any(s['codec_type'] == 'audio' for s in ameta['streams']):
        raise ValueError('No audio stream; supply --audio')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='render-', dir=output.parent) as temp:
        # A fixed relative ASS name avoids drive-colon, comma and quote escaping
        # in FFmpeg's filter grammar. Input/output paths are separate argv entries.
        shutil.copyfile(ass, Path(temp) / 'captions.ass')
        vf = f'ass=filename=captions.ass,trim=start={start}:duration={length},setpts=PTS-STARTPTS,format=yuv420p'
        af = f'apad,atrim=start={start}:duration={length},asetpts=PTS-STARTPTS'
        cmd = ['ffmpeg', '-v', 'warning', '-nostdin', '-n', '-i', str(video)]
        if audio:
            cmd += ['-i', str(audio)]
        graph = f'[0:v:0]{vf}[v];[{1 if audio else 0}:a:0]{af}[a]'
        cmd += ['-filter_complex', graph, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
                '-preset', 'medium', '-crf', '19', '-c:a', 'aac', '-b:a', '256k',
                '-ar', '44100', '-ac', '2', '-movflags', '+faststart', str(output)]
        subprocess.run(cmd, check=True, cwd=temp)
    result = probe(output)
    measured = float(result['format']['duration'])
    if abs(measured-length) > 0.25:
        raise ValueError(f'Output duration {measured} differs from requested {length}; inspect output')
    print(json.dumps({'output': str(output), 'duration': measured,
                     'note': 'Streams/duration checked; inspect subtitle layout and listen for sync.'}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video', type=Path)
    p.add_argument('ass', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--audio', type=Path)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--duration', type=float)
    a = p.parse_args()
    try:
        render(a.video, a.ass, a.output, a.audio, a.start, a.duration)
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        p.exit(1, f'Error: {e}\n')


if __name__ == '__main__':
    main()
