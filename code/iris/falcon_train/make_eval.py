"""make_eval.py: builds the two evaluation sets faultsbench_tA and faultsbench_tB (FALCON_TRAIN_PLAN.md). Committed before any training."""
import os, sys, shutil, subprocess, json
from common import B, items_source
from stories import EVAL, EVAL_SEEDS
for k, t in EVAL.items():
    d = os.path.join(B, f'faultsbench_t{k}')
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
    for f in ('score.py', 'synth.py'): shutil.copy(os.path.join(B, 'faultsbench_r2', f), d)
    s1, s2 = EVAL_SEEDS[k]; open(os.path.join(d, 'items.py'), 'w').write(items_source(t, s1, s2))
    subprocess.run([sys.executable, 'items.py'], cwd=d, check=True, capture_output=True)
    r = subprocess.run([sys.executable, 'synth.py'], cwd=d, capture_output=True, text=True); assert 'SYNTH PASS' in r.stdout, r.stdout[-300:]
    subprocess.run('shasum -a 256 items.py items.json score.py synth.py > CODE.sha256', shell=True, cwd=d, check=True)
    print('eval set', k, len(json.load(open(os.path.join(d, 'items.json')))), 'items')
