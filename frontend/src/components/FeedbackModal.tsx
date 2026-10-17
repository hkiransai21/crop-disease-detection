import { tr } from '../i18n/i18n';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ThumbsUp, ThumbsDown, MessageSquare, Check, X, Shield, Loader2 } from 'lucide-react';
import { api } from '../api/client';

interface FeedbackModalProps {
  analysisId: string;
  predictedLabel: string;
  isOpen: boolean;
  onClose: () => void;
  onSubmitted: () => void;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  analysisId,
  predictedLabel,
  isOpen,
  onClose,
  onSubmitted,
}) => {
  const { t } = useTranslation();
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [correctedLabel, setCorrectedLabel] = useState('');
  const [comments, setComments] = useState('');
  const [consent, setConsent] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isCorrect === null) {
      setError(tr('ui.s_0e60e944e4'));
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await api.submitFeedback(analysisId, {
        is_correct: isCorrect,
        corrected_label: !isCorrect && correctedLabel ? correctedLabel : undefined,
        comments: comments.trim() ? comments : undefined,
        consent_for_retraining: consent,
      });
      setSuccess(true);
      setTimeout(() => {
        onSubmitted();
        onClose();
      }, 1200);
    } catch (err: any) {
      setError(err.message || tr('ui.s_d53daebde2'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-brand-600" />
            <h3 className="text-base font-bold text-slate-900">{t('feedback.title')}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <Check className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-slate-900">{t('feedback.thank_you')}</h4>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-xs text-slate-600">
              {t('feedback.prompt')} (<strong className="text-slate-900">{predictedLabel}</strong>)
            </p>

            {/* Yes / No Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => {
                  setIsCorrect(true);
                  setError(null);
                }}
                className={`flex items-center justify-center space-x-2 p-3 rounded-xl border text-xs font-bold transition-all ${
                  isCorrect === true
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-600/20'
                    : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
                <span>{t('feedback.yes_btn')}</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setIsCorrect(false);
                  setError(null);
                }}
                className={`flex items-center justify-center space-x-2 p-3 rounded-xl border text-xs font-bold transition-all ${
                  isCorrect === false
                    ? 'bg-rose-600 text-white border-rose-600 shadow-md shadow-rose-600/20'
                    : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                }`}
              >
                <ThumbsDown className="w-4 h-4" />
                <span>{t('feedback.no_btn')}</span>
              </button>
            </div>

            {/* If Incorrect: specify label */}
            {isCorrect === false && (
              <div className="space-y-1 animate-fadeIn">
                <label className="block text-xs font-semibold text-slate-700">{t('feedback.select_actual')}</label>
                <input
                  type="text"
                  placeholder={tr('ui.s_f27ffcbc35')}
                  value={correctedLabel}
                  onChange={(e) => setCorrectedLabel(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-brand-500"
                />
              </div>
            )}

            {/* Notes */}
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-slate-700">{t('feedback.comments_label')}</label>
              <textarea
                rows={2}
                placeholder={tr('ui.s_fee3c9ab67')}
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-brand-500"
              />
            </div>

            {/* Retraining Consent */}
            <label className="flex items-start space-x-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 cursor-pointer">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="rounded text-brand-600 focus:ring-brand-500 mt-0.5"
              />
              <span className="leading-tight">
                {t('feedback.consent_checkbox')}
              </span>
            </label>

            {error && <p className="text-xs font-semibold text-rose-600">{error}</p>}

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                {tr('ui.s_77dfd2135f')}</button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center space-x-1.5 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-600/20 disabled:opacity-50"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                <span>{t('feedback.submit')}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

