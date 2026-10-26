import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Leaf, ChevronRight } from "lucide-react";
import { api } from "../api/client";
import { DiseaseEntry } from "../types";
import { ActionChecklist } from "../components/ActionChecklist";
import { Loading, Retry } from "../ui/primitives";
import { Modal } from "../ui/Modal";
export function DiseasesPage() {
  const { t, i18n } = useTranslation();
  const [diseases, setDiseases] = useState<DiseaseEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [crop, setCrop] = useState("");
  const [agent, setAgent] = useState("");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<DiseaseEntry>();
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    setSelected(undefined);
    setCrop("");
    api
      .getDiseases(undefined, undefined, i18n.language)
      .then((data) => {
        if (active) setDiseases(data);
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [i18n.language, retry]);
  const filtered = diseases.filter(
    (d) =>
      (!crop || d.crop === crop) &&
      (!agent || d.causal_agent_type === agent) &&
      `${d.disease_name} ${d.crop} ${d.scientific_name} ${d.symptoms}`
        .toLocaleLowerCase()
        .includes(query.toLocaleLowerCase()),
  );
  return (
    <section className="stack">
      <h1>{t("diseases_page.title")}</h1>
      <label>
        {t("diseases_page.search_placeholder")}
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>
      <label>
        {t("diseases_page.all_crops")}
        <select value={crop} onChange={(e) => setCrop(e.target.value)}>
          <option value="">{t("diseases_page.all_crops")}</option>
          {[...new Set(diseases.map((d) => d.crop))].map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
      </label>
      <label>
        {t("diseases_page.all_agents")}
        <select value={agent} onChange={(e) => setAgent(e.target.value)}>
          <option value="">{t("diseases_page.all_agents")}</option>
          {["fungal", "bacterial", "viral", "pest", "none"].map((a) => (
            <option key={a} value={a}>
              {t(`agents.${a}`)}
            </option>
          ))}
        </select>
      </label>
      {loading ? (
        <Loading />
      ) : error ? (
        <Retry onRetry={() => setRetry((n) => n + 1)} />
      ) : (
        <ul className="guide-list">
          {filtered.map((d) => (
            <li key={d.id}>
              <button className="guide-row" onClick={() => setSelected(d)}>
                <Leaf aria-hidden="true" />
                <span>
                  <strong>{d.disease_name}</strong>
                  <span className="scientific">{d.scientific_name}</span>
                </span>
                <ChevronRight aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
      {selected && (
        <Modal
          title={selected.disease_name}
          onClose={() => setSelected(undefined)}
        >
          <p>{selected.scientific_name}</p>
          <ActionChecklist disease={selected} />
        </Modal>
      )}
    </section>
  );
}
