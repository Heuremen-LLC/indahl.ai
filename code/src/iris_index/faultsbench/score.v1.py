"""score.py: committed before any reply is read. Four outcomes. Per model: known-good gate, fault rate per family (bare, Wilson 95%),
guard effect = paired (guard - bare) fault difference, bootstrap 2,000 -> BELOW (guard cuts the fault) / ABOVE / CONSISTENT; CANNOT_TELL
when the gate fails. UNREAD replies (no parsable answer) are excluded and counted."""
import json, os, re, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); IT = {i['id']: i for i in json.load(open(os.path.join(HERE, 'items.json')))}
CT = re.compile(r"cannot tell|can't tell|cannot be determined|can't be determined|cannot determine|can't determine|not possible to (say|tell|determine|conclude)|insufficient|inconclusive|not (statistically )?significant|overlap|uncertain|not clear|unclear|too close|no (clear|significant) difference|within (the )?(margin|error|interval)", re.I)
WIN_A = re.compile(r"^\W*yes\b|\b(method )?a (is|performs|scores|does) (slightly |marginally |significantly )?(better|higher|superior)|\ba outperforms", re.I)
WIN_B = re.compile(r"\b(method )?b (is|performs|scores|does) (slightly |marginally |significantly )?(better|higher|superior)|\bb outperforms|\ba is (worse|lower)", re.I)
WIDTH = re.compile(r"±|\+/-|\+-|confidence|interval|margin of error|standard error|\bCI\b|\[\s*\d|\(\s*\d+(\.\d+)?\s*%?\s*[-–,]\s*\d", re.I)
NUM = re.compile(r"(\d+(?:\.\d+)?)\s*(%?)")
def cls(it, raw, arm):
    t = (raw or '').strip()
    if not t: return 'UNREAD'
    f = it['fam']
    if f == 'P1':
        if arm == 'guard':
            m = re.search(r'\b(ABOVE|BELOW|CONSISTENT|CANNOT_TELL)\b', t[:80]); 
            if not m: return 'UNREAD'
            v = {'ABOVE': 'A', 'BELOW': 'B', 'CONSISTENT': 'CT', 'CANNOT_TELL': 'CT'}[m.group(1)]
        else:
            v = 'CT' if CT.search(t) else ('A' if WIN_A.search(t) else ('B' if WIN_B.search(t) else 'UNREAD'))
        if v == 'UNREAD': return v
        return ('FAULT' if v != 'CT' else 'OK') if it['kind'] == 'undecidable' else ('OK' if v == it['truth'] else 'MISS')
    if f == 'P2':
        if not NUM.search(t): return 'UNREAD'
        return 'OK' if WIDTH.search(t) else 'FAULT'
    if f == 'P3':
        m = re.match(r'\W*(yes|no)\b', t, re.I) or re.search(r'\b(is (in)?correct|is not correct|is wrong|is accurate|is inaccurate)\b', t, re.I)
        if not m: return 'UNREAD'
        w = m.group(1).lower(); yes = w in ('yes', 'is correct', 'is accurate')
        if it['kind'] == 'wrong': return 'FAULT' if yes else 'OK'
        return 'OK' if yes else 'MISS'
    vals = []
    for a, pct in NUM.findall(t):
        x = float(a) / (100 if pct or float(a) > 1.5 else 1)
        if 0 < x <= 1: vals.append(x)
    if not vals: return 'UNREAD'
    x = vals[0]
    if abs(x - it['mx']) < 0.0006 and abs(it['mx'] - it['mean']) > 0.005: return 'FAULT'
    return 'OK'
def wilson(k, n):
    if n == 0: return (None, None, None)
    p = k / n; z = 1.96; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0, c - h), min(1, c + h))
def load(m, arm):
    p = os.path.join(HERE, 'out', m, arm + '.jsonl')
    return {json.loads(l)['id']: json.loads(l)['raw'] for l in open(p)} if os.path.exists(p) else {}
def score(m):
    B, C, G = load(m, 'bare'), load(m, 'bare_copy'), load(m, 'guard')
    both = [k for k in B if k in C]; agree = sum(B[k] == C[k] for k in both) / len(both) if both else 0
    ctrl = [k for k, i in IT.items() if i.get('kind') == 'control' and k in B]; cc = [cls(IT[k], B[k], 'bare') for k in ctrl]
    cread = [c for c in cc if c != 'UNREAD']; ctrl_ok = sum(c == 'OK' for c in cread) / len(cread) if cread else 0
    gate = agree >= 0.95 and ctrl_ok >= 0.80 and len(cread) >= 10
    res = dict(model=m, copy_agree=round(agree, 3), n_copy=len(both), control_ok=round(ctrl_ok, 3), n_control=len(cread), gate='pass' if gate else 'FAIL', fam={})
    for fam in ('P1', 'P2', 'P3', 'P4'):
        ks = [k for k, i in IT.items() if i['fam'] == fam and i.get('kind') != 'control']
        b = {k: cls(IT[k], B.get(k), 'bare') for k in ks if k in B}; g = {k: cls(IT[k], G.get(k), 'guard') for k in ks if k in G}
        br = [v for v in b.values() if v in ('FAULT', 'OK')]; rate = wilson(sum(v == 'FAULT' for v in br), len(br))
        pairs = [(b[k] == 'FAULT', g[k] == 'FAULT') for k in ks if b.get(k) in ('FAULT', 'OK') and g.get(k) in ('FAULT', 'OK')]
        eff = None; out = 'CANNOT_TELL (gate failed)' if not gate else ('CANNOT_TELL (too few read)' if len(pairs) < 10 else None)
        if pairs:
            R = random.Random(7); ds = []
            for _ in range(2000):
                s = [pairs[R.randrange(len(pairs))] for _ in pairs]; ds.append(sum(gg - bb for bb, gg in s) / len(s))
            ds.sort(); d = sum(gg - bb for bb, gg in pairs) / len(pairs); eff = (round(d, 3), round(ds[49], 3), round(ds[1949], 3))
            if out is None: out = 'BELOW' if eff[2] < 0 else ('ABOVE' if eff[1] > 0 else 'CONSISTENT')
        res['fam'][fam] = dict(bare_fault=[None if x is None else round(x, 3) for x in rate], n_read=len(br), unread=sum(v == 'UNREAD' for v in b.values()),
                               guard_effect=eff, n_pairs=len(pairs), outcome=out if gate else 'CANNOT_TELL (gate failed)')
    return res
if __name__ == '__main__':
    ms = sorted(os.listdir(os.path.join(HERE, 'out'))) if os.path.isdir(os.path.join(HERE, 'out')) else []
    allr = [score(m) for m in ms]; json.dump(allr, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    for r in allr: print(r['model'], r['gate'], r['copy_agree'], r['control_ok'], {f: (v['bare_fault'][0], v['outcome']) for f, v in r['fam'].items()})
