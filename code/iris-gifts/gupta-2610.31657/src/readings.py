#!/usr/bin/env python3
"""K1, G1, G2 (PLAN 03b6048, committed before this ran). Gupta, arXiv 2610.31657. Our code; his released files read as data only."""
import json, os, math, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'unz', 'routeguard_camera_ready_supplement', 'code', 'artifacts', 'ictai2026')
Y = json.load(open(D + '/table_ii_common_subset.json'))['true_labels']
def load(m, s): return json.load(open('%s/llm_inputs/%s__%s__model_reported.json' % (D, m, s)))
def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - h) / d, (c + h) / d
runs = [('gpt4o_mini_zero_shot', 'zero_shot'), ('gpt4o_mini_few_shot_k3', 'few_shot'), ('haiku_zero_shot', 'zero_shot'), ('haiku_few_shot_k3', 'few_shot'),
        ('llama_zero_shot', 'zero_shot'), ('llama_few_shot_k3', 'few_shot'), ('qwen_zero_shot', 'zero_shot'), ('qwen_few_shot_k3', 'few_shot')]
R = {}
print('K1 and G2: accuracy per model and setting against the released true labels (parse failures scored wrong, as the paper does)')
for m, s in runs:
    d = load(m, s); P = d['predictions']; ok = [P[i] == Y[i] for i in range(len(Y))]; k = sum(ok); R[(m, s)] = (d, ok)
    pf = sum(x != 'OK' for x in d['parse_status'])
    print('  %-24s accuracy %.3f [%.3f, %.3f] (stored %.3f) | parse failures %d' % (m, k / len(Y), *wil(k, len(Y)), d['classification']['accuracy'], pf))
print('\nG2 paired few-shot minus zero-shot, exact McNemar on discordant tickets')
for base in ('gpt4o_mini', 'haiku', 'llama', 'qwen'):
    z = R[(base + '_zero_shot', 'zero_shot')][1]; f = R[(base + '_few_shot_k3', 'few_shot')][1]
    b = sum(fi and not zi for zi, fi in zip(z, f)); c = sum(zi and not fi for zi, fi in zip(z, f)); N = b + c
    p = min(1.0, 2 * sum(math.comb(N, i) for i in range(min(b, c) + 1)) / 2 ** N) if N else 1.0
    print('  %-12s few minus zero %+.3f | few-only right %d, zero-only right %d | p %.2g' % (base, (sum(f) - sum(z)) / len(Y), b, c, p))
print('\nG1 model-reported confidence: share exactly 1.0 and distinct values; few-shot examples in the prompt all show 1.0')
for base in ('gpt4o_mini', 'haiku', 'llama', 'qwen'):
    z = R[(base + '_zero_shot', 'zero_shot')][0]['confidences']; f = R[(base + '_few_shot_k3', 'few_shot')][0]['confidences']
    up = sum(1 for a, b2 in zip(z, f) if a is not None and b2 is not None and a < 1.0 and b2 == 1.0)
    print('  %-12s zero-shot: 1.0 on %4d of 1000, %2d distinct | few-shot: 1.0 on %4d of 1000, %2d distinct | tickets moving to exactly 1.0 from below: %d'
          % (base, sum(x == 1.0 for x in z), len(set(z)), sum(x == 1.0 for x in f), len(set(f)), up))

NAMES = {'gpt4o_mini': 'GPT-4o-mini (alias, queried 2026-05-22)', 'haiku': 'Claude Haiku 4.5', 'llama': 'Meta-Llama-3-8B-Instruct-Lite (Together, documented INT4)',
         'qwen': 'Qwen2.5-7B-Instruct-Turbo (Together, documented FP8)'}
def auroc(conf, ok):   # probability a correct reply outranks a wrong one, ties counted half
    pos = [c for c, o in zip(conf, ok) if o]; neg = [c for c, o in zip(conf, ok) if not o]
    if not pos or not neg: return float('nan')
    neg_sorted = sorted(neg); import bisect
    return sum(bisect.bisect_left(neg_sorted, c) + 0.5 * (bisect.bisect_right(neg_sorted, c) - bisect.bisect_left(neg_sorted, c)) for c in pos) / (len(pos) * len(neg))
print('\nG3 correctness AUROC of model-reported confidence, all tickets and parsed replies only (Addendum 1)')
for base in ('gpt4o_mini', 'haiku', 'llama', 'qwen'):
    for m, s_ in ((base + '_zero_shot', 'zero_shot'), (base + '_few_shot_k3', 'few_shot')):
        d, ok = R[(m, s_)]; c = d['confidences']; ps = [x == 'OK' for x in d['parse_status']]
        cp = [ci for ci, p_ in zip(c, ps) if p_]; op = [oi for oi, p_ in zip(ok, ps) if p_]
        print('  %-58s %-9s all %.3f | parsed only %.3f (n %d)' % (NAMES[base], s_, auroc(c, ok), auroc(cp, op), len(cp)))
