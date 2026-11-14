#!/usr/bin/env python3
"""curves.py (13 Nov 2026): read results/<model>_<set>_scores.json written by eval_score.py.
1. Instrument check first: the score at 0.5 against the generated flag in results/<model>_<set>.json, item by item. Disagreements are counted
   by direction; if more than 1 in 10 disagree, that model's curve is marked CANNOT_TELL (the score is not reading what generation reads).
2. For fixed cutoffs (0.5, 0.7, 0.9, 0.95, 0.99, 0.999): chunks caught of positives, chunks flagged of negatives.
3. AUC (probability a positive chunk scores above a negative one) with a paper-cluster bootstrap 95% interval, 2,000 resamples, seed 20261113.
Cutoffs are fixed here before the scores exist. Any operating point chosen from these curves is defined after the data.
Writes results/curves.json and prints one line per model and set."""
import json, os, random, glob
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, 'results')
CUTS = [0.5, 0.7, 0.9, 0.95, 0.99, 0.999]; B = 2000

def auc(items):
    pos = [i['score'] for i in items if i['label'] == 1 and i['score'] is not None]
    neg = [i['score'] for i in items if i['label'] == 0 and i['score'] is not None]
    if not pos or not neg: return None
    w = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return w / (len(pos) * len(neg))

def main():
    rng = random.Random(20261113); out = {}
    for f in sorted(glob.glob(os.path.join(R, '*_scores.json'))):
        name = os.path.basename(f)[:-len('_scores.json')]; S = json.load(open(f))['items']
        gen_p = os.path.join(R, name + '.json'); gen = {(x['arxiv'], x['chunk']): x['flag'] for x in json.load(open(gen_p))['items']} if os.path.exists(gen_p) else {}
        up = sum(1 for i in S if gen.get((i['arxiv'], i['chunk'])) is False and (i['score'] or 0) >= 0.5)
        dn = sum(1 for i in S if gen.get((i['arxiv'], i['chunk'])) is True and (i['score'] or 0) < 0.5)
        unread = sum(1 for i in S if gen.get((i['arxiv'], i['chunk'])) is None)
        papers = sorted({i['arxiv'] for i in S}); byp = {p: [i for i in S if i['arxiv'] == p] for p in papers}
        a = auc(S); boots = []
        for _ in range(B):
            v = auc([i for p in (rng.choice(papers) for _ in papers) for i in byp[p]])
            if v is not None: boots.append(v)
        boots.sort(); ci = [round(boots[int(0.025 * len(boots))], 3), round(boots[int(0.975 * len(boots)) - 1], 3)] if boots else None
        npos = sum(i['label'] == 1 for i in S); nneg = sum(i['label'] == 0 for i in S)
        cuts = {str(c): {'caught': sum(1 for i in S if i['label'] == 1 and (i['score'] or 0) >= c), 'pos': npos,
                         'false_flags': sum(1 for i in S if i['label'] == 0 and (i['score'] or 0) >= c), 'neg': nneg} for c in CUTS}
        disagree = up + dn; read = len(S) - unread
        out[name] = {'items': len(S), 'papers': len(papers), 'auc': round(a, 3) if a is not None else None, 'auc_ci95_paper': ci,
                     'score_vs_generation': {'score_flags_generation_did_not': up, 'generation_flags_score_did_not': dn, 'generation_unread': unread,
                                             'state': 'CANNOT_TELL' if read and disagree / read > 0.1 else 'agrees'},
                     'low_mass_items': sum(1 for i in S if i['mass_on_two'] < 0.9), 'cuts': cuts}
        print(f"{name}: AUC {out[name]['auc']} {ci} | score vs generation +{up}/-{dn} ({out[name]['score_vs_generation']['state']}) | "
              + ' '.join(f"@{c}: {cuts[str(c)]['caught']}/{npos} caught, {cuts[str(c)]['false_flags']}/{nneg} false" for c in (0.5, 0.9, 0.99)))
    json.dump({'note': 'cutoffs fixed before the scores existed; any operating point chosen from these curves is defined after the data', 'models': out},
              open(os.path.join(R, 'curves.json'), 'w'), indent=1)

if __name__ == '__main__': main()
