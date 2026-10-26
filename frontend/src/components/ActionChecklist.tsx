import { useTranslation } from "react-i18next";
import {
  Leaf,
  Hand,
  FlaskConical,
  ShieldCheck,
  UserCheck,
  Search,
  ChevronDown,
  AlertTriangle,
} from "lucide-react";
import { DiseaseEntry } from "../types";
export function ActionChecklist({ disease }: { disease: DiseaseEntry }) {
  const { t } = useTranslation();
  const sections = [
    {
      key: "what",
      Icon: Search,
      items: [disease.disease_name, disease.summary, disease.symptoms],
    },
    { key: "now", Icon: Hand, items: disease.immediate_actions || [] },
    { key: "organic", Icon: Leaf, items: disease.organic_controls },
    { key: "chemical", Icon: FlaskConical, items: disease.chemical_controls },
    { key: "prevention", Icon: ShieldCheck, items: disease.prevention_steps },
    { key: "expert", Icon: UserCheck, items: [disease.when_to_consult_expert] },
  ];
  return (
    <section className="advice" aria-label={t("result.actions_title")}>
      {sections.map(({ key, Icon, items }) => (
        <details className="advice-section" key={key}>
          <summary>
            <Icon aria-hidden="true" />
            <span>{t(`farmer.${key}`)}</span>
            <ChevronDown aria-hidden="true" />
          </summary>
          <div className="advice-body">
            {key === "chemical" && (
              <div className="notice warning">
                <h3>
                  <AlertTriangle aria-hidden="true" />
                  {t("farmer.safety")}
                </h3>
                <p>{disease.safety_notice || t("result.label_dose_only")}</p>
                <ul>
                  {disease.safety_notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              </div>
            )}
            <ul>
              {items.filter(Boolean).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            {key === "expert" && (
              <>
                <h3>{t("result.sources_title")}</h3>
                <ul>
                  {disease.sources.map((source, i) => (
                    <li key={i}>{source}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </details>
      ))}
      {disease.review_status === "machine_suggested" && (
        <p className="review-note">{t("farmer.review")}</p>
      )}
    </section>
  );
}
