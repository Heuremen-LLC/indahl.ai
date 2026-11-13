"""decided_summary.py (12 Nov, Sage break 1): how often each model commits to a call (PRESENT, ABSENT or NOT_APPLICABLE) instead of CANNOT_TELL,
pooled over F1 to F7, n-weighted. Agreement in baseline_dev.json and paired_test.json counts CANNOT_TELL as agreeing with an unflagged recount,
so it measures abstention as much as skill. This share does not fold. Writes results/decided_summary.json."""
import json, os
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out = {}
def pooled(pc):
    n = sum(x['n'] for x in pc.values()); return round(sum(x['n'] * x['decided_share'] for x in pc.values()) / n, 3), n
bd = json.load(open(S + '/results/baseline_dev.json'))
for m, v in bd.items(): d, n = pooled(v['per_code']); out['dev_' + m] = {'decided_share': d, 'calls': n}
if os.path.exists(S + '/results/paired_test.json'):
    pt = json.load(open(S + '/results/paired_test.json'))
    for m in ('base', 'stan'): d, n = pooled(pt[m]['per_code']); out['test_' + m] = {'decided_share': d, 'calls': n}
    pc = pt['base']['per_code']; out['test_gold_present_share'] = round(sum(x['gold_present'] for x in pc.values()) / sum(x['n'] for x in pc.values()), 3)
json.dump(out, open(S + '/results/decided_summary.json', 'w'), indent=1); print(out)
