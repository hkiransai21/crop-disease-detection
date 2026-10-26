import React, { lazy, Suspense, useEffect, useState } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Navbar, BottomNav } from "./components/Navbar";
import { LanguageChoice } from "./components/LanguageChoice";
import { LandingPage } from "./pages/LandingPage";
import { Loading } from "./ui/primitives";
import { api } from "./api/client";
import { User, AnalysisResponse } from "./types";
import { saveCheck } from "./storage/checks";
const AnalyzePage = lazy(() =>
  import("./pages/AnalyzePage").then((m) => ({ default: m.AnalyzePage })),
);
const ResultPage = lazy(() =>
  import("./pages/ResultPage").then((m) => ({ default: m.ResultPage })),
);
const HistoryPage = lazy(() =>
  import("./pages/HistoryPage").then((m) => ({ default: m.HistoryPage })),
);
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const AuthPage = lazy(() =>
  import("./pages/AuthPage").then((m) => ({ default: m.AuthPage })),
);
const DiseasesPage = lazy(() =>
  import("./pages/DiseasesPage").then((m) => ({ default: m.DiseasesPage })),
);
const AboutPage = lazy(() =>
  import("./pages/AboutPage").then((m) => ({ default: m.AboutPage })),
);
export const App: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [user, setUser] = useState<User | null>(null);
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisResponse | null>(
    null,
  );
  const [saveError, setSaveError] = useState(false);
  const route = useLocation();
  useEffect(() => {
    if (api.getToken())
      void api
        .getMe()
        .then(setUser)
        .catch(() => {});
  }, []);
  useEffect(() => {
    document.documentElement.dataset.contrast =
      localStorage.getItem("leaf_contrast") || "normal";
  }, []);
  useEffect(() => {
    window.scrollTo(0, 0);
    document.getElementById("main")?.focus({ preventScroll: true });
  }, [route.pathname]);
  useEffect(() => {
    document.title = t("farmer.brand");
    document.documentElement.lang = i18n.language;
  }, [i18n.language, t]);
  const complete = async (response: AnalysisResponse, file: File) => {
    const result = {
      ...response,
      id: response.id.startsWith("guest_")
        ? `guest_${crypto.randomUUID()}`
        : response.id,
    };
    setLastAnalysis(result);
    setSaveError(false);
    try {
      sessionStorage.setItem(
        "agrishield_last_analysis",
        JSON.stringify(result),
      );
      const photo = await api.downscaleImage(file, 480);
      await saveCheck(result, photo);
    } catch {
      setSaveError(true);
    }
    return result;
  };
  return (
    <LanguageChoice>
      <Navbar />
      <main id="main" tabIndex={-1} className="page-shell">
        {saveError && (
          <p className="notice" role="status">
            {t("farmer.not_saved")}
          </p>
        )}
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/analyze"
              element={<AnalyzePage onAnalysisComplete={complete} />}
            />
            <Route
              path="/result/:id"
              element={<ResultPage lastAnalysis={lastAnalysis} />}
            />
            <Route path="/history" element={<HistoryPage user={user} />} />
            <Route
              path="/settings"
              element={
                <SettingsPage
                  user={user}
                  onLogout={() => {
                    api.logout();
                    setUser(null);
                  }}
                />
              }
            />
            <Route
              path="/auth"
              element={<AuthPage onLoginSuccess={setUser} />}
            />
            <Route path="/diseases" element={<DiseasesPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<LandingPage />} />
          </Routes>
        </Suspense>
      </main>
      <BottomNav />
    </LanguageChoice>
  );
};
export default App;
