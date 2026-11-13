"""Referee: position-based NCHS parse with PyMuPDF (independent of the desk's text-order parse)."""
import fitz, json, re, sys
F='/Users/heuremen/bones-forge/fidelity_index/raw/'
def parse(f):
    p=fitz.open(f)[0]; W=p.get_text('words')
    hdr=[w for w in W if re.fullmatch(r'20[0-2]\d',w[4]) and w[1]<75]
    hdr=sorted(hdr,key=lambda w:w[0]); cx=[(w[0]+w[2])/2 for w in hdr]; assert len(cx)==24,len(cx)
    body=[w for w in W if w[1]>=68 and not re.fullmatch(r'20[0-2]\d',w[4]) or w[1]>=75]
    rows={}
    for w in body:
        ym=round((w[1]+w[3])/2/3)  # cluster
        rows.setdefault(ym,[]).append(w)
    # merge adjacent clusters by sorting
    ys=sorted(rows); merged=[]; 
    for y in ys:
        if merged and y-merged[-1][0]<=1: merged[-1][1]+=rows[y]; merged[-1][0]=y
        else: merged.append([y,list(rows[y])])
    out={}
    for y,ws in merged:
        name=' '.join(w[4] for w in sorted(ws,key=lambda w:w[0]) if w[0]<110 and not re.fullmatch(r'[\d,\-]+',w[4]))
        vals=[None]*24; cnt=0
        for w in ws:
            if re.fullmatch(r'[\d,]+|-',w[4]):
                c=(w[0]+w[2])/2; i=min(range(24),key=lambda k:abs(cx[k]-c)); 
                if w[4]!='-': vals[i]=int(w[4].replace(',',''))
                cnt+=1
        if name and cnt: out[name]=vals
    return out
if __name__=='__main__':
    res={'divorce':parse(F+'div23.pdf'),'marriage':parse(F+'mar23.pdf')}
    json.dump(res,open('nchs_pos.json','w'))
    d=json.load(open('/Users/heuremen/bones-forge/fidelity_index/data/nchs_counts.json'))
    for k in res:
        print(k,len(res[k]),sorted(set(d[k])^set(res[k])))
        diff=[(s,2000+i,d[k][s][i],res[k].get(s,[None]*24)[i]) for s in d[k] for i in range(24) if d[k][s][i]!=res[k].get(s,[None]*24)[i]]
        print(' diffs',len(diff),diff[:20])
