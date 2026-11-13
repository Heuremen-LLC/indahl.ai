"""Positive control for the matcher: real twins of gold items = other DOIs in the OpenAlex family of a gold work (journal, proceedings, Zenodo versions),
fetched as their own records from Crossref or DataCite. The twin record carries its own title, authors and abstract and no family link."""
import json,re,os,time,html,urllib.request
from fetch_meta import *
g=json.load(open(S+'/data/gold_items.json')); out=[]
def clean(t): return html.unescape(re.sub(r'<[^>]+>',' ',t or '')).strip()
for i in g:
    if not i['link']: continue
    m=meta(i['link'])
    for d in [f for f in m['family'] if f.startswith('10.') and not f.startswith('10.48550') and f!=doi_of(i['link'])][:2]:
        try:
            if d.startswith('10.5281/'):
                w=get('https://api.datacite.org/dois/'+d)['data']['attributes']; t=(w.get('titles') or [{}])[0].get('title'); au=[(c.get('name') or '') for c in w.get('creators',[])]
                ab=' '.join(x.get('description','') for x in w.get('descriptions',[]) if x.get('descriptionType')=='Abstract')
                r={'title':t,'authors':au,'abstract':clean(ab) or None}
            else:
                w=get('https://api.crossref.org/works/'+d)['message']; r={'title':clean((w.get('title') or [''])[0]),'authors':[(a.get('given','')+' '+a.get('family','')).strip() for a in w.get('author',[])],'abstract':clean(w.get('abstract')) or None}
            time.sleep(0.4)
        except Exception as e: continue
        if r['title']: out.append({'gold_id':i['id'],'twin_doi':d,'kind':'zenodo_version' if d.startswith('10.5281/') else 'journal_or_proceedings','record':dict(r,family=[])})
json.dump(out,open(S+'/data/twins.json','w'),indent=1); print(len(out),'twin records')
