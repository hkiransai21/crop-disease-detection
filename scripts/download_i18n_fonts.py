"""Download licensed, script-subsetted Noto variable WOFF2 files for self hosting."""
import io,json,tarfile
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'frontend/public/fonts'; folder.mkdir(parents=True,exist_ok=True)
manifest=[]
for script in ('devanagari','tamil','telugu','kannada'):
 package=f'@fontsource-variable/noto-sans-{script}'
 metadata=requests.get(f'https://registry.npmjs.org/{package}/latest',timeout=30).json()
 response=requests.get(metadata['dist']['tarball'],timeout=60); response.raise_for_status()
 with tarfile.open(fileobj=io.BytesIO(response.content),mode='r:gz') as archive:
  member=next(m for m in archive.getmembers() if m.name.endswith(f'noto-sans-{script}-{script}-wght-normal.woff2'))
  name=f'noto-sans-{script}.woff2'
  (folder/name).write_bytes(archive.extractfile(member).read())
  license=next(m for m in archive.getmembers() if m.name.lower().endswith('/license'))
  (folder/f'LICENSE-{script}.txt').write_bytes(archive.extractfile(license).read())
 manifest.append({'file':name,'package':package,'version':metadata['version'],'source':metadata['dist']['tarball']})
 print(name,(folder/name).stat().st_size,flush=True)
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
