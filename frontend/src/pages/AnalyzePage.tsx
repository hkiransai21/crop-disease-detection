import React, { lazy, Suspense, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { CloudSun, ScanLine, Leaf } from "lucide-react";
import { api } from "../api/client";
import { ImageUploader } from "../components/ImageUploader";
import { AnalysisResponse } from "../types";
import { Loading, Retry, useOnline } from "../ui/primitives";
const LocationSelector = lazy(() =>
  import("../components/LocationSelector").then((m) => ({
    default: m.LocationSelector,
  })),
);
export const AnalyzePage: React.FC<{
  onAnalysisComplete: (
    result: AnalysisResponse,
    file: File,
  ) => Promise<AnalysisResponse>;
}> = ({ onAnalysisComplete }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const route = useLocation();
  const online = useOnline();
  const initial = (route.state as { file?: File; automatic?: boolean }) || {};
  const [file, setFile] = useState<File | null>(initial.file || null);
  const started = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [weather, setWeather] = useState(false);
  const [location, setLocation] = useState<{
    latitude: number | null;
    longitude: number | null;
    locationName: string | null;
    manualTemp: number | null;
    manualHumidity: number | null;
    manualRain: number | null;
  }>(() => { try { const saved = JSON.parse(localStorage.getItem('leaf_location') || 'null'); if (saved && Number.isFinite(saved.latitude) && Number.isFinite(saved.longitude) && Math.abs(saved.latitude) <= 90 && Math.abs(saved.longitude) <= 180) return saved; } catch {} return {
    latitude: null,
    longitude: null,
    locationName: null,
    manualTemp: null,
    manualHumidity: null,
    manualRain: null,
  }; });
  useEffect(() => { localStorage.setItem('leaf_location', JSON.stringify(location)); }, [location]);
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  const submit = async (selected: File | null) => {
    if (!selected || busy) return;
    if (!navigator.onLine) {
      setError(t("farmer.offline_photo"));
      return;
    }
    if (!/^image\/(jpeg|png|webp|jpg)$/.test(selected.type)) {
      setError(t("farmer.photo_error"));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const raw = await api.analyzeImage(selected, {
        latitude: location.latitude ?? undefined,
        longitude: location.longitude ?? undefined,
        location_name: location.locationName ?? undefined,
        manual_temp_c: location.manualTemp ?? undefined,
        manual_humidity_pct: location.manualHumidity ?? undefined,
        manual_rainfall_mm: location.manualRain ?? undefined,
      });
      const result = await onAnalysisComplete(raw, selected);
      if (mounted.current)
        navigate(`/result/${result.id}`, {
          state: { analysis: result },
          replace: true,
        });
    } catch (error) {
      if (mounted.current) setError(error instanceof Error ? error.message : t("farmer.error"));
    } finally {
      if (mounted.current) setBusy(false);
    }
  };
  useEffect(() => {
    if (initial.automatic && initial.file && !started.current) {
      started.current = true;
      void submit(initial.file);
    }
  }, []);
  return (
    <div className="capture-page">
      <h1>{t("farmer.photo")}</h1>
      {!online && <p className="notice">{t("farmer.offline_photo")}</p>}
      {error && <Retry message={error} onRetry={() => void submit(file)} />}
      {busy ? (
        <div className="checking" role="status" aria-live="polite">
          <Leaf aria-hidden="true" />
          <h2>{t("farmer.checking")}</h2>
          <p>{t("farmer.wait")}</p>
          <div className="skeleton" />
        </div>
      ) : (
        <>
          <ImageUploader
            selectedFile={file}
            onFileSelect={(next) => {
              setFile(next);
              setError(null);
            }}
          />
          {file && (
            <button
              className="button primary"
              disabled={!online}
              onClick={() => void submit(file)}
            >
              <ScanLine aria-hidden="true" />
              {t("farmer.check")}
            </button>
          )}
          <details
            onToggle={(e) => setWeather(e.currentTarget.open)}
            className="disclosure"
          >
            <summary>
              <CloudSun aria-hidden="true" />
              {t("farmer.weather_optional")}
            </summary>
            {weather && (
              <Suspense fallback={<Loading />}>
                <LocationSelector {...location} onChange={setLocation} />
              </Suspense>
            )}
          </details>
        </>
      )}
    </div>
  );
};
