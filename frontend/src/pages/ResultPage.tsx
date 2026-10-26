import { lazy, Suspense, useEffect, useState } from "react";
import { useParams, useLocation, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Camera, Share2, MessageSquare, HelpCircle } from "lucide-react";
import { api } from "../api/client";
import { AnalysisResponse } from "../types";
import { getCheck, saveCheck } from "../storage/checks";
import { Loading, Retry, usePhoto } from "../ui/primitives";
import { ConfidenceBar } from "../components/ConfidenceBar";
import { ActionChecklist } from "../components/ActionChecklist";
import { AudioNarrator } from "../components/AudioNarrator";
import { RiskGauge } from "../components/RiskGauge";
import { WeatherRisk } from "../components/WeatherRisk";
const FeedbackModal = lazy(() =>
  import("../components/FeedbackModal").then((m) => ({
    default: m.FeedbackModal,
  })),
);
const WhatsAppShareModal = lazy(() =>
  import("../components/WhatsAppShareModal").then((m) => ({
    default: m.WhatsAppShareModal,
  })),
);
const KnapsackCalculator = lazy(() =>
  import("../components/KnapsackCalculator").then((m) => ({
    default: m.KnapsackCalculator,
  })),
);
export function ResultPage({
  lastAnalysis,
}: {
  lastAnalysis: AnalysisResponse | null;
}) {
  const { t, i18n } = useTranslation();
  const { id } = useParams();
  const route = useLocation();
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(() => {
    const state = route.state?.analysis || lastAnalysis;
    if (state?.id === id) return state;
    try {
      const saved = JSON.parse(
        sessionStorage.getItem("agrishield_last_analysis") || "null",
      );
      return saved?.id === id ? saved : null;
    } catch {
      return null;
    }
  });
  const [photo, setPhoto] = useState<Blob>();
  const src = usePhoto(photo, analysis?.image_url);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [feedback, setFeedback] = useState(false);
  const [share, setShare] = useState(false);
  const [done, setDone] = useState(false);
  const [calculator, setCalculator] = useState(false);
  const lang = i18n.language.split("-")[0];
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    void (async () => {
      let cached;
      try {
        cached = id ? await getCheck(id) : undefined;
      } catch {}
      if (!active) return;
      setPhoto(cached?.photo);
      const incoming = route.state?.analysis as AnalysisResponse | undefined;
      let next = incoming?.id === id ? incoming :
        (analysis?.id === id ? analysis : cached?.result);
      if (next && (next.language || "en") !== lang)
        next = await api.localizeResult(next, lang);
      if (!next && id && !id.startsWith("guest_"))
        next = await api.getHistoryDetail(id, lang);
      if (!next) throw new Error();
      if (active) {
        setAnalysis(next);
        void saveCheck(next).catch(() => {});
      }
    })()
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id, lang, retry, route.key]);
  if (loading) return <Loading />;
  if (error || !analysis)
    return <Retry onRetry={() => setRetry((n) => n + 1)} />;
  return (
    <article className="result-page">
      <div className="result-heading">
        {src && (
          <img className="result-photo" src={src} alt={t("farmer.preview")} />
        )}
        <div>
          <p className="eyebrow">{analysis.crop}</p>
          <h1>
            {analysis.is_uncertain
              ? t("farmer.uncertain")
              : analysis.disease_name.split(/[([]/, 1)[0].trim() ||
                analysis.disease_name}
          </h1>
        </div>
      </div>
      <ConfidenceBar
        confidence={analysis.confidence}
        isUncertain={analysis.is_uncertain}
      />
      {analysis.is_uncertain ? (
        <section className="uncertain notice warning">
          <HelpCircle aria-hidden="true" />
          <p>{t("farmer.uncertain_note")}</p>
          <p>{t('result.uncertain_desc')}</p>
          <Link className="primary" to="/analyze">
            <Camera aria-hidden="true" />
            {t("farmer.retake")}
          </Link>
        </section>
      ) : (
        <>
          <AudioNarrator analysis={analysis} />
          <p className="scientific">
            {analysis.scientific_name ||
              analysis.disease_details?.scientific_name}
          </p>
          {analysis.disease_details && (
            <ActionChecklist disease={analysis.disease_details} />
          )}
          <WeatherRisk analysis={analysis} />
          {analysis.disease_details && (
            <details
              className="advice-section"
              onToggle={(e) => setCalculator(e.currentTarget.open)}
            >
              <summary>{t("result.calc_title")}</summary>
              {calculator && (
                <Suspense fallback={<Loading />}>
                  <KnapsackCalculator
                    disease={analysis.disease_details}
                    cropName={analysis.crop}
                  />
                </Suspense>
              )}
            </details>
          )}
        </>
      )}
      <section aria-label={t('pipeline.possibilities')}>
        <h2>{t('pipeline.possibilities')}</h2>
        <ol>{analysis.top_k.map(item => <li key={item.class_id}>
          {item.crop}: {item.disease_name} — {t(`farmer.${item.confidence >= 0.85 ? 'high' : item.confidence >= 0.6 ? 'medium' : 'low'}`)} ({item.confidence_percentage.toFixed(1)}%)
        </li>)}</ol>
      </section>
      <div className="result-actions">
        <Link className="primary" to="/analyze">
          <Camera aria-hidden="true" />
          {t("farmer.photo")}
        </Link>
        <button className="secondary" onClick={() => setShare(true)}>
          <Share2 aria-hidden="true" />
          {t("result.share_whatsapp")}
        </button>
        {!analysis.id.startsWith("guest_") && (
          <button className="secondary" onClick={() => setFeedback(true)}>
            <MessageSquare aria-hidden="true" />
            {t(done ? "result.feedback_done" : "result.feedback_btn")}
          </button>
        )}
      </div>
      <Suspense fallback={<Loading />}>
        {feedback && (
          <FeedbackModal
            analysisId={analysis.id}
            predictedLabel={analysis.predicted_label}
            isOpen
            onClose={() => setFeedback(false)}
            onSubmitted={() => setDone(true)}
          />
        )}
        {share && (
          <WhatsAppShareModal
            analysis={analysis}
            isOpen
            onClose={() => setShare(false)}
          />
        )}
      </Suspense>
    </article>
  );
}
