#!/usr/bin/env python3
"""Known-good for Lail, arXiv 2609.06444 (PLAN 3b3c6f5). Our code; their cache and the ChaosNLI mirror read as data."""
import json, os, re, collections
import numpy as np
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); T = G + '/theirs'
CL = ('e', 'n', 'c')
def load_items():
    uids, counts, old = [], [], []
    for name in ('snli', 'mnli_m'):
        for l in open('%s/chaosnli_mirror/raw/chaosNLI_%s.jsonl' % (T, name)):
            r = json.loads(l); uids.append(r['uid']); counts.append([r['label_counter'].get(c, 0) for c in CL]); old.append(r.get('old_labels'))
    return uids, np.array(counts), old
def judge(uids):
    by, conf, rows = collections.defaultdict(list), collections.defaultdict(list), []
    for l in open(T + '/repo/chaosnli/caches/judge_cache.jsonl'):
        r = json.loads(l); rows.append(r)
        if r.get('dist') is not None: by[r['uid']].append(r['dist'])
        if r.get('confidence') is not None: conf[r['uid']].append(float(r['confidence']))
    q = np.array([np.mean(by[u], axis=0) if by[u] else [1 / 3] * 3 for u in uids])
    q = np.maximum(q, 0.005); q = q / q.sum(1, keepdims=True)
    c = np.array([np.mean(conf[u]) if conf[u] else np.nan for u in uids])
    return q, c, rows
def rank(x):
    o = np.argsort(x, kind='mergesort'); r = np.empty(len(x)); xs = x[o]; i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]: j += 1
        r[o[i:j + 1]] = (i + j) / 2; i = j + 1
    return r
def spearman(a, b): m = ~(np.isnan(a) | np.isnan(b)); return float(np.corrcoef(rank(a[m]), rank(b[m]))[0, 1])
def half_split(counts, rng):
    a = np.zeros_like(counts); draw = np.full(len(counts), 50); pool = counts.sum(1).copy()
    for j in range(3):
        t = rng.hypergeometric(counts[:, j], pool - counts[:, j], draw) if True else None
        a[:, j] = t; draw -= t; pool -= counts[:, j]
    return a, counts - a
if __name__ == '__main__':
    uids, counts, old = load_items(); q, conf, rows = judge(uids)
    freq = counts / counts.sum(1, keepdims=True); err = np.abs(q - freq).sum(1)
    ent = -np.sum(np.where(q > 0, q * np.log(q), 0), 1)
    vc = collections.Counter((r['variant'], (r.get('dist') is not None) or (r.get('confidence') is not None)) for r in rows)
    print('items %d (all 100 labels: %s) | cache rows %d | parsed by variant: %s' % (len(uids), bool((counts.sum(1) == 100).all()), len(rows), dict(vc)))
    print('judge mean Manhattan error vs full 100 labels: %.4f (printed 0.458)' % err.mean())
    print('mean stated confidence: %.2f (printed 90.3) | items with a confidence: %d' % (np.nanmean(conf), int((~np.isnan(conf)).sum())))
    print('Spearman, stated confidence vs error: %+.3f (printed -0.13) | prediction entropy vs error: %+.3f (printed 0.11)' % (spearman(conf, err), spearman(ent, err)))
    rng = np.random.default_rng(0); nc = []
    for s in range(100):
        a, b = half_split(counts, rng); nc.append(np.abs(a / 50 - b / 50).sum(1))
    print('noise ceiling, 100 random half-splits (our seed 0): %.4f (printed 0.158)' % np.mean(np.mean(nc, 0)))
