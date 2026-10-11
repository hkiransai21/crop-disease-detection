import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Volume2,
  VolumeX,
  Play,
  Pause,
  Square,
  RotateCcw,
  Languages,
  Radio,
  Sparkles,
  PhoneCall,
  Loader2,
  WifiOff,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { AnalysisResponse } from '../types';
import { SUPPORTED_LANGUAGES } from '../i18n/i18n';
import { api } from '../api/client';

interface AudioNarratorProps {
  analysis: AnalysisResponse;
}

type AudioSection = 'overview' | 'treatment' | 'prevention';

export const AudioNarrator: React.FC<AudioNarratorProps> = ({ analysis }) => {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language ? i18n.language.split('-')[0].split('_')[0] : 'en';

  const [selectedLang, setSelectedLang] = useState<string>(currentLang);
  const [activeSection, setActiveSection] = useState<AudioSection>('overview');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [speechRate, setSpeechRate] = useState<number>(1.0);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [usingFallback, setUsingFallback] = useState<boolean>(false);
  const [offlineCached, setOfflineCached] = useState<boolean>(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Sync selectedLang with global i18n language
  useEffect(() => {
    setSelectedLang(currentLang);
    handleStop();
  }, [currentLang]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      handleStop();
    };
  }, []);

  const selectedLangObj = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang) || SUPPORTED_LANGUAGES[0];
  const diseaseId = analysis.predicted_label;
  const isHealthy = analysis.disease_details?.is_healthy || analysis.predicted_label.toLowerCase().includes('healthy');

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlaying(false);
    setIsPaused(false);
    setIsLoading(false);
    setCurrentTime(0);
  };

  const handlePlaySection = async (section: AudioSection, langCode: string = selectedLang) => {
    if (isPlaying && activeSection === section && isPaused) {
      if (audioRef.current) {
        audioRef.current.play();
        setIsPaused(false);
        setIsPlaying(true);
        return;
      }
    }

    handleStop();
    setActiveSection(section);
    setIsLoading(true);
    setUsingFallback(false);

    const audioUrl = api.getAudioUrl(diseaseId, section, langCode, speechRate);

    try {
      const audio = new Audio(audioUrl);
      audio.playbackRate = speechRate;

      audio.oncanplay = () => {
        setIsLoading(false);
      };

      audio.onplay = () => {
        setIsPlaying(true);
        setIsPaused(false);
      };

      audio.onpause = () => {
        setIsPaused(true);
      };

      audio.onended = () => {
        setIsPlaying(false);
        setIsPaused(false);
        setCurrentTime(0);
      };

      audio.ontimeupdate = () => {
        setCurrentTime(audio.currentTime);
        setDuration(audio.duration || 0);
      };

      audio.onerror = () => {
        console.warn('Backend neural audio stream unavailable. Falling back to browser speech synthesis.');
        playWithWebSpeech(section, langCode);
      };

      audioRef.current = audio;
      await audio.play();
    } catch (err) {
      console.warn('Error starting server audio:', err);
      playWithWebSpeech(section, langCode);
    }
  };

  const playWithWebSpeech = (section: AudioSection, langCode: string) => {
    setIsLoading(false);
    if (!('speechSynthesis' in window)) {
      setUsingFallback(true);
      return;
    }

    setUsingFallback(true);
    window.speechSynthesis.cancel();

    let textToSpeak = '';
    const details = analysis.disease_details;

    if (section === 'overview') {
      textToSpeak = `${analysis.crop}: ${analysis.disease_name}. ${details?.symptoms || ''}`;
    } else if (section === 'treatment') {
      const org = details?.organic_controls?.[0] || '';
      const chem = details?.chemical_controls?.[0] || '';
      textToSpeak = isHealthy
        ? 'No chemical spray is required. Maintain standard irrigation.'
        : `Organic: ${org}. Chemical: ${chem}. Always wear a protective mask.`;
    } else {
      const prev = details?.prevention_steps?.[0] || '';
      textToSpeak = `Prevention: ${prev}. For government help, call Kisan Call Center 1800 180 1551.`;
    }

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = speechRate;
    utterance.lang = selectedLangObj.voiceLang;

    const voices = window.speechSynthesis.getVoices();
    const matchingVoice = voices.find(
      (v) => v.lang === selectedLangObj.voiceLang || v.lang.startsWith(selectedLangObj.code)
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

  const handleTogglePlayPause = () => {
    if (!isPlaying && !isPaused) {
      handlePlaySection(activeSection, selectedLang);
      return;
    }

    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.pause();
      }
      setIsPaused(true);
      setIsPlaying(false);
    } else if (isPaused) {
      if (audioRef.current) {
        audioRef.current.play();
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
      }
      setIsPaused(false);
      setIsPlaying(true);
    }
  };

  const handleRateChange = () => {
    const nextRate = speechRate === 1.0 ? 0.75 : speechRate === 0.75 ? 1.25 : 1.0;
    setSpeechRate(nextRate);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextRate;
    }
  };

  return (
    <div className="bg-gradient-to-br from-brand-950 via-slate-900 to-emerald-950 rounded-3xl p-5 sm:p-6 text-white shadow-xl border border-brand-800/50 space-y-4">
      {/* Header with Title and Language Picker */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-400/20 border border-amber-400/30 flex items-center justify-center text-amber-300 shadow-inner">
            <Volume2 className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base sm:text-lg font-bold">{t('audio.title')}</h3>
              <span className="px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 text-[10px] font-extrabold uppercase tracking-wide">
                {t('audio.badge')}
              </span>
            </div>
            <p className="text-xs text-brand-200">
              {t('audio.subtitle')}
            </p>
          </div>
        </div>

        {/* Language Picker */}
        <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1.5 rounded-2xl border border-white/15 self-start sm:self-auto">
          <Languages className="w-4 h-4 text-brand-300 shrink-0" />
          <select
            value={selectedLang}
            onChange={(e) => {
              const newLang = e.target.value;
              setSelectedLang(newLang);
              i18n.changeLanguage(newLang);
              localStorage.setItem('agrishield_language', newLang);
              handleStop();
            }}
            className="bg-transparent text-xs font-bold text-white focus:outline-none cursor-pointer pr-1"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code} className="text-slate-900 bg-white font-medium">
                {lang.nativeLabel} ({lang.label})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Section Tabs for Audio Narration */}
      <div className="grid grid-cols-3 gap-2 bg-white/5 p-1.5 rounded-2xl border border-white/10">
        <button
          onClick={() => {
            setActiveSection('overview');
            handlePlaySection('overview');
          }}
          className={`py-2 px-2 text-center rounded-xl text-xs font-bold transition-all ${
            activeSection === 'overview'
              ? 'bg-amber-400 text-slate-950 shadow-md'
              : 'text-slate-300 hover:bg-white/10'
          }`}
        >
          {t('audio.section_overview')}
        </button>

        <button
          onClick={() => {
            setActiveSection('treatment');
            handlePlaySection('treatment');
          }}
          className={`py-2 px-2 text-center rounded-xl text-xs font-bold transition-all ${
            activeSection === 'treatment'
              ? 'bg-amber-400 text-slate-950 shadow-md'
              : 'text-slate-300 hover:bg-white/10'
          }`}
        >
          {t('audio.section_treatment')}
        </button>

        <button
          onClick={() => {
            setActiveSection('prevention');
            handlePlaySection('prevention');
          }}
          className={`py-2 px-2 text-center rounded-xl text-xs font-bold transition-all ${
            activeSection === 'prevention'
              ? 'bg-amber-400 text-slate-950 shadow-md'
              : 'text-slate-300 hover:bg-white/10'
          }`}
        >
          {t('audio.section_prevention')}
        </button>
      </div>

      {/* Controls & Wave Visualizer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div className="flex items-center space-x-3">
          {isLoading ? (
            <button
              disabled
              className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-amber-400/50 text-slate-950 text-xs font-black"
            >
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading Audio...</span>
            </button>
          ) : !isPlaying ? (
            <button
              onClick={() => handlePlaySection(activeSection)}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-black shadow-md shadow-amber-400/20 transition-all active:scale-95"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isPaused ? t('audio.resume') : t('audio.listen_btn', { lang: selectedLangObj.nativeLabel })}</span>
            </button>
          ) : (
            <button
              onClick={handleTogglePlayPause}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-amber-400/90 hover:bg-amber-300 text-slate-950 text-xs font-black shadow-md transition-all active:scale-95"
            >
              <Pause className="w-4 h-4 fill-current" />
              <span>{t('audio.pause')}</span>
            </button>
          )}

          {(isPlaying || isPaused) && (
            <button
              onClick={handleStop}
              className="flex items-center space-x-1.5 px-3 py-2.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/10 transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>{t('audio.stop')}</span>
            </button>
          )}

          {/* Speed Toggle */}
          <button
            onClick={handleRateChange}
            className="flex items-center space-x-1 bg-white/10 hover:bg-white/15 px-3 py-2 rounded-xl border border-white/10 text-xs font-bold transition-colors"
            title="Toggle Narration Speed"
          >
            <span className="text-brand-300">{t('audio.speed')}:</span>
            <span className="text-amber-300">{speechRate}x</span>
          </button>
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
            {isPlaying ? t('audio.playing') : isPaused ? t('audio.paused') : t('audio.ready')}
          </span>
        </div>
      </div>

      {/* Fallback Notice if WebSpeech is used */}
      {usingFallback && (
        <div className="flex items-center space-x-2 text-[11px] text-amber-200 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-xl">
          <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>{t('audio.fallback_notice')}</span>
        </div>
      )}

      {/* Kisan Helpline Shortcut Banner */}
      <div className="flex items-center justify-between text-xs bg-white/10 rounded-2xl px-4 py-2.5 border border-white/10">
        <div className="flex items-center space-x-2">
          <PhoneCall className="w-3.5 h-3.5 text-amber-300" />
          <span className="text-slate-200">{t('audio.helpline_text')}</span>
          <span className="font-mono font-bold text-amber-300">1800-180-1551</span>
        </div>
        <a
          href="tel:18001801551"
          className="px-2.5 py-1 rounded-lg bg-amber-400 text-slate-950 font-extrabold text-[11px] hover:bg-amber-300 transition-colors"
        >
          {t('audio.call_btn')}
        </a>
      </div>
    </div>
  );
};
