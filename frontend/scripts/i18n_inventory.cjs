const fs = require('fs');
const path = require('path');
const ts = require('typescript');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const fix = process.argv.includes('--fix');
const list = [];
const englishFile = path.join(root, 'src/i18n/locales/en.json');
const english = JSON.parse(fs.readFileSync(englishFile, 'utf8'));
english.ui ||= {};
const visibleAttrs = new Set(['title', 'placeholder', 'alt', 'aria-label', 'label']);
function classify(n, sf) {
  const p = n.parent;
  if (ts.isJsxText(n)) return n.text.trim() && /[\p{L}\p{N}]/u.test(n.text) ? 'jsx-text' : null;
  if (!ts.isStringLiteral(n) && !ts.isNoSubstitutionTemplateLiteral(n)) return null;
  if (ts.isJsxAttribute(p)) return visibleAttrs.has(p.name.text) ? 'attribute' : null;
  if (ts.isImportDeclaration(p) || ts.isExportDeclaration(p) || ts.isLiteralTypeNode(p) || ts.isPropertyAssignment(p) && p.name === n) return null;
  if (ts.isCallExpression(p) && /(^|\.)(t|tr)$/.test(p.expression.getText(sf))) return null;
  if (ts.isBinaryExpression(p) && [ts.SyntaxKind.EqualsEqualsEqualsToken,ts.SyntaxKind.ExclamationEqualsEqualsToken,ts.SyntaxKind.EqualsEqualsToken,ts.SyntaxKind.ExclamationEqualsToken].includes(p.operatorToken.kind)) return null;
  if (ts.isCaseClause(p)) return null;
  const s = n.text;
  if (!s.trim() || !/[\p{L}]/u.test(s)) return null;
  if (/^(https?:|\/|\.\/|\.\.\/|tel:|data:|image\/)/.test(s) || /^#[\da-f]+$/i.test(s)) return null;
  if (/(?:^|\s)(?:bg-|text-|border-|flex|grid|rounded|w-|h-|p-|px-|py-|space-|items-|font-|hover:|md:|sm:|absolute|relative|fixed|hidden|block)/.test(s)) return null;
  if (ts.isCallExpression(p) && /\.(includes|startsWith|endsWith|split|replace|join|toLocaleDateString|toLocaleString|format|createElement|setItem|getItem|removeItem|addEventListener|removeEventListener|querySelector|register|open|request|setRequestHeader)$/.test(p.expression.getText(sf))) return null;
  if (ts.isNewExpression(p) && p.expression.getText(sf)==='Error') return 'error';
  if (/\s/.test(s) && /[a-zA-Z]{2}/.test(s)) return 'literal';
  if (ts.isPropertyAssignment(p) && /^(label|title|description|desc|name|unit|text)$/.test(p.name.getText(sf))) return 'display-data';
  if (ts.isJsxExpression(p) || ts.isConditionalExpression(p)) return /[A-Z]/.test(s) ? 'expression' : null;
  return null;
}
function files(dir) { return fs.readdirSync(dir, {withFileTypes:true}).flatMap(e=>e.isDirectory()? files(path.join(dir,e.name)) : /\.tsx?$/.test(e.name)? [path.join(dir,e.name)] : []); }
for (const filename of files(path.join(root,'src')).filter(f=>!f.includes(path.sep+'i18n'+path.sep)&&!f.includes(path.sep+'types'+path.sep)&&!f.includes(path.sep+'hooks'+path.sep))) {
 const source=fs.readFileSync(filename,'utf8'); const sf=ts.createSourceFile(filename,source,ts.ScriptTarget.Latest,true,filename.endsWith('tsx')?ts.ScriptKind.TSX:ts.ScriptKind.TS); const edits=[];
 function walk(n) {
  const kind=classify(n,sf);
  if (kind) {
   let value=n.text.replace(/\s+/g,' ').trim();
   value=value.replace(/&bull;/g,'•').replace(/&amp;/g,'&').replace(/&gt;/g,'>').replace(/&lt;/g,'<').replace(/&nbsp;/g,' ');
   const key='s_'+crypto.createHash('sha1').update(value).digest('hex').slice(0,10);
   const pos=sf.getLineAndCharacterOfPosition(n.getStart(sf));
   list.push({file:path.relative(root,filename).replaceAll('\\','/'),line:pos.line+1,kind,text:value,key:'ui.'+key});
   english.ui[key]=value;
   let replacement=`tr('ui.${key}')`;
   if (kind==='jsx-text') replacement='{'+replacement+'}';
   else if (kind==='attribute') replacement='{'+replacement+'}';
   edits.push([n.getStart(sf),n.end,replacement]);
   return;
  }
  ts.forEachChild(n,walk);
 }
 walk(sf);
 if (fix && edits.length) {
  let output=source;
  for(const [a,b,v] of edits.sort((a,b)=>b[0]-a[0])) output=output.slice(0,a)+v+output.slice(b);
  const rel=path.relative(path.dirname(filename),path.join(root,'src/i18n/i18n')).replaceAll('\\','/');
  output=`import { tr } from '${rel.startsWith('.')?rel:'./'+rel}';\n`+output;
  fs.writeFileSync(filename,output,'utf8');
 }
}
if (fix) fs.writeFileSync(englishFile,JSON.stringify(english,null,2)+'\n');
const target=process.argv.find(x=>x.startsWith('--out='));
if(target)fs.writeFileSync(target.slice(6),JSON.stringify(list,null,2)+'\n');
console.log(`${list.length} hardcoded display strings (${new Set(list.map(x=>x.key)).size} distinct)`);
if(process.argv.includes('--check')&&list.length)process.exit(1);

const missingKeys = [];
for (const filename of files(path.join(root, 'src'))) {
 const source = fs.readFileSync(filename, 'utf8');
 const sf = ts.createSourceFile(filename, source, ts.ScriptTarget.Latest, true);
 function checkKeys(node) {
  if (ts.isCallExpression(node) && /(^|\.)(t|tr)$/.test(node.expression.getText(sf)) && node.arguments.length && ts.isStringLiteral(node.arguments[0])) {
   const key = node.arguments[0].text;
   const value = key.split('.').reduce((obj, part) => obj?.[part], english);
   if (typeof value !== 'string' || !value.trim()) missingKeys.push({ file: path.relative(root, filename), key });
  }
  ts.forEachChild(node, checkKeys);
 }
 checkKeys(sf);
}
console.log(`${missingKeys.length} UI references missing from the English catalog`);
if (missingKeys.length) console.error(JSON.stringify(missingKeys, null, 2));
if (process.argv.includes('--check') && missingKeys.length) process.exit(1);
