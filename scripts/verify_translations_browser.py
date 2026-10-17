"""Capture real result UI at 360x640 for each supported language. Requires local servers."""
import json,os,sys
from urllib.parse import quote
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.services.risk import evaluate_disease_risk
from backend.app.services.i18n import localize_risk_assessment
OUT=ROOT/'docs/i18n-screenshots';OUT.mkdir(exist_ok=True)

def main():
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='msedge',headless=True)
  results=[]
  first=browser.new_context(viewport={'width':360,'height':640});page=first.new_page()
  page.goto('http://127.0.0.1:5173/')
  assert page.get_by_role('main').get_by_role('button').count()==5
  page.get_by_role('button',name='हिन्दी',exact=True).click()
  page.reload();assert page.evaluate("localStorage.getItem('agrishield_language')")=='hi'
  assert page.locator('html').get_attribute('lang')=='hi'
  page.get_by_role('button',name='ಕನ್ನಡ',exact=True).first.click()
  assert page.locator('html').get_attribute('lang')=='kn'
  first.close();print('First launch, persisted choice, one-tap change: PASS',flush=True)
  for lang in ('en','hi','ta','te','kn'):
   context=browser.new_context(viewport={'width':360,'height':640},device_scale_factor=1)
   page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
   entry=json.loads((ROOT/f'backend/app/data/i18n/{lang}/diseases.json').read_text(encoding='utf-8'))['diseases'][0]
   result=dict(id='guest_translation',language=lang,predicted_label=entry['id'],crop=entry['crop'],disease_name=entry['disease_name'],confidence=.95,confidence_display='95%',is_uncertain=False,top_k=[],model_version='ui-verification',image_url='data:image/svg+xml,'+quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 224 224"><rect width="224" height="224" fill="#ecfdf5"/><path d="M40 180Q10 35 190 25Q200 175 40 180" fill="#15803d"/><path d="M40 180L160 55" stroke="#86efac" stroke-width="4"/></svg>'),disease_details=entry,created_at='2026-10-16T00:00:00Z')
   raw=evaluate_disease_risk(entry['id'],None)
   result['risk_assessment']=localize_risk_assessment(raw,lang).model_dump()
   result['localization_source']={'confidence_display':'High Confidence','risk_assessment':raw.model_dump()}
   page.add_init_script(f"localStorage.setItem('agrishield_language',{json.dumps(lang)});sessionStorage.setItem('agrishield_last_analysis',{json.dumps(json.dumps(result))});")
   page.goto('http://127.0.0.1:5173/result/guest_translation',wait_until='networkidle')
   page.evaluate('document.fonts.ready');page.wait_for_timeout(500)
   assert page.locator('html').get_attribute('lang')==lang
   overflow=page.evaluate('''() => [...document.querySelectorAll('body *')].filter(e => {const r=e.getBoundingClientRect();return r.width>0 && (r.right>361 || r.left < -1) && getComputedStyle(e).position!=='absolute';}).map(e=>({tag:e.tagName,text:e.textContent.slice(0,70),width:e.getBoundingClientRect().width}))''')
   page.screenshot(path=str(OUT/f'{lang}-360x640.png'))
   page.screenshot(path=str(OUT/f'{lang}-full.png'),full_page=True)
   locale=json.loads((ROOT/f'frontend/src/i18n/locales/{lang}.json').read_text(encoding='utf-8'))
   page.get_by_role('heading',name=locale['result']['actions_title'],exact=True).locator('../../..').screenshot(path=str(OUT/f'{lang}-treatment.png'),style='nav.sticky { visibility: hidden; }')
   font_names=page.evaluate('Array.from(document.fonts).filter(f=>f.status === "loaded").map(f=>f.family)')
   assert not errors,errors
   assert not overflow,overflow
   if lang!='en':assert any('Noto' in name for name in font_names),font_names
   page.wait_for_function('navigator.serviceWorker.controller !== null')
   context.set_offline(True)
   fonts=page.evaluate('''async () => {const paths=['devanagari','tamil','telugu','kannada'];return Promise.all(paths.map(async s => {const r=await fetch('/fonts/noto-sans-'+s+'.woff2');return r.ok && (await r.arrayBuffer()).byteLength>1000;}));}''')
   assert all(fonts),fonts
   item={'language':lang,'viewport':'360x640','horizontal_overflow':len(overflow),'page_errors':len(errors),'fonts_loaded':font_names,'offline_fonts':all(fonts)}
   results.append(item);print(json.dumps(item),flush=True);context.close()
  browser.close()
 (OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()

