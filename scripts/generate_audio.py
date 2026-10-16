"""Generate deployment MP3s from the separate narration catalog.

TTS_PROVIDER=edge (default), google, or gtts. Optional TTS_FALLBACK_PROVIDER=gtts.
Run from any directory. Failures produce a nonzero exit status, never fake audio.
"""
import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.services.tts import (AUDIO_DIR, LANGUAGES, VOICES, catalog, get_or_synthesize_audio, atomic_write, validate_audio)


def compress(data):
    import imageio_ffmpeg
    result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', '24000', '-codec:a', 'libmp3lame', '-b:a', '40k', '-f', 'mp3', 'pipe:1'], input=data, capture_output=True, check=True)
    validate_audio(result.stdout)
    return result.stdout


async def generate(args):
    if args.verify_voices:
        import edge_tts
        available = {v['ShortName'] for v in await edge_tts.list_voices()}
        for voice in VOICES.values():
            if voice not in available:
                raise RuntimeError(f'Voice missing: {voice}')
            print(f'Verified {voice}', flush=True)
    jobs = []
    for lang in ([args.lang] if args.lang else LANGUAGES):
        data = catalog(lang)
        for key, sections in data['diseases'].items():
            if args.disease and key != args.disease:
                continue
            jobs.extend((lang, key, section, text) for section, text in sections.items())
        if not args.disease:
            jobs.extend((lang, '_common', key, text) for key, text in data['prompts'].items())
    if args.dry_run:
        print(f'Expected {len(jobs)} MP3 files in {AUDIO_DIR}')
        return
    semaphore = asyncio.Semaphore(args.jobs)
    counts = {'generated': 0, 'existing': 0, 'failed': 0}
    async def one(job):
        lang, key, section, text = job
        path = AUDIO_DIR / lang / key / f'{section}.mp3'
        async with semaphore:
            try:
                if path.exists() and not args.force:
                    validate_audio(path.read_bytes())
                    counts['existing'] += 1
                    return
                data = await get_or_synthesize_audio(text, lang, force_refresh=args.force)
                data = await asyncio.to_thread(compress, data)
                atomic_write(path, data)
                counts['generated'] += 1
            except Exception as exc:
                counts['failed'] += 1
                print(f'FAIL {lang}/{key}/{section}: {type(exc).__name__}: {str(exc).split("url=")[0]}', flush=True)
            if sum(counts.values()) % 25 == 0:
                print(json.dumps(counts), flush=True)
    await asyncio.gather(*(one(job) for job in jobs))
    print(json.dumps(counts), flush=True)
    if counts['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang', choices=LANGUAGES)
    parser.add_argument('--disease')
    parser.add_argument('--jobs', type=int, choices=range(1, 9), default=3)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verify-voices', action='store_true')
    asyncio.run(generate(parser.parse_args()))
