"""Generates comprehensive and validated agronomic datasets for 9 languages:
English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn), Malayalam (ml), Marathi (mr), Bengali (bn), Spanish (es).
"""
import json
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_I18N_DIR = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = BACKEND_I18N_DIR / "glossary"
FRONTEND_LOCALES_DIR = BASE_DIR / "frontend" / "src" / "i18n" / "locales"

GLOSSARY_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_LOCALES_DIR.mkdir(parents=True, exist_ok=True)

# Load canonical English diseases
with open(BASE_DIR / "backend" / "app" / "knowledge_base" / "diseases.yaml", "r", encoding="utf-8") as f:
    en_kb_raw = yaml.safe_load(f)

en_diseases = {d["id"]: d for d in en_kb_raw["diseases"]}

# Crop names mapping
CROP_NAMES = {
    "Apple": {
        "en": "Apple", "hi": "सेब (Apple)", "te": "యాపిల్ (Apple)", "ta": "ஆப்பிள் (Apple)",
        "kn": "ಸೇಬು (Apple)", "ml": "ആപ്പിൾ (Apple)", "mr": "सफरचंद (Apple)", "bn": "আপেল (Apple)", "es": "Manzana"
    },
    "Blueberry": {
        "en": "Blueberry", "hi": "ब्लूबेरी (Blueberry)", "te": "బ్లూబెర్రీ (Blueberry)", "ta": "புளூபெர்ரி (Blueberry)",
        "kn": "ಬ್ಲೂಬೆರ್ರಿ (Blueberry)", "ml": "ബ്ലൂബെറി (Blueberry)", "mr": "ब्लूबेरी (Blueberry)", "bn": "ব্লুবেরি (Blueberry)", "es": "Arándano"
    },
    "Cherry": {
        "en": "Cherry", "hi": "चेरी (Cherry)", "te": "చెర్రీ (Cherry)", "ta": "செர்ரி (Cherry)",
        "kn": "ಚೆರ್ರಿ (Cherry)", "ml": "ചെറി (Cherry)", "mr": "चेरी (Cherry)", "bn": "চেরি (Cherry)", "es": "Cereza"
    },
    "Corn (Maize)": {
        "en": "Corn (Maize)", "hi": "मक्का (Corn / Maize)", "te": "మొక్కజొన్న (Maize)", "ta": "மக்காச்சோளம் (Corn)",
        "kn": "ಮೆಕ್ಕೆಜೋಳ (Maize)", "ml": "മക്കച്ചോളം (Maize)", "mr": "मका (Maize)", "bn": "ভুট্টা (Maize)", "es": "Maíz"
    },
    "Grape": {
        "en": "Grape", "hi": "अंगूर (Grape)", "te": "ద్రాక్ష (Grape)", "ta": "திராட்சை (Grape)",
        "kn": "ದ್ರಾಕ್ಷಿ (Grape)", "ml": "മുന്തിരി (Grape)", "mr": "द्राक्ष (Grape)", "bn": "আঙ্গুর (Grape)", "es": "Uva"
    },
    "Orange": {
        "en": "Orange (Citrus)", "hi": "संतरा / मौसंबी (Citrus)", "te": "బత్తాయి / నారింజ (Citrus)", "ta": "ஆரஞ்சு / எலுமிச்சை (Citrus)",
        "kn": "ಕಿತ್ತಳೆ (Citrus)", "ml": "ഓറഞ്ച് (Citrus)", "mr": "संत्रे / मोसंबी (Citrus)", "bn": "লেবু / কমলা (Citrus)", "es": "Naranja (Cítricos)"
    },
    "Peach": {
        "en": "Peach", "hi": "आड़ू (Peach)", "te": "పీచ్ (Peach)", "ta": "பீச் (Peach)",
        "kn": "ಪೀಚ್ (Peach)", "ml": "പീച്ച് (Peach)", "mr": "पीच (Peach)", "bn": "পীচ (Peach)", "es": "Melocotón / Durazno"
    },
    "Pepper (Bell)": {
        "en": "Bell Pepper / Capsicum", "hi": "शिमला मिर्च (Capsicum)", "te": "క్యాప్సికం / బెంగళూరు మిరప", "ta": "குடைமிளகாய் (Capsicum)",
        "kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (Capsicum)", "ml": "ക്യാപ്സിക്കം (Capsicum)", "mr": "ढोबळी मिरची (Capsicum)", "bn": "ক্যাপসিকাম / মিষ্টি মরিচ", "es": "Pimiento morrón"
    },
    "Potato": {
        "en": "Potato", "hi": "आलू (Potato)", "te": "బంగాళాదుంప (Potato)", "ta": "உருளைக்கிழங்கு (Potato)",
        "kn": "ಆಲೂಗಡ್ಡೆ (Potato)", "ml": "ഉരുളക്കിഴങ്ങ് (Potato)", "mr": "बटाटा (Potato)", "bn": "আলু (Potato)", "es": "Patata / Papa"
    },
    "Raspberry": {
        "en": "Raspberry", "hi": "रास्पबेरी (Raspberry)", "te": "రాస్ప్‌బెర్రీ (Raspberry)", "ta": "ராஸ்பெர்ரி (Raspberry)",
        "kn": "ರಾಸ್ಪ್ಬೆರಿ (Raspberry)", "ml": "റാസ്പ്ബെറി (Raspberry)", "mr": "रास्पबेरी (Raspberry)", "bn": "রাস্পবেরি (Raspberry)", "es": "Frambuesa"
    },
    "Soybean": {
        "en": "Soybean", "hi": "सोयाबीन (Soybean)", "te": "సోయాచిక్కుడు (Soybean)", "ta": "சோயாபீன் (Soybean)",
        "kn": "ಸೋಯಾಬೀನ್ (Soybean)", "ml": "സോയാബീൻ (Soybean)", "mr": "सोयाबीन (Soybean)", "bn": "সয়াবিন (Soybean)", "es": "Soja / Soya"
    },
    "Squash": {
        "en": "Squash / Pumpkin", "hi": "कद्दू / चप्पन कद्दू (Squash)", "te": "గుమ్మడి / స్క్వాష్ (Squash)", "ta": "பூசணி / சுரைக்காய் (Squash)",
        "kn": "ಕುಂಬಳಕಾಯಿ (Squash)", "ml": "മത്തങ്ങ (Squash)", "mr": "भोपळा (Squash)", "bn": "মিষ্টি কুমড়া (Squash)", "es": "Calabacín / Calabaza"
    },
    "Strawberry": {
        "en": "Strawberry", "hi": "स्ट्रॉबेरी (Strawberry)", "te": "స్ట్రాబెర్రీ (Strawberry)", "ta": "ஸ்ட்ராபெர்ரி (Strawberry)",
        "kn": "ಸ್ಟ್ರಾಬೆರಿ (Strawberry)", "ml": "സ്ട്രോബെറി (Strawberry)", "mr": "स्ट्रॉबेरी (Strawberry)", "bn": "স্ট্রবেরি (Strawberry)", "es": "Fresa / Frutilla"
    },
    "Tomato": {
        "en": "Tomato", "hi": "टमाटर (Tomato)", "te": "టమోటా (Tomato)", "ta": "தக்காளி (Tomato)",
        "kn": "ಟೊಮೇಟೊ (Tomato)", "ml": "തക്കാളി (Tomato)", "mr": "टोमॅटो (Tomato)", "bn": "টমেটো (Tomato)", "es": "Tomate"
    }
}

print("Base definition tables configured.")
