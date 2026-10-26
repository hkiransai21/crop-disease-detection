"""Real browser interaction/offline checks against the production preview."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from PIL import Image
from verify_farmer_ui import ROOT,OUT,BASE,LANGS,fixture

def main():
 checks=[]
 def passed(name):checks.append(name);print('PASS '+name,flush=True)
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='msedge',headless=True)
  context=browser.new_context(viewport={'width':360,'height':640})
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('''window.__audios=[];const NativeAudio=window.Audio;window.Audio=class extends NativeAudio{constructor(...args){super(...args);window.__audios.push(this);}};''')
  page.goto(BASE,wait_until='networkidle');page.evaluate('document.fonts.ready')
  page.screenshot(path=str(OUT/'first-launch-360.png'))
  assert page.locator('.language-name').count()==5
  for i,lang in enumerate(LANGS):
   page.locator('.language-sound').nth(i).click()
   page.wait_for_function('window.__audios.length && window.__audios.at(-1).duration>0 && !window.__audios.at(-1).paused')
   assert page.evaluate('window.__audios.at(-1).error===null')
  passed('All five native language buttons play bundled audio after a tap')
  page.locator('.language-name').first.click();expect(page.locator('.tutorial')).to_be_visible()
  page.screenshot(path=str(OUT/'tutorial-360.png'))
  page.get_by_role('button',name='Skip',exact=True).click()
  page.reload();expect(page.locator('.camera-hero')).to_be_visible()
  passed('First-launch choice, skip tutorial, persisted choice on reload')
  request_bodies=[]
  def analyze(route):
   request_bodies.append(route.request.post_data_buffer)
   route.fulfill(status=200,content_type='application/json',body=json.dumps(fixture('en')))
  page.route('**/api/v1/analyze*',analyze)
  photo=ROOT/'.translation-cache/ui-leaf-fixture.jpg';Image.new('RGB',(1600,1200),(52,100,45)).save(photo)
  with page.expect_file_chooser() as chooser:page.locator('.camera-hero').click()
  chooser.value.set_files(photo)
  page.wait_for_url('**/result/guest_*');expect(page.locator('.listen-button')).to_be_visible()
  assert len(request_bodies)==1,len(request_bodies)
  image_src=page.locator('.result-photo').get_attribute('src');assert image_src.startswith('blob:')
  assert page.evaluate('document.querySelector(".result-photo").naturalWidth')<=480
  passed('Home camera gesture to result; one analysis request; local compressed thumbnail')
  page.locator('.listen-button').click();expect(page.locator('.listen-button')).to_have_text('Pause',timeout=15000)
  page.locator('.risk-strip .secondary').click();expect(page.locator('.listen-button')).to_have_text('Listen')
  expect(page.locator('.risk-strip .secondary')).to_have_text('Pause')
  page.locator('.header-language').click();expect(page.locator('.risk-strip .secondary')).to_have_text('Listen')
  page.get_by_role('dialog').get_by_role('button',name='Close',exact=True).click()
  passed('Result and weather playback coordinate; opening language choice stops playback')
  # Download is a deliberate user action. No audio cache should exist before this tap.
  assert not page.evaluate('''async()=> (await caches.keys()).some(k=>k.startsWith('agrishield-audio-v2-'))''')
  page.locator('.player-options>summary').click()
  page.get_by_role('button',name='Download audio for offline use',exact=True).click()
  locale=json.loads((ROOT/'frontend/src/i18n/locales/en.json').read_text(encoding='utf-8'))
  expect(page.get_by_text(locale['audio']['downloaded'],exact=True)).to_be_visible(timeout=180000)
  cache_names=page.evaluate('caches.keys()');assert len([k for k in cache_names if k.startswith('agrishield-audio-v2-')])==1
  passed('Audio downloads only after explicit tap, for the selected language')
  result_url=page.url
  page.wait_for_function('navigator.serviceWorker.controller!==null')
  context.set_offline(True)
  page.reload(wait_until='networkidle');expect(page.locator('.listen-button')).to_be_visible()
  page.locator('.listen-button').click();expect(page.locator('.listen-button')).to_have_text('Pause',timeout=15000)
  page.locator('.bottom-nav a[href="/history"]').click();expect(page.locator('.history-row')).to_have_count(1)
  page.reload(wait_until='networkidle');expect(page.locator('.history-row')).to_have_count(1)
  page.locator('.history-link').click();expect(page.locator('.listen-button')).to_be_visible()
  passed('Offline full reload, saved history, thumbnail, route chunks and downloaded narration')
  page.locator('.bottom-nav a[href="/analyze"]').click();expect(page.get_by_text(locale['farmer']['offline_photo'],exact=True)).to_be_visible()
  passed('Offline capture clearly explains that a new diagnosis needs a connection')
  page.locator('.bottom-nav a[href="/settings"]').click()
  page.get_by_role('button',name=locale['farmer']['contrast']).click()
  assert page.locator('html').get_attribute('data-contrast')=='high'
  page.reload();assert page.locator('html').get_attribute('data-contrast')=='high'
  page.screenshot(path=str(OUT/'high-contrast-360.png'))
  passed('High contrast persists across an offline reload')
  context.set_offline(False)
  page.locator('.bottom-nav a[href="/history"]').click();page.get_by_role('button',name='Delete',exact=True).click();expect(page.get_by_role('dialog')).to_be_visible()
  page.get_by_role('dialog').get_by_role('button',name=locale['farmer']['confirm'],exact=True).click();expect(page.locator('.history-row')).to_have_count(0)
  page.reload();expect(page.locator('.history-row')).to_have_count(0)
  passed('Deleting a local check requires confirmation and survives reload')
  assert not errors,errors
  browser.close()
 (OUT/'interaction-results.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
