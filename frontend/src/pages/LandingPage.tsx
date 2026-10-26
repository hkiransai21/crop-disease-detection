import React, { useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Camera, Image, History, ArrowRight } from "lucide-react";
import { LeafDrawing } from "../ui/primitives";
export const LandingPage: React.FC = () => {
  const { t } = useTranslation();
  const camera = useRef<HTMLInputElement>(null);
  const gallery = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const select = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) navigate("/analyze", { state: { file, automatic: true } });
  };
  return (
    <div className="home-page">
      <div className="home-intro">
        <div className="home-title">
          <h1>{t("farmer.home_title")}</h1>
        </div>
        <LeafDrawing />
      </div>
      <p className="home-note">{t("farmer.home_note")}</p>
      <input
        ref={camera}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={select}
        hidden
        aria-label={t("farmer.photo")}
      />
      <input
        ref={gallery}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={select}
        hidden
        aria-label={t("farmer.gallery")}
      />
      <div className="home-actions">
        <button
          className="button primary camera-hero"
          onClick={() => camera.current?.click()}
        >
          <Camera aria-hidden="true" />
          <span>{t("farmer.photo")}</span>
        </button>
        <button
          className="button secondary"
          onClick={() => gallery.current?.click()}
        >
          <Image aria-hidden="true" />
          <span>{t("farmer.gallery")}</span>
        </button>
      </div>
      <Link to="/history" className="history-shortcut">
        <History aria-hidden="true" />
        <span>{t("farmer.history")}</span>
        <ArrowRight aria-hidden="true" />
      </Link>
    </div>
  );
};
