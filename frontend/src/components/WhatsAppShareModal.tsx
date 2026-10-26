import { Modal } from "../ui/Modal";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { AnalysisResponse } from "../types";

export const WhatsAppShareModal: React.FC<{
  analysis: AnalysisResponse;
  isOpen: boolean;
  onClose: () => void;
}> = ({ analysis, isOpen, onClose }) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(false);
  if (!isOpen) return null;
  const details = analysis.disease_details;
  const advice = analysis.is_uncertain
    ? t("result.uncertain_desc")
    : [
        t("result.cultural_tab") +
          ": " +
          (details?.prevention_steps.join(" ") || ""),
        t("result.organic_tab") +
          ": " +
          (details?.organic_controls.join(" ") || ""),
        t("result.chemical_tab") +
          ": " +
          (details?.chemical_controls.join(" ") || ""),
        details?.safety_notes.join(" "),
      ].join("\n");
  const text = t("share.report", {
    crop: analysis.crop,
    disease: analysis.disease_name,
    confidence: Math.round(analysis.confidence * 100),
    advice,
  });
  return (
    <Modal title={t("share.title")} onClose={onClose}>
      <div>
        <p>{text}</p>
        <a
          className="secondary"
          href={`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("share.open")}
        </a>
        <button
          className="secondary"
          onClick={() => {
            navigator.clipboard
              .writeText(text)
              .then(() => setCopied(true))
              .catch(() => setError(true));
          }}
        >
          {t(copied ? "share.copied" : "share.copy")}
        </button>
        {error && <p role="alert">{t("share.copy_error")}</p>}
      </div>
    </Modal>
  );
};
