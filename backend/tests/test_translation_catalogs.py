"""Catalog checks do not load or modify prediction artifacts."""
import importlib.util,json,re
from pathlib import Path
from collections import Counter
import pytest
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'backend/app/data/i18n'
LANGS=('en','hi','ta','te','kn')
FIELDS=('common_name','transliteration','summary','symptoms','immediate_actions','organic_options','chemical_options','prevention','when_to_call_expert','safety_notice')
spec=importlib.util.spec_from_file_location('review',ROOT/'scripts/translation_review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)

def read(path):return json.loads(path.read_text(encoding='utf-8'))

@pytest.mark.parametrize('lang',LANGS)
def test_catalog_shape_utf8_and_safety(lang):
 english=read(BASE/'en/diseases.json')['diseases'];local=read(BASE/lang/'diseases.json')['diseases']
 assert len(local)==38
 assert [d['id'] for d in local]==[d['id'] for d in english]
 for source,target in zip(english,local):
  assert target['scientific_name']==source['scientific_name']
  assert target['review_status'] in ('machine_suggested','human_reviewed')
  assert target['canonical_key']==source['id']
  for field in FIELDS:
   assert target[field],(lang,target['id'],field)
   assert '\ufffd' not in str(target[field])
   if field in ('common_name','transliteration'):continue
   a=source[field] if isinstance(source[field],list) else [source[field]]
   b=target[field] if isinstance(target[field],list) else [target[field]]
   assert len(a)==len(b),(lang,target['id'],field)
   for left,right in zip(a,b):
    assert review.safety_tokens(left)==review.safety_tokens(right),(lang,target['id'],field,left,right)

@pytest.mark.parametrize('lang',LANGS)
def test_ui_and_message_keys(lang):
 for kind in ('ui','messages'):
  english=dict(review.flatten(read(review.catalogs('en')[kind])))
  local=dict(review.flatten(read(review.catalogs(lang)[kind])))
  assert english.keys()<=local.keys()
  for key in english:
   assert local[key].strip(),(lang,key)
   assert '\ufffd' not in local[key]
   assert Counter(re.findall(r'\{\{[^}]+\}\}',english[key]))==Counter(re.findall(r'\{\{[^}]+\}\}',local[key])),(lang,key)

@pytest.mark.parametrize('explicit,header,expected',[(None,'ta-IN;q=0.7,kn-IN;q=0.9','kn'),('hi-IN','ta','hi'),('es','kn','en'),(None,'te;q=0,hi;q=0.3','hi'),(None,None,'en')])
def test_negotiation(explicit,header,expected):
 from backend.app.services.i18n import resolve_language
 assert resolve_language(explicit,header)==expected

def test_missing_symptoms_fail_closed(tmp_path,monkeypatch):
 from backend.app.services import i18n
 source=read(BASE/'en/diseases.json');target=read(BASE/'kn/diseases.json');target['diseases'][0]['symptoms']=''
 for lang,data in [('en',source),('kn',target)]:
  p=tmp_path/lang;p.mkdir();(p/'diseases.json').write_text(json.dumps(data),encoding='utf-8')
 monkeypatch.setattr(i18n,'_I18N_BASE_DIR',tmp_path);monkeypatch.setattr(i18n,'_KB_LANG_CACHE',{})
 with pytest.raises(KeyError):
  i18n.get_localized_disease_entry(source['diseases'][0]['id'],'kn')
@pytest.mark.asyncio
@pytest.mark.parametrize('lang',LANGS)
async def test_endpoint_language_contract(client,lang):
 from backend.app.services.i18n import get_localized_disease_entry
 for suffix,headers in [(f'?lang={lang}',{}),('',{'Accept-Language':lang+'-IN'})]:
  response=await client.get('/api/v1/diseases'+suffix,headers=headers)
  assert response.status_code==200
  entries=response.json();assert len(entries)==38
  assert entries[0]['language']==lang
  assert entries[0]['disease_name']==get_localized_disease_entry(entries[0]['id'],lang).disease_name
  error=await client.get('/api/v1/history'+suffix,headers=headers)
  assert error.status_code in (401,403)
  assert error.headers['Content-Language']==lang
  if lang!='en':assert re.search('[\u0900-\u0d7f]',error.json()['detail'])
  invalid=await client.post('/api/v1/analyze'+suffix,headers=headers)
  assert invalid.status_code==422
  assert invalid.headers['Content-Language']==lang

@pytest.mark.asyncio
@pytest.mark.parametrize('lang',LANGS)
async def test_analysis_history_localization_without_changing_prediction(client,monkeypatch,sample_leaf_image_bytes,auth_headers,lang):
 from backend.app.api.routes import analyze
 from backend.app.services.i18n import get_localized_disease_entry
 from backend.app.main import app
 monkeypatch.setattr(app.state.limiter,'enabled',False)
 key='Apple___Apple_scab'
 monkeypatch.setattr(analyze,'predict_disease',lambda *_:{'predicted_label':key,'crop':'Apple','disease_name':'Apple Scab','confidence':0.4,'confidence_display':'Low / Uncertain','is_uncertain':True,'uncertainty_reason':'uncertain','top_k':[{'class_id':key,'crop':'Apple','disease_name':'Apple Scab','confidence':0.4,'confidence_percentage':40,'is_healthy':False}],'model_version':'localization-test'})
 response=await client.post('/api/v1/analyze?lang='+lang,headers=auth_headers,files={'image':('leaf.jpg',sample_leaf_image_bytes,'image/jpeg')})
 assert response.status_code==200,response.text
 data=response.json();entry=get_localized_disease_entry(key,lang)
 assert data['language']==lang
 assert data['disease_name']==entry.disease_name
 assert data['canonical_key']==key
 assert data['confidence']==0.4 and data['is_uncertain'] is True
 assert data['scientific_name']==entry.scientific_name
 for path in ('/api/v1/history','/api/v1/history/'+data['id']):
  r=await client.get(path+'?lang='+lang,headers=auth_headers);assert r.status_code==200,r.text
  value=r.json();value=value[0] if isinstance(value,list) else value
  assert value['disease_name']==entry.disease_name
  assert value['disease_details']['symptoms']==entry.symptoms
  assert value['confidence']==0.4


@pytest.mark.parametrize('lang,start,end',[('hi',0x900,0x97f),('ta',0xb80,0xbff),('te',0xc00,0xc7f),('kn',0xc80,0xcff)])
def test_no_wrong_indic_script(lang,start,end):
 for kind,path in review.catalogs(lang).items():
  for key,text in review.flatten(read(path)):
   if 'names' in key:continue
   invalid=[char for char in text if 0x900<=ord(char)<=0xd7f and not start<=ord(char)<=end and ord(char) not in (0x964,0x965)]
   assert not invalid,(lang,kind,key,invalid)
