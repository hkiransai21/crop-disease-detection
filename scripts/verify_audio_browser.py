"""Real browser playback and explicit offline-download smoke test; requires local servers."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        for lang in ('en', 'hi', 'ta', 'te', 'kn'):
            context = browser.new_context()
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            entry = json.loads((ROOT / f'backend/app/data/i18n/{lang}/diseases.json').read_text(encoding='utf-8'))['diseases'][0]
            locale = json.loads((ROOT / f'frontend/src/i18n/locales/{lang}.json').read_text(encoding='utf-8'))
            result = dict(id='guest_audio', predicted_label=entry['id'], crop=entry['crop'], disease_name=entry['disease_name'], confidence=.95, confidence_display='95%', is_uncertain=False, top_k=[], model_version='audio-smoke-test', image_url='', disease_details=entry, created_at='2026-10-16T00:00:00Z')
            page.add_init_script(f"localStorage.setItem('agrishield_language', {json.dumps(lang)}); sessionStorage.setItem('agrishield_last_analysis', {json.dumps(json.dumps(result))});")
            page.add_init_script("const OriginalAudio = window.Audio; window.Audio = function(...args) { const a = new OriginalAudio(...args); window.__audio = a; return a; };")
            page.goto('http://127.0.0.1:5173/result/guest_audio')
            player = page.get_by_role('region', name=locale['audio']['title'])
            player.wait_for()
            assert page.evaluate('caches.keys()') == [], 'Audio cached without opt-in'
            prefix = locale['audio']['listen_btn'].split('{{')[0].strip()
            player.get_by_role('button').filter(has_text=prefix).first.click()
            page.wait_for_function('window.__audio && !window.__audio.paused && window.__audio.currentTime > 0.1')
            duration = page.evaluate('window.__audio.duration')
            source = page.evaluate('window.__audio.src')
            assert '/audio/files/' in source
            player.get_by_role('button', name=locale['audio']['pause'], exact=True).click()
            assert page.evaluate('window.__audio.paused')
            player.get_by_role('button', name=locale['audio']['resume'], exact=True).click()
            page.wait_for_function('!window.__audio.paused')
            player.get_by_role('button', name=locale['audio']['stop'], exact=True).click()
            player.get_by_role('button', name=locale['audio']['download'], exact=True).click()
            player.get_by_text(locale['audio']['downloaded'], exact=True).wait_for(timeout=180000)
            keys = page.evaluate('caches.keys()')
            assert len(keys) == 1 and f'-{lang}-' in keys[0], keys
            await_control = 'navigator.serviceWorker.controller !== null'
            page.wait_for_function(await_control)
            context.set_offline(True)
            player.get_by_role('button', name=locale['audio']['replay'], exact=True).click()
            page.wait_for_function('!window.__audio.paused && window.__audio.currentTime > 0.1')
            assert not errors, errors
            print(f'{lang}: static playback {duration:.2f}s; pause/resume/stop PASS; opt-in offline replay PASS; page errors=0', flush=True)
            context.set_offline(False)
            context.close()
        browser.close()


if __name__ == '__main__':
    main()
