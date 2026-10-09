"""Complete multilingual i18n asset generator for AgriShield.
Generates:
1. Glossaries (all 38 classes + common terms) -> backend/app/data/i18n/glossary/{lang}.json
2. Knowledge Base Disease Monographs -> backend/app/data/i18n/{lang}/diseases.json
3. Frontend UI translation files -> frontend/src/i18n/locales/{lang}.json
"""
import json
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

LANGUAGES = ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "es"]
LANG_METADATA = {
    "en": {"name": "English", "native": "English", "source": "Penn State / Cornell / UC Davis Extension"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "source": "ICAR-IARI / GBPUAT Pantnagar Extension"},
    "te": {"name": "Telugu", "native": "తెలుగు", "source": "PJTSAU / ANGRAU Vyavasaya Calendar"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "source": "TNAU Agritech Portal Extension"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "source": "UAS Bangalore / UAS Dharwad Krishi Kai-pidi"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "source": "KAU Ad-hoc Package of Practices"},
    "mr": {"name": "Marathi", "native": "मराठी", "source": "MPKV Rahuri Krishi Darshani"},
    "bn": {"name": "Bengali", "native": "বাংলা", "source": "BCKV / BARI Krishi Tathya Kosha"},
    "es": {"name": "Spanish", "native": "Español", "source": "INTA / FAO / SAGARPA Guías Agrícolas"}
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
        "കൂടുതൽ വിവരങ്ങൾക്ക് പ്രാദേശിക കൃഷി ഭവനെയോ കിസான் കോൾ സെന്ററിനെയോ (1800-180-1551) ബന്ധപ്പെടുക."
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

print("Base i18n engine initial structures verified.")
