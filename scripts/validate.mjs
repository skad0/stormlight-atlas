import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createModel,TYPES,GATES} from '../dist/model.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(fs.readFileSync(path.join(root,'dist/data.json')));
const shell=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
assert.ok(!/(?:src|href)="\/(?!\/)/.test(shell),'Root-relative application assets are not portable');
assert.ok(fs.readFileSync(path.join(root,'dist/app.js'),'utf8').includes("new URL('./data.json', import.meta.url)"),'Dataset URL must be module-relative');
const m=createModel(d,7);
const unique=(items,label)=>assert.equal(new Set(items).size,items.length,`Duplicate ${label}`);
unique(d.entities.map(e=>e.key),'entity keys');unique(d.events.map(e=>e.id),'event IDs');unique(d.chapters.map(c=>c.key),'chapter keys');
const sources=new Set(d.sources.map(s=>s.id).filter(Boolean));
let checkedLinks=0;
for(const e of d.events){
 assert.ok(e.reveal>=1&&e.reveal<=7,`Bad event gate ${e.id}`);
 for(const [field,type] of [['characters','character'],['locations','location'],['factions','faction']])for(const id of e[field]||[]){assert.ok(m.entities.has(type+':'+id),`Dangling ${e.id} -> ${type}:${id}`);checkedLinks++;}
 for(const s of e.sources||[])assert.ok(typeof s==='object'?/^https:/.test(s.url):sources.has(s)||/^https:/.test(s),`Missing source ${s}`);
}
for(const c of d.chapters)for(const id of c.anchors||[]){assert.ok(m.eventMap.has(id),`Dangling chapter anchor ${c.key} -> ${id}`);assert.ok(m.eventMap.get(id).book?.split('/').includes(c.book)||(c.key==='ED:0'&&id==='lift-saves-gawx'),`Wrong-book anchor ${c.key}`);checkedLinks++;}
for(const r of d.relations){assert.ok(m.resolve(r.source),`Relationship source ${r.source}`);assert.ok(m.resolve(r.target),`Relationship target ${r.target}`);}
const expected={TWoK:[75,9],WoR:[89,14],ED:[20,0],OB:[122,14],DS:[19,0],ROW:[117,12],WAT:[147,18]};
for(const [book,[n,interludes]] of Object.entries(expected)){
 const cs=d.chapters.filter(c=>c.book===book);
 for(let i=1;i<=n;i++)assert.ok(cs.some(c=>c.number===i&&!/Interlude|I-\d/.test(c.label)),`Missing ${book} chapter ${i}`);
 assert.equal(cs.filter(c=>/^(?:Interlude\b|I-\d)/.test(c.label)).length,interludes,`Interlude count ${book}`);
 assert.equal(d.books.find(b=>b.abbr===book).chapterCount,cs.length);
}
assert.equal(m.resolve('rysn','character').key,'character:rysn');assert.equal(m.resolve('rysn','faction').key,'faction:rysn');
assert.equal(m.resolve('alethkar','location').key,'location:alethkar');
const transitions=[];
for(let gate=0;gate<=7;gate++){
 m.gate=gate;
 const list=m.list();
 for(const p of list){
  assert.ok(p.facts.every(f=>f.reveal<=gate),`Future status ${p.key}`);
  if(p.full)assert.ok(p.scope<=gate,`Future profile ${p.key}`);
  for(const edge of m.connections(p.key)){assert.ok(m.profile(edge.target.key),`Hidden connection target ${p.key}`);checkedLinks++;}
 }
 assert.ok(m.events().every(e=>e.reveal<=gate));
 if(gate<7){assert.equal(m.profile('magic:retribution'),null);assert.equal(m.search('Herald replacing Jezrien').length,0);assert.equal(m.search('Vessel of combined Honor and Odium').length,0);}
 if(gate<6){assert.equal(m.profile('character:testament'),null);assert.equal(m.search('Anti-Voidlight').length,0);}
 transitions.push({gate,entities:list.length,events:m.events().length});
}
m.gate=7;assert.match(m.profile('character:dalinar').status,/Dead/);assert.match(m.profile('character:shallan').status,/implied/);assert.ok(m.profile('character:shallan').facts.some(f=>f.certainty==='strong inference'));assert.ok(m.search('Retribution').length>0);
m.gate=4;assert.doesNotMatch(m.profile('character:dalinar').status,/Dead/);assert.equal(m.profile('character:shallan').full,true);assert.equal(m.profile('character:shallan').scope,4);
m.gate=5;assert.ok(m.profile('character:rysn').facts.some(f=>f.reveal===5),'Dawnshard facts missing before ROW');
const corrected={'dalinar-navani-marriage':'Ch. 4','szeth-restored':'Ch. 88','moash-kills-jezrien':'Ch. 121','chasmfiend-hunt':'Ch. 13'};
for(const [id,c] of Object.entries(corrected))assert.equal(m.eventMap.get(id).chapter,c);
assert.match(m.eventMap.get('gavilar-assassinated').dateLabel,/1167/);
// Run the actual renderer without a browser. This verifies all templates and route handlers;
// it intentionally does not claim visual or real browser verification.
class Element{
 constructor(id=''){this.id=id;this.innerHTML='';this.textContent='';this.value='';this.hidden=true;this.style={};this.dataset={};this.isConnected=true;this.tagName='DIV';this.classList={toggle(){},add(){},remove(){}};this.listeners={};}
 addEventListener(t,f){this.listeners[t]=f;}
 setAttribute(){} focus(){globalThis.document.activeElement=this;} querySelector(){return new Element();} querySelectorAll(){return [];} closest(){return null;}
}
const elements=new Map(['main','detail','veil','toast','search','boundary','mobile-view'].map(id=>[id,new Element(id)]));
elements.get('main').hidden=false;elements.get('search').tagName='INPUT';
const documentListeners={};
globalThis.document={getElementById:id=>elements.get(id)||null,querySelectorAll:()=>[],activeElement:new Element(),body:{style:{}},addEventListener:(t,f)=>{documentListeners[t]=f},createElement:()=>new Element()};
const values=new Map();globalThis.localStorage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};
globalThis.location={hash:'#/home'};globalThis.history={replaceState:(a,b,hash)=>{location.hash=hash;}};
globalThis.window={addEventListener(){},scrollTo(){}};globalThis.fetch=async()=>({ok:true,json:async()=>d});
const app=await import('../dist/app.js');
let rendered=0;
for(let gate=0;gate<=7;gate++){
 app.model.gate=gate;
 for(const view of ['home','explore','timeline','chapters','map','connections','status','saved','sources','search']){
  location.hash='#/'+view;app.render();assert.ok(elements.get('main').innerHTML.length>50,`Empty view ${view}`);rendered++;
  if(gate<7)assert.doesNotMatch(elements.get('main').innerHTML,/Herald replacing Jezrien|Vessel of combined Honor and Odium|Kaladin’s Honorspear/);
 }
}
app.model.gate=7;
const outputs=[];
for(const p of app.model.list()){
 const html=app.detailContent(p.type,p.id);assert.ok(html.includes('detail-title'),`Broken detail ${p.key}`);outputs.push(html);rendered++;
}
for(const e of d.events){outputs.push(app.detailContent('event',e.id));rendered++;}
for(const c of d.chapters){outputs.push(app.chapterDetail(c.book,String(c.number)));rendered++;}
for(const view of ['home','explore','timeline','chapters','map','connections','status','saved','sources']){location.hash='#/'+view;app.render();outputs.push(elements.get('main').innerHTML);}
app.state.chapterBook='supplements';outputs.push(app.chapterList(new URLSearchParams()));
for(const html of outputs){
 assert.ok(!html.includes('undefined'),'Undefined rendered text');
 for(const match of html.matchAll(/href="(#\/[^" ]+)"/g)){
  const [route]=match[1].slice(2).split('?'),p=route.split('/').map(decodeURIComponent);
  if(p[0]==='entity'){assert.ok(p[1]==='event'?m.eventMap.has(p[2]):m.entities.has(p[1]+':'+p[2]),`Broken rendered entity link ${match[1]}`);checkedLinks++;}
  else if(p[0]==='chapter'){assert.ok(m.chapterMap.has(p[1]+':'+p[2]),`Broken chapter link ${match[1]}`);checkedLinks++;}
 }
}
// Exercise progress and bookmarks with the actual delegated click handler.
const click=(dataset,attr)=>documentListeners.click({target:{closest:()=>({dataset,hasAttribute:x=>x===attr})}});
location.hash='#/chapter/TWoK/1';click({read:'TWoK:1'});assert.ok(app.state.read.has('TWoK:1'));click({read:'TWoK:1'});assert.ok(!app.state.read.has('TWoK:1'));
location.hash='#/entity/character/kaladin';click({bookmark:'character:kaladin'});assert.ok(app.state.saved.has('character:kaladin'));assert.ok(values.get('stormlight.v3.saved').includes('character:kaladin'));
app.model.gate=4;location.hash='#/entity/magic/retribution';app.render();assert.match(elements.get('detail').innerHTML,/Beyond this boundary/);
const report={passed:true,entities:d.entities.length,events:d.events.length,chapters:d.chapters.length,rendered,checkedLinks,transitions,browserVisualQA:'Not performed. The validation harness does not run a browser.',summary:`Validated ${d.entities.length} typed entities, ${d.events.length} events and ${d.chapters.length} indexed sections; ${rendered} rendered routes/details and ${checkedLinks} link checks passed.`};
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(report,null,2));
d.validation={summary:report.summary,visual:'Browser visual review was unavailable in the build environment.'};
fs.writeFileSync(path.join(root,'dist/data.json'),JSON.stringify(d));
console.log(JSON.stringify(report,null,2));
