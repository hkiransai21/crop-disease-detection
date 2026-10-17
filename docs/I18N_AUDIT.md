# Translation audit — 16 October 2026

## Reproduced code-level causes

- 181 hardcoded display-string occurrences (179 distinct) bypassed i18next. The full file/line/string inventory is in `i18n-audit/frontend-strings-before.json`. Multi-line share templates are additionally identified below.
- No missing or empty keys were found among the five existing JSON bundles, and no missing literal `t()` keys were found. Exact per-language empty lists are in `i18n-audit/key-gaps-before.json`. This gate missed hardcoded components and interpolated templates entirely.
- The disease guide called `getDiseases(i18n.language)`, passing the language as the **crop filter**, resulting in an empty guide for languages such as `kn`.
- `/analyze` read `lang` from multipart form only; query-string `lang` was ignored. `/diseases` and `/history` used Query('en'), so an omitted query parameter hid Accept-Language.
- API client generally sends Accept-Language and explicit language, but the above call signature and route defaults break negotiation.
- Risk localization tries to match English risk names against already translated crop/disease strings, which can leave English names or choose an unrelated same-crop disease. Contributing factors, daily outlook, regional threats and disclaimers remain English. The complete backend display-expression inventory is in `i18n-audit/backend-strings-before.json`.
- Confidence labels and errors are English. Historic guest results retain old-language risk/confidence fields after switching language.
- WhatsApp report text is hardcoded in two long English/Hindi templates, defaults to Hindi irrespective of the selected language, and offers no Tamil/Telugu/Kannada. Both templates invent a universal 35–40 gram chemical dose per 15 L tank. The calculator independently assumes a 2.5 g/L chemical dose and 5 ml/L organic dose for every disease. Neither comes from a product-specific source. These must not be reproduced as localized treatment advice.
- Low-confidence results still display treatment, a dosage calculator and treatment audio. An uncertainty badge alone does not prevent confident advice.
- The font is externally hosted Inter. No Indic fonts are bundled, and there is no offline font cache. A device lacking Indic fallback fonts can show missing glyphs. HTML correctly declares UTF-8; existing supported-language JSON decodes as UTF-8. PowerShell's default console can display mojibake even when files are valid; byte/codepoint tests are necessary.
- No first-launch language gate. Browser detection selects language without a deliberate choice. The existing selector requires opening a dropdown before choosing a language.
- Extra language disease/glossary files and old translation-generator dictionaries remain on disk, despite the prior audio UI restriction.

## Content and review findings

The original translations are not reliably disease-specific. For example, the Kannada Apple scab symptom text says generically that spots appear and leaves dry, omitting the English source's olive-brown velvety spots and fruit cracking. Generic organic/chemical/prevention replacements discard named ingredients and FRAC details. The previous parity test's superficial checks did not establish complete content parity.

Risk wording in Hindi and Tamil instructs immediate protective spraying in high weather risk, even though the English risk summary describes favorable conditions rather than prescribing a spray. This introduces advice during translation. English UI phrases such as “environmental telemetry,” “university protocols,” and “extension-verified” are unnecessarily technical or imply review that has not occurred. These are being replaced with plain language and an explicit review status.

Every regional entry that lacks documented human review must be machine_suggested. Descriptive disease labels retain the English term in brackets; they are not claimed to be established local common names. Native-speaker review is still required for common names, transliterations, glossary consistency, symptom specificity and natural imperative wording.

Scientific names, canonical keys, citations, product/active-ingredient names and locked numeric units are intentional untranslated identifiers, not UI translation gaps. They are kept byte-identical. Scientific names, canonical identifiers and source citations are excluded from editable review rows.

Additional wording findings during draft review:

- The old Kannada glossary incorrectly translated Early/Late Blight as monsoon-season terms (`ಮುಂಗಾರು`/`ಹಿಂಗಾರು`). These names describe different diseases, not simply seasons. Replace with descriptive leaf-symptom labels plus the English disease name.
- The old Kannada leaf-mold label contained Telugu glyphs (`ಬೂజు`) inside Kannada text. This is a mixed-script content error, not missing font support.
- The local translation model rendered Apple Scab as Hindi “सेब का कफ” (cough) and Tamil “ஆப்பிள் கஞ்சி” (porridge). These generated labels are rejected; use the existing descriptive disease glossary, correct known problems, and keep English names visible. Machine output must not be treated as approved farmer terminology.
- English scientific names, active ingredients, product names, source citations, units and canonical identifiers are intentional preserved text. They are not evidence that an entire recommendation was translated or reviewed.

A script-level audit and screenshot inspection also found **71 existing Kannada UI keys containing Hindi text**, including the entire feedback/history sections and many result labels. Key-completeness tests passed because the keys existed and were nonempty. `kannada-wrong-language-before.json` lists every affected original key. These are corrected, and the regression suite now checks for unexpected Indic scripts as well as missing keys.
