"""Real MP3 contract checks plus deterministic provider-failure regressions."""
import io
import pytest
from mutagen.mp3 import MP3
from backend.app.services import tts
from backend.app.api.deps import limiter


@pytest.fixture(autouse=True)
def reset_limits():
    limiter.reset()


@pytest.mark.asyncio
@pytest.mark.parametrize('lang', tts.LANGUAGES)
@pytest.mark.parametrize('section', tts.SECTIONS)
async def test_static_audio_is_real_playable_mp3(client, lang, section):
    response = await client.get(f'/api/v1/audio/files/{lang}/Apple___Apple_scab/{section}.mp3')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'audio/mpeg'
    assert len(response.content) > 5120
    info = MP3(io.BytesIO(response.content)).info
    assert info.length > 1
    assert info.channels == 1
    assert 31000 <= info.bitrate <= 49000


@pytest.mark.asyncio
@pytest.mark.parametrize('lang', tts.LANGUAGES)
async def test_dynamic_audio_and_cache(client, monkeypatch, tmp_path, lang):
    data = (tts.AUDIO_DIR / lang / 'Apple___Apple_scab/diagnosis.mp3').read_bytes()
    calls = []
    class RecordedProvider(tts.TTSProvider):
        async def synthesize(self, text, language='en', voice=None, rate=1):
            calls.append(language)
            return data
    monkeypatch.setattr(tts, 'AUDIO_CACHE_DIR', tmp_path)
    monkeypatch.setattr(tts, 'get_tts_provider', lambda: RecordedProvider())
    for _ in range(2):
        response = await client.get('/api/v1/audio/tts', params={'text': 'Check the leaves carefully before choosing a treatment.', 'lang': lang})
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/mpeg'
        assert len(response.content) > 5120
        assert MP3(io.BytesIO(response.content)).info.length > 1
    assert calls == [lang]
    assert len(list(tmp_path.glob('*.mp3'))) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('broken', [b'', b'\xff\xfb\x90\x64' + b'fake' * 82, b'x' * 6000])
async def test_never_cache_or_serve_fake_success(client, monkeypatch, tmp_path, broken):
    class BrokenProvider(tts.TTSProvider):
        async def synthesize(self, *args):
            return broken
    monkeypatch.delenv('TTS_FALLBACK_PROVIDER', raising=False)
    monkeypatch.setattr(tts, 'AUDIO_CACHE_DIR', tmp_path)
    monkeypatch.setattr(tts, 'get_tts_provider', lambda: BrokenProvider())
    response = await client.get('/api/v1/audio/tts', params={'text': 'Test narration', 'lang': 'kn'})
    assert response.status_code == 503
    assert response.headers['cache-control'] == 'no-store'
    assert not list(tmp_path.glob('*.mp3'))


@pytest.mark.asyncio
async def test_bad_cache_is_replaced(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, 'AUDIO_CACHE_DIR', tmp_path)
    real = (tts.AUDIO_DIR / 'en/Apple___Apple_scab/diagnosis.mp3').read_bytes()
    path = tmp_path / (tts.compute_audio_hash('Test narration', 'en') + '.mp3')
    path.write_bytes(b'bad cache')
    class Provider(tts.TTSProvider):
        async def synthesize(self, *args): return real
    monkeypatch.setattr(tts, 'get_tts_provider', lambda: Provider())
    assert await tts.get_or_synthesize_audio('Test narration') == real
    assert path.read_bytes() == real


@pytest.mark.asyncio
async def test_audio_limits_and_languages(client):
    for params in ({'text': 'x', 'lang': 'es'}, {'text': ' '}, {'text': 'x' * 2001}, {'text': 'ಕ' * 1600}):
        assert (await client.get('/api/v1/audio/tts', params=params)).status_code == 422
    assert (await client.get('/api/v1/audio/files/en/unknown/diagnosis.mp3')).status_code == 404
    response = await client.get('/api/v1/audio/languages')
    assert {x['code'] for x in response.json()['languages']} == set(tts.LANGUAGES)


@pytest.mark.asyncio
async def test_rate_limit(client, monkeypatch):
    from backend.app.api.routes import audio
    async def recorded(*args):
        return (tts.AUDIO_DIR / 'en/Apple___Apple_scab/diagnosis.mp3').read_bytes()
    monkeypatch.setattr(audio, 'get_or_synthesize_audio', recorded)
    codes = [(await client.get('/api/v1/audio/tts', params={'text': 'Test narration'})).status_code for _ in range(11)]
    assert codes == [200] * 10 + [429]


def test_narration_inventory_and_ssml():
    import re
    for lang in tts.LANGUAGES:
        data = tts.catalog(lang)
        assert len(data['diseases']) == 38
        for sections in data['diseases'].values():
            assert set(sections) == set(tts.SECTIONS)
            for text in sections.values():
                assert not re.search(r'\d|[%&<>/]', text)
                assert len(text) <= 2000 and len(text.encode()) <= 4500
        ssml = tts.spoken_text('Mancozeb. Check leaves.', lang, ssml=True)
        assert '<sub alias=' in ssml and '<break ' in ssml
