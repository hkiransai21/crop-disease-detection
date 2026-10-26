import React, { useRef, useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Volume2, Check, Camera, ScanLine, ArrowRight } from "lucide-react";
import { SUPPORTED_LANGUAGES } from "../i18n/i18n";
export function LanguageButtons({ onSelect }: { onSelect?: () => void }) {
  const { t, i18n } = useTranslation();
  const sound = useRef<HTMLAudioElement | null>(null);
  const [error, setError] = useState(false);
  useEffect(
    () => () => {
      sound.current?.pause();
    },
    [],
  );
  return (
    <>
      <div className="language-list">
        {SUPPORTED_LANGUAGES.map((lang) => (
          <div className="language-row" key={lang.code}>
            <button
              className="language-name"
              lang={lang.code}
              onClick={() => {
                sound.current?.pause();
                localStorage.setItem("agrishield_language", lang.code);
                void i18n.changeLanguage(lang.code);
                onSelect?.();
              }}
            >
              <span>{lang.nativeLabel}</span>
              {i18n.language === lang.code && <Check aria-hidden="true" />}
            </button>
            <button
              className="language-sound"
              aria-label={t("farmer.hear_language", { name: lang.nativeLabel })}
              onClick={() => {
                sound.current?.pause();
                window.dispatchEvent(new CustomEvent("leaf-audio-start"));
                const audio = new Audio(`/voice/${lang.code}.mp3`);
                sound.current = audio;
                setError(false);
                void audio.play().catch(() => setError(true));
              }}
            >
              <Volume2 aria-hidden="true" />
              <span className="sr-only">{t("farmer.listen")}</span>
            </button>
          </div>
        ))}
      </div>
      {error && <p role="alert">{t("audio.unavailable")}</p>}
    </>
  );
}
export function LanguageChoice({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();
  const [chosen, setChosen] = useState(() =>
    SUPPORTED_LANGUAGES.some(
      (l) => l.code === localStorage.getItem("agrishield_language"),
    ),
  );
  const [learned, setLearned] = useState(
    () => localStorage.getItem("leaf_tutorial") === "done",
  );
  if (!chosen)
    return (
      <main className="onboarding">
        <div className="eyebrow">{t("farmer.brand")}</div>
        <h1>{t("farmer.choose_language")}</h1>
        <LanguageButtons onSelect={() => setChosen(true)} />
      </main>
    );
  const finish = () => {
    localStorage.setItem("leaf_tutorial", "done");
    setLearned(true);
  };
  if (!learned)
    return (
      <main className="onboarding">
        <h1>{t("farmer.learn")}</h1>
        <ol className="tutorial">
          <li>
            <Camera aria-hidden="true" />
            <span>{t("farmer.tutorial_photo")}</span>
          </li>
          <li>
            <ScanLine aria-hidden="true" />
            <span>{t("farmer.tutorial_result")}</span>
          </li>
          <li>
            <Volume2 aria-hidden="true" />
            <span>{t("farmer.tutorial_listen")}</span>
          </li>
        </ol>
        <button className="button primary" onClick={finish}>
          <ArrowRight aria-hidden="true" />
          {t("farmer.start")}
        </button>
        <button className="button plain" onClick={finish}>
          {t("farmer.skip")}
        </button>
      </main>
    );
  return <>{children}</>;
}
