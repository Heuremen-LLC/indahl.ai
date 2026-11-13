import sys, json, os, glob, collections
sys.path.insert(0, os.path.expanduser('~/bones-forge/yo/read'))
import yr_data as Y
M = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/')
test = [json.loads(l) for l in open(os.path.expanduser('~/bones-forge/yo/read/data/test_items.jsonl'))]
T = {i['id']: i['answer'] for i in test}; TP = {i['paper'] for i in test}
real_open = open
for snap in ['list.json.pre-removal-20261102','list.json.pre-unimind-20261102','list.json.pre-linkfix-20261102','list.json.pre-zen48-20261102','list.json.pre-ramm-20261103','list.json.pre-decker-20261103','list.json']:
    def op(p, *a, **k):
        if p.endswith('matrix_page/list.json'): p = M + snap
        return real_open(p, *a, **k)
    Y.open = op
    P = Y.papers()
    tp = {k for k, r, p in P if Y.split(k) == 'TEST'}
    lab = {f'{k}|{q}': v for k, r, p in P for q, v in Y.truth(r).items() if Y.split(k) == 'TEST'}
    diff = [i for i in T if i in lab and lab[i] != T[i]]
    print(f'{snap:40s} papers {len(P)} TEST {len(tp)} missing_vs_scored {len(TP-tp)} extra {len(tp-TP)} label_diffs {len(diff)}', [d for d in diff][:5])
