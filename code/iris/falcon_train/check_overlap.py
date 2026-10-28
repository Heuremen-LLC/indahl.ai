"""check_overlap.py: no training prompt is identical, as full text, to any prompt in bench rounds 1 to 13 or either evaluation set, and no training story is a bench story. Number coincidences are counted and printed for disclosure: P1 and P2 draw from small number spaces, so a (k, n) pair or a pair of scores can recur under a different story. That is not a failure."""
import json, os, glob, importlib.util, sys, collections
from common import B, items_module, train_seeds
from stories import TRAIN, EVAL
def load_prompts(d):
    spec = importlib.util.spec_from_file_location('it_' + os.path.basename(d), os.path.join(d, 'items.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return {m.prompt(it, 'bare') for it in m.I}, {(it['fam'], tuple(sorted((k, str(v)) for k, v in it.items() if k in ('a', 'b', 'ha', 'hb', 'k', 'n', 'shown', 'xs')))) for it in m.I}
bp, bn = set(), set()
for d in glob.glob(os.path.join(B, 'faultsbench2')) + glob.glob(os.path.join(B, 'faultsbench_r*')) + glob.glob(os.path.join(B, 'faultsbench_t*')):
    p, n = load_prompts(d); bp |= p; bn |= n
tp, tn = set(), collections.Counter()
for si, t in enumerate(TRAIN):
    for rep in range(3):
      m = items_module(t, *train_seeds(si, rep))
      for it in m.I:
        tp.add(m.prompt(it, 'bare')); k = (it['fam'], tuple(sorted((a, str(v)) for a, v in it.items() if a in ('a', 'b', 'ha', 'hb', 'k', 'n', 'shown', 'xs'))))
        if k in bn: tn[it['fam']] += 1
meta = json.load(open('train_meta.json')); used = {r['prompt'] for r in meta}
print('training prompts identical to a bench or evaluation prompt:', len(used & bp), 'of', len(used))
print('number coincidences with a bench item under another story, by family:', dict(tn))
assert not (used & bp)
