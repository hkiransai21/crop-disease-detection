import { useTranslation } from "react-i18next";
import { CheckCircle2, AlertTriangle, HelpCircle } from "lucide-react";
export function ConfidenceBar({
  confidence,
  isUncertain,
}: {
  confidence: number;
  isUncertain: boolean;
}) {
  const { t } = useTranslation();
  const level = isUncertain ? "low" : confidence >= 0.85 ? "high" : "medium";
  const Icon = isUncertain
    ? HelpCircle
    : level === "high"
      ? CheckCircle2
      : AlertTriangle;
  return (
    <p className={`confidence ${level}`}>
      <Icon aria-hidden="true" />
      <span>
        {t("farmer.confidence")}: <strong>{t(`farmer.${level}`)}</strong>
      </span>
    </p>
  );
}
