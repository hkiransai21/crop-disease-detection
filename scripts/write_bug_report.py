"""Build the review report from captured evidence, not guessed outcomes."""
import json
from pathlib import Path
from backend.app.schemas.weather import WeatherSummary
from backend.app.services.risk import evaluate_disease_risk
from backend.app.services.i18n import localize_risk_assessment

ROOT=Path('docs/bug-evidence')
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
before=read('before/images.json');after=read('after/images.json')
assert read('before/model-hashes.json')==read('after/model-hashes.json')
assert all(a['logits']==b['logits'] for a,b in zip(before,after))
live=read('after/live-weather.json')
for row in live:
    row['results']={key:{lang:localize_risk_assessment(evaluate_disease_risk(key,WeatherSummary(**row['summary'])),lang).model_dump() for lang in ('en','hi','ta','te','kn')} for key in ('Tomato___Late_blight','Tomato___Bacterial_spot','Squash___Powdery_mildew')}
(ROOT/'after/live-weather.json').write_text(json.dumps(live,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['''# Diagnosis and weather pipeline repair — 26 October 2026

## Scope and honest completion limits

Model weights, ONNX files, labels, temperature and training code are unchanged. All seven model-directory artifact hashes match the baseline, and the two available fixture raw output arrays are exactly equal before/after. Existing user changes in the working tree were preserved.

**No real labelled leaf photographs were supplied.** The only two images in `sample_images/` are drawings, copied unchanged to `backend/tests/fixtures/leaves/`. `ml/data/` is absent. Therefore six-real-image accuracy, three-different-real-leaf browser validation, and in-distribution versus field entropy distributions are **not completed**. No synthetic examples were substituted for real accuracy evidence. Six injected-logit API tests are mapping tests only. Browser checks distinguish two actual uploads from three explicitly mocked class responses.

## Root causes established before edits

The baseline regression run was **9 failed, 15 passed**; see [original failing output](before/tests.txt) and [pre-edit findings](ROOT_CAUSES_BEFORE.md).

1. **Repeated immediate advice:** every class in each of five language catalogs had the same `immediate_actions` array (one unique array across 38 classes). ActionChecklist renders that array. Symptoms, organic controls and prevention already had 38 distinct values in each language. Thus the broad claim that *all* symptom/treatment/prevention content was constant is **not reproduced**; the confirmed content defect is the immediate-action section. It now uses existing class-specific localized controls; healthy classes use maintenance/prevention. All entries remain `machine_suggested`. No new chemical names or dosages were created.
2. **Repeated weather advice:** no location generated baseline risk=40; weather failures generated fixed 22 °C/65% current weather. RiskGauge prominently rendered only one generic string per level, omitted the score and all measured contributing factors, and used static generic audio. These combined into apparently constant advice. Failures now produce no live score, and the UI shows location/unavailable states and a working retry. Live risk displays score, class-specific prevention/action, measured reasons and matching dynamic narration.
3. Additional confirmed unsafe paths: absent ONNX sessions produced random Dirichlet predictions; unknown classes produced risk=50, while localization returned None. These now fail explicitly. Missing localized records/critical advice fields also raise errors.
4. Fresh result routing previously preferred a saved language variant over incoming route data. The regression exercises a collision and now verifies fresh data wins. App already assigned guest UUIDs before this task, so backend's formerly constant guest ID was **not** the primary cause in this frontend; backend IDs are now unique too.

## Suspect-by-suspect verdict

| Bug 1 suspect | Evidence / verdict |
|---|---|
| a: same ONNX output | False for the two drawings: different logits/top-1. Real-photo behavior remains unmeasured. RGB conversion, bilinear resize, ImageNet mean/std, float32 NCHW/batch are present. Training eval actually resizes shorter side to `int(224*1.14)=255`, backend uses 256. This mismatch is recorded, not silently changed, to preserve raw-output parity. |
| b: constant/wrong class mapping | No constant index: two different labels reach matching records. Six controlled output vectors map to six correct canonical keys through HTTP. Label set is validated against all 38 KB keys. Real accuracy still needs labelled data. |
| c: rejection dominates | Unproven for real photos. One of two drawings rejected; both confidence and entropy safeguards retained. |
| d: mismatched lookup/default | Not observed for known labels. Unknown-key fallback was a real defect and now raises/logs. Exact PlantVillage strings are the sole canonical keys; aliases are not guessed. |
| e: mock/default record | True only on missing-model and missing-weather/unknown-risk paths. Random/fabricated outputs removed. |
| f: frontend constants/cache | Symptoms and controls already render response fields. Fresh-vs-saved precedence fixed and tested. No analyze service-worker caching found; now explicitly excluded, HTTP/client use no-store, stored language variants use image hash + language (legacy records use their unique ID). Saved history is retained. |
| g: shared i18n content | True for the immediate-action catalog array, not a universal treatment lookup key. |
| h: repeated upload blob | Not reproduced. Browser upload hashes differ; client test checks distinct filenames and no-store. |

| Bug 2 suspect | Evidence / verdict |
|---|---|
| a: no real coordinates | Default quick-photo flow supplies none; weather selector was optional. No automatic 0,0 was found. UI now explicitly asks for location, explains geolocation, supports existing place search and remembers choices. |
| b: API failure swallowed | Confirmed: previously returned fixed fallback weather. Now API failure is visible without fabricated risk; diagnosis/general advice remain available. Five live requests succeeded with actual responses captured. |
| c: ignores inputs/units | Not a constant engine: class thresholds and weather already affected scores. Wind was fetched but discarded, current hour assumed index 168, past daily rows appeared as forecasts. These are fixed; recent 72 h/next 48 h rain and wetness proxies added. Temperature suppression prevents cold-weather mite scores being high from dryness alone. |
| d: generic i18n string | Confirmed visible UI selected only a level tip and ignored actual measured reasons. Now 2–3 measured reasons and localized class action are visible. |
| e: cached/hardcoded | Fixed fallback was hardcoded. Weather cache is coordinate-specific; no evidence of a global stale analyze response. |

## Actual inference trace (before and after)

Raw and calibrated probabilities below are fractions, not percentages. Full logits and complete final HTTP JSON: [before](before/images.json), [after](after/images.json). Actual browser-rendered text, network response JSON and upload hashes: [browser trace](browser/results.json). Browser JPEG downscaling/recompression slightly changes numeric probabilities from direct uploads; it is not an inference regression. Before UI descriptions below are derived from the inspected pre-edit components, not fabricated pre-edit screenshots.

| Drawing | Raw top-three class: probability | Calibrated top-three probability | Entropy before → after | KB key / returned record | UI before → after |
|---|---|---|---|---|---|''']
for a,b in zip(before,after):
    p=a['prediction'];raw='<br>'.join(f"{x['class']}: {x['probability']:.6f}" for x in a['raw_top3'])
    calibrated=', '.join(f"{x['confidence']:.6f}" for x in p['top_k'])
    ui='Uncertain, no top-three shown → uncertain plus three localized possibilities and retake guidance' if p['is_uncertain'] else 'Healthy class content, generic immediate actions → healthy maintenance and three possibilities'
    lines.append(f"| {a['image']} | {raw} | {calibrated} | {p['entropy']} → {b['prediction']['entropy']} | {p['predicted_label']} / {a['final_json']['disease_details']['id']} | {ui} |")
lines.append('''
## Entropy decision and model limitation

Keep **H > 2.20**, confidence cutoff **0.60**, temperature **0.413**. Drawing entropies span 1.7300–2.6612; one accepted and one rejected. In-distribution labelled sample count=0; real-field sample count=0. There is no defensible distribution or threshold-retuning experiment here. Lowering rejection from these drawings would risk presenting wrong field predictions as certain. The new uncertain screen preserves three possibilities and withholds disease treatment.

The existing `ml/reports/plantdoc_metrics.json` reports accuracy **0.213 on 216 field samples**, 170 errors; this is historical repository evidence, not a new evaluation. `calibration_report.json` reports temperature 0.413. Field-domain accuracy is a model limitation; this patch does not solve it. Next: obtain verified PlantVillage/field holdouts, assess the 255-versus-256 preprocessing discrepancy separately, plot entropy and confidence for correct/incorrect/OOD images, choose an operating point by false-accept versus rejection cost, and consider field-data fine-tuning in a separate task.

## Weather evidence

Five controlled scenarios use explicitly **mocked** Open-Meteo raw responses, not claims about actual weather at those coordinates. [Full scenarios, request URLs, raw hourly arrays, summaries, scores, levels and all five localized responses](after/weather-scenarios.json).

| Scenario | Late blight | Bacterial spot | Spider mites | Squash powdery mildew |
|---|---:|---:|---:|---:|''')
for row in read('after/weather-scenarios.json'):
    scores=[row['results'][k]['en']['risk_score'] for k in ('Tomato___Late_blight','Tomato___Bacterial_spot','Tomato___Spider_mites Two-spotted_spider_mite','Squash___Powdery_mildew')]
    lines.append('| '+row['scenario']+' | '+' | '.join(map(str,scores))+' |')
lines.append('''
Five **live** API calls all returned HTTP 200 after sandbox network access was approved. [Full live URLs/raw responses/computed localized output](after/live-weather.json). These are distinct from the controlled scenarios.

| Coordinates | Late blight score | Bacterial spot score | Powdery mildew score |
|---|---:|---:|---:|''')
for row in live:
    lines.append('| '+str(row['coordinates'])+' | '+' | '.join(str(row['results'][key]['en']['risk_score']) for key in ('Tomato___Late_blight','Tomato___Bacterial_spot','Squash___Powdery_mildew'))+' |')
lines.append('''
Risk rules live in `backend/app/data/risk_rules.json`, keyed by all 38 canonical classes, with existing agronomic reasoning/source citations and review status. Index weights, wind modifier and temperature suppression are heuristic, not validated infection probabilities. Leaf wetness is a cumulative rain/high-RH proxy, not a leaf sensor or proven consecutive infection period. The UI presents Low/Medium/High; legacy API levels MODERATE/VERY HIGH remain compatible and map to Medium/High.

## Verification

Actual captured terminal output:

```text
Before regression: 9 failed, 15 passed
Full backend: 162 passed in 9.73s
Final focused backend regression: 60 passed in 1.82s
Frontend: Test Files 6 passed (6); Tests 37 passed (37)
Browser: PASS: 2 real uploads; 3 explicitly mocked class responses;
         4 language transitions; 9 screenshots
Production build: built in 25.77s
Offline app shell: 23 files, revision d009578812fe0064
```

Here "real uploads" means actual browser POSTs of the bundled drawings, **not real photographed leaves**. [Backend log](after/backend-suite.txt), [frontend log](after/frontend-suite.txt), [build log](after/build.txt). Screenshots: [uncertain](browser/sample_leaf_diseased.png), [healthy](browser/sample_leaf_healthy.png), [class 1](browser/mocked-class-0.png), [class 2](browser/mocked-class-1.png), [class 3](browser/mocked-class-2.png), [Hindi](browser/localized-hi.png), [Tamil](browser/localized-ta.png), [Telugu](browser/localized-te.png), [Kannada](browser/localized-kn.png).

The backend regression covers all 38×5 symptoms/immediate actions/organic controls/prevention arrays for uniqueness and nonempty/nonplaceholder content, six controlled-logit mappings, exact raw-output parity for both bundled drawings, unknown keys, missing model, missing location, API failure, wind differences, weather/class sensitivity and five-language measurement templates. Distinct *combined* treatment advice is provided by class-specific organic controls; generic chemical safety/no-pesticide statements may appropriately repeat and were not artificially rewritten to pretend to be different medicines.

## Changed files

* Backend routes: `api/routes/analyze.py`, `diseases.py`, `weather.py`; localized error handling: `api/i18n_errors.py`.
* Backend services: `services/i18n.py`, `risk.py`, `weather.py`; inference safeguards only: `ml/inference.py`.
* Backend schemas: `schemas/analysis.py`, `risk.py`, `weather.py`.
* Data: `data/risk_rules.json`; `data/i18n/{en,hi,ta,te,kn}/{diseases,messages}.json`.
* Frontend: `api/client.ts`, `components/RiskGauge.tsx`, new `WeatherRisk.tsx`, `LocationSelector.tsx`; `pages/ResultPage.tsx`, `AnalyzePage.tsx`, `HistoryPage.tsx`; `storage/checks.ts`; `types/index.ts`; five UI locales; `public/audio-sw.js` (explicit API exclusion). Build regenerates offline precache output.
* Tests: new `backend/tests/test_pipeline_regressions.py`, `weather_scenarios.py`, fixtures; updated `test_weather.py`, `test_analyze_api.py`, `test_coverage_expansion.py`, `test_translation_catalogs.py`; new `frontend/tests/pipelineRegression.test.tsx`.
* Reproduction/data scripts: `trace_diagnosis.py`, `trace_weather.py`, `capture_live_weather.py`, `verify_pipeline_browser.py`, `fix_pipeline_data.py`, `add_pipeline_messages.py`, `write_bug_report.py`.

## Required human review / unfinished evidence

* Agronomist: every machine-suggested catalog entry (38 keys × 5 languages); reused immediate controls/healthy maintenance; existing chemical advice remains subject to local product-label approval.
* Agronomist: all 38 risk-rule records, numerical weights, suppression multiplier, wind threshold, wetness approximation, action timing and powdery-mildew humidity/rain tradeoffs. Existing sources were retained; an attempted web-source search failed in the tool environment, so these were not independently recertified.
* Native-language reviewers: all five catalogs, new location/error prompts, measured weather templates and action timing; automated checks cannot certify translation or agronomic correctness.
* Missing evidence: six labelled real images, separate in-distribution and field entropy evaluation, third distinct real-leaf E2E image, and before-fix browser screenshots. Do not treat the controlled class tests or drawings as these missing evaluations.
''')
(ROOT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
catalog=json.loads(Path('backend/app/data/i18n/en/diseases.json').read_text(encoding='utf-8'))['diseases']
(ROOT/'expert-review.json').write_text(json.dumps({'review_status':'machine_suggested','languages':['en','hi','ta','te','kn'],'classes':[{'canonical_key':d['id'],'review':['localized immediate_actions','healthy maintenance' if d['is_healthy'] else 'existing disease controls and symptoms','risk_rules thresholds, reasoning, weights and action timing']} for d in catalog],'additional_review':['native-language weather and location templates','field-data entropy threshold experiment']},ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'REPORT.md').open('a',encoding='utf-8') as report:
    report.write('\nExplicit per-class review list: [expert-review.json](expert-review.json).\n')
print('Report written; model hashes and raw logits verified identical.')
