"""Import reviewed translations from CSV back into AgriShield i18n data files with safety validations."""
import csv
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
I18N_DIR = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = I18N_DIR / "glossary"


def import_language_from_csv(csv_path: Path):
    if not csv_path.exists():
        print(f"Error: CSV file '{csv_path}' does not exist.")
        return

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    if not reader:
        print(f"Error: Empty CSV in {csv_path}")
        return

    lang = reader[0]["language"].strip()
    glossary_path = GLOSSARY_DIR / f"{lang}.json"
    diseases_path = I18N_DIR / lang / "diseases.json"

    if not glossary_path.exists() or not diseases_path.exists():
        print(f"Error: Destination files for {lang} not found.")
        return

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_data = json.load(f)
    with open(diseases_path, "r", encoding="utf-8") as f:
        diseases_data = json.load(f)

    diseases_list = diseases_data.get("diseases", [])
    disease_dict = {d["id"]: d for d in diseases_list}

    updated_count = 0
    for row in reader:
        cid = row["canonical_id"].strip()
        if not cid:
            continue

        # Update glossary entry
        if cid in glossary_data.get("diseases", {}):
            g_entry = glossary_data["diseases"][cid]
            if row.get("common_name"):
                g_entry["common_name"] = row["common_name"].strip()
            if row.get("transliteration"):
                g_entry["transliteration"] = row["transliteration"].strip()
            if row.get("tts_text"):
                g_entry["tts_text"] = row["tts_text"].strip()
            if row.get("source"):
                g_entry["source"] = row["source"].strip()
            if row.get("review_status") in ["draft", "machine_suggested", "expert_reviewed"]:
                g_entry["review_status"] = row["review_status"].strip()

        # Update disease entry
        if cid in disease_dict:
            d_entry = disease_dict[cid]
            if row.get("common_name"):
                d_entry["disease_name"] = row["common_name"].strip()
            if row.get("symptoms"):
                d_entry["symptoms"] = row["symptoms"].strip()
            if row.get("prevention_steps"):
                d_entry["prevention_steps"] = [s.strip() for s in row["prevention_steps"].split("|") if s.strip()]
            if row.get("organic_controls"):
                d_entry["organic_controls"] = [s.strip() for s in row["organic_controls"].split("|") if s.strip()]
            if row.get("chemical_controls"):
                d_entry["chemical_controls"] = [s.strip() for s in row["chemical_controls"].split("|") if s.strip()]
            if row.get("review_status") in ["draft", "machine_suggested", "expert_reviewed"]:
                d_entry["review_status"] = row["review_status"].strip()

        updated_count += 1

    with open(glossary_path, "w", encoding="utf-8") as f:
        json.dump(glossary_data, f, ensure_ascii=False, indent=2)
    with open(diseases_path, "w", encoding="utf-8") as f:
        json.dump(diseases_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully re-imported {updated_count} reviewed entries for language '{lang}'.")


def main():
    parser = argparse.ArgumentParser(description="Import reviewed translations from CSV back into JSON.")
    parser.add_argument("csv_file", type=Path, help="Path to reviewed CSV file")
    args = parser.parse_args()

    import_language_from_csv(args.csv_file)


if __name__ == "__main__":
    main()
