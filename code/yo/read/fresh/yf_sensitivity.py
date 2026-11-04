"""yf_sensitivity.py -- SENSITIVITY set for PLAN_YO_FRESH Addendum 3 (Sage VERDICT 23:15Z): the 88 primary papers minus four labels known before any
model answer to be wrong or tainted: elte.2025.051 (DATES note says no date, parsed YES), zenodo.18049904 and zenodo.17883260 (LINK notes say no link or a
placeholder, parsed YES), ssrn.7358502 (same-author near-twin of a used paper). Writes data/test_items_sensitivity.jsonl, primary_ids.txt, sensitivity_ids.txt."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
DROP = ['doi:10.15476/elte.2025.051', 'doi:10.5281/zenodo.18049904', 'doi:10.5281/zenodo.17883260', 'doi:10.2139/ssrn.7358502']
P = [json.loads(l) for l in open(H + '/data/test_items_primary.jsonl')]; ids = sorted({i['paper'] for i in P})
assert all(d in ids for d in DROP), [d for d in DROP if d not in ids]
S = [i for i in P if i['paper'] not in DROP]; sids = sorted({i['paper'] for i in S})
with open(H + '/data/test_items_sensitivity.jsonl', 'w') as f:
    for i in S: f.write(json.dumps(i) + '\n')
open(H + '/primary_ids.txt', 'w').write('\n'.join(ids) + '\n'); open(H + '/sensitivity_ids.txt', 'w').write('\n'.join(sids) + '\n')
for q in ('DATES', 'LINK', 'REQUEST'):
    a = [i['answer'] for i in S if i['q'] == q]; print(q, 'YES', a.count('YES'), 'of', len(a))
print('primary', len(ids), 'sensitivity', len(sids))
