"""readings_after_referee.py -- YO v3 readings added after the referee (31 Oct 2026), all defined after the data except the nulls the plan named."""
import sys, json, re, random, collections; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo3_compare as Y
v3, v2, dr, no = Y.load('yo_v3'), Y.load('yo_v2'), Y.load('daterule'), Y.load('nothing')
A = [i for i in Y.items if Y.items[i]['job'] == 'A']; C = [i for i in Y.items if Y.items[i]['job'] == 'C']
def mean(ev, ids): return sum(ev[i]['score'] for i in ids) / len(ids)
print('NULLS (named in the plan): Job A flag nothing %.3f, date rule %.3f; Job C flag nothing n/a' % (mean(no, A), mean(dr, A)))
for n, ev in (('date rule', dr),):
    r = Y.readings(ev); print('date rule: stale recall %.3f precision %.3f band recall %.3f (%d of %d)' % (r['recall'], r['precision'], r['band_recall'], round(r['band_recall'] * r['band_n']), r['band_n']))
empty = [i for i in A if not json.loads(Y.items[i]['answer'])['stale'] and not json.loads(Y.items[i]['answer'])['zero']]
ne = [i for i in A if i not in empty]
print('Job A items with nothing to flag: %d of %d (every system scores them %s)' % (len(empty), len(A), sorted(set(round(ev[i]['score'], 3) for ev in (v3, v2, dr) for i in empty))))
print('Job A on the %d items with something to flag (defined after the data): v3 %.3f, v2 %.3f, date rule %.3f' % (len(ne), mean(v3, ne), mean(v2, ne), mean(dr, ne)))
# band split by whether every qubit in the item is band-stale (defined after the data, conditioned on the truth)
def split(ev):
    full = part = None; out = {'all8': [0, 0], 'some': [0, 0]}
    for i in A:
        q = Y.qubits(i, ev); nb = sum(1 for x in q if x[0] and x[1])
        if not nb: continue
        k = 'all8' if nb == len(q) else 'some'
        for x in q:
            if x[0] and x[1]: out[k][0] += x[2]; out[k][1] += 1
    return out
for n, ev in (('v3', v3), ('v2', v2), ('date rule', dr)):
    s = split(ev); print('band recall, %s: items where all 8 are band-stale %d/%d = %.3f; other items %d/%d = %.3f' % (n, s['all8'][0], s['all8'][1], s['all8'][0] / s['all8'][1], s['some'][0], s['some'][1], s['some'][0] / s['some'][1]))
for n, ev in (('v3', v3), ('v2', v2)):
    said = collections.Counter(ev[i]['pred'] for i in C); wrong_ct = sum(1 for i in C if ev[i]['pred'] == 'CANNOT_TELL' and Y.items[i]['answer'] != 'CANNOT_TELL')
    print('%s Job C: answers CANNOT_TELL on %d of 400 (100 true); %d of them wrong' % (n, said['CANNOT_TELL'], wrong_ct))
for n, ev in (('v3', v3), ('v2', v2)):
    tp = fp = 0; tot = 0
    for i in A:
        t = set(json.loads(Y.items[i]['answer'])['zero']); tot += len(t)
        o = ev[i]['out']; o = json.loads(o[o.index('{'):o.rindex('}') + 1]); y = set(o.get('zero', []))
        tp += len(t & y); fp += len(y - t)
    print('%s zero flags: %d of %d found, %d false' % (n, tp, tot, fp))
# split intervals: paired bootstrap over records as the plan's ruler (2,000 resamples, seed 31, 95 %), defined after the data
byrec = collections.defaultdict(list)
for i, it in Y.items.items(): byrec[it['record']].append(i)
recs = sorted(byrec); rng = random.Random(31)
def dsplit(kind):
    def f(R):
        h3 = h2 = n = 0
        for r in R:
            for i in byrec[r]:
                if Y.items[i]['job'] != 'A': continue
                q3, q2 = Y.qubits(i, v3), Y.qubits(i, v2); nb = sum(1 for x in q3 if x[0] and x[1])
                if not nb or (nb == len(q3)) != (kind == 'all8'): continue
                for (s, b, f3), (_, _, f2) in zip(q3, q2):
                    if s and b: n += 1; h3 += f3; h2 += f2
        return (h3 - h2) / max(1, n)
    return f
for kind in ('all8', 'some'):
    v, lo, hi = Y.boot(dsplit(kind), recs, rng)
    print('band recall v3 minus v2, %s: %+.3f [%+.3f, %+.3f] -> %s' % ('items where all 8 are band-stale' if kind == 'all8' else 'other items', v, lo, hi, Y.outcome(lo, hi)))
