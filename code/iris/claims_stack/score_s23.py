"""score_s23.py S2|S3: reads the harness outputs of round S2 or S3 and applies the committed outcome rule (ROUND_S2.md, ROUND_S3.md and their
addenda). Interval per variant: our value +- (1.96 x harness standard error + the card's rounding). CONSISTENT if the stated value is inside any
listed variant. Outside every variant: the harness differs (S2) or is not named (S3), so CANNOT_TELL with the direction under our harness beside it
(S2 Addendum 2, S3 Addendum 3). Parser notes from HANDCHECK_S2.md / HANDCHECK_S3.md ride beside the GSM8K and BBH rows. Writes outcomes_<round>.json."""
import json, glob, os, math, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1].upper(); r_ = R.lower()
ROUND = {'S2': 0.05, 'S3': 0.005}[R]   # the card's printed rounding
HARNESS = {'S2': "The card's figures come from Microsoft's internal benchmark platform", 'S3': 'The card does not name its harness or prompts'}[R]
def load(d):
    fs = glob.glob(os.path.join(HERE, r_, d, 'eval_*')); return json.load(open(fs[0])) if fs else None
def one(r, task, key):
    t = (r or {}).get(task)
    if not t or key not in t: return None
    return 100 * t[key], 100 * t[key.replace(',', '_stderr,', 1)]
def mmlu(r):
    subs = {k: v for k, v in r.items() if k.startswith('mmlu_') and 'acc,none' in v and k not in ('mmlu_humanities', 'mmlu_stem', 'mmlu_social_sciences', 'mmlu_other')}
    assert len(subs) == 57, len(subs)
    N = sum(v['sample_len'] for v in subs.values())
    w = (100 * sum(v['acc,none'] * v['sample_len'] for v in subs.values()) / N, 100 * math.sqrt(sum((v['sample_len'] / N * v['acc_stderr,none']) ** 2 for v in subs.values())))
    m = (100 * sum(v['acc,none'] for v in subs.values()) / 57, 100 * math.sqrt(sum(v['acc_stderr,none'] ** 2 for v in subs.values())) / 57)
    return {'size-weighted acc': w, 'macro mean of 57 subject acc': m}
def bbh(r):
    subs = {k: v for k, v in r.items() if k.startswith('bbh_cot_fewshot_')}; assert len(subs) == 27, len(subs)
    vs = [(100 * v['exact_match,get-answer'], 100 * v['exact_match_stderr,get-answer']) for v in subs.values()]
    return {'chat exact_match mean over 27 subtasks': (sum(x[0] for x in vs) / 27, math.sqrt(sum(x[1] ** 2 for x in vs)) / 27)}
MC = {'arc_challenge': ('arc_challenge',), 'boolq': ('boolq',), 'hellaswag': ('hellaswag',), 'openbookqa': ('openbookqa',), 'piqa': ('piqa',), 'social_iqa': ('social_iqa',), 'winogrande': ('winogrande',)}
# Parser check (replies read in full), counts re-read from handcheck/*.json on 30 Oct 2026 (site pass). More than 1 of 10 replies off: that variant is CANNOT_TELL (parser) and does not count
# toward the outcome (same rule as score_s1.py). Off counts. S2 gsm8k_cot: plain strict 0, plain flexible 0, chat flexible 1 of 10, chat strict 5 of 10.
# S3 gsm8k: plain 0 and 0, chat flexible 1 of 10, chat strict 2 of 10. S3 bbh_cot_fewshot: 1 of 10.
PARSER = {'S2': {'gsm8k_cot': {'chat CoT strict-match'}}, 'S3': {'gsm8k_cot; gsm8k': {'chat CoT strict-match'}}}[R]
NOTE = {'S2': {'gsm8k_cot': "Parser check (replies read in full) (HANDCHECK_S2.md): plain variants read 10 of 10 replies as written. Chat flexible-extract read 9 of 10 as written (question 8 took '4' from 'those 4 hours', on a reply that is wrong either way). Chat strict-match found no answer on 5 of 10, 2 of them correct, so it is CANNOT_TELL (parser) and does not count toward the outcome."},
        'S3': {'gsm8k_cot; gsm8k': "Parser check (replies read in full) (HANDCHECK_S3.md): plain variants read 10 of 10 as written. Chat flexible-extract read 9 of 10 as written (question 5 took '16' from 'for 16 glasses', where the model answered 64). Chat strict-match found no answer on 2 of 10 (questions 5 and 8), 1 of them correct, so it is CANNOT_TELL (parser) and does not count toward the outcome.",
               'bbh_cot_fewshot': "Parser check (replies read in full) (HANDCHECK_S3.md): the filter missed 1 correct answer in 10, and 2 replies in 10 ended without an answer (one at our 512-token cap, one at the task's blank-line stop). The claim lists strict and flexible filters, but this task has one filter (get-answer), so that is the variant read."}}[R]
def variants(row):
    t = row['lm_eval_task']
    if t in MC:
        r = load(t); ms = [m.strip() for m in row['metric_variants'].split(';')]
        return {m: one(r, t, m + ',none') for m in ms} if r else None
    if t == 'mmlu': r = load('mmlu'); return mmlu(r) if r else None
    if t == 'bbh_cot_fewshot': r = load('bbh_cot_chat'); return bbh(r) if r else None
    if t in ('gsm8k_cot', 'gsm8k_cot; gsm8k'):
        o = {}
        for d, task, lab in ((('gsm8k_cot_plain', 'gsm8k_cot', 'plain CoT'), ('gsm8k_cot_chat', 'gsm8k_cot', 'chat CoT')) if R == 'S2' else (('gsm8k_plain', 'gsm8k', 'plain'), ('gsm8k_cot_chat', 'gsm8k_cot', 'chat CoT'))):
            r = load(d)
            if not r: return None
            for f in ('strict-match', 'flexible-extract'): o[f'{lab} {f}'] = one(r, task, 'exact_match,' + f)
        return o
    return None
rows = list(csv.DictReader(open(os.path.join(HERE, f'claims_{r_}.csv')))); out = {}
for row in rows:
    cid = row['claim_id']
    if row['status'] != 'RUN': continue
    v = variants(row)
    if not v or any(x is None for x in v.values()): out[cid] = {'state': 'not finished', 'ours': '', 'outcome': ''}; continue
    s = float(row['stated_value']); hit = False; lo_all = hi_all = True; txt = []; pf = PARSER.get(row['lm_eval_task'], ())
    for name, (val, se) in v.items():
        w = 1.96 * se + ROUND; txt.append(f'{name} {val:.1f} ± {w:.1f}' + (' [CANNOT_TELL (parser)]' if name in pf else ''))
        if name in pf: continue
        hit |= abs(s - val) <= w; lo_all &= s > val + w; hi_all &= s < val - w
    if hit: oc, note = 'CONSISTENT', ''
    else:
        d = 'above every variant\'s interval' if lo_all else ('below every variant\'s interval' if hi_all else 'outside every interval, on both sides')
        oc, note = 'CANNOT_TELL', f'. Under our harness the stated value is {d}. {HARNESS}, so this reads CANNOT_TELL until that difference is tested'
    pn = NOTE.get(row['lm_eval_task'], '')
    out[cid] = {'state': 'read', 'ours': ', '.join(txt) + note + (('. ' + pn) if pn else ''), 'outcome': oc}
json.dump(out, open(os.path.join(HERE, f'outcomes_{r_}.json'), 'w'), indent=1)
for k, x in out.items(): print(k, x['outcome'], x['ours'][:200])
