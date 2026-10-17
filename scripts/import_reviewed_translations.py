"""Validate an entire review CSV before writing any catalog."""
import argparse,csv,json
from translation_review import *

def main():
 parser=argparse.ArgumentParser();parser.add_argument('csv',type=Path);parser.add_argument('--lang',choices=LANGUAGES[1:],required=True);parser.add_argument('--check',action='store_true');args=parser.parse_args()
 paths=catalogs(args.lang);data={k:read(p) for k,p in paths.items() if p.exists()};sources={k:read(catalogs('en')[k]) for k in data};seen=set();reviews={}
 with args.csv.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   key=row['key']
   if key in seen:raise ValueError(f'Duplicate key: {key}')
   seen.add(key);kind,*address=json.loads(key)
   if kind not in data or not editable(address):raise ValueError(f'Unknown or immutable key: {key}')
   source=get(sources[kind],address);get(data[kind],address)
   if source!=row['English']:raise ValueError(f'English changed; export again: {key}')
   value=row['translation'].strip()
   if not value or '\ufffd' in value:raise ValueError(f'Empty or corrupt text: {key}')
   if safety_tokens(source)!=safety_tokens(value):raise ValueError(f'Ingredient, number or unit mismatch: {key}')
   if row['review_status'] not in ('machine_suggested','human_reviewed'):raise ValueError(f'Invalid review status: {key}')
   if row['review_status']=='human_reviewed' and not row['reviewer notes'].strip():raise ValueError(f'Name reviewer and date in notes: {key}')
   set_value(data[kind],address,value);reviews[key]={'review_status':row['review_status'],'reviewer_notes':row['reviewer notes']}
 if args.check:
  print(f'Validated {len(seen)} review rows for {args.lang}; no files changed.');return
 for kind,value in data.items():
  pending=paths[kind].with_suffix('.json.pending');pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');pending.replace(paths[kind])
 target=ROOT/f'backend/app/data/i18n/{args.lang}/reviews.json'
 old=read(target) if target.exists() else {};old.update(reviews);target.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Imported {len(seen)} reviewed rows for {args.lang}. Row-level review records saved; catalog-wide review status is not promoted automatically.')
if __name__=='__main__':main()
