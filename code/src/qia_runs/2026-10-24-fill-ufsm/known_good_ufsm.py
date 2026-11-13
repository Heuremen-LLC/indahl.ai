"""known_good_ufsm.py NBDIR -- their saved Fig 8 notebook OUTPUT text (counts printed by their cells; no code of theirs executed) through
OUR deficit(): pooled 5 jobs x 8192 shots. Must give deficit (a) 1.24 pp and (b) 4.67 pp (to 0.01 pp), extra 3.43 pp."""
import sys, json, re, ast, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ufsm
nb = json.load(open(os.path.join(sys.argv[1], '02-EXPS_FIGURE_08.ipynb'))); groups = []
for c in nb['cells']:
    if c['cell_type'] != 'code': continue
    for o in c.get('outputs', []):
        t = ''.join(o.get('text', [])) if 'text' in o else ''
        m = re.search(r'complete exp\. counts: (\{.*?\})', t, re.S)
        if m: groups.append(ast.literal_eval(m.group(1)))
A, B = groups[0:5], groups[5:10]
pa = {}; pb = {}
for g in A:
    for k, v in g.items(): pa[k] = pa.get(k, 0) + v
for g in B:
    for k, v in g.items(): pb[k] = pb.get(k, 0) + v
da, _ = ufsm.deficit(pa, 'a'); db, _ = ufsm.deficit(pb, 'b')
print(f'KNOWN-GOOD their Fig 8 counts: deficit (a) {100*da:.3f} pp, (b) {100*db:.3f} pp, extra {100*(db-da):.3f} pp; jobs {len(A)}+{len(B)}, shots {sum(pa.values())}+{sum(pb.values())}')
ok = abs(100 * da - 1.24) < 0.01 and abs(100 * db - 4.67) < 0.01; print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
