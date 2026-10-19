import json, re, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'source-data'
OLD=json.loads((SRC/'oathbringer.json').read_text())
NEW=json.loads((SRC/'rhythm-of-war.json').read_text())
ORDER={'TWoK':1,'WoR':2,'ED':3,'OB':4,'DS':5,'ROW':6,'WAT':7,'EC':2,'KL':2}
KINDS={'characters':'character','factions':'faction','locations':'location','magic':'magic','items':'item'}
THRESHOLDS=[(80,1),(200,2),(232,3),(450,4),(520,5),(850,6)]
def reveal_at(n,scope):
    if n<0:return scope
    return next((g for t,g in THRESHOLDS if n<=t),7)
def fix(d):
    audit=SRC/'reference-audit.json'
    if audit.exists():
        for change in json.loads(audit.read_text()).get('suggestedCorrections',[]):
            group,ident=change['target'].split(':',1)
            raw=next((x for x in d[group] if x['id']==ident),None)
            if raw and 'value' in change:raw[change['field']]=change['value']
    for item in d['items']:
        item['locations']=['kharbranth-city' if x=='kharbranth' else x for x in item['locations']]
    for e in d['events']:
        if e['id'] in ['gavilar-assassinated','ob-prologue']:
            e['dateLabel']=re.sub(r'1173','1167',e['dateLabel'])
        if e['id']=='row-prologue':e['dateLabel']='Treaty feast, 1167; revealed in Rhythm of War prologue'
        e['dateLabel']=e['dateLabel'].replace('This is the atlas’s hard spoiler boundary.','')
    return d
OLD=fix(OLD);NEW=fix(NEW)
entities={}
for scope,d in [(4,OLD),(6,NEW)]:
    for collection,kind in KINDS.items():
        for raw in d[collection]:
            key=kind+':'+raw['id']
            entry=entities.setdefault(key,{'key':key,'type':kind,'id':raw['id'],'versions':[]})
            r=copy.deepcopy(raw)
            r['facts']=[{'text':s['label'],'reveal':reveal_at(s['at'],scope),'position':s['at'],'locator':'Inherited dated status; exact chapter unverified'} for s in raw.get('status',[])]
            if raw['id']=='szeth':
                for f in r['facts']:
                    if f['position']==0:f['text']='Truthless assassin serving successive masters.'
            r.pop('status',None)
            entry['versions'].append({'scope':scope,'data':r})
events=[]
for e in NEW['events']:
    x=copy.deepcopy(e);x['reveal']=ORDER.get(e.get('book'),4)
    x['key']='event:'+e['id'];x['provenance']='Reconciled inherited atlas; anchor not independently rechecked'
    x['sources']=[]
    x['chronology']='Relative anchor; cross-viewpoint alignment approximate'
    label=x['dateLabel'].lower()
    if any(t in label for t in ['flashback','years before','years earlier','prehistory','ancient','aharietiam']) or 'flashback' in x.get('tags',[]):
        x['history']=True;x['chronology']='Historical/flashback event; exact placement uncertain'
    if 'prologue' in str(e.get('chapter','')).lower():
        if e['id'] not in ['ds-prologue']:x['history']=True
    events.append(x)
relations=[]
for i,r in enumerate(NEW['manualRelations']):
    x=copy.deepcopy(r);x['reveal']=max([ORDER[b] for b in r.get('books',[]) if b in ORDER] or [4]);x['id']='manual-'+str(i)
    relations.append(x)
chapters=copy.deepcopy(NEW['chapters'])
for c in chapters:
    c['key']=c['book']+':'+str(c['number']);c['reveal']=ORDER[c['book']]
    c['source']='https://coppermind.net/wiki/Summary:'+{'TWoK':'The_Way_of_Kings','WoR':'Words_of_Radiance','ED':'Edgedancer','OB':'Oathbringer','DS':'Dawnshard','ROW':'Rhythm_of_War'}[c['book']]
    c['coverage']='Curated arc anchor' if c.get('anchors') else 'Chapter index; no scene-specific recap'
audit=SRC/'reference-audit.json'
if audit.exists():
    a=json.loads(audit.read_text())
    for c in json.loads((SRC/'missing-chapters.json').read_text()):
        c=copy.deepcopy(c);c['key']=c['book']+':'+str(c['number']);c['reveal']=ORDER[c['book']];c.setdefault('anchors',[]);c.setdefault('arcSummary','Interlude index; use the linked source for chapter details.');c.setdefault('coverage','Interlude index')
        if c['key'] not in {x['key'] for x in chapters}:chapters.append(c)
    for change in a.get('suggestedCorrections',[]):
        if change['target'].startswith('events:') and change.get('sourceUrl'):
            e=next((x for x in events if x['id']==change['target'].split(':')[1]),None)
            if e:
                e['sources'].append({'url':change['sourceUrl'],'title':'Verified anchor correction'})
                e['provenance']='Selected locator or date corrected against source; surrounding narrative inherited'
    for change in a.get('chapterAnchorSuggestions',[]):
        c=next((x for x in chapters if x['book']==change['book'] and x['number']==change['number']),None)
        if c:
            if change.get('remove') in c['anchors']:c['anchors'].remove(change['remove'])
            if change.get('add') and change['add'] not in c['anchors']:c['anchors'].append(change['add'])
books=copy.deepcopy(NEW['books'])
for b in books:
    b['gate']=ORDER[b['abbr']];b['coverage']='Major arcs and named reference records; chapter index'
    if b['abbr']=='ROW':b['why']='Fourth core novel. Follow with Wind and Truth.'
    if b['abbr']=='OB':b['why']='Third core novel. Follow with Dawnshard.'
books.append({'id':'wat','abbr':'WAT','title':'Wind and Truth','year':2024,'seriesOrder':5,'gate':7,'scope':'Core Stormlight novel','chronology':'Ten-day main narrative after Rhythm of War, with flashbacks and Spiritual Realm sequences','summary':'A ten-day contest deadline brings battles across Roshar, a journey through Shinovar, and a search through the Spiritual Realm.','why':'Closes the first five-novel arc.','chapters':'147 numbered chapters, prologue, interludes, epilogue and postlude','coverage':'Sourced major arcs and outcomes; chapter index','color':'#d6bd87'})
extension=SRC/'wind-and-truth.json'
supplements=[];newSources=[]
if extension.exists():
    ext=json.loads(extension.read_text())
    def enrich(kind,ident,name=None,summary=None,fact=None,sources=None,scope=7,book='WAT'):
        key=kind+':'+ident
        if key in entities:
            entry=entities[key]
            if entry['versions'][-1]['scope']==scope:r=entry['versions'][-1]['data']
            else:
                r=copy.deepcopy(entry['versions'][-1]['data']);entry['versions'].append({'scope':scope,'data':r})
        else:
            r={'id':ident,'name':name or ident,'summary':summary or '', 'books':[book],'facts':[],'kind':'person' if kind=='character' else kind,'tags':[]}
            entities[key]={'key':key,'type':kind,'id':ident,'versions':[{'scope':scope,'data':r}]}
        if name:r['name']=name
        if summary:r['watSummary']=summary
        r['books']=list(dict.fromkeys(r.get('books',[])+[book]))
        if fact:r.setdefault('facts',[]).append(fact)
        r['sources']=list(dict.fromkeys(r.get('sources',[])+(sources or [])))
        return r
    for raw in ext.get('newEntitiesNeeded',[]):
        r=enrich(raw['type'],raw['id'],raw['name'],raw['note'])
        if raw['type']=='location':r['plane']='Spiritual';r['region']='Non-geographic';r['summary']=raw['note']
    for raw in ext.get('statusChanges',[]):
        fact={'text':raw['label'],'reveal':7,'locator':'WAT · '+str(raw['chapter']),'certainty':raw.get('certainty','confirmed'),'sources':raw.get('sources',[])}
        enrich('character',raw['entityId'],fact=fact,sources=raw.get('sources'))
    for name,kind in [('magicUpdates','magic'),('itemUpdates','item'),('factionUpdates','faction')]:
        for raw in ext.get(name,[]):
            fact={'text':raw['summary'],'reveal':7,'locator':'WAT · '+str(raw['chapter']),'sources':raw.get('sources',[])}
            enrich(kind,raw['entityId'],raw.get('name'),fact=fact,sources=raw.get('sources'))
    enrich('character','gawx',name='Yanagawn (Gawx)')
    for i,raw in enumerate(ext.get('relationships',[])):
        r=copy.deepcopy(raw);r['id']='wat-relation-'+str(i);r['reveal']=7;r['summary']=r['label'];r['books']=['WAT'];relations.append(r)
    for e in ext.get('events',[]):
        x=copy.deepcopy(e);x['book']='WAT';x['reveal']=7;x['key']='event:'+x['id'];x['sort']=900+len([e for e in events if e['book']=='WAT']);x['dateLabel']=x.get('timeLabel','Wind and Truth; relative position uncertain');x.setdefault('explanation','');x.setdefault('characters',[]);x.setdefault('locations',[]);x.setdefault('factions',[]);x.setdefault('tags',[]);x['provenance']='New sourced research';x['chronology']=x.get('chronologyNote','Approximate; reading order is not a canonical date');x['history']=x.get('timeKind') in ['flashback','historical','vision','spiritual-vision'];events.append(x)
    supplements=ext.get('supplements',[]);newSources=ext.get('sources',[])
    sourceById={s['id']:s for s in newSources}
    for s in supplements:
        s['sources']=[sourceById[x] for x in s['sources']]
        for raw in s.get('characters',[]):enrich('character',raw['id'],raw['name'],raw['summary'],sources=raw.get('sources'),scope=2,book=s['abbr'])
        for e in s.get('events',[]):
            x=copy.deepcopy(e);x['reveal']=2;x['key']='event:'+x['id'];x['sort']=110+x['narrativeOrder']*5 if s['abbr']=='EC' else 175+x['narrativeOrder'];x['dateLabel']=s['placement'];x['locations']=x.get('locations',[]);x['factions']=[];x['explanation']='';x['tags']=['side-story'];x['sources']=[x['source']];x['chronology']=x['chronologyNote'];events.append(x)
    index=copy.deepcopy(ext['chapterIndex'])
    index += [{'number':-1,'label':'Prologue'},{'number':1000,'label':'Epilogue'},{'number':1001,'label':'Postlude'}]
    # Pair positions are established by the publisher-hosted reread index.
    for pair,after in enumerate([13,33,42,54,68,77,87,99,125]):
        for j in range(2):index.append({'number':after+(j+1)/10,'label':'Interlude '+str(pair*2+j+1),'interludeNumber':pair*2+j+1})
    for c in index:
        c['book']='WAT';c['key']='WAT:'+str(c['number']);c['reveal']=7;c['anchors']=[];c['source']=sourceById['wat-index']['url'];c['arcSummary']='Chapter index. Use linked story anchors for selected event context; no scene recap or unverified chapter title is invented.';c['coverage']='Chapter index'
        chapters.append(c)
    for e in events:
        if e['book']!='WAT':continue
        label=str(e['chapter'])
        if label=='Prologue':nums=[-1]
        elif 'Interlude' in label:
            n=int(re.search(r'\d+',label).group());nums=[c['number'] for c in index if c.get('interludeNumber')==n]
        elif label=='Epilogue':nums=[1000]
        elif label=='Postlude':nums=[1001]
        else:
            m=re.search(r'(\d+)(?:[–-](\d+))?',label);nums=list(range(int(m[1]),int(m[2] or m[1])+1)) if m else []
        for c in chapters:
            if c['book']=='WAT' and c['number'] in nums:c['anchors'].append(e['id']);c['coverage']='Curated event anchor'
for b in books:
    b['chapterCount']=len([c for c in chapters if c['book']==b['abbr']])
sources=copy.deepcopy(NEW['sources'])+newSources
for s in sources:
    s['use']=s.get('use','').replace('The live page also contains later books; this artifact stops at Oathbringer.','Catalog and publication scope, checked 2026-10-16.')
    if s in newSources:
        s['reveal']=0 if s['id'].startswith('official') else 2 if s['id'] in ['lost-tales-official','elsecaller-wiki','tyvneri-wiki','lopen-wiki'] else 7
    else:
        s['reveal']=6 if 'Rhythm' in s['title'] or 'Urithiru' in s['title'] else 5 if 'Dawnshard' in s['title'] or 'Akinah' in s['title'] else 4
for e in events:
    e['explanation']=e.get('explanation','').replace('This is the atlas’s hard spoiler boundary.','')
    e['sources']=list(e.get('sources',[]))
    for field,kind in [('characters','character'),('locations','location'),('factions','faction')]:
        for ident in list(e.get(field,[])):
            if kind+':'+ident not in entities:
                for alt,altKind in [('characters','character'),('locations','location'),('factions','faction')]:
                    if altKind+':'+ident in entities:
                        e[field].remove(ident);e.setdefault(alt,[]).append(ident);break
data={'meta':{'title':'Stormlight Atlas','date':'2026-10-16','version':3,'scope':'All five published core novels, Edgedancer, Dawnshard, and cataloged Story Deck side stories. Future/unpublished books are excluded.','reconciliation':'Oathbringer edition (2026-08-21) and Rhythm of War edition (2026-10-05) preserved as separate profile snapshots. Wind and Truth facts are appended with their sources. Duplicate generated graph links are replaced with typed links.','chronology':'Reading positions in the inherited atlas are not canonical dates. In-world view separates historical/flashback material and labels uncertain alignment. Story order within parallel fronts is approximate.','spoilers':'Completed-book boundaries. Final-scope summaries, aliases, memberships and associations remain hidden until their snapshot is safe. Earlier boundaries show only dated status facts and approved event anchors. This is a reading aid, not a security boundary: all static data is downloaded to your browser.','coverage':'Major arcs and outcomes, recurring named entities and linked chapter anchors. Chapter index coverage does not mean every scene or every mention is annotated. Inherited chapter/range locators are not all independently verified.','copyright':'Unofficial fan-made study aid. Original paraphrases and schematic coordinates; no book text or official map art reproduced.'},'books':books,'entities':list(entities.values()),'events':events,'relations':relations,'chapters':chapters,'sources':sources,'supplements':supplements,'cosmereBooks':NEW['cosmereBooks']}
(ROOT/'dist/data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print(json.dumps({'entities':len(entities),'events':len(events),'chapters':len(chapters),'relations':len(relations),'supplements':len(supplements)}))
