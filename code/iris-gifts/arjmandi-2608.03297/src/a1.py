#!/usr/bin/env python3
"""A1 (PLAN 7c1e223, committed before this ran): Arjmandi's own repeat floor. At 100% retention the naive and signal-aware runs send the same
prompt; per model and eval, on items whose prompt_hash is equal, score differences between the two runs. Reads his results as data only."""
import json, os, glob, collections, numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'repo', 'results')
def load(p): return {d['sample_id']: d for d in (json.loads(l) for l in open(p))}
print('%-11s %-27s %5s %5s | %-30s | %s' % ('eval', 'model', 'pairs', 'equal', 'items scored differently (n>s / s>n)', 'mean signal-aware minus naive [95% paired, three seeds]'))
for p in sorted(glob.glob(R + '/*_naive_trunc100.jsonl')):
    base = os.path.basename(p)[:-len('_naive_trunc100.jsonl')]; ev = 'mrcr_v2' if base.startswith('mrcr_v2_') else base.split('_', 1)[0]; model = base[len(ev) + 1:]
    q = p.replace('_naive_trunc100', '_signal_aware_trunc100')
    if not os.path.exists(q): continue
    a, b = load(p), load(q); common = sorted(set(a) & set(b)); same = [i for i in common if a[i]['prompt_hash'] == b[i]['prompt_hash']]
    if not same: print('%-11s %-27s %5d %5d | no equal prompts' % (ev, model, len(common), 0)); continue
    x = np.array([float(a[i]['score']) for i in same]); y = np.array([float(b[i]['score']) for i in same]); d = y - x
    up = int((d > 0).sum()); dn = int((d < 0).sum()); cis = []
    for s in (1, 2, 3):
        idx = np.random.default_rng(s).integers(0, len(d), size=(10000, len(d))); cis.append(np.percentile(d[idx].mean(1), [2.5, 97.5]))
    print('%-11s %-27s %5d %5d | %4d of %4d (%d / %d)               | %+.3f %s' % (ev, model, len(common), len(same), up + dn, len(same), dn, up, d.mean(), ' '.join('[%+.3f, %+.3f]' % tuple(c) for c in cis)))

# Beside his Table 1 (25% against full context, within each protocol, paired on sample_id): items whose score changes, our count, against
# the full-context repeat floor above. A contrast whose changed items are no more than its model's floor carries no item movement beyond rerun.
print('\nTable 1 contrasts: items changed from full context to 25% (our count) against the full-context repeat floor of that model and eval')
for p in sorted(glob.glob(R + '/*_naive_trunc100.jsonl')):
    base = os.path.basename(p)[:-len('_naive_trunc100.jsonl')]; ev = 'mrcr_v2' if base.startswith('mrcr_v2_') else base.split('_', 1)[0]; model = base[len(ev) + 1:]
    q = p.replace('_naive_trunc100', '_signal_aware_trunc100')
    if not os.path.exists(q): continue
    a, b = load(p), load(q); same = [i for i in set(a) & set(b) if a[i]['prompt_hash'] == b[i]['prompt_hash']]
    floor = sum(float(a[i]['score']) != float(b[i]['score']) for i in same)
    for mode in ('naive', 'signal_aware'):
        full = load(R + '/%s_%s_trunc100.jsonl' % (base, mode)); t25 = load(R + '/%s_%s_trunc25.jsonl' % (base, mode)); c = sorted(set(full) & set(t25))
        ch = sum(float(full[i]['score']) != float(t25[i]['score']) for i in c); dm = np.mean([float(t25[i]['score']) - float(full[i]['score']) for i in c])
        print('  %-10s %-27s %-12s n %4d | changed %4d (mean delta %+.3f) | floor %3d of %4d | %s' % (ev, model, mode, len(c), ch, dm, floor, len(same), 'within floor' if ch <= floor else 'above floor by %d' % (ch - floor)))

# Addendum 1 (A1b-A1d): date span of each floor, a 0.05 threshold for continuous scores, and the floor's mean difference beside his delta.
print('\nA1b-A1d per model and eval: floor date span | floor at any change and at |d| >= 0.05 | floor mean (signal-aware minus naive at 100%) beside his two Table 1 deltas')
for p in sorted(glob.glob(R + '/*_naive_trunc100.jsonl')):
    base = os.path.basename(p)[:-len('_naive_trunc100.jsonl')]; ev = 'mrcr_v2' if base.startswith('mrcr_v2_') else base.split('_', 1)[0]; model = base[len(ev) + 1:]
    q = p.replace('_naive_trunc100', '_signal_aware_trunc100')
    if not os.path.exists(q): continue
    a, b = load(p), load(q); same = [i for i in set(a) & set(b) if a[i]['prompt_hash'] == b[i]['prompt_hash']]
    ts = sorted(r['timestamp_utc'][:10] for r in list(a.values()) + list(b.values()))
    d = np.array([float(b[i]['score']) - float(a[i]['score']) for i in same])
    deltas = []
    for mode in ('naive', 'signal_aware'):
        full = load(R + '/%s_%s_trunc100.jsonl' % (base, mode)); t25 = load(R + '/%s_%s_trunc25.jsonl' % (base, mode)); c = sorted(set(full) & set(t25))
        x = np.array([float(t25[i]['score']) - float(full[i]['score']) for i in c])
        deltas.append('%s %+.3f (changed %d, at 0.05: %d)' % (mode, x.mean(), int((x != 0).sum()), int((abs(x) >= 0.05).sum())))
    print('  %-10s %-27s %s to %s | floor %d, at 0.05: %d | floor mean %+.3f | %s' % (ev, model, ts[0], ts[-1], int((d != 0).sum()), int((abs(d) >= 0.05).sum()), d.mean(), ' | '.join(deltas)))
