"""Independent recount of S1-S3 outcomes from the raw harness JSON, applying the round-plan rule (read-only)."""
import json, glob, math, os, csv
B = '/Users/heuremen/bones-forge/iris_index/claims_stack'
def load(rnd, d):
    fs = glob.glob(f'{B}/{rnd}/{d}/eval_*'); return json.load(open(fs[0]))['results'] if False else None
def raw(rnd, d):
    fs = glob.glob(f'{B}/{rnd}/{d}/eval_*')
    if not fs: return None
    j = json.load(open(fs[0]))
    return j.get('results', j)
def g(r, task, key):
    t = r[task]; se = t[key.replace(',', '_stderr,', 1)]
    return 100 * t[key], 100 * se
def mean(vs):
    n = len(vs); return sum(v[0] for v in vs) / n, math.sqrt(sum(v[1] ** 2 for v in vs)) / n
def classify(s, variants, rnd):
    rd = 0.05 if rnd != 'S3' else 0.005
    inside = []; lo_all = hi_all = True; out = {}
    for name, (v, se) in variants.items():
        w = 1.96 * se + rd; out[name] = (round(v, 3), round(w, 3))
        if abs(s - v) <= w: inside.append(name)
        lo_all &= s > v + w; hi_all &= s < v - w
    if inside: oc = 'CONSISTENT'
    elif lo_all: oc = 'stated ABOVE every interval (printed BELOW)'
    elif hi_all: oc = 'stated BELOW every interval (printed ABOVE)'
    else: oc = 'between/both sides'
    margins = {n: round(min(abs(s - (v - w)), abs(s - (v + w))), 3) for n, (v, w) in out.items()}
    return oc, inside, out, margins
claims = {}
for rnd in ('s1', 's2', 's3'):
    for row in csv.DictReader(open(f'{B}/claims_{rnd}.csv')): claims[row['claim_id']] = row
res = {}
# S1
r = raw('s1', 'hellaswag'); res['S1-04'] = {m: g(r, 'hellaswag', m + ',none') for m in ('acc', 'acc_norm')}
ra, rc = raw('s1', 'arc_easy'), raw('s1', 'arc_challenge'); res['S1-05'] = {m: mean([g(ra, 'arc_easy', m + ',none'), g(rc, 'arc_challenge', m + ',none')]) for m in ('acc', 'acc_norm')}
r = raw('s1', 'piqa'); res['S1-06'] = {m: g(r, 'piqa', m + ',none') for m in ('acc', 'acc_norm')}
v = {}
for d in ('bbh_plain', 'bbh_chat'):
    r = raw('s1', d); subs = [k for k in r if k.startswith('bbh_fewshot_')]
    v[d] = mean([g(r, k, 'exact_match,none') for k in subs]); v[d + '_n'] = len(subs)
res['S1-08'] = {k: x for k, x in v.items() if not k.endswith('_n')}; print('bbh subtasks', v['bbh_plain_n'], v['bbh_chat_n'])
o = {}
for d in ('gsm8k_plain', 'gsm8k_chat', 'gsm8k_chatmt'):
    r = raw('s1', d)
    for f in ('strict-match', 'flexible-extract'): o[f'{d} {f}'] = g(r, 'gsm8k', 'exact_match,' + f)
res['S1-09'] = o
# S2
def mmlu(r):
    subs = {k: x for k, x in r.items() if k.startswith('mmlu_') and 'acc,none' in x and k not in ('mmlu_humanities', 'mmlu_stem', 'mmlu_social_sciences', 'mmlu_other')}
    N = sum(x['sample_len'] for x in subs.values())
    return {'weighted': (100 * sum(x['acc,none'] * x['sample_len'] for x in subs.values()) / N, 100 * math.sqrt(sum((x['sample_len'] / N * x['acc_stderr,none']) ** 2 for x in subs.values()))), 'macro': mean([(100 * x['acc,none'], 100 * x['acc_stderr,none']) for x in subs.values()]), 'n_subs': len(subs), 'N': N}
for rnd in ('s2', 's3'):
    m = mmlu(raw(rnd, 'mmlu')); print(rnd, 'mmlu n_subs', m.pop('n_subs'), 'N', m.pop('N'))
    res['S2-03' if rnd == 's2' else 'S3-01'] = m
for cid, t in (('S2-05', 'arc_challenge'), ('S2-06', 'boolq'), ('S2-08', 'hellaswag'), ('S2-09', 'openbookqa'), ('S2-10', 'piqa'), ('S2-11', 'social_iqa'), ('S2-13', 'winogrande')):
    r = raw('s2', t); ms = [m.strip() for m in claims[cid]['metric_variants'].split(';')]
    res[cid] = {m: g(r, t, m + ',none') for m in ms}
o = {}
for d in ('gsm8k_cot_plain', 'gsm8k_cot_chat'):
    r = raw('s2', d)
    for f in ('strict-match', 'flexible-extract'): o[f'{d} {f}'] = g(r, 'gsm8k_cot', 'exact_match,' + f)
res['S2-16'] = o
r = raw('s3', 'bbh_cot_chat'); subs = [k for k in r if k.startswith('bbh_cot_fewshot_')]; print('s3 bbh subs', len(subs))
res['S3-03'] = {'bbh chat mean': mean([g(r, k, 'exact_match,get-answer') for k in subs])}
o = {}
r = raw('s3', 'gsm8k_plain')
for f in ('strict-match', 'flexible-extract'): o['plain ' + f] = g(r, 'gsm8k', 'exact_match,' + f)
r = raw('s3', 'gsm8k_cot_chat')
for f in ('strict-match', 'flexible-extract'): o['chat ' + f] = g(r, 'gsm8k_cot', 'exact_match,' + f)
res['S3-11'] = o
pub = {}
for rnd in ('s1', 's2', 's3'): pub.update(json.load(open(f'{B}/outcomes_{rnd}.json')))
for cid, variants in res.items():
    s = float(claims[cid]['stated_value'])
    oc, inside, out, margins = classify(s, variants, cid[:2])
    print(f"{cid} stated {s} | mine: {oc} inside={inside} | published: {pub[cid]['outcome']}")
    for n, (v_, w_) in out.items(): print(f'     {n}: {v_} +- {w_}  -> [{v_-w_:.3f}, {v_+w_:.3f}] margin {margins[n]}')
