# Translation verification — 17 October 2026

The audit is in [I18N_AUDIT.md](I18N_AUDIT.md), with complete original string/key inventories under `i18n-audit/`.

Implemented: only en/hi/ta/te/kn; JSON-backed UI strings; first-launch native-script language choice and persistent language controls; bundled, offline-cached Noto Indic fonts; localized analyze/diseases/history responses and errors; guest-result re-localization; 38 disease records per language with canonical identifiers and scientific names; protected ingredient/number/unit checks; uncertainty-only presentation for low-confidence results; and CSV review tooling. Universal pesticide-dose calculations were removed because they were not product-specific source recommendations.

The model, ONNX artifacts, preprocessing, calibration, inference implementation, risk calculation service and English prediction knowledge-base YAML were not modified. Changes to analyze/history routes format responses and carry language metadata; tests check canonical labels and confidence values remain unchanged.

## Real command output

Backend:

```text
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
102 passed in 11.52s
```

Frontend:

```text
npm test -- --reporter=dot
0 hardcoded display strings (0 distinct)
0 UI references missing from the English catalog
Test Files  4 passed (4)
Tests  25 passed (25)
```

The frontend suite emits existing React Router v7 migration notices. They are warnings, not failed assertions. The source audit checks display literals and static key references; dynamic keys are also exercised by locale completeness tests and browser checks.

Production build:

```text
npm run build
✓ 1536 modules transformed.
dist/index.html                   0.82 kB │ gzip:   0.48 kB
dist/assets/index-C5ImdgMG.css   40.14 kB │ gzip:   7.02 kB
dist/assets/index-DNIZXwBe.js   417.88 kB │ gzip: 139.58 kB
✓ built in 22.32s
```

Browser translation checks (real headless Edge, fixed result fixtures, 360×640 viewport):

```text
First launch, persisted choice, one-tap change: PASS
language  horizontal_overflow  page_errors  offline_fonts
en        0                    0            true
hi        0                    0            true
ta        0                    0            true
te        0                    0            true
kn        0                    0            true
```

Raw browser results: [results.json](i18n-screenshots/results.json). These screenshots exercise real React rendering using representative seeded result data, not a new model prediction. Top-of-screen and treatment captures were visually inspected for glyph rendering and clipping. Treatment-only captures hide the sticky navigation during capture so it does not obscure the cropped artifact; the full result captures retain the real navigation.

| Language | Result at 360×640 | Full result | Treatment |
|---|---|---|---|
| English | [Screenshot](i18n-screenshots/en-360x640.png) | [Full](i18n-screenshots/en-full.png) | [Treatment](i18n-screenshots/en-treatment.png) |
| Hindi | [Screenshot](i18n-screenshots/hi-360x640.png) | [Full](i18n-screenshots/hi-full.png) | [Treatment](i18n-screenshots/hi-treatment.png) |
| Tamil | [Screenshot](i18n-screenshots/ta-360x640.png) | [Full](i18n-screenshots/ta-full.png) | [Treatment](i18n-screenshots/ta-treatment.png) |
| Telugu | [Screenshot](i18n-screenshots/te-360x640.png) | [Full](i18n-screenshots/te-full.png) | [Treatment](i18n-screenshots/te-treatment.png) |
| Kannada | [Screenshot](i18n-screenshots/kn-360x640.png) | [Full](i18n-screenshots/kn-full.png) | [Treatment](i18n-screenshots/kn-treatment.png) |

Audio regression output:

```text
en: static playback 7.01s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
hi: static playback 8.78s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
ta: static playback 6.96s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
te: static playback 7.32s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
kn: static playback 7.99s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
```

An earlier audio smoke-test run timed out because its prefix-based button locator selected the section button for labels beginning with `{{lang}}`. The script now resolves the full translated accessible name; all five languages pass the real playback check.

CSV validation:

```text
Validated 1661 review rows for hi; no files changed.
Validated 1661 review rows for ta; no files changed.
Validated 1661 review rows for te; no files changed.
Validated 1661 review rows for kn; no files changed.
```

## Human review still required

All 152 regional disease records, their romanizations and glossaries remain `machine_suggested`. Every regional UI/backend review row is pending human review. The exact lists are [Hindi](translation-review/hi.csv), [Tamil](translation-review/ta.csv), [Telugu](translation-review/te.csv) and [Kannada](translation-review/kn.csv), with 1,661 editable rows each. Follow [TRANSLATION_REVIEW.md](TRANSLATION_REVIEW.md).

Numeric/ingredient parity and correct script rendering do not establish agronomic accuracy or natural local wording. These are usable review drafts, not human-certified translations. English source recommendations also require local product-label/agriculture-office confirmation. Existing narration remains separately authored and requires its own pronunciation review when scripts change.
