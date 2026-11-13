"""read_jobA.py -- fetch job A results (dbeo59fpc3tc739m2p1g) from the IBM record (zero QPU) and run the committed analysis on them; job B is still running.
Same ordering as fire_t10.py (interleaved by delay: free a, cpmg a, t10 a, t10 b)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from t10 import DELAYS_US
from t10_fill import analyse
from sweep import service
j = service().job('dbeo59fpc3tc739m2p1g'); res = j.result(); raw = {}; k = 0
for i, _ in enumerate(DELAYS_US):
    for arm, cp in (('free', 'a'), ('cpmg', 'a'), ('t10', 'a'), ('t10', 'b')):
        raw.setdefault(arm, {}).setdefault(cp, [None] * len(DELAYS_US))[i] = res[k].data.c.get_counts(); k += 1
json.dump(raw, open(os.path.join(HERE, 'raw_counts_jobA.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_t10_jobA.text'), 'w').write(json.dumps(out, indent=1, default=float))
print(json.dumps({k: out[k] for k in ('KNOWN_GOOD', 'LAYOUT', 'POOLED', 'RANK')}, default=float)); print({k: (round(v[0], 1), round(v[1], 1)) for k, v in out['T'].items()})
print([(round(x['diff'], 1), round(x['sd'], 1), x['outcome']) for x in out['THEIRS']['per_qubit']])
