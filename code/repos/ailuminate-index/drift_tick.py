#!/usr/bin/env python3
"""drift_tick.py: AILUMINATE drift tests F to J per PLAN_ADDENDUM_drift.md. Reads only stored data (data/reads.jsonl, data/raw). No network. Writes summary_drift.json. Never publishes.
Run: python3 drift_tick.py --draft   (--draft is needed while the addendum is not committed)"""
import os, sys, re, json, io, html, hashlib, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
CATS = ['Violent Crimes', 'Sex-Related Crimes', 'Child Sexual Exploitation', 'Suicide and Self-Harm', 'Indiscriminate Weapons', 'Intellectual Property', 'Defamation', 'Non-Violent Crimes', 'Hate', 'Privacy', 'Specialized Advice', 'Sexual Content']
KEYS = ['overall'] + CATS
NR = K.NOTHING_RETURNED
LABEL_RX = re.compile(r'Technical labels\s*:?\s*AILuminate\s+(\w+)\s+(\d+(?:\.\d+)*)\s*·\s*Problem Set\s+([\d.]+)[^·]*·\s*evaluator\s+v([\d.]+)')
STMT_RX = [('Technical labels', r'Technical labels\s*:?\s*AILuminate Safety.*?English \(US\)\.'),
           ('Release notes (new components)', r'The Safety 1\.\d(?:\.\d)? benchmark introduces three new components.*?single reference system\.'),
           ('Only results labeled', r'Only results labeled.*?not comparable\.'),
           ('Reference set', r'The composition of the reference set.*?previously tested systems\.'),
           ('Run started', r'MLCommons began running.*?(?:the run is ongoing|ongoing)\.')]

def parse_label(text):
    """-> 'Safety 1.2.1 | Problem Set 2.0 | evaluator v1.4' from the Technical labels line of a report, or None"""
    m = LABEL_RX.search(re.sub(r'[ \t]+', ' ', text.replace('\n', ' ')))
    return '%s %s | Problem Set %s | evaluator v%s' % m.groups() if m else None
def page_text(raw):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', raw, flags=re.S); t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(re.sub(r'\s+', ' ', t))
def page_statements(raw):
    t = page_text(raw); out = {}
    for n, rx in STMT_RX:
        m = re.search(rx, t); out[n] = m.group(0).strip() if m else None
    return out
def oc_share(lo, hi): return K.ABOVE if lo > 0.05 else (K.CONSISTENT if hi < 0.15 else K.CANNOT_TELL)
def share_block(k, n):
    if n == 0: return dict(of=0, n=0, share=None, share_lo=0.0, share_hi=1.0, outcome=NR)
    lo, hi = K.wilson(k, n); return dict(of=n, n=k, share=round(k / n, 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc_share(lo, hi))
def oc_dir(up, down):
    n = up + down
    if n < 30: return K.CANNOT_TELL
    lo, hi = K.wilson(up, n)
    return K.ABOVE if lo > 0.5 else (K.BELOW if hi < 0.5 else (K.CONSISTENT if lo >= 0.35 and hi <= 0.65 else K.CANNOT_TELL))

def analyse(reads, labels, pages):
    """reads: list of dict(stamp, t, systems{name: dict(release, overall, cats)}). labels: {(stamp, name): label or None}. pages: {stamp: {statement: sentence or None}}.
    -> dict of tests F G H I J"""
    def vals(v): return [v.get('overall')] + [(v.get('cats') or {}).get(c) for c in CATS]
    seq = {}   # name -> list of (stamp, label, values, release)
    for rd in reads:
        for n, v in rd['systems'].items():
            lab = labels.get((rd['stamp'], n))
            if lab is None: continue
            seq.setdefault(n, []).append((rd['stamp'], lab, vals(v), v.get('release')))
    unreadable = sum(1 for rd in reads for n in rd['systems'] if labels.get((rd['stamp'], n)) is None)
    # F
    f_units = {n: s for n, s in seq.items() if len(s) >= 2}; f_chg = sorted(n for n, s in f_units.items() if any(x[1] != s[0][1] for x in s))
    tuples = {}
    for rd in reads:
        for n in rd['systems']:
            lab = labels.get((rd['stamp'], n))
            if lab is None: continue
            e = tuples.setdefault(lab, dict(first_read=rd['stamp'], last_read=rd['stamp'], latest_systems=0)); e['last_read'] = rd['stamp']
    latest = reads[-1] if reads else None
    for n in (latest['systems'] if latest else {}):
        lab = labels.get((latest['stamp'], n))
        if lab: tuples[lab]['latest_systems'] += 1
    F = share_block(len(f_chg), len(f_units)); F.update(changed=f_chg, label_tuples=tuples, label_tuple_count=len(tuples), reports_without_readable_label=unreadable)
    # G
    per_sys = {}; tot = dict(up=0, down=0, same=0); per_cat = {k: dict(up=0, down=0, same=0) for k in KEYS}
    for n, s in seq.items():
        l0, l1 = s[0][1], s[-1][1]
        if l0 == l1: continue
        a = s[0][2]; b = s[-1][2]; c = dict(up=0, down=0, same=0)
        for k, x, y in zip(KEYS, a, b):
            if x is None or y is None: continue
            d = 'up' if y > x else ('down' if y < x else 'same'); c[d] += 1; per_cat[k][d] += 1; tot[d] += 1
        per_sys[n] = dict(from_label=l0, to_label=l1, from_read=s[0][0], to_read=s[-1][0], **c)
    if not per_sys: G = dict(outcome=NR, systems=0, why='no system has been read under two label tuples')
    else:
        moved = tot['up'] + tot['down']; lo, hi = K.wilson(tot['up'], moved) if moved else (0.0, 1.0)
        G = dict(outcome=oc_dir(tot['up'], tot['down']), systems=len(per_sys), up=tot['up'], down=tot['down'], same=tot['same'], moved=moved, share_up=round(tot['up'] / moved, 4) if moved else None, share_up_lo=round(lo, 4), share_up_hi=round(hi, 4), per_system=per_sys, per_category=per_cat)
    # H: unit = system and label tuple, at least two reads under it
    units = {}
    for n, s in seq.items():
        for x in s: units.setdefault((n, x[1]), []).append(x)
    h_units = {k: v for k, v in units.items() if len(v) >= 2}; h_chg = []
    for (n, lab), v in sorted(h_units.items()):
        diff = [k for k, a, b in zip(KEYS, v[0][2], v[-1][2]) if a != b]
        if v[-1][3] != v[0][3]: diff.append('release')
        if diff: h_chg.append(dict(system=n, label=lab, differs=diff, first_read=v[0][0], now_read=v[-1][0], first=dict(zip(KEYS, v[0][2]), release=v[0][3]), now=dict(zip(KEYS, v[-1][2]), release=v[-1][3])))
    H_ = share_block(len(h_chg), len(h_units)); H_.update(changed=h_chg)
    # I: earlier tuples are all tuples except the newest one (the one first seen last)
    dropped = sorted(n for n in seq if latest and n not in latest['systems'])
    order = sorted(tuples, key=lambda t: (tuples[t]['first_read'], t)); earlier = order[:-1]
    if not earlier: I = dict(outcome=NR, why='only one label tuple has been seen', earlier_tuples=[], dropped_systems=dropped, dropped_n=len(dropped))
    else:
        wd = [t for t in earlier if tuples[t]['latest_systems'] == 0]; I = share_block(len(wd), len(earlier))
        I.update(earlier_tuples=[dict(label=t, status='WITHDRAWN' if tuples[t]['latest_systems'] == 0 else 'STILL_PUBLISHED', first_read=tuples[t]['first_read'], last_read=tuples[t]['last_read'], systems_in_latest_read=tuples[t]['latest_systems']) for t in earlier], dropped_systems=dropped, dropped_n=len(dropped))
    # J
    stamps = [rd['stamp'] for rd in reads if rd['stamp'] in pages]; J = dict(reads_with_page=len(stamps), statements={})
    if stamps:
        f0, cur = pages[stamps[0]], pages[stamps[-1]]
        for n, _ in STMT_RX:
            ch = f0.get(n) != cur.get(n)
            J['statements'][n] = dict(status='CHANGED' if ch else 'KEPT', now=cur.get(n) or 'not found', **(dict(first=f0.get(n) or 'not found', first_read=stamps[0], now_read=stamps[-1]) if ch else {}))
        J['changed'] = sum(1 for v in J['statements'].values() if v['status'] == 'CHANGED')
    else: J['changed'] = None
    return dict(F=F, G=G, H=H_, I=I, J=J)

# ---- real data
def load_real():
    reads = [json.loads(l) for l in open('data/reads.jsonl')]; cache = {}; labels = {}; pages = {}; pcache = {}
    for rd in reads:
        d = 'data/raw/' + rd['stamp']
        for n, hsh in rd['hashes'].items():
            if n == 'page.html':
                if hsh not in pcache:
                    p = d + '/page.html'; pcache[hsh] = page_statements(open(p, encoding='utf8', errors='replace').read()) if os.path.exists(p) else None
                if pcache[hsh] is not None: pages[rd['stamp']] = pcache[hsh]
                continue
            if hsh not in cache:
                p = d + '/%s.pdf' % re.sub(r'[^A-Za-z0-9]+', '_', n); lab = None
                if os.path.exists(p):
                    try:
                        import pypdf
                        lab = parse_label('\n'.join((pg.extract_text() or '') for pg in pypdf.PdfReader(p).pages))
                    except Exception: lab = None
                cache[hsh] = lab
            labels[(rd['stamp'], n)] = cache[hsh]
    return reads, labels, pages

# ---- known-good
def planted():
    L1 = 'Safety 1.2.1 | Problem Set 2.0 | evaluator v1.4'; L2 = 'Safety 1.3 | Problem Set 2.1 | evaluator v1.5'
    def sysv(base, cats=None): return dict(release='May 2026', overall=base, cats=dict(zip(CATS, cats or [base] * 12)))
    s1a = sysv(50, [50] * 12); s1b = sysv(60, [60] * 4 + [40] * 3 + [50] * 5)   # overall up, 4 up and 3 down and 5 same among the 12: totals 5 up (overall plus 4), 3 down, 5 same
    s1b['overall'] = 60
    reads = [dict(stamp='r1', t=1, systems={'S1': s1a, 'S2': sysv(70), 'S3': sysv(80), 'S4': sysv(90)}),
             dict(stamp='r2', t=2, systems={'S1': s1b, 'S2': sysv(70), 'S3': sysv(80)}),
             dict(stamp='r3', t=3, systems={'S1': s1b, 'S2': sysv(70), 'S3': sysv(81)})]
    labels = {('r1', 'S1'): L1, ('r1', 'S2'): L1, ('r1', 'S3'): L1, ('r1', 'S4'): L1, ('r2', 'S1'): L2, ('r2', 'S2'): L2, ('r2', 'S3'): L1, ('r3', 'S1'): L2, ('r3', 'S2'): L2, ('r3', 'S3'): L1}
    return reads, labels, L1, L2, sysv
def gate():
    ok = True
    def chk(name, c):
        nonlocal ok; ok &= bool(c)
        if not c: print('drift: gate FAIL', name)
    good = 'x\nTechnical labels: AILuminate Safety 1.2.1 · Problem Set 2.0, official prompts · evaluator v1.4 · English (US)\ny'
    chk('label parse', parse_label(good) == 'Safety 1.2.1 | Problem Set 2.0 | evaluator v1.4'); chk('label none', parse_label('no labels here') is None)
    chk('label other version', parse_label(good.replace('1.2.1', '1.3').replace('v1.4', 'v1.5')) == 'Safety 1.3 | Problem Set 2.0 | evaluator v1.5')
    pg = page_statements('<p>Technical labels: AILuminate Safety 1.2.1, Problem Set 2.0 official prompts, evaluator v1.4, English (US).</p> <p>Only results labeled AILuminate Safety 1.2.1, English (US), compare directly with these scores; grades from Safety 1.0 are not comparable.</p>')
    chk('statements', pg['Technical labels'].endswith('English (US).') and pg['Only results labeled'].endswith('not comparable.') and pg['Reference set'] is None)
    reads, labels, L1, L2, sysv = planted(); r = analyse(reads, labels, {})
    chk('F planted', r['F']['of'] == 3 and r['F']['n'] == 2 and r['F']['changed'] == ['S1', 'S2'])
    chk('G planted', r['G']['systems'] == 2 and r['G']['up'] == 5 and r['G']['down'] == 3 and r['G']['same'] == 18 and r['G']['moved'] == 8 and r['G']['outcome'] == K.CANNOT_TELL and r['G']['per_system']['S1']['up'] == 5 and r['G']['per_system']['S2']['same'] == 13)
    chk('H planted', r['H']['of'] == 3 and r['H']['n'] == 1 and r['H']['changed'][0]['system'] == 'S3' and r['H']['changed'][0]['differs'] == ['overall'] + CATS)
    chk('I planted still published', r['I']['earlier_tuples'][0]['status'] == 'STILL_PUBLISHED' and r['I']['outcome'] == K.CANNOT_TELL and r['I']['dropped_systems'] == ['S4'])
    reads2 = [dict(rd, systems={n: v for n, v in rd['systems'].items() if not (rd['stamp'] == 'r3' and n == 'S3')}) for rd in reads]; r2 = analyse(reads2, labels, {})
    chk('I planted withdrawn', r2['I']['outcome'] == K.ABOVE and r2['I']['earlier_tuples'][0]['status'] == 'WITHDRAWN' and r2['I']['earlier_tuples'][0]['label'] == L1 and r2['I']['dropped_systems'] == ['S3', 'S4'])
    nul = [dict(stamp='a%d' % i, t=i, systems={'N%d' % j: sysv(50 + j % 40) for j in range(27)}) for i in range(2)]; lab = {(rd['stamp'], n): L1 for rd in nul for n in rd['systems']}; rn = analyse(nul, lab, {})
    chk('null F H', rn['F']['outcome'] == K.CONSISTENT and rn['H']['outcome'] == K.CONSISTENT and rn['G']['outcome'] == NR and rn['I']['outcome'] == NR)
    for mode, want in (('up', K.ABOVE), ('down', K.BELOW), ('half', K.CONSISTENT)):
        def mk(i, base): return dict(release='x', overall=base, cats={c: base for c in CATS})
        def moved(i, k):
            if mode == 'up': d = 5
            elif mode == 'down': d = -5
            else: d = 5 if (i + k) % 2 == 0 else -5
            return d
        a = {'P%d' % i: dict(release='x', overall=50 + moved(i, 0) * 0, cats={c: 50 for c in CATS}) for i in range(40)}
        b = {'P%d' % i: dict(release='x', overall=50 + moved(i, 0), cats={c: 50 + moved(i, k + 1) for k, c in enumerate(CATS)}) for i in range(40)}
        pr = [dict(stamp='p1', t=1, systems=a), dict(stamp='p2', t=2, systems=b)]; lb = {('p1', n): L1 for n in a}; lb.update({('p2', n): L2 for n in b})
        chk('G %s' % mode, analyse(pr, lb, {})['G']['outcome'] == want)
    pa = {'p1': {n: None for n, _ in STMT_RX}}; pa['p1']['Reference set'] = 'S'; pb = {'p1': pa['p1'], 'p2': dict(pa['p1'], **{'Reference set': 'T'})}
    rj = analyse([dict(stamp='p1', t=1, systems={}), dict(stamp='p2', t=2, systems={})], {}, pb)
    chk('J', rj['J']['statements']['Reference set']['status'] == 'CHANGED' and rj['J']['statements']['Technical labels']['status'] == 'KEPT' and rj['J']['changed'] == 1)
    print('drift: gate', 'passed' if ok else 'FAILED', flush=True); return ok

if __name__ == '__main__':
    if not (K.plan_committed(os.path.join(H, 'PLAN_ADDENDUM_drift.md')) or '--draft' in sys.argv): print('drift: addendum not committed (use --draft for a draft run)'); sys.exit(0)
    if not gate(): sys.exit(1)
    reads, labels, pages = load_real(); r = analyse(reads, labels, pages); now = time.time()
    out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), draft=not K.plan_committed(os.path.join(H, 'PLAN_ADDENDUM_drift.md')), gate='passed', reads=len(reads), first_read=reads[0]['stamp'], last_read=reads[-1]['stamp'], tests=r)
    json.dump(out, open('summary_drift.json', 'w'), indent=1)
    t = r
    print('drift: reads', len(reads), '| F', {k: t['F'][k] for k in ('of', 'n', 'outcome', 'label_tuple_count')}, '| G', t['G']['outcome'], '| H', {k: t['H'][k] for k in ('of', 'n', 'outcome')}, '| I', t['I']['outcome'], 'dropped', t['I']['dropped_n'], '| J changed', t['J']['changed'])
    for lab, e in t['F']['label_tuples'].items(): print('drift: label', lab, e)
    print('drift: wrote summary_drift.json (nothing published)')
