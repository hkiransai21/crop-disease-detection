"""Multilingual Audio Narration and TTS API Endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Response, Request, Depends
from backend.app.schemas.i18n import SupportedLanguagesResponse, AudioSynthesizeRequest
from backend.app.services.i18n import get_supported_languages, resolve_language, get_localized_disease_entry, get_localized_glossary
from backend.app.services.tts import get_or_synthesize_audio, build_narration_script
from backend.app.api.deps import limiter
from backend.app.core.config import settings

router = APIRouter(prefix="/audio", tags=["Multilingual Audio Narration"])


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def list_supported_audio_languages():
    """Retrieve all configured regional languages, native labels, and neural voice models."""
    return get_supported_languages()


@router.get("/glossary/{lang}")
async def get_language_glossary(lang: str):
    """Retrieve curated disease names and agronomic terminology glossary for a language."""
    glossary = get_localized_glossary(lang)
    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glossary not found for language '{lang}'."
        )
    return glossary


@router.get("/{disease_id}/{section}")
async def get_disease_section_audio(
    disease_id: str,
    section: str,
    lang: Optional[str] = Query("en", description="Language code (e.g. en, hi, te, ta, kn, ml, mr, bn, es)"),
    rate: float = Query(1.0, ge=0.5, le=2.0, description="Speech rate multiplier (0.5 to 2.0)"),
    force_refresh: bool = Query(False, description="Bypass cache and force re-synthesis")
):
    """
    Fetch pre-rendered or on-demand synthesized spoken audio narration for a specific disease section.
    Sections: 'overview', 'treatment', 'prevention'.
    Returns streaming MP3 audio with long-lived browser cache headers.
    """
    resolved_lang = resolve_language(lang)
    if section not in ("overview", "treatment", "prevention"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid section. Must be one of: overview, treatment, prevention."
        )

    entry = get_localized_disease_entry(disease_id, resolved_lang)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease '{disease_id}' not found in knowledge base."
        )

    narration_text = build_narration_script(disease_id, section, resolved_lang)
    audio_bytes = await get_or_synthesize_audio(
        text=narration_text,
        lang=resolved_lang,
        rate=rate,
        force_refresh=force_refresh
    )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'inline; filename="{disease_id}_{section}_{resolved_lang}.mp3"',
            "Cache-Control": "public, max-age=86400, stale-while-revalidate=604800",
            "X-Language-Code": resolved_lang,
            "X-Audio-Section": section
        }
    )


@router.post("/synthesize")
@limiter.limit("30/minute")
async def synthesize_dynamic_text(
    request: Request,
    payload: AudioSynthesizeRequest
):
    """
    Synthesize arbitrary farmer advisory or risk text into natural neural audio with rate limiting.
    """
    if not payload.text or len(payload.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    resolved_lang = resolve_language(payload.lang)
    audio_bytes = await get_or_synthesize_audio(
        text=payload.text,
        lang=resolved_lang,
        voice=payload.voice,
        rate=payload.rate
    )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": 'inline; filename="dynamic_narration.mp3"',
            "Cache-Control": "public, max-age=3600",
            "X-Language-Code": resolved_lang
        }
    )
