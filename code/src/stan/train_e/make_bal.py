"""make_bal.py (13 Nov 2026): lora_v1 and lora_v2 learned to answer {"errors": []} to everything (0/23 and 0/27 recall; 390 of 541 train
targets are the empty answer). data_bal/ keeps valid.jsonl as is and rebalances train: every positive twice, negatives sampled down to 250
(seed 20261113). Test sets are untouched, so v3 is scored on the same rows as base, v1 and v2."""
import json, random, shutil
from pathlib import Path
D = Path(__file__).parent / 'data'; B = Path(__file__).parent / 'data_bal'; B.mkdir(exist_ok=True)
L = [json.loads(l) for l in open(D / 'train.jsonl')]
pos = [x for x in L if x['messages'][-1]['content'] != '{"errors": []}']; neg = [x for x in L if x not in pos]
random.seed(20261113); rows = pos * 2 + random.sample(neg, min(250, len(neg))); random.shuffle(rows)
with open(B / 'train.jsonl', 'w') as o:
    for x in rows: o.write(json.dumps(x) + '\n')
shutil.copy(D / 'valid.jsonl', B / 'valid.jsonl')
json.dump({'pos': len(pos), 'neg_all': len(neg), 'train_rows': len(rows), 'pos_share': round(2 * len(pos) / len(rows), 3)}, open(B / 'manifest.json', 'w'))
print(open(B / 'manifest.json').read())
