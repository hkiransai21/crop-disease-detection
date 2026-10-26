"""Read-only live Open-Meteo capture; failures are retained verbatim, never replaced."""
import asyncio
import json
from pathlib import Path
from unittest.mock import patch
import httpx
from backend.app.services.weather import fetch_weather_summary, _WEATHER_CACHE


async def main():
    records=[]
    original=httpx.AsyncClient.get
    for lat,lon in [(26.9,75.8),(31.1,77.2),(13.1,80.3),(18.5,73.9),(34.1,74.8)]:
        row={'coordinates':[lat,lon]}
        async def capture(client,url,**kwargs):
            row['request_url']=str(httpx.Request('GET',url,params=kwargs.get('params')).url)
            response=await original(client,url,**kwargs)
            row['status']=response.status_code
            try:row['raw_response']=response.json()
            except ValueError:row['raw_response']=response.text
            return response
        try:
            _WEATHER_CACHE.clear()
            with patch.object(httpx.AsyncClient,'get',capture):
                row['summary']=(await fetch_weather_summary(lat,lon)).model_dump()
        except Exception as exc:row['error']=repr(exc)
        records.append(row)
    p=Path('docs/bug-evidence/after/live-weather.json')
    p.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('raw_response','summary')} for r in records],indent=2))
    if any('error' in r for r in records):raise SystemExit(1)


if __name__=='__main__':asyncio.run(main())
