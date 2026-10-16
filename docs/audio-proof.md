# Recorded audio verification — 16 October 2026

## Original failure

Exact HTTP observations before the fix, Apple___Apple_scab/overview with force_refresh=true:

```text
en HTTP=200 type=audio/mpeg bytes=332
hi HTTP=200 type=audio/mpeg bytes=332
ta HTTP=200 type=audio/mpeg bytes=332
te HTTP=200 type=audio/mpeg bytes=332
kn HTTP=200 type=audio/mpeg bytes=332
```

Each backend call logged `403, message='Invalid response status'` from the Edge synthesis WebSocket, followed by `Falling back to mock synthesis.` Every language produced browser console `NotSupportedError: Failed to load because no supported source was found.` Actual installed browser voice locales: `en-US, en-IN, en-IN, en-US, en-US`. See audio-root-cause.md for the complete requested cause audit.

## Generated library

Real generation used TTS_PROVIDER=gtts because Edge synthesis failed. Initial 20 disease-section samples succeeded, then the complete pass reported:

```text
{"generated": 864, "existing": 20, "failed": 0}
```

Five added loading prompts were subsequently generated. An intermediate authoring attempt passed Unicode through a PowerShell pipe and failed for four prompts with `AssertionError: No text to send to TTS API`; writing UTF-8 source directly corrected this, and regeneration reported:

```text
{"generated": 4, "existing": 885, "failed": 0}
```

Final `python scripts/verify_audio.py` output (all files decoded; RMS checked):

```text
language | diagnosis | symptoms | treatment | prevention | common
en | 38/38 | 38/38 | 38/38 | 38/38 | 25/25
hi | 38/38 | 38/38 | 38/38 | 38/38 | 26/26
ta | 38/38 | 38/38 | 38/38 | 38/38 | 26/26
te | 38/38 | 38/38 | 38/38 | 38/38 | 26/26
kn | 38/38 | 38/38 | 38/38 | 38/38 | 26/26
Failures: 0
```

889 real MP3s: 760 disease sections plus 129 common prompts. The English Listen label contains a language interpolation and is not a standalone prompt; regional labels are standalone, hence one additional common file per regional language.

## Automated tests and production build

`DEBUG=false python -m pytest backend/tests/test_audio.py backend/tests/test_i18n.py -q`:

```text
...............................................                          [100%]
47 passed in 0.86s
```

These include twenty static language/section checks using real generated audio and mutagen, five dynamic response/cache contract checks using a recorded real MP3 provider, malformed payload rejection, poisoned-cache replacement, request validation, rate limiting, SSML, language configuration, and the existing model-invariance test. The deterministic dynamic tests do not claim live Google/Edge synthesis.

`npm test -- --reporter=dot`:

```text
Test Files  3 passed (3)
     Tests  20 passed (20)
```

The player tests cover static → dynamic → voice fallback, voiceschanged, absent matching voices, gesture denial/retry, loading/play/pause/resume/stop/replay/speed, and cancellation on language/navigation/unmount. Existing React Router future-flag warnings remain; no test failed.

`npm run build`:

```text
✓ 1535 modules transformed.
dist/index.html                   1.13 kB │ gzip:   0.60 kB
dist/assets/index-CO4zGWa9.css   41.34 kB │ gzip:   7.14 kB
dist/assets/index-D-oiWOf7.js   382.48 kB │ gzip: 116.42 kB
✓ built in 7.86s
```

## Real browser

`python scripts/verify_audio_browser.py` against Vite and uvicorn, headless installed Microsoft Edge:

```text
en: static playback 7.01s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
hi: static playback 8.78s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
ta: static playback 6.96s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
te: static playback 7.32s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
kn: static playback 7.99s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0
```

Each language starts in an isolated browser context with no cache. The test clicks Listen, verifies advancing playback time, pauses/resumes/stops, taps Download, checks only that language's cache exists, switches the browser offline, and replays real audio. This proves offline audio in an open app; it does not claim an offline HTML shell.

## Running dynamic endpoint

GET /api/v1/audio/tts with each language's diagnosis narration, server configured with TTS_PROVIDER=gtts. These requests exercised the running endpoint and its real provider-generated disk cache:

```text
en 200 audio/mpeg 55680 6.96
hi 200 audio/mpeg 69888 8.74
ta 200 audio/mpeg 55296 6.91
te 200 audio/mpeg 58176 7.27
kn 200 audio/mpeg 63552 7.94
```

Columns: language, HTTP status, content type, bytes, decoded duration in seconds.

## Scope and limitations

```text
Protected model/prediction paths changed: []
Static MP3 files: 889
Native-script narration coverage: PASS
```

No ONNX, preprocessing, calibration, prediction or ML source changed. Google provider is implemented but credentials were unavailable, so it was not exercised against Google. Edge voice names were verified live, but Edge synthesis failed. All five languages nevertheless have validated static audio via gTTS. Native-speaker listening review, Android/iOS physical-device checks and Docker image execution were not performed. The existing frontend had no service worker; the added worker supports explicit audio downloads, not offline page bootstrapping.

Sandbox impediments encountered and resolved: network proxy refusal for voice listing; pip package access; Vite esbuild spawn EPERM; pytest temporary-directory WinError 5. Authorized reruns outside the sandbox succeeded. Installing gTTS also reported that this workspace's pre-existing huggingface-hub expects a newer Click than gTTS permits; no ML source was changed. Audio generation and the existing model-invariance tests passed in this environment.
