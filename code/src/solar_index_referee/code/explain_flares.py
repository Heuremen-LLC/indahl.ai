# Explains the M/X row differences: replays the desk's published regex shape on the raw events and compares to DSD. python3 -I
import re
src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
DESK = re.compile(r'^\d+\s+\+?\s*(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+XRA\s+\S+\s+([A-Z])(\d+(?:\.\d+)?)', re.M)
lead = C.Counter(); tot = 0; fl_desk = C.defaultdict(lambda: [0, 0])
for ds, tx in events_files():
    d0 = dt.date(int(ds[:4]), int(ds[4:6]), int(ds[6:]))
    for ln in tx.splitlines():
        if ' XRA ' in ln:
            tot += 1; lead[ln[0] == ' '] += 1
    for b, mx, e, L_, num in DESK.findall(tx):
        tb, tm = hm(b), hm(mx); d = d0 + dt.timedelta(1) if (tm is not None and tb is not None and tm < tb) else d0
        if L_ in 'MX': fl_desk[d][0] += 1
        if L_ == 'X': fl_desk[d][1] += 1
print('XRA lines', tot, 'with leading space', lead[True], 'without', lead[False])
mine = {d for d in flare if flare[d][0] > 0}; desk = {d for d in fl_desk if fl_desk[d][0] > 0}
minex = {d for d in flare if flare[d][1] > 0}; deskx = {d for d in fl_desk if fl_desk[d][1] > 0}
print('M-or-X days mine', len(mine), 'desk-regex', len(desk), 'mine-not-desk', len(mine - desk), 'desk-not-mine', len(desk - mine))
print('X days mine', len(minex), 'desk-regex', len(deskx))
# frame days only 2021-01-02 .. 2026-11-06
fr = lambda S: {d for d in S if dt.date(2021,1,2) <= d < SETTLED and d in evdays}
print('in-frame M days mine', len(fr(mine)), 'desk', len(fr(desk)))
# DSD join, complete years 2021-2025 (desk's gate rule)
both = [d for d in dsd if d in evdays and 2021 <= d.year < 2026]
def agree(S): return sum(1 for d in both if ((dsd[d][0] + dsd[d][1]) > 0) == (d in S))
print('join days', len(both), 'desk-regex agree', agree(desk), 'referee agree', agree(mine))
dis = sorted(d for d in both if ((dsd[d][0] + dsd[d][1]) > 0) != (d in mine))
print('referee disagreeing days', len(dis))
for d in dis: print(' ', d, 'DSD M,X', dsd[d], 'events M+X lines', flare[d] if d in flare else [0,0])
dd = sorted(d for d in both if ((dsd[d][0] + dsd[d][1]) > 0) != (d in desk))
print('desk-regex disagreeing days', len(dd), 'of which fixed by referee reading', len([d for d in dd if d not in dis]))
# X-days check against DSD
bx = sum(1 for d in both if (dsd[d][1] > 0) == (d in minex)); print('X join agree (referee)', bx, 'of', len(both))
bxd = sum(1 for d in both if (dsd[d][1] > 0) == (d in deskx)); print('X join agree (desk regex)', bxd)
# how many DSD flare counts equal number of M lines per day (distinct flares)
