#!/usr/bin/env python3
"""clustered_read.py (13 Nov 2026): re-read the night ladder evals with the paper as the unit.

The eval sets hold several chunks per paper, so chunk-level Wilson intervals are too narrow (handoff caveat, MORNING.md).
For each model against base, on the same items: flips counted both ways (base miss -> model flag, base flag -> model miss),
an exact two-sided sign test on the discordant chunks, and a paper-cluster bootstrap (resample papers, keep all their chunks)
for recall, false-flag rate and their differences from base. Outcome per measure: ABOVE / BELOW / CONSISTENT / CANNOT_TELL
against base, where CANNOT_TELL means the 95% interval of the difference reaches both 0 and +-0.10 (the size that matters,
fixed here before reading). Defined after the data: the 0.10 size, chosen at this writing, after the chunk-level rows were seen.
Usage: python3 clustered_read.py [model ...]   (default lora_v4 lora_v6; reads results/<model>_<set>.json)"""
import json, os, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'results')
SETS = ('test_hand', 'test_pipeline'); B = 5000; MATTER = 0.10

def items(name, s):
    return {(x['arxiv'], x['chunk']): x for x in json.load(open(os.path.join(R, f'{name}_{s}.json')))['items']}

def sign_p(a, b):
    n = a + b
    if n == 0: return 1.0
    k = min(a, b); p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)

def rates(keys, M):
    pos = [k for k in keys if M[k]['label'] == 1]; neg = [k for k in keys if M[k]['label'] == 0]
    r = sum(M[k]['flag'] for k in pos) / len(pos) if pos else float('nan')
    f = sum(M[k]['flag'] for k in neg) / len(neg) if neg else float('nan')
    return r, f

def outcome(lo, hi):
    if lo > 0: return 'ABOVE'
    if hi < 0: return 'BELOW'
    if lo > -MATTER and hi < MATTER: return 'CONSISTENT'
    return 'CANNOT_TELL'

def read(model, s, rng):
    Bm, Mm = items('base', s), items(model, s)
    both = set(Bm) & set(Mm); dropped = len(set(Bm) ^ set(Mm))
    unparsed = {'base': sum(1 for k in both if Bm[k]['flag'] is None), model: sum(1 for k in both if Mm[k]['flag'] is None)}
    keys = sorted(k for k in both if Bm[k]['flag'] is not None and Mm[k]['flag'] is not None)   # unparsed replies counted by arm, left out of the pairing
    papers = sorted({k[0] for k in keys}); byp = {p: [k for k in keys if k[0] == p] for p in papers}
    out = {'set': s, 'chunks': len(keys), 'papers': len(papers), 'unmatched_chunks': dropped, 'unparsed_by_arm': unparsed}
    for lab, nm in ((1, 'pos'), (0, 'neg')):
        ks = [k for k in keys if Bm[k]['label'] == lab]
        up = sum(1 for k in ks if Mm[k]['flag'] and not Bm[k]['flag']); dn = sum(1 for k in ks if Bm[k]['flag'] and not Mm[k]['flag'])
        out[nm] = {'chunks': len(ks), 'papers': len({k[0] for k in ks}), 'base_flag': sum(Bm[k]['flag'] for k in ks), 'model_flag': sum(Mm[k]['flag'] for k in ks),
                   'flips_base_miss_to_flag': up, 'flips_flag_to_miss': dn, 'sign_test_p': round(sign_p(up, dn), 4)}
    br, bf = rates(keys, Bm); mr, mf = rates(keys, Mm)
    boot = {'recall': [], 'false_flag': [], 'd_recall': [], 'd_false_flag': []}
    for _ in range(B):
        ks = [k for p in (rng.choice(papers) for _ in papers) for k in byp[p]]
        b_r, b_f = rates(ks, Bm); m_r, m_f = rates(ks, Mm)
        for nm, v in (('recall', m_r), ('false_flag', m_f), ('d_recall', m_r - b_r), ('d_false_flag', m_f - b_f)):
            if not math.isnan(v): boot[nm].append(v)
    q = lambda v: [round(sorted(v)[int(0.025 * len(v))], 3), round(sorted(v)[int(0.975 * len(v)) - 1], 3)]
    out['recall'] = {'base': round(br, 3), 'model': round(mr, 3), 'model_ci95_paper': q(boot['recall']), 'diff': round(mr - br, 3), 'diff_ci95_paper': q(boot['d_recall'])}
    out['false_flag'] = {'base': round(bf, 3), 'model': round(mf, 3), 'model_ci95_paper': q(boot['false_flag']), 'diff': round(mf - bf, 3), 'diff_ci95_paper': q(boot['d_false_flag'])}
    out['recall']['outcome'] = outcome(*out['recall']['diff_ci95_paper']); out['false_flag']['outcome'] = outcome(*out['false_flag']['diff_ci95_paper'])
    return out

def main():
    models = sys.argv[1:] or ['lora_v4', 'lora_v6']; rng = random.Random(20261113)
    res = {'ruler': f'paper-cluster bootstrap, {B} resamples, seed 20261113; exact sign test on discordant chunks; size that matters {MATTER} (defined after the data)',
           'models': {m: [read(m, s, rng) for s in SETS] for m in models}}
    json.dump(res, open(os.path.join(R, 'clustered_read.json'), 'w'), indent=1)
    for m, rows in res['models'].items():
        for r in rows:
            print(f"{m} {r['set']}: {r['papers']} papers, {r['chunks']} chunks, unparsed {r['unparsed_by_arm']} | recall {r['recall']['base']}->{r['recall']['model']} diff {r['recall']['diff']} {r['recall']['diff_ci95_paper']} {r['recall']['outcome']}"
                  f" (flips +{r['pos']['flips_base_miss_to_flag']}/-{r['pos']['flips_flag_to_miss']}, p {r['pos']['sign_test_p']}) | false-flag {r['false_flag']['base']}->{r['false_flag']['model']} diff {r['false_flag']['diff']} {r['false_flag']['diff_ci95_paper']} {r['false_flag']['outcome']}"
                  f" (flips +{r['neg']['flips_base_miss_to_flag']}/-{r['neg']['flips_flag_to_miss']}, p {r['neg']['sign_test_p']})")

if __name__ == '__main__': main()
