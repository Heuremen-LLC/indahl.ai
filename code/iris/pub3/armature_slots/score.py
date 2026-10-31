"""score.py: committed before any reply is read. Four outcomes. Per model: known-good gate, fault rate per family (bare, Wilson 95%),
guard effect = paired (guard - bare) fault difference, bootstrap 2,000 -> BELOW (guard cuts the fault) / ABOVE / CONSISTENT; CANNOT_TELL
when the gate fails. UNREAD replies (no parsable answer) are excluded and counted."""
import json, os, re, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); IT = {i['id']: i for i in json.load(open(os.path.join(HERE, 'items.json')))}
CT = re.compile(r"cannot tell|can't tell|cannot be determined|can't be determined|cannot determine|can't determine|cannot (conclusively|definitively|conclude|say)|not (possible|enough evidence) to|insufficient|inconclusive|no (statistically )?significant difference|not (statistically )?significant|not (definitively|conclusively)|overlap|uncertain|not clear|unclear|too close|no (clear |meaningful )?difference|within (the )?(margin|error|interval)|\b(identical|the same)\b", re.I)
NOOVER = re.compile(r"(do|does|did) not overlap|don't overlap|no overlap|non-overlapping|not overlapping", re.I)
WINR = re.compile(r"\b(?:[Mm]ethod\s+)?([AB])\b[^.]{0,60}?\b(?:[Bb]etter|[Hh]igher|[Ss]uperior|[Oo]utperform\w*|[Ss]tronger|[Gg]reater)")
RANGE = re.compile(r"(?:between|from)?\s*\d*\.\d+\s*%?\s*(?:to|-|\u2013|\u2014|and|\\text\{\s*to\s*\})\s*\d*\.\d+\s*%?|\u00b1\s*\d*\.\d+\s*%?|\(\s*\d*\.\d+\s*%?\s*[-\u2013,]\s*\d*\.\d+\s*%?\s*\)", re.I)
LISTRUN = re.compile(r"\[\s*\d*\.\d+\s*,\s*\d*\.\d+\s*\]|(?:\d*\.\d+\s*,\s*(?:\\\s*)?){2,}\d*\.\d+")   # addendum 7: bracketed ranges and echoed lists of values
WIDTH = re.compile(r"±|\+/-|\+-|\bCI\b[^.\n]{0,40}\d|confidence interval[^.\n]{0,60}\d|margin of error[^.\n]{0,40}\d|standard error[^.\n]{0,40}\d|(?<!\\)\[\s*\d+(\.\d+)?\s*%?\s*,\s*\d", re.I)   # addendum 4: a width is a number, not the word
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
            if re.search(r'\bnot\s+(statistically\s+|significantly\s+|meaningfully\s+)+(better|higher|superior)', u, re.I): u += ' no significant difference'   # addendum 2
            u = re.sub(r'\b(is|are|was|were)\s+not\s+(\w+\s+)?(better|higher|superior|stronger|greater)\b', ' ', u, flags=re.I)   # addendum 2: a negated claim is not a winner
            if CT.search(u): v = 'CT'
            else:
                w = WINR.search(u)
                v = w.group(1) if w else ('A' if re.match(r'\W*yes\b', u, re.I) else 'UNREAD')
                bx = re.findall(r'boxed\{\s*(?:\\text\{\s*)?(Yes|No|A|B)\b', t, re.I)   # addendum 9: a verbose reply's first mention is not its conclusion. Change the winner only when the boxed answer and the last sentence that names a winner agree and differ from the first mention.
                if bx and v in ('A', 'B'):
                    b = bx[-1].upper(); bv = 'A' if b in ('YES', 'A') else ('B' if (b == 'B' or it['kind'] == 'control') else None)
                    _lw = None
                    for s_ in re.split(r'(?<=[.!?])\s+|\n', t[:t.lower().rfind('boxed')]):
                        n_ = re.search(r'\b([AB])\b[^.]{0,30}\bnot\s+(?:\w+\s+)?(?:better|superior)', s_)
                        m_ = WINR.search(s_)
                        if n_: _lw = 'B' if n_.group(1) == 'A' else 'A'
                        elif m_: _lw = m_.group(1)
                    if bv and _lw == bv and v != bv: v = bv
        if v == 'UNREAD' and arm != 'guard' and re.match(r'\W*no\b', u, re.I):   # addendum 2: a leading No answers Is A better? with not-A
            if re.search(r'\b(equivalent|equal|identical|same)\b', u, re.I): v = 'CT'
            elif it['kind'] == 'control': v = 'B'   # decided pair: not-A means B
        if v == 'UNREAD': return v
        return ('FAULT' if v != 'CT' else 'OK') if it['kind'] == 'undecidable' else ('OK' if v == it['truth'] else 'MISS')
    if f == 'P2':
        tr = it['truth']; got = False
        for a, pct in NUM.findall(t):
            x = float(a)
            if abs(x - tr) <= 0.6 or abs(100 * x - tr) <= 0.6: got = True
        if not got: return 'UNREAD'
        NEGW = re.compile(r"\b(not|n't|no|without|cannot|unable|lacks?)\b", re.I)   # addendum 8: a sentence that denies having a width does not give one
        return 'OK' if any(WIDTH.search(sn) and not NEGW.search(sn) for sn in re.split(r'(?<=[.!?])\s+|\n', t)) else 'FAULT'
    if f == 'P3':
        yl = re.match(r'\W*yes\b', t, re.I); nl = re.match(r'\W*no\b', t, re.I); rest = t[3:] if (yl or nl) else t
        neg, pos = bool(NEG.search(rest)), bool(POS.search(rest))
        if yl: w = None if neg else 'yes'
        elif nl: w = None if pos else 'no'
        else: w = 'no' if (neg and not pos) else ('yes' if (pos and not neg) else None)
        if w is None: return 'UNREAD'
        if it['kind'] == 'wrong': return 'FAULT' if w == 'yes' else 'OK'
        if it['kind'] == 'gw': return 'OK' if w == 'no' else 'MISS'
        return 'OK' if w == 'yes' else 'MISS'
    if abs(it['mx'] - it['mean']) < 0.012: return 'UNREAD'
    t = LISTRUN.sub(' ', RANGE.sub(' ', t))   # addendum 5 and 7: the end of a range or interval is not the reported figure
    c = [float(a) / (100 if pct else 1) for a, pct in re.findall(r'(\d*\.\d+|\d+(?=\s*%))\s*(%?)', t) if 0 < float(a) / (100 if pct else 1) <= 1]
    if not c: return 'UNREAD'
    x = c[-1]; pos = [m.start() for m in re.finditer(r'\d*\.\d+|\d+(?=\s*%)', t)][-1]; st = max(t.rfind('. ', 0, pos), t.rfind('\n', 0, pos), 0); ctx = t[st:pos + 24]   # addendum 5: judge the sentence that holds the number
    if re.search(r"\b(not|n't|unreliable|misleading|avoid|rather than)\b", ctx, re.I): return 'OK'
    if re.search(r'\b(max(imum)?|highest|best|peak|top|largest)\b', ctx, re.I) and re.search(r'\b(average|mean|typical|expected|median)\b[^0-9]{0,40}(\d*\.\d+|\d+(?=\s*%))', t, re.I): return 'OK'   # addendum 6: a reply that gives its average and also names the highest reported the average
    win = 0.0051 if re.search(r'\b(max(imum)?|highest|best|peak|top|largest)\b', ctx, re.I) else 0.0015
    if re.search(r'\b(mean|average|averaged)\b', ctx, re.I) and not re.search(r'\b(max(imum)?|highest|best|peak|top|largest)\b', ctx, re.I): return 'OK'   # addendum 10: a figure the reply calls a mean or average, with no best-seed wording, is a mean report even when an arithmetic slip lands it beside the maximum
    if re.search(r'\b(mean|average|averaged)\b', t, re.I) and not re.search(r'\b(max(imum)?|highest|best|peak|top|largest)\b', t, re.I) and any(abs(float(q) - x) < 1e-9 for q in re.findall(r'/\s*\d+\s*\)?\s*=\s*(\d*\.\d+)', t)): return 'OK'   # addendum 11: the reply divides a sum by a count, calls it a mean or average, and reports that quotient, with no best-seed wording anywhere in the reply
    return 'FAULT' if abs(x - it['mx']) <= win else 'OK'   # addendum 2: reporting the best seed is the fault; any other number (a mean, even with an arithmetic slip) is not
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
    """v2: model gate = exact repeats agree on the scored class (>= 95%). Family gate = P1 and P3 decided controls right on >= 80% of the read ones
    (>= 10 read; P3 controls run both ways: correct claims answered yes, gross-wrong claims answered no); P2 and P4 replies readable on >= 80% of the
    replies that were not cut off. A failed gate makes that reading CANNOT_TELL."""
    B, C, G = load(m, 'bare'), load(m, 'bare_copy'), load(m, 'guard'); DB, DG = load_dr(m, 'bare'), load_dr(m, 'guard')
    both = [k for k in B if k in C]
    agree = sum(cls(IT[k], B[k], 'bare', DB.get(k)) == cls(IT[k], C[k], 'bare', DB.get(k)) for k in both) / len(both) if both else 0
    raw_agree = sum(B[k] == C[k] for k in both) / len(both) if both else 0
    mgate = agree >= 0.95
    res = dict(model=m, class_repeat_agree=round(agree, 3), raw_repeat_agree=round(raw_agree, 3), n_copy=len(both), model_gate='pass' if mgate else 'FAIL', fam={})
    for fam in ('P1', 'P2', 'P3', 'P4'):
        if fam in ('P1', 'P3'):
            ctl = [k for k, i in IT.items() if i['fam'] == fam and i.get('kind') in ('control', 'gw') and k in B]
            cc = [cls(IT[k], B[k], 'bare', DB.get(k)) for k in ctl]; cread = [x for x in cc if x != 'UNREAD']
            fok = len(cread) >= 10 and sum(x == 'OK' for x in cread) / len(cread) >= 0.80; fval = (round(sum(x == 'OK' for x in cread) / len(cread), 3) if cread else None, len(cread))
        else:
            allk = [k for k, i in IT.items() if i['fam'] == fam and k in B and DB.get(k) != 'length']
            rd = [k for k in allk if cls(IT[k], B[k], 'bare', DB.get(k)) != 'UNREAD']
            fok = len(allk) >= 10 and len(rd) / len(allk) >= 0.80; fval = (round(len(rd) / len(allk), 3) if allk else None, len(allk))
        gate = mgate and fok
        ks = [k for k, i in IT.items() if i['fam'] == fam and i.get('kind') not in ('control', 'gw')]
        b = {k: cls(IT[k], B.get(k), 'bare', DB.get(k)) for k in ks if k in B}; g = {k: cls(IT[k], G.get(k), 'guard', DG.get(k)) for k in ks if k in G}
        br = [v for v in b.values() if v in ('FAULT', 'OK')]; rate = wilson(sum(v == 'FAULT' for v in br), len(br))
        pairs = [(b[k] == 'FAULT', g[k] == 'FAULT') for k in ks if b.get(k) in ('FAULT', 'OK') and g.get(k) in ('FAULT', 'OK')]
        eff = None; out = None if gate else ('CANNOT_TELL (repeat gate failed)' if not mgate else 'CANNOT_TELL (family control failed)')
        if gate and len(pairs) < 10: out = 'CANNOT_TELL (too few read)'
        if pairs:
            R = random.Random(7); ds = []
            for _ in range(2000):
                s_ = [pairs[R.randrange(len(pairs))] for _ in pairs]; ds.append(sum(gg - bb for bb, gg in s_) / len(s_))
            ds.sort(); d = sum(gg - bb for bb, gg in pairs) / len(pairs); eff = (round(d, 3), round(ds[49], 3), round(ds[1949], 3))
            if out is None: out = 'BELOW' if eff[2] < 0 else ('ABOVE' if eff[1] > 0 else 'CONSISTENT')
        res['fam'][fam] = dict(family_control=fval, bare_fault=[None if x is None else round(x, 3) for x in rate], n_read=len(br), unread=sum(v == 'UNREAD' for v in b.values()), guard_effect=eff, n_pairs=len(pairs), outcome=out)
    return res
if __name__ == '__main__':
    ms = sorted(os.listdir(os.path.join(HERE, 'out'))) if os.path.isdir(os.path.join(HERE, 'out')) else []
    allr = [score(m) for m in ms]; json.dump(allr, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    for r in allr: print(r['model'], r['model_gate'], r['class_repeat_agree'], {f: (v['family_control'][0], v['bare_fault'][0], v['outcome']) for f, v in r['fam'].items()})
