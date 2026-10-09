import React, { useState, useEffect, useRef } from 'react';
import {
  Volume2,
  VolumeX,
  Play,
  Pause,
  Square,
  Languages,
  Radio,
  RotateCcw,
  Sparkles,
  PhoneCall
} from 'lucide-react';
import { AnalysisResponse } from '../types';

interface AudioNarratorProps {
  analysis: AnalysisResponse;
}

interface LanguageOption {
  code: string;
  label: string;
  nativeLabel: string;
  voiceLang: string;
}

const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', voiceLang: 'hi-IN' },
  { code: 'en', label: 'English (India)', nativeLabel: 'English', voiceLang: 'en-IN' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी', voiceLang: 'mr-IN' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు', voiceLang: 'te-IN' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்', voiceLang: 'ta-IN' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ', voiceLang: 'kn-IN' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা', voiceLang: 'bn-IN' },
  { code: 'gu', label: 'Gujarati', nativeLabel: 'ગુજરાતી', voiceLang: 'gu-IN' },
  { code: 'pa', label: 'Punjabi', nativeLabel: 'ਪੰਜਾਬੀ', voiceLang: 'pa-IN' },
  { code: 'es', label: 'Spanish', nativeLabel: 'Español', voiceLang: 'es-ES' },
];

export const AudioNarrator: React.FC<AudioNarratorProps> = ({ analysis }) => {
  const [selectedLang, setSelectedLang] = useState<string>('hi');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [speechRate, setSpeechRate] = useState<number>(0.9); // Slightly slower for clear rural comprehension
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const updateVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        setAvailableVoices(voices);
      };
      updateVoices();
      window.speechSynthesis.onvoiceschanged = updateVoices;
    } else {
      setIsSupported(false);
    }

    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const isHealthy = analysis.disease_details?.is_healthy || analysis.predicted_label.toLowerCase().includes('healthy');
  const crop = analysis.crop;
  const diseaseName = analysis.disease_name;
  const riskLevel = analysis.risk_assessment?.risk_level || 'MODERATE';
  const riskScore = analysis.risk_assessment?.risk_score || 50;
  const prevention = analysis.disease_details?.prevention_steps?.[0] || 'Remove visibly affected leaves and avoid overwatering.';
  const organic = analysis.disease_details?.organic_controls?.[0] || 'Spray organic Neem oil solution (5ml per liter).';
  const chemical = analysis.disease_details?.chemical_controls?.[0] || 'Consult local extension officer for recommended fungicide.';

  /**
   * Generates a spoken, friendly script in the selected language.
   */
  const generateSpokenScript = (langCode: string): string => {
    if (langCode === 'hi') {
      if (isHealthy) {
        return `नमस्ते किसान भाई! खुशखबरी! आपके ${crop} के पौधे का पत्ता बिल्कुल स्वस्थ और सुरक्षित है। कोई बीमारी के लक्षण नहीं मिले हैं। सामान्य सिंचाई और पोषण जारी रखें।`;
      }
      return `नमस्ते किसान भाई! ध्यान दें, आपके ${crop} के पौधे में ${diseaseName} की बीमारी पाई गई है। वर्तमान मौसम के आधार पर बीमारी फैलने का खतरा ${riskLevel === 'HIGH' || riskLevel === 'VERY HIGH' ? 'बहुत ज्यादा' : 'मध्यम'} है (जोखिम स्कोर ${riskScore} प्रतिशत)।

तुरंत यह कदम उठाएं:
पहला कदम: ${prevention}।
दूसरा जैविक उपाय: ${organic}।
तीसरा रासायनिक उपाय: ${chemical}। छिड़काव करते समय मास्क अवश्य पहनें।

किसी भी सहायता के लिए किसान कॉल सेंटर के टोल-फ्री नंबर 1800 180 1551 पर संपर्क करें।`;
    }

    if (langCode === 'mr') {
      if (isHealthy) {
        return `नमस्कार शेतकरी बंधूंनो! आपल्या ${crop} पिकाचे पान पूर्णपणे निरोगी आहे. कोणतीही कीड किंवा रोग आढळलेला नाही.`;
      }
      return `नमस्कार शेतकरी बंधूंनो! आपल्या ${crop} पिकावर ${diseaseName} या रोगाची लक्षणे आढळली आहेत. रोग प्रसाराचा धोका ${riskLevel} आहे.

तात्काळ उपाय:
१. ${prevention}।
२. सेंद्रिय उपाय: ${organic}।
३. रासायनिक फवारणी: ${chemical}।
अधिक माहितीसाठी किसान कॉल सेंटर १८०० १८० १५५१ वर संपर्क साधा.`;
    }

    if (langCode === 'te') {
      if (isHealthy) {
        return `నమస్కారం రైతు సోదరులారా! మీ ${crop} పంట ఆకు ఆరోగ్యంగా ఉంది. ఎటువంటి తెగులు లక్షణాలు కనిపించలేదు.`;
      }
      return `నమస్కారం రైతు సోదరులారా! మీ ${crop} పంటకు ${diseaseName} తెగులు సోకినట్లు గుర్తించబడింది. వాతావరణం వల్ల వ్యాప్తి ప్రమాదం ${riskLevel} గా ఉంది.

వెంటనే చేయవలసిన పనులు:
మొదటిది: ${prevention}.
సేంద్రీయ నివారణ: ${organic}.
రసాయన మందు: ${chemical}.
సహాయం కోసం కిసాన్ కాల్ సెంటర్ 1800 180 1551 కి కాల్ చేయండి.`;
    }

    if (langCode === 'ta') {
      if (isHealthy) {
        return `வணக்கம் விவசாய தோழரே! உங்கள் ${crop} பயிர் இலை ஆரோக்கியமாக உள்ளது. எந்த நோயும் தாக்கவில்லை.`;
      }
      return `வணக்கம் விவசாய தோழரே! உங்கள் ${crop} பயிரில் ${diseaseName} நோய் கண்டறியப்பட்டுள்ளது.

உடனடி நடவடிக்கைகள்:
1. ${prevention}.
2. இயற்கை முறை: ${organic}.
3. பரிந்துரைக்கப்பட்ட மருந்து: ${chemical}.
உதவிக்கு கிசான் கால் சென்டர் 1800 180 1551 ஐ அழைக்கவும்.`;
    }

    if (langCode === 'kn') {
      if (isHealthy) {
        return `ನಮಸ್ಕಾರ ರೈತ ಬಾಂಧವರೇ! ನಿಮ್ಮ ${crop} ಬೆಳೆ ಸಂಪೂರ್ಣವಾಗಿ ಆರೋಗ್ಯಕರವಾಗಿದೆ.`;
      }
      return `ನಮಸ್ಕಾರ ರೈತ ಬಾಂಧವರೇ! ನಿಮ್ಮ ${crop} ಬೆಳೆಗೆ ${diseaseName} ರೋಗ ತಗುಲಿರುವುದು ಕಂಡುಬಂದಿದೆ.

ತಕ್ಷಣದ ಕ್ರಮಗಳು:
೧. ${prevention}.
೨. ಸಾವಯವ ನಿಯಂತ್ರಣ: ${organic}.
೩. ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ: ${chemical}.
ಸಹಾಯಕ್ಕಾಗಿ ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ 1800 180 1551 ಗೆ ಕರೆ ಮಾಡಿ.`;
    }

    if (langCode === 'bn') {
      if (isHealthy) {
        return `নমস্কার কৃষক বন্ধু! আপনার ${crop} গাছের পাতা সম্পূর্ণ সুস্থ ও রোগমুক্ত।`;
      }
      return `নমস্কার কৃষক বন্ধু! আপনার ${crop} গাছে ${diseaseName} রোগ শনাক্ত হয়েছে। আবহাওয়ার কারণে ছড়ানোর ঝুঁকি ${riskLevel}।

জরুরি পদক্ষেপ:
১. ${prevention}।
২. জৈব নিয়ন্ত্রণ: ${organic}।
৩. রাসায়নিক স্প্রে: ${chemical}।
সাহায্যের জন্য কিষাণ কল সেন্টার ১৮০০ ১৮০ ১৫৫১ নম্বরে যোগাযোগ করুন।`;
    }

    if (langCode === 'gu') {
      if (isHealthy) {
        return `નમસ્તે ખેડૂત મિત્રો! તમારા ${crop} પાકનું પાંદડું તંદુરસ્ત છે અને કોઈ રોગ નથી.`;
      }
      return `નમસ્તે ખેડૂત મિત્રો! તમારા ${crop} પાકમાં ${diseaseName} રોગ જોવા મળ્યો છે.

તાત્કાલિક પગલાં:
૧. ${prevention}.
૨. જૈવિક ઉપાય: ${organic}.
૩. રાસાયણિક દવા: ${chemical}.
મદદ માટે કિસાન કૉલ સેન્ટર ૧૮૦૦ ૧૮૦ ૧૫૫૧ પર સંપર્ક કરો.`;
    }

    if (langCode === 'pa') {
      if (isHealthy) {
        return `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਵੀਰੋ! ਤੁਹਾਡੀ ${crop} ਦੀ ਫ਼ਸਲ ਬਿਲਕੁਲ ਤੰਦਰੁਸਤ ਹੈ। ਕੋਈ ਬਿਮਾਰੀ ਨਹੀਂ ਹੈ।`;
      }
      return `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਵੀਰੋ! ਤੁਹਾਡੀ ${crop} ਦੀ ਫ਼ਸਲ ਵਿੱਚ ${diseaseName} ਬਿਮਾਰੀ ਦੇਖੀ ਗਈ ਹੈ।

ਤੁਰੰਤ ਕਰਨ ਵਾਲੇ ਕੰਮ:
੧. ${prevention}।
੨. ਜੈਵਿਕ ਤਰੀਕਾ: ${organic}।
੩. ਰਸਾਇਣਕ ਸਪਰੇਅ: ${chemical}।
ਸਹਾਇਤਾ ਲਈ ਕਿਸਾਨ ਕਾਲ ਸੈਂਟਰ 1800 180 1551 'ਤੇ ਸੰਪਰਕ ਕਰੋ।`;
    }

    if (langCode === 'es') {
      if (isHealthy) {
        return `¡Hola agricultor! Buenas noticias: la hoja de su cultivo de ${crop} se encuentra completamente sana. No se detectaron síntomas de enfermedades.`;
      }
      return `¡Atención agricultor! Se ha detectado la enfermedad ${diseaseName} en su cultivo de ${crop}. El nivel de riesgo de propagación climática es ${riskLevel} con una puntuación de ${riskScore} sobre 100.

Acciones inmediatas recomendadas:
Primero: ${prevention}.
Tratamiento orgánico: ${organic}.
Tratamiento químico: ${chemical}. Use equipo de protección personal.`;
    }

    // Default English (India)
    if (isHealthy) {
      return `Hello Farmer! Good news: your ${crop} crop leaf is healthy and showing no disease symptoms. Continue your standard irrigation and nutrient schedule.`;
    }
    return `Hello Farmer! Alert: your ${crop} crop has been diagnosed with ${diseaseName}. Based on current weather conditions, the risk of disease spread is ${riskLevel}, with a risk score of ${riskScore} out of 100.

Immediate Recommended Actions:
First: ${prevention}.
Organic Control: ${organic}.
Chemical Control: ${chemical}. Always wear protective gloves and a mask when spraying.

For free government assistance, you can call the Kisan Call Center at toll-free number 1800 180 1551.`;
  };

  const handlePlay = () => {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-Speech is not supported in this browser.');
      return;
    }

    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    window.speechSynthesis.cancel(); // Stop any active speech

    const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang) || SUPPORTED_LANGUAGES[0];
    const scriptText = generateSpokenScript(selectedLang);

    const utterance = new SpeechSynthesisUtterance(scriptText);
    utterance.rate = speechRate;
    utterance.pitch = 1.0;
    utterance.lang = langObj.voiceLang;

    // Try to find matching regional voice if installed on device
    const matchingVoice = availableVoices.find(
      (v) => v.lang === langObj.voiceLang || v.lang.startsWith(langObj.code)
    );
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    utterance.onerror = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const handlePause = () => {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
    setIsPaused(false);
  };

  // Always render UI so farmer guidance and Kisan helpline are accessible across all devices

  const selectedLangObj = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang) || SUPPORTED_LANGUAGES[0];

  return (
    <div className="bg-gradient-to-br from-brand-900 via-emerald-900 to-teal-950 rounded-3xl p-5 sm:p-6 text-white shadow-lg border border-brand-700/50 space-y-4">
      {/* Header with Title and Language Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-400/20 border border-amber-400/30 flex items-center justify-center text-amber-300 shadow-inner">
            <Volume2 className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base sm:text-lg font-bold">Kisan Audio Assistant</h3>
              <span className="px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 text-[10px] font-extrabold uppercase tracking-wide">
                Voice Narration
              </span>
            </div>
            <p className="text-xs text-brand-200">
              Listen to complete diagnosis and treatment steps in your local language
            </p>
          </div>
        </div>

        {/* Language Picker */}
        <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1.5 rounded-2xl border border-white/15">
          <Languages className="w-4 h-4 text-brand-300 shrink-0" />
          <select
            value={selectedLang}
            onChange={(e) => {
              setSelectedLang(e.target.value);
              if (isPlaying) {
                window.speechSynthesis.cancel();
                setIsPlaying(false);
                setIsPaused(false);
              }
            }}
            className="bg-transparent text-xs font-bold text-white focus:outline-none cursor-pointer pr-2"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code} className="text-slate-900 bg-white font-medium">
                {lang.nativeLabel} ({lang.label})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Playback Controls & Equalizer Wave */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        {/* Play/Pause/Stop Buttons */}
        <div className="flex items-center space-x-3">
          {!isPlaying ? (
            <button
              onClick={handlePlay}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-black shadow-md shadow-amber-400/20 transition-all active:scale-95"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isPaused ? 'Resume Audio' : `Listen in ${selectedLangObj.nativeLabel}`}</span>
            </button>
          ) : (
            <button
              onClick={handlePause}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-amber-400/90 hover:bg-amber-300 text-slate-950 text-xs font-black shadow-md transition-all active:scale-95"
            >
              <Pause className="w-4 h-4 fill-current" />
              <span>Pause</span>
            </button>
          )}

          {(isPlaying || isPaused) && (
            <button
              onClick={handleStop}
              className="flex items-center space-x-1.5 px-3 py-2.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/10 transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Stop</span>
            </button>
          )}

          {/* Speed Toggle */}
          <div className="flex items-center space-x-1 bg-white/10 px-2.5 py-1.5 rounded-xl border border-white/10 text-[11px] font-bold">
            <span className="text-brand-300">Speed:</span>
            <button
              onClick={() => {
                const nextRate = speechRate === 0.9 ? 1.0 : speechRate === 1.0 ? 0.75 : 0.9;
                setSpeechRate(nextRate);
              }}
              className="text-amber-300 hover:underline px-1"
            >
              {speechRate}x
            </button>
          </div>
        </div>

        {/* Audio Wave Visualizer Animation */}
        <div className="flex items-center space-x-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/10">
          <Radio className={`w-4 h-4 ${isPlaying ? 'text-emerald-400 animate-pulse' : 'text-slate-400'}`} />
          <div className="flex items-center space-x-1 h-5">
            {[40, 70, 30, 90, 50, 80, 45, 60].map((h, i) => (
              <span
                key={i}
                style={{ height: isPlaying ? `${h}%` : '20%' }}
                className={`w-1 rounded-full transition-all duration-300 ${
                  isPlaying ? 'bg-amber-300 animate-pulse' : 'bg-white/20'
                }`}
              />
            ))}
          </div>
          <span className="text-[11px] font-semibold text-brand-200">
            {isPlaying ? 'Playing Audio...' : isPaused ? 'Audio Paused' : 'Ready to Play'}
          </span>
        </div>
      </div>

      {/* Kisan Helpline Shortcut Banner */}
      <div className="flex items-center justify-between text-xs bg-white/10 rounded-2xl px-4 py-2.5 border border-white/10">
        <div className="flex items-center space-x-2">
          <PhoneCall className="w-3.5 h-3.5 text-amber-300" />
          <span className="text-slate-200">Kisan Call Center (Toll-Free Govt. Helpline):</span>
          <span className="font-mono font-bold text-amber-300">1800-180-1551</span>
        </div>
        <a
          href="tel:18001801551"
          className="px-2.5 py-1 rounded-lg bg-amber-400 text-slate-950 font-extrabold text-[11px] hover:bg-amber-300 transition-colors"
        >
          Call
        </a>
      </div>
    </div>
  );
};
