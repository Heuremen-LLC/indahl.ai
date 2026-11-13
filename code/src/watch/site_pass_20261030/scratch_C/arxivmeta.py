import re,glob,json,html,os,sys
sys.path.insert(0,'.')
import parse as P
import xml.etree.ElementTree as ET
ns={'a':'http://www.w3.org/2005/Atom'}
meta={}
for f in sorted(glob.glob('arxiv_api_*.xml')):
    root=ET.parse(f).getroot()
    for e in root.findall('a:entry',ns):
        id_=e.find('a:id',ns).text.split('/abs/')[1]
        base=re.sub(r'v\d+$','',id_)
        meta[base]={'id':id_,'title':' '.join(e.find('a:title',ns).text.split()),'authors':[a.find('a:name',ns).text for a in e.findall('a:author',ns)],
                    'published':e.find('a:published',ns).text,'updated':e.find('a:updated',ns).text,
                    'aff':[ (x.text or '') for x in e.findall('.//{http://arxiv.org/schemas/atom}affiliation')]}
json.dump(meta,open('arxiv_meta.json','w'),indent=1)
print(len(meta))
pages={os.path.basename(f)[:-5]:P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
T=P.text
for n,p in pages.items():
    s=p['sections']
    work=s['Work']
    m=re.search(r'arxiv\.org/abs/([^"]+)"',work)
    if not m: continue
    aid=m.group(1); base=re.sub(r'v\d+$','',aid)
    mt=meta.get(base)
    if not mt: print('NO META',n,aid); continue
    ptitle=T(re.findall(r'<a [^>]*>(.*?)</a>',work,re.S)[0])
    org=T(re.search(r'<b>(.*?)</b>',work,re.S).group(1))
    # for research table: link text is paper title
    if not ptitle.startswith('arXiv'):
        a=re.sub(r'[^a-z0-9]','',ptitle.lower()); b=re.sub(r'[^a-z0-9]','',mt['title'].lower())
        if a!=b: print('TITLE DIFF',n,'|page:',ptitle[:110],'|arxiv:',mt['title'][:110])
