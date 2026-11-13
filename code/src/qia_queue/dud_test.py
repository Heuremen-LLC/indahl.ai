"""dud_test.py: does a job that fails at the front of the queue get a running stamp and cost 0 s? Two candidates on one processor."""
import sys, json, time, datetime as dt
sys.path.insert(0, '.'); import queue_probe as Q
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2
s = Q.service(); be = s.backend(sys.argv[1] if len(sys.argv) > 1 else 'ibm_fez'); dtv = be.dt
jobs = []
for secs in (10, 1000):
    qc = QuantumCircuit(1, 1); qc.delay(int(secs / dtv), 0, unit='dt'); qc.measure(0, 0)
    isa = transpile(qc, be, optimization_level=0)
    try:
        sm = SamplerV2(mode=be); sm.options.environment.job_tags = ['qia-queue-dud-test']
        j = sm.run([isa], shots=1); jobs.append((secs, j)); print('submitted delay', secs, 's', j.job_id(), flush=True)
    except Exception as e:
        print('refused at submission, delay', secs, 's:', type(e).__name__, str(e)[:200], flush=True)
for secs, j in jobs:
    t0 = time.time()
    while str(j.status()) not in ('DONE', 'ERROR', 'CANCELLED') and time.time() - t0 < 900: time.sleep(5)
    m = j.metrics(); ts = m.get('timestamps') or {}; err = ''
    try: j.result()
    except Exception as e: err = str(e)[:240]
    print(json.dumps(dict(delay_s=secs, id=j.job_id(), status=str(j.status()), timestamps=ts, usage=m.get('usage'), error=err), default=str))
print('remaining', s.usage().get('usage_remaining_seconds'))
