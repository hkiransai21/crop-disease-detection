import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AnalysisResponse } from '../types';

export const WhatsAppShareModal: React.FC<{ analysis: AnalysisResponse; isOpen: boolean; onClose: () => void }> = ({ analysis, isOpen, onClose }) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(false);
  if (!isOpen) return null;
  const details = analysis.disease_details;
  const advice = analysis.is_uncertain ? t('result.uncertain_desc') : [
    t('result.cultural_tab') + ': ' + (details?.prevention_steps.join(' ') || ''),
    t('result.organic_tab') + ': ' + (details?.organic_controls.join(' ') || ''),
    t('result.chemical_tab') + ': ' + (details?.chemical_controls.join(' ') || ''),
    details?.safety_notes.join(' '),
  ].join('\n');
  const text = t('share.report', { crop: analysis.crop, disease: analysis.disease_name, confidence: Math.round(analysis.confidence * 100), advice });
  return <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/60" role="dialog" aria-modal="true" aria-label={t('share.title')}>
    <div className="max-h-[90dvh] overflow-y-auto bg-white rounded-2xl p-5 w-full max-w-lg space-y-4">
      <h2 className="text-lg font-bold">{t('share.title')}</h2>
      <button onClick={onClose}>{t('common.close')}</button>
      <p className="whitespace-pre-line text-sm break-words">{text}</p>
      <a className="block rounded bg-emerald-700 p-3 text-white text-center" href={`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`} target="_blank" rel="noopener noreferrer">{t('share.open')}</a>
      <button onClick={() => { navigator.clipboard.writeText(text).then(() => setCopied(true)).catch(() => setError(true)); }}>{t(copied ? 'share.copied' : 'share.copy')}</button>
      {error && <p role="alert">{t('share.copy_error')}</p>}
    </div>
  </div>;
};
