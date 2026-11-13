"""Rebuild WALL_S3.md from rows/*.md. Class = first word(s) after the S3 heading's colon; anything else is READ BY HAND."""
import re,glob,os,collections
out=[];cnt=collections.Counter();hand=[]
for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__),'*.md'))):
    slug=os.path.basename(f)[:-3]
    if slug=='SCHOOL_LIST': continue
    txt=open(f).read()
    m=re.search(r'^[#\- ]*S3[^:\n]*:\s*(.*)$',txt,re.M)
    h=re.search(r'^#+ *S3 data released *\n+(.*)$',txt,re.M)
    if not m and h: txt=txt.replace(h.group(0),'- S3: '+h.group(1).lstrip('- ')); m=re.search(r'^[#\- ]*S3[^:\n]*:\s*(.*)$',txt,re.M)
    if not m: cnt['NO S3 LINE']+=1; hand.append(slug); out.append(f'- {slug}: [NO S3 LINE]'); continue
    body=m.group(1).strip(); hd=m.group(0)
    head=(re.sub(r'^[#\- ]*S3[^:\n]*:','',hd).strip() or body)[:40].upper()
    if 'data released: none' in hd.lower() or head.startswith(('NONE','NO ','INSTITUTIONAL DOCUMENTS: NONE','NOT ')): c='NONE (institutional)'
    elif head.startswith(('AGGREGATE','PARTIAL','INSTRUMENT')) or 'data released: aggregate' in hd.lower() or 'data released: partial' in hd.lower() or 'data released: instrument' in hd.lower(): c='AGGREGATES / INSTRUMENT ONLY'
    else: c='READ BY HAND'; hand.append(slug)
    cnt[c]+=1; out.append(f'- {slug}: [{c}] {m.group(0).strip()[:300]}')
print('\n'.join(out)); print(); print('Counts:',dict(cnt)); print('READ BY HAND:',hand)
