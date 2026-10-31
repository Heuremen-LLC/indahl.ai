#!/usr/bin/env python3
"""Token tie-out for the live arm (zero GPU): for every released trajectory of a model whose GGUF we hold, our rendered prompt per step
(env replica, replay of his logged replies) is tokenized with that GGUF's own vocabulary (llama-cpp-python 0.3.19, vocab_only, BOS added,
special tokens parsed) and the logged reply text is tokenized without BOS; the sum per trajectory is compared with his total_tokens.
Usage: lcpvenv/bin/python tokens_tieout.py <model_id>=<gguf path> ..."""
import os, sys, collections, statistics
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'env'))
import acceptance, prompts
from replay import replay
from llama_cpp import Llama
paths = dict(a.split('=', 1) for a in sys.argv[1:])
tok = {m: Llama(model_path=p, vocab_only=True, verbose=False) for m, p in paths.items()}
cache = {}
def tasks_in(d):
    if d not in cache: cache[d] = acceptance.taskmod.load_dir(os.path.join(acceptance.THEIRS, 'tasks', d))
    return cache[d]
res = collections.defaultdict(list); per_step = collections.defaultdict(collections.Counter); skipped = collections.Counter()
for run in acceptance.collect_runs():
    m = run['model_id']
    if m not in tok: skipped[m] += 1; continue
    L = tok[m]; fam = prompts.FAMILY_OF_MODEL[m]; td = tasks_in(run['tasks_dir'])
    for rec in acceptance.read_jsonl(run['traj']):
        if rec['task_id'] not in td or rec.get('total_tokens') is None: skipped['no task or no total'] += 1; continue
        rp = replay(td[rec['task_id']], rec, run['repair'], fam)
        n = 0
        for prompt, s in zip(rp.traj.prompts, rec['steps']):
            reply = s['raw_model_output_pre_repair'] if s['repair_applied'] else s['raw_model_output']
            n += len(L.tokenize(prompt.encode('utf-8'), add_bos=True, special=True)) + len(L.tokenize((reply or '').encode('utf-8'), add_bos=False, special=True))
        d = rec['total_tokens'] - n; res[m].append(d); per_step[m][(d, len(rec['steps']))] += 1
for m, ds in res.items():
    c = collections.Counter(ds)
    print('%s: %d trajectories | logged minus ours: exact 0 on %d | median %+g | min %+d max %+d | most common %s' % (m, len(ds), c[0], statistics.median(ds), min(ds), max(ds), c.most_common(5)))
    print('   (difference, steps) most common:', per_step[m].most_common(8))
print('runs skipped by model:', dict(skipped))
