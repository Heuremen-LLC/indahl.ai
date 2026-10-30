#!/usr/bin/env python3
"""S1-S3 (PLAN a1f47f8, committed before this ran). Sarkar, arXiv 2608.14329. Our code; their run files and benchmark read as data."""
import json, os, glob, math, random
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'tree_a2e47ae')
CD, CO = 'PRINCIPLE_CONSUMER_DUTY_FAIR_VALUE', 'PRINCIPLE_FAIR_CLEAR_NOT_MISLEADING'
def run(method, split, j2=False):
    fs = glob.glob(B + '/runs/*_%s_%s%s.json' % (method, split, '_judge2' if j2 else '')); assert len(fs) == 1, fs; return json.load(open(fs[0]))
def verdicts(d):
    out, fail = {}, {}
    for s in d['per_scenario']:
        if 'assessments' not in s: fail[s['id']] = str(s.get('error'))[:90]; continue
        out[s['id']] = {a['principle_id']: ('escalate' if a['escalation_required'] else 'comply') for a in s['assessments']}
    return out, fail
exp = lambda sid: sid.rsplit('_', 1)[1]
own = lambda sid: CD if 'CONSUMER_DUTY' in sid else CO
ADV = {json.loads(l)['id']: json.loads(l) for l in open(B + '/benchmark/eval/adversarial.jsonl') if l.strip()}
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
def binom2(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; pe = sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    return (po - pe) / (1 - pe) if pe < 1 else float('nan')
def boot_kappa(a, b, n=10000, seed=42):
    r = random.Random(seed); ks = []
    for _ in range(n):
        ix = [r.randrange(len(a)) for _ in a]; k = kappa([a[i] for i in ix], [b[i] for i in ix])
        if not math.isnan(k): ks.append(k)
    ks.sort(); return ks[int(0.025 * len(ks))], ks[int(0.975 * len(ks)) - 1], len(ks)
o1, fo = verdicts(run('llm-judge', 'original')); a1, fa = verdicts(run('llm-judge', 'adversarial'))
o2, _ = verdicts(run('llm-judge', 'original', True)); a2, fa2 = verdicts(run('llm-judge', 'adversarial', True))
# S1
print('S1 the headline drop, LLM-judge (gpt-oss:120b), Consumer Duty, each scenario on its own principle')
ko = sum(o1[i][CD] == exp(i) for i in o1 if own(i) == CD); no = sum(1 for i in o1 if own(i) == CD)
ka = sum(a1[i][CD] == exp(i) for i in a1 if own(i) == CD); na = sum(1 for i in a1 if own(i) == CD)
print('  (a) original %d/%d = %.3f Wilson [%.3f, %.3f] | adversarial %d/%d = %.3f Wilson [%.3f, %.3f]' % ((ko, no, ko / no) + wilson(ko, no) + (ka, na, ka / na) + wilson(ka, na)))
d, lo, hi = newcombe(ko, no, ka, na); print('      drop %+.3f, Newcombe 95%% [%+.3f, %+.3f] (printed 47 points)' % (d, lo, hi))
print('  (b) like for like: adversarial item against its own source original')
rows = []
for i in sorted(a1):
    if own(i) != CD: continue
    s = ADV[i]['source_id']; tgt = ADV[i]['adversarial_target']
    so = (o1[s][CD] == exp(s)) if s in o1 else None
    rows.append((i, s, tgt, so, a1[i][CD] == exp(i)))
    print('      %-58s %-13s source %-9s adversarial %s' % (i, tgt, {True: 'right', False: 'wrong', None: 'NO ASSESS'}[so], 'right' if rows[-1][4] else 'wrong'))
pr = [r for r in rows if r[3] is not None]
b = sum(1 for r in pr if r[3] and not r[4]); c = sum(1 for r in pr if not r[3] and r[4])
print('      paired n %d: source right, adversarial wrong %d | source wrong, adversarial right %d | exact McNemar p %.4f' % (len(pr), b, c, binom2(b, c)))
print('      source originals right %d/%d, adversarial right %d/%d on the same pairs' % (sum(r[3] for r in pr), len(pr), sum(r[4] for r in pr), len(pr)))
fcd = [i for i in fa if own(i) == CD]; focd = [i for i in fo if own(i) == CD]
print('  (c) failed scenarios: adversarial %s; originals %s' % (fcd, focd))
for lab, ko2, no2, ka2, na2 in (('failed counted wrong', ko, no + len(focd), ka, na + len(fcd)), ('failed counted right', ko + len(focd), no + len(focd), ka + len(fcd), na + len(fcd))):
    d, lo, hi = newcombe(ko2, no2, ka2, na2); print('      %-22s original %d/%d adversarial %d/%d drop %+.3f [%+.3f, %+.3f]' % (lab, ko2, no2, ka2, na2, d, lo, hi))
# S2
print('\nS2 Consumer Duty adversarial by flip direction (own principle)')
for jn, v in (('judge 1 gpt-oss:120b', a1), ('judge 2 kimi-k2.6', a2)):
    for tgt in ('flip_positive', 'flip_negative'):
        ids = [i for i in v if own(i) == CD and ADV[i]['adversarial_target'] == tgt]; k = sum(v[i][CD] == exp(i) for i in ids)
        print('  %-22s %-13s %d/%d' % (jn, tgt, k, len(ids)) + (' Wilson [%.2f, %.2f]' % wilson(k, len(ids)) if ids else ''))
print('  items per direction in adversarial.jsonl (Consumer Duty):', {t: sum(1 for x in ADV.values() if own(x['id']) == CD and x['adversarial_target'] == t) for t in ('flip_positive', 'flip_negative')})
print('  judge 2 failed adversarial scenarios:', sorted(fa2))
# S3
print('\nS3 second judge on Consumer Duty adversarial, own scenarios both judges assessed')
ids = sorted(i for i in a1 if i in a2 and own(i) == CD)
r1 = [a1[i][CD] == exp(i) for i in ids]; r2 = [a2[i][CD] == exp(i) for i in ids]
b = sum(1 for x, y in zip(r1, r2) if x and not y); c = sum(1 for x, y in zip(r1, r2) if not x and y)
print('  n %d | judge 1 right %d | judge 2 right %d | judge 1 only %d, judge 2 only %d | exact McNemar p %.4f' % (len(ids), sum(r1), sum(r2), b, c, binom2(b, c)))
v1 = [a1[i][CD] for i in ids]; v2 = [a2[i][CD] for i in ids]
k = kappa(v1, v2); lo, hi, m = boot_kappa(v1, v2); print('  kappa on own scenarios %.3f, bootstrap 95%% [%.3f, %.3f] (%d resamples defined)' % (k, lo, hi, m))
pid = sorted(i for i in a1 if i in a2 and CD in a1[i] and CD in a2[i]); p1 = [a1[i][CD] for i in pid]; p2 = [a2[i][CD] for i in pid]
k = kappa(p1, p2); lo, hi, m = boot_kappa(p1, p2)
print('  kappa pooled as theirs (n %d: %d Consumer Duty, %d COBS scenarios scored against Consumer Duty) %.3f, bootstrap 95%% [%.3f, %.3f] (%d resamples defined)' % (len(pid), sum(own(i) == CD for i in pid), sum(own(i) == CO for i in pid), k, lo, hi, m))
# S3b (PLAN Addendum 1, b3c3939, defined after the data)
print('\nS3b (defined after the data) Consumer Duty scenarios on their own principle, by split: escalate share and accuracy by expected verdict')
for split in ('original', 'paraphrase', 'adversarial', 'boundary'):
    for jn, j2 in (('judge 1', False), ('judge 2', True)):
        v, _ = verdicts(run('llm-judge', split, j2)); ids = [i for i in v if own(i) == CD and CD in v[i]]
        if not ids: print('  %-11s %s no scenarios' % (split, jn)); continue
        esc = sum(v[i][CD] == 'escalate' for i in ids)
        e = [i for i in ids if exp(i) == 'escalate']; c = [i for i in ids if exp(i) == 'comply']
        ke = sum(v[i][CD] == 'escalate' for i in e); kc = sum(v[i][CD] == 'comply' for i in c)
        print('  %-11s %s escalates %2d/%2d | right on escalate-expected %2d/%2d%s | right on comply-expected %2d/%2d%s' % (
            split, jn, esc, len(ids), ke, len(e), (' [%.2f, %.2f]' % wilson(ke, len(e))) if e else '', kc, len(c), (' [%.2f, %.2f]' % wilson(kc, len(c))) if c else ''))
# S3c, S1d (PLAN Addendum 2, fc8f51d, defined after the data)
print('\nS3c (defined after the data) pooled kappa ceiling given each judge\'s escalation count')
e1 = sum(a1[i][CD] == 'escalate' for i in pid); e2 = sum(a2[i][CD] == 'escalate' for i in pid); n = len(pid)
po_max = (min(e1, e2) + min(n - e1, n - e2)) / n; pe = (e1 * e2 + (n - e1) * (n - e2)) / n ** 2
po = sum(x == y for x, y in zip(p1, p2)) / n
print('  n %d | judge 1 escalates %d, judge 2 escalates %d | raw agreement %.4f, the most these rates allow %.4f | kappa %.4f, ceiling %.4f' % (n, e1, e2, po, po_max, (po - pe) / (1 - pe), (po_max - pe) / (1 - pe)))
print('\nS1d (defined after the data) judge 1 wrong adversarial verdicts by kind, Consumer Duty, own principle')
fp = sum(1 for i in a1 if own(i) == CD and exp(i) == 'escalate' and a1[i][CD] == 'comply'); fe = sum(1 for i in a1 if own(i) == CD and exp(i) == 'comply' and a1[i][CD] == 'escalate')
print('  false pass of an escalate-expected item %d | escalation of a comply-expected item %d' % (fp, fe))
a_ = sum(1 for r in pr if r[3] and r[4]); b_ = sum(1 for r in pr if r[3] and not r[4]); c_ = sum(1 for r in pr if not r[3] and r[4]); d_ = sum(1 for r in pr if not r[3] and not r[4]); m = len(pr)
q1, q2 = (a_ + b_) / m, (a_ + c_) / m; l1, u1 = wilson(a_ + b_, m); l2, u2 = wilson(a_ + c_, m)
den = math.sqrt((a_ + b_) * (c_ + d_) * (a_ + c_) * (b_ + d_)); ph = (a_ * d_ - b_ * c_) / den if den else 0.0
lo = (q1 - q2) - math.sqrt(max(0.0, (q1 - l1) ** 2 - 2 * ph * (q1 - l1) * (u2 - q2) + (u2 - q2) ** 2))
hi = (q1 - q2) + math.sqrt(max(0.0, (u1 - q1) ** 2 - 2 * ph * (u1 - q1) * (q2 - l2) + (q2 - l2) ** 2))
print('  matched drop on %d pairs: %d/%d to %d/%d = %+.3f, Newcombe paired 95%% [%+.3f, %+.3f] (cells a %d b %d c %d d %d)' % (m, a_ + b_, m, a_ + c_, m, q1 - q2, lo, hi, a_, b_, c_, d_))
