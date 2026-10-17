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
  { code: 'en', label: 'English (India)', nativeLabel: en.language.names.en, voiceLang: 'en-IN' },
  { code: 'hi', label: 'Hindi', nativeLabel: en.language.names.hi, voiceLang: 'hi-IN' },
  { code: 'ta', label: 'Tamil', nativeLabel: en.language.names.ta, voiceLang: 'ta-IN' },
  { code: 'te', label: 'Telugu', nativeLabel: en.language.names.te, voiceLang: 'te-IN' },
  { code: 'kn', label: 'Kannada', nativeLabel: en.language.names.kn, voiceLang: 'kn-IN' },
];

export const initialLanguageChosen = SUPPORTED_LANGUAGES.some(l => l.code === localStorage.getItem('agrishield_language'));

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
      order: ['localStorage'],
      lookupLocalStorage: 'agrishield_language',
      caches: [],
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;

export function tr(key: string, values?: Record<string, unknown>): string {
  return String(i18n.t(key, values || {}));
}
i18n.on('languageChanged', lang => {
  document.documentElement.lang = lang.split('-')[0];
  document.title = tr('app_title');
});
document.documentElement.lang = i18n.language || 'en';
