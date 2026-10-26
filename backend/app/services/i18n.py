"""Presentation-only localization. Canonical prediction/risk inputs remain unchanged."""
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional
from backend.app.knowledge_base.schema import DiseaseEntry
from backend.app.schemas.i18n import LanguageConfig, SupportedLanguagesResponse
from backend.app.schemas.risk import RiskAssessment

LANGUAGES=('en','hi','ta','te','kn')
_I18N_BASE_DIR=Path(__file__).resolve().parents[1]/'data/i18n'
_CONFIG_CACHE=None
_KB_LANG_CACHE={}
_GLOSSARY_CACHE={}
UNCERTAINTY='This photo does not give a clear result. Take another photo in good light. Do not choose a pesticide from this result. Ask your local agriculture office to check the plant.'


def resolve_language(lang: Optional[str]=None, accept_language: Optional[str]=None):
    def code(value):return value.strip().lower().replace('_','-').split('-')[0]
    if lang is not None and lang.strip():
        return code(lang) if code(lang) in LANGUAGES else 'en'
    candidates=[]
    for index,part in enumerate((accept_language or '').split(',')):
        pieces=part.strip().split(';')
        try:quality=float(next((x.strip()[2:] for x in pieces[1:] if x.strip().startswith('q=')), '1'))
        except ValueError:continue
        if 0<quality<=1 and code(pieces[0]) in LANGUAGES:candidates.append((-quality,index,code(pieces[0])))
    return sorted(candidates)[0][2] if candidates else 'en'


def get_i18n_config():
    data=json.loads((_I18N_BASE_DIR/'config.json').read_text(encoding='utf-8'))
    data['supported_languages']=[x for x in data['supported_languages'] if x['code'] in LANGUAGES]
    return data


def get_supported_languages():
    return SupportedLanguagesResponse(default_language='en',languages=[LanguageConfig(**x) for x in get_i18n_config()['supported_languages']])


def load_localized_knowledge_base(lang='en'):
    lang=resolve_language(lang)
    if lang in _KB_LANG_CACHE:return _KB_LANG_CACHE[lang]
    english=json.loads((_I18N_BASE_DIR/'en/diseases.json').read_text(encoding='utf-8'))['diseases']
    path=_I18N_BASE_DIR/lang/'diseases.json'
    local={x['id']:x for x in json.loads(path.read_text(encoding='utf-8'))['diseases']} if path.exists() else {}
    entries={}
    for source in english:
        if source['id'] not in local:
            raise KeyError(f"Missing {lang} disease record: {source['id']}")
        entry=dict(source); translated=local.get(source['id'],{})
        for field in ('disease_name', 'crop', 'symptoms', 'immediate_actions', 'organic_controls', 'chemical_controls', 'prevention_steps'):
            if not translated.get(field) or isinstance(translated[field], str) and not translated[field].strip():
                raise KeyError(f"Missing {lang} {source['id']}.{field}")
        missing=[]
        for key,value in source.items():
            candidate=translated.get(key)
            if candidate is None or isinstance(candidate,str) and not candidate.strip():
                if lang!='en':missing.append(key)
            else:entry[key]=candidate
        entry['language']=lang
        entry['fallback_fields']=missing
        entries[entry['id']]=DiseaseEntry(**entry)
    _KB_LANG_CACHE[lang]=entries
    return entries


def get_localized_disease_entry(disease_id,lang='en'):
    import logging
    try:
        return load_localized_knowledge_base(lang)[canonical_class_key(disease_id)]
    except KeyError:
        logging.getLogger(__name__).error('Unknown disease class key: %r', disease_id)
        raise


def canonical_class_key(value):
    """Only exact model labels are accepted. Never guess an alias or a default."""
    if not isinstance(value, str) or value not in load_localized_knowledge_base('en'):
        raise KeyError(value)
    return value


def get_localized_glossary(lang='en'):
    lang=resolve_language(lang)
    path=_I18N_BASE_DIR/'glossary'/f'{lang}.json'
    if not path.exists():path=_I18N_BASE_DIR/'glossary/en.json'
    return json.loads(path.read_text(encoding='utf-8'))


@lru_cache(maxsize=5)
def messages(lang):
    path=_I18N_BASE_DIR/resolve_language(lang)/'messages.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def localize_name(value,lang,crop=None):
    english=load_localized_knowledge_base('en'); target=load_localized_knowledge_base(lang)
    for key,entry in english.items():
        if crop and entry.crop != crop:continue
        if value in (entry.disease_name,entry.canonical_disease_name,entry.common_name):return target[key].disease_name
        if value==entry.crop:return target[key].crop
    return value


def translate_message(value,lang='en',crop=None):
    if not isinstance(value,str) or resolve_language(lang)=='en':return value
    table=messages(lang)
    if value in table:return table[value]
    # Match presentation templates extracted from the unchanged risk/validation code.
    for source,translation in table.items():
        slots=re.findall(r'\{\{p\d+\}\}',source)
        if not slots:continue
        pattern=re.escape(source)
        for slot in slots:pattern=pattern.replace(re.escape(slot),'(.+?)',1)
        match=re.fullmatch(pattern,value)
        if match:
            for slot,captured in zip(slots,match.groups()):translation=translation.replace(slot,localize_name(captured,lang,crop))
            return translation
    return localize_name(value,lang,crop)


def localize_risk_assessment(assessment: RiskAssessment,lang='en'):
    if assessment is None:return None
    data=assessment.model_dump()
    crop=data['crop']
    if data.get('canonical_key'):
        entry = get_localized_disease_entry(data['canonical_key'], lang)
        schedule = 'Re-check in 24 hours and consult the local agriculture office.' if data['risk_score'] >= 50 else 'Re-check in 48 hours.'
        data['action'] = entry.prevention_steps[0] + ' ' + translate_message(schedule, lang)
    for key in ('crop','target_condition','headline','summary','disclaimer'):
        data[key]=translate_message(data[key],lang,crop)
    data['risk_level_label']=translate_message(data['risk_level'],lang)
    for factor in data['contributing_factors']:
        for key in ('factor_name','explanation'):factor[key]=translate_message(factor[key],lang,crop)
        factor['impact_label']=translate_message(factor['impact'],lang)
    for day in data['daily_outlook']:
        day['risk_level_label']=translate_message(day['risk_level'],lang)
        day['favorable_factors']=[translate_message(x,lang) for x in day['favorable_factors']]
    for threat in data.get('top_regional_threats') or []:
        entry=get_localized_disease_entry(threat.get('disease_id'),lang)
        for key in ('disease_name','headline','summary'):threat[key]=translate_message(threat.get(key,''),lang,crop)
        if entry:
            threat['disease_name']=entry.disease_name
            threat['prevention_steps']=entry.prevention_steps[:2]
        threat['risk_level_label']=translate_message(threat['risk_level'],lang)
    return RiskAssessment(**data)
