import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin, Navigation, Search, Sliders, Cloud, Check, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { GeocodingResult } from '../types';

interface LocationSelectorProps {
  latitude: number | null;
  longitude: number | null;
  locationName: string | null;
  manualTemp: number | null;
  manualHumidity: number | null;
  manualRain: number | null;
  onChange: (data: {
    latitude: number | null;
    longitude: number | null;
    locationName: string | null;
    manualTemp: number | null;
    manualHumidity: number | null;
    manualRain: number | null;
  }) => void;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  latitude,
  longitude,
  locationName,
  manualTemp,
  manualHumidity,
  manualRain,
  onChange,
}) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<GeocodingResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);

  // Debounced search
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await api.geocode(searchQuery);
        setSearchResults(results);
      } catch {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleUseGps = () => {
    if (!navigator.geolocation) {
      setGeoError('GPS Geolocation is not supported by your browser.');
      return;
    }

    setIsLocating(true);
    setGeoError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLocating(false);
        onChange({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          locationName: 'My Farm (GPS Coordinates)',
          manualTemp: null,
          manualHumidity: null,
          manualRain: null,
        });
      },
      (error) => {
        setIsLocating(false);
        setGeoError(`Location access denied or unavailable (${error.message}). Please search by town or enter manually.`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const handleSelectLocation = (loc: GeocodingResult) => {
    const name = `${loc.name}${loc.admin1 ? `, ${loc.admin1}` : ''}${loc.country ? `, ${loc.country}` : ''}`;
    setSearchQuery('');
    setSearchResults([]);
    onChange({
      latitude: loc.latitude,
      longitude: loc.longitude,
      locationName: name,
      manualTemp: null,
      manualHumidity: null,
      manualRain: null,
    });
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-brand-600" />
          <h4 className="text-sm font-bold text-slate-900">{t('analyze.location_title')}</h4>
        </div>
        <button
          type="button"
          onClick={() => setShowManual(!showManual)}
          className="text-xs font-semibold text-brand-700 hover:text-brand-800 flex items-center space-x-1"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>{showManual ? t('analyze.use_gps') : t('analyze.manual_weather')}</span>
        </button>
      </div>

      {geoError && (
        <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{geoError}</span>
        </div>
      )}

      {!showManual ? (
        <div className="space-y-3">
          {/* Active location badge */}
          {latitude !== null && longitude !== null ? (
            <div className="flex items-center justify-between p-3 rounded-xl bg-brand-50 border border-brand-200 text-xs">
              <div className="flex items-center space-x-2">
                <Check className="w-4 h-4 text-brand-600" />
                <div>
                  <span className="font-bold text-brand-950">{locationName || 'Farm Location'}</span>
                  <p className="text-brand-800 text-[11px] font-mono">
                    Lat: {latitude.toFixed(3)}, Lon: {longitude.toFixed(3)}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() =>
                  onChange({
                    latitude: null,
                    longitude: null,
                    locationName: null,
                    manualTemp: null,
                    manualHumidity: null,
                    manualRain: null,
                  })
                }
                className="text-xs font-semibold text-slate-500 hover:text-rose-600"
              >
                Change
              </button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-2">
              <button
                type="button"
                onClick={handleUseGps}
                disabled={isLocating}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-brand-50 hover:bg-brand-100 border border-brand-200 text-brand-800 text-xs font-bold transition-all"
              >
                {isLocating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
                <span>{isLocating ? 'Acquiring GPS...' : t('analyze.use_gps')}</span>
              </button>

              {/* Search place input */}
              <div className="relative flex-1">
                <div className="flex items-center rounded-xl border border-slate-300 focus-within:border-brand-500 bg-slate-50 px-3 py-2">
                  <Search className="w-4 h-4 text-slate-400 mr-2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder={t('analyze.search_place')}
                    className="w-full bg-transparent text-xs text-slate-900 focus:outline-none placeholder-slate-400"
                  />
                  {isSearching && <Loader2 className="w-3.5 h-3.5 animate-spin text-slate-400" />}
                </div>

                {/* Dropdown Results */}
                {searchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-20 max-h-48 overflow-y-auto">
                    {searchResults.map((res, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSelectLocation(res)}
                        className="w-full text-left px-3 py-2 text-xs hover:bg-brand-50 border-b border-slate-100 last:border-0 flex items-center justify-between"
                      >
                        <span className="font-medium text-slate-800 truncate">
                          {res.name}{res.admin1 ? `, ${res.admin1}` : ''}{res.country ? `, ${res.country}` : ''}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono shrink-0 ml-2">
                          {res.latitude.toFixed(1)}, {res.longitude.toFixed(1)}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Manual Weather Input */
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">{t('analyze.temp_label')}</label>
            <input
              type="number"
              placeholder="e.g. 24"
              value={manualTemp ?? ''}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: 'Manual Weather Entry',
                  manualTemp: e.target.value ? parseFloat(e.target.value) : null,
                  manualHumidity,
                  manualRain,
                })
              }
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">{t('analyze.humidity_label')}</label>
            <input
              type="number"
              placeholder="e.g. 85"
              value={manualHumidity ?? ''}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: 'Manual Weather Entry',
                  manualTemp,
                  manualHumidity: e.target.value ? parseFloat(e.target.value) : null,
                  manualRain,
                })
              }
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">{t('analyze.rainfall_label')}</label>
            <input
              type="number"
              placeholder="e.g. 15"
              value={manualRain ?? ''}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: 'Manual Weather Entry',
                  manualTemp,
                  manualHumidity,
                  manualRain: e.target.value ? parseFloat(e.target.value) : null,
                })
              }
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};
