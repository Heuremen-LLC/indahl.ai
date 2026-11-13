#!/usr/bin/env python3
"""freeze.py (10 Nov: the raw log and the stamped log copies are not placed in the site's public folder, held for Bones's call on the public-repo guard; the .ots proofs and the stamp index are):
 writes data/page_reading.json, the reading the page is built from (summary, entries with their rows, stamps, Wayback captures),
and data/shipped_<date>_reading.json, the copy ledger rows cite. Also copies the log and its stamp index for the site's public files.
The page changes only when this is run again at a ship, so a daily rider run never moves a number a ledger row holds."""
import os, sys, json, time, hashlib, shutil
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import now_log as NL
PUBDIR = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/public/predictions')

S = json.load(open(os.path.join(H, 'summary_now.json')))
caps = {}
wb = os.path.join(H, 'data', 'wayback.jsonl')
if os.path.exists(wb):
    for l in open(wb):
        try:
            r = json.loads(l)
            if r.get('capture'): caps[r['url']] = r['capture']
        except ValueError: pass
ents = NL.current()
for e in ents:
    if not e.get('archive_url') and caps.get(e.get('source_url')): e['archive_url'] = caps[e['source_url']]; e['archive_from'] = 'data/wayback.jsonl'
mr = json.load(open(os.path.join(H, 'data', 'research', 'manifold_resolved.json')))['counts']
WHY = {'fewer than 50 unique bettors': 'fewer than 50 traders', 'reference time outside the window': 'closed outside the window', 'created less than 30 days before the reference time': 'open for less than 30 days',
       'no bet before the stated moment': 'no trade 30 days before close', 'resolved CANCEL': 'cancelled', 'resolved MKT': 'resolved to a probability, not yes or no'}
line = ', '.join('%s %s' % (format(v, ','), WHY.get(k, k)) for k, v in mr.items() if k not in ('found', 'read')) + ', of %s binary AI markets found.' % format(mr['found'], ',')
ls = NL.lines(); last = hashlib.sha256(ls[-1]).hexdigest() if ls else ''
idx = os.path.join(NL.ST, 'index.json'); stamps = json.load(open(idx)) if os.path.exists(idx) else []
R = dict(frozen_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), summary=S, entries=ents, log_rows=len(ls), log_sha256=NL.head_sha(), log_last_line_sha256=last,
         stamps=stamps, manifold_counts_line=line)
json.dump(R, open(os.path.join(H, 'data', 'page_reading.json'), 'w'), indent=1, ensure_ascii=False)
day = time.strftime('%Y%m%d')
shutil.copy2(os.path.join(H, 'data', 'page_reading.json'), os.path.join(H, 'data', 'shipped_%s_reading.json' % day))
os.makedirs(PUBDIR, exist_ok=True)
json.dump(stamps, open(os.path.join(PUBDIR, 'stamps.json'), 'w'), indent=1)
for s in stamps:
    p = os.path.join(NL.ST, s['file'] + '.ots')
    if os.path.exists(p):
        os.makedirs(os.path.join(PUBDIR, 'stamps'), exist_ok=True); shutil.copy2(p, os.path.join(PUBDIR, 'stamps', s['file'] + '.ots'))
f = os.path.join(H, 'data', 'fortune.json')
if os.path.exists(f): shutil.copy2(f, os.path.join(PUBDIR, 'fortune.json'))
print('frozen', R['frozen_at'], 'rows', len(ls), 'entries', len(ents), 'captures joined', sum(1 for e in ents if e.get('archive_from')))
