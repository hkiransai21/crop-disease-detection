"""Capture five explicitly MOCKED weather scenarios plus an optional live request."""
import asyncio
import json
from pathlib import Path
from unittest.mock import patch
import httpx
from backend.tests.weather_scenarios import SCENARIOS, raw_weather
from backend.app.services.weather import fetch_weather_summary, _WEATHER_CACHE
from backend.app.services.risk import evaluate_disease_risk
from backend.app.services.i18n import localize_risk_assessment


async def main():
    out=Path('docs/bug-evidence/after');out.mkdir(parents=True,exist_ok=True)
    records=[]
    for name,t,h,r,w,lat,lon in SCENARIOS:
        raw=raw_weather(t,h,r,w)
        record={'scenario':name,'source':'MOCKED controlled weather, not observed weather','coordinates':[lat,lon], 'raw_response':raw}
        async def get(self,url,params):
            request=httpx.Request('GET',url,params=params);record['request_url']=str(request.url)
            return httpx.Response(200,json=raw,request=request)
        _WEATHER_CACHE.clear()
        with patch.object(httpx.AsyncClient,'get',get): summary=await fetch_weather_summary(lat,lon)
        record['summary']=summary.model_dump()
        record['results']={key:{lang:localize_risk_assessment(evaluate_disease_risk(key,summary),lang).model_dump() for lang in ('en','hi','ta','te','kn')} for key in ('Tomato___Late_blight','Tomato___Bacterial_spot','Tomato___Spider_mites Two-spotted_spider_mite','Squash___Powdery_mildew')}
        records.append(record)
    (out/'weather-scenarios.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in records: print(row['scenario'], {k:v['en']['risk_score'] for k,v in row['results'].items()})


if __name__=='__main__':asyncio.run(main())
