# Farmer UI redesign

## Audit and proposed wireframes

The previous home screen led with branding and a marketing hero. Camera and upload competed with secondary navigation. Result pages used gradients, tiny text, numerical confidence, and large panels of advice. Weather was a dashboard of scores and forecasts. Guest history was unavailable. The first language choice had no spoken names or tutorial. Route code loaded together, and the service worker cached fonts and opt-in narration but not the application shell.

The wireframes proposed before implementation were:

- **First launch:** five native-script language rows, each with a separate speaker button → three illustrated steps → start or skip.
- **Home:** compact leaf wordmark and language control → short heading and line-drawn leaf → large camera action → gallery → history shortcut.
- **Capture:** one leaf / good light / fill frame → camera or gallery → preview and retake → check. Optional weather stays behind a disclosure.
- **Result:** photo, crop and local disease name → High/Medium/Low confidence → large Listen button → scientific name → six expandable advice sections. An uncertain result gets a retake/expert message without treatment advice.
- **Weather:** colored, labeled risk indicator → short action → Listen. Supporting explanation is expandable.
- **History:** thumbnail, local disease name and date in a vertical list; confirm deletion.
- **Settings:** high contrast, offline-audio guidance, disease guide, help and account. Language remains in the shared header.
- **Navigation:** fixed Home / Camera / History / Settings, with icons and labels.

## Implementation

The frontend components were replaced with an earthy, flat layout: `#FAF6EE` background, `#2A2118` text, `#2F5D3A` primary actions, amber warnings and brick-red danger. Noto fonts are self-hosted, script-subsetted, swap immediately and load when used. Body text is 18px; the smallest text is 16px. Buttons are at least 56px high. The high-contrast option persists. Decorative drawings and icons are SVG; no stock or generated bitmap artwork is used.

Home opens the native photo chooser from the user's tap and submits the selected image automatically. The direct Camera route supports preview, retake and optional weather. The existing upload downscaler and API client are unchanged. A second small thumbnail is stored with each check in IndexedDB so results and history can reopen offline. API calls, backend response contracts, prediction and ML files are unchanged.

The result heading displays the main local name; parenthetical technical aliases remain in “What is this,” and the scientific name remains visible below the player. This keeps Listen above the bottom navigation even for the longest disease name. Confidence labels change presentation only; the backend uncertainty flag still controls whether treatment is shown.

Narration retains its static → dynamic → matching browser voice fallback. Result and weather players stop one another. Navigation, language changes and opening the language picker stop narration. Language-name and short weather recordings are bundled in `frontend/public/voice` and requested only after a tap. Offline narration is downloaded only through the explicit download control, for the selected language.

The production service worker caches the app shell and lazy route chunks, caches fonts as used, and preserves explicitly downloaded audio. It does not queue photographs or pretend to diagnose offline. New diagnoses still need the existing server. Saved results can reopen without it. Nginx revalidates the service worker, cache manifest and index document.

## Reproduce verification

Run the backend normally on port 8000. In `frontend` run `npm ci`, `npm test`, `npm run build`, then `npm run preview -- --port 4173`.

From the repository root:

```powershell
.venv/Scripts/python.exe scripts/verify_farmer_ui.py
.venv/Scripts/python.exe scripts/verify_farmer_interactions.py
```

These use headless Microsoft Edge through Playwright. The UI matrix uses existing localized disease records as deterministic fixtures; it does not run or modify the model. The interaction test fulfills one analyze request with a fixture while exercising the real chooser, client downscaler, navigation, IndexedDB, service worker and audio playback. An artificial green test image and the app's leaf illustration are verification assets, not disease photographs.

In `frontend`, `node scripts/lighthouse_ui.mjs` measures the returning-user home and Tamil result screens. Reports record a 360×640 mobile viewport, simulated 150ms network RTT, 1,638kbps throughput and 6× CPU slowdown. Returning-user reports preserve selected language, local results and cached assets. The separate first-launch report uses Lighthouse's default storage reset.

## Review limits

- The new `farmer.*` wording in Hindi, Tamil, Telugu and Kannada is machine-suggested and needs native-speaker review, especially shortened navigation labels. Existing disease translations retain their human-review status; this redesign does not certify them.
- Browser checks verify dimensions, font loading and screenshots. They do not replace testing on physical low-end Android phones, in direct sunlight, with farmers or with screen readers. Safari/iOS was not tested in this run.
- Offline reading requires an earlier online visit. A saved result can be reopened in a language previously loaded for that result. Switching to an uncached result language needs a connection. New diagnosis always needs the existing backend.
- Lighthouse scores are laboratory measurements on this machine, not a guarantee for every phone or network. It still reports unused JavaScript in the shared application bundle.

## Recorded results

Final production build:

```text
> tsc && vite build && node scripts/build_offline.cjs
vite v5.4.21 building for production...
✓ 1541 modules transformed.
✓ built in 7.58s
Offline app shell: 24 files, revision e1b9536d05f9b100. Audio remains opt-in.
```

Main JavaScript: 342.75 kB, 128.64 kB gzip. CSS: 11.41 kB, 3.23 kB gzip. Analysis, result, history, settings, guide, account, help and optional dialogs are separate chunks.

Final test run:

```text
0 hardcoded display strings (0 distinct)
0 UI references missing from the English catalog
Test Files  5 passed (5)
     Tests  29 passed (29)
  Duration  2.68s
```

The suite covers all five catalogs, uncertain-result suppression, narration fallback/player states, competing audio players, StrictMode's single camera submission, retained-photo retry and onboarding persistence. React Router emits its existing v7 migration warnings; there were no test failures.

Final browser output:

```text
105 screen checks; 0 layouts with issues.
30 tutorial/uncertainty checks passed; no overflow; tutorial fits one screen.
PASS All five native language buttons play bundled audio after a tap
PASS First-launch choice, skip tutorial, persisted choice on reload
PASS Home camera gesture to result; one analysis request; local compressed thumbnail
PASS Result and weather playback coordinate; opening language choice stops playback
PASS Audio downloads only after explicit tap, for the selected language
PASS Offline full reload, saved history, thumbnail, route chunks and downloaded narration
PASS Offline capture clearly explains that a new diagnosis needs a connection
PASS High contrast persists across an offline reload
PASS Deleting a local check requires confirmation and survives reload
```

The 105-screen matrix covers Home, Capture, Result, History, Settings, Guide and Account × five languages × 360×640, 412×915 and 768×1024. It checks horizontal overflow, text below 16px and control height below 56px. Additional captures cover weather and expanded advice. The result uses the longest disease name in each catalog, checks that Listen remains above the bottom navigation, and stress-checks labels expanded by forty percent. The additional 30 checks cover tutorial and uncertain results at every language/size combination. Screenshots were inspected for Indic rendering and wrapping; this is not a linguistic certification.

[Browse all screenshots](ui-screenshots/README.md). Representative screens: [English home](ui-screenshots/en-360-home.png), [Tamil result](ui-screenshots/ta-360-result.png), [Kannada result](ui-screenshots/kn-360-result.png), [high contrast](ui-screenshots/high-contrast-360.png).

| Lighthouse run | Performance | Accessibility | Report |
|---|---:|---:|---|
| First launch, storage reset | 98 | 100 | [HTML](ui-lighthouse-first-launch.report.html) |
| Returning English home | 100 | 100 | [HTML](ui-lighthouse-home-en.html) |
| Returning Tamil result | 100 | 100 | [HTML](ui-lighthouse-result-ta.html) |

Returning-user reports were rerun on the final build. They preserve stored language/results and cached assets; the first-launch report measures the initial uncached picker. Reports and raw JSON are retained beside this document.

Calculated contrast ratios: dark text/background **14.66:1**, white/primary green **7.64:1**, dark text/amber warning **12.06:1**, danger red/background **5.54:1**. These exceed 4.5:1 for the named text pairs.

`git diff --name-only -- backend frontend/src/api/client.ts` returned no paths: the backend, model/prediction code, API client/contracts and original image downscaler were not edited.
