import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
export function args(argv=process.argv.slice(2)) {const a={}; for(let i=0;i<argv.length;i++){const s=argv[i];if(!s.startsWith('--'))throw Error(`Unexpected argument ${s}`);const k=s.slice(2);if(!k)throw Error('Empty argument');if(i+1<argv.length&&!argv[i+1].startsWith('--'))a[k]=argv[++i];else a[k]=true;}return a;}
export function root(p) {const d=fs.realpathSync(path.resolve(p??process.cwd()));if(!fs.statSync(d).isDirectory())throw Error('Not a directory');return d;}
export function canonicalPath(p) {let current=path.resolve(p);const missing=[];while(!fs.existsSync(current)){const parent=path.dirname(current);if(parent===current)break;missing.unshift(path.basename(current));current=parent;}return path.join(fs.realpathSync(current),...missing);}
export function packageJson(project){const file=path.join(project,'package.json');if(!fs.existsSync(file))return null;return JSON.parse(fs.readFileSync(file,'utf8'));}
export function git(project, params){const r=spawnSync('git',params,{cwd:project,encoding:'utf8',timeout:15000});return r.status===0?r.stdout.trim():null;}
export function fingerprint(project){const head=git(project,['rev-parse','HEAD']);const state=git(project,['status','--porcelain=v1','--untracked-files=all']);if(head===null||state===null)return null;const digest=createHash('sha256');digest.update(head);digest.update('\n');const filtered=state.split('\n').filter(line=>line && !line.slice(3).startsWith('.sdd/work/'));digest.update(filtered.join('\n'));
 // Include content for tracked modifications, staged changes, and untracked files, excluding .sdd/work verification artifacts.
 const entries=state.split('\n').filter(Boolean);for(const line of entries){let rel=line.slice(3);if(rel.includes(' -> '))rel=rel.split(' -> ').at(-1);if(rel.startsWith('.sdd/work/'))continue;const absolute=path.resolve(project,rel);if(!absolute.startsWith(project+path.sep))continue;try{if(fs.statSync(absolute).isFile()){digest.update(rel);digest.update(fs.readFileSync(absolute));}}catch{digest.update(`missing:${rel}`)}}return {head,digest:digest.digest('hex')};}
export function writeAtomic(file,value){fs.mkdirSync(path.dirname(file),{recursive:true});const temp=file+`.tmp-${process.pid}`;fs.writeFileSync(temp,JSON.stringify(value,null,2)+'\n',{mode:0o600});fs.renameSync(temp,file);}
export function inside(parent,child){const rel=path.relative(parent,child);return rel!==''&&!rel.startsWith('..'+path.sep)&&rel!=='..'&&!path.isAbsolute(rel);}
export function fail(msg,code=1){console.error(JSON.stringify({error:msg}));process.exit(code);}
