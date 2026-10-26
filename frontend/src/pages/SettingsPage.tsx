import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Contrast, BookOpen, UserRound, HelpCircle } from "lucide-react";
import { User } from "../types";
export default function SettingsPage({
  user,
  onLogout,
}: {
  user: User | null;
  onLogout: () => void;
}) {
  const { t } = useTranslation();
  const [contrast, setContrast] = useState(
    localStorage.getItem("leaf_contrast") === "high",
  );
  return (
    <section className="settings-page stack">
      <h1>{t("farmer.settings")}</h1>
      <button
        className="secondary"
        aria-pressed={contrast}
        onClick={() => {
          const next = !contrast;
          setContrast(next);
          localStorage.setItem("leaf_contrast", next ? "high" : "normal");
          document.documentElement.dataset.contrast = next ? "high" : "normal";
        }}
      >
        <Contrast aria-hidden="true" />
        {t("farmer.contrast")}
      </button>
      <section className="settings-note">
        <h2>{t("farmer.offline_audio")}</h2>
        <p>{t("farmer.offline_help")}</p>
      </section>
      <Link className="shortcut" to="/diseases">
        <BookOpen aria-hidden="true" />
        {t("nav.diseases")}
      </Link>
      <Link className="shortcut" to="/about">
        <HelpCircle aria-hidden="true" />
        {t("farmer.help")}
      </Link>
      {user ? (
        <>
          <p>{user.full_name || user.email}</p>
          <button className="secondary" onClick={onLogout}>
            {t("nav.logout")}
          </button>
        </>
      ) : (
        <Link className="shortcut" to="/auth">
          <UserRound aria-hidden="true" />
          {t("farmer.account")}
        </Link>
      )}
    </section>
  );
}
