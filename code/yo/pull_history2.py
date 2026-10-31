"""pull_history2.py (31 Oct 2026, YO v2): IBM properties history, every backend the service lists, 2-hour steps, the 180 days ending
31 Oct 21:00 UTC; distinct stamps saved gzipped to history/<backend>__<stamp>.json.gz. Read only, zero QPU seconds. Resumable. Optional args: backend names (one process per backend runs them side by side).
Service from sweep_run/sweep.py (the same login the 31 Oct keystone run used)."""
import sys, os, json, gzip, datetime as dt
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
OUT = '/Users/heuremen/bones-forge/yo/history'
s = service(); now = dt.datetime(2026, 10, 31, 21, 0, tzinfo=dt.timezone.utc)
have = set(os.listdir(OUT))
names = sorted(b.name for b in s.backends()); names = [n for n in names if len(sys.argv) < 2 or n in sys.argv[1:]]; print('backends', names, flush=True)
for name in names:
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
