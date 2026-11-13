"""publish_results.py: scores every finished round (all ten models, all arms complete) with that round's own score.py and publishes rates with Wilson widths to the IRIS page (KV key results).
Shown per model and family: share of readable replies that commit the Fault, bare and with the Guard wording. CANNOT_TELL where the round's gates failed. No ranking."""
import os, sys, json, subprocess, importlib
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(B, '..', 'heuremen_kit')); import heuremen_kit as K   # 12 Nov 2026: Faults and Guards 2.0 read(), see PLAN_ADDENDUM_std2.md
SIZE = 0.10   # size that matters and band edge, addendum 12 Nov 2026
def std2(o, eff):
    # o: the round's own outcome string from score.py, eff: its (difference, lo, hi) guard effect. Returns (outcome, reason, why_text).
    if o and str(o).startswith('CANNOT_TELL'):
        txt = str(o)[13:-1] if '(' in str(o) else ''
        return ('CANNOT_TELL', K.TOO_WIDE_TO_RESOLVE if txt == 'too few read' else K.NO_INTERVAL_FORMABLE, txt)
    if not eff: return ('CANNOT_TELL', K.NO_INTERVAL_FORMABLE, 'no interval')
    r = K.read(eff[1], eff[2], band=(-SIZE, SIZE), matters=SIZE, null=0.0, direction='both'); return (r[0], r[1], '')
ORDER = ['phi4-mini', 'mistral:7b', 'falcon3:3b', 'smollm2:1.7b', 'llama3.1:8b', 'gemma3:4b', 'olmo2:7b', 'granite3.3:2b', 'qwen3:4b', 'deepseek-r1:1.5b']
DIRS = [(1, 'faultsbench2')] + [(n, f'faultsbench_r{n}') for n in range(2, 12)]
def complete(d, n):
    for m in ORDER:
        for arm in ('bare', 'bare_copy', 'guard'):
            p = os.path.join(B, d, 'out', m.replace(':', '_'), arm + '.jsonl')
            if not os.path.exists(p) or sum(1 for _ in open(p)) < n: return False
    return True
rounds = []; READS = []
for rn, d in DIRS:
    dp = os.path.join(B, d)
    if not os.path.isdir(dp): continue
    n = len(json.load(open(os.path.join(dp, 'items.json'))))
    if not complete(d, n): continue
    sys.path.insert(0, dp); sys.modules.pop('score', None); sys.modules.pop('items', None)
    S = importlib.import_module('score'); sys.path.pop(0)
    models = []
    for m in ORDER:
        mk = m.replace(':', '_'); r = S.score(mk)
        G, Bm, DG, DB = S.load(mk, 'guard'), S.load(mk, 'bare'), S.load_dr(mk, 'guard'), S.load_dr(mk, 'bare')
        fam = {}
        for f in ('P1', 'P2', 'P3', 'P4'):
            o = r['fam'][f]['outcome']
            ks = [k for k, i in S.IT.items() if i['fam'] == f and i.get('kind') not in ('control', 'gw')]
            b = [x for x in (S.cls(S.IT[k], Bm.get(k), 'bare', DB.get(k)) for k in ks if k in Bm) if x in ('FAULT', 'OK')]
            g = [x for x in (S.cls(S.IT[k], G.get(k), 'guard', DG.get(k)) for k in ks if k in G) if x in ('FAULT', 'OK')]
            ct = str(o).startswith('CANNOT_TELL')
            def rate(v):
                if not v: return None
                w = S.wilson(sum(x == 'FAULT' for x in v), len(v)); return [round(100 * w[0]), round(100 * w[1]), round(100 * w[2]), len(v)]
            eff = r['fam'][f].get('guard_effect'); so, sr, wt = std2(o, eff); READS.append((so, sr))
            fam[f] = dict(ct=ct, why=(sr if ct else ''), why_text=wt, out=None if ct else so, reason=sr, out_pre_std2=None if ct else o, effect=eff, n_pairs=r['fam'][f].get('n_pairs'),
                          bare=None if ct else rate(b), guard=None if ct else rate(g))
        models.append(dict(name=m, gate=r['model_gate'], fam=fam))
    rounds.append(dict(round=rn, models=models))
d = dict(rounds=rounds, req13=K.req13(READS, nothing_returned=0))   # every cell read is a reading of the guard effect. No failed reads in this publisher.
f = os.path.join(B, 'results_status.json'); json.dump(d, open(f, 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894')
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'results', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                   cwd=os.path.join(B, '..', 'cloudflare-workers', 'heuremen-door'), env=env, capture_output=True, text=True)
print('rounds published:', [x['round'] for x in rounds], 'ok' if r.returncode == 0 else 'FAILED')
