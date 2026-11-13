"""select_finalists.py: applies THUNDERDOME_PLAN.md to the scored rounds. Run once, after round 11. Prints the pool, each score and the two finalists."""
import os, sys, json, importlib.util, collections
B = os.path.dirname(os.path.abspath(__file__)); DIRS = ['faultsbench2'] + [f'faultsbench_r{n}' for n in range(2, 12)]
ORDER = ['phi4-mini', 'mistral:7b', 'falcon3:3b', 'smollm2:1.7b', 'llama3.1:8b', 'gemma3:4b', 'olmo2:7b', 'granite3.3:2b', 'qwen3:4b', 'deepseek-r1:1.5b']
def load(d):
    sys.path.insert(0, os.path.join(B, d)); sys.modules.pop('items', None); sys.modules.pop('score', None)
    import score; importlib.reload(score); sys.path.pop(0); return score
gates = collections.defaultdict(int); rnds = collections.defaultdict(list); bare = collections.defaultdict(list)
for d in DIRS:
    S = load(d)
    for m in ORDER:
        mk = m.replace(':', '_')
        if not os.path.exists(os.path.join(B, d, 'out', mk, 'guard.jsonl')): continue
        r = S.score(mk)
        if r['model_gate'] != 'pass': continue
        G, Bm, DG, DB = S.load(mk, 'guard'), S.load(mk, 'bare'), S.load_dr(mk, 'guard'), S.load_dr(mk, 'bare')
        fg, fb = [], []
        for fam in ('P1', 'P2', 'P3', 'P4'):
            # 30 Oct 2026 correction: THUNDERDOME_PLAN.md says families whose gate failed are excluded. Until 30 Oct this line skipped only "CANNOT_TELL (family" and "CANNOT_TELL (repeat",
            # so a family with "CANNOT_TELL (too few read)" (under 10 readable pairs) stayed in. Every CANNOT_TELL outcome is excluded now. See the 30 Oct addendum in THUNDERDOME_PLAN.md.
            if r['fam'][fam]['outcome'] is None or str(r['fam'][fam]['outcome']).startswith('CANNOT_TELL'): continue
            ks = [k for k, i in S.IT.items() if i['fam'] == fam and i.get('kind') not in ('control', 'gw')]
            g = [S.cls(S.IT[k], G.get(k), 'guard', DG.get(k)) for k in ks if k in G]; b = [S.cls(S.IT[k], Bm.get(k), 'bare', DB.get(k)) for k in ks if k in Bm]
            g = [x for x in g if x in ('FAULT', 'OK')]; b = [x for x in b if x in ('FAULT', 'OK')]
            if g and b: fg.append(sum(x == 'FAULT' for x in g) / len(g)); fb.append(sum(x == 'FAULT' for x in b) / len(b))
        gates[m] += 1
        if fg: rnds[m].append(sum(fg) / len(fg)); bare[m].append(sum(fb) / len(fb))
pool = {m: (sum(rnds[m]) / len(rnds[m]), sum(bare[m]) / len(bare[m]), gates[m]) for m in ORDER if gates[m] >= 9 and rnds[m]}
rank = sorted(pool.items(), key=lambda kv: kv[1][0])
if len(rank) >= 2 and abs(rank[1][1][0] - rank[2][1][0]) <= 0.005 if len(rank) > 2 else False:
    rank = sorted(pool.items(), key=lambda kv: (round(kv[1][0] / 0.005), -kv[1][2], kv[1][1]))
for m, (g, b, n) in rank: print(f'{m}\tguard-arm fault {g:.3f}\tbare {b:.3f}\tgate passes {n}/11')
print('FINALISTS:', [m for m, _ in rank[:2]] if len(rank) >= 2 else 'none (fewer than two qualify)')
