"""publish_hf_bench.py: stages every FINISHED bench round (all ten models, all three arms, full item count) as one dataset and uploads it to huggingface.co/indahl/iris-faults-guards-bench.
Per round: items.json, the plan(s), CODE.sha256, score.py/synth.py/run.py as committed, raw replies (out/<model>/<arm>.jsonl), and the scored results. Needs the indahl login (hf auth). Never prints a token."""
import os, sys, json, shutil, glob
B = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(B, 'hf_stage_bench'); ORDER = ['phi4-mini', 'mistral:7b', 'falcon3:3b', 'smollm2:1.7b', 'llama3.1:8b', 'gemma3:4b', 'olmo2:7b', 'granite3.3:2b', 'qwen3:4b', 'deepseek-r1:1.5b']
DIRS = [(1, 'faultsbench2')] + [(n, f'faultsbench_r{n}') for n in range(2, 12)]
def complete(d, n):
    return all(os.path.exists(os.path.join(B, d, 'out', m.replace(':', '_'), a + '.jsonl')) and sum(1 for _ in open(os.path.join(B, d, 'out', m.replace(':', '_'), a + '.jsonl'))) >= n for m in ORDER for a in ('bare', 'bare_copy', 'guard'))
shutil.rmtree(S, ignore_errors=True); os.makedirs(S); done = []
res = json.load(open(os.path.join(B, 'results_status.json'))) if os.path.exists(os.path.join(B, 'results_status.json')) else {'rounds': []}
for rn, d in DIRS:
    dp = os.path.join(B, d)
    if not os.path.isdir(dp): continue
    n = len(json.load(open(os.path.join(dp, 'items.json'))))
    if not complete(d, n): continue
    o = os.path.join(S, f'round-{rn:02d}'); os.makedirs(o)
    for f in ['items.json', 'CODE.sha256', 'run.py', 'score.py', 'synth.py', 'items.py'] + [os.path.basename(p) for p in glob.glob(os.path.join(dp, 'PLAN*.md'))]:
        if os.path.exists(os.path.join(dp, f)): shutil.copy(os.path.join(dp, f), o)
    for m in ORDER:
        mk = m.replace(':', '_'); os.makedirs(os.path.join(o, 'replies', mk))
        for a in ('bare', 'bare_copy', 'guard'): shutil.copy(os.path.join(dp, 'out', mk, a + '.jsonl'), os.path.join(o, 'replies', mk, a + '.jsonl'))
    rr = [r for r in res['rounds'] if r['round'] == rn]
    if rr: json.dump(rr[0], open(os.path.join(o, 'scored.json'), 'w'), indent=1)
    done.append(rn)
if not done: print('no finished rounds'); sys.exit(0)
TERMS = "Free to download, read and cite with attribution (Heuremen LLC, link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted. Policy: https://indahl.ai/terms#ai-training"
open(os.path.join(S, 'README.md'), 'w').write(f"""---
license: other
license_name: heuremen-attribution-no-ai-training
license_link: https://indahl.ai/terms#ai-training
pretty_name: "IRIS Faults and Guards bench: raw replies and scores"
tags:
- llm-evaluation
- reproducibility
- open-weight-models
---

# IRIS Faults and Guards bench

Open-weight models served locally (Ollama), temperature 0, fixed seed. Per model and round: a bare arm, a bare repeat (determinism check) and a guard arm with the wording of a published Fault and Guard appended to the prompt. Four families: forced verdict (Fault 19, Guard 8), verdict without a width (Fault 25), unchecked equals sign (Fault 29, Guard 27), best of n (Fault 3, Guard 9).

Each finished round is one folder: `round-NN/` with `items.json` (every item and its truth), the committed plan(s) (`PLAN*.md`, including dated addenda), `CODE.sha256`, the code as run (`run.py`, `score.py`, `synth.py`, `items.py`), the raw replies per model and arm (`replies/<model>/<arm>.jsonl`) and the scored results with Wilson intervals (`scored.json`). Plans were committed before any reply existed. Rounds are reported side by side and never pooled.

Finished rounds in this release: {', '.join(str(x) for x in done)}. Live progress and results: https://indahl.ai/iris

## Terms

{TERMS}

Published by Heuremen LLC. We found it.
""")
from huggingface_hub import HfApi
api = HfApi(); print('logged in as', api.whoami()['name']); rid = 'indahl/iris-faults-guards-bench'
api.create_repo(rid, repo_type='dataset', exist_ok=True)
api.upload_folder(folder_path=S, repo_id=rid, repo_type='dataset', commit_message=f'Heuremen LLC: rounds {done}')
print('uploaded', rid, 'rounds', done)
