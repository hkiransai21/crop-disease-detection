import { tr } from "../i18n/i18n";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  MapPin,
  Navigation,
  Search,
  Sliders,
  Cloud,
  Check,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { api } from "../api/client";
import { GeocodingResult } from "../types";

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
  const [searchQuery, setSearchQuery] = useState("");
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
      setGeoError(tr("ui.s_f3e1416adb"));
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
          locationName: tr("ui.s_1a5712e514"),
          manualTemp: null,
          manualHumidity: null,
          manualRain: null,
        });
      },
      (error) => {
        setIsLocating(false);
        setGeoError(tr("location.unavailable"));
      },
      { timeout: 10000, enableHighAccuracy: true },
    );
  };

  const handleSelectLocation = (loc: GeocodingResult) => {
    const name = `${loc.name}${loc.admin1 ? `, ${loc.admin1}` : ""}${loc.country ? `, ${loc.country}` : ""}`;
    setSearchQuery("");
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
    <div>
      <p>{t('pipeline.location_reason')}</p>
      <div>
        <div>
          <MapPin />
          <h2>{t("analyze.location_title")}</h2>
        </div>
        <button type="button" onClick={() => setShowManual(!showManual)}>
          <Sliders />
          <span>
            {showManual ? t("analyze.use_gps") : t("analyze.manual_weather")}
          </span>
        </button>
      </div>

      {geoError && (
        <div>
          <AlertCircle />
          <span>{geoError}</span>
        </div>
      )}

      {!showManual ? (
        <div>
          {/* Active location badge */}
          {latitude !== null && longitude !== null ? (
            <div>
              <div>
                <Check />
                <div>
                  <span>{locationName || tr("ui.s_9786edfe4c")}</span>
                  <p>
                    {tr("ui.s_46cc95041a")}
                    {latitude.toFixed(3)}
                    {tr("ui.s_ad72300a9f")}
                    {longitude.toFixed(3)}
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
              >
                {tr("ui.s_64fbd995d3")}
              </button>
            </div>
          ) : (
            <div>
              <button
                type="button"
                onClick={handleUseGps}
                disabled={isLocating}
              >
                {isLocating ? <Loader2 /> : <Navigation />}
                <span>
                  {isLocating ? tr("ui.s_aa9d35245b") : t("analyze.use_gps")}
                </span>
              </button>

              {/* Search place input */}
              <div>
                <div>
                  <Search />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder={t("analyze.search_place")}
                    aria-label={t("analyze.search_place")}
                  />
                  {isSearching && <Loader2 />}
                </div>

                {/* Dropdown Results */}
                {searchResults.length > 0 && (
                  <div>
                    {searchResults.map((res, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSelectLocation(res)}
                      >
                        <span>
                          {res.name}
                          {res.admin1 ? `, ${res.admin1}` : ""}
                          {res.country ? `, ${res.country}` : ""}
                        </span>
                        <span>
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
        <div>
          <div>
            <label htmlFor="weather-temperature">
              {t("analyze.temp_label")}
            </label>
            <input
              type="number"
              placeholder={tr("ui.s_77026bd31e")}
              id="weather-temperature"
              value={manualTemp ?? ""}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: tr("ui.s_e6465317e1"),
                  manualTemp: e.target.value
                    ? parseFloat(e.target.value)
                    : null,
                  manualHumidity,
                  manualRain,
                })
              }
            />
          </div>

          <div>
            <label htmlFor="weather-humidity">
              {t("analyze.humidity_label")}
            </label>
            <input
              type="number"
              placeholder={tr("ui.s_873c3e53aa")}
              id="weather-humidity"
              value={manualHumidity ?? ""}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: tr("ui.s_e6465317e1"),
                  manualTemp,
                  manualHumidity: e.target.value
                    ? parseFloat(e.target.value)
                    : null,
                  manualRain,
                })
              }
            />
          </div>

          <div>
            <label htmlFor="weather-rain">{t("analyze.rainfall_label")}</label>
            <input
              type="number"
              placeholder={tr("ui.s_3cfcdb32cc")}
              id="weather-rain"
              value={manualRain ?? ""}
              onChange={(e) =>
                onChange({
                  latitude: null,
                  longitude: null,
                  locationName: tr("ui.s_e6465317e1"),
                  manualTemp,
                  manualHumidity,
                  manualRain: e.target.value
                    ? parseFloat(e.target.value)
                    : null,
                })
              }
            />
          </div>
        </div>
      )}
    </div>
  );
};
