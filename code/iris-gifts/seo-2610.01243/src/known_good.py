#!/usr/bin/env python3
"""known_good.py (ours): Seo, arXiv 2610.01243, three headline numbers from runs/*.jsonl. First-slot share of valid choices, share of
prompts whose selected image changes across the three orders, and call-level agreement between two runs of the 4B judge. Data only."""
import json, os, sys, glob, collections
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'JudgeActs', 'runs')
def load(p): return [json.loads(l) for l in open(p)]
def summary(R, name):
    ok = [r for r in R if r.get('parse_ok') and r.get('parsed')]
    first = sum(r['parsed']['choice'] == 'A' for r in ok)
    byp = collections.defaultdict(set); n_ord = collections.Counter()
    for r in ok: byp[r['prompt_id']].add(r['selected_id']); n_ord[r['prompt_id']] += 1
    full = [p for p in byp if n_ord[p] == 3]; ch = sum(len(byp[p]) > 1 for p in full)
    print('%-28s calls %d, valid %d | first slot (A) %d = %.3f | prompts with all three orders valid %d, selection changes %d = %.3f' % (name, len(R), len(ok), first, first / len(ok), len(full), ch, ch / len(full)))
    return {(r['prompt_id'], str(r['permutation'])): r.get('selected_id') for r in R}
a = summary(load(T + '/qwen_main.jsonl'), 'qwen 4B main (bf16)')
for p in sorted(glob.glob(T + '/extension/*.jsonl')):
    b = summary(load(p), os.path.basename(p))
    common = set(a) & set(b)
    if common: print('   call-level same selection as qwen main: %d of %d = %.3f' % (sum(a[k] == b[k] for k in common), len(common), sum(a[k] == b[k] for k in common) / len(common)))
