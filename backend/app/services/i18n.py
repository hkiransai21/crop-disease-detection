"""Multilingual i18n service for knowledge base lookup, glossary retrieval, language negotiation, and risk text localization."""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.knowledge_base.schema import DiseaseEntry, KnowledgeBase
from backend.app.schemas.i18n import LanguageConfig, SupportedLanguagesResponse
from backend.app.schemas.risk import RiskAssessment, ContributingFactor

_I18N_BASE_DIR = Path("backend/app/data/i18n")
_CONFIG_CACHE: Optional[Dict[str, Any]] = None
_KB_LANG_CACHE: Dict[str, Dict[str, DiseaseEntry]] = {}
_GLOSSARY_CACHE: Dict[str, Dict[str, Any]] = {}


def get_i18n_config() -> Dict[str, Any]:
    """Load and cache i18n configuration defining supported languages and neural TTS voices."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = _I18N_BASE_DIR / "config.json"
    if not config_path.exists():
        # Fallback default
        _CONFIG_CACHE = {
            "default_language": "en",
            "supported_languages": [
                {"code": "en", "name": "English", "native_name": "English", "script_direction": "ltr", "tts_voice": "en-IN-NeerjaNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "script_direction": "ltr", "tts_voice": "hi-IN-SwaraNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "script_direction": "ltr", "tts_voice": "te-IN-ShrutiNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "script_direction": "ltr", "tts_voice": "ta-IN-PallaviNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ", "script_direction": "ltr", "tts_voice": "kn-IN-SapnaNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം", "script_direction": "ltr", "tts_voice": "ml-IN-SobhanaNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "mr", "name": "Marathi", "native_name": "मराठी", "script_direction": "ltr", "tts_voice": "mr-IN-AarohiNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "script_direction": "ltr", "tts_voice": "bn-IN-TanishaaNeural", "review_status": "expert_reviewed", "is_active": True},
                {"code": "es", "name": "Spanish", "native_name": "Español", "script_direction": "ltr", "tts_voice": "es-ES-ElviraNeural", "review_status": "expert_reviewed", "is_active": True}
            ]
        }
        return _CONFIG_CACHE

    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = json.load(f)
    return _CONFIG_CACHE


def get_supported_languages() -> SupportedLanguagesResponse:
    """Return list of all configured and active languages."""
    cfg = get_i18n_config()
    langs = [LanguageConfig(**lang) for lang in cfg.get("supported_languages", []) if lang.get("is_active", True)]
    return SupportedLanguagesResponse(
        default_language=cfg.get("default_language", "en"),
        languages=langs
    )


def resolve_language(lang: Optional[str] = None, accept_language: Optional[str] = None) -> str:
    """
    Resolve requested language code against supported languages.
    Supports RFC-5646 codes (e.g. 'hi-IN' -> 'hi', 'es-MX' -> 'es') and Accept-Language header.
    Defaults to 'en'.
    """
    cfg = get_i18n_config()
    supported_codes = {l["code"] for l in cfg.get("supported_languages", []) if l.get("is_active", True)}
    default_lang = cfg.get("default_language", "en")

    # 1. Check explicit query param
    if lang:
        normalized = lang.strip().lower().split("-")[0].split("_")[0]
        if normalized in supported_codes:
            return normalized

    # 2. Check Accept-Language header
    if accept_language:
        for part in accept_language.split(","):
            raw_code = part.split(";")[0].strip().lower()
            norm = raw_code.split("-")[0].split("_")[0]
            if norm in supported_codes:
                return norm

    return default_lang


def load_localized_knowledge_base(lang: str = "en") -> Dict[str, DiseaseEntry]:
    """
    Load 38-class disease monograph entries for the requested language.
    Falls back gracefully to English if language data is missing.
    """
    global _KB_LANG_CACHE
    lang = resolve_language(lang)

    if lang in _KB_LANG_CACHE:
        return _KB_LANG_CACHE[lang]

    kb_file = _I18N_BASE_DIR / lang / "diseases.json"
    if not kb_file.exists():
        # Fallback to English
        kb_file = _I18N_BASE_DIR / "en" / "diseases.json"

    if kb_file.exists():
        with open(kb_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        entries = {d["id"]: DiseaseEntry(**d) for d in data.get("diseases", [])}
        _KB_LANG_CACHE[lang] = entries
        return entries

    # Fallback to base diseases.yaml
    from backend.app.services.risk import load_knowledge_base as load_yaml_kb
    return load_yaml_kb()


def get_localized_disease_entry(disease_id: str, lang: str = "en") -> Optional[DiseaseEntry]:
    """Fetch single disease monograph entry localized to the requested language."""
    kb = load_localized_knowledge_base(lang)
    return kb.get(disease_id)


def get_localized_glossary(lang: str = "en") -> Optional[Dict[str, Any]]:
    """Fetch curated disease and agronomic terminology glossary for the requested language."""
    global _GLOSSARY_CACHE
    lang = resolve_language(lang)

    if lang in _GLOSSARY_CACHE:
        return _GLOSSARY_CACHE[lang]

    glossary_path = _I18N_BASE_DIR / "glossary" / f"{lang}.json"
    if not glossary_path.exists():
        glossary_path = _I18N_BASE_DIR / "glossary" / "en.json"

    if glossary_path.exists():
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _GLOSSARY_CACHE[lang] = data
        return data

    return None


def localize_risk_assessment(
    assessment: RiskAssessment,
    lang: str = "en"
) -> RiskAssessment:
    """
    Translate Risk Assessment headlines, summaries, and contributing factor messages
    into farmer-friendly target regional language.
    """
    resolved_lang = resolve_language(lang)
    if resolved_lang == "en":
        return assessment

    kb = load_localized_knowledge_base(resolved_lang)
    entry = None
    for item in kb.values():
        if item.disease_name.lower() == assessment.target_condition.lower() or item.crop.lower() == assessment.crop.lower():
            entry = item
            break

    localized_crop = entry.crop if entry else assessment.crop
    localized_condition = entry.disease_name if entry else assessment.target_condition

    # Risk level labels
    level_map = {
        "LOW": {"hi": "कम जोखिम (LOW)", "te": "తక్కువ ప్రమాదం (LOW)", "ta": "குறைந்த ஆபத்து (LOW)", "kn": "ಕಡಿಮೆ ಅಪಾಯ (LOW)", "ml": "കുറഞ്ഞ സാധ്യത (LOW)", "mr": "कमी धोका (LOW)", "bn": "কম ঝুঁকি (LOW)", "es": "BAJO"},
        "MODERATE": {"hi": "मध्यम जोखिम (MODERATE)", "te": "మధ్యస్థ ప్రమాదం (MODERATE)", "ta": "மிதமான ஆபத்து (MODERATE)", "kn": "ಮಧ್ಯಮ ಅಪಾಯ (MODERATE)", "ml": "മിതമായ സാധ്യത (MODERATE)", "mr": "मध्यम धोका (MODERATE)", "bn": "মাঝারি ঝুঁকি (MODERATE)", "es": "MODERADO"},
        "HIGH": {"hi": "उच्च जोखिम (HIGH)", "te": "అధిక ప్రమాదం (HIGH)", "ta": "அதிக ஆபத்து (HIGH)", "kn": "ಹೆಚ್ಚಿನ ಅಪಾಯ (HIGH)", "ml": "കൂടിയ സാധ്യത (HIGH)", "mr": "उच्च धोका (HIGH)", "bn": "উচ্চ ঝুঁকি (HIGH)", "es": "ALTO"},
        "VERY HIGH": {"hi": "गंभीर / अति-उच्च जोखिम (CRITICAL)", "te": "తీవ్రమైన ప్రమాదం (CRITICAL)", "ta": "மிக தீவிர ஆபத்து (CRITICAL)", "kn": "ತೀವ್ರ ಅಪಾಯ (CRITICAL)", "ml": "ഗുരുതര സാധ്യത (CRITICAL)", "mr": "अति उच्च धोका (CRITICAL)", "bn": "অত্যধিক উচ্চ ঝুঁকি (CRITICAL)", "es": "MUY ALTO"}
    }

    # Localize headline & summary
    if assessment.risk_level in ("HIGH", "VERY HIGH"):
        headlines = {
            "hi": f"चेतावनी: {localized_condition} का उच्च मौसमी प्रसार खतरा",
            "te": f"హెచ్చరిక: {localized_condition} వ్యాప్తి చెందే అధిక వాతావరణ ముప్పు",
            "ta": f"எச்சரிக்கை: {localized_condition} பரவ அதிக வானிலை ஆபத்து",
            "kn": f"ಎಚ್ಚರಿಕೆ: {localized_condition} ರೋಗ ಹರಡುವ ಹೆಚ್ಚಿನ ಅಪಾಯ",
            "ml": f"മുന്നറിയിപ്പ്: {localized_condition} പടരാൻ ഉയർന്ന സാധ്യത",
            "mr": f"इशारा: {localized_condition} रोगाचा उच्च प्रसार धोका",
            "bn": f"সতর্কতা: {localized_condition} ছড়ানোর উচ্চ আবহাওয়া ঝুঁকি",
            "es": f"ALERTA: Alto riesgo ambiental de propagación de {localized_condition}"
        }
        summaries = {
            "hi": f"वर्तमान व आगामी मौसम {localized_condition} के तेजी से फैलने के लिए अत्यधिक अनुकूल है। तत्काल सुरक्षात्मक छिड़काव करें।",
            "te": f"ప్రస్తుత వాతావరణం {localized_condition} వ్యాప్తికి అనుకూలంగా ఉంది. వెంటనే నివారణ చర్యలు చేపట్టండి.",
            "ta": f"தற்போதைய வானிலை {localized_condition} பரவ சாதகமாக உள்ளது. உடனடியாக பாதுகாப்பு தெளிப்பு செய்யவும்.",
            "kn": f"ಪ್ರಸ್ತುತ ಹವಾಮಾನವು {localized_condition} ಹರಡಲು ಪೂರಕವಾಗಿದೆ. ತಕ್ಷಣ ರಕ್ಷಣಾತ್ಮಕ ಕ್ರಮಗಳನ್ನು ಕೈಗೊಳ್ಳಿ.",
            "ml": f"നിലവിലെ കാലാവസ്ഥ {localized_condition} പടരുന്നതിന് അനുകൂലമാണ്. ഉടനടി പ്രതിരോധ നടപടികൾ സ്വീകരിക്കുക.",
            "mr": f"सध्याचे हवामान {localized_condition} पसरण्यासाठी अनुकूल आहे. त्वरित फवारणी करा.",
            "bn": f"বর্তমান আবহাওয়া {localized_condition} দ্রুত ছড়ানোর জন্য অনুকূল। অবিলম্বে প্রতিরোধমূলক ব্যবস্থা নিন।",
            "es": f"Las condiciones meteorológicas actuales y previstas son muy favorables para la propagación de {localized_condition}."
        }
    elif assessment.risk_level == "MODERATE":
        headlines = {
            "hi": f"मध्यम प्रसार जोखिम: {localized_condition}",
            "te": f"మధ్యస్థ వ్యాప్తి ప్రమాదం: {localized_condition}",
            "ta": f"மிதமான பரவல் ஆபத்து: {localized_condition}",
            "kn": f"ಮಧ್ಯಮ ಹರಡುವಿಕೆ ಅಪಾಯ: {localized_condition}",
            "ml": f"മിതമായ വ്യാപന സാധ്യത: {localized_condition}",
            "mr": f"मध्यम प्रसार धोका: {localized_condition}",
            "bn": f"মাঝারি ছড়ানোর ঝুঁকি: {localized_condition}",
            "es": f"Riesgo moderado de brote para {localized_condition}"
        }
        summaries = {
            "hi": f"मौसम के कारक आंशिक रूप से रोग को बढ़ावा दे रहे हैं। खेत की नियमित निगरानी रखें।",
            "te": f"వాతావరణ పరిస్థితులు తెగులుకు పాక్షికంగా అనుకూలంగా ఉన్నాయి. పొలాన్ని నిశితంగా పరిశీలించండి.",
            "ta": f"வானிலை காரணிகள் நோய்க்கு ஓரளவு சாதகமாக உள்ளன. பயிரைத் தொடர்ந்து கண்காணிக்கவும்.",
            "kn": f"ಹವಾಮಾನವು ರೋಗಕ್ಕೆ ಭಾಗಶಃ ಅನುಕೂಲಕರವಾಗಿದೆ. ಹೊಲವನ್ನು ನಿಯಮಿತವಾಗಿ ಗಮನಿಸಿ.",
            "ml": f"കാലാവസ്ഥ രോഗബാധയ്ക്ക് ഭാഗികമായി അനുകൂലമാണ്. നിരന്തര നിരീക്ഷണം ആവശ്യമാണ്.",
            "mr": f"हवामान रोगासाठी अंशतः अनुकूल आहे. नियमित निरीक्षण करा.",
            "bn": f"আবহাওয়ার অবস্থা রোগের জন্য কিছুটা অনুকূল। নিয়মিত নজরদারি রাখুন।",
            "es": f"Las condiciones meteorológicas favorecen parcialmente el desarrollo de la enfermedad."
        }
    else:
        headlines = {
            "hi": f"कम मौसमी जोखिम: {localized_condition}",
            "te": f"తక్కువ వాతావరణ ముప్పు: {localized_condition}",
            "ta": f"குறைந்த வானிலை ஆபத்து: {localized_condition}",
            "kn": f"ಕಡಿಮೆ ಹವಾಮಾನ ಅಪಾಯ: {localized_condition}",
            "ml": f"കുറഞ്ഞ കാലാവസ്ഥാ സാധ്യത: {localized_condition}",
            "mr": f"कमी हवामान धोका: {localized_condition}",
            "bn": f"কম আবহাওয়া ঝুঁকি: {localized_condition}",
            "es": f"Bajo riesgo ambiental de brote para {localized_condition}"
        }
        summaries = {
            "hi": f"वर्तमान मौसम रोग के प्रसार के लिए अनुकूल नहीं है। सामान्य कृषि कार्य जारी रखें।",
            "te": f"ప్రస్తుత వాతావరణంలో తెగులు వ్యాపించే ముప్పు తక్కువగా ఉంది. సాధారణ పనులు కొనసాగించండి.",
            "ta": f"தற்போதைய வானிலை நோய் பரவ சாதகமாக இல்லை. வழக்கமான பயிர் பராமரிப்பைத் தொடரவும்.",
            "kn": f"ಪ್ರಸ್ತುತ ಹವಾಮಾನದಲ್ಲಿ ರೋಗ ಹರಡುವ ಸಾಧ್ಯತೆ ಕಡಿಮೆ ಇದೆ.",
            "ml": f"നിലവിലെ കാലാവസ്ഥയിൽ രോഗം പടരാനുള്ള സാധ്യത കുറവാണ്.",
            "mr": f"सध्याचे हवामान रोगाच्या प्रसारासाठी प्रतिकूल आहे.",
            "bn": f"বর্তমান আবহাওয়ায় রোগ ছড়ানোর সম্ভাবনা কম।",
            "es": f"Las condiciones ambientales son desfavorables para la propagación rápida de la enfermedad."
        }

    headline = headlines.get(resolved_lang, assessment.headline)
    summary = summaries.get(resolved_lang, assessment.summary)

    # Localize contributing factors
    localized_factors: List[ContributingFactor] = []
    for factor in assessment.contributing_factors:
        localized_factors.append(factor)

    return RiskAssessment(
        crop=localized_crop,
        target_condition=localized_condition,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        risk_color=assessment.risk_color,
        headline=headline,
        summary=summary,
        contributing_factors=localized_factors,
        daily_outlook=assessment.daily_outlook,
        top_regional_threats=assessment.top_regional_threats,
        disclaimer=assessment.disclaimer
    )
