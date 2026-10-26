"""Regressions for repeated advice, silent defaults and fabricated weather."""
import pytest
import httpx
from backend.app.services.i18n import load_localized_knowledge_base, get_localized_disease_entry
from backend.app.services.risk import evaluate_disease_risk
from backend.app.services import weather
from backend.app.ml import inference
from PIL import Image
import json
from pathlib import Path
from backend.tests.weather_scenarios import SCENARIOS, raw_weather
from backend.app.services.i18n import localize_risk_assessment


@pytest.mark.parametrize('lang', ['en', 'hi', 'ta', 'te', 'kn'])
@pytest.mark.parametrize('field', ['symptoms', 'immediate_actions', 'organic_controls', 'prevention_steps'])
def test_distinct_content(lang, field):
    entries = load_localized_knowledge_base(lang)
    assert len(entries) == 38
    values = [str(getattr(d, field)).strip() for d in entries.values()]
    assert len(set(values)) == 38
    assert all(v and v != '[]' and 'lorem' not in v.lower() and 'TBD' not in v for v in values)


def test_unknown_key_is_not_a_default():
    with pytest.raises(KeyError):
        get_localized_disease_entry('unknown')
    with pytest.raises(KeyError):
        evaluate_disease_risk('unknown')


def test_no_weather_is_not_a_risk_score():
    assert evaluate_disease_risk('Tomato___Late_blight', None) is None


def test_no_model_is_not_random_advice(monkeypatch):
    monkeypatch.setattr(inference, '_ORT_SESSION', None)
    with pytest.raises(RuntimeError):
        inference.predict_disease(Image.new('RGB', (224,224)))


@pytest.mark.asyncio
async def test_api_failure_does_not_fabricate_weather(monkeypatch):
    weather._WEATHER_CACHE.clear()
    async def fail(*args, **kwargs):
        raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx.AsyncClient, 'get', fail)
    with pytest.raises(httpx.ConnectError):
        await weather.fetch_weather_summary(12, 77)


@pytest.mark.parametrize('scenario', SCENARIOS, ids=[x[0] for x in SCENARIOS])
@pytest.mark.parametrize('lang', ['en','hi','ta','te','kn'])
def test_weather_reasons_include_actual_measurements(scenario, lang):
    name, temp, humidity, rain, wind, lat, lon = scenario
    summary = weather._parse_open_meteo_response(raw_weather(temp, humidity, rain, wind))
    risk = localize_risk_assessment(evaluate_disease_risk('Tomato___Late_blight', summary), lang)
    assert len(risk.contributing_factors) == 3
    text = ' '.join(x.explanation for x in risk.contributing_factors)
    assert str(float(temp)) in text and str(float(humidity)) in text
    assert str(summary.past_72h_rain_mm) in text
    if lang != 'en':
        assert 'Forecast:' not in text and 'Rain:' not in text and 'Forecast wind:' not in text


def test_weather_and_class_change_scores():
    results = {}
    for name,t,h,r,w,lat,lon in SCENARIOS:
        summary = weather._parse_open_meteo_response(raw_weather(t,h,r,w))
        results[name] = [evaluate_disease_risk(key, summary) for key in ('Tomato___Late_blight','Tomato___Spider_mites Two-spotted_spider_mite','Tomato___Bacterial_spot')]
    assert results['cool_humid'][0].risk_score > results['hot_dry'][0].risk_score
    assert results['hot_dry'][1].risk_score > results['cool_humid'][1].risk_score
    assert results['warm_rain'][2].risk_score > results['low_risk'][2].risk_score
    assert len({r.risk_level for row in results.values() for r in row}) >= 3


def test_wind_changes_wind_dispersed_disease():
    calm = weather._parse_open_meteo_response(raw_weather(23,75,0,2))
    windy = weather._parse_open_meteo_response(raw_weather(23,75,0,30))
    assert evaluate_disease_risk('Apple___Apple_scab', windy).risk_score > evaluate_disease_risk('Apple___Apple_scab', calm).risk_score


@pytest.mark.asyncio
@pytest.mark.parametrize('filename', ['sample_leaf_diseased.jpg','sample_leaf_healthy.jpg'])
async def test_real_onnx_output_unchanged_and_reaches_response(client, filename):
    inference.load_inference_artifacts()
    baseline = next(x for x in json.loads(Path('docs/bug-evidence/before/images.json').read_text(encoding='utf-8')) if x['image']==filename)
    p=Path('backend/tests/fixtures/leaves')/filename
    import numpy as np
    tensor=inference.preprocess_image(Image.open(p).convert('RGB'))
    actual=inference._ORT_SESSION.run(None,{inference._ORT_SESSION.get_inputs()[0].name:tensor})[0][0]
    np.testing.assert_array_equal(actual,np.array(baseline['logits'],dtype=np.float32))
    response=await client.post('/api/v1/analyze',files={'image':(filename,p.read_bytes(),'image/jpeg')})
    assert response.status_code==200
    data=response.json()
    assert data['predicted_label']==baseline['prediction']['predicted_label']==data['disease_details']['id']
    assert data['risk_assessment'] is None and data['weather_status']=='location_required'
    assert response.headers['cache-control']=='no-store'


@pytest.mark.asyncio
async def test_weather_failure_preserves_diagnosis(client, monkeypatch):
    from backend.app.api.routes import analyze
    async def fail(*a): raise httpx.ConnectError('offline')
    monkeypatch.setattr(analyze,'fetch_weather_summary',fail)
    inference.load_inference_artifacts()
    p=Path('backend/tests/fixtures/leaves/sample_leaf_healthy.jpg')
    r=await client.post('/api/v1/analyze',files={'image':(p.name,p.read_bytes(),'image/jpeg')},data={'latitude':12,'longitude':77})
    assert r.status_code==200
    assert r.json()['disease_details']
    assert r.json()['weather_status']=='unavailable'
    assert r.json()['risk_assessment'] is None


@pytest.mark.asyncio
@pytest.mark.parametrize('key', ['Apple___Apple_scab','Apple___healthy','Potato___Late_blight','Tomato___Bacterial_spot','Squash___Powdery_mildew','Grape___Black_rot'])
async def test_controlled_logits_reach_class_specific_api_content(client,monkeypatch,key):
    """Mapping contract, NOT an accuracy claim: inject six known ONNX output vectors."""
    import numpy as np
    from types import SimpleNamespace
    inference.load_inference_artifacts()
    labels=inference._LABELS
    class Session:
        def get_inputs(self):return [SimpleNamespace(name='input')]
        def run(self,*args):
            logits=np.full((1,len(labels)),-10,dtype=np.float32)
            logits[0,labels.index(key)]=10
            return [logits]
    monkeypatch.setattr(inference,'_ORT_SESSION',Session())
    p=Path('backend/tests/fixtures/leaves/sample_leaf_healthy.jpg')
    response=await client.post('/api/v1/analyze',files={'image':(p.name,p.read_bytes(),'image/jpeg')})
    assert response.status_code==200
    data=response.json()
    assert data['predicted_label']==key==data['disease_details']['id']==data['top_k'][0]['class_id']
    assert data['disease_details']['symptoms']==get_localized_disease_entry(key).symptoms
    assert not data['is_uncertain']
