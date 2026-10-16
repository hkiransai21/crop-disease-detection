"""Static narration delivery and bounded dynamic TTS fallback."""
import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from backend.app.api.deps import limiter
from backend.app.services.i18n import get_supported_languages, get_localized_glossary
from backend.app.services.tts import AUDIO_DIR, catalog, get_or_synthesize_audio

Language = Literal['en', 'hi', 'ta', 'te', 'kn']
router = APIRouter(prefix='/audio', tags=['Audio'])
logger = logging.getLogger(__name__)


@router.get('/languages')
async def languages():
    return get_supported_languages()


@router.get('/glossary/{lang}')
async def glossary(lang: Language):
    return get_localized_glossary(lang)


@router.get('/catalog/{lang}')
async def narration_catalog(lang: Language):
    return catalog(lang)


@router.get('/manifest/{lang}')
async def manifest(lang: Language):
    data = catalog(lang)
    paths = [f'{key}/{section}' for key, sections in data['diseases'].items() for section in sections]
    paths += [f'_common/{key}' for key in data['prompts']]
    return {'language': lang, 'files': [f'/api/v1/audio/files/{lang}/{path}.mp3' for path in paths]}


@router.get('/files/{lang}/{disease_id}/{filename}')
async def static_audio(lang: Language, disease_id: str, filename: str):
    data = catalog(lang)
    sections = data['prompts'] if disease_id == '_common' else data['diseases'].get(disease_id, {})
    if not filename.endswith('.mp3') or filename[:-4] not in sections:
        raise HTTPException(404, 'Unknown narration')
    path = AUDIO_DIR / lang / disease_id / filename
    if not path.is_file():
        raise HTTPException(404, 'Audio has not been generated')
    return FileResponse(path, media_type='audio/mpeg', headers={'Cache-Control': 'no-store'})


@router.get('/tts')
@limiter.limit('10/minute')
async def dynamic_tts(request: Request, text: str = Query(..., min_length=1, max_length=2000), lang: Language = 'en'):
    if not text.strip() or len(text.encode('utf-8')) > 4500:
        raise HTTPException(422, 'Text is empty or exceeds 4500 UTF-8 bytes; split into shorter sections')
    try:
        data = await get_or_synthesize_audio(text, lang)
    except Exception as exc:
        logger.error('TTS failed for %s: %s: %s', lang, type(exc).__name__, str(exc).split('url=')[0])
        raise HTTPException(503, 'Audio synthesis unavailable', headers={'Cache-Control': 'no-store'}) from exc
    return Response(data, media_type='audio/mpeg', headers={'Cache-Control': 'no-store'})


@router.get('/{disease_id}/{section}')
async def legacy_static_audio(disease_id: str, section: str, lang: Language = 'en'):
    # Existing bookmarks can still play, but never synthesize on this route.
    section = 'diagnosis' if section == 'overview' else section
    return await static_audio(lang, disease_id, f'{section}.mp3')
