"""fire_hebrew.py -- dry run by default (transpile, equal-duration check, estimate, seconds); --fire submits two jobs (copy 0 in build order,
copy 1 reversed = ABBA over the circuit list), saving the backend record BEFORE each job and the raw fin bits after. <our IBM instance>."""
import os, sys, json, time, hashlib
import numpy as np
sys.path.insert(0, os.path.expanduser('<local helper folder>')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import service
from qiskit import transpile, qpy
import hebrew as H
HERE = os.path.dirname(os.path.abspath(__file__)); CHIP = 'ibm_fez'; CAP = 200
s = service(); b = s.backend(CHIP); circs, meta = H.build()
tq = transpile(circs, b, optimization_level=0, initial_layout=list(range(b.num_qubits)), seed_transpiler=7)
dur = [c.estimate_duration(b.target, 's') for c in tq]
bad = []
for N in H.NS:
    for st in H.SETS:
        i = {a: next(k for k, m in enumerate(meta) if m['kind'] == 'main' and m['arm'] == a and m['N'] == N and m['setting'] == st) for a in H.ARMS}
        if abs(dur[i['M']] - dur[i['D']]) > 1e-12: bad.append(('M/D', N, st, dur[i['M']], dur[i['D']]))
        if abs(dur[i['MD']] - dur[i['DD']]) > 1e-12: bad.append(('MD/DD', N, st, dur[i['MD']], dur[i['DD']]))
ik = [k for k, m in enumerate(meta) if m['kind'] == 'kg']
if abs(dur[ik[0]] - dur[ik[2]]) > 1e-12: bad.append(('KG', dur[ik[0]], dur[ik[2]]))
est = 2 * sum(H.SHOTS * (d + 250e-6) for d in dur); rem = s.usage().get('usage_remaining_seconds')
print(f'{CHIP}: {len(tq)} circuits/job x 2 jobs, {H.SHOTS} shots, equal-duration check: {"PASS" if not bad else "FAIL " + str(bad[:3])}, '
      f'max duration {max(dur)*1e6:.1f} us, ESTIMATED {est:.0f} s (cap {CAP}), remaining {rem}', flush=True)
if '--fire' not in sys.argv: sys.exit(0)
if bad or est > CAP or (rem is not None and rem < est + 30): print('STOP: duration check, cap or seconds'); sys.exit(1)
from qiskit_ibm_runtime import SamplerV2
qpy.dump(tq, open(f'{HERE}/circuits_hebrew.qpy', 'wb')); chash = hashlib.sha256(open(f'{HERE}/circuits_hebrew.qpy', 'rb').read()).hexdigest()
rec = dict(chip=CHIP, shots=H.SHOTS, circuits_sha256=chash, durations_s=dur, meta=meta, jobs=[])
for copy, order in ((0, list(range(len(tq)))), (1, list(range(len(tq)))[::-1])):
    json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_hebrew_before_J{copy}.json', 'w'), default=str)
    for attempt in (1, 2):
        job = SamplerV2(mode=b).run([tq[i] for i in order], shots=H.SHOTS); sub = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f'SUBMITTED J{copy} {job.job_id()} {sub} attempt {attempt}', flush=True)
        try: res = job.result(); break
        except Exception as e:
            print(f'ERROR J{copy}: {str(e)[:160]}', flush=True); rec['jobs'].append(dict(copy=copy, job_id=job.job_id(), error=str(e)[:200]))
            if attempt == 2: print('HOLD: second IBM-side error'); json.dump(rec, open(f'{HERE}/job_hebrew.json', 'w'), default=str); sys.exit(1)
    out = {}
    for pos, (i, pr) in enumerate(zip(order, res)): out[f'fin_{i}'] = pr.data.fin.to_bool_array(order='little')
    np.savez_compressed(f'{HERE}/raw_hebrew_J{copy}.npz', **out)
    m = job.metrics(); rec['jobs'].append(dict(copy=copy, job_id=job.job_id(), submitted_utc=sub, usage=m.get('usage'), timestamps=m.get('timestamps')))
    json.dump(rec, open(f'{HERE}/job_hebrew.json', 'w'), default=str); print(f'DONE J{copy} usage {(m.get("usage") or {}).get("qpu_charge_time_seconds")} s', flush=True)
json.dump(b.properties(refresh=True).to_dict(), open(f'{HERE}/props_hebrew_after.json', 'w'), default=str); print('ALL DONE')
