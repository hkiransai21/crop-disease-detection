# Audio narration

Supported languages are exactly en, hi, ta, te and kn. Their speech locales are en-IN, hi-IN, ta-IN, te-IN and kn-IN.

## Static library

`backend/app/data/narration/{lang}.json` contains independent narration scripts for every canonical disease key and the four sections: diagnosis, symptoms, treatment and prevention. Common audio prompts are under `prompts`. Edit these scripts independently of display text. Use short sentences, written-out numbers and units, and no symbols or emojis. The initial disease advice was adapted from the existing localized knowledge base; native-speaker pronunciation/agronomy review has not been performed in this session.

`backend/app/data/narration/lexicon/{lang}.json` maps disease, product and agricultural terms to spoken aliases. Google receives escaped SSML with sub aliases and sentence breaks. Edge and gTTS receive plain text with aliases applied because they do not accept arbitrary SSML.

The committed MP3 library is generated using gTTS: Edge's voice list worked but synthesis returned 403 in this environment. Files are mono, 24 kHz, 40 kbps, at `backend/app/static/audio/{lang}/{disease_key}/{section}.mp3`. Common files use `_common/{prompt}.mp3`. Keep these deployment files; static playback needs no provider, credentials or network access beyond the app server. The Docker backend copies them with the application. Dynamic cache files remain git-ignored.

From the repository root, install `backend/requirements.txt`, then choose a provider using environment variables:

```powershell
$env:TTS_PROVIDER='edge' # default development provider
python scripts/generate_audio.py --verify-voices

$env:TTS_PROVIDER='google'
$env:GOOGLE_APPLICATION_CREDENTIALS='C:/secure/service-account.json'
python scripts/generate_audio.py

$env:TTS_PROVIDER='gtts' # last resort
python scripts/generate_audio.py
python scripts/verify_audio.py
```

On POSIX use `export TTS_PROVIDER=...`. Optionally set `TTS_FALLBACK_PROVIDER=gtts` for an explicit fallback after the selected provider fails. Google discovers available Neural2/WaveNet voices for each locale; optional `GOOGLE_TTS_VOICE_EN`, `_HI`, `_TA`, `_TE`, `_KN` override the selection and must match a discovered voice. Google authentication and synthesis were not tested without credentials.

Generation supports `--lang kn`, `--disease Apple___Apple_scab`, `--jobs 1` through `8`, `--dry-run`, and `--force`. Use `--force` after editing narration or pronunciation: existing files otherwise remain unchanged. Failures return a nonzero exit code; partial output can be resumed. `imageio-ffmpeg` supplies the encoder/decoder; `mutagen` validates the MP3 structure and duration. The verifier additionally decodes every file and checks signal RMS. This detects silence, not pronunciation quality.

## HTTP and player behavior

- `GET /api/v1/audio/files/{lang}/{disease}/{section}.mp3`: static file only, 404 if missing, no TTS call. Supports byte ranges.
- `GET /api/v1/audio/catalog/{lang}`: independent narration text for fallback.
- `GET /api/v1/audio/manifest/{lang}`: expected static URLs for explicit downloads.
- `GET /api/v1/audio/tts?text=...&lang=...`: dynamic fallback, maximum 2000 characters and 4500 UTF-8 bytes. Oversize text is rejected, never truncated. Limit is ten requests per minute per client IP per backend process, using the existing SlowAPI limiter. Multi-worker/global rate limits require a shared SlowAPI storage backend if deployed at scale.

The dynamic cache uses a SHA256 of text, language, provider, voice, rate and lexicon. Its v2 directory excludes the old poisoned cache; cached bytes are validated before serving. Provider errors return 503 with no-store, never fake audio. Static serving also sends no-store so offline persistence is controlled by the user's download action.

`useAudio` owns playback and stops on language, section, diagnosis or navigation changes. It tries static audio, then dynamic audio, then an exact matching browser voice after checking `voiceschanged`. Browser speech requires a fresh tap after asynchronous fallback. An autoplay rejection leaves the current file ready for another tap. Missing voices produce the localized “Audio not available, please read the text” message. Speed controls use 0.75, 1 and 1.25 times playback speed; changing browser-speech speed restarts that utterance on the next tap.

The audio service worker is registered by the download button. It caches only the selected language's manifest files and narration text after that action. It rejects unsuccessful, wrong-type and undersized responses and retains the previous complete download on failure. Cached byte-range responses support media seeking. The app must be open to replay downloaded audio offline; this worker does not add an offline HTML application shell to the previously non-PWA frontend.

## Tests

```powershell
$env:DEBUG='false' # only needed if the host has an incompatible DEBUG environment variable
python -m pytest backend/tests/test_audio.py backend/tests/test_i18n.py -q
cd frontend
npm test
npm run build
```

For real browser checks, install Playwright (`pip install playwright`), run backend port 8000 and Vite port 5173, then `python scripts/verify_audio_browser.py`. It uses installed Microsoft Edge in headless mode and checks all five languages, real playback, pause/resume/stop and offline replay. `scripts/reproduce_audio.py` records the original failure on the original revision. Android and iOS devices still require manual checks; desktop tests do not establish behavior on those devices.
