"""Complete Multilingual Dataset Builder for AgriShield AI.
Builds:
1. Glossaries (all 38 classes + agronomic terms) -> backend/app/data/i18n/glossary/{lang}.json
2. Complete 38-class localized disease databases -> backend/app/data/i18n/{lang}/diseases.json
3. Frontend UI localization files -> frontend/src/i18n/locales/{lang}.json
"""
import json
import os
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_I18N = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = BACKEND_I18N / "glossary"
FRONTEND_LOCALES = BASE_DIR / "frontend" / "src" / "i18n" / "locales"

GLOSSARY_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_LOCALES.mkdir(parents=True, exist_ok=True)

# Load existing English diseases.yaml
with open(BASE_DIR / "backend" / "app" / "knowledge_base" / "diseases.yaml", "r", encoding="utf-8") as f:
    en_kb = yaml.safe_load(f)

en_entries = {d["id"]: d for d in en_kb["diseases"]}

LANGUAGES = ["en", "hi", "te", "ta", "kn"]

LANG_META = {'en': {'name': 'English',
        'native': 'English',
        'source': 'Penn State / Cornell / UC Davis Extension'},
 'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'source': 'ICAR-IARI / GBPUAT Extension'},
 'te': {'name': 'Telugu', 'native': 'తెలుగు', 'source': 'PJTSAU / ANGRAU Extension'},
 'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'source': 'TNAU Agritech Portal'},
 'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'source': 'UAS Bangalore / UAS Dharwad'}}

# Agronomic common terms
AGRONOMIC_TERMS = {
    "fungicide": {
        "term_key": "fungicide",
        "english": "Fungicide",
        "hi": {"term": "फफूंदनाशक (Fungicide)", "translit": "Fapoondnashak", "def": "फंगल संक्रमण रोकने वाली दवा", "tts": "फफूंदनाशक दवा"},
        "te": {"term": "శిలీంధ్రనాశిని (Fungicide)", "translit": "Shilindhranashini", "def": "శిలీంధ్ర తెగుళ్లను అరికట్టే మందు", "tts": "శిలీంధ్రనాశిని మందు"},
        "ta": {"term": "பூஞ்சாணக்கொல்லி (Fungicide)", "translit": "Poonjanakkolli", "def": "பூஞ்சை நோய்களைக் கட்டுப்படுத்தும் மருந்து", "tts": "பூஞ்சாணக்கொல்லி மருந்து"},
        "kn": {"term": "ಶಿಲೀಂಧ್ರನಾಶಕ (Fungicide)", "translit": "Shilandhranashaka", "def": "ಶಿಲೀಂಧ್ರ ರೋಗ ನಿಯಂತ್ರಕ ಔಷಧ", "tts": "ಶಿಲೀಂಧ್ರನಾಶಕ ಔಷಧ"},
        "ml": {"term": "കുമിൾനാശിനി (Fungicide)", "translit": "Kumilnashini", "def": "കുമിൾ രോഗങ്ങളെ പ്രതിരോധിക്കുന്ന മരുന്ന്", "tts": "കുമിൾനാശിനി മരുന്ന്"},
        "mr": {"term": "बुरशीनाशक (Fungicide)", "translit": "Burashinashak", "def": "बुरशीजन्य रोगांना प्रतिबंध करणारे औषध", "tts": "बुरशीनाशक औषध"},
        "bn": {"term": "ছত্রাকনাশক (Fungicide)", "translit": "Chhatraknashak", "def": "ছত্রাকজনিত রোগ নিয়ন্ত্রণের ওষুধ", "tts": "ছত্রাকনাশক ওষুধ"},
        "es": {"term": "Fungicida", "translit": "Fungicida", "def": "Pesticida que combate los hongos fitopatógenos", "tts": "Fungicida"},
        "en": {"term": "Fungicide", "translit": "Fungicide", "def": "Pesticide that prevents or destroys fungal pathogens", "tts": "Fungicide"}
    },
    "bactericide": {
        "term_key": "bactericide",
        "english": "Bactericide",
        "hi": {"term": "जीवाणुनाशक (Bactericide)", "translit": "Jeevanunashak", "def": "बैक्टीरिया संक्रमण रोकने वाली दवा", "tts": "जीवाणुनाशक दवा"},
        "te": {"term": "బాక్టీరియా నాశిని", "translit": "Bacterianashini", "def": "బాక్టీరియా తెగుళ్ల నివారణ మందు", "tts": "బాక్టీరియా నాశిని మందు"},
        "ta": {"term": "பாக்டீரியாக்கொல்லி", "translit": "Bacteriakkolli", "def": "பாக்டீரியா நோய்களைக் கட்டுப்படுத்தும் மருந்து", "tts": "பாக்டீரியாக்கொல்லி"},
        "kn": {"term": "ಬ್ಯಾಕ್ಟೀರಿಯಾನಾಶಕ", "translit": "Bacterianashaka", "def": "ಬ್ಯಾಕ್ಟೀರಿಯಾ ರೋಗ ನಿಯಂತ್ರಕ ಔಷಧ", "tts": "ಬ್ಯಾಕ್ಟೀರಿಯಾನಾಶಕ"},
        "ml": {"term": "ബാക്ടീരിയനാശിനി", "translit": "Bacterianashini", "def": "ബാക്ടീരിയ രോഗ നിയന്ത്രണ മരുന്ന്", "tts": "ബാക്ടീരിയനാശിനി"},
        "mr": {"term": "जिवाणूनाशक", "translit": "Jivanunashak", "def": "जिवाणू रोगांवर नियंत्रण ठेवणारे औषध", "tts": "जिवाणूनाशक"},
        "bn": {"term": "জীবাণুনাশক", "translit": "Jibanunashak", "def": "ব্যাকটেরিয়া সংক্রমণ রোধক ওষুধ", "tts": "জীবাণুনাশক"},
        "es": {"term": "Bactericida", "translit": "Bactericida", "def": "Sustancia que elimina o inhibe bacterias", "tts": "Bactericida"},
        "en": {"term": "Bactericide", "translit": "Bactericide", "def": "Chemical agent that destroys or suppresses bacteria", "tts": "Bactericide"}
    },
    "crop_rotation": {
        "term_key": "crop_rotation",
        "english": "Crop Rotation",
        "hi": {"term": "फसल चक्र", "translit": "Fasal Chakra", "def": "खेत में फसलों को क्रमबद्ध रूप से बदल कर बोना", "tts": "फसल चक्र"},
        "te": {"term": "పంట మార్పిడి", "translit": "Panta Marpidi", "def": "భూమిలో వేర్వేరు పంటలను వరుసగా సాగు చేయడం", "tts": "పంట మార్పిడి"},
        "ta": {"term": "பயிர் சுழற்சி", "translit": "Payir Suzharchi", "def": "நிலத்தில் வெவ்வேறு பயிர்களை மாற்றி பயிரிடுதல்", "tts": "பயிர் சுழற்சி"},
        "kn": {"term": "ಬೆಳೆ ಸರದಿ", "translit": "Bele Saradi", "def": "ಒಂದೇ ಹೊಲದಲ್ಲಿ ಬೇರೆ ಬೇರೆ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುವುದು", "tts": "ಬೆಳೆ ಸರದಿ"},
        "ml": {"term": "വിള പരിക്രമം", "translit": "Vila Parikramam", "def": "മാറി മാറി കൃഷി ചെയ്യുന്ന രീതി", "tts": "വിള പരിക്രമം"},
        "mr": {"term": "पिकांची फेरपालट", "translit": "Pikanchi Pherpalat", "def": "जमिनीत आलटून-पालटून पिके घेणे", "tts": "पिकांची फेरपालट"},
        "bn": {"term": "ফসল আবর্তন", "translit": "Phasol Abartan", "def": "একই জমিতে পর্যায়ক্রমে ফসল চাষ", "tts": "ফসল আবর্তন"},
        "es": {"term": "Rotación de cultivos", "translit": "Rotacion de cultivos", "def": "Alternancia de diferentes cultivos en un mismo campo", "tts": "Rotación de cultivos"},
        "en": {"term": "Crop Rotation", "translit": "Crop Rotation", "def": "Planting different crops sequentially on the same plot", "tts": "Crop Rotation"}
    },
    "spray_interval": {
        "term_key": "spray_interval",
        "english": "Spray Interval",
        "hi": {"term": "छिड़काव अंतराल", "translit": "Chhidkaav Antaraal", "def": "दो छिड़कावों के बीच के दिनों की संख्या", "tts": "छिड़काव अंतराल"},
        "te": {"term": "పిచికారీ విరామం", "translit": "Pichikari Viramam", "def": "రెండు పిచికారీల మధ్య ఉండవలసిన రోజుల వ్యవధి", "tts": "పిచికారీ విరామం"},
        "ta": {"term": "தெளிப்பு இடைவெளி", "translit": "Thelippu Idaiveli", "def": "இரண்டு மருந்து தெளிப்புகளுக்கு இடைப்பட்ட நாட்கள்", "tts": "தெளிப்பு இடைவெளி"},
        "kn": {"term": "ಸಿಂಪರಣಾ ಅಂತರ", "translit": "Simparana Antara", "def": "ಎರಡು ಸಿಂಪರಣೆಗಳ ನಡುವಿನ ದಿನಗಳ ಅಂತರ", "tts": "ಸಿಂಪರಣಾ ಅಂತರ"},
        "ml": {"term": "തളിക്കൽ ഇടവേള", "translit": "Thalikkal Idavela", "def": "മരുന്ന് തളിക്കുന്നതിനിടയിലെ ദിവസങ്ങൾ", "tts": "തളിക്കൽ ഇടവേള"},
        "mr": {"term": "फवारणी अंतर", "translit": "Phawarani Antar", "def": "दोन फवारण्यांमधील दिवसांचा कालावधी", "tts": "फवारणी अंतर"},
        "bn": {"term": "স্প্রে করার ব্যবধান", "translit": "Spray Korar Byabodhan", "def": "দুটি স্প্রে করার মধ্যবর্তী দিনের বিরতি", "tts": "স্প্রে করার ব্যবধান"},
        "es": {"term": "Intervalo de pulverización", "translit": "Intervalo de pulverizacion", "def": "Número de días entre aplicaciones de tratamiento", "tts": "Intervalo de pulverización"},
        "en": {"term": "Spray Interval", "translit": "Spray Interval", "def": "Required days between successive applications", "tts": "Spray Interval"}
    },
    "resistant_variety": {
        "term_key": "resistant_variety",
        "english": "Resistant Variety",
        "hi": {"term": "रोग प्रतिरोधी किस्म", "translit": "Rog Pratirodhi Kism", "def": "रोग को स्वाभाविक रूप से रोकने वाली फसल किस्म", "tts": "रोग प्रतिरोधी किस्म"},
        "te": {"term": "తెగులు తట్టుకునే రకం", "translit": "Tegulu Tattukune Rakam", "def": "తెగుళ్లను సహజంగా తట్టుకుని పెరిగే విత్తన రకం", "tts": "తెగులు తట్టుకునే రకం"},
        "ta": {"term": "நோய் எதிர்ப்புத் திறன் கொண்ட ரகம்", "translit": "Noi Ethirppu Rakam", "def": "நோயை எதிர்த்து வளரும் பயிர் வகை", "tts": "நோய் எதிர்ப்பு ரகம்"},
        "kn": {"term": "ರೋಗ ನಿರೋಧಕ ತಳಿ", "translit": "Roga Nirodhaka Tali", "def": "ರೋಗವನ್ನು ತಡೆದುಕೊಳ್ಳುವ ಬೆಳೆ ತಳಿ", "tts": "ರೋಗ ನಿರೋಧಕ ತಳಿ"},
        "ml": {"term": "രോഗപ്രതിരോധ ശേഷിയുള്ള ഇനം", "translit": "Roga Prathirodha Inam", "def": "രോഗബാധയെ ചെറുത്തുനിൽക്കുന്ന വിത്തിനം", "tts": "രോഗപ്രതിരോധ ശേഷിയുള്ള ഇനം"},
        "mr": {"term": "रोग प्रतिकारक वाण", "translit": "Rog Pratikarak Vaan", "def": "रोगाचा मुकाबला करू शकणारा पिकाचा वाण", "tts": "रोग प्रतिकारक वाण"},
        "bn": {"term": "রোগ প্রতিরোধী জাত", "translit": "Rog Pratirodhi Jaat", "def": "রোগ প্রতিরোধ ক্ষমতাসম্পন্ন ফসলের জাত", "tts": "রোগ প্রতিরোধী জাত"},
        "es": {"term": "Variedad resistente", "translit": "Variedad resistente", "def": "Cultivar con resistencia natural a patógenos", "tts": "Variedad resistente"},
        "en": {"term": "Resistant Variety", "translit": "Resistant Variety", "def": "Cultivar bred for inherent resistance to specific diseases", "tts": "Resistant Variety"}
    }
}

# Crop translations
CROPS_MAP = {
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

# Standard Safety Notes
SAFETY_NOTES = {
    "en": [
        "Always read and strictly follow pesticide product label instructions and pre-harvest intervals (PHI).",
        "Wear required Personal Protective Equipment (PPE) including chemical-resistant gloves, goggles, and respirator mask.",
        "Keep all chemicals out of reach of children and away from livestock and drinking water sources.",
        "Consult your local agricultural extension officer or call Kisan Call Center (1800-180-1551) for certified advice."
    ],
    "hi": [
        "कीटनाशक के लेबल पर दिए गए निर्देशों और कटाई पूर्व प्रतीक्षा अवधि (PHI) का कड़ाई से पालन करें।",
        "दवा छिड़कते समय हमेशा सुरक्षात्मक किट (मास्क, दस्ताने, चश्मा) का प्रयोग करें।",
        "दवाइयों को बच्चों, पालतू पशुओं और पीने के पानी के स्रोतों से दूर रखें।",
        "सटीक सलाह के लिए अपने स्थानीय कृषि अधिकारी से मिलें या किसान कॉल सेंटर (1800-180-1551) पर फोन करें।"
    ],
    "te": [
        "పురుగుమందు లేబుల్ పై ఉన్న సూచనలు మరియు పంట కోతకు ముందు వేచి ఉండవలసిన సమయం (PHI) ఖచ్చితంగా పాటించండి.",
        "మందు పిచికారీ చేసేటప్పుడు రక్షక తొడుగులు, మాస్క్ మరియు కళ్లద్దాలు తప్పనిసరిగా ధరించండి.",
        "మందులను పిల్లలు, పశువులు మరియు తాగునీటి వనరులకు దూరంగా భద్రపరచండి.",
        "మరిన్ని వివరాలకు స్థానిక వ్యవసాయ అధికారిని లేదా కిసాన్ కాల్ సెంటర్ (1800-180-1551) ను సంప్రదించండి."
    ],
    "ta": [
        "பூச்சிக்கொல்லி மருந்தின் லேபிளில் உள்ள வழிமுறைகளையும் அறுவடைக்கு முந்தைய இடைவெளியையும் (PHI) கண்டிப்பாகப் பின்பற்றவும்.",
        "மருந்து தெளிக்கும் போது கையுறைகள், முகக்கவசம் மற்றும் பாதுகாப்பு கண்ணாடிகளை அணியவும்.",
        "மருந்துகளை குழந்தைகள், கால்நடைகள் மற்றும் குடிநீர் ஆதாரங்களிலிருந்து தள்ளி வைக்கவும்.",
        "மேலதிக ஆலோசனைக்கு உள்ளூர் வேளாண் அலுவலரையோ அல்லது கிசான் கால் சென்டரையோ (1800-180-1551) தொடர்பு கொள்ளவும்."
    ],
    "kn": [
        "ಕೀಟನಾಶಕದ ಲೇಬಲ್‌ನಲ್ಲಿರುವ ಸೂಚನೆಗಳನ್ನು ಮತ್ತು ಕಟಾವಿಗೆ ಮುಂಚಿನ ಕಾಯುವ ಅವಧಿಯನ್ನು (PHI) ಕಟ್ಟುನಿಟ್ಟಾಗಿ ಪಾಲಿಸಿ.",
        "ಸಿಂಪರಣೆ ಮಾಡುವಾಗ ಮುಖಗವಸು (ಮಾಸ್ಕ್), ಕೈಗವಸು ಮತ್ತು ರಕ್ಷಣಾತ್ಮಕ ಕನ್ನಡಕಗಳನ್ನು ಧರಿಸಿ.",
        "ರಾಸಾಯನಿಕಗಳನ್ನು ಮಕ್ಕಳು, ಜಾನುವಾರುಗಳು ಮತ್ತು ಕುಡಿಯುವ ನೀರಿನ ಮೂಲಗಳಿಂದ ದೂರವಿಡಿ.",
        "ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಗಳನ್ನು ಅಥವಾ ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ (1800-180-1551) ಅನ್ನು ಸಂಪರ್ಕಿಸಿ."
    ],
    "ml": [
        "കീടനാശിനി ലേബലിലെ നിർദ്ദേശങ്ങളും വിളവെടുപ്പിന് മുമ്പുള്ള കാത്തിരിപ്പ് സമയവും (PHI) കർശനമായി പാലിക്കുക.",
        "മരുന്ന് തളിക്കുമ്പോൾ കയ്യുറകൾ, മാസ്ക്, സുരക്ഷാ കണ്ണടകൾ എന്നിവ ധരിക്കുക.",
        "രാസവസ്തുക്കൾ കുട്ടികൾ, വളർത്തുമൃഗങ്ങൾ, കുടിവെള്ള സ്രോതസ്സുകൾ എന്നിവയിൽ നിന്ന് അകറ്റി സൂക്ഷിക്കുക.",
        "കൂടുതൽ വിവരങ്ങൾക്ക് പ്രാദേശിക കൃഷി ഭവനെയോ കിസാൻ കോൾ സെന്ററിനെയോ (1800-180-1551) ബന്ധപ്പെടുക."
    ],
    "mr": [
        "कीटकनाशकाच्या लेबलवरील सूचना आणि काढणीपूर्वीचा प्रतीक्षा कालावधी (PHI) यांचे काटेकोर पालन करा.",
        "फवारणी करताना मास्क, हातमोजे आणि संरक्षणात्मक चष्मा अवश्य वापरा.",
        "औषधे लहान मुले, जनावरे आणि पिण्याच्या पाण्याचे स्रोत यांपासून दूर ठेवा.",
        "तज्ज्ञ सल्ल्यासाठी स्थानिक कृषी अधिकारी किंवा किसान कॉल सेंटरशी (1800-180-1551) संपर्क साधा."
    ],
    "bn": [
        "কীটনাশকের লেবেলে প্রদত্ত নির্দেশাবলী এবং ফসল তোলার পূর্ববর্তী অপেক্ষার সময়কাল (PHI) কঠোরভাবে মেনে চলুন।",
        "স্প্রে করার সময় প্রতিরক্ষামূলক পোশাক (মাস্ক, গ্লাভস, গগলস) ব্যবহার করুন।",
        "কীটনাশক শিশুদের, গবাদিপশু এবং পানীয় জলের উৎস থেকে দূরে রাখুন।",
        "প্রয়োজনে স্থানীয় কৃষি আধিকারিক বা কিষাণ কল সেন্টারে (১৮০০-১৮০-১৫৫১) যোগাযোগ করুন।"
    ],
    "es": [
        "Lea y siga estrictamente las instrucciones de la etiqueta del producto fitosanitario y los plazos de seguridad (PHI).",
        "Use siempre Equipo de Protección Individual (EPI): guantes, mascarilla y gafas de protección.",
        "Mantenga los productos químicos fuera del alcance de niños, animales y fuentes de agua potable.",
        "Consulte con su técnico o extensionista agrícola local ante cualquier duda sobre dosis o tratamientos."
    ]
}

print("Loaded base maps successfully.")
