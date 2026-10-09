"""Script to generate complete, high-quality, verified agronomic multilingual data.
Generates:
1. Curated glossaries for all 38 classes + agronomic terms in backend/app/data/i18n/glossary/{lang}.json
2. Complete 38-class localized disease databases in backend/app/data/i18n/{lang}/diseases.json
3. UI localization files in frontend/src/i18n/locales/{lang}.json
"""
import json
import os
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_I18N_DIR = BASE_DIR / "backend" / "app" / "data" / "i18n"
GLOSSARY_DIR = BACKEND_I18N_DIR / "glossary"
FRONTEND_LOCALES_DIR = BASE_DIR / "frontend" / "src" / "i18n" / "locales"

# Ensure directories exist
GLOSSARY_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_LOCALES_DIR.mkdir(parents=True, exist_ok=True)

# Load existing English diseases.yaml
with open(BASE_DIR / "backend" / "app" / "knowledge_base" / "diseases.yaml", "r", encoding="utf-8") as f:
    en_kb = yaml.safe_load(f)

print(f"Loaded {len(en_kb['diseases'])} English disease classes from diseases.yaml")
