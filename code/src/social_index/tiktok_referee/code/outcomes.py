"""Referee: combine the stated and delivered recounts into ranges and outcomes (PLAN.md rule, Addendum 2.3 windows),
and compare every EU row with data/tiktok.json."""
import json
R = '/Users/heuremen/bones-forge/social_index/tiktok_referee/'
S = json.load(open(R + 'stated_recount.json'))
Dd = json.load(open(R + 'delivered_recount.json'))
T = json.load(open('/Users/heuremen/bones-forge/social_index/tiktok/data/tiktok.json'))
rows = {(r['quarter'], r['measure']): r for r in T['rows'] if r['market'] == 'EU'}
DEC = ('app', 'app-1', 'app+1'); ALL = DEC + ('created',)
def ranges(g, allow, wins):
    P = g['point|app']
    out = {'videos_removed': dict(point=P['n'], lo=min(g['lower|' + w]['n'] for w in wins), hi=max(g['upper|' + w]['n'] for w in wins) + allow['n']),
           'automated_removals': dict(point=P['fully'], lo=min(g['lower|' + w]['fully'] for w in wins), hi=max(g['upper|' + w]['fully'] for w in wins) + allow['fully'])}
    cells = [g[s + '|' + w] for s in ('lower', 'point', 'upper') for w in wins]
    for nm, k in (('automated_share', 'fully'), ('proactive_rate', 'vol')):
        v = [c[k] / c['n'] for c in cells if c['n']]
        out[nm] = dict(point=P[k] / P['n'], lo=min(v), hi=max(v))
    out['within_24h_rate'] = dict(point=None, lo=min(c['d0'] / c['n'] for c in cells if c['n']), hi=max(c['d01'] / c['n'] for c in cells if c['n']))
    return out
def outcome(s, d, share):
    glo, ghi = d['lo'] - s['hi'], d['hi'] - s['lo']
    m = 0.01 if share else 0.05 * s['point']
    if glo > 0: return 'ABOVE', glo, ghi, ('yes' if glo > m else ('no' if ghi <= m else 'cannot tell'))
    if ghi < 0: return 'BELOW', glo, ghi, ('yes' if ghi < -m else ('no' if glo >= -m else 'cannot tell'))
    if glo >= -m and ghi <= m: return 'CONSISTENT', glo, ghi, 'no'
    return 'CANNOT_TELL', glo, ghi, None
SH = {'automated_share', 'proactive_rate', 'within_24h_rate'}
res = {}
mism = 0
for q in sorted(Dd):
    st = S[q]['stated']
    dr = ranges(Dd[q]['grid'], Dd[q]['allow'], DEC)
    dr_sub = ranges(Dd[q]['grid'], Dd[q]['allow'], ALL)
    for ms in ('videos_removed', 'automated_removals', 'automated_share', 'proactive_rate', 'within_24h_rate'):
        sh = ms in SH
        oc, glo, ghi, mat = outcome(st[ms], dr[ms], sh)
        oc2, glo2, ghi2, mat2 = outcome(st[ms], dr_sub[ms], sh)
        r = rows.get((q, ms))
        res['%s|%s' % (q, ms)] = dict(stated=st[ms], delivered=dr[ms], gap=[glo, ghi], rule_outcome=oc, material=mat,
                                      with_submission=dict(delivered=dr_sub[ms], gap=[glo2, ghi2], outcome=oc2, material=mat2))
        # compare with desk
        flag = []
        if r:
            for a, b, nm in ((st[ms]['point'], r['stated'], 'stated'), (st[ms]['lo'], r['stated_interval'][0], 'S_lo'), (st[ms]['hi'], r['stated_interval'][1], 'S_hi'),
                             (dr[ms]['lo'], r['delivered_interval'][0], 'D_lo'), (dr[ms]['hi'], r['delivered_interval'][1], 'D_hi'),
                             (dr_sub[ms]['lo'], r['delivered_interval_with_submission_date'][0], 'Dsub_lo'), (dr_sub[ms]['hi'], r['delivered_interval_with_submission_date'][1], 'Dsub_hi')):
                if a is None and b is None: continue
                if a is None or b is None or abs(a - b) > (1e-9 if sh else 0.5): flag.append((nm, a, b))
            desk_rule = r.get('outcome_rule_without_coverage_limit') or (r['outcome'] if 'day check' not in (r.get('reason') or '') else None)
            if flag: mism += 1
        f = lambda x: ('%.4f' % x) if sh else ('%d' % round(x))
        print('%s %-18s S=%s [%s,%s] D=%s [%s,%s] gap=[%s,%s] rule=%s mat=%s | +sub: D=[%s,%s] %s | desk: %s %s %s' % (
            q, ms, f(st[ms]['point']), f(st[ms]['lo']), f(st[ms]['hi']), f(dr[ms]['point']) if dr[ms]['point'] is not None else '-', f(dr[ms]['lo']), f(dr[ms]['hi']),
            f(glo), f(ghi), oc, mat, f(dr_sub[ms]['lo']), f(dr_sub[ms]['hi']), oc2,
            r['outcome'] if r else None, (r.get('defined_after_the_data') or {}).get('outcome') if r else None, ('MISMATCH ' + str(flag)) if flag else 'match'))
print('rows with a numeric mismatch against the desk:', mism)
json.dump(res, open(R + 'outcomes_recount.json', 'w'), indent=1)
