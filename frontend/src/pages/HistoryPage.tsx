import { Modal } from "../ui/Modal";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Leaf, Trash2, Camera } from "lucide-react";
import { api } from "../api/client";
import { AnalysisHistoryItem, User } from "../types";
import { listChecks, deleteCheck, SavedCheck } from "../storage/checks";
import { Loading, Retry, usePhoto } from "../ui/primitives";
type Row = AnalysisHistoryItem & { photo?: Blob };
function HistoryRow({ item, onDelete }: { item: Row; onDelete: () => void }) {
  const { t, i18n } = useTranslation();
  const src = usePhoto(item.photo, item.image_url);
  return (
    <li className="history-row">
      <Link to={`/result/${item.id}`} className="history-link">
        {src ? (
          <img src={src} alt="" loading="lazy" />
        ) : (
          <Leaf aria-hidden="true" />
        )}
        <span>
          <strong>{item.disease_name}</strong>
          <time dateTime={item.created_at}>
            {new Date(item.created_at).toLocaleDateString(i18n.language, {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </time>
        </span>
      </Link>
      <button className="delete-button" onClick={onDelete}>
        <Trash2 aria-hidden="true" />
        {t("farmer.delete")}
      </button>
    </li>
  );
}
export function HistoryPage({ user }: { user: User | null }) {
  const { t, i18n } = useTranslation();
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [target, setTarget] = useState<string>();
  const [query, setQuery] = useState("");
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    void (async () => {
      let local: SavedCheck[] = [];
      try {
        local = await listChecks();
      } catch {}
      const map = new Map<string, Row>(
        local.map((c) => [
          c.id,
          {
            ...(c.variants[`${c.result.image_sha256 || c.id}:${i18n.language}`] || c.result),
            photo: c.photo,
            has_feedback: false,
          },
        ]),
      );
      // Local guest records need the same localized names as server history.
      if (navigator.onLine && local.some((c) => !c.variants[`${c.result.image_sha256 || c.id}:${i18n.language}`])) {
        try {
          const names = new Map(
            (await api.getDiseases(undefined, undefined, i18n.language)).map(
              (d) => [d.id, d],
            ),
          );
          for (const [id, row] of map) {
            const disease = names.get(row.predicted_label);
            if (disease)
              map.set(id, {
                ...row,
                crop: disease.crop,
                disease_name: disease.disease_name,
              });
          }
        } catch {
          if (active) setError(true);
        }
      }
      if (user && navigator.onLine) {
        try {
          for (const row of await api.getHistory(100, 0, i18n.language))
            map.set(row.id, { ...map.get(row.id), ...row });
        } catch {
          if (active) setError(true);
        }
      }
      if (active)
        setRows(
          [...map.values()].sort((a, b) =>
            b.created_at.localeCompare(a.created_at),
          ),
        );
    })().finally(() => {
      if (active) setLoading(false);
    });
    return () => {
      active = false;
    };
  }, [user, i18n.language, attempt]);
  async function remove() {
    if (!target) return;
    try {
      if (!target.startsWith("guest_")) await api.deleteHistory(target);
      await deleteCheck(target);
      setRows(rows.filter((row) => row.id !== target));
      setTarget(undefined);
    } catch {
      setError(true);
    }
  }
  return (
    <section className="history-page stack">
      <h1>{t("farmer.history")}</h1>
      {error && <Retry onRetry={() => setAttempt((n) => n + 1)} />}
      <label>
        {t("history.filter_placeholder")}
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>
      {loading ? (
        <Loading />
      ) : rows.length ? (
        <ul className="history-list">
          {rows
            .filter((row) =>
              (row.crop + row.disease_name)
                .toLocaleLowerCase()
                .includes(query.toLocaleLowerCase()),
            )
            .map((item) => (
              <HistoryRow
                key={item.id}
                item={item}
                onDelete={() => setTarget(item.id)}
              />
            ))}
        </ul>
      ) : (
        <>
          <Leaf className="empty-leaf" aria-hidden="true" />
          <p>{t("farmer.empty")}</p>
          <Link className="primary" to="/analyze">
            <Camera aria-hidden="true" />
            {t("farmer.photo")}
          </Link>
        </>
      )}
      {target && (
        <Modal
          title={t("history.delete_confirm")}
          onClose={() => setTarget(undefined)}
        >
          <div className="button-row">
            <button className="secondary" onClick={() => void remove()}>
              {t("farmer.confirm")}
            </button>
            <button className="secondary" onClick={() => setTarget(undefined)}>
              {t("farmer.close")}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
