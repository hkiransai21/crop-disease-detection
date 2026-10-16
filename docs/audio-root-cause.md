# Audio root cause — reproduced 16 October 2026

The original flow was AudioNarrator Listen → GET /api/v1/audio/{disease}/overview → EdgeTTSProvider → exception → MockTTSProvider → disk cache → HTTP 200 audio/mpeg → HTMLAudioElement → browser speech fallback.

The app was run with uvicorn on port 8000 and Vite on port 5173. An inherited DEBUG=release initially prevented startup (Pydantic bool_parsing); setting DEBUG=false for the process allowed normal database/model startup. No model changes were made. The browser was real headless Microsoft Edge, driven by Playwright, with a saved guest diagnosis; no prediction was fabricated as a model test.

| Language | Original network response | Backend log | Browser console |
|---|---|---|---|
| en | 200 audio/mpeg, 332 bytes | 403, Invalid response status; Falling back to mock synthesis | NotSupportedError: Failed to load because no supported source was found. |
| hi | 200 audio/mpeg, 332 bytes | same | same |
| ta | 200 audio/mpeg, 332 bytes | same | same |
| te | 200 audio/mpeg, 332 bytes | same | same |
| kn | 200 audio/mpeg, 332 bytes | same | same |

The 403 is from the Edge synthesis WebSocket. Voice listing succeeds outside the sandbox; synthesis is a separate request. Do not infer that a successful voice list means synthesis works. The original code converts ANY provider exception into 332 bytes consisting of a frame-like header and repeated SHA256 digest. These are not playable narration, and are cached as successful MP3s. Old tests only checked nonempty bytes.

## Requested cause audit

- (a) Applies. getVoices is read synchronously, no voiceschanged listener, and speaking proceeds even without a matching voice. Actual installed languages were en-US, en-IN, en-IN, en-US, en-US. No hi/ta/te/kn voice. The fallback also runs twice via onerror and the play rejection.
- (b) Not the cause for the five requested languages. The configured browser locales are en-IN, hi-IN, ta-IN, te-IN, kn-IN. `edge-tts --list-voices` verified en-IN-NeerjaNeural, hi-IN-SwaraNeural, ta-IN-PallaviNeural, te-IN-ShrutiNeural, kn-IN-SapnaNeural. Extra languages were configured and must be removed.
- (c) Initial play is from a click, so not the reproduced failure. Asynchronous browser fallback can lose user activation. iOS/Safari hardware was not available; this cannot be claimed tested there.
- (d) Applies: content type is correct but the 332-byte payload is broken. The failure is hidden behind HTTP 200 and long cache headers.
- (e) Edge does not require credentials. No missing Edge key. Google credentials are not configured for this test environment. DEBUG is a separate startup environment issue.
- (f) Not reproduced: all five same-origin proxied audio requests reached the backend without auth and returned 200. The upstream provider's 403 is not app CORS/auth.
- (g) No silent backend truncation found; the old POST schema limits text to 2000 characters. However the old narration deliberately includes only the first organic, chemical and prevention item, omitting remaining advice. There is no dedicated symptoms section.
- (h) No service worker registration or cache code exists in the original frontend. Not the cause. Backend disk caching and HTTP caching can preserve the fake response.

Additional issues: relative cache paths depend on working directory; pre-generation writes opaque hashes rather than stable disease/section files; fallback speech mixes English templates with localized text; playback state can be overwritten by stale events.

## Provider references

Google supports sub aliases and break tags: https://docs.cloud.google.com/text-to-speech/docs/ssml
Edge custom SSML is restricted: https://github.com/rany2/edge-tts
