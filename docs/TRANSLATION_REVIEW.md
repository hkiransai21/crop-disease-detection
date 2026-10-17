# Translation review

The supported languages are English, Hindi, Tamil, Telugu and Kannada. Drafts are machine suggestions, not verified farmer terminology or approved pesticide advice. A native-speaking farmer and an agricultural adviser should review each non-English catalog before release.

Run `python scripts/export_translations_for_review.py --output translation-review` to create UTF-8 CSV files. Open them with UTF-8 encoding, keeping the key and English columns unchanged. Each row contains the translation, review status and reviewer notes.

Check each disease name against local usage. Prefer an understandable description when a recognized local name is unavailable. Keep the English/scientific name in brackets. Verify the transliteration aloud. Use short everyday sentences and consistent glossary terms. Read symptoms, immediate actions, organic options, chemical options and prevention together so instructions retain their meaning.

Keep every active ingredient, product name, number, unit and interval exactly as in English. Never infer a dose or substitute another pesticide. Confirm recommendations against the local registered product label and agriculture office. Keep the full safety notice: read the label, wear protection, protect children and water sources, and consult the local agriculture office. English source recommendations also need agronomic review.

For uncertain results, confirm the screen asks for a better photo or expert help and does not recommend treatment confidently. Test language switching and read the small-screen result aloud. Check the local font offline, text wrapping and accessible controls.

Set an individually checked row to `human_reviewed`. Put the reviewer name, date, locale and any agronomic qualifications in reviewer notes. Leave unchecked rows as `machine_suggested`. Import with `python scripts/import_reviewed_translations.py translation-review/kn.csv --lang kn` (substitute hi, ta or te). The importer rejects changed English, missing values, duplicated keys and altered ingredient/number/unit tokens before writing. Row-level review metadata is stored in `reviews.json`; it does not claim the entire disease was reviewed.

Rerun the catalog and frontend tests after import. Regenerate and separately listen to narration when its scripts change: written-text review does not certify recorded pronunciation. All current draft strings require native-speaker review unless their row-level record explicitly states otherwise.

Current draft provenance: the expanded translations were prepared with an isolated local NLLB translation model and explicit glossary corrections. The runtime app uses only committed JSON. Romanizations use automatic IAST transliteration; they still need a native-speaker pronunciation check. No translation model or translation service is required to run the app.

The committed review CSVs are in `docs/translation-review/`. There are 1,661 editable rows per regional language. Scientific names, canonical identifiers and source citations are excluded from editing. Every row currently needs human review. Use `--check` on the import command to validate a CSV without changing files.
