import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { AlertCircle, RefreshCw, Leaf } from "lucide-react";
export function LeafDrawing() {
  return (
    <svg
      className="leaf-drawing"
      viewBox="0 0 280 170"
      fill="none"
      aria-hidden="true"
    >
      <path d="M20 150H260M34 160H242" stroke="currentColor" opacity=".3" />
      <path
        d="M100 145C45 104 74 38 211 19C224 112 169 156 100 145Z"
        fill="#DCE8D6"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        d="M87 160L190 40M112 128L102 78M139 98L191 89M159 76L153 42"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <circle cx="242" cy="34" r="15" stroke="currentColor" strokeWidth="2" />
      <path
        d="M242 10V3M242 58V65M218 34H211M266 34H273"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}
export function Loading() {
  const { t } = useTranslation();
  return (
    <div className="loading-state" role="status">
      <Leaf aria-hidden="true" />
      <p>{t("farmer.loading")}</p>
      <div className="skeleton" />
      <div className="skeleton short" />
    </div>
  );
}
export function Retry({
  onRetry,
  message,
}: {
  onRetry: () => void;
  message?: string;
}) {
  const { t } = useTranslation();
  return (
    <div className="notice danger" role="alert">
      <AlertCircle aria-hidden="true" />
      <p>{message || t("farmer.error")}</p>
      <button className="button secondary" onClick={onRetry}>
        <RefreshCw aria-hidden="true" />
        {t("farmer.retry")}
      </button>
    </div>
  );
}
export function useOnline() {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const update = () => setOnline(navigator.onLine);
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);
  return online;
}
export function usePhoto(blob?: Blob, fallback?: string) {
  const [url, setUrl] = useState(fallback);
  useEffect(() => {
    if (!blob) {
      setUrl(fallback);
      return;
    }
    const value = URL.createObjectURL(blob);
    setUrl(value);
    return () => URL.revokeObjectURL(value);
  }, [blob, fallback]);
  return url;
}
