#!/usr/bin/env python3
"""parkcheck.py: the parking detector's hand-check (PLAN.md Addendum 3). Draws, in the order of a second key SHA-256(seed | handcheck | unit id) across every sample read so far (PLAN.md note 5),
the first 50 units whose state is PARKED_OR_FOR_SALE (detections) and the first 50 whose state is one where a parked page could hide
(LIVE_SAME, LIVE_CHANGED, LIVE_NO_BASELINE, REDIRECTED_ELSEWHERE: non-detections). Each page is read again for evidence (robots.txt
obeyed, same reader), and the evidence goes to data/early/handcheck_evidence.json, which is private and never published.
Judgments are entered by a reader into data/early/handcheck_parked.json ({"judgments": {unit id: "parked" | "not parked"}}), and
`python3 -I parkcheck.py score` writes the result and the sentence the page shows.
Usage: python3 -I parkcheck.py draw | show [detections|nondetections] | score"""
import os, sys, json, re
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); sys.path.insert(0, H)
import linkstate as L, frames_common as F
D = os.path.join(ROOT, 'data', 'early'); STORE = os.path.join(D, 'reads.json'); EV = os.path.join(D, 'handcheck_evidence.json'); J = os.path.join(D, 'handcheck_parked.json')
HIDE = ('LIVE_SAME', 'LIVE_CHANGED', 'LIVE_NO_BASELINE', 'REDIRECTED_ELSEWHERE'); N = 50

def draw():
    s = json.load(open(STORE))['units']
    last = {uid: u['reads'][-1] for uid, u in s.items() if u['reads']}
    sd = F.seed(); hk = lambda u: F.key(sd, 'handcheck', u)   # PLAN.md note 5: a second key, so the draw spreads across samples
    det = sorted((hk(u), u) for u, r in last.items() if r['state'] == 'PARKED_OR_FOR_SALE')[:N]
    non = sorted((hk(u), u) for u, r in last.items() if r['state'] in HIDE)[:N]
    def ev(item):
        k, uid = item; u = s[uid]; r = last[uid]
        target = r.get('final') or u['url']
        f = L.fetch(target) if r['state'] != 'PARKED_OR_FOR_SALE' or (r.get('status') and 200 <= r['status'] < 300) else L.fetch(u['url'])
        text, title = '', ''
        if f['kind'] == 'http' and f['body']:
            text, dec = L.to_text(f['body'], (f['headers'] or {}).get('content-type', '')); title = L.title_of(dec)
        return uid, dict(url=u['url'], sample=u['sample'], state=r['state'], signals=r.get('park_signals'), ns=r.get('ns'), status_then=r.get('status'),
                         final_then=r.get('final'), refetch_status=f['status'], refetch_final=f['final'], title=title, text=text[:1500])
    out = {'detections': [], 'nondetections': []}
    with ThreadPoolExecutor(8) as ex:
        out['detections'] = [dict(id=i, **e) for i, e in ex.map(ev, det)]
        out['nondetections'] = [dict(id=i, **e) for i, e in ex.map(ev, non)]
    json.dump(out, open(EV, 'w'), indent=1)
    print('drawn', len(out['detections']), 'detections and', len(out['nondetections']), 'non-detections')

def show(which):
    ev = json.load(open(EV))[which]
    for n, e in enumerate(ev, 1):
        host = re.sub(r'^https?://', '', (e.get('refetch_final') or '')).split('/')[0]
        print('%d. %s | %s | signals %s | ns %s | now %s on %s | title: %s | text: %s' % (n, e['id'], e['state'], ','.join(e['signals'] or [])[:120], ','.join((e['ns'] or [])[:2]), e['refetch_status'], host, e['title'][:90], re.sub(r'\s+', ' ', e['text'])[:420]))

def score():
    ev = json.load(open(EV)); j = json.load(open(J)); jd = j['judgments']
    det = [e['id'] for e in ev['detections']]; non = [e['id'] for e in ev['nondetections']]
    missing = [i for i in det + non if i not in jd]
    if missing: sys.exit('%d items have no judgment yet' % len(missing))
    wrong = sum(1 for i in det if jd[i] != 'parked'); missed = sum(1 for i in non if jd[i] == 'parked')
    trusted = wrong <= 5 and missed <= 5
    sent = ('We read %d detections and %d non-detections in full, drawn across the samples in the order of a second random key (PLAN.md, note 5). %d of the %d detections were not parked or for sale, and %d of the %d non-detections %s the detector missed. %s'
            % (len(det), len(non), wrong, len(det), missed, len(non), 'was a parked page' if missed == 1 else 'were parked pages', 'Under the rule fixed before the first read, the parked column passes the full reading.' if trusted else 'Under the rule fixed before the first read, the parked column fails the full reading, and its shares carry that result beside them.'))
    j['result'] = dict(detections=len(det), detections_wrong=wrong, nondetections=len(non), nondetections_parked=missed, trusted=trusted, sentence=sent)
    json.dump(j, open(J, 'w'), indent=1); print(sent)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'draw': draw()
    elif a[0] == 'show': show(a[1] if len(a) > 1 else 'detections')
    elif a[0] == 'score': score()
