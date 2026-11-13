"""Baseline on gold DEV: untrained base and the three teachers. Writes results/baseline_dev.json. Reads no test file."""
import json
from common import *; from score import *
G=gold(); cfg=json.load(open(S+'/teachers/config.json'))['teachers']; out={}
rows={'base':jl_read(S+'/runs/base_dev.jsonl')}
for n in cfg: rows[n]=jl_read(S+'/teachers/%s_round1.jsonl'%n)
for n,r in rows.items():
    V=agree_vec(r,G,'dev'); out[n]={'per_code':table(V,G,'dev'),'pooled':pooled_rate(V)}
json.dump(out,open(S+'/results/baseline_dev.json','w'),indent=1)
with open(S+'/results/baseline_dev.md','w') as f:
    f.write('# Baseline on gold dev\n\nAgreement = (predicted PRESENT) equals (gold PRESENT). 95% Wilson interval. CANNOT_TELL by reason is in baseline_dev.json.\n\n| model | code | n | agree | rate | 95% Wilson | gold present | majority-class rate | decided share |\n|---|---|---|---|---|---|---|---|---|\n')
    for n in out:
        for c in CODES:
            t=out[n]['per_code'][c]; f.write('| %s | %s | %d | %d | %s | %s | %d | %s | %s |\n'%(n,c,t['n'],t['agree'],t['rate'],t['wilson95'],t['gold_present'],t['majority_class_rate'],t['decided_share']))
        p=out[n]['pooled']; f.write('| %s | all | %d | %d | %s | %s | | | |\n'%(n,p['n'],p['agree'],p['rate'],p['wilson95']))
print(open(S+'/results/baseline_dev.md').read()[:1500])
