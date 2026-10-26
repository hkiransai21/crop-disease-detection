import React from 'react';
import { beforeEach, afterEach, expect, it, vi } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ResultPage } from '../src/pages/ResultPage';
import { RiskGauge } from '../src/components/RiskGauge';
import { WeatherRisk } from '../src/components/WeatherRisk';
import { fireEvent } from '@testing-library/react';
import { api } from '../src/api/client';
import { AnalysisResponse, RiskAssessment } from '../src/types';
import i18n from '../src/i18n/i18n';
import catalog from '../../backend/app/data/i18n/en/diseases.json';
import { getCheck, saveCheck } from '../src/storage/checks';

vi.mock('../src/storage/checks', () => ({getCheck: vi.fn(), saveCheck: vi.fn().mockResolvedValue({})}));
vi.mock('../src/components/AudioNarrator', () => ({AudioNarrator: () => null}));
vi.mock('../src/hooks/useAudio', () => ({useAudio: () => ({state:'idle', play: vi.fn(), pause: vi.fn()})}));
beforeEach(async () => { await i18n.changeLanguage('en'); vi.mocked(getCheck).mockResolvedValue(undefined); vi.mocked(saveCheck).mockResolvedValue({} as any); });
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const result = (index: number, uncertain=false) => {
  const d = catalog.diseases[index];
  return {id:'guest_test', language:'en', predicted_label:d.id, crop:d.crop, disease_name:d.disease_name, confidence:0.92,
    is_uncertain:uncertain, image_url:'', disease_details:d, weather_status:'location_required',
    top_k:catalog.diseases.slice(index,index+3).map((x,i) => ({class_id:x.id,crop:x.crop,disease_name:x.disease_name,confidence:0.9-i*0.4, confidence_percentage:90-i*40}))} as unknown as AnalysisResponse;
};
function show(value: AnalysisResponse) {
  return render(<MemoryRouter initialEntries={[{pathname:'/result/guest_test', state:{analysis:value}}]}><Routes>
    <Route path='/result/:id' element={<ResultPage lastAnalysis={value}/>}/></Routes></MemoryRouter>);
}
it.each([0,1,2])('renders class-specific symptoms and treatment for response %s', async index => {
  const value=result(index); show(value);
  expect(await screen.findByText(value.disease_details!.symptoms)).toBeInTheDocument();
  expect(screen.getAllByText(value.disease_details!.organic_controls[0]).length).toBeGreaterThan(0);
});
it('fresh navigation wins over an old saved language variant', async () => {
  const stale=result(0), fresh=result(1);
  vi.mocked(getCheck).mockResolvedValue({id:stale.id,result:stale,variants:{en:stale}});
  show(fresh);
  expect(await screen.findByText(fresh.disease_details!.symptoms)).toBeInTheDocument();
  expect(screen.queryByText(stale.disease_details!.symptoms)).not.toBeInTheDocument();
});
it('uncertainty retains three possibilities without treatment', async () => {
  const value=result(0,true); show(value);
  expect(await screen.findByRole('heading',{name:i18n.t('pipeline.possibilities')})).toBeInTheDocument();
  for(const p of value.top_k) expect(screen.getByText(new RegExp(p.disease_name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')))).toBeInTheDocument();
  expect(screen.queryByText(value.disease_details!.symptoms)).not.toBeInTheDocument();
});
it('displays score and measured risk reasons', () => {
  const risk={risk_level:'HIGH',risk_score:87,headline:'Late blight weather',summary:'Cool and wet',contributing_factors:[{explanation:'Humidity 92%; rain 18 mm'}],disclaimer:'Estimate'} as RiskAssessment;
  render(<MemoryRouter><RiskGauge assessment={risk}/></MemoryRouter>);
  expect(screen.getByText('87 / 100')).toBeInTheDocument();
  expect(screen.getByText('Humidity 92%; rain 18 mm')).toBeInTheDocument();
});
it('analysis sends each fresh image with no-store', async () => {
  const first=new File(['first'],'first.jpg',{type:'image/jpeg'}), second=new File(['second'],'second.jpg',{type:'image/jpeg'});
  vi.spyOn(api,'downscaleImage').mockImplementation(async file => file);
  const fetchMock=vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:true,status:200,json:async()=>result(0)} as Response);
  await api.analyzeImage(first); await api.analyzeImage(second);
  expect(fetchMock.mock.calls.map(x=>x[1]?.cache)).toEqual(['no-store','no-store']);
  expect(((fetchMock.mock.calls[0][1]?.body as FormData).get('image') as File).name).toBe('first.jpg');
  expect(((fetchMock.mock.calls[1][1]?.body as FormData).get('image') as File).name).toBe('second.jpg');
});
it('weather failure has no score and retry uses the selected coordinates', async () => {
  const value={...result(0),latitude:12,longitude:77,weather_status:'unavailable' as const};
  const request=vi.spyOn(api,'getRisk').mockResolvedValue({risk_level:'LOW',risk_score:12,headline:'Low risk',summary:'Dry',contributing_factors:[],daily_outlook:[]} as unknown as RiskAssessment);
  render(<MemoryRouter><WeatherRisk analysis={value}/></MemoryRouter>);
  expect(screen.getByText(i18n.t('pipeline.weather_unavailable'))).toBeInTheDocument();
  expect(screen.queryByText(/\/ 100/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:i18n.t('farmer.retry')}));
  expect(await screen.findByText('12 / 100')).toBeInTheDocument();
  expect(request).toHaveBeenCalledWith(value.predicted_label,12,77);
});
