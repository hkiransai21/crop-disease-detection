"""Verify tutorial and uncertainty screens in every language and viewport."""
import json
from playwright.sync_api import sync_playwright
from verify_farmer_ui import ROOT,OUT,BASE,LANGS,fixture
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=True)
 rows=[]
 for width,height in [(360,640),(412,915),(768,1024)]:
  for lang in LANGS:
   for screen in ['tutorial','uncertain']:
    ctx=browser.new_context(viewport={'width':width,'height':height});page=ctx.new_page()
    data=fixture(lang);data['is_uncertain']=True;data['confidence']=.3
    init=f"localStorage.setItem('agrishield_language',{json.dumps(lang)});"
    if screen=='uncertain':init+=f"localStorage.setItem('leaf_tutorial','done');sessionStorage.setItem('agrishield_last_analysis',{json.dumps(json.dumps(data))});"
    page.add_init_script(init);page.goto(BASE+('/result/guest_ui' if screen=='uncertain' else '/'),wait_until='networkidle');page.evaluate('document.fonts.ready')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    if screen=='tutorial':
     assert page.locator('.tutorial li').count()==3
     skip=page.locator('.onboarding>.plain').bounding_box();assert skip['y']+skip['height']<=height
    else:
     assert page.locator('.uncertain').count()==1
     assert page.locator('.advice').count()==0
     assert page.locator('.audio-player').count()==0
    page.screenshot(path=str(OUT/f'{lang}-{width}-{screen}.png'))
    rows.append(dict(lang=lang,width=width,screen=screen,passed=True));ctx.close()
 browser.close()
(OUT/'supplemental-results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(f'{len(rows)} tutorial/uncertainty checks passed; no overflow; tutorial fits one screen.')
