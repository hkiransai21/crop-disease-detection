import { Volume2, Pause, Square, RotateCcw, Download } from "lucide-react";
import { tr } from "../i18n/i18n";
import React, { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";
import { AnalysisResponse } from "../types";
import { SUPPORTED_LANGUAGES } from "../i18n/i18n";
import { useAudio } from "../hooks/useAudio";

type Section = "diagnosis" | "symptoms" | "treatment" | "prevention";
type Catalog = { diseases: Record<string, Record<Section, string>> };

export const AudioNarrator: React.FC<{ analysis: AnalysisResponse }> = ({
  analysis,
}) => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const requested = i18n.language.split("-")[0];
  const lang = SUPPORTED_LANGUAGES.some((l) => l.code === requested)
    ? requested
    : "en";
  const [section, setSection] = useState<Section>("diagnosis");
  const [catalog, setCatalog] = useState<{
    lang: string;
    data: Catalog;
  } | null>(null);
  const downloadGeneration = useRef(0);
  const [download, setDownload] = useState<
    "idle" | "loading" | "done" | "error"
  >("idle");
  useEffect(() => {
    const abort = new AbortController();
    downloadGeneration.current += 1;
    setDownload("idle");
    fetch(`/api/v1/audio/catalog/${lang}`, { signal: abort.signal })
      .then((response) => {
        if (!response.ok) throw new Error(tr("ui.s_033863e5c3"));
        return response.json();
      })
      .then((data) => setCatalog({ lang, data }))
      .catch(() => {});
    return () => abort.abort();
  }, [lang]);
  const disease = analysis.predicted_label;
  const text =
    catalog?.lang === lang
      ? catalog.data.diseases[disease]?.[section] || ""
      : "";
  const player = useAudio({
    staticUrl: `/api/v1/audio/files/${lang}/${encodeURIComponent(disease)}/${section}.mp3`,
    text,
    lang,
    scope: location.key,
  });
  const downloadAudio = async () => {
    const token = downloadGeneration.current;
    setDownload("loading");
    try {
      if (!("serviceWorker" in navigator))
        throw new Error(tr("ui.s_5c6a5ce6e9"));
      await navigator.serviceWorker.register("/audio-sw.js", { scope: "/" });
      const registration = await navigator.serviceWorker.ready;
      await new Promise<void>((resolve, reject) => {
        const channel = new MessageChannel();
        const timer = setTimeout(() => {
          channel.port1.close();
          reject(new Error(tr("ui.s_ac8642a983")));
        }, 300000);
        channel.port1.onmessage = (event) => {
          clearTimeout(timer);
          channel.port1.close();
          event.data.ok ? resolve() : reject(new Error(event.data.error));
        };
        registration.active!.postMessage({ type: "DOWNLOAD_AUDIO", lang }, [
          channel.port2,
        ]);
      });
      if (token === downloadGeneration.current) setDownload("done");
    } catch {
      if (token === downloadGeneration.current) setDownload("error");
    }
  };
  const status =
    player.state === "error"
      ? "unavailable"
      : player.state === "ready"
        ? "tap_play"
        : player.state === "playing"
          ? "playing"
          : player.state === "paused"
            ? "paused"
            : "ready";
  return (
    <section aria-label={t("audio.title")} className="audio-player">
      <button
        type="button"
        className="primary listen-button"
        disabled={player.state === "loading"}
        onClick={player.state === "playing" ? player.pause : player.play}
      >
        {player.state === "playing" ? (
          <Pause aria-hidden="true" />
        ) : (
          <Volume2 aria-hidden="true" />
        )}
        {t(
          player.state === "playing"
            ? "audio.pause"
            : player.state === "paused"
              ? "audio.resume"
              : "farmer.listen",
        )}
      </button>
      <p
        className="audio-status"
        role={player.state === "error" ? "alert" : "status"}
        aria-live="polite"
      >
        {player.state === "loading" ? t("audio.loading") : t(`audio.${status}`)}
      </p>
      <details className="player-options">
        <summary>{t("farmer.more")}</summary>
        <div className="stack">
          <label>
            {t("audio.title")}
            <select
              value={section}
              onChange={(e) => {
                player.stop();
                setSection(e.target.value as Section);
              }}
            >
              {(
                [
                  "diagnosis",
                  "symptoms",
                  "treatment",
                  "prevention",
                ] as Section[]
              ).map((s) => (
                <option key={s} value={s}>
                  {t(`audio.section_${s}`)}
                </option>
              ))}
            </select>
          </label>
          <div className="button-row">
            <button className="secondary" onClick={player.stop}>
              <Square aria-hidden="true" />
              {t("audio.stop")}
            </button>
            <button className="secondary" onClick={player.replay}>
              <RotateCcw aria-hidden="true" />
              {t("audio.replay")}
            </button>
          </div>
          <label>
            {t("audio.speed")}
            <select
              value={player.speed}
              onChange={(e) => player.changeSpeed(Number(e.target.value))}
            >
              {[0.75, 1, 1.25].map((speed) => (
                <option key={speed} value={speed}>
                  {speed}
                  {tr("ui.s_11f6ad8ec5")}
                </option>
              ))}
            </select>
          </label>
          <button
            className="secondary"
            disabled={download === "loading"}
            onClick={() => void downloadAudio()}
          >
            <Download aria-hidden="true" />
            {t("audio.download")}
          </button>
          {download !== "idle" && (
            <p role="status">
              {t(
                download === "loading"
                  ? "audio.loading"
                  : download === "done"
                    ? "audio.downloaded"
                    : "audio.download_error",
              )}
            </p>
          )}
        </div>
      </details>
    </section>
  );
};
