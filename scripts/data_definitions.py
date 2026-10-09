"""Agronomic glossary and disease translation dictionaries for all 38 PlantVillage classes across 9 languages.
Languages: English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn), Malayalam (ml), Marathi (mr), Bengali (bn), Spanish (es).
"""

# Common Agronomic Terms Glossary
AGRONOMIC_TERMS = {
    "fungicide": {
        "english": "Fungicide",
        "hi": {"term": "फफूंदनाशक (फंगीसाइड)", "translit": "Fapoondnashak", "def": "फंगल रोगों को नियंत्रित करने वाली दवा", "tts": "फफूंदनाशक"},
        "te": {"term": "శిలీంధ్రనాశిని (ఫంగిసైడ్)", "translit": "Shilindhranashini", "def": "శిలీంధ్ర తెగుళ్లను నివారించే మందు", "tts": "శిలీంధ్రనాశిని"},
        "ta": {"term": "பூஞ்சாணக்கொல்லி (பங்கிசைடு)", "translit": "Poonjanakkolli", "def": "பூஞ்சை நோய்களைக் கட்டுப்படுத்தும் மருந்து", "tts": "பூஞ்சாணக்கொல்லி"},
        "kn": {"term": "ಶಿಲೀಂಧ್ರನಾಶಕ (ಫಂಗಿಸೈಡ್)", "translit": "Shilandhranashaka", "def": "ಶಿಲೀಂಧ್ರ ರೋಗಗಳನ್ನು ನಿಯಂತ್ರಿಸುವ ಔಷಧ", "tts": "ಶಿಲೀಂಧ್ರನಾಶಕ"},
        "ml": {"term": "കുമിൾനാശിനി (ഫംഗിസൈഡ്)", "translit": "Kumilnashini", "def": "കുമിൾ രോഗങ്ങളെ നിയന്ത്രിക്കുന്ന മരുന്ന്", "tts": "കുമിൾനാശിനി"},
        "mr": {"term": "बुरशीनाशक (फंगीसाइड)", "translit": "Burashinashak", "def": "बुरशीजन्य रोगांवर नियंत्रण ठेवणारे औषध", "tts": "बुरशीनाशक"},
        "bn": {"term": "ছত্রাকনাশক (ফাংগিসাইড)", "translit": "Chhatraknashak", "def": "ছত্রাকজনিত রোগ নিয়ন্ত্রণের ওষুধ", "tts": "ছত্রাকনাশক"},
        "es": {"term": "Fungicida", "translit": "Fungicida", "def": "Sustancia que destruye los hongos perjudiciales", "tts": "Fungicida"},
        "en": {"term": "Fungicide", "translit": "Fungicide", "def": "Pesticide that prevents or destroys fungal pathogens", "tts": "Fungicide"}
    },
    "bactericide": {
        "english": "Bactericide",
        "hi": {"term": "जीवाणुनाशक (बैक्टीरीसाइड)", "translit": "Jeevanunashak", "def": "जीवाणु संक्रमण रोकने वाली दवा", "tts": "जीवाणुनाशक"},
        "te": {"term": "బాక్టీరియా నాశిని", "translit": "Bacteria Nashini", "def": "బాక్టీరియా తెగుళ్లను నివారించే మందు", "tts": "బాక్టీరియా నాశిని"},
        "ta": {"term": "பாக்டீரியாக்கொல்லி", "translit": "Bacteria-kkolli", "def": "பாக்டீரியா நோய்களைக் கட்டுப்படுத்தும் மருந்து", "tts": "பாக்டீரியாக்கொல்லி"},
        "kn": {"term": "ಬ್ಯಾಕ್ಟೀರಿಯಾನಾಶಕ", "translit": "Bacterianashaka", "def": "ಬ್ಯಾಕ್ಟೀರಿಯಾ ರೋಗ ನಿಯಂತ್ರಕ", "tts": "ಬ್ಯಾಕ್ಟೀರಿಯಾನಾಶಕ"},
        "ml": {"term": "ബാക്ടീരിയനാശിനി", "translit": "Bacterianashini", "def": "ബാക്ടീരിയ ബാധ തടയുന്ന മരുന്ന്", "tts": "ബാക്ടീരിയനാശിനി"},
        "mr": {"term": "जिवाणूनाशक", "translit": "Jivanunashak", "def": "जिवाणू रोगांवर नियंत्रण ठेवणारे औषध", "tts": "जिवाणूनाशक"},
        "bn": {"term": "জীবাণুনাশক / ব্যাকটেরিসাইড", "translit": "Jibanunashak", "def": "ব্যাকটেরিয়াজনিত রোগ নিয়ন্ত্রক", "tts": "জীবাণুনাশক"},
        "es": {"term": "Bactericida", "translit": "Bactericida", "def": "Agente que destruye las bacterias", "tts": "Bactericida"},
        "en": {"term": "Bactericide", "translit": "Bactericide", "def": "Substance that destroys or suppresses bacteria", "tts": "Bactericide"}
    },
    "crop_rotation": {
        "english": "Crop Rotation",
        "hi": {"term": "फसल चक्र (क्रॉप रोटेशन)", "translit": "Fasal Chakra", "def": "एक ही खेत में फसलों को बदल-बदल कर बोना", "tts": "फसल चक्र"},
        "te": {"term": "పంట మార్పిడి", "translit": "Panta Marpidi", "def": "ఒకే నేలలో వేర్వేరు రకాల పంటలను వరుసగా సాగు చేయడం", "tts": "పంట మార్పిడి"},
        "ta": {"term": "பயிர் சுழற்சி", "translit": "Payir Suzharchi", "def": "ஒரே நிலத்தில் வெவ்வேறு பயிர்களை மாற்றி பயிரிடுதல்", "tts": "பயிர் சுழற்சி"},
        "kn": {"term": "ಬೆಳೆ ಪರಿವರ್ತನೆ (ಬೆಳೆ ಸರದಿ)", "translit": "Bele Parivartane", "def": "ಒಂದೇ ಜಮೀನಿನಲ್ಲಿ ವಿವಿಧ ಬೆಳೆಗಳನ್ನು ಅನುಕ್ರಮವಾಗಿ ಬೆಳೆಯುವುದು", "tts": "ಬೆಳೆ ಪರಿವರ್ತನೆ"},
        "ml": {"term": "വിള പരിക്രമം", "translit": "Vila Parikramam", "def": "ഒരു നിലത്ത് മാറി മാറി കൃഷി ചെയ്യൽ", "tts": "വിള പരിക്രമം"},
        "mr": {"term": "पिकांची फेरपालट", "translit": "Pikanchi Pherpalat", "def": "एकाच जमिनीत आलटून-पालटून पिके घेणे", "tts": "पिकांची फेरपालट"},
        "bn": {"term": "ফসল আবর্তন", "translit": "Phasol Abartan", "def": "একই জমিতে পর্যায়ক্রমে বিভিন্ন ফসল চাষ", "tts": "ফসল আবর্তন"},
        "es": {"term": "Rotación de cultivos", "translit": "Rotacion de cultivos", "def": "Alternancia sistemática de diferentes cultivos en una misma parcela", "tts": "Rotación de cultivos"},
        "en": {"term": "Crop Rotation", "translit": "Crop Rotation", "def": "Successive planting of different crops on the same land to improve soil and reduce disease", "tts": "Crop Rotation"}
    },
    "resistant_variety": {
        "english": "Resistant Variety",
        "hi": {"term": "रोग प्रतिरोधी किस्म", "translit": "Rog Pratirodhi Kism", "def": "ऐसी किस्म जो रोग के संक्रमण को सहन कर सके", "tts": "रोग प्रतिरोधी किस्म"},
        "te": {"term": "తెగులు తట్టుకునే రకం", "translit": "Tegulu Tattukune Rakam", "def": "తెగుళ్లను తట్టుకుని దిగుబడినిచ్చే వంగడం", "tts": "తెగులు తట్టుకునే రకం"},
        "ta": {"term": "நோய் எதிர்ப்புத் திறன் கொண்ட ரகம்", "translit": "Noi Ethirppu Rakam", "def": "நோயை எதிர்த்து வளரும் பயிர் வகை", "tts": "நோய் எதிர்ப்பு ரகம்"},
        "kn": {"term": "ರೋಗ ನಿರೋಧಕ ತಳಿ", "translit": "Roga Nirodhaka Tali", "def": "ರೋಗಗಳನ್ನು ತಡೆಯುವ ಸಾಮರ್ಥ್ಯವುಳ್ಳ ಬೆಳೆ ತಳಿ", "tts": "ರೋಗ ನಿರೋಧಕ ತಳಿ"},
        "ml": {"term": "രോഗപ്രതിരോധ ശേഷിയുള്ള ഇനം", "translit": "Roga Prathirodha Inam", "def": "രോഗബാധയെ ചെറുത്തുനിൽക്കാൻ കഴിയുന്ന വിത്തിനം", "tts": "രോഗപ്രതിരോധ ശേഷിയുള്ള ഇനം"},
        "mr": {"term": "रोग प्रतिकारक वाण", "translit": "Rog Pratikarak Vaan", "def": "रोगांना बळी न पडणारा पिकाचा वाण", "tts": "रोग प्रतिकारक वाण"},
        "bn": {"term": "রোগ প্রতিরোধী জাত", "translit": "Rog Pratirodhi Jaat", "def": "যে জাত রোগ সংক্রমণ প্রতিরোধ করতে সক্ষম", "tts": "রোগ প্রতিরোধী জাত"},
        "es": {"term": "Variedad resistente", "translit": "Variedad resistente", "def": "Variedad vegetal capaz de resistir el ataque de patógenos", "tts": "Variedad resistente"},
        "en": {"term": "Resistant Variety", "translit": "Resistant Variety", "def": "Crop cultivar bred or selected for natural disease resistance", "tts": "Resistant Variety"}
    },
    "spray_interval": {
        "english": "Spray Interval",
        "hi": {"term": "छिड़काव अंतराल", "translit": "Chhidkaav Antaraal", "def": "दो छिड़कावों के बीच के दिनों की संख्या", "tts": "छिड़काव अंतराल"},
        "te": {"term": "పిచికారీ విరామం", "translit": "Pichikari Viramam", "def": "రెండు పిచికారీల మధ్య ఉండాల్సిన వ్యవధి", "tts": "పిచికారీ విరామం"},
        "ta": {"term": "தெளிப்பு இடைவெளி", "translit": "Thelippu Idaiveli", "def": "இரண்டு மருந்து தெளிப்புகளுக்கு இடைப்பட்ட நாட்கள்", "tts": "தெளிப்பு இடைவெளி"},
        "kn": {"term": "ಸಿಂಪರಣಾ ಅಂತರ", "translit": "Simparana Antara", "def": "ಎರಡು ಸಿಂಪರಣೆಗಳ ನಡುವಿನ ದಿನಗಳ ಅಂತರ", "tts": "ಸಿಂಪರಣಾ ಅಂತರ"},
        "ml": {"term": "തളിക്കൽ ഇടവേള", "translit": "Thalikkal Idavela", "def": "മരുന്ന് തളിക്കുന്നതിനിടയിലെ ദിവസങ്ങളുടെ വ്യത്യാസം", "tts": "തളിക്കൽ ഇടവേള"},
        "mr": {"term": "फवारणी अंतर", "translit": "Phawarani Antar", "def": "दोन फवारण्यांमधील दिवसांचा कालावधी", "tts": "फवारणी अंतर"},
        "bn": {"term": "স্প্রে করার ব্যবধান", "translit": "Spray Korar Byabodhan", "def": "দুটি স্প্রে করার মধ্যবর্তী দিনের সময়", "tts": "স্প্রে করার ব্যবধান"},
        "es": {"term": "Intervalo de pulverización", "translit": "Intervalo de pulverizacion", "def": "Número de días entre aplicaciones sucesivas de tratamiento", "tts": "Intervalo de pulverización"},
        "en": {"term": "Spray Interval", "translit": "Spray Interval", "def": "Required duration in days between successive chemical or biological applications", "tts": "Spray Interval"}
    }
}
