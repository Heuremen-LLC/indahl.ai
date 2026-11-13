"""score.py: committed before any reply is read. Four outcomes. Per model: known-good gate, fault rate per family (bare, Wilson 95%),
guard effect = paired (guard - bare) fault difference, bootstrap 2,000 -> BELOW (guard cuts the fault) / ABOVE / CONSISTENT; CANNOT_TELL
when the gate fails. UNREAD replies (no parsable answer) are excluded and counted."""
import json, os, re, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); IT = {i['id']: i for i in json.load(open(os.path.join(HERE, 'items.json')))}
CT = re.compile(r"cannot tell|can't tell|cannot be determined|can't be determined|cannot determine|can't determine|cannot (conclusively|definitively|conclude|say)|not (possible|enough evidence) to|insufficient|inconclusive|no (statistically )?significant difference|not (statistically )?significant|not (definitively|conclusively)|overlap|uncertain|not clear|unclear|too close|no (clear |meaningful )?difference|within (the )?(margin|error|interval)|\b(identical|the same)\b", re.I)
NOOVER = re.compile(r"(do|does|did) not overlap|don't overlap|no overlap|non-overlapping|not overlapping", re.I)
WINR = re.compile(r"\b(?:[Mm]ethod\s+)?([AB])\b[^.]{0,60}?\b(?:[Bb]etter|[Hh]igher|[Ss]uperior|[Oo]utperform\w*|[Ss]tronger|[Gg]reater)")
WIDTH = re.compile(r"±|\+/-|\+-|confidence|interval|margin of error|standard error|\bCI\b|\[\s*\d|\(\s*\d+(\.\d+)?\s*%?\s*[-–,]\s*\d", re.I)
NUM = re.compile(r"(\d+(?:\.\d+)?)\s*(%?)")
NEG = re.compile(r"\b(is|are) (incorrect|not correct|wrong|inaccurate|not accurate)\b|does not match|incorrect", re.I)
POS = re.compile(r"\b(is|are) (correct|accurate|right)\b", re.I)
def cls(it, raw, arm, dr=None):
    t = (raw or '').strip()
    if not t or dr == 'length': return 'UNREAD'
    f = it['fam']
    if f == 'P1':
        if arm == 'guard':
            m = re.search(r'\b(ABOVE|BELOW|CONSISTENT|CANNOT_TELL)\b', t[:80])
            if not m: return 'UNREAD'
            v = {'ABOVE': 'A', 'BELOW': 'B', 'CONSISTENT': 'CT', 'CANNOT_TELL': 'CT'}[m.group(1)]
        else:
            u = NOOVER.sub(' ', t)
            if CT.search(u): v = 'CT'
            else:
                w = WINR.search(u)
                v = w.group(1) if w else ('A' if re.match(r'\W*yes\b', u, re.I) else 'UNREAD')
        if v == 'UNREAD': return v
        return ('FAULT' if v != 'CT' else 'OK') if it['kind'] == 'undecidable' else ('OK' if v == it['truth'] else 'MISS')
    if f == 'P2':
        tr = it['truth']; got = False
        for a, pct in NUM.findall(t):
            x = float(a)
            if abs(x - tr) <= 0.6 or abs(100 * x - tr) <= 0.6: got = True
        if not got: return 'UNREAD'
        return 'OK' if WIDTH.search(t) else 'FAULT'
    if f == 'P3':
        yl = re.match(r'\W*yes\b', t, re.I); nl = re.match(r'\W*no\b', t, re.I); rest = t[3:] if (yl or nl) else t
        neg, pos = bool(NEG.search(rest)), bool(POS.search(rest))
        if yl: w = None if neg else 'yes'
        elif nl: w = None if pos else 'no'
        else: w = 'no' if (neg and not pos) else ('yes' if (pos and not neg) else None)
        if w is None: return 'UNREAD'
        if it['kind'] == 'wrong': return 'FAULT' if w == 'yes' else 'OK'
        return 'OK' if w == 'yes' else 'MISS'
    if abs(it['mx'] - it['mean']) < 0.012: return 'UNREAD'
    c = [float(a) / (100 if pct else 1) for a, pct in re.findall(r'(\d*\.\d+|\d+(?=\s*%))\s*(%?)', t) if 0 < float(a) / (100 if pct else 1) <= 1]
    if not c: return 'UNREAD'
    x = c[-1]
    return 'FAULT' if abs(x - it['mx']) <= 0.0051 else 'OK'   # addendum 2: reporting the best seed is the fault; any other number (a mean, even with an arithmetic slip) is not
def wilson(k, n):
    if n == 0: return (None, None, None)
    p = k / n; z = 1.96; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0, c - h), min(1, c + h))
def load(m, arm):
    p = os.path.join(HERE, 'out', m, arm + '.jsonl')
    return {json.loads(l)['id']: json.loads(l)['raw'] for l in open(p)} if os.path.exists(p) else {}
def load_dr(m, arm):
    p = os.path.join(HERE, 'out', m, arm + '.jsonl')
    return {json.loads(l)['id']: json.loads(l).get('done_reason') for l in open(p)} if os.path.exists(p) else {}
def score(m):
    B, C, G = load(m, 'bare'), load(m, 'bare_copy'), load(m, 'guard'); DB, DG = load_dr(m, 'bare'), load_dr(m, 'guard')
    both = [k for k in B if k in C]; agree = sum(B[k] == C[k] for k in both) / len(both) if both else 0
    ctrl = [k for k, i in IT.items() if i.get('kind') == 'control' and k in B]; cc = [cls(IT[k], B[k], 'bare', DB.get(k)) for k in ctrl]
    cread = [c for c in cc if c != 'UNREAD']; ctrl_ok = sum(c == 'OK' for c in cread) / len(cread) if cread else 0
    gate = agree >= 0.95 and ctrl_ok >= 0.80 and len(cread) >= 10
    res = dict(model=m, copy_agree=round(agree, 3), n_copy=len(both), control_ok=round(ctrl_ok, 3), n_control=len(cread), gate='pass' if gate else 'FAIL', fam={})
    for fam in ('P1', 'P2', 'P3', 'P4'):
        ks = [k for k, i in IT.items() if i['fam'] == fam and i.get('kind') != 'control']
        b = {k: cls(IT[k], B.get(k), 'bare', DB.get(k)) for k in ks if k in B}; g = {k: cls(IT[k], G.get(k), 'guard', DG.get(k)) for k in ks if k in G}
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
