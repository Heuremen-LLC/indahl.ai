import sys, json, re, datetime as DT, collections as C
sys.path.insert(0, '/Users/heuremen/bones-forge/steo_index_referee/code')
import recount as R
def level_of(s, cells):
    """own level finder: numeric in (0,1] in the 6 rows above the header row, any column"""
    r0 = s['r0']
    vals = [v for (r, c), v in cells.items() if r0-8 <= r < r0 and isinstance(v, float) and 0 < v <= 1]
    return vals[0] if vals else None
def build():
    REL, SP, copies = R.main()
    relname = {d: (n, p) for d, n, p in REL}
    ok = []
    for c in copies:
        if 'err' in c or not c['rel']: continue
        ok.append(c)
    byrel = C.defaultdict(list)
    for c in ok:
        if c['rel'] > c['cap']: continue   # captured before release: not usable
        byrel[c['rel']].append(c)
    rows = []; begun = 0; nostated = 0; disagree = 0
    for rel, cps in sorted(byrel.items()):
        cps.sort(key=lambda x: x['ts']); c = cps[0]
        for later in cps[1:]:
            for sr in ('WTI', 'HH'):
                a = c['sheets'].get(sr); b = later['sheets'].get(sr)
                if a and b:
                    for ym, (lo, up, _) in a['rows'].items():
                        if ym in b['rows'] and isinstance(lo, float) and (b['rows'][ym][0], b['rows'][ym][1]) != (lo, up): disagree += 1
        for sr in ('WTI', 'HH'):
            s = c['sheets'].get(sr)
            if not s: continue
            # re-read cells for the level: reload file
            for ym, (lo, up, rr) in sorted(s['rows'].items()):
                lo_n = lo if isinstance(lo, float) else None; up_n = up if isinstance(up, float) else None
                if lo_n is None and up_n is None: nostated += 1; continue
                if (ym[0], ym[1]) <= (rel.year, rel.month): begun += 1; continue
                y = SP[sr].get(ym)
                rows.append(dict(rel=str(rel), issue=relname[rel][1], series=sr, ym='%04d-%02d' % ym, lead=(ym[0]-rel.year)*12+ym[1]-rel.month,
                                 lo=lo_n, up=up_n, spot=y, copy=c['file'], has_level=s['has_level'], level=s['level'], sheet=s['sheet']))
    return REL, SP, copies, rows, dict(begun=begun, nostated=nostated, disagree=disagree)
def outcome(r):
    if r['lo'] is None or r['up'] is None or r['lo'] > r['up']: return 'CANNOT_TELL'
    if r['spot'] is None: return 'NOTHING_RETURNED'
    return 'ABOVE' if r['spot'] > r['up'] else ('BELOW' if r['spot'] < r['lo'] else 'CONSISTENT')
if __name__ == '__main__':
    REL, SP, copies, rows, ex = build()
    for r in rows: r['out'] = outcome(r)
    print(ex, len(rows))
    json.dump(rows, open('/Users/heuremen/bones-forge/steo_index_referee/out/rows.json', 'w'))
