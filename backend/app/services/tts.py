"""Audio providers and validated, content-addressed MP3 cache. No synthetic success."""
import abc
import asyncio
import hashlib
import io
import json
import logging
import os
import re
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
from mutagen.mp3 import MP3

ROOT = Path(__file__).resolve().parents[3]
NARRATION_DIR = ROOT / 'backend/app/data/narration'
AUDIO_DIR = ROOT / 'backend/app/static/audio'
# New namespace deliberately excludes the old poisoned cache.
AUDIO_CACHE_DIR = ROOT / 'backend/app/static/audio_cache/v2'
LANGUAGES = ('en', 'hi', 'ta', 'te', 'kn')
SECTIONS = ('diagnosis', 'symptoms', 'treatment', 'prevention')
VOICES = dict(zip(LANGUAGES, ('en-IN-NeerjaNeural', 'hi-IN-SwaraNeural', 'ta-IN-PallaviNeural', 'te-IN-ShrutiNeural', 'kn-IN-SapnaNeural')))
MAX_TEXT = 2000
logger = logging.getLogger(__name__)


def validate_language(lang):
    if lang not in LANGUAGES:
        raise ValueError('Supported languages: en, hi, ta, te, kn')
    return lang


def catalog(lang):
    validate_language(lang)
    return json.loads((NARRATION_DIR / f'{lang}.json').read_text(encoding='utf-8'))


def lexicon(lang):
    return json.loads((NARRATION_DIR / 'lexicon' / f'{lang}.json').read_text(encoding='utf-8'))


def spoken_text(text, lang, ssml=False):
    aliases = lexicon(lang)
    pattern = '|'.join(re.escape(k) for k in sorted(aliases, key=len, reverse=True) if k)
    parts, last = [], 0
    for match in re.finditer(pattern, text) if pattern else []:
        parts.append(escape(text[last:match.start()]) if ssml else text[last:match.start()])
        word = match.group()
        parts.append(f'<sub alias={quoteattr(aliases[word])}>{escape(word)}</sub>' if ssml else aliases[word])
        last = match.end()
    parts.append(escape(text[last:]) if ssml else text[last:])
    result = ''.join(parts)
    return '<speak>' + result.replace('. ', '.<break time="300ms"/>') + '</speak>' if ssml else result


def validate_audio(data):
    if len(data) <= 5120:
        raise ValueError(f'Audio too small: {len(data)} bytes')
    info = MP3(io.BytesIO(data)).info
    if info.length <= 1:
        raise ValueError('Audio duration must exceed one second')
    return info


class TTSProvider(abc.ABC):
    @abc.abstractmethod
    async def synthesize(self, text, lang='en', voice=None, rate=1.0):
        """Return real MP3 bytes or raise. Never return placeholder audio."""


class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text, lang='en', voice=None, rate=1.0):
        import edge_tts
        stream = edge_tts.Communicate(spoken_text(text, lang), voice or VOICES[lang], rate=f'{int((rate-1)*100):+d}%')
        return b''.join([chunk['data'] async for chunk in stream.stream() if chunk['type'] == 'audio'])


class GoogleTTSProvider(TTSProvider):
    async def synthesize(self, text, lang='en', voice=None, rate=1.0):
        from google.cloud import texttospeech as g
        def run():
            client = g.TextToSpeechClient()  # GOOGLE_APPLICATION_CREDENTIALS / ADC
            code = f'{lang}-IN'
            available = client.list_voices(language_code=code).voices
            candidates = sorted(v.name for v in available if any(t in v.name for t in ('Neural2', 'WaveNet')))
            selected = voice or os.getenv(f'GOOGLE_TTS_VOICE_{lang.upper()}')
            if selected and selected not in candidates:
                raise ValueError(f'Google neural/WaveNet voice unavailable: {selected}')
            if not candidates:
                raise ValueError(f'No Google neural/WaveNet voice for {code}')
            return client.synthesize_speech(
                input=g.SynthesisInput(ssml=spoken_text(text, lang, ssml=True)),
                voice=g.VoiceSelectionParams(language_code=code, name=selected or candidates[0]),
                audio_config=g.AudioConfig(audio_encoding=g.AudioEncoding.MP3, speaking_rate=rate),
            ).audio_content
        return await asyncio.to_thread(run)


class GTTSProvider(TTSProvider):
    async def synthesize(self, text, lang='en', voice=None, rate=1.0):
        def run():
            from gtts import gTTS
            buffer = io.BytesIO()
            gTTS(spoken_text(text, lang), lang=lang, tld='co.in', timeout=30).write_to_fp(buffer)
            return buffer.getvalue()
        return await asyncio.to_thread(run)


def get_tts_provider(name=None):
    name = (name or os.getenv('TTS_PROVIDER', 'edge')).lower()
    providers = {'edge': EdgeTTSProvider, 'edge-tts': EdgeTTSProvider, 'google': GoogleTTSProvider, 'gtts': GTTSProvider}
    if name not in providers:
        raise ValueError(f'Unknown TTS_PROVIDER: {name}')
    return providers[name]()


def compute_audio_hash(text, lang, voice=None, rate=1.0):
    token = json.dumps([text.strip(), lang, voice, rate, os.getenv('TTS_PROVIDER', 'edge'), os.getenv('TTS_FALLBACK_PROVIDER', ''), os.getenv(f'GOOGLE_TTS_VOICE_{lang.upper()}', ''), lexicon(lang)], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(token.encode()).hexdigest()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, suffix='.tmp') as file:
        temporary = Path(file.name)
        file.write(data)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


async def get_or_synthesize_audio(text, lang='en', voice=None, rate=1.0, force_refresh=False):
    validate_language(lang)
    text = text.strip()
    if not text or len(text) > MAX_TEXT or len(text.encode()) > 4500:
        raise ValueError('Text must contain one to two thousand characters and at most 4500 UTF-8 bytes')
    path = AUDIO_CACHE_DIR / f'{compute_audio_hash(text, lang, voice, rate)}.mp3'
    if path.exists() and not force_refresh:
        data = path.read_bytes()
        try:
            validate_audio(data)
            return data
        except Exception:
            logger.warning('Ignoring invalid audio cache: %s', path.name)
    try:
        data = await asyncio.wait_for(get_tts_provider().synthesize(text, lang, voice, rate), timeout=45)
        validate_audio(data)
    except Exception:
        fallback = os.getenv('TTS_FALLBACK_PROVIDER')
        if not fallback:
            raise
        logger.warning('Primary TTS failed; trying configured fallback %s', fallback)
        data = await asyncio.wait_for(get_tts_provider(fallback).synthesize(text, lang, None, rate), timeout=45)
        validate_audio(data)
    await asyncio.to_thread(atomic_write, path, data)
    return data


def build_narration_script(disease_id, section='diagnosis', lang='en'):
    section = 'diagnosis' if section == 'overview' else section
    return catalog(lang)['diseases'][disease_id][section]
