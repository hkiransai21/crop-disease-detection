"""Generate audio listening review QA checklist spreadsheet template for native speakers."""
import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.services.i18n import get_supported_languages, load_localized_knowledge_base
from backend.app.services.tts import build_narration_script
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = DOCS_DIR / "audio_qa_checklist.csv"


def generate_audio_qa_checklist():
    cfg = get_supported_languages()
    languages = [l.code for l in cfg.languages if l.code != "en"]
    sections = ["overview", "treatment", "prevention"]

    fieldnames = [
        "language",
        "disease_id",
        "crop_name",
        "disease_name",
        "section",
        "tts_voice_configured",
        "narration_script_preview",
        "name_pronunciation_correct_yn",
        "naturalness_score_1_to_5",
        "terminology_correct_yn",
        "cadence_and_pause_acceptable_yn",
        "reviewer_native_speaker_name",
        "reviewer_feedback_and_corrections"
    ]

    total_rows = 0
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lang in languages:
            voice = next((l.tts_voice for l in cfg.languages if l.code == lang), "default")
            kb = load_localized_knowledge_base(lang)

            for cid, entry in kb.items():
                for section in sections:
                    script = build_narration_script(cid, section, lang)
                    preview = (script[:120] + "...") if len(script) > 120 else script

                    writer.writerow({
                        "language": lang,
                        "disease_id": cid,
                        "crop_name": entry.crop,
                        "disease_name": entry.disease_name,
                        "section": section,
                        "tts_voice_configured": voice,
                        "narration_script_preview": preview.replace("\n", " "),
                        "name_pronunciation_correct_yn": "",
                        "naturalness_score_1_to_5": "",
                        "terminology_correct_yn": "",
                        "cadence_and_pause_acceptable_yn": "",
                        "reviewer_native_speaker_name": "",
                        "reviewer_feedback_and_corrections": ""
                    })
                    total_rows += 1

    print(f"Generated Audio Listening Review QA Checklist at {OUTPUT_CSV} ({total_rows} evaluation rows).")


if __name__ == "__main__":
    generate_audio_qa_checklist()
