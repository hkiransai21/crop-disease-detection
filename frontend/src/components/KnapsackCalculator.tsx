import React from "react";
import { useTranslation } from "react-i18next";
import { DiseaseEntry } from "../types";

export const KnapsackCalculator: React.FC<{
  disease: DiseaseEntry;
  cropName: string;
}> = ({ disease }) => {
  const { t } = useTranslation();
  // The old calculator invented a universal chemical dose for all diseases.
  // Only product-specific, locally approved label rates can support a calculation.
  return (
    <section>
      <h3>{t("result.calc_title")}</h3>
      <p>
        {t(
          disease.is_healthy
            ? "result.calc_healthy_notice"
            : "result.label_dose_only",
        )}
      </p>
    </section>
  );
};
