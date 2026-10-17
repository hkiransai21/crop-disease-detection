"""Shared review-catalog helpers; paths are fixed to supported language catalogs."""
import json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LANGUAGES=('en','hi','ta','te','kn')

def catalogs(lang):
 return {'ui':ROOT/f'frontend/src/i18n/locales/{lang}.json','diseases':ROOT/f'backend/app/data/i18n/{lang}/diseases.json','glossary':ROOT/f'backend/app/data/i18n/glossary/{lang}.json','messages':ROOT/f'backend/app/data/i18n/{lang}/messages.json'}

def flatten(value,path=()):
 if isinstance(value,str):yield path,value
 elif isinstance(value,dict):
  for key,item in value.items():yield from flatten(item,path+(key,))
 elif isinstance(value,list):
  for index,item in enumerate(value):yield from flatten(item,path+(index,))

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def get(data,path):
 for key in path:data=data[key]
 return data

def set_value(data,path,value):
 for key in path[:-1]:data=data[key]
 data[path[-1]]=value

def safety_tokens(text):
 config=ROOT/'backend/app/data/i18n/protected_terms.json'
 tokens=Counter(re.findall(r'\d+(?:[.,]\d+)*',text))
 if config.exists():
  p=read(config)
  for term in set(p['ingredients']):
   n=len(re.findall(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text))
   if n:tokens['ingredient:'+term]=n
  tokens.update('unit:'+x for x in re.findall(p['units_pattern'],text))
 return tokens

IMMUTABLE={'id','canonical_key','canonical_disease_name','scientific_name','language','review_status','review_notes','term_key','english','source','source_url','source_name','reference_url','causal_agent_type'}
def editable(path):return bool(path) and path[-1] not in IMMUTABLE and 'sources' not in path
