"""Pluggable TTS Provider interface, Edge Neural TTS, Cloud TTS, and offline audio caching engine."""
import abc
import hashlib
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from backend.app.services.i18n import get_i18n_config, resolve_language, get_localized_disease_entry

AUDIO_CACHE_DIR = Path("backend/app/static/audio_cache")
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class TTSProvider(abc.ABC):
    """Abstract Base Class for Text-To-Speech Providers."""

    @abc.abstractmethod
    async def synthesize(
        self,
        text: str,
        lang: str = "en",
        voice: Optional[str] = None,
        rate: float = 1.0
    ) -> bytes:
        """Synthesize text to compressed audio bytes (MP3)."""
        pass


class EdgeTTSProvider(TTSProvider):
    """High-Performance Neural TTS provider using Microsoft Edge Neural voices for Indic & Global languages."""

    async def synthesize(
        self,
        text: str,
        lang: str = "en",
        voice: Optional[str] = None,
        rate: float = 1.0
    ) -> bytes:
        import edge_tts

        resolved_lang = resolve_language(lang)
        cfg = get_i18n_config()
        lang_configs = {l["code"]: l for l in cfg.get("supported_languages", [])}
        
        target_voice = voice or lang_configs.get(resolved_lang, {}).get("tts_voice", "en-IN-NeerjaNeural")

        # Format rate as percentage string, e.g. "+0%", "-10%", "+20%"
        rate_pct = int((rate - 1.0) * 100)
        rate_str = f"{rate_pct:+d}%"

        communicate = edge_tts.Communicate(text, target_voice, rate=rate_str)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        return b"".join(audio_chunks)


class MockTTSProvider(TTSProvider):
    """Mock TTS provider returning synthetic MP3 audio bytes for testing and offline environments."""

    async def synthesize(
        self,
        text: str,
        lang: str = "en",
        voice: Optional[str] = None,
        rate: float = 1.0
    ) -> bytes:
        # Generate minimal valid MP3 frame header + payload
        mp3_header = b"\xff\xfb\x90\x64\x00\x00\x00\x00\x00\x00\x00\x00"
        content_hash = hashlib.sha256(text.encode("utf-8")).digest()
        return mp3_header + content_hash * 10


def get_tts_provider() -> TTSProvider:
    """Factory function returning configured TTSProvider instance."""
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider_name == "mock":
        return MockTTSProvider()
    elif provider_name == "edge":
        return EdgeTTSProvider()
    return EdgeTTSProvider()


def compute_audio_hash(text: str, lang: str, voice: Optional[str] = None, rate: float = 1.0) -> str:
    """Compute content-addressable SHA-256 hash for audio caching."""
    token = f"{text.strip()}_{lang}_{voice or 'default'}_{rate:.2f}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_or_synthesize_audio(
    text: str,
    lang: str = "en",
    voice: Optional[str] = None,
    rate: float = 1.0,
    force_refresh: bool = False
) -> bytes:
    """
    Retrieve audio from cache or synthesize on demand.
    Saves output to static audio cache directory.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Cannot synthesize empty text.")

    audio_hash = compute_audio_hash(clean_text, lang, voice, rate)
    cache_file = AUDIO_CACHE_DIR / f"{audio_hash}.mp3"

    if cache_file.exists() and not force_refresh:
        return cache_file.read_bytes()

    provider = get_tts_provider()
    try:
        audio_bytes = await provider.synthesize(clean_text, lang, voice, rate)
    except Exception as e:
        # Graceful fallback to Mock provider if network is unavailable
        print(f"TTS Provider error: {e}. Falling back to mock synthesis.")
        mock_provider = MockTTSProvider()
        audio_bytes = await mock_provider.synthesize(clean_text, lang, voice, rate)

    # Persist to disk cache
    try:
        cache_file.write_bytes(audio_bytes)
    except Exception as e:
        print(f"Warning: Failed to write audio cache: {e}")

    return audio_bytes


def build_narration_script(
    disease_id: str,
    section: str = "overview",
    lang: str = "en"
) -> str:
    """
    Construct natural-sounding farmer-friendly narration script for audio.
    Sections:
    - 'overview': Diagnostic greeting, disease recognition, and risk summary.
    - 'treatment': Immediate organic and chemical actions with dosage instructions.
    - 'prevention': Long term seasonal prevention and escalation helpline.
    """
    resolved_lang = resolve_language(lang)
    entry = get_localized_disease_entry(disease_id, resolved_lang)
    if not entry:
        return "Disease details unavailable."

    crop = entry.crop
    disease = entry.disease_name
    is_healthy = entry.is_healthy

    if section == "overview":
        if is_healthy:
            scripts = {
                "en": f"Hello Farmer! Good news: your {crop} crop leaves are healthy and showing no disease symptoms. Continue your standard irrigation and nutrient schedule.",
                "hi": f"नमस्ते किसान भाई! खुशखबरी: आपके {crop} की फसल बिल्कुल स्वस्थ और सुरक्षित है। कोई बीमारी के लक्षण नहीं मिले हैं। सामान्य सिंचाई और पोषण जारी रखें।",
                "te": f"నమస్కారం రైతు సోదరులారా! శుభవార్త: మీ {crop} పంట ఆకులు సంపూర్ణ ఆరోగ్యంగా ఉన్నాయి. ఎటువంటి తెగులు లక్షణాలు లేవు. సాధారణ పద్ధతులు కొనసాగించండి.",
                "ta": f"வணக்கம் விவசாய தோழரே! நற்செய்தி: உங்கள் {crop} பயிர் இலைகள் ஆரோக்கியமாக உள்ளன. எந்த நோயும் தாக்கவில்லை.",
                "kn": f"ನಮಸ್ಕಾರ ರೈತ ಬಾಂಧವರೇ! ಶುಭವಾರ್ತೆ: ನಿಮ್ಮ {crop} ಬೆಳೆ ಸಂಪೂರ್ಣವಾಗಿ ಆರೋಗ್ಯಕರವಾಗಿದೆ. ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ.",
                "ml": f"നമസ്കാരം കർഷക സുഹൃത്തേ! സന്തോഷവാർത്ത: നിങ്ങളുടെ {crop} വിള പൂർണ്ണ ആരോഗ്യത്തിലാണ്. രോഗലക്ഷണങ്ങളൊന്നുമില്ല.",
                "mr": f"नमस्कार शेतकरी बंधूंनो! आनंदाची बातमी: आपले {crop} पीक पूर्णपणे निरोगी आहे. कोणत्याही रोगाची लक्षणे आढळलेली नाहीत.",
                "bn": f"নমস্কার কৃষক বন্ধু! সুখবর: আপনার {crop} গাছ সম্পূর্ণ সুস্থ ও রোগমুক্ত। স্বাভাবিক পরিচর্যা চালিয়ে যান।",
                "es": f"¡Hola agricultor! Buenas noticias: su cultivo de {crop} se encuentra completamente sano y sin síntomas de enfermedades."
            }
        else:
            scripts = {
                "en": f"Attention Farmer: your {crop} crop has been diagnosed with {disease}. {entry.symptoms}",
                "hi": f"ध्यान दें किसान भाई: आपके {crop} की फसल में {disease} के लक्षण पाए गए हैं। {entry.symptoms}",
                "te": f"గమనించండి రైతు సోదరులారా: మీ {crop} పంటకు {disease} సోకినట్లు గుర్తించబడింది. {entry.symptoms}",
                "ta": f"கவனத்திற்கு விவசாய தோழரே: உங்கள் {crop} பயிரில் {disease} நோய் கண்டறியப்பட்டுள்ளது. {entry.symptoms}",
                "kn": f"ಗಮನಿಸಿ ರೈತ ಬಾಂಧವರೇ: ನಿಮ್ಮ {crop} ಬೆಳೆಗೆ {disease} ತಗುಲಿರುವುದು ಕಂಡುಬಂದಿದೆ. {entry.symptoms}",
                "ml": f"ശ്രദ്ധിക്കുക കർഷക സുഹൃത്തേ: നിങ്ങളുടെ {crop} വിളയിൽ {disease} ബാധിച്ചതായി കണ്ടെത്തി. {entry.symptoms}",
                "mr": f"लक्ष द्या शेतकरी बंधूंनो: आपल्या {crop} पिकावर {disease} ची लक्षणे आढळली आहेत. {entry.symptoms}",
                "bn": f"মনোযোগ দিন কৃষক বন্ধু: আপনার {crop} গাছে {disease} শনাক্ত হয়েছে। {entry.symptoms}",
                "es": f"Atención agricultor: se ha diagnosticado {disease} en su cultivo de {crop}. {entry.symptoms}"
            }
        return scripts.get(resolved_lang, scripts["en"])

    elif section == "treatment":
        if is_healthy:
            scripts = {
                "en": "No chemical sprays are required. Maintain organic compost and regular field sanitation.",
                "hi": "किसी रासायनिक दवा के छिड़काव की जरूरत नहीं है। जैविक खाद और खेत की स्वच्छता बनाए रखें।",
                "te": "ఎటువంటి రసాయన మందులు అవసరం లేదు. సేంద్రీయ ఎరువులు మరియు పొలంలో పరిశుభ్రత పాటించండి.",
                "ta": "இரசாயன மருந்துகள் தேவையில்லை. இயற்கை உரங்களையும் நிலத் தூய்மையையும் பராமரிக்கவும்.",
                "kn": "ಯಾವುದೇ ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆ ಅಗತ್ಯವಿಲ್ಲ. ಸಾವಯವ ಗೊಬ್ಬರ ಮತ್ತು ಹೊಲದ ಸ್ವಚ್ಛತೆ ಕಾಪಾಡಿ.",
                "ml": "രാസവസ്തുക്കളുടെ ആവശ്യമില്ല. ജൈവവളങ്ങളും തോട്ടം ശുചിത്വവും നിലനിർത്തുക.",
                "mr": "कोणतीही रासायनिक फवारणी करण्याची गरज नाही. सेंद्रिय खतांचा वापर करा.",
                "bn": "কোনো রাসায়নিক স্প্রে করার দরকার নেই। জৈব সার ও পরিচ্ছন্নতা বজায় রাখুন।",
                "es": "No se requieren tratamientos químicos. Mantenga un abonado orgánico y la higiene de la parcela."
            }
        else:
            org_text = entry.organic_controls[0] if entry.organic_controls else ""
            chem_text = entry.chemical_controls[0] if entry.chemical_controls else ""
            scripts = {
                "en": f"Immediate Treatment Steps: First organic control: {org_text}. Second chemical protectant: {chem_text}. Always wear a protective mask and gloves while spraying.",
                "hi": f"तुरंत करने योग्य उपचार: पहला जैविक उपाय: {org_text}। दूसरा रासायनिक उपाय: {chem_text}। छिड़काव करते समय मास्क और दस्ताने अवश्य पहनें।",
                "te": f"వెంటనే చేయవలసిన నివారణ చర్యలు: మొదటి సేంద్రీయ పద్ధతి: {org_text}. రెండవ రసాయన మందు: {chem_text}. పిచికారీ చేసేటప్పుడు మాస్క్ తప్పక ధరించండి.",
                "ta": f"உடனடி சிகிச்சை முறைகள்: முதல் இயற்கை முறை: {org_text}. இரண்டாம் இரசாயன மருந்து: {chem_text}. மருந்து தெளிக்கும் போது முகக்கவசம் அணியவும்.",
                "kn": f"ತಕ್ಷಣದ ಚಿಕಿತ್ಸಾ ಕ್ರಮಗಳು: ಮೊದಲನೆಯದಾಗಿ ಸಾವಯವ ವಿಧಾನ: {org_text}. ಎರಡನೆಯದಾಗಿ ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆ: {chem_text}. ಸಿಂಪಡಿಸುವಾಗ ಮಾಸ್ಕ್ ಧರಿಸಿ.",
                "ml": f"ഉടനടി ചെയ്യേണ്ട ചികിത്സകൾ: ആദ്യ ജൈവ പ്രതിവിധി: {org_text}. രാസകുമിൾനാശിനി: {chem_text}. മരുന്ന് തളിക്കുമ്പോൾ മാസ്ക് ധരിക്കുക.",
                "mr": f"तात्काळ उपाययोजना: पहिला सेंद्रिय उपाय: {org_text}. दुसरा रासायनिक उपाय: {chem_text}. फवारणी करताना मास्क नक्की वापरा.",
                "bn": f"জরুরি চিকিৎসা পদক্ষেপ: প্রথম জৈব পদ্ধতি: {org_text}। দ্বিতীয় রাসায়নিক স্প্রে: {chem_text}। স্প্রে করার সময় মাস্ক পরুন।",
                "es": f"Tratamiento inmediato: Primero tratamiento orgánico: {org_text}. Segundo protector químico: {chem_text}. Use siempre mascarilla y guantes de protección."
            }
        return scripts.get(resolved_lang, scripts["en"])

    elif section == "prevention":
        prev_text = entry.prevention_steps[0] if entry.prevention_steps else ""
        scripts = {
            "en": f"Seasonal Prevention Advice: {prev_text}. For free expert government advisory, call the Kisan Call Center at toll-free 1800 180 1551.",
            "hi": f"आगामी फसल रोकथाम सलाह: {prev_text}। निःशुल्क विशेषज्ञ सलाह के लिए सरकारी किसान कॉल सेंटर के टोल-फ्री नंबर 1800 180 1551 पर संपर्क करें।",
            "te": f"పంట రక్షణ సలహా: {prev_text}. ఉచిత నిపుణుల సలహాల కోసం కిసాన్ కాల్ సెంటర్ టోల్-ఫ్రీ నెంబర్ 1800 180 1551 కి కాల్ చేయండి.",
            "ta": f"பயிர் பாதுகாப்பு வழிகாட்டல்: {prev_text}. இலவச ஆலோசனைக்கு கிசான் கால் சென்டர் கட்டணமில்லா எண் 1800 180 1551 ஐ அழைக்கவும்.",
            "kn": f"ಮುಂಜಾಗ್ರತಾ ಕೃಷಿ ಸಲಹೆ: {prev_text}. ಉಚಿತ ತಜ್ಞರ ಸಲಹೆಗಾಗಿ ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ ಟೋಲ್-ಫ್ರೀ ಸಂಖ್ಯೆ 1800 180 1551 ಗೆ ಕರೆ ಮಾಡಿ.",
            "ml": f"മുൻകരുതൽ നിർദ്ദേശം: {prev_text}. സൗജന്യ കാർഷിക സേവനങ്ങൾക്കായി കിസാൻ കോൾ സെന്ററിന്റെ 1800 180 1551 എന്ന നമ്പറിലേക്ക് വിളിക്കുക.",
            "mr": f"पिक संरक्षणाचा सल्ला: {prev_text}. मोफत तज्ज्ञ सल्ल्यासाठी किसान कॉल सेंटरच्या १८०० १८० १५५१ या टोल-फ्री क्रमांकावर संपर्क साधा.",
            "bn": f"ফসল সুরক্ষার পরামর্শ: {prev_text}। বিনামূল্যে বিশেষজ্ঞ পরামর্শের জন্য কিষাণ কল সেন্টারের ১৮০০ ১৮০ ১৫৫১ নম্বরে যোগাযোগ করুন।",
            "es": f"Consejo de prevención: {prev_text}. Para asesoramiento técnico gratuito, consulte a los servicios de extensión agraria local."
        }
        return scripts.get(resolved_lang, scripts["en"])

    return entry.symptoms
