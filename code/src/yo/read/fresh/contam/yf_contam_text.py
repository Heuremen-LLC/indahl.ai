"""yf_contam_text.py -- /tp 5 Nov: the shown-sentence check (yf_contam.py) missed 5 of the 8 known same-work fresh papers whose twin was trained on.
This compares FULL TEXTS: for each fresh paper, the share of its 8-word shingles found in ONE trained paper's text (max over the trained papers,
TRAIN and VALID splits of the 688, the papers whose sentences the adapters saw). Inputs only; no model output read.
Known-good, required before any fresh reading: all 8 known same-work papers with a TRAINED twin must top-match their own twin.
Floor: the same score for the 6 known same-work papers whose twin was in TEST (never trained) against the trained papers, and the score
distribution for the 148 TEST papers against the trained papers (same corpus as training, so a high-side floor)."""
import json, os, re, sys, hashlib, builtins, collections
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); Q = os.path.expanduser('~/bones-forge/qia_leads/')
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))   # yd, USED, PAIRS
_open = builtins.open
def _op(p, *a, **k): return _open(Q + 'matrix_page/list.json.pre-removal-20261102' if p == Q + 'matrix_page/list.json' else p, *a, **k)
builtins.open = _op; P688 = {k: p for k, _, p in yd.papers()}; builtins.open = _open
TRAINED = {k: p for k, p in P688.items() if yd.split(k) in ('TRAIN', 'VALID')}; TEST = {k: p for k, p in P688.items() if yd.split(k) == 'TEST'}
def shingles(path, n=8):
    w = re.findall(r'[a-z0-9]+', open(path, errors='replace').read().lower())
    return {hashlib.blake2b(' '.join(w[i:i + n]).encode(), digest_size=8).digest() for i in range(max(0, len(w) - n + 1))}
print(f'688 papers: {len(TRAINED)} trained (TRAIN+VALID), {len(TEST)} TEST')
TS = {k: shingles(p) for k, p in TRAINED.items()}
inv = collections.defaultdict(list)
for k, s in TS.items():
    for h in s: inv[h].append(k)
def best(s):
    c = collections.Counter()
    for h in s:
        for k in inv.get(h, ()): c[k] += 1
    if not c or not s: return (0.0, None, 0.0)
    (k1, n1), *rest = c.most_common(2) + [(None, 0)]
    return (n1 / len(s), k1, (rest[0][1] / len(s)) if rest else 0.0)
fresh = [json.loads(l) for l in open(H + '/data/test_items_fresh.jsonl')]
ftext = {}
for r in fresh:
    for base in (Q, Q + 'sweep_20261101/', Q + 'backfill_20261101/'):
        if os.path.exists(base + r['text_file']): ftext[r['paper']] = base + r['text_file']; break
print(f'fresh papers: {len({r["paper"] for r in fresh})}, with a text file found: {len(ftext)}')
L = json.load(open(Q + 'matrix_page/list.json')); lr = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
by = {yd.norm(r['link']): r for r in lr}
known = {}
for k in ftext:
    v = str(by.get(k, {}).get('version', '')); m = re.search(r'(10\.\d{4,9}/[^\s)]+)', v) if 'open copy read' in v else None
    if m and 'doi:' + m.group(1).lower().rstrip('/.') in USED: known[k] = 'doi:' + m.group(1).lower().rstrip('/.')
    elif k in PAIRS: known[k] = PAIRS[k]
score = {k: best(shingles(p)) for k, p in ftext.items()}
print('\n== KNOWN-GOOD: known same-work fresh papers (twin, twin split, best-matching trained paper, share, runner-up share)')
kg_ok = 0; kg_n = 0
for k, tw in sorted(known.items(), key=lambda x: yd.split(x[1])):
    s, top, ru = score[k]; trained_twin = tw in TRAINED
    ok = (top == tw) if trained_twin else None
    if trained_twin: kg_n += 1; kg_ok += bool(ok)
    print(f'  {k} <- {tw} [{yd.split(tw)}]: top {top} share {s:.3f} runner-up {ru:.3f}' + ('' if ok is None else ('  TOP = TWIN' if ok else '  MISSED')))
print(f'known-good: {kg_ok} of {kg_n} trained twins found as the top match')
fl = sorted(best(shingles(p))[0] for p in TEST.values())
q = lambda a, f: a[min(len(a) - 1, int(f * len(a)))]
print(f'\n== FLOOR: 148 TEST papers vs trained papers: median {q(fl,.5):.3f}, 90th {q(fl,.9):.3f}, 99th {q(fl,.99):.3f}, max {fl[-1]:.3f}')
prim = set(open(H + '/primary_ids.txt').read().split()); sens = set(open(H + '/sensitivity_ids.txt').read().split())
for name, ids in (('primary', prim), ('sensitivity', sens), ('full', set(ftext))):
    rows = sorted(((score[k][0], k, score[k][1]) for k in ids if k in score), reverse=True)
    miss = len([k for k in ids if k not in score])
    print(f'\n== FRESH {name}: {len(rows)} papers (no text file: {miss}); share > floor max ({fl[-1]:.3f}): {sum(1 for r in rows if r[0] > fl[-1])}; '
          f'> floor 99th: {sum(1 for r in rows if r[0] > q(fl,.99))}')
    for s, k, top in rows[:8]: print(f'   {k}: share {s:.3f} with {top}' + ('  [known same work]' if k in known else ''))
