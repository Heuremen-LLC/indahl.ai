#!/usr/bin/env python3
"""K and S1-S4 (PLAN 0721111, committed before this ran). Sasi, arXiv 2607.25451. Our code; his result JSON read as data."""
import os, json, math, glob
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'hf', 'results')
def J(n): return json.load(open(os.path.join(R, n)))
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
T1 = {'160m': ('fp32', [('fp32', .756, 25.60, 12.27, 1.000, 1.000, None), ('fp16', .746, 25.84, 12.37, .987, .992, None), ('int8', .734, 26.07, 12.48, .971, .983, 1.7), ('nf4', .294, 38.39, 17.33, .389, .708, 2.7), ('fp4', .176, 48.61, 21.22, .233, .578, 2.7)]),
      '410m': ('fp32', [('fp32', .834, 15.86, 8.88, 1.000, 1.000, None), ('fp16', .822, 15.87, 8.89, .986, .999, None), ('int8', .810, 16.13, 8.98, .971, .989, 2.6), ('nf4', .228, 32.40, 15.35, .273, .579, 2.4), ('rtn4', .176, 37.14, 18.49, .211, .480, 2.1), ('fp4', .132, 39.60, 20.59, .158, .431, 2.2)]),
      '1b': ('fp16', [('fp16', .830, 12.68, 7.58, 1.000, 1.000, None), ('int8', .826, 12.72, 7.60, .995, .997, 1.5), ('nf4', .596, 13.30, 7.90, .718, .959, 8.0), ('rtn4', .498, 14.28, 8.32, .600, .910, 5.4), ('fp4', .460, 14.25, 8.32, .554, .911, 6.3)])}
print('K Table 1 from the result files (extract, PPL WT, PPL Pile, m, c, s against the printed digits)')
bad = 0
for size, (ref, rows) in T1.items():
    tag = 'pythia-%s-deduped' % size; er = J('extract_%s_%s_s0.json' % (tag, ref))['exact_match']; pr = J('ppl_%s_%s_pile.json' % (tag, ref))['perplexity']
    for q, ex, wt, pile, m, c, s in rows:
        e = J('extract_%s_%s_s0.json' % (tag, q)); w = J('ppl_%s_%s.json' % (tag, q))['perplexity']; pp = J('ppl_%s_%s_pile.json' % (tag, q))['perplexity']
        mm, cc = e['exact_match'] / er, pr / pp; ss = (math.log(mm) / math.log(cc)) if q != ref and cc != 1 and mm > 0 and not (size in ('160m', '410m') and q == 'fp16') else None
        ok = (round(e['exact_match'], 3) == ex and round(w, 2) == wt and round(pp, 2) == pile and round(mm, 3) == m and round(cc, 3) == c and (s is None or round(ss, 1) == s))
        bad += not ok
        print('  %-4s %-5s n %d extract %.3f | WT %.2f | Pile %.2f | m %.3f | c %.3f | s %s | matches printed: %s' % (size, q, e['n'], e['exact_match'], w, pp, mm, cc, ('%.2f' % ss) if ss else '-', ok))
print('  rows not matching: %d' % bad)
print('\nS1 Wilson 95%% for every extraction rate (n 500) and the difference from the reference (Newcombe, unpaired)')
for size, (ref, rows) in T1.items():
    tag = 'pythia-%s-deduped' % size; r = J('extract_%s_%s_s0.json' % (tag, ref)); kr = round(r['exact_match'] * r['n'])
    for q, *_ in rows:
        e = J('extract_%s_%s_s0.json' % (tag, q)); k = round(e['exact_match'] * e['n']); lo, hi = wilson(k, e['n'])
        if q == ref: print('  %-4s %-5s %d/%d = %.3f [%.3f, %.3f] (reference)' % (size, q, k, e['n'], k / e['n'], lo, hi)); continue
        d, dl, dh = newcombe(k, e['n'], kr, r['n'])
        print('  %-4s %-5s %d/%d = %.3f [%.3f, %.3f] | minus reference %+.3f [%+.3f, %+.3f]' % (size, q, k, e['n'], k / e['n'], lo, hi, d, dl, dh))
print('\nS2 the 410M runs at other seeds (not cited in the paper)')
for s in (0, 1, 2):
    f = J('extract_pythia-410m-deduped_fp16_s%d.json' % s); n4 = J('extract_pythia-410m-deduped_nf4_s%d.json' % s)
    kf, kn = round(f['exact_match'] * f['n']), round(n4['exact_match'] * n4['n'])
    print('  seed %d: FP16 n %d %.3f [%.3f, %.3f] | NF4 n %d %.3f [%.3f, %.3f] | m (NF4 over FP16) %.3f, memorization lost %.3f' % (s, f['n'], f['exact_match'], *wilson(kf, f['n']), n4['n'], n4['exact_match'], *wilson(kn, n4['n']), n4['exact_match'] / f['exact_match'], 1 - n4['exact_match'] / f['exact_match']))
print('\nS3 two sentences against Table 1')
e = J('extract_pythia-1b-deduped_nf4_s0.json'); r = J('extract_pythia-1b-deduped_fp16_s0.json')
print('  "over seventy percent of memorized sequences": 1B NF4 extracts %.3f of the sample; m against the FP16 reference %.3f' % (e['exact_match'], e['exact_match'] / r['exact_match']))
mm = e['exact_match'] / r['exact_match']
for corp, suf in (('Pile', '_pile'), ('WikiText', '')):
    c = J('ppl_pythia-1b-deduped_fp16%s.json' % suf)['perplexity'] / J('ppl_pythia-1b-deduped_nf4%s.json' % suf)['perplexity']
    print('  "selectivity about seven": 1B NF4 s on %-8s %.2f' % (corp, math.log(mm) / math.log(c)))
print('\nS4 the reference against the definition: extraction at the reference precision on sequences defined as reproduced by the full-precision model')
for size, (ref, _) in T1.items():
    e = J('extract_pythia-%s-deduped_%s_s0.json' % (size, ref)); print('  %-4s %s %.3f (%d of %d not reproduced)' % (size, ref, e['exact_match'], e['n'] - round(e['exact_match'] * e['n']), e['n']))
txt = ' '.join(open(f, errors='ignore').read().lower() for f in glob.glob(os.path.join(R, '..', '..', 'repo', '**', '*.md'), recursive=True) + glob.glob(os.path.join(R, '..', '*.md')))
print('  released README/markdown mentions of why the reference falls short (words "not reproduce", "reference", "fp32" near "memorized"):', any(k in txt for k in ('do not reproduce', 'does not reproduce', 'not all memorized', 'falls short')))
