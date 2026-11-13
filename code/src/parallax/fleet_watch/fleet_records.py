"""fleet_records.py -- the fleet watch (6 Oct 2026, Wayfinder and Bones): every reachable IBM chip's PUBLISHED calibration record, day by day, read from
IBM's own properties history. No job, no chip time; every request logged as one of our looks. Per chip-day: the record's stamp, median T1, median T2,
T2:T1, median readout length, number of qubits reported. Written raw to fleet_records.jsonl; the reader (fleet_read.py) flags frozen records (a NEW stamp
carrying IDENTICAL medians) and throws the Bonefish at each chip's clock ratio. Run with the IBM venv:  qvenv/bin/python fleet_records.py [days]"""
import json, os, sys, statistics as S, datetime as D
sys.path.insert(0, os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run'))
import live
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fleet_records.jsonl')
days = int(sys.argv[1]) if len(sys.argv) > 1 else 21
svc, _ = live.open_service(f'FLEET WATCH: published calibration records (properties history, {days} days) of every reachable IBM chip; no job, no chip config')
now = D.datetime.now(D.timezone.utc)
seen = set()
if os.path.exists(OUT):
    for l in open(OUT):
        r = json.loads(l); seen.add((r['chip'], r['day']))
def g(f, q):
    try: return f(q) * 1e6
    except Exception: return None
n = 0
for be in svc.backends(simulator=False):
    for k in range(days, -1, -1):
        day = (now - D.timedelta(days=k)).date().isoformat()
        if (be.name, day) in seen: continue
        try:
            p = be.properties(datetime=D.datetime.fromisoformat(day + 'T12:00:00'))
            if p is None: continue
            t1 = [x for x in (g(p.t1, q) for q in range(be.num_qubits)) if x]; t2 = [x for x in (g(p.t2, q) for q in range(be.num_qubits)) if x]
            rl = [x for x in (g(p.readout_length, q) for q in range(be.num_qubits)) if x]
            r = dict(chip=be.name, day=day, stamp=str(p.last_update_date), n=len(t1), t1=round(S.median(t1), 3) if t1 else None, t2=round(S.median(t2), 3) if t2 else None,
                     ratio=round(S.median(t2) / S.median(t1), 4) if t1 and t2 else None, readout=round(S.median(rl), 4) if rl else None, read_at=D.datetime.now().isoformat(timespec='seconds'))
            open(OUT, 'a').write(json.dumps(r) + '\n'); n += 1
        except Exception as e:
            open(OUT, 'a').write(json.dumps(dict(chip=be.name, day=day, error=str(e)[:120])) + '\n')
    print(be.name, 'done', flush=True)
print('records written', n)
