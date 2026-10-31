"""read_live.py (31 Oct 2026, PLAN.md L1 to L4 with addendum 1). Reads our runs and their released files as data; never runs their code.
Usage: python3 -I read_live.py L1 | L2 | L3 | L4 [--source NAME] | L4dump NAME   (L4dump prints the replies on dd_e01..dd_e12 for reading)"""
import json, re, sys, os, glob, math
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); TH = G + '/theirs/hf_at_b112204c'
sys.path.insert(0, H); import score
TB = {t['task_id']: t for t in json.load(open(TH + '/task_bank.json'))['tasks'][:30]}
EASY = [f'dd_e{i:02d}' for i in range(1, 13)]
def ours(model, ses):
    p = f'{H}/runs/{model}_s{ses}.jsonl'
    return {json.loads(l)['task_id']: json.loads(l) for l in open(p)} if os.path.exists(p) else {}
def theirs(folder, suffix):
    out = {}
    for f in glob.glob(f'{TH}/{folder}/dd_*_{suffix}.json'):
        d = json.load(open(f)); s = d['trajectory'][0]
        out[d['task_id']] = dict(raw=s['raw_response'], final=d['outcome']['final_claim'], err=s.get('error', {}).get('occurred'))
    return out
SOURCES = {'ours_qwen15': lambda: {k: v['text'] for k, v in ours('qwen15', 1).items()},
           'ours_phi35': lambda: {k: v['text'] for k, v in ours('phi35', 1).items()},
           'theirs_qwen15': lambda: {k: v['raw'] for k, v in theirs('trajectories_opensource', 'qwen2.5').items()},
           'theirs_qwen7': lambda: {k: v['raw'] for k, v in theirs('trajectories_qwen2.5-7b', 'qwen2.5-7b').items()},
           'theirs_mistral7': lambda: {k: v['raw'] for k, v in theirs('trajectories_mistral-7b-v0.3', 'mistral-7b-v0.3').items()},
           'theirs_phi35': lambda: {k: v['raw'] for k, v in theirs('trajectories_phi-3.5-mini', 'phi-3.5-mini').items()}}
def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)
def mcnemar_exact(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
STRIP_MARK = re.compile(r'(?m)^\s*(?:[-*]\s*)?\(?\d+[.)](?=\s)|\b[Ss]tep\s+\d+\b')
MIXED = re.compile(r'\S*[A-Za-z]\S*\d\S*|\S*\d\S*[A-Za-z]\S*')
def found_B(kind, val, reply):
    if kind == 'ident': return val in reply
    if kind in ('yesno', 'text'): return score.found(kind, val, reply)
    clean = MIXED.sub(' ', STRIP_MARK.sub(' ', reply))
    return score.found(kind, val, clean)
def score_B(gt, reply):
    res = [found_B(*score.classify(p), reply) for p in score.split_parts(gt)]
    sc = [f for f in res if f is not None]
    return (all(sc) if sc else None), sum(sc), len(sc), len(res) - len(sc)
cmd = sys.argv[1]
if cmd == 'L1':
    T = {k: v['raw'] for k, v in theirs('trajectories_opensource', 'qwen2.5').items()}
    for ses in (1, 2):
        O = ours('qwen15', ses); eq = 0; rows = []
        for t in TB:
            a, b = O[t]['text'][:3000], T[t]
            if a == b: eq += 1; continue
            i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
            rows.append(f'  {t} first differing character {i} of ours {len(a)} / theirs {len(b)}')
        print(f'L1 Qwen-1.5B session {ses} against their stored raw_response: text equal on {eq} of {len(TB)}'); print('\n'.join(rows))
elif cmd == 'L2':
    for m in ('qwen15', 'phi35'):
        a, b = ours(m, 1), ours(m, 2)
        if not a or not b: print(f'L2 {m}: sessions missing ({len(a)}, {len(b)})'); continue
        diff = [t for t in TB if a[t]['ids'] != b[t]['ids']]
        print(f'L2 {m}: generated token ids differ between sessions on {len(diff)} of {len(TB)} {diff}')
elif cmd == 'L3':
    for m in ('phi35',):
        for ses in (1, 2):
            O = ours(m, ses)
            if not O: print(f'L3 {m} s{ses}: not run yet'); continue
            err = [t for t in TB if (not O[t]['text'].strip()) or O[t]['text'].startswith('Error:')]
            n = sorted(O[t]['n_new'] for t in TB); cap = [t for t in TB if O[t]['hit_cap']]
            print(f'L3 {m} s{ses}: model text on {len(TB) - len(err)} of {len(TB)} (empty or error {err}), new tokens min {n[0]} median {n[len(n)//2]} max {n[-1]}, hit the 512 cap on {len(cap)} {cap}')
    T = theirs('trajectories_phi-3.5-mini', 'phi-3.5-mini')
    print(f'L3 their Phi-3.5-mini files: error string on {sum(1 for v in T.values() if v["raw"].startswith("Error"))} of {len(T)}')
elif cmd == 'L4dump':
    S = SOURCES[sys.argv[2]]()
    for t in (sys.argv[3].split(',') if len(sys.argv) > 3 else EASY):
        print(f'===== {t} | ground truth: {TB[t].get("ground_truth")}\n{S.get(t, "(missing)")}\n')
elif cmd == 'L4':
    # addendum 3: parts where L5 found DIFFERS under every convention printed (L5.text), set aside only with --set-aside (defined after the data)
    SET_ASIDE = {('dd_e03', 'LogP=-1.43'), ('dd_e03', 'HBD=2'), ('dd_e03', 'HBA=4'), ('dd_e05', 'Tanimoto 0.55-0.65'), ('dd_e10', '4 aromatic rings'), ('dd_e12', 'QED 0.3-0.4')}   # dd_e03 LogP added 31 Oct after the referee (addendum 3's rule applied as written)
    if '--set-aside' in sys.argv: print('Ruler A with the L5 DIFFERS parts set aside (defined after the data):', sorted(SET_ASIDE))
    srcs = [s for s in SOURCES if s != 'theirs_phi35']
    A = {}
    ap = H + '/L4_READ.tsv'
    if os.path.exists(ap):
        for l in open(ap):
            if l.startswith('#') or not l.strip(): continue
            src, t, part, verdict, stated = (l.rstrip('\n').split('\t') + [''])[:5]
            if (t, part) in SET_ASIDE and '--set-aside' in sys.argv: verdict = 'unscored'
            A.setdefault((src, t), []).append(verdict)
    per = {}
    for s in srcs:
        S = SOURCES[s]()
        if not S: print(f'{s}: no replies yet'); continue
        rows = {}
        for t in EASY:
            gt = TB[t]['ground_truth']; c = score.score(gt, S[t]); b = score_B(gt, S[t])
            av = A.get((s, t)); a = None if not av else (None if not [v for v in av if v != 'unscored'] else all(v == 'found' for v in av if v != 'unscored'))
            rows[t] = dict(committed=c[0], B=b[0], A=a, A_parts=(sum(v == 'found' for v in av or []), sum(v != 'unscored' for v in av or [])))
        per[s] = rows
        for r in ('A', 'B', 'committed'):
            sc = [t for t in EASY if rows[t][r] is not None]; k = sum(rows[t][r] for t in sc); lo, hi = wilson(k, len(sc))
            dis = [t for t in EASY if r != 'A' and rows[t]['A'] is not None and rows[t][r] != rows[t]['A']]
            print(f'{s:16s} ruler {r:9s} items correct {k} of {len(sc)} ({lo:.2f}, {hi:.2f})' + ('' if r == 'A' else f' | disagrees with A on {len(dis)} {dis}')
                  + (' [CANNOT_TELL (parser): failed its check against the full read, addendum 1]' if r == 'committed' else ' [CANNOT_TELL (parser): failed its check against the full read, addendum 2]' if r == 'B' else ''))
        print(f'{s:16s} ruler A   parts marked cut {sum(v == "cut" for t in EASY for v in A.get((s, t), []))}, no value given {sum(v == "no value given" for t in EASY for v in A.get((s, t), []))}')
        pf = sum(rows[t]['A_parts'][0] for t in EASY); pn = sum(rows[t]['A_parts'][1] for t in EASY)
        if pn: lo, hi = wilson(pf, pn); print(f'{s:16s} ruler A   parts found {pf} of {pn} ({lo:.2f}, {hi:.2f})')
    print('\nPaired exact McNemar on ruler A (items scored by A in both sources):')
    ks = list(per)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            both = [t for t in EASY if per[ks[i]][t]['A'] is not None and per[ks[j]][t]['A'] is not None]
            b = sum(1 for t in both if per[ks[i]][t]['A'] and not per[ks[j]][t]['A']); c = sum(1 for t in both if per[ks[j]][t]['A'] and not per[ks[i]][t]['A'])
            print(f'  {ks[i]} vs {ks[j]}: n {len(both)}, only first correct {b}, only second correct {c}, p {mcnemar_exact(b, c):.3f}')
