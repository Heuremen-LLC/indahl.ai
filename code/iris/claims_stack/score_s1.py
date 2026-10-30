"""score_s1.py knowngood | read: reads the lm-evaluation-harness outputs of round S1 (ROUND_S1.md) and applies the pre-registered outcome rule. Writes outcomes_s1.json."""
import json, glob, os, math, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__))
def load(d):
    fs = [f for f in glob.glob(os.path.join(HERE, d, '*')) if os.path.isfile(f) and os.path.basename(f).startswith('eval_')]
    return json.load(open(fs[0])) if fs else None
def get(r, task, metric):
    t = r.get(task) if r else None
    if not t: return None
    for k in (metric + ',none', metric):
        if k in t:
            se = t.get(k.replace(metric, metric + '_stderr'), t.get(metric + '_stderr,none', 0)); return 100 * t[k], 100 * (se if isinstance(se, (int, float)) else 0)
def mean2(a, b):
    if not a or not b: return None
    return (a[0] + b[0]) / 2, math.hypot(a[1], b[1]) / 2
if sys.argv[1] == 'knowngood':
    rec = {'arc': (22.01, 'arc_challenge', 'acc_norm', 'kg/arc'), 'hs': (31.53, 'hellaswag', 'acc_norm', 'kg/hs')}; ok = True; parts = []
    for k, (ref, task, m, d) in rec.items():
        r = load(d); v = get(r, task, m)
        if not v: print('known-good not finished'); sys.exit()
        z = abs(v[0] - ref) / v[1]; ok &= z <= 2; parts.append(f'{task} {m} {v[0]:.2f} against the record {ref:.2f} ({z:.1f} standard errors)')
    print(('passed. ' if ok else 'FAILED. ') + '; '.join(parts)); sys.exit()
if sys.argv[1] == 'genknowngood':
    f = glob.glob(os.path.join(HERE, 'kg/gsm8k/eval_*'))
    if not f: print('not finished'); sys.exit()
    t_ = json.load(open(f[0]))['gsm8k']; ref, se_r = 33.59, 1.30; best = None; parts = []
    for m in ('strict-match', 'flexible-extract'):
        v, se = 100 * t_['exact_match,' + m], 100 * t_['exact_match_stderr,' + m]; lim = 2 * math.hypot(se, se_r); parts.append(f'{m} {v:.1f} (limit {lim:.1f})')
        if abs(v - ref) <= lim: best = True
    print(('passed. ' if best else 'FAILED. ') + 'Qwen1.5-1.8B GSM8K 5-shot against the record 33.59: ' + '; '.join(parts)); sys.exit()
rows = {r['claim_id']: r for r in csv.DictReader(open(os.path.join(HERE, 'claims_s1.csv')))}
R = {t: load(f's1/{t}') for t in ('hellaswag', 'arc_easy', 'arc_challenge', 'piqa')}
GV = {d: load(f's1/{d}') for d in ('gsm8k_plain', 'gsm8k_chat', 'gsm8k_chatmt', 'ifeval_chat', 'bbh_plain', 'bbh_chat')}
def variants(cid):
    if cid == 'S1-01':
        r = GV['ifeval_chat']; g = lambda m: get(r, 'ifeval', m)
        return {'chat strict mean of prompt and inst': mean2(g('prompt_level_strict_acc'), g('inst_level_strict_acc')), 'chat loose mean of prompt and inst': mean2(g('prompt_level_loose_acc'), g('inst_level_loose_acc'))} if r else None
    if cid == 'S1-04': r = R['hellaswag']; return {m: get(r, 'hellaswag', m) for m in ('acc', 'acc_norm')} if r else None
    if cid == 'S1-05':
        a, b = R['arc_easy'], R['arc_challenge']; return {m: mean2(get(a, 'arc_easy', m), get(b, 'arc_challenge', m)) for m in ('acc', 'acc_norm')} if a and b else None
    if cid == 'S1-06': r = R['piqa']; return {m: get(r, 'piqa', m) for m in ('acc', 'acc_norm')} if r else None
    if cid == 'S1-08':
        o = {}
        for d, lab in (('bbh_plain', 'plain'), ('bbh_chat', 'chat')):
            r = GV[d]
            if not r: continue
            subs = [x for x in r if x.startswith('bbh_fewshot_')]; vs = [get(r, x, 'exact_match') for x in subs]; vs = [x for x in vs if x]
            if vs: o[lab + ' exact_match mean over subtasks'] = (sum(x[0] for x in vs) / len(vs), math.sqrt(sum(x[1] ** 2 for x in vs)) / len(vs))
        return o or None
    if cid == 'S1-09':
        o = {}
        for d, lab in (('gsm8k_plain', 'plain'), ('gsm8k_chat', 'chat'), ('gsm8k_chatmt', 'chat with turns')):
            r = GV[d]
            if not r: continue
            t_ = r['gsm8k']
            for m in ('strict-match', 'flexible-extract'): o[f'{lab} {m}'] = (100 * t_['exact_match,' + m], 100 * t_['exact_match_stderr,' + m])
        return o or None
out = {}
for cid, row in rows.items():
    if row['status'] != 'RUN': continue
    if row['lm_eval_task'] in ('gsm8k', 'bbh_fewshot', 'ifeval') and not os.path.exists(os.path.join(HERE, 'gen_ok')):   # addendum 1: no generation result is read until a generation known-good passes
        out[cid] = {'state': 'held: generation check pending', 'ours': '', 'outcome': ''}; continue
    v = variants(cid)
    if cid == 'S1-01' and not v: out[cid] = {'state': 'nothing returned: the evaluation tool stops with an error after generating (ROUND_S1.md addendum 5)', 'ours': '', 'outcome': ''}; continue
    if not v or any(x is None for x in v.values()): out[cid] = {'state': 'running' if os.path.isdir(os.path.join(HERE, 's1')) else 'queued', 'ours': '', 'outcome': ''}; continue
    s = float(row['stated_value']); hit = []; lo_all = True; hi_all = True; txt = []
    for name, (val, se) in v.items():
        w = 1.96 * se + 0.05; txt.append(f'{name} {val:.1f} ± {w:.1f}')
        if abs(s - val) <= w: hit.append(name)
        lo_all &= s > val + w; hi_all &= s < val - w
    oc = 'CONSISTENT' if hit else ('BELOW' if lo_all else ('ABOVE' if hi_all else 'CANNOT_TELL'))
    harness_note = ''
    if oc in ('ABOVE', 'BELOW') and 'lighteval' in row['stated_setting']:   # Addendum 6: the card ran lighteval, we ran lm-eval; the prompt rebuttal is untested
        harness_note = f'. Under our harness the stated value is {"above" if oc == "BELOW" else "below"} our interval. The card ran lighteval, so this reads CANNOT_TELL until that is tested'
    marg = min(abs(s - (val - (1.96 * se + 0.05))) if hi_all else abs(s - (val + (1.96 * se + 0.05))) for val, se in v.values()) if oc in ('ABOVE', 'BELOW') else None
    out[cid] = {'state': 'read', 'ours': '; '.join(txt) + (f'. Margin outside the interval: {marg:.3f} points' if marg is not None else '') + harness_note, 'outcome': 'CANNOT_TELL' if harness_note else oc}
json.dump(out, open(os.path.join(HERE, 'outcomes_s1.json'), 'w'), indent=1)
