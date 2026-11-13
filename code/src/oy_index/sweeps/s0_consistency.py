"""Compare each school's S0 bin in WALL_S0.md with the S0 line in its own row file. Prints mismatches for hand review."""
import re,glob,os
B=os.path.expanduser('~/bones-forge/oy_index/')
LV=['MEASURED-POLICY','TRIAL REPORTED WITHOUT NUMBERS','PLANNED ONLY','USAGE-OR-ATTITUDE ONLY','NONE FOUND']
tab={}
for l in open(B+'WALL_S0.md'):
    if l.startswith('| ') and not l.startswith('| school'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        lv=next(k for k in LV if c[1].startswith(k))
        for n in c[0].split(','): tab[n.strip()]=lv
def rowlv(t):
    m=re.search(r'^[#\- ]*S0[^:\n]*:\s*(.{0,200})',t,re.M)
    if not m: return None,''
    s=m.group(0).upper()
    found=[k for k in ['MEASURED','TRIAL','PLANNED','USAGE','NONE FOUND'] if k in s]
    return found,m.group(0)[:200]
for f in sorted(glob.glob(B+'rows/*.md')):
    slug=os.path.basename(f)[:-3]
    if slug=='SCHOOL_LIST': continue
    t=open(f).read(); found,line=rowlv(t); w=tab.get(slug)
    if w is None: print('NOT IN TABLE',slug); continue
    key={'MEASURED-POLICY':'MEASURED','TRIAL REPORTED WITHOUT NUMBERS':'TRIAL','PLANNED ONLY':'PLANNED','USAGE-OR-ATTITUDE ONLY':'USAGE','NONE FOUND':'NONE FOUND'}[w]
    if not found or key!=found[0]: print(f'{slug:14s} wall={w:32s} row={found} | {line}')
