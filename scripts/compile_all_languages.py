"""Complete data compiler for AgriShield 9 languages.
Generates:
- backend/app/data/i18n/glossary/{lang}.json
- backend/app/data/i18n/{lang}/diseases.json
- frontend/src/i18n/locales/{lang}.json
"""
import json
import yaml
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_I18N = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = BACKEND_I18N / "glossary"
FRONTEND_LOCALES = BASE_DIR / "frontend" / "src" / "i18n" / "locales"

GLOSSARY_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_LOCALES.mkdir(parents=True, exist_ok=True)

with open(BASE_DIR / "backend" / "app" / "knowledge_base" / "diseases.yaml", "r", encoding="utf-8") as f:
    en_kb = yaml.safe_load(f)

# Common crop translations
CROPS = {
    "Apple": {"en": "Apple", "hi": "सेब", "te": "యాపిల్", "ta": "ஆப்பிள்", "kn": "ಸೇಬು", "ml": "ആപ്പിൾ", "mr": "सफरचंद", "bn": "আপেল", "es": "Manzana"},
    "Blueberry": {"en": "Blueberry", "hi": "ब्लूबेरी", "te": "బ్లూబెర్రీ", "ta": "புளூபெர்ரி", "kn": "ಬ್ಲೂಬೆರ್ರಿ", "ml": "ബ്ലൂബെറി", "mr": "ब्लूबेरी", "bn": "ব্লুবেরি", "es": "Arándano"},
    "Cherry": {"en": "Cherry", "hi": "चेरी", "te": "చెర్రీ", "ta": "செர்ரி", "kn": "ಚೆರ್ರಿ", "ml": "ചെറി", "mr": "चेरी", "bn": "চেরি", "es": "Cereza"},
    "Corn (Maize)": {"en": "Corn (Maize)", "hi": "मक्का", "te": "మొక్కజొన్న", "ta": "மக்காச்சோளம்", "kn": "ಮೆಕ್ಕೆಜೋಳ", "ml": "മക്കച്ചോളം", "mr": "मका", "bn": "ভুট্টা", "es": "Maíz"},
    "Grape": {"en": "Grape", "hi": "अंगूर", "te": "ద్రాక్ష", "ta": "திராட்சை", "kn": "ದ್ರಾಕ್ಷಿ", "ml": "മുന്തിരി", "mr": "द्राक्ष", "bn": "আঙ্গুর", "es": "Uva"},
    "Orange": {"en": "Orange (Citrus)", "hi": "संतरा / मौसंबी", "te": "బత్తాయి / నారింజ", "ta": "ஆரஞ்சு / எலுமிச்சை", "kn": "ಕಿತ್ತಳೆ", "ml": "ഓറഞ്ച്", "mr": "संत्रे / मोसंबी", "bn": "লেবু / কমলা", "es": "Naranja (Cítricos)"},
    "Peach": {"en": "Peach", "hi": "आड़ू", "te": "పీచ్", "ta": "பீச்", "kn": "ಪೀಚ್", "ml": "പീച്ച്", "mr": "पीच", "bn": "পীচ", "es": "Melocotón / Durazno"},
    "Pepper (Bell)": {"en": "Bell Pepper / Capsicum", "hi": "शिमला मिर्च", "te": "క్యాప్సికం / బెంగళూరు మిరప", "ta": "குடைமிளகாய்", "kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ", "ml": "ക്യാപ്സിക്കം", "mr": "ढोबळी मिरची", "bn": "ক্যাপসিকাম", "es": "Pimiento morrón"},
    "Potato": {"en": "Potato", "hi": "आलू", "te": "బంగాళాదుంప", "ta": "உருளைக்கிழங்கு", "kn": "ಆಲೂಗಡ್ಡೆ", "ml": "ഉരുളക്കിഴങ്ങ്", "mr": "बटाटा", "bn": "আলু", "es": "Patata / Papa"},
    "Raspberry": {"en": "Raspberry", "hi": "रास्पबेरी", "te": "రాస్ప్‌బెర్రీ", "ta": "ராஸ்பெர்ரி", "kn": "ರಾಸ್ಪ್ಬೆರಿ", "ml": "റാസ്പ്ബെറി", "mr": "रास्पबेरी", "bn": "রাস্পবেরি", "es": "Frambuesa"},
    "Soybean": {"en": "Soybean", "hi": "सोयाबीन", "te": "సోయాచిక్కుడు", "ta": "சோயாபீன்", "kn": "ಸೋಯಾಬೀನ್", "ml": "സോയാബീൻ", "mr": "सोयाबीन", "bn": "সয়াবিন", "es": "Soja / Soya"},
    "Squash": {"en": "Squash / Pumpkin", "hi": "कद्दू / चप्पन कद्दू", "te": "గుమ్మడి / స్క్వాష్", "ta": "பூசணி / சுரைக்காய்", "kn": "ಕುಂಬಳಕಾಯಿ", "ml": "മത്തങ്ങ", "mr": "भोपळा", "bn": "মিষ্টি কুমড়া", "es": "Calabacín / Calabaza"},
    "Strawberry": {"en": "Strawberry", "hi": "स्ट्रॉबेरी", "te": "స్ట్రాబెర్రీ", "ta": "ஸ்ட்ராபெர்ரி", "kn": "ಸ್ಟ್ರಾಬೆರಿ", "ml": "സ്ട്രോബെറി", "mr": "स्ट्रॉबेरी", "bn": "স্ট্রবেরি", "es": "Fresa / Frutilla"},
    "Tomato": {"en": "Tomato", "hi": "टमाटर", "te": "టమోటా", "ta": "தக்காளி", "kn": "ಟೊಮೇಟೊ", "ml": "തക്കാളി", "mr": "टोमॅटो", "bn": "টমেটো", "es": "Tomate"}
}

# 38 Disease specific translations dictionary
DISEASE_DICTS = {
    "Apple___Apple_scab": {
        "names": {"en": "Apple Scab", "hi": "सेब का पपड़ी रोग (Apple Scab)", "te": "యాపిల్ పొలుసు తెగులు (Apple Scab)", "ta": "ஆப்பிள் செதில் நோய் (Apple Scab)", "kn": "ಸೇಬು ಕಜ್ಜಿ ರೋಗ (Apple Scab)", "ml": "ആപ്പിൾ സ്കാബ് രോഗം (Apple Scab)", "mr": "सफरचंद खपली रोग (Apple Scab)", "bn": "আপেল স্ক্যাব বা খোস রোগ (Apple Scab)", "es": "Sarna del manzano (Moteado)"},
        "tts": {"en": "Apple Scab fungal infection", "hi": "सेब का पपड़ी रोग यानी एप्पल स्कैब", "te": "యాపిల్ పొలుసు తెగులు", "ta": "ஆப்பிள் செதில் நோய்", "kn": "ಸೇಬು ಕಜ್ಜಿ ರೋಗ", "ml": "ആപ്പിൾ സ്കാബ് രോഗം", "mr": "सफरचंद खपली रोग", "bn": "আপেল স্ক্যাব রোগ", "es": "Sarna del manzano"},
        "translit": "Apple Scab",
        "alt_names": {"en": ["Black Spot of Apple"], "hi": ["काला धब्बा"], "te": ["నల్ల మచ్చ"], "ta": ["கருந்தழும்பு"], "kn": ["ಕಪ್ಪು ಮಚ್ಚೆ"], "ml": ["കറുത്ത പാട്"], "mr": ["काळे डाग"], "bn": ["কালো দাগ"], "es": ["Moteado del manzano"]}
    },
    "Apple___Black_rot": {
        "names": {"en": "Black Rot & Frogeye Leaf Spot", "hi": "सेब का ब्लैक रॉट व मेढक-आंख धब्बा", "te": "యాపిల్ నల్ల కుళ్ళు & కప్పకన్ను మచ్చ తెగులు", "ta": "ஆப்பிள் கறுப்பு அழுகல் மற்றும் தவளைக்கண் இலைப்புள்ளி", "kn": "ಸೇಬು ಕಪ್ಪು ಕೊಳೆ ರೋಗ & ಕಪ್ಪೆಗಣ್ಣು ಮಚ್ಚೆ", "ml": "ആപ്പിൾ ബ്ലാക്ക് റോട്ട് & തവളക്കണ്ണൻ പുള്ളിക്കുത്ത്", "mr": "सफरचंद काळी कुज आणि फ्रॉग-आय डाग", "bn": "আপেল ব্ল্যাক রট ও ব্যাঙের চোখের মতো পাতার দাগ", "es": "Podredumbre negra y mancha de ojo de rana"},
        "tts": {"en": "Apple Black Rot and Frogeye Leaf Spot", "hi": "सेब का ब्लैक रॉट और पत्ती धब्बा रोग", "te": "యాపిల్ నల్ల కుళ్ళు తెగులు", "ta": "ஆப்பிள் கறுப்பு அழுகல் நோய்", "kn": "ಸೇಬು ಕಪ್ಪು ಕೊಳೆ ರೋಗ", "ml": "ആപ്പിൾ ബ്ലാക്ക് റോട്ട് രോഗം", "mr": "सफरचंद काळी कुज रोग", "bn": "আপেল ব্ল্যাক রট রোগ", "es": "Podredumbre negra del manzano"},
        "translit": "Apple Black Rot",
        "alt_names": {"en": ["Frogeye Leaf Spot"], "hi": ["काला सड़न रोग"], "te": ["నల్ల కుళ్ళు"], "ta": ["கறுப்பு அழுகல்"], "kn": ["ಕಪ್ಪು ಕೊಳೆ"], "ml": ["കറുത്ത ചീയൽ"], "mr": ["काळी कुज"], "bn": ["কালো পচন"], "es": ["Ojo de rana del manzano"]}
    },
    "Apple___Cedar_apple_rust": {
        "names": {"en": "Cedar Apple Rust", "hi": "सेब का देवदार रतुआ रोग (Cedar Apple Rust)", "te": "యాపిల్ సెడార్ రస్ట్ (తుప్పు తెగులు)", "ta": "ஆப்பிள் செடார் துரு நோய்", "kn": "ಸೇಬು ತುಕ್ಕು ರೋಗ (Cedar Apple Rust)", "ml": "ആപ്പിൾ തുരുമ്പ് രോഗം (Cedar Apple Rust)", "mr": "सफरचंद तांबेरा रोग (Cedar Apple Rust)", "bn": "আপেল সিডার মরিচা রোগ (Cedar Apple Rust)", "es": "Roya del manzano y del enebro"},
        "tts": {"en": "Cedar Apple Rust fungal disease", "hi": "सेब का रतुआ रोग यानी सीडार एप्पल रस्ट", "te": "యాపిల్ తుప్పు తెగులు", "ta": "ஆப்பிள் துரு நோய்", "kn": "ಸೇಬು ತುಕ್ಕು ರೋಗ", "ml": "ആപ്പിൾ തുരുമ്പ് രോഗം", "mr": "सफरचंद तांबेरा रोग", "bn": "আপেল মরিচা রোগ", "es": "Roya del manzano"},
        "translit": "Cedar Apple Rust",
        "alt_names": {"en": ["Gymnosporangium Rust"], "hi": ["रतुआ रोग"], "te": ["తుప్పు మచ్చలు"], "ta": ["துருப்புள்ளி"], "kn": ["ಕಿತ್ತಳೆ ತುಕ್ಕು"], "ml": ["തുരുമ്പ് പാടുകൾ"], "mr": ["सफरचंद तांबेरा"], "bn": ["হলুদ মরিচা"], "es": ["Roya del cedro y manzano"]}
    },
    "Apple___healthy": {
        "names": {"en": "Healthy Apple Foliage", "hi": "स्वस्थ सेब के पत्ते", "te": "ఆరోగ్యకరమైన యాపిల్ ఆకులు", "ta": "ஆரோக்கியமான ஆப்பிள் இலை", "kn": "ಆರೋಗ್ಯಕರ ಸೇಬು ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള ആപ്പിൾ ഇലകൾ", "mr": "निरोगी सफरचंद पाने", "bn": "সুস্থ ও নিরোগ আপেল পাতা", "es": "Follaje de manzano sano"},
        "tts": {"en": "Healthy Apple crop foliage", "hi": "सेब की फसल स्वस्थ है", "te": "యాపిల్ పంట ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "ஆப்பிள் இலை ஆரோக்கியமாக உள்ளது", "kn": "ಸೇಬು ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "ആപ്പിൾ ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "सफरचंदाची पाने निरोगी आहेत", "bn": "আপেল পাতা সম্পূর্ণ সুস্থ", "es": "Hojas de manzano completamente sanas"},
        "translit": "Healthy Apple",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యవంతమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Blueberry___healthy": {
        "names": {"en": "Healthy Blueberry Foliage", "hi": "स्वस्थ ब्लूबेरी के पत्ते", "te": "ఆరోగ్యకరమైన బ్లూబెర్రీ ఆకులు", "ta": "ஆரோக்கியமான புளூபெர்ரி இலை", "kn": "ಆರೋಗ್ಯಕರ ಬ್ಲೂಬೆರ್ರಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള ബ്ലൂബെറി ഇലകൾ", "mr": "निरोगी ब्लूबेरी पाने", "bn": "সুস্থ ও নিরোগ ব্লুবেরি পাতা", "es": "Follaje de arándano sano"},
        "tts": {"en": "Healthy Blueberry foliage", "hi": "ब्लूबेरी की पत्तियां स्वस्थ हैं", "te": "బ్లూబెర్రీ పంట ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "புளூபெர்ரி இலை ஆரோக்கியமாக உள்ளது", "kn": "ಬ್ಲೂಬೆರ್ರಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "ബ്ലൂബെറി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "ब्लूबेरीची पाने निरोगी आहेत", "bn": "ব্লুবেরি পাতা সম্পূর্ণ সুস্থ", "es": "Hojas de arándano completamente sanas"},
        "translit": "Healthy Blueberry",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యవంతమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "names": {"en": "Cherry Powdery Mildew", "hi": "चेरी का चूर्णिल आसिता (Powdery Mildew)", "te": "చెర్రీ బూడిద తెగులు (Powdery Mildew)", "ta": "செர்ரி சாம்பல் நோய் (Powdery Mildew)", "kn": "ಚೆರ್ರಿ ಬೂದಿ ರೋಗ (Powdery Mildew)", "ml": "ചെറി ചാരപ്പൂപ്പ് രോഗം (Powdery Mildew)", "mr": "चेरी भुरी रोग (Powdery Mildew)", "bn": "চেরি পাউডারি মিলডিউ বা সাদা গুঁড়ো রোগ", "es": "Oídio del cerezo (Ceniza)"},
        "tts": {"en": "Cherry Powdery Mildew fungal infection", "hi": "चेरी का चूर्णिल फफूंद यानी पाउडरी मिल्ड्यू रोग", "te": "చెర్రీ బూడిద తెగులు", "ta": "செர்ரி சாம்பல் நோய்", "kn": "ಚೆರ್ರಿ ಬೂದಿ ರೋಗ", "ml": "ചെറി ചാരപ്പൂപ്പ് രോഗം", "mr": "चेरी भुरी रोग", "bn": "চেরি পাউডারি মিলডিউ রোগ", "es": "Oídio o ceniza del cerezo"},
        "translit": "Cherry Powdery Mildew",
        "alt_names": {"en": ["Podosphaera Mildew"], "hi": ["सफेद चूर्ण रोग"], "te": ["తెల్ల బూడిద"], "ta": ["வெள்ளை சாம்பல்"], "kn": ["ಬಿಳಿ ಬೂದಿ"], "ml": ["വെള്ളപ്പൂപ്പ്"], "mr": ["भुरी रोग"], "bn": ["সাদা পাউডার রোগ"], "es": ["Cenicilla del cerezo"]}
    },
    "Cherry_(including_sour)___healthy": {
        "names": {"en": "Healthy Cherry Foliage", "hi": "स्वस्थ चेरी के पत्ते", "te": "ఆరోగ్యకరమైన చెర్రీ ఆకులు", "ta": "ஆரோக்கியமான செர்ரி இலை", "kn": "ಆರೋಗ್ಯಕರ ಚೆರ್ರಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള ചെറി ഇലകൾ", "mr": "निरोगी चेरी पाने", "bn": "সুস্থ ও নিরোগ চেরি পাতা", "es": "Follaje de cerezo sano"},
        "tts": {"en": "Healthy Cherry crop foliage", "hi": "चेरी की फसल स्वस्थ है", "te": "చెర్రీ ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "செர்ரி இலை ஆரோக்கியமாக உள்ளது", "kn": "ಚೆರ್ರಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "ചെറി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "चेरीची पाने निरोगी आहेत", "bn": "চেরি পাতা সুস্থ ও রোগমুক্ত", "es": "Hojas de cerezo sanas"},
        "translit": "Healthy Cherry",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యవంతమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "names": {"en": "Corn Gray Leaf Spot & Cercospora", "hi": "मक्का का ग्रे लीफ स्पॉट (सर्कोस्पोरा धब्बा)", "te": "మొక్కజొన్న సర్కోస్పోరా బూడిద రంగు ఆకుమచ్చ తెగులు", "ta": "மக்காச்சோளம் சாம்பல் இலைப்புள்ளி நோய் (செர்கோஸ்போரா)", "kn": "ಮೆಕ್ಕೆಜೋಳ ಬೂದು ಎಲೆ ಮಚ್ಚೆ ರೋಗ (Cercospora)", "ml": "മക്കച്ചോളം ചാരനിറ ഇലപ്പുള്ളി രോഗം", "mr": "मका करपा व करडा पानांवरील ठिपके रोग (Cercospora)", "bn": "ভুট্টার ধূসর পাতার দাগ ও সারকোস্পোরা রোগ", "es": "Mancha gris de la hoja del maíz (Cercospora)"},
        "tts": {"en": "Corn Gray Leaf Spot fungal infection", "hi": "मक्के का ग्रे लीफ स्पॉट और सर्कोस्पोरा पत्ती धब्बा रोग", "te": "మొక్కజొన్న సర్కోస్పోరా ఆకుమచ్చ తెగులు", "ta": "மக்காச்சோளம் சாம்பல் இலைப்புள்ளி நோய்", "kn": "ಮೆಕ್ಕೆಜೋಳ ಬೂದು ಎಲೆ ಮಚ್ಚೆ ರೋಗ", "ml": "മക്കച്ചോളം ചാരനിറ ഇലപ്പുള്ളി രോഗം", "mr": "मका करपा व करडा ठिपके रोग", "bn": "ভুট্টার ধূসর পাতার দাগ রোগ", "es": "Mancha gris foliar del maíz"},
        "translit": "Corn Gray Leaf Spot",
        "alt_names": {"en": ["Cercospora Leaf Spot"], "hi": ["मक्का धब्बा रोग"], "te": ["బూడిద ఆకుమచ్చ"], "ta": ["சாம்பல் புள்ளி"], "kn": ["ಬೂದು ಮಚ್ಚೆ"], "ml": ["ഇലപ്പുള്ളി"], "mr": ["करपा रोग"], "bn": ["ধূসর দাগ"], "es": ["Cercosporiosis del maíz"]}
    },
    "Corn_(maize)___Common_rust_": {
        "names": {"en": "Corn Common Rust", "hi": "मक्का का सामान्य रतुआ / गेरुई रोग (Common Rust)", "te": "మొక్కజొన్న తుప్పు తెగులు (Common Rust)", "ta": "மக்காச்சோளம் பொதுவான துரு நோய் (Common Rust)", "kn": "ಮೆಕ್ಕೆಜೋಳ ತುಕ್ಕು ರೋಗ (Common Rust)", "ml": "മക്കച്ചോളം തുരുമ്പ് രോഗം (Common Rust)", "mr": "मका तांबेरा रोग (Common Rust)", "bn": "ভুট্টার সাধারণ মরিচা রোগ (Common Rust)", "es": "Roya común del maíz"},
        "tts": {"en": "Corn Common Rust fungal infection", "hi": "मक्के का रतुआ या गेरुई रोग", "te": "మొక్కజొన్న తుప్పు తెగులు", "ta": "மக்காச்சோளம் துரு நோய்", "kn": "ಮೆಕ್ಕೆಜೋಳ ತುಕ್ಕು ರೋಗ", "ml": "മക്കച്ചോളം തുരുമ്പ് രോഗം", "mr": "मका तांबेरा रोग", "bn": "ভুট্টার সাধারণ মরিচা রোগ", "es": "Roya común del maíz"},
        "translit": "Corn Common Rust",
        "alt_names": {"en": ["Puccinia Rust"], "hi": ["गेरुई रोग"], "te": ["తుప్పు మచ్చ"], "ta": ["துரு நோய்"], "kn": ["ತುಕ್ಕು ರೋಗ"], "ml": ["തുരുമ്പ് രോഗം"], "mr": ["तांबेरा"], "bn": ["মরিচা রোগ"], "es": ["Roya de la hoja de maíz"]}
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "names": {"en": "Corn Northern Leaf Blight", "hi": "मक्का का उत्तरी पत्ता झुलसा रोग (Northern Leaf Blight)", "te": "మొక్కజొన్న నార్తర్న్ ఆకు ఎండు తెగులు (బ్లైట్)", "ta": "மக்காச்சோளம் வடக்கு இலை கருகல் நோய் (Northern Leaf Blight)", "kn": "ಮೆಕ್ಕೆಜೋಳ ಉತ್ತರ ಎಲೆ ಸುಟ್ಟ ರೋಗ (Northern Leaf Blight)", "ml": "മക്കച്ചോളം വടക്കൻ ഇല കരിച്ചിൽ രോഗം", "mr": "मका तुरा करपा किंवा उत्तर पान करपा", "bn": "ভুট্টার নর্দান লিফ ব্লাইট বা পাতার ঝলসানো রোগ", "es": "Tizón foliar del maíz (Helmintosporiosis norteña)"},
        "tts": {"en": "Corn Northern Leaf Blight fungal disease", "hi": "मक्के का उत्तरी पत्ता झुलसा रोग यानी नॉर्दर्न लीफ ब्लाइट", "te": "మొక్కజొన్న నార్తర్న్ ఆకు ఎండు తెగులు", "ta": "மக்காச்சோளம் வடக்கு இலை கருகல் நோய்", "kn": "ಮೆಕ್ಕೆಜೋಳ ಉತ್ತರ ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "മക്കച്ചോളം വടക്കൻ ഇല കരിച്ചിൽ രോഗം", "mr": "मका उत्तर पान करपा रोग", "bn": "ভুট্টার নর্দান লিফ ব্লাইট রোগ", "es": "Tizón foliar del maíz"},
        "translit": "Corn Northern Leaf Blight",
        "alt_names": {"en": ["Turcicum Leaf Blight"], "hi": ["पत्ता झुलसा"], "te": ["ఆకు ఎండు తెగులు"], "ta": ["இலை கருகல்"], "kn": ["ಎಲೆ ಸುಟ್ಟ ರೋಗ"], "ml": ["ഇല കരിച്ചിൽ"], "mr": ["पान करपा"], "bn": ["পাতা ঝলসানো"], "es": ["Helmintosporiosis del maíz"]}
    },
    "Corn_(maize)___healthy": {
        "names": {"en": "Healthy Corn Foliage", "hi": "स्वस्थ मक्का के पत्ते", "te": "ఆరోగ్యకరమైన మొక్కజొన్న ఆకులు", "ta": "ஆரோக்கியமான மக்காச்சோளம் இலை", "kn": "ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള മക്കച്ചോളം ഇലകൾ", "mr": "निरोगी मका पाने", "bn": "সুস্থ ও নিরোগ ভুট্টা পাতা", "es": "Follaje de maíz sano"},
        "tts": {"en": "Healthy Corn crop foliage", "hi": "मक्का की फसल बिल्कुल स्वस्थ है", "te": "మొక్కజొన్న ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "மக்காச்சோளம் பயிர் ஆரோக்கியமாக உள்ளது", "kn": "ಮೆಕ್ಕೆಜೋಳ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "മക്കച്ചോളം ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "मका पीक निरोगी आहे", "bn": "ভুট্টা পাতা সুস্থ ও রোগমুক্ত", "es": "Hojas de maíz sanas"},
        "translit": "Healthy Corn",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Grape___Black_rot": {
        "names": {"en": "Grape Black Rot", "hi": "अंगूर का ब्लैक रॉट (काला सड़न रोग)", "te": "ద్రాక్ష నల్ల కుళ్ళు తెగులు (Black Rot)", "ta": "திராட்சை கறுப்பு அழுகல் நோய் (Black Rot)", "kn": "ದ್ರಾಕ್ಷಿ ಕಪ್ಪು ಕೊಳೆ ರೋಗ (Black Rot)", "ml": "മുന്തിരി കറുത്ത ചീയൽ രോഗം (Black Rot)", "mr": "द्राक्ष काळी कुज रोग (Black Rot)", "bn": "আঙ্গুর ব্ল্যাক রট বা কালো পচন রোগ", "es": "Podredumbre negra de la vid (Black rot)"},
        "tts": {"en": "Grape Black Rot fungal disease", "hi": "अंगूर का काला सड़न रोग यानी ब्लैक रॉट", "te": "ద్రాక్ష నల్ల కుళ్ళు తెగులు", "ta": "திராட்சை கறுப்பு அழுகல் நோய்", "kn": "ದ್ರಾಕ್ಷಿ ಕಪ್ಪು ಕೊಳೆ ರೋಗ", "ml": "മുന്തിരി കറുത്ത ചീയൽ രോഗം", "mr": "द्राक्ष काळी कुज रोग", "bn": "আঙ্গুর ব্ল্যাক রট রোগ", "es": "Podredumbre negra de la vid"},
        "translit": "Grape Black Rot",
        "alt_names": {"en": ["Guignardia Rot"], "hi": ["काला सड़न"], "te": ["నల్ల కుళ్ళు"], "ta": ["கறுப்பு அழுகல்"], "kn": ["ಕಪ್ಪು ಕೊಳೆ"], "ml": ["കറുത്ത ചീയൽ"], "mr": ["काळी कुज"], "bn": ["কালো পচন"], "es": ["Podredumbre negra"]}
    },
    "Grape___Esca_(Black_Measles)": {
        "names": {"en": "Grape Esca (Black Measles)", "hi": "अंगूर का एस्का / ब्लैक मीसल्स रोग", "te": "ద్రాక్ష ఎస్కా (నల్ల పొంగు తెగులు / బ్లాక్ మీజిల్స్)", "ta": "திராட்சை எஸ்கா நோய் (கறுப்பு தட்டம்மை)", "kn": "ದ್ರಾಕ್ಷಿ ಎಸ್ಕಾ ರೋಗ (ಬ್ಲಾಕ್ ಮೀಸಲ್ಸ್)", "ml": "മുന്തിരി എസ്ക രോഗം (ബ്ലാക്ക് മീസിൽസ്)", "mr": "द्राक्ष एस्का किंवा काळा गोवर रोग", "bn": "আঙ্গুর এসকা বা ব্ল্যাক মিসেলস রোগ", "es": "Yesca de la vid (Esca o sarampión negro)"},
        "tts": {"en": "Grape Esca or Black Measles disease", "hi": "अंगूर का एस्का और ब्लैक मीसल्स रोग", "te": "ద్రాక్ష ఎస్కా తెగులు", "ta": "திராட்சை எஸ்கா நோய்", "kn": "ದ್ರಾಕ್ಷಿ ಎಸ್ಕಾ ರೋಗ", "ml": "മുന്തിരി എസ്ക രോഗം", "mr": "द्राक्ष एस्का रोग", "bn": "আঙ্গুর এসকা রোগ", "es": "Yesca de la vid"},
        "translit": "Grape Esca Black Measles",
        "alt_names": {"en": ["Vine Decline"], "hi": ["बाघ की धारियां रोग"], "te": ["పులి చారల మచ్చ"], "ta": ["புலி வரி நோய்"], "kn": ["ಹುಲಿ ಪಟ್ಟೆ ರೋಗ"], "ml": ["കടുവ വര രോഗം"], "mr": ["वाघाचे पट्टे डाग"], "bn": ["এসকা রোগ"], "es": ["Apolillado de la madera"]}
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "names": {"en": "Grape Leaf Blight (Isariopsis Leaf Spot)", "hi": "अंगूर का पत्ता झुलसा (आइसारियोप्सिस धब्बा)", "te": "ద్రాక్ష ఆకు ఎండు / ఇసారియోప్సిస్ ఆకుమచ్చ తెగులు", "ta": "திராட்சை இலை கருகல் (ஐசாரியோப்சிஸ் இலைப்புள்ளி)", "kn": "ದ್ರಾಕ್ಷಿ ಎಲೆ ಸುಟ್ಟ ರೋಗ (Isariopsis Spot)", "ml": "മുന്തിരി ഇല കരിച്ചിൽ രോഗം (Isariopsis Leaf Spot)", "mr": "द्राक्ष पान करपा व इसारिओप्सिस ठिपके रोग", "bn": "আঙ্গুর পাতা ঝলসানো ও ইসারিওপসিস পাতার দাগ", "es": "Tizón de la hoja de la vid (Mancha por Isariopsis)"},
        "tts": {"en": "Grape Leaf Blight fungal disease", "hi": "अंगूर का पत्ता झुलसा रोग यानी लीफ ब्लाइट", "te": "ద్రాక్ష ఆకు ఎండు తెగులు", "ta": "திராட்சை இலை கருகல் நோய்", "kn": "ದ್ರಾಕ್ಷಿ ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "മുന്തിരി ഇല കരിച്ചിൽ രോഗം", "mr": "द्राक्ष पान करपा रोग", "bn": "আঙ্গুর পাতা ঝলসানো রোগ", "es": "Tizón foliar de la vid"},
        "translit": "Grape Leaf Blight",
        "alt_names": {"en": ["Isariopsis Leaf Spot"], "hi": ["पत्ती झुलसा"], "te": ["ఆకుమచ్చ"], "ta": ["இலைப்புள்ளி"], "kn": ["ಎಲೆ ಮಚ್ಚೆ"], "ml": ["ഇലപ്പുള്ളി"], "mr": ["पान करपा"], "bn": ["পাতার দাগ"], "es": ["Mancha foliar de la vid"]}
    },
    "Grape___healthy": {
        "names": {"en": "Healthy Grape Foliage", "hi": "स्वस्थ अंगूर के पत्ते", "te": "ఆరోగ్యకరమైన ద్రాక్ష ఆకులు", "ta": "ஆரோக்கியமான திராட்சை இலை", "kn": "ಆರೋಗ್ಯಕರ ದ್ರಾಕ್ಷಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള മുന്തിരി ഇലകൾ", "mr": "निरोगी द्राक्ष पाने", "bn": "সুস্থ ও নিরোগ আঙ্গুর পাতা", "es": "Follaje de vid sano"},
        "tts": {"en": "Healthy Grape crop foliage", "hi": "अंगूर की बेल स्वस्थ है", "te": "ద్రాక్ష తోట ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "திராட்சை இலை ஆரோக்கியமாக உள்ளது", "kn": "ದ್ರಾಕ್ಷಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "മുന്തിരി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "द्राक्ष वेल निरोगी आहे", "bn": "আঙ্গুর পাতা সুস্থ ও নিরোগ", "es": "Hojas de vid completamente sanas"},
        "translit": "Healthy Grape",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "names": {"en": "Citrus Greening (Huanglongbing)", "hi": "नींबू / संतरे का सिट्रस ग्रीनिंग (हुआंगलोंगबिंग)", "te": "బత్తాయి / నారింజ గ్రీనింగ్ తెగులు (Huanglongbing)", "ta": "சிட்ரஸ் கிரீனிங் நோய் (எலுமிச்சை மஞ்சள் வரி நோய்)", "kn": "ಕಿತ್ತಳೆ ಗ್ರೀನಿಂಗ್ ರೋಗ (Citrus Greening / HLB)", "ml": "സിട്രസ് ഗ്രീനിംഗ് രോഗം (Huanglongbing)", "mr": "संत्रे-मोसंबी ग्रीनिंग रोग (Huanglongbing / HLB)", "bn": "লেবুর সাইট্রাস গ্রিনিং রোগ (হুয়াংলংবিং)", "es": "Huanglongbing de los cítricos (Citrus Greening)"},
        "tts": {"en": "Citrus Greening or Huanglongbing bacterial disease", "hi": "नींबू और संतरे का सिट्रस ग्रीनिंग रोग", "te": "బత్తాయి సిట్రస్ గ్రీనింగ్ తెగులు", "ta": "சிட்ரஸ் கிரீனிங் நோய்", "kn": "ಕಿತ್ತಳೆ ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ", "ml": "സിട്രസ് ഗ്രീനിംഗ് രോഗം", "mr": "संत्रे-मोसंबी ग्रीनिंग रोग", "bn": "লেবুর সাইট্রাস গ্রিনিং রোগ", "es": "Huanglongbing de los cítricos"},
        "translit": "Citrus Greening Huanglongbing",
        "alt_names": {"en": ["Yellow Dragon Disease", "HLB"], "hi": ["पीला ड्रैगन रोग"], "te": ["ఆకు పసుపు తెగులు"], "ta": ["மஞ்சள் நோய்"], "kn": ["ಹಳದಿ ರೋಗ"], "ml": ["മഞ്ഞളിപ്പ് രോഗം"], "mr": ["पिवळेपणा"], "bn": ["হলুদ রোগ"], "es": ["Dragón amarillo"]}
    },
    "Peach___Bacterial_spot": {
        "names": {"en": "Peach Bacterial Spot", "hi": "आड़ू का जीवाणु धब्बा रोग (Bacterial Spot)", "te": "పీచ్ బాక్టీరియా మచ్చ తెగులు (Bacterial Spot)", "ta": "பீச் பாக்டீரியா இலைப்புள்ளி நோய்", "kn": "ಪೀಚ್ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ", "ml": "പീച്ച് ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "पीच जिवाणूजन्य ठिपके रोग (Bacterial Spot)", "bn": "পীচ ব্যাকটেরিয়াল পাতার দাগ রোগ", "es": "Mancha bacteriana del melocotonero"},
        "tts": {"en": "Peach Bacterial Spot disease", "hi": "आड़ू का जीवाणु धब्बा रोग यानी बैक्टीरियल स्पॉट", "te": "పీచ్ బాక్టీరియా మచ్చ తెగులు", "ta": "பீச் பாக்டீரியா புள்ளி நோய்", "kn": "ಪೀಚ್ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ", "ml": "പീച്ച് ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "पीच जिवाणू ठिपके रोग", "bn": "পীচ ব্যাকটেরিয়াল দাগ রোগ", "es": "Mancha bacteriana del melocotón"},
        "translit": "Peach Bacterial Spot",
        "alt_names": {"en": ["Bacterial Shot Hole"], "hi": ["गोली छेद रोग"], "te": ["రంధ్రాల మచ్చ"], "ta": ["துளை நோய்"], "kn": ["ರಂಧ್ರ ಮಚ್ಚೆ"], "ml": ["ദ്വാര പുള്ളി"], "mr": ["गोळी भोक रोग"], "bn": ["ছিদ্র দাগ"], "es": ["Cribado bacteriano"]}
    },
    "Peach___healthy": {
        "names": {"en": "Healthy Peach Foliage", "hi": "स्वस्थ आड़ू के पत्ते", "te": "ఆరోగ్యకరమైన పీచ్ ఆకులు", "ta": "ஆரோக்கியமான பீச் இலை", "kn": "ಆರೋಗ್ಯಕರ ಪೀಚ್ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള പീച്ച് ഇലകൾ", "mr": "निरोगी पीच पाने", "bn": "সুস্থ ও নিরোগ পীচ পাতা", "es": "Follaje de melocotonero sano"},
        "tts": {"en": "Healthy Peach crop foliage", "hi": "आड़ू की फसल स्वस्थ है", "te": "పీచ్ ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "பீச் இலை ஆரோக்கியமாக உள்ளது", "kn": "ಪೀಚ್ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "പീച്ച് ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "पीच झाड निरोगी आहे", "bn": "পীচ পাতা সুস্থ ও রোগমুক্ত", "es": "Hojas de melocotonero sanas"},
        "translit": "Healthy Peach",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Pepper,_bell___Bacterial_spot": {
        "names": {"en": "Bell Pepper Bacterial Spot", "hi": "शिमला मिर्च का जीवाणु धब्बा रोग (Bacterial Spot)", "te": "క్యాప్సికం బాక్టీరియా మచ్చ తెగులు (Bacterial Spot)", "ta": "குடைமிளகாய் பாக்டீரியா இலைப்புள்ளி நோய்", "kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ", "ml": "ക്യാപ്സിക്കം ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "ढोबळी मिरची जिवाणूजन्य ठिपके रोग (Bacterial Spot)", "bn": "ক্যাপসিকাম ব্যাকটেরিয়াল পাতার দাগ রোগ", "es": "Mancha bacteriana del pimiento"},
        "tts": {"en": "Bell Pepper Bacterial Spot disease", "hi": "शिमला मिर्च का जीवाणु धब्बा रोग यानी बैक्टीरियल स्पॉट", "te": "క్యాప్సికం బాక్టీరియా మచ్చ తెగులు", "ta": "குடைமிளகாய் பாக்டீரியா புள்ளி நோய்", "kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ", "ml": "ക്യാപ്സിക്കം ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "ढोबळी मिरची जिवाणू ठिपके रोग", "bn": "ক্যাপসিকাম ব্যাকটেরিয়াল পাতার দাগ রোগ", "es": "Mancha bacteriana del pimiento"},
        "translit": "Bell Pepper Bacterial Spot",
        "alt_names": {"en": ["Xanthomonas Leaf Spot"], "hi": ["जीवाणु पत्ती धब्बा"], "te": ["బాక్టీరియా ఆకుమచ్చ"], "ta": ["பாக்டீரியா புள்ளி"], "kn": ["ಬ್ಯಾಕ್ಟೀರಿಯಾ ಕಲೆ"], "ml": ["ബാക്ടീരിയൽ പുള്ളി"], "mr": ["जिवाणू करपा"], "bn": ["ব্যাকটেরিয়াল দাগ"], "es": ["Bacteriosis del pimiento"]}
    },
    "Pepper,_bell___healthy": {
        "names": {"en": "Healthy Bell Pepper Foliage", "hi": "स्वस्थ शिमला मिर्च के पत्ते", "te": "ఆరోగ్యకరమైన క్యాప్సికం ఆకులు", "ta": "ஆரோக்கியமான குடைமிளகாய் இலை", "kn": "ಆರೋಗ್ಯಕರ ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള ക്യാപ്സിക്കം ഇലകൾ", "mr": "निरोगी ढोबळी मिरची पाने", "bn": "সুস্থ ও নিরোগ ক্যাপসিকাম পাতা", "es": "Follaje de pimiento sano"},
        "tts": {"en": "Healthy Bell Pepper crop foliage", "hi": "शिमला मिर्च की फसल स्वस्थ है", "te": "క్యాప్సికం ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "குடைமிளகாய் இலை ஆரோக்கியமாக உள்ளது", "kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "ക്യാപ്സിക്കം ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "ढोबळी मिरची पीक निरोगी आहे", "bn": "ক্যাপসিকাম পাতা সম্পূর্ণ সুস্থ", "es": "Hojas de pimiento completamente sanas"},
        "translit": "Healthy Bell Pepper",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Potato___Early_blight": {
        "names": {"en": "Potato Early Blight", "hi": "आलू का अगेती झुलसा रोग (Early Blight)", "te": "బంగాళాదుంప ముందస్తు ఆకు ఎండు తెగులు (Early Blight)", "ta": "உருளைக்கிழங்கு முன் பருவ கருகல் நோய் (Early Blight)", "kn": "ಆಲೂಗಡ್ಡೆ ಮುಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ (Early Blight)", "ml": "ഉരുളക്കിഴങ്ങ് മുൻകാല ഇല കരിച്ചിൽ രോഗം (Early Blight)", "mr": "बटाटा अगेती करपा रोग (Early Blight)", "bn": "আলুর আগাম ধ্বসা বা আর্লি ব্লাইট রোগ", "es": "Tizón temprano de la patata (Alternariosis)"},
        "tts": {"en": "Potato Early Blight fungal infection", "hi": "आलू का अगेती झुलसा रोग यानी अर्ली ब्लाइट", "te": "బంగాళాదుంప ముందస్తు ఆకు ఎండు తెగులు", "ta": "உருளைக்கிழங்கு முன் பருவ கருகல் நோய்", "kn": "ಆಲೂಗಡ್ಡೆ ಮುಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "ഉരുളക്കിഴങ്ങ് ഏർലി ബ്ലൈറ്റ് രോഗം", "mr": "बटाटा अगेती करपा रोग", "bn": "আলুর আগাম ধ্বসা বা আর্লি ব্লাইট রোগ", "es": "Tizón temprano de la patata"},
        "translit": "Potato Early Blight",
        "alt_names": {"en": ["Alternaria Leaf Blight", "Target Spot"], "hi": ["अगेती झुलसा", "लक्ष्य चक्र धब्बा"], "te": ["ముందస్తు ఎండు తెగులు", "వలయాల మచ్చ"], "ta": ["முன் கருகல் நோய்"], "kn": ["ಮುಂಗಾರು ಕರಗು ರೋಗ"], "ml": ["ഏർലി ബ്ലൈറ്റ്"], "mr": ["अगेती करपा"], "bn": ["আগাম ধ্বসা"], "es": ["Alternariosis de la patata", "Negrón de la patata"]}
    },
    "Potato___Late_blight": {
        "names": {"en": "Potato Late Blight", "hi": "आलू का पछेती झुलसा रोग (Late Blight)", "te": "బంగాళాదుంప లేట్ బ్లైట్ (ఆలస్యపు ఆకు ఎండు తెగులు)", "ta": "உருளைக்கிழங்கு பின் பருவ கருகல் நோய் (Late Blight)", "kn": "ಆಲೂಗಡ್ಡೆ ಹಿಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ (Late Blight)", "ml": "ഉരുളക്കിഴങ്ങ് ലേറ്റ് ബ്ലൈറ്റ് രോഗം", "mr": "बटाटा पछेती करपा रोग (Late Blight)", "bn": "আলুর নাবী ধ্বসা বা লেইট ব্লাইট রোগ", "es": "Tizón tardío de la patata (Mildiú de la patata)"},
        "tts": {"en": "Potato Late Blight oomycete infection", "hi": "आलू का पछेती झुलसा रोग यानी लेट ब्लाइट", "te": "బంగాళాదుంప లేట్ బ్లైట్ తెగులు", "ta": "உருளைக்கிழங்கு பின் பருவ கருகல் நோய்", "kn": "ಆಲೂಗಡ್ಡೆ ಹಿಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "ഉരുളക്കിഴങ്ങ് ലേറ്റ് ബ്ലൈറ്റ് രോഗം", "mr": "बटाटा पछेती करपा रोग", "bn": "আলুর নাবী ধ্বসা বা লেইট ব্লাইট রোগ", "es": "Tizón tardío o mildiú de la patata"},
        "translit": "Potato Late Blight",
        "alt_names": {"en": ["Phytophthora Blight"], "hi": ["पछेती झुलसा"], "te": ["ఆలస్యపు ఎండు తెగులు"], "ta": ["பின் கருகல் நோய்"], "kn": ["ಹಿಂಗಾರು ಕರಗು"], "ml": ["ലേറ്റ് ബ്ലൈറ്റ്"], "mr": ["पछेती करपा"], "bn": ["নাবী ধ্বসা"], "es": ["Mildiú de la patata", "Tizón tardío"]}
    },
    "Potato___healthy": {
        "names": {"en": "Healthy Potato Foliage", "hi": "स्वस्थ आलू के पत्ते", "te": "ఆరోగ్యకరమైన బంగాళాదుంప ఆకులు", "ta": "ஆரோக்கியமான உருளைக்கிழங்கு இலை", "kn": "ಆರೋಗ್ಯಕರ ಆಲೂಗಡ್ಡೆ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള ഉരുളക്കിഴങ്ങ് ഇലകൾ", "mr": "निरोगी बटाटा पाने", "bn": "সুস্থ ও নিরোগ আলু পাতা", "es": "Follaje de patata sano"},
        "tts": {"en": "Healthy Potato crop foliage", "hi": "आलू की फसल स्वस्थ है", "te": "బంగాళాదుంప ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "உருளைக்கிழங்கு இலை ஆரோக்கியமாக உள்ளது", "kn": "ಆಲೂಗಡ್ಡೆ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "ഉരുളക്കിഴങ്ങ് ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "बटाटा पीक निरोगी आहे", "bn": "আলু পাতা সম্পূর্ণ সুস্থ ও রোগমুক্ত", "es": "Hojas de patata sanas"},
        "translit": "Healthy Potato",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Raspberry___healthy": {
        "names": {"en": "Healthy Raspberry Foliage", "hi": "स्वस्थ रास्पबेरी के पत्ते", "te": "ఆరోగ్యకరమైన రాస్ప్‌బెర్రీ ఆకులు", "ta": "ஆரோக்கியமான ராஸ்பெர்ரி இலை", "kn": "ಆರೋಗ್ಯಕರ ರಾಸ್ಪ್ಬೆರಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള റാസ്പ്ബെറി ഇലകൾ", "mr": "निरोगी रास्पबेरी पाने", "bn": "সুস্থ ও নিরোগ রাস্পবেরি পাতা", "es": "Follaje de frambuesa sano"},
        "tts": {"en": "Healthy Raspberry crop foliage", "hi": "रास्पबेरी की पत्तियां स्वस्थ हैं", "te": "రాస్ప్‌బెర్రీ ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "ராஸ்பெர்ரி இலை ஆரோக்கியமாக உள்ளது", "kn": "ರಾಸ್ಪ್ಬೆರಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "റാസ്പ്ബെറി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "रास्पबेरी पीक निरोगी आहे", "bn": "রাস্পবেরি পাতা সুস্থ ও রোগমুক্ত", "es": "Hojas de frambuesa sanas"},
        "translit": "Healthy Raspberry",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Soybean___healthy": {
        "names": {"en": "Healthy Soybean Foliage", "hi": "स्वस्थ सोयाबीन के पत्ते", "te": "ఆరోగ్యకరమైన సోయాచిక్కుడు ఆకులు", "ta": "ஆரோக்கியமான சோயாபீன் இலை", "kn": "ಆರೋಗ್ಯಕರ ಸೋಯಾಬೀನ್ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള സോയാബീൻ ഇലകൾ", "mr": "निरोगी सोयाबीन पाने", "bn": "সুস্থ ও নিরোগ সয়াবিন পাতা", "es": "Follaje de soja sano"},
        "tts": {"en": "Healthy Soybean crop foliage", "hi": "सोयाबीन की फसल पूरी तरह स्वस्थ है", "te": "సోయాచిక్కుడు పంట ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "சோயாபீன் பயிர் ஆரோக்கியமாக உள்ளது", "kn": "ಸೋಯಾಬೀನ್ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "സോയാബീൻ ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "सोयाबीन पीक निरोगी आहे", "bn": "সয়াবিন পাতা সম্পূর্ণ সুস্থ", "es": "Hojas de soja completamente sanas"},
        "translit": "Healthy Soybean",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Squash___Powdery_mildew": {
        "names": {"en": "Squash Powdery Mildew", "hi": "कद्दू का चूर्णिल आसिता रोग (Powdery Mildew)", "te": "గుమ్మడి / దోస బూడిద తెగులు (Powdery Mildew)", "ta": "பூசணி சாம்பல் நோய் (Powdery Mildew)", "kn": "ಕುಂಬಳಕಾಯಿ ಬೂದಿ ರೋಗ (Powdery Mildew)", "ml": "മത്തങ്ങ ചാരപ്പൂപ്പ് രോഗം (Powdery Mildew)", "mr": "भोपळा भुरी रोग (Powdery Mildew)", "bn": "মিষ্টি কুমড়ার পাউডারি মিলডিউ বা সাদা গুঁড়ো রোগ", "es": "Oídio de las cucurbitáceas (Calabacín)"},
        "tts": {"en": "Squash Powdery Mildew fungal infection", "hi": "कद्दू का चूर्णिल फफूंद यानी पाउडरी मिल्ड्यू रोग", "te": "గుమ్మడి బూడిద తెగులు", "ta": "பூசணி சாம்பல் நோய்", "kn": "ಕುಂಬಳಕಾಯಿ ಬೂದಿ ರೋಗ", "ml": "മത്തങ്ങ ചാരപ്പൂപ്പ് രോഗം", "mr": "भोपळा भुरी रोग", "bn": "মিষ্টি কুমড়ার পাউডারি মিলডিউ রোগ", "es": "Oídio o cenicilla del calabacín"},
        "translit": "Squash Powdery Mildew",
        "alt_names": {"en": ["Cucurbit Powdery Mildew"], "hi": ["सफेद चूर्ण रोग"], "te": ["తెల్ల బూడిద తెగులు"], "ta": ["சாம்பல் நோய்"], "kn": ["ಬೂದಿ ರೋಗ"], "ml": ["വെള്ളപ്പൂപ്പ് രോഗം"], "mr": ["भुरी रोग"], "bn": ["পাউডারি মিলডিউ"], "es": ["Cenicilla de las cucurbitáceas"]}
    },
    "Strawberry___Leaf_scorch": {
        "names": {"en": "Strawberry Leaf Scorch", "hi": "स्ट्रॉबेरी का पत्ती झुलसा रोग (Leaf Scorch)", "te": "స్ట్రాబెర్రీ ఆకు ఎండ తెగులు (Leaf Scorch)", "ta": "ஸ்ட்ராபெர்ரி இலை கருகல் நோய் (Leaf Scorch)", "kn": "ಸ್ಟ್ರಾಬೆರಿ ಎಲೆ ಸುಟ್ಟ ರೋಗ (Leaf Scorch)", "ml": "സ്ട്രോബെറി ഇല കരിച്ചിൽ രോഗം (Leaf Scorch)", "mr": "स्ट्रॉबेरी पान करपा रोग (Leaf Scorch)", "bn": "স্ট্রবেরি পাতা ঝলসানো রোগ (Leaf Scorch)", "es": "Quemadura de la hoja de la fresa"},
        "tts": {"en": "Strawberry Leaf Scorch fungal disease", "hi": "स्ट्रॉबेरी का पत्ती झुलसा रोग यानी लीफ स्कॉर्च", "te": "స్ట్రాబెర్రీ ఆకు ఎండ తెగులు", "ta": "ஸ்ட்ராபெர்ரி இலை கருகல் நோய்", "kn": "ಸ್ಟ್ರಾಬೆರಿ ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "സ്ട്രോബെറി ഇല കരിച്ചിൽ രോഗം", "mr": "स्ट्रॉबेरी पान करपा रोग", "bn": "স্ট্রবেরি পাতা ঝলসানো রোগ", "es": "Quemadura foliar de la fresa"},
        "translit": "Strawberry Leaf Scorch",
        "alt_names": {"en": ["Diplocarpon Spot"], "hi": ["पत्ती झुलसन"], "te": ["ఆకు ఎండ తెగులు"], "ta": ["இலை கருகல்"], "kn": ["ಎಲೆ ಸುಟ್ಟ ಮಚ್ಚೆ"], "ml": ["ഇല കരിച്ചിൽ"], "mr": ["पान करपा"], "bn": ["পাতা পোড়া রোগ"], "es": ["Mancha púrpura de la fresa"]}
    },
    "Strawberry___healthy": {
        "names": {"en": "Healthy Strawberry Foliage", "hi": "स्वस्थ स्ट्रॉबेरी के पत्ते", "te": "ఆరోగ్యకరమైన స్ట్రాబెర్రీ ఆకులు", "ta": "ஆரோக்கியமான ஸ்ட்ராபெர்ரி இலை", "kn": "ಆರೋಗ್ಯಕರ ಸ್ಟ್ರಾಬೆರಿ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള സ്ട്രോബെറി ഇലകൾ", "mr": "निरोगी स्ट्रॉबेरी पाने", "bn": "সুস্থ ও নিরোগ স্ট্রবেরি পাতা", "es": "Follaje de fresa sano"},
        "tts": {"en": "Healthy Strawberry crop foliage", "hi": "स्ट्रॉबेरी की फसल स्वस्थ है", "te": "స్ట్రాబెర్రీ ఆకులు ఆరోగ్యంగా ఉన్నాయి", "ta": "ஸ்ட்ராபெர்ரி இலை ஆரோக்கியமாக உள்ளது", "kn": "ಸ್ಟ್ರಾಬೆರಿ ಎಲೆಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "സ്ട്രോബെറി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "स्ट्रॉबेरी पीक निरोगी आहे", "bn": "স্ট্রবেরি পাতা সম্পূর্ণ সুস্থ", "es": "Hojas de fresa completamente sanas"},
        "translit": "Healthy Strawberry",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    },
    "Tomato___Bacterial_spot": {
        "names": {"en": "Tomato Bacterial Spot", "hi": "टमाटर का जीवाणु धब्बा रोग (Bacterial Spot)", "te": "టమోటా బాక్టీరియా మచ్చ తెగులు (Bacterial Spot)", "ta": "தக்காளி பாக்டீரியா இலைப்புள்ளி நோய் (Bacterial Spot)", "kn": "ಟೊಮೇಟೊ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ (Bacterial Spot)", "ml": "തക്കാളി ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "टोमॅटो जिवाणूजन्य ठिपके रोग (Bacterial Spot)", "bn": "টমেটো ব্যাকটেরিয়াল পাতার দাগ রোগ (Bacterial Spot)", "es": "Mancha bacteriana del tomate"},
        "tts": {"en": "Tomato Bacterial Spot disease", "hi": "टमाटर का जीवाणु धब्बा रोग यानी बैक्टीरियल स्पॉट", "te": "టమోటా బాక్టీరియా మచ్చ తెగులు", "ta": "தக்காளி பாக்டீரியா புள்ளி நோய்", "kn": "ಟೊಮೇಟೊ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಮಚ್ಚೆ ರೋಗ", "ml": "തക്കാളി ബാക്ടീരിയൽ ഇലപ്പുള്ളി രോഗം", "mr": "टोमॅटो जिवाणू ठिपके रोग", "bn": "টমেটো ব্যাকটেরিয়াল দাগ রোগ", "es": "Mancha bacteriana del tomate"},
        "translit": "Tomato Bacterial Spot",
        "alt_names": {"en": ["Xanthomonas Spot"], "hi": ["जीवाणु पत्ती धब्बा"], "te": ["బాక్టీరియా ఆకుమచ్చ"], "ta": ["பாக்டீரியா புள்ளி"], "kn": ["ಬ್ಯಾಕ್ಟೀರಿಯಾ ಕಲೆ"], "ml": ["ബാക്ടീരിയൽ പുള്ളി"], "mr": ["जिवाणू करपा"], "bn": ["ব্যাকটেরিয়াল পাতার দাগ"], "es": ["Bacteriosis del tomate"]}
    },
    "Tomato___Early_blight": {
        "names": {"en": "Tomato Early Blight", "hi": "टमाटर का अगेती झुलसा रोग (Early Blight)", "te": "టమోటా ముందస్తు ఆకు ఎండు తెగులు (Early Blight)", "ta": "தக்காளி முன் பருவ கருகல் நோய் (Early Blight)", "kn": "ಟೊಮೇಟೊ ಮುಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ (Early Blight)", "ml": "തക്കാളി മുൻകാല ഇല കരിച്ചിൽ രോഗം (Early Blight)", "mr": "टोमॅटो अगेती करपा रोग (Early Blight)", "bn": "টমেটোর আগাম ধ্বসা বা আর্লি ব্লাইট রোগ", "es": "Tizón temprano del tomate (Alternariosis)"},
        "tts": {"en": "Tomato Early Blight fungal disease", "hi": "टमाटर का अगेती झुलसा रोग यानी अर्ली ब्लाइट", "te": "టమోటా ముందస్తు ఆకు ఎండు తెగులు", "ta": "தக்காளி முன் பருவ கருகல் நோய்", "kn": "ಟೊಮೇಟೊ ಮುಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "തക്കാളി ഏർലി ബ്ലൈറ്റ് രോഗം", "mr": "टोमॅटो अगेती करपा रोग", "bn": "টমেটোর আগাম ধ্বসা রোগ", "es": "Tizón temprano del tomate"},
        "translit": "Tomato Early Blight",
        "alt_names": {"en": ["Target Spot of Tomato"], "hi": ["अगेती झुलसा"], "te": ["ముందస్తు ఎండు తెగులు"], "ta": ["முன் கருகல்"], "kn": ["ಮುಂಗಾರು ಸುಟ್ಟ ರೋಗ"], "ml": ["ഏർലി ബ്ലൈറ്റ്"], "mr": ["अगेती करपा"], "bn": ["আগাম ধ্বসা"], "es": ["Alternariosis del tomate"]}
    },
    "Tomato___Late_blight": {
        "names": {"en": "Tomato Late Blight", "hi": "टमाटर का पछेती झुलसा रोग (Late Blight)", "te": "టమోటా లేట్ బ్లైట్ (ఆలస్యపు ఆకు ఎండు తెగులు)", "ta": "தக்காளி பின் பருவ கருகல் நோய் (Late Blight)", "kn": "ಟೊಮೇಟೊ ಹಿಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ (Late Blight)", "ml": "തക്കാളി ലേറ്റ് ബ്ലൈറ്റ് രോഗം", "mr": "टोमॅटो पछेती करपा रोग (Late Blight)", "bn": "টমেটোর নাবী ধ্বসা বা লেইট ব্লাইট রোগ", "es": "Tizón tardío del tomate (Mildiú)"},
        "tts": {"en": "Tomato Late Blight oomycete infection", "hi": "टमाटर का पछेती झुलसा रोग यानी लेट ब्लाइट", "te": "టమోటా లేట్ బ్లైట్ తెగులు", "ta": "தக்காளி பின் பருவ கருகல் நோய்", "kn": "ಟೊಮೇಟೊ ಹಿಂಗಾರು ಎಲೆ ಸುಟ್ಟ ರೋಗ", "ml": "തക്കാളി ലേറ്റ് ബ്ലൈറ്റ് രോഗം", "mr": "टोमॅटो पछेती करपा रोग", "bn": "টমেটোর নাবী ধ্বসা বা লেইট ব্লাইট রোগ", "es": "Tizón tardío o mildiú del tomate"},
        "translit": "Tomato Late Blight",
        "alt_names": {"en": ["Phytophthora Infestans"], "hi": ["पछेती झुलसा"], "te": ["ఆలస్యపు ఎండు తెగులు"], "ta": ["பின் கருகல் நோய்"], "kn": ["ಹಿಂಗಾರು ಕರಗು"], "ml": ["ലേറ്റ് ബ്ലൈറ്റ്"], "mr": ["पछेती करपा"], "bn": ["নাবী ধ্বসা"], "es": ["Mildiú del tomate"]}
    },
    "Tomato___Leaf_Mold": {
        "names": {"en": "Tomato Leaf Mold", "hi": "टमाटर का लीफ मोल्ड (पत्ती फफूंद रोग)", "te": "టమోటా బూజు ఆకుమచ్చ తెగులు (Leaf Mold)", "ta": "தக்காளி இலை பூஞ்சை பூஞ்சணம் (Leaf Mold)", "kn": "ಟೊಮೇಟೊ ಎಲೆ ಬೂజు ರೋಗ (Leaf Mold)", "ml": "തക്കാളി ഇലപ്പൂപ്പ് രോഗം (Leaf Mold)", "mr": "टोमॅटो पान बुरशी रोग (Leaf Mold)", "bn": "টমেটো পাতার ছত্রাক বা লিফ মোল্ড রোগ", "es": "Moho de la hoja del tomate (Cladosporiosis)"},
        "tts": {"en": "Tomato Leaf Mold fungal infection", "hi": "टमाटर का लीफ मोल्ड यानी पत्ती फफूंद रोग", "te": "టమోటా బూజు ఆకుమచ్చ తెగులు", "ta": "தக்காளி இலை பூஞ்சை நோய்", "kn": "ಟೊಮೇಟೊ ಎಲೆ ಬೂಜು ರೋಗ", "ml": "തക്കാളി ഇലപ്പൂപ്പ് രോഗം", "mr": "टोमॅटो पान बुरशी रोग", "bn": "টমেটো লিফ মোল্ড রোগ", "es": "Moho foliar del tomate"},
        "translit": "Tomato Leaf Mold",
        "alt_names": {"en": ["Cladosporium Leaf Mold"], "hi": ["पत्ती फफूंद"], "te": ["బూజు మచ్చ"], "ta": ["இலை பூஞ்சணம்"], "kn": ["ಬೂಜು ರೋಗ"], "ml": ["ഇലപ്പൂപ്പ്"], "mr": ["पान बुरशी"], "bn": ["পাতার মোল্ড"], "es": ["Cladosporiosis"]}
    },
    "Tomato___Septoria_leaf_spot": {
        "names": {"en": "Tomato Septoria Leaf Spot", "hi": "टमाटर का सेप्टोरिया पत्ता धब्बा रोग", "te": "టమోటా సెప్టోరియా ఆకుమచ్చ తెగులు (Septoria Spot)", "ta": "தக்காளி செப்டோரியா இலைப்புள்ளி நோய்", "kn": "ಟೊಮೇಟೊ ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಮಚ್ಚೆ ರೋಗ", "ml": "തക്കാളി സെപ്റ്റോറിയ ഇലപ്പുള്ളി രോഗം", "mr": "टोमॅटो सेप्टोरिया ठिपके रोग (Septoria Leaf Spot)", "bn": "টমেটো সেপপ্টোরিয়া পাতার দাগ রোগ", "es": "Mancha foliar por Septoria del tomate"},
        "tts": {"en": "Tomato Septoria Leaf Spot fungal disease", "hi": "टमाटर का सेप्टोरिया पत्ता धब्बा रोग", "te": "టమోటా సెప్టోరియా ఆకుమచ్చ తెగులు", "ta": "தக்காளி செப்டோரியா புள்ளி நோய்", "kn": "ಟೊಮೇಟೊ ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಮಚ್ಚೆ ರೋಗ", "ml": "തക്കാളി സെപ്റ്റോറിയ ഇലപ്പുള്ളി രോഗം", "mr": "टोमॅटो सेप्टोरिया ठिपके रोग", "bn": "টমেটো সেপপ্টোরিয়া দাগ রোগ", "es": "Septoriosis del tomate"},
        "translit": "Tomato Septoria Leaf Spot",
        "alt_names": {"en": ["Septoria Spot"], "hi": ["सेप्टोरिया धब्बा"], "te": ["సెప్టోరియా మచ్చ"], "ta": ["செப்டோரியா புள்ளி"], "kn": ["ಸೆಪ್ಟೋರಿಯಾ ಮಚ್ಚೆ"], "ml": ["സെപ്റ്റോറിയ പുള്ളി"], "mr": ["सेप्टोरिया करपा"], "bn": ["সেপপ্টোরিয়া দাগ"], "es": ["Septoriosis"]}
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "names": {"en": "Tomato Two-Spotted Spider Mite", "hi": "टमाटर का लाल मकड़ी / दो-धब्बेदार मकड़ी कीट", "te": "టమోటా రెండు చుక్కల ఎర్ర నల్లి / ఎర్ర సాలీడు కీటకం", "ta": "தக்காளி இரண்டு புள்ளி செம்பேன் / சிலந்திப் பேன்", "kn": "ಟೊಮೇಟೊ ಕೆಂಪು ಜಿಗ್ಗಿ / ಜೇಡ ನುಸಿ ಕೀಟ", "ml": "തക്കാളി ചുവന്ന മണ്ഡരി / ചിലന്തി മണ്ഡരി ബാധ", "mr": "टोमॅटो लाल कोळी / दोन ठिपक्यांचा कोळी कीड", "bn": "টমেটোর লাল মাকড় বা দুই-দাগযুক্ত লাল মাইট", "es": "Araña roja de dos puntos del tomate"},
        "tts": {"en": "Tomato Two-Spotted Spider Mite infestation", "hi": "टमाटर का लाल मकड़ी और दो धब्बेदार मकड़ी कीट", "te": "టమోటా ఎర్ర నల్లి లేదా సాలీడు కీటకం", "ta": "தக்காளி செம்பேன் சிலந்திப் பேன் தாக்குதல்", "kn": "ಟೊಮೇಟೊ ಕೆಂಪು ಜೇಡ ನುಸಿ ಕೀಟ", "ml": "തക്കാളി ചുവന്ന ചിലന്തി മണ്ഡരി ബാധ", "mr": "टोमॅटो लाल कोळी कीड प्रादुर्भाव", "bn": "টমেটোর লাল মাকড় পোকা", "es": "Plaga de araña roja en tomate"},
        "translit": "Tomato Spider Mite",
        "alt_names": {"en": ["Red Spider Mite"], "hi": ["लाल मकड़ी"], "te": ["ఎర్ర నల్లి"], "ta": ["செம்பேன்"], "kn": ["ಕೆಂಪು ನುಸಿ"], "ml": ["ചുവന്ന മണ്ഡരി"], "mr": ["लाल कोळी"], "bn": ["লাল মাকড়"], "es": ["Ácaro de dos puntos"]}
    },
    "Tomato___Target_Spot": {
        "names": {"en": "Tomato Target Spot", "hi": "टमाटर का लक्ष्य चक्र धब्बा रोग (Target Spot)", "te": "టమోటా టార్గెట్ స్పాట్ (లక్ష్య చక్ర ఆకుమచ్చ తెగులు)", "ta": "தக்காளி இலக்கு புள்ளி நோய் (Target Spot)", "kn": "ಟೊಮೇಟೊ ಗುರಿ ಮಚ್ಚೆ ರೋಗ (Target Spot)", "ml": "തക്കാളി ലക്ഷ്യ പുള്ളിക്കുത്ത് രോഗം (Target Spot)", "mr": "टोमॅटो टार्गेट स्पॉट किंवा गोल कडी ठिपके रोग", "bn": "টমেটো টার্গেট স্পট বা বৃত্তাকার দাগ রোগ", "es": "Mancha concéntrica del tomate (Target spot)"},
        "tts": {"en": "Tomato Target Spot fungal infection", "hi": "टमाटर का टार्गेट स्पॉट यानी चक्राकार धब्बा रोग", "te": "టమోటా టార్గెట్ స్పాట్ ఆకుమచ్చ తెగులు", "ta": "தக்காளி டார்கெட் ஸ்பாட் நோய்", "kn": "ಟೊಮೇಟೊ ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್ ರೋಗ", "ml": "തക്കാളി ടാർഗറ്റ് സ്പോട്ട് രോഗം", "mr": "टोमॅटो टार्गेट स्पॉट रोग", "bn": "টমেটো টার্গেট স্পট রোগ", "es": "Mancha concéntrica del tomate"},
        "translit": "Tomato Target Spot",
        "alt_names": {"en": ["Corynespora Spot"], "hi": ["चक्राकार धब्बा"], "te": ["వలయాల మచ్చ"], "ta": ["வளைய புள்ளி"], "kn": ["ಗುರಿ ಕಲೆ"], "ml": ["വളയപ്പുള്ളി"], "mr": ["कडी ठिपका"], "bn": ["টার্গেট স্পট"], "es": ["Corynespora del tomate"]}
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "names": {"en": "Tomato Yellow Leaf Curl Virus (TYLCV)", "hi": "टमाटर का पीला पत्ती मरोड़ विषाणु (TYLCV / चुर्रा-मुर्रा)", "te": "టమోటా ఆకు ముడత / పసుపు రంగు వైరస్ తెగులు (TYLCV)", "ta": "தக்காளி இலை சுருள் மஞ்சள் வைரஸ் நோய் (TYLCV)", "kn": "ಟೊಮೇಟೊ ಎಲೆ ಸುರುಳಿ ಹಳದಿ ವೈರಸ್ ರೋಗ (TYLCV)", "ml": "തക്കാളി ഇലച്ചുരുൾ മഞ്ഞളിപ്പ് വൈറസ് രോഗം (TYLCV)", "mr": "टोमॅटो पर्णगुच्छ / पिवळा पानांचा मुरडा रोग (TYLCV)", "bn": "টমেটো পাতা কোঁকড়ানো হলুদ ভাইরাস রোগ (TYLCV)", "es": "Virus del rizado amarillo del tomate (TYLCV / Virus de la cuchara)"},
        "tts": {"en": "Tomato Yellow Leaf Curl Virus infection transmitted by whiteflies", "hi": "सफेद मक्खी द्वारा फैलने वाला टमाटर का पीला पत्ती मरोड़ विषाणु रोग", "te": "తెల్లదోమ ద్వారా వ్యాపించే టమోటా ఆకు ముడత వైరస్ తెగులు", "ta": "வெள்ளை ஈக்களால் பரவும் தக்காளி இலை சுருள் மஞ்சள் வைரஸ் நோய்", "kn": "ಬಿಳಿ ನೊಣದಿಂದ ಹರಡುವ ಟೊಮೇಟೊ ಎಲೆ ಸುರುಳಿ ವೈರಸ್ ರೋಗ", "ml": "വെള്ളീച്ച വഴി പകരുന്ന തക്കാളി ഇലച്ചുരുൾ വൈറസ് രോഗം", "mr": "पांढऱ्या माशीमुळे पसरणारा टोमॅटो पानांचा मुरडा रोग", "bn": "সাদা মাছি বাহিত টমেটোর পাতা কোঁকড়ানো হলুদ ভাইরাস রোগ", "es": "Virus del rizado amarillo del tomate transmitido por mosca blanca"},
        "translit": "Tomato Yellow Leaf Curl Virus",
        "alt_names": {"en": ["Leaf Curl Virus", "TYLCV"], "hi": ["चुर्रा-मुर्रा रोग", "पत्ती मरोड़"], "te": ["ఆకు ముడత", "జెమిని వైరస్"], "ta": ["இலை சுருள் நோய்"], "kn": ["ಎಲೆ ಮುರುಟು ರೋಗ"], "ml": ["ഇലച്ചുരുൾ രോഗം"], "mr": ["चुरडा-मुरडा रोग"], "bn": ["পাতা কোঁকড়ানো রোগ"], "es": ["Virus de la cuchara"]}
    },
    "Tomato___Tomato_mosaic_virus": {
        "names": {"en": "Tomato Mosaic Virus (ToMV)", "hi": "टमाटर का मोजेक विषाणु रोग (Tomato Mosaic Virus)", "te": "టమోటా మొజాయిక్ వైరస్ తెగులు (చిత్రవర్ణ తెగులు)", "ta": "தக்காளி மொசைக் வைரஸ் நோய் (வண்ண வரி நோய்)", "kn": "ಟೊಮೇಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್ ರೋಗ (ಚಿತ್ರವಿಚಿತ್ರ ಕಲೆ ರೋಗ)", "ml": "തക്കാളി മൊസൈക് വൈറസ് രോഗം (ToMV)", "mr": "टोमॅटो मोझॅक विषाणू रोग (Tomato Mosaic Virus)", "bn": "টমেটো মোজাইক ভাইরাস রোগ (ToMV)", "es": "Virus del mosaico del tomate (ToMV)"},
        "tts": {"en": "Tomato Mosaic Virus infection", "hi": "टमाटर का मोजेक विषाणु रोग यानी टोमैटो मोज़ेक वायरस", "te": "టమోటా మొజాయిక్ వైరస్ తెగులు", "ta": "தக்காளி மொசைக் வைரஸ் நோய்", "kn": "ಟೊಮೇಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್ ರೋಗ", "ml": "തക്കാളി മൊസൈക് വൈറസ് രോഗം", "mr": "टोमॅटो मोझॅक विषाणू रोग", "bn": "টমেটো মোজাইক ভাইরাস রোগ", "es": "Virus del mosaico del tomate"},
        "translit": "Tomato Mosaic Virus",
        "alt_names": {"en": ["ToMV", "Mosaic Disease"], "hi": ["मोजेक रोग"], "te": ["చిత్రవర్ణ తెగులు"], "ta": ["மொசைக் நோய்"], "kn": ["ಮೊಸಾಯಿಕ್ ರೋಗ"], "ml": ["മൊസൈക് രോഗം"], "mr": ["मोझॅक करपा"], "bn": ["মোজাইক রোগ"], "es": ["Mosaico del tomate"]}
    },
    "Tomato___healthy": {
        "names": {"en": "Healthy Tomato Foliage", "hi": "स्वस्थ टमाटर के पत्ते", "te": "ఆరోగ్యకరమైన టమోటా ఆకులు", "ta": "ஆரோக்கியமான தக்காளி இலை", "kn": "ಆರೋಗ್ಯಕರ ಟೊಮೇಟೊ ಎಲೆಗಳು", "ml": "ആരോഗ്യമുള്ള തക്കാളി ഇലകൾ", "mr": "निरोगी टोमॅटो पाने", "bn": "সুস্থ ও নিরোগ টমেটো পাতা", "es": "Follaje de tomate sano"},
        "tts": {"en": "Healthy Tomato crop foliage", "hi": "टमाटर की फसल बिल्कुल स्वस्थ और सुरक्षित है", "te": "టమోటా పంట ఆకులు సంపూర్ణ ఆరోగ్యంగా ఉన్నాయి", "ta": "தக்காளி பயிர் இலை முழுமையாக ஆரோக்கியமாக உள்ளது", "kn": "ಟೊಮೇಟೊ ಬೆಳೆ ಎಲೆಗಳು ಸಂಪೂರ್ಣವಾಗಿ ಆರೋಗ್ಯಕರವಾಗಿವೆ", "ml": "തക്കാളി ഇലകൾ പൂർണ്ണ ആരോഗ്യത്തിലാണ്", "mr": "टोमॅटो पिकाची पाने पूर्णपणे निरोगी आहेत", "bn": "টমেটো গাছের পাতা সম্পূর্ণ সুস্থ ও রোগমুক্ত", "es": "Follaje de la planta de tomate completamente sano"},
        "translit": "Healthy Tomato",
        "alt_names": {"en": ["Normal Leaf"], "hi": ["निरोगी पत्ता"], "te": ["ఆరోగ్యకరమైన ఆకు"], "ta": ["ஆரோக்கிய இலை"], "kn": ["ಆರೋಗ್ಯಕರ ಎಲೆ"], "ml": ["രോഗമില്ലാത്ത ഇല"], "mr": ["स्वस्थ पान"], "bn": ["রোগমুক্ত পাতা"], "es": ["Hojas sanas"]}
    }
}

print(f"Total disease dictionary entries configured: {len(DISEASE_DICTS)}")
assert len(DISEASE_DICTS) == 38, f"Expected 38 diseases in dictionary, found {len(DISEASE_DICTS)}"
