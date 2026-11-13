#!/usr/bin/env python3
"""early_tick.py: one pass of the LINKROT broader samples (PLAN.md Addendum 3 and 4). Rerunnable, no timers: run it by hand or hang it
on the tick bus. Each run: refuses unless PLAN.md is committed, runs the gate (early/gate.py), then reads what is due in key order:
units never read, units whose last read was NOTHING_RETURNED (our failure, retried), and repeat-floor units (key starting 0, 1 or 2)
whose first read is at least three hours old and which have no second read. Then writes the summary and the section fragments.
Usage: python3 -I early_tick.py [--samples ncsa,dmoz,rfc,fedreg,landmarks,suggested] [--max N] [--workers 12] [--no-repeat]"""
import os, sys, json, time, fcntl, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); sys.path.insert(0, H); sys.path.insert(0, ROOT)
import linkstate as L, gate as G, heuremen_kit as K
D = os.path.join(ROOT, 'data')
SAMPLES = {   # sample name -> (sample file, archive options)
    'ncsa': (os.path.join(D, 'early', 'ncsa', 'sample_ncsa.json'), dict(first='live', history='live')),
    'dmoz': (os.path.join(D, 'early', 'dmoz', 'sample_dmoz.json'), dict(first='all', history='live')),
    'rfc': (os.path.join(D, 'early', 'rfc', 'sample_rfc.json'), dict(first='live', history='live')),
    'fedreg': (os.path.join(D, 'gov', 'sample_fedreg.json'), dict(first='live', history='live')),
    'landmarks': (os.path.join(D, 'landmarks', 'sample_landmarks.json'), dict(first='all', history='all')),
    'suggested': (os.path.join(D, 'landmarks', 'sample_suggested.json'), dict(first='all', history='all')),
}
STORE = os.path.join(D, 'early', 'reads.json'); REPEAT_AFTER = 3 * 3600; RETRY_AFTER = 1800

def in_repeat(key): return key[0] in '012'

def first_valid(s): return next((r for r in s['reads'] if r['state'] != 'NOTHING_RETURNED'), None)

def needs_archive(r, opt):
    """A read whose state is decided but whose archive fields the sample needs and did not get (the archive failed or was paused)."""
    if r['state'] == 'NOTHING_RETURNED' or not r.get('archive_err') and ('first_capture' in r or opt['first'] != 'all'): return False
    if opt['first'] == 'all' and 'first_capture' not in r: return True
    if opt['history'] == 'all' and r.get('archive_err'): return True
    return False

def load_units(names):
    units = []
    for n in names:
        p, opt = SAMPLES[n]
        if not os.path.exists(p): print('early: no sample file yet for', n); continue
        for u in json.load(open(p))['units']: u = dict(u); u['sample'] = n; units.append(u)
    return units

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--samples', default='ncsa,dmoz,rfc,fedreg,landmarks,suggested'); ap.add_argument('--max', type=int, default=100000)
    ap.add_argument('--workers', type=int, default=12); ap.add_argument('--no-repeat', action='store_true'); a = ap.parse_args()
    lock = open(os.path.join(D, 'early', '.lock'), 'w')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('early: another run holds the lock, skipping'); return
    if not K.plan_committed(os.path.join(ROOT, 'PLAN.md')): print('early: PLAN.md not committed, refusing to read'); return
    names = [n for n in a.samples.split(',') if n in SAMPLES]
    store = json.load(open(STORE)) if os.path.exists(STORE) else {'units': {}, 'passes': []}
    ok, rows = G.run()
    gate_rec = dict(t=round(time.time()), passed=ok, failed=[[n, w, g] for n, w, g in rows if w != g])
    store['passes'].append(gate_rec)
    if not ok:
        print('early: gate FAILED, nothing read', gate_rec['failed']); json.dump(store, open(STORE + '.tmp', 'w')); os.replace(STORE + '.tmp', STORE); return
    units = load_units(names); now = time.time(); due = []
    for u in units:
        s = store['units'].setdefault(u['id'], dict(url=u['url'], sample=u['sample'], key=u['key'], reads=[], repeat=None))
        s.update({k: v for k, v in u.items() if k not in ('id',)})
        last = s['reads'][-1] if s['reads'] else None; fv = first_valid(s)
        if last is None: due.append((0, u['key'], u['id'], 'first'))
        elif last['state'] == 'NOTHING_RETURNED' and now - last['t'] > RETRY_AFTER: due.append((1, u['key'], u['id'], 'retry'))
        elif needs_archive(last, SAMPLES[u['sample']][1]): due.append((1, u['key'], u['id'], 'archive'))
        elif not a.no_repeat and in_repeat(u['key']) and s.get('repeat') is None and fv and now - fv['t'] >= REPEAT_AFTER:
            due.append((2, u['key'], u['id'], 'repeat'))
    due.sort(); due = due[:a.max]
    # one read per address per pass, shared by the units that carry it
    by_url = {}
    for pri, k, uid, kind in due: by_url.setdefault((store['units'][uid]['url'], kind if kind in ('repeat', 'archive') else 'read'), []).append((uid, kind))
    print('early: gate passed, %d units due (%d addresses)' % (len(due), len(by_url)), flush=True)
    lk = threading.Lock(); n_done = [0]
    def work(item):
        (url, mode), members = item; s0 = store['units'][members[0][0]]; opt = dict(SAMPLES[s0['sample']][1])
        for uid, _ in members:   # the widest archive options among the units sharing this address
            o2 = SAMPLES[store['units'][uid]['sample']][1]
            if o2['first'] == 'all': opt['first'] = 'all'
            if o2['history'] == 'all': opt['history'] = 'all'
        if mode == 'repeat':
            fv = first_valid(s0); b = fv.get('baseline')
            if b is None and fv.get('state') == 'LIVE_NO_BASELINE': b = {'ts': None}
            r = L.check(url, first='live', history='none', baseline=b)
        elif mode == 'archive':
            r = dict(s0['reads'][-1]); r.pop('archive_err', None)
            if L.archive_down(): r['archive_err'] = 'archive paused'
            else: L._archive_fields(r, url, opt['history'] == 'all', None)
            r['archive_filled'] = round(time.time())
        else:
            r = L.check(url, **opt)
        return item, r
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(work, it) for it in by_url.items()]
        for f in as_completed(futs):
            ((url, mode), members), r = f.result()
            with lk:
                for uid, kind in members:
                    s = store['units'][uid]
                    if kind == 'repeat': s['repeat'] = r
                    elif kind == 'archive': s['reads'][-1] = r
                    else: s['reads'].append(r)
                n_done[0] += 1
                if n_done[0] % 25 == 0:
                    json.dump(store, open(STORE + '.tmp', 'w')); os.replace(STORE + '.tmp', STORE)
                    print('early: %d of %d addresses read' % (n_done[0], len(by_url)), flush=True)
    json.dump(store, open(STORE + '.tmp', 'w')); os.replace(STORE + '.tmp', STORE)
    print('early: pass done, %d addresses read' % n_done[0], flush=True)
    import early_summary; early_summary.main()

if __name__ == '__main__':
    main()
