import React, { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Leaf,
  Languages,
  Home,
  Camera,
  History,
  Settings,
  X,
  WifiOff,
} from "lucide-react";
import { LanguageButtons } from "./LanguageChoice";
import { useOnline } from "../ui/primitives";
export function Navbar() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const online = useOnline();
  const route = useLocation();
  useEffect(() => {
    if (open) dialog.current?.showModal();
    else dialog.current?.close();
  }, [open]);
  useEffect(() => {
    setOpen(false);
  }, [route.pathname]);
  return (
    <>
      <a className="skip-link" href="#main">
        {t("farmer.skip_content")}
      </a>
      <header className="site-header">
        <Link to="/" className="wordmark">
          <Leaf aria-hidden="true" />
          <span>{t("farmer.brand")}</span>
        </Link>
        <button
          ref={trigger}
          className="header-language"
          onClick={() => {
            window.dispatchEvent(new CustomEvent("leaf-audio-start"));
            setOpen(true);
          }}
        >
          <Languages aria-hidden="true" />
          <span>{t("farmer.language")}</span>
        </button>
      </header>
      {!online && (
        <p className="offline-banner" role="status">
          <WifiOff aria-hidden="true" />
          {t("farmer.offline")}
        </p>
      )}
      <dialog
        ref={dialog}
        onCancel={() => setOpen(false)}
        onClose={() => {
          setOpen(false);
          trigger.current?.focus();
        }}
        aria-labelledby="language-heading"
      >
        <div className="dialog-head">
          <h2 id="language-heading">{t("farmer.language")}</h2>
          <button className="button plain" onClick={() => setOpen(false)}>
            <X aria-hidden="true" />
            {t("farmer.close")}
          </button>
        </div>
        <LanguageButtons onSelect={() => setOpen(false)} />
      </dialog>
    </>
  );
}
export function BottomNav() {
  const { t } = useTranslation();
  return (
    <nav className="bottom-nav" aria-label={t("farmer.home")}>
      {[
        { to: "/", key: "home", Icon: Home },
        { to: "/analyze", key: "camera", Icon: Camera },
        { to: "/history", key: "history", Icon: History },
        { to: "/settings", key: "settings", Icon: Settings },
      ].map(({ to, key, Icon }) => (
        <NavLink
          key={key}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <Icon aria-hidden="true" />
          <span>{t(`farmer.${key}`)}</span>
        </NavLink>
      ))}
    </nav>
  );
}
