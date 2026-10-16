"""Check every expected MP3 for duration, format, size, and decoded signal energy."""
import argparse
import array
import math
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.services.tts import AUDIO_DIR, LANGUAGES, SECTIONS, catalog, validate_audio


def verify(path):
    import imageio_ffmpeg
    info = validate_audio(path.read_bytes())
    if info.channels != 1 or not 31000 <= info.bitrate <= 49000:
        raise ValueError(f'Expected mono 32–48 kbps, got {info.channels} channels, {info.bitrate} bps')
    result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', '8000', 'pipe:1'], capture_output=True, check=True)
    samples = array.array('h', result.stdout)
    rms = math.sqrt(sum(float(x)*x for x in samples)/max(1, len(samples)))
    if rms < 10:
        raise ValueError(f'Silent audio: RMS {rms:.3f}')
    return info.length, rms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang', choices=LANGUAGES)
    args = parser.parse_args()
    failures = []
    print('language | diagnosis | symptoms | treatment | prevention | common')
    for lang in ([args.lang] if args.lang else LANGUAGES):
        data = catalog(lang)
        row = []
        for section in (*SECTIONS, 'common'):
            paths = [AUDIO_DIR/lang/key/f'{section}.mp3' for key in data['diseases']] if section != 'common' else [AUDIO_DIR/lang/'_common'/f'{key}.mp3' for key in data['prompts']]
            valid = 0
            for path in paths:
                try:
                    verify(path)
                    valid += 1
                except Exception as exc:
                    failures.append(f'{path.relative_to(AUDIO_DIR)}: {exc}')
            row.append(f'{valid}/{len(paths)}')
        print(lang + ' | ' + ' | '.join(row), flush=True)
    print(f'Failures: {len(failures)}')
    for failure in failures[:30]:
        print(failure)
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
