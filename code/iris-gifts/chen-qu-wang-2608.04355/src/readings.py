#!/usr/bin/env python3
"""D1-D4 of PLAN.md (3e889dc, committed before this ran). arXiv 2608.04355. Our code; their files read as data; no reply text printed."""
import os, sys, json, glob, re
from decimal import Decimal, InvalidOperation
import numpy as np
from scipy import stats
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from common import load_jsonl, is_bad, category, decompose, cell_path, DATA
from cells import CELLS
from tokenizers import Tokenizer
cells = list(CELLS); assert len(cells) == 29
tok = Tokenizer.from_file(os.path.join(H, '..', 'tok', '0.8B', 'tokenizer.json'))
CAP = {'mcq': 896, 'open': 1024, 'code': 512}
floor = lambda lab: lab.split(' x ')[0] in ('0.8B', '2B')
print('D1 content margin per cell: helpful, harmful, margin with exact conditional interval (Clopper-Pearson on helpful share of the discordant pairs) | outcome')
out = {'ABOVE': [], 'BELOW': [], 'CONSISTENT': []}
for lab in cells:
    rows = load_jsonl(cell_path(lab)); d = decompose(rows); b, c, n = d['helpful'], d['harmful'], d['n']; m = b + c
    if m:
        lo = stats.beta.ppf(0.025, b, c + 1) if b > 0 else 0.0; hi = stats.beta.ppf(0.975, b + 1, c) if c > 0 else 1.0
        L, U = (2 * lo - 1) * m / n, (2 * hi - 1) * m / n
    else: L = U = 0.0
    oc = 'ABOVE' if L > 0 else ('BELOW' if U < 0 else 'CONSISTENT'); out[oc].append(lab)
    print('  %-24s n %3d | helpful %2d harmful %2d | margin %+.3f [%+.3f, %+.3f] | %s' % (lab, n, b, c, d['d_content'], L, U, oc))
for oc, labs in out.items():
    print('  %s: %d cells (floor scale %d, capable %d)%s' % (oc, len(labs), sum(map(floor, labs)), sum(not floor(l) for l in labs), (' ' + ', '.join(labs)) if oc != 'CONSISTENT' else ''))
print('\nD2 unparseable first answers against the token cap (Qwen3.5 tokenizer, sha256 in tok/SHA256.json; at cap = re-encoded length at least cap minus 3)')
tot = {'bad': 0, 'bad_cap': 0, 'ok': 0, 'ok_cap': 0, 'rec': 0, 'rec_cap': 0}
hist_bad = {}
for lab in cells:
    rows = load_jsonl(cell_path(lab)); gem = lab.startswith('Gemma')
    if gem:
        nb = sum(is_bad(r['a0_answer']) for r in rows); print('  %-24s Gemma cell: %d unparseable first answers (Qwen tokenizer not used; median %d characters)' % (lab, nb, int(np.median([len(r['a0_text']) for r in rows if is_bad(r['a0_answer'])] or [0])))); continue
    cap = CAP[rows[0]['kind']]; assert all(CAP[r['kind']] == cap for r in rows)
    L = [len(tok.encode(r['a0_text'], add_special_tokens=False).ids) for r in rows]
    bad = [i for i, r in enumerate(rows) if is_bad(r['a0_answer'])]; ok = [i for i in range(len(rows)) if i not in set(bad)]
    rec = [i for i in bad if category(rows[i]) == 'recover' and rows[i]['yf'] == 1]
    at = lambda i: L[i] >= cap - 3
    for i in bad: hist_bad[L[i] - cap] = hist_bad.get(L[i] - cap, 0) + 1
    s = dict(bad=len(bad), bad_cap=sum(map(at, bad)), ok=len(ok), ok_cap=sum(map(at, ok)), rec=len(rec), rec_cap=sum(map(at, rec)))
    for k in tot: tot[k] += s[k]
    n = len(rows)
    print('  %-24s cap %4d | unparseable %3d, at cap %3d | parsed %3d, at cap %2d | format recoveries (a0 unparseable, final right) %2d, a0 at cap %2d -> recover margin %+.3f, of which a0 at cap %+.3f' % (lab, cap, s['bad'], s['bad_cap'], s['ok'], s['ok_cap'], s['rec'], s['rec_cap'], s['rec'] / n, s['rec_cap'] / n))
print('  all Qwen cells: unparseable %d, at cap %d | parsed %d, at cap %d | recoveries %d, a0 at cap %d' % (tot['bad'], tot['bad_cap'], tot['ok'], tot['ok_cap'], tot['rec'], tot['rec_cap']))
print('  unparseable first answers, re-encoded length minus cap, from -10 to +5:', {k: hist_bad.get(k, 0) for k in range(-10, 6)}, '| below -10:', sum(v for k, v in hist_bad.items() if k < -10), '| above +5:', sum(v for k, v in hist_bad.items() if k > 5))
print('\nD3 answer change by string inequality (their change rate) against numeric equality, GSM8K and MATH cells, both answers parseable')
def num(s):
    try: return Decimal(str(s).replace(',', '').replace('$', '').strip().rstrip('.'))
    except (InvalidOperation, ValueError): return None
for lab in cells:
    if not re.search(r'GSM8K|MATH', lab): continue
    rows = load_jsonl(cell_path(lab)); bo = [r for r in rows if category(r) == 'bothok']
    sdiff = [r for r in bo if str(r['a0_answer']).strip() != str(r['yf_answer']).strip()]
    neq = [r for r in sdiff if num(r['a0_answer']) is not None and num(r['a0_answer']) == num(r['yf_answer'])]
    print('  %-24s both parseable %3d | string change %3d (%.3f) | of those, numerically equal %2d | change rate by number %.3f' % (lab, len(bo), len(sdiff), len(sdiff) / len(bo), len(neq), (len(sdiff) - len(neq)) / len(bo)))
print('\nD4 closure per constrained cell with a paired bootstrap over task ids (10,000 draws, seed 2026), and medians by population')
cmap = {"2B ARC": "2b_arc", "4B ARC": "4b_arc", "0.8B MMLU": "0.8b_mmlu", "2B MMLU": "2b_mmlu", "4B TruthfulQA-MC1": "4b_truthfulqa_mc1", "9B ARC": "9b_arc",
        "9B GSM8K": "9b_gsm8k", "9B MMLU": "9b_mmlu", "4B CommonsenseQA": "4b_commonsenseqa", "4B MMLU": "4b_mmlu", "4B GSM8K": "4b_gsm8k",
        "0.8B ARC": "0.8b_arc", "0.8B GSM8K": "0.8b_gsm8k", "2B GSM8K": "2b_gsm8k"}
rng = np.random.default_rng(2026); B = 10000; CL = {}; BS = {}; A0B = {}
for lab, key in cmap.items():
    c = load_jsonl(os.path.join(DATA, 'constrained', 'constrained_qwen35_%s.jsonl' % key)); s2 = {r['task_id']: r for r in load_jsonl(os.path.join(DATA, 'stage2_qwen35_%s.jsonl' % key))}
    o = np.array([r['yf_correct_original'] - r['a0_correct_original'] for r in c], float); k = np.array([r['yf_correct_constrained'] - r['a0_correct_constrained'] for r in c], float)
    def cont(r):
        if category(r) != 'bothok': return 0.0
        return 1.0 if (r['y0'] == 0 and r['yf'] == 1) else (-1.0 if (r['y0'] == 1 and r['yf'] == 0) else 0.0)
    q = np.array([cont(s2[r['task_id']]) for r in c], float); n = len(c)
    cl = 1 - abs(k.mean() - q.mean()) / abs(o.mean() - q.mean()) if abs(o.mean() - q.mean()) > 1e-12 else float('nan')
    I = rng.integers(0, n, size=(B, n)); om, km, qm = o[I].mean(1), k[I].mean(1), q[I].mean(1)
    den = np.abs(om - qm); bs = np.where(den > 1e-12, 1 - np.abs(km - qm) / np.where(den > 1e-12, den, 1), np.nan)
    CL[lab] = cl; BS[lab] = bs; A0B[lab] = decompose(list(s2.values()))['a0_bad']
    print('  %-20s a0-bad %5.1f%% | closure %6.1f%% | bootstrap 95%% [%6.1f, %6.1f] | draws with a zero denominator %d' % (lab, 100 * A0B[lab], 100 * cl, 100 * np.nanpercentile(bs, 2.5), 100 * np.nanpercentile(bs, 97.5), int(np.isnan(bs).sum())))
pops = {'a0-bad at least 8% (the population the text names)': [l for l in cmap if A0B[l] >= 0.08], 'the ten with a printed closure': ["2B ARC", "4B ARC", "0.8B MMLU", "2B MMLU", "4B TruthfulQA-MC1", "9B ARC", "9B GSM8K", "9B MMLU", "4B CommonsenseQA", "4B MMLU"], 'all fourteen': list(cmap)}
for nm, labs in pops.items():
    med = np.median([CL[l] for l in labs]); bm = np.nanmedian(np.stack([BS[l] for l in labs]), axis=0)
    print('  median closure over %s (%d cells: %s): %.1f%% [%.1f, %.1f]' % (nm, len(labs), ', '.join(labs), 100 * med, 100 * np.nanpercentile(bm, 2.5), 100 * np.nanpercentile(bm, 97.5)))
