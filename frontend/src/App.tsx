import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { ResultPage } from './pages/ResultPage';
import { HistoryPage } from './pages/HistoryPage';
import { AuthPage } from './pages/AuthPage';
import { DiseasesPage } from './pages/DiseasesPage';
import { AboutPage } from './pages/AboutPage';
import { api } from './api/client';
import { User, AnalysisResponse } from './types';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisResponse | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      api
        .getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          api.logout();
          setUser(null);
        })
        .finally(() => setIsInitializing(false));
    } else {
      setIsInitializing(false);
    }
  }, []);

  const handleLogout = () => {
    api.logout();
    setUser(null);
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-brand-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-brand-500 selection:text-white">
      <Navbar user={user} onLogout={handleLogout} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route
            path="/analyze"
            element={<AnalyzePage onAnalysisComplete={setLastAnalysis} />}
          />
          <Route
            path="/result/:id"
            element={<ResultPage lastAnalysis={lastAnalysis} />}
          />
          <Route
            path="/history"
            element={<HistoryPage user={user} />}
          />
          <Route
            path="/diseases"
            element={<DiseasesPage />}
          />
          <Route
            path="/about"
            element={<AboutPage />}
          />
          <Route
            path="/auth"
            element={<AuthPage onLoginSuccess={setUser} />}
          />
        </Routes>
      </main>

      <footer className="bg-white border-t border-slate-200 py-8 text-center text-xs text-slate-500 space-y-2">
        <div className="max-w-7xl mx-auto px-4">
          <p className="font-semibold text-slate-700">
            AgriShield AI &bull; AI Crop Disease Detection & Outbreak Risk Prediction System
          </p>
          <p className="text-[11px] text-slate-400 max-w-2xl mx-auto mt-1">
            Advisory decision-support tool. Always consult your regional agricultural extension officer before applying chemical crop protectants.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
