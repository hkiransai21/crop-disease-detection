import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import hi from './locales/hi.json';
import te from './locales/te.json';
import ta from './locales/ta.json';
import kn from './locales/kn.json';

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
    },
    fallbackLng: 'en',
    supportedLngs: ['en', 'hi', 'ta', 'te', 'kn'],
    load: 'languageOnly',
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
