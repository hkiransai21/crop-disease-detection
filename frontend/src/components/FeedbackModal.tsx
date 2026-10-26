import { Modal } from "../ui/Modal";
import { tr } from "../i18n/i18n";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Check,
  X,
  Shield,
  Loader2,
} from "lucide-react";
import { api } from "../api/client";

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
  const [correctedLabel, setCorrectedLabel] = useState("");
  const [comments, setComments] = useState("");
  const [consent, setConsent] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isCorrect === null) {
      setError(tr("ui.s_0e60e944e4"));
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await api.submitFeedback(analysisId, {
        is_correct: isCorrect,
        corrected_label:
          !isCorrect && correctedLabel ? correctedLabel : undefined,
        comments: comments.trim() ? comments : undefined,
        consent_for_retraining: consent,
      });
      setSuccess(true);
      setTimeout(() => {
        onSubmitted();
        onClose();
      }, 1200);
    } catch (err: any) {
      setError(t("farmer.error"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal title={t("feedback.title")} onClose={onClose}>
      <div>
        <div>
          <div>
            <MessageSquare />
            <h3>{t("feedback.title")}</h3>
          </div>
          <button onClick={onClose} aria-label={t("farmer.close")}>
            <X />
          </button>
        </div>

        {success ? (
          <div>
            <div>
              <Check />
            </div>
            <h4>{t("feedback.thank_you")}</h4>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <p>
              {t("feedback.prompt")} (<strong>{predictedLabel}</strong>)
            </p>

            {/* Yes / No Buttons */}
            <div>
              <button
                type="button"
                aria-pressed={isCorrect === true}
                onClick={() => {
                  setIsCorrect(true);
                  setError(null);
                }}
              >
                <ThumbsUp />
                <span>{t("feedback.yes_btn")}</span>
              </button>

              <button
                type="button"
                aria-pressed={isCorrect === false}
                onClick={() => {
                  setIsCorrect(false);
                  setError(null);
                }}
              >
                <ThumbsDown />
                <span>{t("feedback.no_btn")}</span>
              </button>
            </div>

            {/* If Incorrect: specify label */}
            {isCorrect === false && (
              <div>
                <label htmlFor="corrected-label">
                  {t("feedback.select_actual")}
                </label>
                <input
                  id="corrected-label"
                  type="text"
                  placeholder={tr("ui.s_f27ffcbc35")}
                  value={correctedLabel}
                  onChange={(e) => setCorrectedLabel(e.target.value)}
                />
              </div>
            )}

            {/* Notes */}
            <div>
              <label htmlFor="feedback-comments">
                {t("feedback.comments_label")}
              </label>
              <textarea
                id="feedback-comments"
                rows={2}
                placeholder={tr("ui.s_fee3c9ab67")}
                value={comments}
                onChange={(e) => setComments(e.target.value)}
              />
            </div>

            {/* Retraining Consent */}
            <label>
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
              />
              <span>{t("feedback.consent_checkbox")}</span>
            </label>

            {error && <p>{error}</p>}

            <div>
              <button type="button" onClick={onClose}>
                {tr("ui.s_77dfd2135f")}
              </button>
              <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? <Loader2 /> : null}
                <span>{t("feedback.submit")}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
};
