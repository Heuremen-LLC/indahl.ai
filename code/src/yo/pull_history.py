"""pull_history.py -- IBM properties history per PLAN_YO_PAPER: every open-instance backend, 2-hour steps, last 180 days, distinct stamps
saved gzipped to history/<backend>__<stamp>.json.gz. Read only, zero QPU seconds. Resumable (skips stamps already saved)."""
import sys, os, json, gzip, datetime as dt
H = '/Users/heuremen/bones-forge/arxiv_one_readout/hahn_t2'; OUT = '/Users/heuremen/bones-forge/yo/history'
src = open(f'{H}/hahn.py').read(); old = "KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'open-instance'"; assert src.count(old) == 1
g = {'__name__': 'h', '__file__': f'{H}/hahn.py'}; sys.argv = ['x']
exec(compile(src.replace(old, "KEYFILE, INSTANCE = '.ibm_quantum_key_2', 'open-instance'"), 'hahn.py', 'exec'), g)
s = g['service'](); now = dt.datetime(2026, 10, 23, 13, 0, tzinfo=dt.timezone.utc)
have = set(os.listdir(OUT))
for name in sorted(b.name for b in s.backends()):
    b = s.backend(name); new = 0
    for k in range(0, 180 * 12):
        t = now - dt.timedelta(hours=2 * k)
        try: p = b.properties(datetime=t)
        except Exception as e: print(name, t, 'ERR', str(e)[:60], flush=True); continue
        if p is None: continue
        f = f"{name}__{p.last_update_date.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')}.json.gz"
        if f in have: continue
        with gzip.open(f'{OUT}/{f}', 'wt') as fh: json.dump(p.to_dict(), fh, default=str)
        have.add(f); new += 1
        if new % 25 == 0: print(name, 'distinct', new, 'back to', p.last_update_date, flush=True)
    print(name, 'DONE distinct', new, flush=True)
