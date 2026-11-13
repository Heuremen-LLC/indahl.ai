#!/usr/bin/env python3
"""airq_tie.py (10 Nov 2026, PLAN Addendum 5, after the data): the plan takes the sensor of the median-RMSE pair at each monitor and states no
rule for a monitor with an even number of sensors. The code has always taken the lower of the two middle pairs ((n - 1) // 2 after sorting by
RMSE). This script prints that reading and the one the other tie gives, for each reading, into the window summaries and the feed, and it states
that the plan names no headline reading. Run after airq_tick.py and airq_promote.py. Standard library only."""
import os, json, fcntl, collections
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); import sys; sys.path.insert(0, H)
import heuremen_kit as K
def meets(m): return bool(m and 0.65 <= m['slope'] <= 1.35 and -5 <= m['intercept'] <= 5 and m['r2'] >= 0.70 and (m['rmse'] <= 7 or (m['nrmse'] is not None and m['nrmse'] <= 30)))
def outcome(n_not, n):
    if n < 30: return K.CANNOT_TELL
    lo, hi = K.wilson(n_not, n); return K.ABOVE if lo > 0.5 else (K.CONSISTENT if hi < 0.5 else K.CANNOT_TELL)
NAME = {'R1': 'Map reading (atm channels, raw)', 'R2': 'cf_1 channels, raw', 'R3': 'cf_1 corrected for humidity (Barkjohn 2021)'}
TIE = ('At a monitor with an even number of sensors the plan states no rule for the median pair. The code takes the lower of the two middle pairs by RMSE, '
       'for each reading separately. The other tie, the upper middle pair, is printed beside each count. Both were stated on 10 Nov 2026, after the data.')
HEAD = ('The plan names no headline reading. The map reading (what the PurpleAir map shows as raw) and the reading corrected for humidity are shown with equal weight.')
def ties(pairs):
    by = collections.defaultdict(list)
    for p in pairs: by[p['monitor']].append(p)
    out = {}
    for r, nm in NAME.items():
        unit = [sorted([p for p in ps if p[r]], key=lambda p: p[r]['rmse']) for ps in by.values()]; unit = [u for u in unit if u]
        n = len(unit); hi_not = sum(1 for u in unit if not meets(u[len(u) // 2][r])); lo_, hi_ = K.wilson(hi_not, n)
        out[nm] = dict(n_other_tie=hi_not, share_other_tie=round(hi_not / n, 4), share_other_tie_lo=round(lo_, 4), share_other_tie_hi=round(hi_, 4), outcome_other_tie=outcome(hi_not, n),
                       monitors_even=sum(1 for u in unit if len(u) % 2 == 0))
    return out
def apply(S, T):
    for nm, v in T.items():
        if nm in S.get('comparison', {}): S['comparison'][nm].update(v)
    S['tie_rule'] = TIE; S['headline_rule'] = HEAD
    for k in ('headline', 'headline_n', 'headline_of'): S.pop(k, None)
    return S
t26 = ties(json.load(open('data/w2026/pairs.json'))); t25 = ties(json.load(open('data/pairs.json')))
for f, t in (('summary_airq_w2026.json', t26), ('summary_airq_w2025.json', t25)):
    json.dump(apply(json.load(open(f)), t), open(f, 'w'), indent=1)
_l = open('data/.live.lock', 'w'); fcntl.flock(_l, fcntl.LOCK_EX)   # the live tick reads and writes summary_airq.json under the same lock
S = apply(json.load(open('summary_airq.json')), t26)
if S.get('previous'): S['previous'] = apply(S['previous'], t25); S['previous'].pop('tie_rule', None); S['previous'].pop('headline_rule', None)
json.dump(S, open('summary_airq.json', 'w'), indent=1)
for nm in NAME.values(): c = S['comparison'][nm]; print('airq-tie:', nm, c['n'], 'or', c['n_other_tie'], 'of', c['of'], c['outcome'], c['outcome_other_tie'])
