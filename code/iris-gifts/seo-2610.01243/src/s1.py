#!/usr/bin/env python3
"""S1 (PLAN 60806aa, committed before this ran): the unanimity gate under two runs of one judge (Qwen3-VL-4B, bf16 main and 8-bit MLX).
Gain over random = utility (mean alignment rating) of the returned image minus the pool mean; bootstrap over prompts, 10,000, three seeds."""
import json, os, collections, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'JudgeActs')
U = {}; pool = {}
for l in open(T + '/data/derived/main.jsonl'):
    d = json.loads(l); hs = [float(c['utility']) for c in d['candidates']]
    for c in d['candidates']: U[c['id']] = float(c['utility'])
    pool[d['prompt_id']] = float(np.mean(hs))
def gate(path):
    sel = collections.defaultdict(dict)
    for l in open(path):
        r = json.loads(l)
        if r.get('parse_ok') and r.get('selected_id'): sel[r['prompt_id']][str(r['permutation'])] = r['selected_id']
    return {p: list(v.values())[0] for p, v in sel.items() if len(v) == 3 and len(set(v.values())) == 1}
def gain(keep):
    return np.array([U[s] - pool[p] for p, s in sorted(keep.items())])
def ci(g):
    out = []
    for seed in (1, 2, 3):
        i = np.random.default_rng(seed).integers(0, len(g), size=(10000, len(g))); out.append(np.percentile(g[i].mean(1), [2.5, 97.5]))
    return ' '.join('[%.3f, %.3f]' % tuple(x) for x in out)
A = gate(T + '/runs/qwen_main.jsonl'); B = gate(T + '/runs/extension/qwen4b_mlx_main.jsonl')
both = set(A) & set(B); onlyA = set(A) - set(B); onlyB = set(B) - set(A); diffsel = [p for p in both if A[p] != B[p]]
print('unanimity gate: bf16 keeps %d, 8-bit keeps %d, both %d (different unanimous image on %d), bf16 only %d, 8-bit only %d, union %d' % (len(A), len(B), len(both), len(diffsel), len(onlyA), len(onlyB), len(set(A) | set(B))))
for name, keep in (('bf16 gate (printed 121, 0.141 [0.110, 0.173])', A), ('8-bit gate', B), ('kept by both, bf16 choice', {p: A[p] for p in both}),
                   ('bf16 only', {p: A[p] for p in onlyA}), ('8-bit only', {p: B[p] for p in onlyB})):
    g = gain(keep); print('  %-48s n %3d  gain %+.3f  95%% CI by seed %s' % (name, len(g), g.mean(), ci(g) if len(g) > 1 else '-'))

# Referee pass (30 Oct): how the moves arise, call by call. The paper already prints the 8-bit MLX gate (Table 12, 128 prompts, 0.135);
# the overlap above is the new part. Counted here: prompts with at least one call whose selected image differs between the two runs, and
# for the prompts that change gate membership, how many of their three calls differ.
def calls(path):
    out = {}
    for l in open(path):
        r = json.loads(l); out[(r['prompt_id'], str(r['permutation']))] = r.get('selected_id')
    return out
ca, cb = calls(T + '/runs/qwen_main.jsonl'), calls(T + '/runs/extension/qwen4b_mlx_main.jsonl')
nd = collections.Counter(p for (p, k) in ca if ca[(p, k)] != cb.get((p, k)))
moved = (set(A) ^ set(B))
print('\nprompts with at least one call selecting a different image: %d of 300 | calls differing: %d of 900' % (len(nd), sum(nd.values())))
print('of the %d prompts that change gate membership: differing calls per prompt %s' % (len(moved), dict(collections.Counter(nd[p] for p in moved))))
g = gain({p: B[p] for p in onlyB}); print('8-bit-only set (n %d): gain %+.2f, %d of %d below zero; too small for an interval worth printing' % (len(g), g.mean(), (g < 0).sum(), len(g)))
