# AgriShield Agronomic Translation Review Guide

This guide establishes the standardized workflow for native-speaking agronomists, plant pathologists, and agricultural extension workers reviewing AgriShield's regional translations.

---

## 1. Review Status Lifecycle

Every terminology entry and disease guidance monograph tracks its verification status:

| Status | Meaning | Action Needed |
| :--- | :--- | :--- |
| `draft` | Initial translation under active editing | Complete draft terminology |
| `machine_suggested` | Algorithmically generated from university databases | Native agronomist review required |
| `expert_reviewed` | Verified by a native-speaking plant pathologist or extension officer | Approved for production advisory |

---

## 2. Reviewer Tooling: CSV Export & Re-import

To allow agronomists to review translations in Microsoft Excel, Google Sheets, or LibreOffice without editing JSON files directly, AgriShield provides automated CSV tools:

### 2.1 Export to CSV
Export translations to `docs/reviews/translation_review_{lang}.csv`:
```bash
python scripts/export_translations_csv.py --lang te     # Export Telugu only
python scripts/export_translations_csv.py --lang all    # Export all 8 regional languages
```

### 2.2 Review Guidelines for Agronomists
Open the CSV and evaluate the following columns:
1. **`common_name`**: Must be the actual term used by local farmers in the field (e.g. *ముందస్తు ఆకు ఎండు తెగులు* for Tomato Early Blight in Andhra Pradesh/Telangana). Avoid literal English transliterations when an authentic vernacular name exists.
2. **`transliteration`**: Latin phonetic spelling for search.
3. **`tts_text`**: Ensure phonetic phrasing reads naturally when spoken aloud.
4. **`symptoms`**: Keep sentences short and clear (Grade 6 reading level). Avoid dense botanical jargon without plain explanation.
5. **`prevention_steps` & `organic_controls`**: Prioritize low-cost and bio-control methods first.
6. **`chemical_controls`**: **STRICT SAFETY RULE:** Active ingredient names must stay in Latin script or standard label spelling (e.g., *Mancozeb 75% WP*, *Copper Oxychloride 50% WP*). Exact dosages (e.g., $2.5\text{ g/L}$, $5\text{ ml/L}$) must be numerically identical to label instructions.
7. **`review_status`**: Change from `machine_suggested` to `expert_reviewed` once verified.
8. **`reviewer_name` & `reviewer_notes`**: Record reviewer name, university/KVK affiliation, and field notes.

### 2.3 Re-import to JSON
Once review is completed and saved to CSV, import the verified data back into the codebase:
```bash
python scripts/import_translations_csv.py docs/reviews/translation_review_te.csv
```

The script updates `backend/app/data/i18n/glossary/{lang}.json` and `backend/app/data/i18n/{lang}/diseases.json`.

---

## 3. Audio Listening QA Checklist

To verify neural audio naturalness, pronunciation, and pacing:
1. Reviewers use the spreadsheet template generated at `docs/audio_qa_checklist.csv` (contains 912 evaluation rows covering all 38 diseases × 8 languages × 3 sections).
2. Listen to playback using the in-app player or `GET /api/v1/audio/{disease_id}/{section}?lang={lang}`.
3. Score each section on:
   - **Name pronunciation correct (Y/N)**
   - **Naturalness (1 to 5 stars)**
   - **Terminology correct (Y/N)**
   - **Cadence and pause acceptable (Y/N)**
   - **Reviewer comments and phonetic corrections**

---

## 4. Automated Safety & Parity Gate

Before any reviewed translations can be merged, run the automated verification suite:
```bash
pytest backend/tests/test_i18n.py -v
```

This gate validates:
- [x] All 38 classes are present without missing keys.
- [x] All chemical dosages ($2.5\text{ g/L}$, $5\text{ ml/L}$, $15\text{ L}$) match the English reference exactly.
- [x] No raw emojis exist in audio scripts.
- [x] Schema integrity is strictly enforced.
