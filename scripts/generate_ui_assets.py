import io,json,tarfile
from pathlib import Path
import requests
from gtts import gTTS
root=Path(__file__).resolve().parents[1]
folder=root/'frontend/public/fonts'
meta=requests.get('https://registry.npmjs.org/@fontsource-variable/noto-sans/latest',timeout=30).json()
r=requests.get(meta['dist']['tarball'],timeout=60);r.raise_for_status()
with tarfile.open(fileobj=io.BytesIO(r.content),mode='r:gz') as a:
 m=next(m for m in a.getmembers() if m.name.endswith('/noto-sans-latin-wght-normal.woff2'))
 (folder/'noto-sans-latin.woff2').write_bytes(a.extractfile(m).read())
 m=next(m for m in a.getmembers() if m.name.lower().endswith('/license'))
 (folder/'LICENSE-latin.txt').write_bytes(a.extractfile(m).read())
manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
manifest=[m for m in manifest if m['file']!='noto-sans-latin.woff2']+[{'file':'noto-sans-latin.woff2','package':meta['name'],'version':meta['version'],'source':meta['dist']['tarball']}]
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for lang in ['en','hi','ta','te','kn']:
 data=json.loads((root/f'frontend/src/i18n/locales/{lang}.json').read_text(encoding='utf-8'))
 # Native labels already reviewed in the app's language catalog.
 name=data['language']['names'][lang]
 texts={lang:name,**{f'risk-{lang}-{level}':data['farmer'][f'risk_{level}'] for level in ['low','medium','high']}}
 for key,text in texts.items():
  path=root/f'frontend/public/voice/{key}.mp3'
  if not path.exists():gTTS(text,lang=lang).save(str(path))
  print(key,path.stat().st_size,flush=True)
