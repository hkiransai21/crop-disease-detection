"""Export fixed-language catalogs to UTF-8 CSV for native-speaker review."""
import argparse,csv,json
from pathlib import Path
from translation_review import *

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'translation-review');args=parser.parse_args()
 args.output.mkdir(parents=True,exist_ok=True)
 for lang in LANGUAGES[1:]:
  rows=[]
  records_path=ROOT/f"backend/app/data/i18n/{lang}/reviews.json"
  records=read(records_path) if records_path.exists() else {}
  for kind,path in catalogs(lang).items():
   if not path.exists():continue
   english=read(catalogs('en')[kind]);local=read(path)
   for address,source in flatten(english):
    if not editable(address):continue
    try:value=get(local,address)
    except (KeyError,IndexError):value=''
    key=json.dumps([kind,*address],ensure_ascii=False);record=records.get(key,{})
    rows.append({'key':key,'English':source,'translation':value,'review_status':record.get('review_status','machine_suggested'),'reviewer notes':record.get('reviewer_notes','')})
  target=args.output/f'{lang}.csv'
  with target.open('w',encoding='utf-8-sig',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=['key','English','translation','review_status','reviewer notes']);writer.writeheader();writer.writerows(rows)
  print(f'{lang}: {len(rows)} strings -> {target}')
if __name__=='__main__':main()
