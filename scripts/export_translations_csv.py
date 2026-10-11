"""Export multilingual agricultural glossaries and treatment guidance to CSV for expert review."""
import csv
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
I18N_DIR = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = I18N_DIR / "glossary"
OUTPUT_DIR = BASE_DIR / "docs" / "reviews"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_language_to_csv(lang: str, output_path: Path):
    glossary_path = GLOSSARY_DIR / f"{lang}.json"
    diseases_path = I18N_DIR / lang / "diseases.json"

    if not glossary_path.exists() or not diseases_path.exists():
        print(f"Warning: Data files for language '{lang}' not found.")
        return

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_data = json.load(f)
    with open(diseases_path, "r", encoding="utf-8") as f:
        diseases_data = json.load(f)

    disease_map = {d["id"]: d for d in diseases_data.get("diseases", [])}

    fieldnames = [
        "canonical_id",
        "language",
        "common_name",
        "transliteration",
        "scientific_name",
        "tts_text",
        "symptoms",
        "prevention_steps",
        "organic_controls",
        "chemical_controls",
        "source",
        "review_status",
        "reviewer_name",
        "reviewer_notes"
    ]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for cid, g_entry in glossary_data.get("diseases", {}).items():
            d_entry = disease_map.get(cid, {})

            writer.writerow({
                "canonical_id": cid,
                "language": lang,
                "common_name": g_entry.get("common_name", ""),
                "transliteration": g_entry.get("transliteration", ""),
                "scientific_name": g_entry.get("scientific_name", ""),
                "tts_text": g_entry.get("tts_text", ""),
                "symptoms": d_entry.get("symptoms", ""),
                "prevention_steps": " | ".join(d_entry.get("prevention_steps", [])),
                "organic_controls": " | ".join(d_entry.get("organic_controls", [])),
                "chemical_controls": " | ".join(d_entry.get("chemical_controls", [])),
                "source": g_entry.get("source", ""),
                "review_status": g_entry.get("review_status", "machine_suggested"),
                "reviewer_name": "",
                "reviewer_notes": ""
            })

    print(f"Exported {len(glossary_data.get('diseases', {}))} entries to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Export i18n data to CSV for agronomist review.")
    parser.add_argument("--lang", default="all", help="Target language code or 'all'")
    args = parser.parse_args()

    languages = ["hi", "te", "ta", "kn", "ml", "mr", "bn", "es"] if args.lang == "all" else [args.lang]

    for lang in languages:
        csv_file = OUTPUT_DIR / f"translation_review_{lang}.csv"
        export_language_to_csv(lang, csv_file)


if __name__ == "__main__":
    main()
