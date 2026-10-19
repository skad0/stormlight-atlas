export const GATES={TWoK:1,WoR:2,ED:3,OB:4,DS:5,ROW:6,WAT:7,EC:2,KL:2};
export const TYPES=['character','location','faction','item','magic'];
export const plural={character:'characters',location:'locations',faction:'factions',item:'items',magic:'magic'};
export const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const entityHref=(type,id)=>`#/entity/${encodeURIComponent(type)}/${encodeURIComponent(id)}`;
export const chapterHref=(book,number)=>`#/chapter/${encodeURIComponent(book)}/${encodeURIComponent(number)}`;
export function createModel(data,gate=4){
  const entities=new Map(data.entities.map(x=>[x.key,x]));
  const eventMap=new Map(data.events.map(x=>[x.id,x]));
  const chapterMap=new Map(data.chapters.map(x=>[x.key,x]));
  let currentGate=gate;
  const profileCache=new Map(),connectionCache=new Map();
  const model={data,entities,eventMap,chapterMap};
  Object.defineProperty(model,'gate',{get:()=>currentGate,set:value=>{currentGate=value;profileCache.clear();connectionCache.clear();}});
  model.events=()=>data.events.filter(e=>e.reveal<=model.gate);
  model.book=b=>data.books.find(x=>x.abbr===b);
  model.resolve=(id,type)=>{
    if(type&&entities.has(type+':'+id))return entities.get(type+':'+id);
    for(const t of TYPES)if(entities.has(t+':'+id))return entities.get(t+':'+id);
    return null;
  };
  model.profile=key=>{
    if(profileCache.has(key))return profileCache.get(key);
    const e=entities.get(key);if(!e)return null;
    const versions=e.versions.filter(v=>v.scope<=model.gate);
    const version=versions.at(-1)||e.versions[0],raw=version.data;
    const full=version.scope<=model.gate;
    let facts=(e.versions.at(-1).data.facts||[]).filter(f=>(f.reveal??version.scope)<=model.gate);
    const events=model.events().filter(ev=>({character:ev.characters,location:ev.locations,faction:ev.factions}[e.type]||[]).includes(e.id));
    const knownBooks=(raw.books||[]).filter(b=>GATES[b]&&GATES[b]<=model.gate);
    const coreGates=(raw.books||[]).filter(b=>GATES[b]).map(b=>GATES[b]);
    const first=coreGates.length?Math.min(...coreGates):version.scope;
    const hiddenIds={'pattern':2,'maya':4,'testament':6,'sibling':6,'vasher-past':4,'vivenna-past':4};
    const visible=(full||facts.length>0||events.length>0)&&first<=model.gate&&(hiddenIds[e.id]||0)<=model.gate;
    if(!visible){profileCache.set(key,null);return null;}
    let name=raw.name;
    if(e.id==='maya-blade'&&model.gate<4)name='Adolin’s Shardblade';
    if(e.id==='narak'&&model.gate<2)name='Narak';
    const summary=full?raw.summary:(facts.at(-1)?.text||events[0]?.summary||'No safe profile summary at this boundary.');
    const p={...e,raw,scope:version.scope,full,name,summary:summary||'',facts,events,books:knownBooks,status:facts.at(-1)?.text||'',sources:raw.sources||[]};profileCache.set(key,p);return p;
  };
  model.list=(type='all',q='',book='all')=>{
    const query=q.trim().toLowerCase();
    return data.entities.filter(e=>type==='all'||e.type===type).map(e=>model.profile(e.key)).filter(Boolean).filter(p=>book==='all'||p.books.includes(book)||p.events.some(e=>e.book===book)).filter(p=>!query||[p.name,p.summary,p.status,...p.facts.map(f=>f.text),...(p.full?p.raw.aliases||[]:[]),...(p.full?p.raw.roles||[]:[])].join(' ').toLowerCase().includes(query)).sort((a,b)=>((b.full&&b.raw.tags?.includes('major'))?1:0)-((a.full&&a.raw.tags?.includes('major'))?1:0)||a.name.localeCompare(b.name));
  };
  model.search=q=>{
    const needle=q.trim().toLowerCase();if(!needle)return [];
    return [...model.list('all',q).map(p=>({kind:p.type,title:p.name,summary:p.summary,href:entityHref(p.type,p.id)})),...model.events().filter(e=>[e.title,e.summary,e.chapter].join(' ').toLowerCase().includes(needle)).map(e=>({kind:'event',title:e.title,summary:e.summary,href:entityHref('event',e.id)})),...data.chapters.filter(c=>c.reveal<=model.gate&&[c.book,c.label,c.arc,c.arcSummary].join(' ').toLowerCase().includes(needle)).map(c=>({kind:'chapter',title:model.book(c.book)?.title+' · '+c.label,summary:c.arc||c.coverage,href:chapterHref(c.book,c.number)}))];
  };
  model.connections=key=>{
    if(connectionCache.has(key))return connectionCache.get(key);
    const focus=model.profile(key);if(!focus)return [];
    const links=[];const seen=new Set();
    const add=(target,kind,label,summary='',evidence='Catalog association',source=null)=>{
      if(!target||target.key===key||!model.profile(target.key))return;
      const unique=target.key+'|'+kind+'|'+label;if(seen.has(unique))return;seen.add(unique);
      links.push({target:model.profile(target.key),kind,label,summary,evidence,source});
    };
    for(const r of data.relations.filter(r=>r.reveal<=model.gate)){
      const source=model.resolve(r.source),target=model.resolve(r.target);
      if(source?.key===key)add(target,r.kind,r.label,r.summary,'Book-scoped relationship; temporal start/end not independently verified',r.chapter);
      if(target?.key===key)add(source,r.kind,r.label,r.summary,'Book-scoped relationship; temporal start/end not independently verified',r.chapter);
    }
    const attrs={factions:'faction',members:'character',locations:'location',owners:'character',users:'character',related:null};
    if(focus.full)for(const [field,type] of Object.entries(attrs))for(const id of focus.raw[field]||[])add(model.resolve(id,type),field,field,'','Profile association, not a claim of current allegiance');
    for(const other of model.list())if(other.full)for(const [field,type] of Object.entries(attrs))for(const id of other.raw[field]||[])if(model.resolve(id,type)?.key===key)add(entities.get(other.key),field,field,'','Profile association, not a dated relationship');
    connectionCache.set(key,links);return links;
  };
  model.routePoints=(id,plane)=>{
    const result=[];
    for(const e of model.events().filter(e=>e.characters?.includes(id)&&!e.history).sort((a,b)=>a.sort-b.sort)){
      const location=(e.locations||[]).map(x=>model.profile('location:'+x)).find(p=>p?.raw.plane===plane);
      if(location&&result.at(-1)?.location.id!==location.id)result.push({event:e,location});
    }
    return result;
  };
  return model;
}
