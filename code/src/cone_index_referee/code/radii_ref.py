# Referee: re-derive cone radii from the archived HTML copies. Own parser.
import re, glob, json, os, collections
D='/Users/heuremen/bones-forge/cone_index/data/raw/docs/'
HRS=[12,24,36,48,60,72,96,120]
def strip(x): return re.sub(r'\s+',' ',re.sub(r'<[^>]*>',' ',x)).strip()
def parse(path):
    t=open(path,errors='replace').read()
    m=re.findall(r'cones?\s+in\s+(\d{4})',t,flags=re.S)
    if not m: return None
    yr=int(m[0])
    rows=collections.OrderedDict(); order=[]
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',t,flags=re.S|re.I):
        cells=[strip(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',tr,flags=re.S|re.I)]
        if len(cells)>=3 and cells[0].isdigit() and int(cells[0]) in HRS and all(re.fullmatch(r'\d+',c) for c in cells[1:]):
            h=int(cells[0])
            if h in rows: continue  # first table only
            rows[h]=[int(c) for c in cells[1:]]
    ncol=set(len(v) for v in rows.values())
    return yr,rows,ncol
def main():
    files=sorted(glob.glob(D+'aboutcone_wb/*.html'))+[D+'aboutcone.shtml']
    byyear=collections.defaultdict(list)
    for f in files:
        r=parse(f)
        if r is None: print('no year',os.path.basename(f)); continue
        yr,rows,ncol=r
        ts=os.path.basename(f).split('.')[0]
        if f.endswith('aboutcone.shtml'): ts='live'
        byyear[yr].append((ts,rows,ncol))
    out={}; dis={}
    for yr,L in sorted(byyear.items()):
        L.sort(key=lambda x:(x[0]=='live',x[0]))
        ts,rows,ncol=L[0]
        al={str(h):rows[h][0] for h in rows}; ep={str(h):rows[h][1] for h in rows}
        out[yr]={'AL':al,'EP':ep,'first_copy':ts,'ncols':sorted(ncol),'nrows':len(rows)}
        for ts2,r2,_ in L[1:]:
            if r2!=rows: dis.setdefault(yr,[]).append(ts2)
    json.dump({'radii':out,'disagree':dis},open('/Users/heuremen/bones-forge/cone_index_referee/out/radii_ref.json','w'),indent=1)
    desk=json.load(open('/Users/heuremen/bones-forge/cone_index/data/radii.json'))
    for yr in sorted(out):
        d=desk.get(str(yr))
        if d is None: print(yr,'not in desk'); continue
        okal=d['AL']==out[yr]['AL']; okep=d['EP']==out[yr]['EP']
        print(yr,out[yr]['ncols'],'AL same' if okal else 'AL DIFF','EP same' if okep else 'EP DIFF',out[yr]['first_copy'],d['first_copy'])
    print('desk years not mine',set(desk)-set(map(str,out)))
    print('disagreements among copies naming same year',dis)
main()
