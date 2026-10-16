import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { AnalysisResponse } from '../types';
import { SUPPORTED_LANGUAGES } from '../i18n/i18n';
import { useAudio } from '../hooks/useAudio';

type Section = 'diagnosis' | 'symptoms' | 'treatment' | 'prevention';
type Catalog = { diseases: Record<string, Record<Section, string>> };

export const AudioNarrator: React.FC<{ analysis: AnalysisResponse }> = ({ analysis }) => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const requested = i18n.language.split('-')[0];
  const lang = SUPPORTED_LANGUAGES.some(l => l.code === requested) ? requested : 'en';
  const [section, setSection] = useState<Section>('diagnosis');
  const [catalog, setCatalog] = useState<{ lang: string; data: Catalog } | null>(null);
  const downloadGeneration = useRef(0);
  const [download, setDownload] = useState<'idle' | 'loading' | 'done' | 'error'>('idle');
  useEffect(() => {
    const abort = new AbortController();
    downloadGeneration.current += 1;
    setDownload('idle');
    fetch(`/api/v1/audio/catalog/${lang}`, { signal: abort.signal })
      .then(response => { if (!response.ok) throw new Error('Catalog unavailable'); return response.json(); })
      .then(data => setCatalog({ lang, data })).catch(() => {});
    return () => abort.abort();
  }, [lang]);
  const disease = analysis.predicted_label;
  const text = catalog?.lang === lang ? catalog.data.diseases[disease]?.[section] || '' : '';
  const player = useAudio({
    staticUrl: `/api/v1/audio/files/${lang}/${encodeURIComponent(disease)}/${section}.mp3`,
    text, lang, scope: location.key,
  });
  const downloadAudio = async () => {
    const token = downloadGeneration.current;
    setDownload('loading');
    try {
      if (!('serviceWorker' in navigator)) throw new Error('Offline audio unsupported');
      await navigator.serviceWorker.register('/audio-sw.js', { scope: '/' });
      const registration = await navigator.serviceWorker.ready;
      await new Promise<void>((resolve, reject) => {
        const channel = new MessageChannel();
        const timer = setTimeout(() => { channel.port1.close(); reject(new Error('Download timed out')); }, 300000);
        channel.port1.onmessage = event => {
          clearTimeout(timer); channel.port1.close();
          event.data.ok ? resolve() : reject(new Error(event.data.error));
        };
        registration.active!.postMessage({ type: 'DOWNLOAD_AUDIO', lang }, [channel.port2]);
      });
      if (token === downloadGeneration.current) setDownload('done');
    } catch { if (token === downloadGeneration.current) setDownload('error'); }
  };
  const status = player.state === 'error' ? 'unavailable' : player.state === 'ready' ? 'tap_play' : player.state === 'playing' ? 'playing' : player.state === 'paused' ? 'paused' : 'ready';
  return <section aria-label={t('audio.title')} className="rounded-3xl bg-slate-900 p-6 text-white space-y-4">
    <h3 className="text-lg font-bold">{t('audio.title')}</h3>
    <label className="block">{t('audio.listen_btn', { lang: SUPPORTED_LANGUAGES.find(l => l.code === lang)?.nativeLabel })}
      <select aria-label={t('audio.title')} className="ml-3 rounded bg-slate-800 p-2" value={lang} onChange={e => { player.stop(); void i18n.changeLanguage(e.target.value); }}>
        {SUPPORTED_LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.nativeLabel}</option>)}
      </select>
    </label>
    <div className="flex flex-wrap gap-2">
      {(['diagnosis', 'symptoms', 'treatment', 'prevention'] as Section[]).map(s => <button key={s} type="button" aria-pressed={section === s} onClick={() => { player.stop(); setSection(s); }} className={`rounded px-3 py-2 ${section === s ? 'bg-brand-600' : 'bg-slate-700'}`}>{t(`audio.section_${s}`)}</button>)}
    </div>
    <div className="flex flex-wrap items-center gap-3">
      <button type="button" disabled={player.state === 'loading'} onClick={player.state === 'playing' ? player.pause : player.play} className="rounded bg-brand-600 px-4 py-2 disabled:opacity-50">
        {player.state === 'playing' ? t('audio.pause') : player.state === 'paused' ? t('audio.resume') : t('audio.listen_btn', { lang: SUPPORTED_LANGUAGES.find(l => l.code === lang)?.nativeLabel })}
      </button>
      <button type="button" onClick={player.stop}>{t('audio.stop')}</button>
      <button type="button" onClick={player.replay}>{t('audio.replay')}</button>
      <label>{t('audio.speed')} <select className="rounded bg-slate-800 p-2" value={player.speed} onChange={e => player.changeSpeed(Number(e.target.value))}>{[0.75, 1, 1.25].map(speed => <option key={speed} value={speed}>{speed}x</option>)}</select></label>
    </div>
    <p role={player.state === 'error' ? 'alert' : 'status'} aria-live="polite" aria-busy={player.state === 'loading'}>{player.state === 'loading' ? t('audio.loading') : t(`audio.${status}`)}</p>
    <button type="button" disabled={download === 'loading'} onClick={() => void downloadAudio()} className="rounded border border-slate-500 px-3 py-2">{t('audio.download')}</button>
    {download !== 'idle' && <p role="status">{download === 'loading' ? t('audio.loading') : t(download === 'done' ? 'audio.downloaded' : 'audio.download_error')}</p>}
  </section>;
};
