import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import hi from './locales/hi.json';
import te from './locales/te.json';
import ta from './locales/ta.json';
import kn from './locales/kn.json';
import ml from './locales/ml.json';
import mr from './locales/mr.json';
import bn from './locales/bn.json';
import es from './locales/es.json';

export interface LanguageOption {
  code: string;
  label: string;
  nativeLabel: string;
  voiceLang: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', label: 'English (India)', nativeLabel: 'English', voiceLang: 'en-IN' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', voiceLang: 'hi-IN' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు', voiceLang: 'te-IN' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்', voiceLang: 'ta-IN' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ', voiceLang: 'kn-IN' },
  { code: 'ml', label: 'Malayalam', nativeLabel: 'മലയാളം', voiceLang: 'ml-IN' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी', voiceLang: 'mr-IN' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা', voiceLang: 'bn-IN' },
  { code: 'es', label: 'Spanish', nativeLabel: 'Español', voiceLang: 'es-ES' },
];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      te: { translation: te },
      ta: { translation: ta },
      kn: { translation: kn },
      ml: { translation: ml },
      mr: { translation: mr },
      bn: { translation: bn },
      es: { translation: es },
    },
    fallbackLng: 'en',
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'agrishield_language',
      caches: ['localStorage'],
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
