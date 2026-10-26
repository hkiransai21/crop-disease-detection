"""Production UI matrix. API results are deterministic localized fixtures; prediction is not invoked."""
import json,sys,os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/ui-screenshots';OUT.mkdir(exist_ok=True)
BASE=os.environ.get('UI_URL','http://127.0.0.1:4173')
LANGS=['en','hi','ta','te','kn']
def fixture(lang):
 entry=max(json.loads((ROOT/f'backend/app/data/i18n/{lang}/diseases.json').read_text(encoding='utf-8'))['diseases'],key=lambda d:len(d['disease_name']))
 return dict(id='guest_ui',language=lang,predicted_label=entry['id'],crop=entry['crop'],disease_name=entry['disease_name'],confidence=.95,confidence_display='95%',is_uncertain=False,top_k=[],model_version='ui-fixture',image_url='/icon.svg',disease_details=entry,created_at='2026-10-17T00:00:00Z',risk_assessment=dict(crop=entry['crop'],target_condition=entry['disease_name'],risk_score=78,risk_level='HIGH',risk_color='#B3382C',headline='',summary='',contributing_factors=[],daily_outlook=[],disclaimer=''))
def main():
 results=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='msedge',headless=True)
  for width,height in [(360,640),(412,915),(768,1024)]:
   for lang in LANGS:
    locale=json.loads((ROOT/f'frontend/src/i18n/locales/{lang}.json').read_text(encoding='utf-8'))
    context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,reduced_motion='reduce')
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    data=fixture(lang)
    page.add_init_script(f"localStorage.setItem('agrishield_language',{json.dumps(lang)});localStorage.setItem('leaf_tutorial','done');sessionStorage.setItem('agrishield_last_analysis',{json.dumps(json.dumps(data))});")
    for name,path in [('home','/'),('capture','/analyze'),('result','/result/guest_ui'),('history','/history'),('settings','/settings'),('guide','/diseases'),('account','/auth')]:
     page.goto(BASE+path,wait_until='networkidle');page.evaluate('document.fonts.ready')
     page.wait_for_timeout(100)
     if name=='result':
      page.locator('.listen-button').wait_for()
      assert page.locator('.listen-button').bounding_box()['y']+page.locator('.listen-button').bounding_box()['height']<=page.locator('.bottom-nav').bounding_box()['y'], 'Listen is below the fold'
     measurements=page.evaluate('''() => {
      const visible=e=>e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
      const elements=[...document.querySelectorAll('body *')].filter(visible);
      return {overflow:elements.filter(e=>{const r=e.getBoundingClientRect();return r.left < -1 || r.right>innerWidth+1;}).filter(e=>!e.classList.contains('sr-only')).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.slice(0,50)})),smallText:elements.filter(e=>e.childNodes.length && [...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()) && parseFloat(getComputedStyle(e).fontSize)<16).map(e=>e.tagName),smallTargets:[...document.querySelectorAll('button,summary,.nav-item')].filter(visible).filter(e=>e.getBoundingClientRect().height<55).map(e=>e.textContent),fonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)};
     }''')
     page.screenshot(path=str(OUT/f'{lang}-{width}-{name}.png'))
     results.append(dict(language=lang,width=width,screen=name,**measurements))
     if name=='result':
      page.locator('.advice-section').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Expanded advice overflow'
      page.evaluate('''() => {window.__stress=[];for(const el of document.querySelectorAll('button,summary,.nav-item')){const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);while(walker.nextNode()){const n=walker.currentNode;if(n.textContent.trim()){window.__stress.push([n,n.textContent]);n.textContent+=n.textContent.slice(0,Math.ceil(n.textContent.length*.4));}}}}''')
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), '40 percent longer label overflow'
      page.evaluate('window.__stress.forEach(([node,text])=>node.textContent=text)')
      page.screenshot(path=str(OUT/f'{lang}-{width}-advice-full.png'),full_page=True)
      page.locator('.risk-strip').screenshot(path=str(OUT/f'{lang}-{width}-weather.png'))
    print(f'{lang} {width}x{height}: 7 screens captured; overflow={sum(len(r["overflow"]) for r in results if r["language"]==lang and r["width"]==width)}; errors={len(errors)}',flush=True)
    assert not errors,errors
    context.close()
  browser.close()
 (OUT/'matrix.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 issues=[r for r in results if r['overflow'] or r['smallText'] or r['smallTargets']]
 print(f'{len(results)} screen checks; {len(issues)} layouts with issues.',flush=True)
 if issues:print(json.dumps(issues,ensure_ascii=True,indent=2));sys.exit(1)
if __name__=='__main__':main()
