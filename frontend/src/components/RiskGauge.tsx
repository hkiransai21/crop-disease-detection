import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";
import {
  CloudSun,
  ShieldCheck,
  AlertTriangle,
  Volume2,
  Pause,
} from "lucide-react";
import { RiskAssessment } from "../types";
import { useAudio } from "../hooks/useAudio";
export function RiskGauge({ assessment }: { assessment: RiskAssessment }) {
  const { t, i18n } = useTranslation();
  const route = useLocation();
  const level =
    assessment.risk_level === "LOW"
      ? "low"
      : assessment.risk_level === "MODERATE"
        ? "medium"
        : "high";
  const text = [assessment.headline, assessment.summary, ...assessment.contributing_factors.map(f => f.explanation)].join(' ');
  const player = useAudio({
    staticUrl: `/api/v1/audio/tts?${new URLSearchParams({text, lang: i18n.language})}`,
    text,
    lang: i18n.language,
    scope: route.key,
  });
  return (
    <section className={`risk-strip risk-${level}`}>
      <h2>
        <CloudSun aria-hidden="true" />
        {t("farmer.weather")}
      </h2>
      <p className="risk-label">
        {level === "low" ? (
          <ShieldCheck aria-hidden="true" />
        ) : (
          <AlertTriangle aria-hidden="true" />
        )}
        <strong>{t(`farmer.${level}`)}</strong>
      </p>
      <p>{`${assessment.risk_score} / 100`}</p>
      <p>{assessment.headline}</p>
      <p>{assessment.summary}</p>
      {assessment.action && <p>{assessment.action}</p>}
      <ul>{assessment.contributing_factors.slice(0, 3).map((factor, i) => <li key={i}>{factor.explanation}</li>)}</ul>
      <p>{t(`farmer.risk_${level}`)}</p>
      <button
        className="secondary"
        onClick={player.state === "playing" ? player.pause : player.play}
        disabled={player.state === "loading"}
      >
        {player.state === "playing" ? (
          <Pause aria-hidden="true" />
        ) : (
          <Volume2 aria-hidden="true" />
        )}
        {t(player.state === "playing" ? "audio.pause" : "farmer.listen")}
      </button>
      {player.state === "error" && <p role="alert">{t("audio.unavailable")}</p>}
      <details>
        <summary>{t("farmer.more")}</summary>
        <p>{assessment.disclaimer}</p>
      </details>
    </section>
  );
}
