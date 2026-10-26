import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AnalysisResponse } from '../types';
import { api } from '../api/client';
import { LocationSelector } from './LocationSelector';
import { RiskGauge } from './RiskGauge';

export function WeatherRisk({ analysis }: { analysis: AnalysisResponse }) {
  const { t, i18n } = useTranslation();
  const [risk, setRisk] = useState(analysis.risk_assessment);
  const [status, setStatus] = useState(analysis.weather_status || (risk ? 'available' : 'location_required'));
  const [busy, setBusy] = useState(false);
  const [location, setLocation] = useState({ latitude: analysis.latitude ?? null, longitude: analysis.longitude ?? null, locationName: analysis.location_name ?? null, manualTemp: null, manualHumidity: null, manualRain: null } as Parameters<typeof LocationSelector>[0]);
  useEffect(() => { setRisk(analysis.risk_assessment); setStatus(analysis.weather_status || 'location_required'); }, [analysis, i18n.language]);
  async function refresh() {
    if (location.latitude === null || location.longitude === null) { setStatus('location_required'); return; }
    setBusy(true);
    try { setRisk(await api.getRisk(analysis.predicted_label, location.latitude, location.longitude)); setStatus('available'); }
    catch { setRisk(undefined); setStatus('unavailable'); }
    finally { setBusy(false); }
  }
  return <section>
    {risk ? <RiskGauge assessment={risk} /> : <p role="status">{t(status === 'unavailable' ? 'pipeline.weather_unavailable' : status === 'available' ? 'pipeline.no_rules' : 'pipeline.location_required')}</p>}
    {status === 'manual' && <p>{t('analyze.manual_weather')}</p>}
    {!risk && <p>{t('pipeline.general_advice')}</p>}
    <details><summary>{t('analyze.location_title')}</summary>
      <p>{t('pipeline.location_reason')}</p>
      <LocationSelector {...location} onChange={(value) => { setLocation(value as typeof location); localStorage.setItem('leaf_location', JSON.stringify(value)); }} />
    </details>
    <button className="secondary" disabled={busy} onClick={() => void refresh()}>{t('farmer.retry')}</button>
  </section>;
}
