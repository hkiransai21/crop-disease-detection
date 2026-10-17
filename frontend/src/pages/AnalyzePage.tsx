import { tr } from '../i18n/i18n';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Sprout, Loader2, AlertCircle, Sparkles, ArrowRight } from 'lucide-react';
import { api } from '../api/client';
import { ImageUploader } from '../components/ImageUploader';
import { LocationSelector } from '../components/LocationSelector';
import { AnalysisResponse } from '../types';

interface AnalyzePageProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
}

export const AnalyzePage: React.FC<AnalyzePageProps> = ({ onAnalysisComplete }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [locationData, setLocationData] = useState<{
    latitude: number | null;
    longitude: number | null;
    locationName: string | null;
    manualTemp: number | null;
    manualHumidity: number | null;
    manualRain: number | null;
  }>({
    latitude: null,
    longitude: null,
    locationName: null,
    manualTemp: null,
    manualHumidity: null,
    manualRain: null,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError(t('analyze.upload_instruction'));
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await api.analyzeImage(selectedFile, {
        latitude: locationData.latitude ?? undefined,
        longitude: locationData.longitude ?? undefined,
        location_name: locationData.locationName ?? undefined,
        manual_temp_c: locationData.manualTemp ?? undefined,
        manual_humidity_pct: locationData.manualHumidity ?? undefined,
        manual_rainfall_mm: locationData.manualRain ?? undefined,
      });

      onAnalysisComplete(response);
      navigate(`/result/${response.id}`, { state: { analysis: response } });
    } catch (err: any) {
      setError(err.message || tr('ui.s_a8e0832194'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-6 space-y-6">
      <div className="space-y-1">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-brand-100 text-brand-800 text-xs font-bold uppercase tracking-wider">
          <Sprout className="w-3.5 h-3.5 text-brand-600" />
          <span>{t('app_title')}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
          {t('analyze.title')}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          {t('analyze.upload_instruction')}
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Image Uploader */}
        <ImageUploader selectedFile={selectedFile} onFileSelect={setSelectedFile} />

        {/* Location & Microclimate Selector */}
        <LocationSelector
          latitude={locationData.latitude}
          longitude={locationData.longitude}
          locationName={locationData.locationName}
          manualTemp={locationData.manualTemp}
          manualHumidity={locationData.manualHumidity}
          manualRain={locationData.manualRain}
          onChange={setLocationData}
        />

        {/* Submit CTA */}
        <button
          type="submit"
          disabled={!selectedFile || isSubmitting}
          className="w-full flex items-center justify-center space-x-2 px-6 py-4 rounded-2xl bg-brand-600 hover:bg-brand-700 text-white font-extrabold text-sm sm:text-base shadow-lg shadow-brand-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01] active:scale-98"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>{t('analyze.analyzing')}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>{t('analyze.submit_btn')}</span>
              <ArrowRight className="w-5 h-5 ml-1" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};

