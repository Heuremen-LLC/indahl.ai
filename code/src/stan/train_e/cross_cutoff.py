#!/usr/bin/env python3
"""cross_cutoff.py (13 Nov 2026): choose each model's flag cutoff on one held-out set, score it on the other (both directions).
Rule fixed here before running: on the choosing set, the cutoff is the lowest score threshold whose false-flag rate is at or below the
untouched model's generated false-flag rate on that set (base generation: 1/30 hand, 0/39 pipeline), maximising caught chunks; ties
take the higher cutoff. Applied unchanged to the other set. Reads results/<model>_<set>_scores.json. The test sets were seen before
(defined after the data as a design); the cutoff itself never sees the set it is scored on."""
import json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
BASE_FF = {'test_hand': 1 / 30, 'test_pipeline': 0 / 39}
def load(m, s): return json.load(open(os.path.join(R, f'{m}_{s}_scores.json')))['items']
def rates(items, c):
    pos = [i for i in items if i['label'] == 1]; neg = [i for i in items if i['label'] == 0]
    return sum((i['score'] or 0) >= c for i in pos), len(pos), sum((i['score'] or 0) >= c for i in neg), len(neg)
def choose(items, cap):
    best = None
    for c in sorted({round(i['score'] or 0, 6) for i in items} | {1.01}):
        tp, P, fp, N = rates(items, c)
        if fp / N <= cap + 1e-12 and (best is None or tp > best[1] or (tp == best[1] and c > best[0])): best = (c, tp)
    return best[0]
out = {}
for m in ('base', 'lora_v4', 'lora_v6', 'lora_v7'):
    for a, b in (('test_hand', 'test_pipeline'), ('test_pipeline', 'test_hand')):
        c = choose(load(m, a), BASE_FF[a]); tp, P, fp, N = rates(load(m, b), c)
        out[f'{m} chosen on {a}, scored on {b}'] = {'cutoff': c, 'caught': tp, 'pos': P, 'false_flags': fp, 'neg': N}
        print(f'{m:8} chose {c:.4f} on {a:13} -> {b:13}: caught {tp}/{P}, false flags {fp}/{N}')
json.dump({'rule': __doc__, 'results': out}, open(os.path.join(R, 'cross_cutoff.json'), 'w'), indent=1)
