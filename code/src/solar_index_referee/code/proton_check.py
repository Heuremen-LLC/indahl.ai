# python3 -I : RSGA IIA proton peaks vs SPE.txt
src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
P = re.compile(r'Protons\s+greater\s+than\s+10\s+MeV\s+at\s+geosynchronous\s+orbit\s+reached\s+a\s+peak\s+level\s+of\s+(\d+)\s+pfu\s+at\s+(\d\d)/(\d{4})Z', re.S)
days = {}
for src_, tx in rsga_files():
    s = re.search(r'^SDF Number\s+\d+\s+Issued at \d{4}Z[^\n]* on (\d+) (\w{3}) (\d{4})', tx, re.M)
    if not s: continue
    day = dt.date(int(s[3]), MO[s[2]], int(s[1]))
    if day < dt.date(2021,1,1): continue
    m = P.search(tx)
    if m: days[day] = int(m[1])
big = {d: v for d, v in days.items() if v >= 10}
print('RSGA days with reported >10 MeV peak >= 10 pfu:', len(big), ' (SPE start days in frame:', len([d for d in spe if d >= dt.date(2021,1,1)]), ')')
# SPE spans: event days from start through the next day (rough) ; match RSGA days within +-1 day of a listed start
near = lambda d: any(abs((d - s).days) <= 1 for s in spe)
miss = sorted((d, v) for d, v in big.items() if not near(d))
print('RSGA >=10 pfu days with no SPE start within +-1 day:', len(miss))
for d, v in miss: print('  ', d, v, 'pfu')
