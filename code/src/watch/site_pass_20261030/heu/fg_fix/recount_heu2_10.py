"""recount_heu2_10.py -- HEU2-10/13/14 recount from the record, 30 Oct 2026.

Source: triangulation/triangle/runs/hook_fires.log, first 374 rows (cut at 2026-10-08T16:31:51, the
"374 logged checks" of iris_index/recounts/seed_faults_guards/RESULT.md line 9).
Seated = session 1fecc2b7. Cold = one-shot sessions (not seated, not 'testtest').

Width rule reproduced from triangulation/triangle/audit_guard.py lines 92-106 (written 8 Oct, the
script that first printed +3.02 and +0.97):
  per reply:   p = k/n, se = sqrt(p(1-p)/n)          (binomial, unpooled)
  per 1k words r = 1000 k/w, se = 1000 sqrt(max(k,1))/w (Poisson)
  width count  = (x_day - x_prev) / sqrt(se_day^2 + se_prev^2), each day against the PREVIOUS day.
audit_guard.py counts frames as occurrences of 'frame(s): "' in a row (one per flagged row here).

Run: ~/bones-forge/qvenv/bin/python -I recount_heu2_10.py
"""
import re, math, collections, statistics as st
from scipy import stats

LOG = '/Users/heuremen/bones-forge/triangulation/triangle/runs/hook_fires.log'
L = open(LOG).read().split('\n')[:374]
rows = []
for i, l in enumerate(L):
    m = re.match(r'(\S+) session (\S+) mode (\S+) words (\d+) (.*)', l)
    if not m:
        print('NOMATCH', i + 1, l[:80]); continue
    rows.append(dict(i=i + 1, t=m.group(1), s=m.group(2), w=int(m.group(4)), rest=m.group(5), line=l))
print('rows parsed', len(rows), ' last row time', rows[-1]['t'])

def kind(r):
    return 'seated' if r['s'] == '1fecc2b7' else ('test' if r['s'] == 'testtest' else 'cold')

S = [r for r in rows if kind(r) == 'seated']
C = [r for r in rows if kind(r) == 'cold']
pb = lambda r: 'PUSHED BACK' in r['rest']
tl = lambda r: 'Two-lane' in r['rest']
fa = lambda r: len(re.findall(r'frame\(s\): "', r['line']))   # audit_guard.py's frame count

print('\n== arms (HEU2-14) ==')
print(f"cold   rows {len(C)}  two-lane {sum(map(tl, C))}  = {100*sum(map(tl, C))/len(C):.1f}%   median words {st.median(r['w'] for r in C)}  min {min(r['w'] for r in C)}  >=300 {sum(r['w']>=300 for r in C)}")
print(f"seated rows {len(S)}  two-lane {sum(map(tl, S))}  = {100*sum(map(tl, S))/len(S):.1f}%   pushbacks {sum(map(pb, S))} = {100*sum(map(pb, S))/len(S):.1f}%   median words {st.median(r['w'] for r in S)}  max {max(r['w'] for r in S)}")
print(f"seated rows with words >= cold min ({min(r['w'] for r in C)}): {sum(r['w']>=min(x['w'] for x in C) for r in S)}")
print('cold sessions', len(set(r['s'] for r in C)))

days = ['2026-10-06', '2026-10-07', '2026-10-08']
D = {}
for d in days:
    s = [r for r in S if r['t'].startswith(d)]
    D[d] = dict(n=len(s), pb=sum(map(pb, s)), tl=sum(map(tl, s)), fa=sum(map(fa, s)), w=sum(r['w'] for r in s),
                med=st.median(r['w'] for r in s))
print('\n== seated by day (HEU2-10) ==')
for d in days:
    x = D[d]
    print(f"{d}  replies {x['n']:3d}  pushbacks {x['pb']:3d}  two-lane rows {x['tl']:3d}  audit_guard frames {x['fa']:3d}  words {x['w']:6d}  median {x['med']}")
    print(f"            per reply: pushbacks {100*x['pb']/x['n']:.1f}%  frames {100*x['tl']/x['n']:.1f}%   per 1k words: pushbacks {1000*x['pb']/x['w']:.2f}  frames {1000*x['tl']/x['w']:.2f}")
print('mean words/reply by day', [round(D[d]['w']/D[d]['n'], 1) for d in days],
      ' day3 vs day2 longer by', f"{100*((D[days[2]]['w']/D[days[2]]['n'])/(D[days[1]]['w']/D[days[1]]['n'])-1):.0f}%")

def w_reply(k, n, k0, n0):
    p, p0 = k / n, k0 / n0
    se, se0 = math.sqrt(p * (1 - p) / n), math.sqrt(p0 * (1 - p0) / n0)
    return (p - p0) / math.sqrt(se ** 2 + se0 ** 2)

def w_words(k, w, k0, w0):
    r, r0 = 1000 * k / w, 1000 * k0 / w0
    se, se0 = 1000 * math.sqrt(max(k, 1)) / w, 1000 * math.sqrt(max(k0, 1)) / w0
    return (r - r0) / math.sqrt(se ** 2 + se0 ** 2)

print('\n== widths, audit_guard.py rule (each day against the previous day) ==')
for key, lab in (('pb', 'pushbacks'), ('tl', 'frames')):
    for a, b in ((1, 0), (2, 1), (2, 0)):
        da, db = D[days[a]], D[days[b]]
        print(f"{lab:9s} {days[a][-5:]} vs {days[b][-5:]}:  per reply {w_reply(da[key], da['n'], db[key], db['n']):+.2f}   per 1k words {w_words(da[key], da['w'], db[key], db['w']):+.2f}")

print('\n== plain cross-check: day 3 against days 1 and 2 pooled ==')
d3 = D[days[2]]; d12 = {k: D[days[0]][k] + D[days[1]][k] for k in ('n', 'pb', 'tl', 'w')}
def z2pooled(a, n, b, m):
    p = (a + b) / (n + m); return (a / n - b / m) / math.sqrt(p * (1 - p) * (1 / n + 1 / m))
def zpois(a, w, b, v):
    return (a / w - b / v) / math.sqrt(a / w ** 2 + b / v ** 2)
for key, lab in (('pb', 'pushbacks'), ('tl', 'frames')):
    print(f"{lab:9s} per reply two-proportion z {z2pooled(d3[key], d3['n'], d12[key], d12['n']):+.2f}   per 1k words Poisson z {zpois(d3[key], d3['w'], d12[key], d12['w']):+.2f}")

print('\n== HEU2-13 bound: frames per 1k words, day 3 against days 1 and 2 pooled ==')
k3, w3, k12, w12 = d3['tl'], d3['w'], d12['tl'], d12['w']
r3, r12 = 1000 * k3 / w3, 1000 * k12 / w12
print(f"day 3 {k3}/{w3} = {r3:.3f}/1k   days 1-2 {k12}/{w12} = {r12:.3f}/1k   ratio {r3/r12:.3f}")
# exact conditional: k3 | total ~ Binomial(K, pi), pi = w3 R/(w3 R + w12)  -> R = pi/(1-pi) * w12/w3
K = k3 + k12
lo = stats.beta.ppf(0.025, k3, K - k3 + 1); hi = stats.beta.ppf(0.975, k3 + 1, K - k3)
Rlo, Rhi = lo / (1 - lo) * w12 / w3, hi / (1 - hi) * w12 / w3
print(f"exact 95% (conditional binomial, Clopper-Pearson) rate ratio day3/days1-2: [{Rlo:.3f}, {Rhi:.3f}]")
lr = math.log(r3 / r12); se = math.sqrt(1 / k3 + 1 / k12)
print(f"Wald-log 95% rate ratio: [{math.exp(lr-1.96*se):.3f}, {math.exp(lr+1.96*se):.3f}]")
# day 3 against day 1
k1, w1 = D[days[0]]['tl'], D[days[0]]['w']
K = k3 + k1
lo = stats.beta.ppf(0.025, k3, K - k3 + 1); hi = stats.beta.ppf(0.975, k3 + 1, K - k3)
print(f"exact 95% rate ratio day3/day1: [{lo/(1-lo)*w1/w3:.3f}, {hi/(1-hi)*w1/w3:.3f}]  point {(k3/w3)/(k1/w1):.3f}")
# per reply day3 vs days1-2: difference and Newcombe-ish (Wald) interval
p3, p12 = k3 / d3['n'], k12 / d12['n']
se = math.sqrt(p3 * (1 - p3) / d3['n'] + p12 * (1 - p12) / d12['n'])
print(f"per reply frames day3 {100*p3:.1f}% vs days1-2 {100*p12:.1f}%: diff {100*(p3-p12):+.1f} pts, Wald 95% [{100*(p3-p12-1.96*se):+.1f}, {100*(p3-p12+1.96*se):+.1f}]")

print('\n== seated totals ==')
print('replies', len(S), 'pushbacks', sum(map(pb, S)), 'frame rows', sum(map(tl, S)), 'words', sum(r['w'] for r in S))
print('pushback rows WITHOUT a two-lane frame', sum(pb(r) and not tl(r) for r in S), ' two-lane rows not pushed', sum(tl(r) and not pb(r) for r in S))
