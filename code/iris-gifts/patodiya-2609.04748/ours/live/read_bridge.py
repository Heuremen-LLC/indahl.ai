#!/usr/bin/env python3
"""Readings L0-L6 of PLAN.md (5d3a336, Addendum 1 36655da) for the Metal bridge. Written before any live reply existed (31 Oct 2026).
  --sample FMT SES : 10 replies (seed 7) with the Table 7 scorer's answer and the run-time rule's answer, for the read in full. No rates.
  --rates          : L0-L6 for every session on disk. Refuses a session whose note runs/READ_<FMT>_s<SES>.md is missing.
Her CUDA logs are read as data; nothing of hers is run."""
import os, sys, json, gzip, glob, re, math, random
from decimal import Decimal
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); T = G + '/theirs'; RUNS = os.environ.get('BRIDGE_RUNS', H + '/runs')
HERS = {'Q8_0': ('bridge-qwen7b-q80', 89), 'Q4_K_M': ('bridge-lcpp-qwen7b-q4km', 83), 'Q3_K_M': ('bridge-qwen7b-q3km', 96)}  # printed k of 200
PATS = [re.compile(r"####\s*\$?(-?[\d,]+(?:\.\d+)?)"), re.compile(r"\\boxed\{\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\}"),
        re.compile(r"\\boxed\{\\text\{\s*\$?(-?[\d,]+(?:\.\d+)?)[^}]*\}\}"), re.compile(r"(?:final answer|answer)\s*(?:is|:)\s*\$?(-?[\d,]+(?:\.\d+)?)", re.I),
        re.compile(r"\\boxed\{\s*\\?\$\s*(-?[\d,]+(?:\.\d+)?)"), re.compile(r"\\boxed\{\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\\text"),
        re.compile(r"\*\*\s*\$?(-?[\d,]+(?:\.\d+)?)\s*\*\*\s*[\.\)]?\s*$", re.M)]
def extract(t):   # Table 7 scorer (scout/rebuild_bridge.py, rebuilds her printed counts)
    for p in PATS:
        m = p.findall(t)
        if m: return m[-1].replace(",", "").rstrip(".").strip()
    return None
def runtime(t):   # her run-time rule, harness/run_gsm8k.py
    m = re.findall(r"####\s*([\-\d,\.]+)", t); return m[-1].replace(",", "").rstrip(".") if m else None
def num(s):
    try: return Decimal(s.replace(",", "").rstrip(".").strip())
    except Exception: return None
rows = {}
for f in sorted(glob.glob(T + '/gsm8k_test_rows/rows_*.json')):
    for r in json.load(open(f))['rows']: rows[r['row_idx']] = r['row']
gold = {i: runtime(rows[i]['answer']) for i in range(200)}
def rec(r):
    c = r['response']['choices'][0]; u = r['response'].get('usage') or {}
    return {'text': c['text'], 'ids': [t['id'] for t in ((c.get('logprobs') or {}).get('content') or [])], 'finish': c.get('finish_reason'),
            'cached': ((u.get('prompt_tokens_details') or {}).get('cached_tokens')), 'prompt_tokens': u.get('prompt_tokens')}
def load(path, opener=open):
    D = {}
    with opener(path, 'rt') as fh:
        for l in fh:
            if l.strip():
                r = json.loads(l); D[(r['item_idx'], r['pass'])] = rec(r)   # a later record of the same item and pass supersedes
    return D
def ours(fmt, ses):
    p = '%s/%s_s%d.jsonl' % (RUNS, fmt, ses); return load(p) if os.path.exists(p) else None
def hers(fmt): return load('%s/repo_bc0551d/results/%s/cache_on/raw_requests.jsonl.gz' % (T, HERS[fmt][0]), gzip.open)
def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - h) / d, (c + h) / d
def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    return p1 - p2, p1 - p2 - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), p1 - p2 + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, j) for j in range(min(b, c) + 1)) / 2 ** n)
def ok(a, g): return a is not None and num(a) is not None and num(a) == num(g)
if sys.argv[1] == '--sample':
    fmt, ses = sys.argv[2], int(sys.argv[3]); D = ours(fmt, ses); ks = sorted(D); random.Random(7).shuffle(ks)
    for k in ks[:10]:
        d = D[k]; print('== item %d %s | Table 7 scorer %s | run-time rule %s | finish %s | tokens %d\n%s\n' % (k[0], k[1], extract(d['text']), runtime(d['text']), d['finish'], len(d['ids']), d['text'][-700:]))
    sys.exit()
for fmt in ('Q4_K_M', 'Q8_0', 'Q3_K_M'):
    S = {s: ours(fmt, s) for s in (1, 2)}; S = {s: d for s, d in S.items() if d is not None}
    if not S: continue
    for s in S:
        if not os.path.exists('%s/READ_%s_s%d.md' % (RUNS, fmt, s)): sys.exit('REFUSED: runs/READ_%s_s%d.md is missing (read 10 replies in full first)' % (fmt, s))
    Hd = hers(fmt); print('\n######## Qwen2.5-7B %s (her CUDA row: %d of 200 = %.1f%%)' % (fmt, HERS[fmt][1], HERS[fmt][1] / 2))
    for s, D in sorted(S.items()):
        items = sorted({i for i, _ in D}); n = len(items); full = [i for i in items if all((i, p) in D for p in ('cold', 'cold2', 'warm', 'warm2'))]
        print('  session %d: items %d (all four passes %d)' % (s, n, len(full)))
        bad_c = sum(1 for i in full for p in ('cold', 'cold2') if D[(i, p)]['cached'] != 0)
        bad_w = sum(1 for i in full for p in ('warm', 'warm2') if D[(i, p)]['cached'] is None or D[(i, p)]['prompt_tokens'] is None or D[(i, p)]['cached'] < D[(i, p)]['prompt_tokens'] - 1)
        fin = {}
        for i in full:
            for p in ('cold', 'cold2', 'warm', 'warm2'): fin[D[(i, p)]['finish']] = fin.get(D[(i, p)]['finish'], 0) + 1
        print('    L0 telemetry: cold passes with cached_tokens not 0: %d of %d | warm passes with cached_tokens below prompt minus 1: %d of %d | finish reasons %s' % (bad_c, 2 * len(full), bad_w, 2 * len(full), fin))
        dc = [i for i in full if D[(i, 'cold')]['ids'] == D[(i, 'cold2')]['ids']]; dw = [i for i in full if D[(i, 'warm')]['ids'] == D[(i, 'warm2')]['ids']]
        print('    L1 path determinism (token ids): recompute %d of %d | cache hit %d of %d' % (len(dc), len(full), len(dw), len(full)))
        det = [i for i in full if i in set(dc) and i in set(dw)]
        kt = sum(1 for i in det if D[(i, 'cold')]['text'] != D[(i, 'warm')]['text']); ki = sum(1 for i in det if D[(i, 'cold')]['ids'] != D[(i, 'warm')]['ids'])
        lo, hi = wilson(kt, len(det)); d, dl, dh = newcombe(kt, len(det), HERS[fmt][1], 200)
        print('    L2 path divergence (text): %d of %d = %.1f%% [%.1f, %.1f] | token ids %d | ours minus hers %+.1f pp [%+.1f, %+.1f] (Newcombe 95%%)' % (kt, len(det), 100 * kt / max(1, len(det)), 100 * lo, 100 * hi, ki, 100 * d, 100 * dl, 100 * dh))
        Hc = sum(1 for i in full if (i, 'cold') in Hd and Hd[(i, 'cold')]['ids'] == D[(i, 'cold')]['ids']); Hw = sum(1 for i in full if (i, 'warm') in Hd and Hd[(i, 'warm')]['ids'] == D[(i, 'warm')]['ids'])
        print('    L4 Metal against her CUDA, identical token ids: cold %d of %d | warm %d of %d' % (Hc, len(full), Hw, len(full)))
        cc = {i: ok(extract(D[(i, 'cold')]['text']), gold[i]) for i in full}; wc = {i: ok(extract(D[(i, 'warm')]['text']), gold[i]) for i in full}
        b = sum(1 for i in det if wc[i] and not cc[i]); c = sum(1 for i in det if cc[i] and not wc[i])
        rc = sum(ok(runtime(D[(i, 'cold')]['text']), gold[i]) for i in full); rw = sum(ok(runtime(D[(i, 'warm')]['text']), gold[i]) for i in full)
        print('    L5 correct (Table 7 scorer): recompute %d, cache hit %d of %d | flips: %d favour cache hit, %d favour recompute | exact McNemar p %.3f | run-time rule: %d, %d' % (sum(cc.values()), sum(wc.values()), len(full), b, c, mcnemar(b, c), rc, rw))
        dv = [i for i in det if D[(i, 'cold')]['text'] != D[(i, 'warm')]['text']]
        same_ans = sum(1 for i in dv if extract(D[(i, 'cold')]['text']) == extract(D[(i, 'warm')]['text']))
        pos = sorted(next((j for j, (x, y) in enumerate(zip(D[(i, 'cold')]['ids'], D[(i, 'warm')]['ids'])) if x != y), min(len(D[(i, 'cold')]['ids']), len(D[(i, 'warm')]['ids']))) for i in dv)
        q = lambda f: pos[min(len(pos) - 1, int(f * len(pos)))] if pos else float('nan')
        print('    L6 divergent items with the same extracted answer: %d of %d | first differing token position: quartiles %s, %s, %s' % (same_ans, len(dv), q(.25), q(.5), q(.75)))
    if len(S) == 2:
        D1, D2 = S[1], S[2]; both = [i for i in range(200) if all((i, p) in D1 and (i, p) in D2 for p in ('cold', 'warm'))]
        fc = sum(1 for i in both if D1[(i, 'cold')]['ids'] != D2[(i, 'cold')]['ids']); fw = sum(1 for i in both if D1[(i, 'warm')]['ids'] != D2[(i, 'warm')]['ids'])
        print('  L3 session floor: items whose token ids differ between sessions: recompute %d of %d | cache hit %d of %d' % (fc, len(both), fw, len(both)))
