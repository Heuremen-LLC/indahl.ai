import json, numpy as np, datetime as D
R='/Users/heuremen/bones-forge/arxiv_one_readout/'
def bits(arr, nbits):
    return np.unpackbits(np.asarray(arr, np.uint8), axis=1, bitorder='big')[:, ::-1][:, :nbits].astype(np.int8)
def qprops(props):
    """per-qubit dict name -> (value, date) """
    out=[]
    for q in props['qubits']:
        d={}
        for p in q: d[p['name']]=(p['value'], p.get('date'))
        out.append(d)
    return out
def pt(s): return D.datetime.fromisoformat(s)
def boot_median(x, B=2000, seed=1):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)<5: return np.nan, (np.nan,np.nan), len(x)
    rng=np.random.default_rng(seed); b=np.median(rng.choice(x,(B,len(x))),axis=1)
    return float(np.median(x)), tuple(np.percentile(b,[2.5,97.5])), len(x)
def outcome(ci):
    lo,hi=ci
    if not np.isfinite(lo): return 'CANNOT_TELL'
    return 'ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'

def edges_from(props):
    return sorted({tuple(sorted(g['qubits'])) for g in props['gates'] if g['gate']=='cz' and len(g['qubits'])==2})
def zz_map(props):
    """edge -> published zz in kHz (general field zz_<a><b>, a<b or b<a tried both)."""
    ed=edges_from(props); idx={}
    for a,b in ed:
        for n in (f'{a}{b}',f'{b}{a}'): idx.setdefault(n,[]).append((a,b))
    out={}; amb=0; miss=0
    for g in props.get('general') or []:
        if g['name'].startswith('zz_'):
            k=g['name'][3:]
            c=idx.get(k)
            if not c: miss+=1; continue
            if len(set(c))>1: amb+=1; continue
            out[c[0]]=g['value']*1e6  # GHz -> kHz
    return out,amb,miss,len(ed)
