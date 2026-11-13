#!/usr/bin/env python3
"""ship_samples.py: freeze the LINKROT samples beside arXiv (PLAN.md Addenda 3 and 4) for the public page, and write their ledger rows.
The tick (early_tick.py, ownname_tick.py) keeps reading and rewriting section_*.html. The public page never reads those files directly.
It reads shipped/linkrot_samples.html, which only this script writes, so a reading reaches the page only through a deliberate ship with
its ledger rows. Heuremen LLC, 10 Nov 2026.
  python3 -I ship_samples.py freeze STAMP     copy the current fragments and summaries into shipped/, write the combined fragment and the
                                               numbers file (one line per public row that carries a number)
  python3 -I ship_samples.py rows STAMP CHECKS write ledger rows (desk_linkrot surface) for every line of the numbers file, into
                                               ~/bones-forge/ledger/ledger.jsonl (a backup is kept), retiring earlier linkrot.samples rows"""
import os, sys, re, json, html, shutil, time
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); OUT = os.path.join(ROOT, 'shipped')
LEDGER = os.path.expanduser('~/bones-forge/ledger')

def norm(s):   # the same normalising the ledger check uses, so a row's text is found on the page
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S); s = re.sub(r'<[^>]+>', ' ', s); s = html.unescape(s)
    s = s.replace('\u2212', '-').replace('\u2013', '-').replace('\u2014', '-').replace('\u2009', ' ').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()

def freeze(stamp):
    os.makedirs(OUT, exist_ok=True)
    parts = []
    for name in ('section_early.html', 'section_landmarks.html', 'section_ownname.html'):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(OUT, '%s_%s' % (stamp, name))); parts.append(open(p, encoding='utf-8').read())
    for src, dst in (('summary_early.json', 'summary_early.json'), ('data/ownname.json', 'ownname.json'), ('data/landmarks.json', 'landmarks.json')):
        p = os.path.join(ROOT, src)
        if os.path.exists(p): shutil.copy2(p, os.path.join(OUT, '%s_%s' % (stamp, dst)))
    frag = '\n'.join(parts)
    hcp = os.path.join(ROOT, 'data', 'early', 'handcheck_parked.json')
    hc = json.load(open(hcp)).get('result') if os.path.exists(hcp) else None
    if hc and not hc.get('trusted'):   # the own-name table uses the same detector, so it carries the same hand-check result
        frag = frag.replace('<th>Parked or for sale</th>', '<th>Parked or for sale (the detector failed the full reading above)</th>')
    open(os.path.join(OUT, 'linkrot_samples.html'), 'w', encoding='utf-8').write(frag)
    lines = []; sec = None; n = 0; seen = set()
    for m in re.finditer(r'<section id="([^"]+)"|<h[23][^>]*>(.*?)</h[23]>|<tr>(.*?)</tr>|<p[^>]*>(.*?)</p>', frag, re.S):
        if m.group(1): sec = m.group(1).replace('linkrot-', ''); head = sec; continue
        if m.group(2) is not None: head = norm(m.group(2)); continue
        t = norm(m.group(3) or m.group(4) or '')
        if not re.search(r'\d', t) or t in seen: continue
        seen.add(t); n += 1
        lines.append('linkrot.samples.%s.%s.%03d\t%s\t%s' % (stamp, sec, n, head, t))
    open(os.path.join(OUT, 'numbers_%s.txt' % stamp), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('froze', len(parts), 'fragments,', len(lines), 'numbered rows ->', os.path.join(OUT, 'numbers_%s.txt' % stamp))

def rows(stamp, checks):
    sys.path.insert(0, LEDGER); import ledger as LG
    ck = LG.checks_ref(checks)
    src = 'linkrot_index/shipped/numbers_%s.txt' % stamp
    lines = [l.rstrip('\n').split('\t') for l in open(os.path.join(ROOT, 'shipped', 'numbers_%s.txt' % stamp), encoding='utf-8') if l.strip()]
    p = os.path.join(LEDGER, 'ledger.jsonl'); shutil.copy2(p, p + '.bak-%s-linkrotsamples' % stamp)
    allr = LG.load(); now = LG.now(); retired = 0
    for rid in list(allr):
        r = allr[rid]
        if rid.startswith('linkrot.samples.%s.' % stamp): del allr[rid]; continue
        if rid.startswith('linkrot.samples.') and r['status'] == 'live':
            r['status'] = 'withdrawn'; r.setdefault('history', []).append(dict(at=now, change='superseded by the %s ship' % stamp)); retired += 1
    for rid, head, text in lines:
        num = re.search(r'\d[\d,]*(?:\.\d+)?%?', text).group(0)
        allr[rid] = dict(checks=ck, id=rid, claim='LINKROT samples beside arXiv, %s: %s' % (head, text[:160]), value=num.replace(',', ''), lo=None, hi=None,
                         unit='as printed in the row', outcome='COUNT', source=dict(file=src, grep='%s\t%s\t%s' % (rid, head, text)),
                         surfaces=[dict(surface='desk_linkrot', text=text)], status='live', history=[dict(at=now, change='added', evidence=src)])
    LG.save(allr)
    print('ledger: %d rows written for %s, %d earlier sample rows superseded' % (len(lines), stamp, retired))

if __name__ == '__main__':
    if sys.argv[1] == 'freeze': freeze(sys.argv[2])
    elif sys.argv[1] == 'rows': rows(sys.argv[2], sys.argv[3])
