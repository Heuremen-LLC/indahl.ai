# synth_fake_raw.py -- writes PLANTED raw/job/props files for an analyze.py dry run (run from a scratch copy, never in the run folder)
import sys, json, numpy as np
sys.path.insert(0, 'src')
from fire import build
from assqd import sample
from circuits import ideal_probs
from synth import ro
circs, meta = build(); rng = np.random.default_rng(5); raw = []
for qc, m in zip(circs, meta):
    pr = ro(ideal_probs(qc), 0.01, 0.02); c = sample(rng, pr, m['shots'])
    raw.append(dict(m, counts={format(k, '012b'): v for k, v in c.items()}))
json.dump(raw, open('raw_2603.13536.json', 'w'))
ring = list(range(12))
json.dump(dict(ring=ring, attempts=[dict(attempt=1, job_id='FAKE', usage=dict(qpu_charge_time_seconds=0), timestamps=dict(created='x'))]), open('job_2603.13536.json', 'w'))
json.dump(dict(last_update_date='fake', qubits=[[dict(name='readout_error', value=0.015), dict(name='prob_meas1_prep0', value=0.01), dict(name='prob_meas0_prep1', value=0.02)] for q in range(156)]), open('props_2603.13536_before_1.json', 'w'))
