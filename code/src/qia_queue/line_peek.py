"""line_peek.py: put a one-shot job at the back of a long line, read everything IBM's server returns about it while it waits, then cancel it
while still queued (not charged). Prints the raw server fields so we can see whether any of them carry a position or an expected start."""
import sys, json, time
sys.path.insert(0, '.'); import queue_probe as Q
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2
s = Q.service(); be = s.backend(sys.argv[1] if len(sys.argv) > 1 else 'ibm_phoenix')
qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0); isa = transpile(qc, be, optimization_level=1)
sm = SamplerV2(mode=be); sm.options.environment.job_tags = ['qia-line-peek']
j = sm.run([isa], shots=1); print('queued', be.name, j.job_id(), flush=True)
time.sleep(20)
print('status', j.status())
raw = None
for name in ('job_get', 'job_metadata'):
    f = getattr(s._api_client, name, None)
    if f:
        try: raw = f(j.job_id()); print('--- raw', name); print(json.dumps(raw, indent=1, default=str)[:3000]); break
        except Exception as e: print(name, 'failed', type(e).__name__, str(e)[:150])
try: print('--- metrics'); print(json.dumps(j.metrics(), indent=1, default=str)[:1500])
except Exception as e: print('metrics failed', e)
try: print('usage_estimation', j.usage_estimation)
except Exception as e: print('usage_estimation failed', e)
st = str(j.status())
if st in ('QUEUED', 'INITIALIZING', 'VALIDATING'):
    j.cancel(); time.sleep(5); print('cancelled while', st, '->', j.status())
else: print('NOT cancelled, status', st)
m = j.metrics(); print('final usage', m.get('usage'), 'timestamps', m.get('timestamps'))
