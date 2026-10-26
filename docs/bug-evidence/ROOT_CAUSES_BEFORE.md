# Evidence recorded before application edits

HTTP capture: `before/images.json` includes raw logits, raw top three, calibrated predictions, entropy and complete HTTP JSON for both available samples. No dataset directory or six labelled photographs were supplied. The sample filenames are not verified ground truth. Later visual inspection confirmed these are drawings, not field photographs.

* All five catalogs have 38 distinct symptoms, organic controls and prevention lists, but only ONE immediate_actions list across all 38 classes. ActionChecklist renders this list under the immediate-action heading. This reproduces repeated immediate advice, not a claim that every symptom/treatment is identical.
* RiskGauge renders only farmer.risk_<level> prominently; hides the actual headline/summary and never renders contributing factors or score. Weather fetch exceptions return constant fabricated weather (22C/65% current). Missing coordinates return a manufactured risk score of 40. These are confirmed code paths, with regression tests failing before edits.
* ONNX outputs differ: diseased sample -> Peach bacterial spot, H=2.6612 (uncertain); healthy sample -> Corn healthy, H=1.7300 (accepted). Both HTTP responses have matching class-specific KB records. No constant index or key mismatch observed. Temperature=0.413. Threshold=2.20; confidence cutoff=0.60. No evidence to estimate field rejection frequency from two samples.
* Missing model silently produces random Dirichlet predictions. Unknown disease gets a fabricated risk=50; localization returns None. These fail-closed regressions fail before edits.
* Guest backend ID is constant, but App.complete already replaces it with a UUID. Current service worker does not cache analyze POSTs. Upload downscaler constructs a fresh canvas per file. No confirmed constant-image/cache cause.
* Training evaluation uses int(224*1.14)=255 shorter-side resize; backend uses 256. Both use bilinear RGB, ImageNet normalization and float32 NCHW. Preserve existing preprocessing/raw logits for this task's exact-output regression; record this discrepancy for separate model/preprocessing evaluation.

Baseline regression run: **9 failed, 15 passed** (`before/tests.txt`). Existing working-tree frontend edits were present before this task and must be preserved.
