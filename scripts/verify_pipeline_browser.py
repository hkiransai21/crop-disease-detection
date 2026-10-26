"""Real two-image browser trace plus explicitly mocked three-class rendering regression."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/bug-evidence/browser'
BASE='http://127.0.0.1:5173'


def wait(url):
    for _ in range(60):
        try:
            urllib.request.urlopen(url,timeout=1);return
        except Exception:time.sleep(.5)
    raise RuntimeError('Server failed to start: '+url)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'DEBUG':'false'}
    logs=[(OUT/'backend.log').open('w'),(OUT/'frontend.log').open('w')]
    procs=[]
    results=[]
    try:
        procs.append(subprocess.Popen([str(ROOT/'.venv/Scripts/python.exe'),'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000'],cwd=ROOT,env=env,stdout=logs[0],stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW))
        procs.append(subprocess.Popen(['node',str(ROOT/'frontend/node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5173','--strictPort'],cwd=ROOT/'frontend',env=env,stdout=logs[1],stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW))
        wait('http://127.0.0.1:8000/api/v1/health');wait(BASE)
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='msedge',headless=True)
            context=browser.new_context(viewport={'width':900,'height':900})
            context.add_init_script("localStorage.setItem('agrishield_language','en');localStorage.setItem('leaf_tutorial','done');")
            page=context.new_page()
            async_errors=[];page.on('pageerror',lambda e:async_errors.append(str(e)))
            def upload(path):
                page.goto(BASE+'/analyze')
                page.locator('input[type=file]').first.set_input_files(str(path))
                with page.expect_response(lambda r:'/api/v1/analyze' in r.url and r.request.method=='POST') as response:
                    page.get_by_role('button',name='Check this leaf',exact=True).click()
                data=response.value.json()
                page.wait_for_url('**/result/**')
                page.get_by_role('heading',name='Top three possibilities').wait_for()
                return data
            for path in sorted((ROOT/'backend/tests/fixtures/leaves').glob('*.jpg')):
                data=upload(path)
                assert len(data['top_k'])==3
                for candidate in data['top_k']:
                    assert candidate['disease_name'] in page.locator('article').inner_text()
                page.locator('.advice-section').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
                if not data['is_uncertain']:
                    assert data['disease_details']['symptoms'] in page.locator('article').inner_text()
                page.screenshot(path=str(OUT/(path.stem+'.png')),full_page=True)
                results.append({'mode':'real ONNX via browser downscaler','image':path.name,'response':data,'ui':page.locator('article').inner_text()})
            assert len({x['response']['image_sha256'] for x in results})==2
            # Controlled API responses isolate UI wiring from model correctness.
            base=copy.deepcopy(results[-1]['response'])
            entries=json.loads((ROOT/'backend/app/data/i18n/en/diseases.json').read_text(encoding='utf-8'))['diseases']
            current={}
            page.route('**/api/v1/analyze',lambda route:route.fulfill(json=current))
            for index in range(3):
                entry=entries[index]
                current=copy.deepcopy(base)
                current.update(id=f'guest_browser_{index}',predicted_label=entry['id'],canonical_key=entry['id'],crop=entry['crop'],disease_name=entry['disease_name'],disease_details=entry,is_uncertain=False,scientific_name=entry['scientific_name'],confidence=.95)
                current['top_k']=[dict(class_id=d['id'],crop=d['crop'],disease_name=d['disease_name'],confidence=.95 if i==0 else .02,confidence_percentage=95 if i==0 else 2,is_healthy=d['is_healthy']) for i,d in enumerate(entries[index:index+3])]
                upload(ROOT/'backend/tests/fixtures/leaves/sample_leaf_healthy.jpg')
                page.locator('.advice-section').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
                body=page.locator('article').inner_text()
                assert entry['symptoms'] in body and entry['organic_controls'][0] in body
                page.screenshot(path=str(OUT/f'mocked-class-{index}.png'),full_page=True)
                results.append({'mode':'MOCKED class response, same sample image','class':entry['id'],'ui':body})
            assert len({x['ui'] for x in results if x['mode'].startswith('MOCKED')})==3
            # All five language transitions use the real localization endpoint.
            page.unroute('**/api/v1/analyze')
            for lang in ('hi','ta','te','kn'):
                context.add_init_script(f"localStorage.setItem('agrishield_language','{lang}');")
                page.reload();page.locator('.advice-section').first.wait_for()
                localized=json.loads((ROOT/f'backend/app/data/i18n/{lang}/diseases.json').read_text(encoding='utf-8'))['diseases'][2]
                page.locator('.advice-section').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
                assert localized['symptoms'] in page.locator('article').inner_text()
                page.screenshot(path=str(OUT/f'localized-{lang}.png'),full_page=True)
            assert not async_errors,async_errors
            browser.close()
        (OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
        print('PASS: 2 real uploads; 3 explicitly mocked class responses; 4 language transitions; 9 screenshots')
    finally:
        for proc in reversed(procs):proc.terminate();proc.wait(timeout=15)
        for log in logs:log.close()


if __name__=='__main__':main()
