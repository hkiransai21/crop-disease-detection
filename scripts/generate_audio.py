"""Script to pre-generate and cache compressed neural audio for all 38 diseases and sections across regional languages."""
import asyncio
import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.services.i18n import get_i18n_config, load_localized_knowledge_base
from backend.app.services.tts import build_narration_script, get_or_synthesize_audio, AUDIO_CACHE_DIR


async def pregenerate_all_audio(
    target_languages=None,
    dry_run: bool = False,
    force: bool = False
):
    """Pre-generate and cache MP3 audio files for 38 classes × sections × languages."""
    cfg = get_i18n_config()
    supported_langs = [l["code"] for l in cfg.get("supported_languages", []) if l.get("is_active", True)]
    
    langs_to_process = target_languages or supported_langs
    sections = ["overview", "treatment", "prevention"]
    
    print(f"Starting audio pre-generation for {len(langs_to_process)} languages: {langs_to_process}")
    print(f"Target Cache Directory: {AUDIO_CACHE_DIR}")
    
    total_generated = 0
    total_skipped = 0
    
    for lang in langs_to_process:
        kb = load_localized_knowledge_base(lang)
        print(f"\nProcessing language: '{lang}' ({len(kb)} classes)...")
        
        for disease_id in kb.keys():
            for section in sections:
                script = build_narration_script(disease_id, section, lang)
                
                if dry_run:
                    print(f"  [DRY-RUN] {lang} | {disease_id} | {section} -> Script length: {len(script)} chars")
                    total_generated += 1
                    continue
                
                try:
                    audio_bytes = await get_or_synthesize_audio(
                        text=script,
                        lang=lang,
                        rate=1.0,
                        force_refresh=force
                    )
                    total_generated += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to synthesize {disease_id}/{section} in {lang}: {e}")
                    
    print(f"\nAudio generation completed! Total files generated/cached: {total_generated}")


def main():
    parser = argparse.ArgumentParser(description="AgriShield Audio Narration Pre-Generator")
    parser.add_argument("--lang", type=str, help="Specific language code (e.g. hi, te, ta, kn, ml, mr, bn, es, en)")
    parser.add_argument("--dry-run", action="store_true", help="Print scripts without making TTS network calls")
    parser.add_argument("--force", action="store_true", help="Force re-generation and overwrite existing cache")
    args = parser.parse_args()

    target_langs = [args.lang] if args.lang else None
    asyncio.run(pregenerate_all_audio(target_languages=target_langs, dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
