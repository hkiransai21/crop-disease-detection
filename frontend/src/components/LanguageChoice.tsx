import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, initialLanguageChosen } from '../i18n/i18n';

export function LanguageChoice({ children }: { children: React.ReactNode }) {
  const { t, i18n } = useTranslation();
  const [chosen, setChosen] = useState(initialLanguageChosen);
  const select = (lang: string) => {
    localStorage.setItem('agrishield_language', lang);
    void i18n.changeLanguage(lang);
    setChosen(true);
  };
  if (!chosen) return <main className="min-h-screen bg-emerald-50 p-5 flex flex-col justify-center gap-4" aria-label={t('language.choose')}>
    <h1 className="text-2xl font-bold text-center">{t('language.choose')}</h1>
    {SUPPORTED_LANGUAGES.map(lang => <button key={lang.code} lang={lang.code} className="mx-auto w-full max-w-md rounded-2xl bg-white border-2 border-emerald-600 p-5 text-2xl font-bold" onClick={() => select(lang.code)}>{t(`language.names.${lang.code}`)}</button>)}
  </main>;
  return <>
    <nav aria-label={t('nav.select_language')} className="sticky top-0 z-[60] flex flex-wrap justify-center gap-1 bg-white border-b border-emerald-200 px-1 py-2">
      {SUPPORTED_LANGUAGES.map(lang => <button key={lang.code} lang={lang.code} aria-pressed={i18n.language === lang.code} onClick={() => select(lang.code)} className={`rounded-lg px-2 py-2 text-sm ${i18n.language === lang.code ? 'bg-emerald-700 text-white' : 'bg-emerald-50 text-emerald-950'}`}>{t(`language.names.${lang.code}`)}</button>)}
    </nav>
    {children}
  </>;
}
