import { tr } from '../i18n/i18n';
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  MessageSquare,
  ShieldCheck,
  Calendar,
  MapPin,
  Leaf,
  Bug,
  Activity,
  ArrowLeft,
  Share2
} from 'lucide-react';
import { api } from '../api/client';
import { AnalysisResponse } from '../types';
import { RiskGauge } from '../components/RiskGauge';
import { ConfidenceBar } from '../components/ConfidenceBar';
import { ActionChecklist } from '../components/ActionChecklist';
import { FeedbackModal } from '../components/FeedbackModal';
import { AudioNarrator } from '../components/AudioNarrator';
import { KnapsackCalculator } from '../components/KnapsackCalculator';
import { WhatsAppShareModal } from '../components/WhatsAppShareModal';

interface ResultPageProps {
  lastAnalysis: AnalysisResponse | null;
}

export const ResultPage: React.FC<ResultPageProps> = ({ lastAnalysis }) => {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  // Prefer in-memory navigation state, then prop, then sessionStorage backup
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(() => {
    const navAnalysis = (location.state as any)?.analysis;
    if (navAnalysis && (!id || navAnalysis.id === id)) return navAnalysis;
    if (lastAnalysis && (!id || lastAnalysis.id === id)) return lastAnalysis;
    try {
      const saved = sessionStorage.getItem('agrishield_last_analysis');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (!id || parsed.id === id) return parsed;
      }
    } catch {}
    return null;
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedbackDone, setFeedbackDone] = useState(false);
  const [isShareOpen, setIsShareOpen] = useState(false);

  const currentLang = i18n.language ? i18n.language.split('-')[0].split('_')[0] : 'en';
  const prevLangRef = useRef(currentLang);

  useEffect(() => {
    if (!id) return;

    const isGuest = id.startsWith('guest_');
    const isLangChange = prevLangRef.current !== currentLang || Boolean(analysis && (analysis.language || 'en') !== currentLang);
    prevLangRef.current = currentLang;

    // Case 1: We already have the analysis in memory for this ID
    if (analysis && analysis.id === id) {
      if (!isLangChange) {
        // Initial mount or state transition: already loaded, do NOT fetch from API!
        return;
      }

      // Language was changed while viewing:
      if (isGuest || !api.getToken()) {
        // Guest or unauthenticated user: re-localize disease details from public encyclopedia
        if (analysis.predicted_label) {
          setLoading(true);
          api.localizeResult(analysis, currentLang)
            .then((result) => { if (i18n.language.split('-')[0] === currentLang) setAnalysis(result); })
            .catch(() => setError(tr('ui.s_c70a63d267')))
            .finally(() => setLoading(false));
        }
      } else {
        // Authenticated user with saved analysis in DB: fetch fully localized record
        api
          .getHistoryDetail(id, currentLang)
          .then((res) => { if (i18n.language.split('-')[0] === currentLang) setAnalysis(res); })
          .catch(() => setError(tr('ui.s_c70a63d267')));
      }
      return;
    }

    // Case 2: Analysis is not in memory (direct URL or refreshed guest without cache)
    if (isGuest) {
      setError(tr('ui.s_60d8892340'));
      setLoading(false);
      return;
    }

    // Case 3: Persistent analysis ID from database
    if (!api.getToken()) {
      setError(tr('ui.s_54fc8a7dad'));
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .getHistoryDetail(id, currentLang)
      .then((res) => {
        setAnalysis(res);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || tr('ui.s_c70a63d267'));
      })
      .finally(() => setLoading(false));
  }, [id, currentLang]);

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <div className="w-12 h-12 border-4 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm font-semibold text-slate-600">{t('analyze.analyzing')}</p>
      </div>
    );
  }

  if (error || !analysis) {
    const isAuthError =
      error?.toLowerCase().includes('sign in') ||
      error?.toLowerCase().includes('login') ||
      error?.toLowerCase().includes('credential');

    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">{t('history.empty')}</h2>
        <p className="text-xs text-slate-500">{error || tr('ui.s_30f5d11bb2')}</p>
        <div className="flex items-center justify-center gap-3 pt-2">
          {isAuthError && (
            <Link
              to="/auth"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-xs font-bold shadow-md"
            >
              <span>{t('nav.login')}</span>
            </Link>
          )}
          <Link
            to="/analyze"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t('result.scan_another')}</span>
          </Link>
        </div>
      </div>
    );
  }

  const isHealthy = analysis.disease_details?.is_healthy || analysis.predicted_label.toLowerCase().includes('healthy');

  return (
    <div className="max-w-4xl mx-auto py-6 space-y-8">
      {/* Top Bar Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link
          to="/analyze"
          className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t('result.back_btn')}</span>
        </Link>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setIsShareOpen(true)}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm shadow-emerald-600/20 transition-all active:scale-95"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{t('result.share_whatsapp')}</span>
          </button>

          <button
            onClick={() => setIsFeedbackOpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-700 transition-colors"
          >
            <MessageSquare className="w-3.5 h-3.5 text-brand-600" />
            <span>{feedbackDone ? t('result.feedback_done') : t('result.feedback_btn')}</span>
          </button>
        </div>
      </div>

      {/* Main Diagnostic Header Card */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className={`p-6 sm:p-8 text-white ${
          isHealthy
            ? 'bg-gradient-to-r from-emerald-700 to-teal-800'
            : 'bg-gradient-to-r from-slate-900 via-brand-950 to-emerald-950'
        }`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-white/20 text-white text-[11px] font-bold uppercase tracking-wider backdrop-blur-sm">
                  {analysis.crop}
                </span>
                {analysis.disease_details?.causal_agent_type && (
                  <span className="px-2.5 py-0.5 rounded-full bg-white/10 text-white/90 text-[11px] font-medium uppercase tracking-wider">
                    {t(`agents.${analysis.disease_details.causal_agent_type}`)}
                  </span>
                )}
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                {analysis.is_uncertain ? t('result.possible', { name: analysis.disease_name }) : analysis.disease_name}
              </h1>

              {analysis.disease_details?.scientific_name && (
                <p className="text-xs sm:text-sm text-slate-300 italic">
                  {t('result.pathogen_label')}: {analysis.disease_details.scientific_name}
                </p>
              )}
            </div>

            {/* Diagnostic Status Icon */}
            <div className="shrink-0">
              {isHealthy ? (
                <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white shadow-inner">
                  <CheckCircle2 className="w-10 h-10" />
                </div>
              ) : (
                <div className="w-16 h-16 rounded-2xl bg-amber-500/20 border border-amber-400/30 backdrop-blur-md flex items-center justify-center text-amber-300 shadow-inner">
                  <Bug className="w-10 h-10" />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Diagnostic Metadata Sub-bar */}
        <div className="px-6 py-3 bg-slate-50 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 font-medium">
          <div className="flex items-center space-x-1.5">
            <Calendar className="w-3.5 h-3.5" />
            <span>{t('result.diagnosed_on')} {new Date(analysis.created_at).toLocaleDateString(i18n.language + '-IN')}</span>
          </div>

          {analysis.location_name && (
            <div className="flex items-center space-x-1.5 text-slate-700">
              <MapPin className="w-3.5 h-3.5 text-brand-600" />
              <span>{analysis.location_name}</span>
            </div>
          )}

          <div className="font-mono text-[10px] text-slate-400">
            {tr('ui.s_9e1279af1f')}{analysis.model_version}
          </div>
        </div>
      </div>

      {/* Voice Assistant / Multi-lingual Spoken Audio Narration */}
      {!analysis.is_uncertain && <AudioNarrator analysis={analysis} />}

      {/* Grid: Image & Confidence Meter */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Uploaded Image Preview */}
        <div className="md:col-span-5 bg-white rounded-2xl border border-slate-200/80 p-3 shadow-sm flex flex-col items-center justify-center">
          <div className="relative rounded-xl overflow-hidden aspect-square w-full bg-slate-900 flex items-center justify-center">
            <img
              src={analysis.image_url}
              alt={tr('ui.s_48cc1eaaf7')}
              className="w-full h-full object-contain"
            />
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-2">{tr('ui.s_07e5acb78f')}</span>
        </div>

        {/* Confidence & Diagnostic Reliability Bar */}
        <div className="md:col-span-7">
          <ConfidenceBar
            confidence={analysis.confidence}
            confidenceDisplay={analysis.confidence_display}
            isUncertain={analysis.is_uncertain}
            uncertaintyReason={analysis.uncertainty_reason}
            topK={analysis.top_k}
          />
        </div>
      </div>

      {/* Outbreak Risk Engine Gauge */}
      {analysis.risk_assessment && !analysis.is_uncertain && (
        <RiskGauge assessment={analysis.risk_assessment} />
      )}

      {/* Actionable Treatment & Prevention Protocol */}
      {analysis.disease_details && !analysis.is_uncertain && (
        <ActionChecklist disease={analysis.disease_details} />
      )}

      {/* Knapsack Sprayer & Tank Dosage Calculator */}
      {analysis.disease_details && !analysis.is_uncertain && (
        <KnapsackCalculator
          disease={analysis.disease_details}
          cropName={analysis.crop}
        />
      )}

      {/* Bottom CTA */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200">
        <Link
          to="/analyze"
          className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3.5 rounded-2xl bg-brand-600 hover:bg-brand-700 text-white text-sm font-bold shadow-md shadow-brand-600/20"
        >
          <RefreshCw className="w-4 h-4" />
          <span>{t('result.scan_another')}</span>
        </Link>

        <Link
          to="/history"
          className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3.5 rounded-2xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 text-sm font-bold"
        >
          <span>{t('result.view_history')}</span>
        </Link>
      </div>

      {/* Feedback Dialog */}
      <FeedbackModal
        analysisId={analysis.id}
        predictedLabel={analysis.predicted_label}
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        onSubmitted={() => setFeedbackDone(true)}
      />

      {/* WhatsApp Share Dialog */}
      <WhatsAppShareModal
        analysis={analysis}
        isOpen={isShareOpen}
        onClose={() => setIsShareOpen(false)}
      />
    </div>
  );
};
