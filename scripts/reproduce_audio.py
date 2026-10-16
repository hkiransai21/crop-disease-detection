"""Reproduce the original player with a saved result (no model invocation)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    for lang in ("en", "hi", "ta", "te", "kn"):
        page = browser.new_page()
        events = []
        page.on("console", lambda msg: events.append(f"console {msg.type}: {msg.text}") if msg.type in ("error", "warning") else None)
        page.on("pageerror", lambda err: events.append(str(err)))
        entry = json.loads((ROOT / f"backend/app/data/i18n/{lang}/diseases.json").read_text(encoding="utf-8"))["diseases"][0]
        result = dict(id="guest_audio", predicted_label=entry["id"], crop=entry["crop"], disease_name=entry["disease_name"], confidence=.95, confidence_display="95%", is_uncertain=False, top_k=[], model_version="audio-reproduction", image_url="", disease_details=entry, created_at="2026-10-16T00:00:00Z")
        page.add_init_script(f"localStorage.setItem('agrishield_language', {json.dumps(lang)}); sessionStorage.setItem('agrishield_last_analysis', {json.dumps(json.dumps(result))});")
        page.goto("http://127.0.0.1:5173/result/guest_audio")
        page.wait_for_timeout(1500)
        # Locale labels vary; locate the existing Listen control using its translation.
        locale = json.loads((ROOT / f"frontend/src/i18n/locales/{lang}.json").read_text(encoding="utf-8"))
        prefix = locale["audio"]["listen_btn"].split("{{")[0].strip()
        page.get_by_role("button").filter(has_text=prefix).first.click()
        page.wait_for_timeout(4000)
        print(lang, json.dumps({"events": events, "voices": page.evaluate("speechSynthesis.getVoices().map(v=>v.lang)")}, ensure_ascii=True))
        page.close()
    browser.close()
