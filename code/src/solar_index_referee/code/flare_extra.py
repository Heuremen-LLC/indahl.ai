# python3 -I : flare assignment variants, M-only, secondary satellite, X<=M check, missing-K selection, autocorrelation
src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
# variants of day assignment
fb = C.defaultdict(lambda: [0, 0]); fm_only = C.defaultdict(int); sat = C.defaultdict(lambda: C.defaultdict(float)); cross = []; nomax = 0; chan = C.Counter()
for ds, tx in events_files():
    d0 = dt.date(int(ds[:4]), int(ds[4:6]), int(ds[6:]))
    for ln in tx.splitlines():
        if ' XRA ' not in ln: continue
        t = ln.split(); k = t.index('XRA'); chan[t[k+1]] += 1
        cls = t[k+2]; mm = re.fullmatch(r'([A-Z])(\d+(?:\.\d+)?)', cls)
        if not mm: continue
        pre = [x for x in t[:k] if x != '+']; b, m_ = hm(pre[1]), hm(pre[2]); obs_ = pre[4]
        if m_ is None: nomax += 1
        day_max = d0 + dt.timedelta(1) if (m_ is not None and b is not None and m_ < b) else d0
        if day_max != d0 and mm[1] in 'MX': cross.append((str(d0), cls))
        sat[day_max][obs_] = max(sat[day_max][obs_], (ord(mm[1]) - 65) * 10 + float(mm[2]) if mm[1] in 'ABCMX' else 0)
        if mm[1] in 'MX': fb[d0][0] += 1
        if mm[1] == 'X': fb[d0][1] += 1
        if mm[1] == 'M': fm_only[day_max] += 1
print('XRA channel tokens:', dict(chan)); print('XRA lines with //// max:', nomax)
print('M/X flares whose max falls on the next UTC day than begin:', len(cross), cross[:12])
both = [d for d in dsd if d in evdays and 2021 <= d.year < 2026]
agree_b = sum(1 for d in both if ((dsd[d][0] + dsd[d][1]) > 0) == (fb[d][0] > 0))
agree_m = sum(1 for d in both if ((dsd[d][0] + dsd[d][1]) > 0) == (flare[d][0] > 0))
print('join with begin-day assignment: %d / %d ; with max-day (plan): %d / %d' % (agree_b, len(both), agree_m, len(both)))
dis = [str(d) for d in both if ((dsd[d][0] + dsd[d][1]) > 0) != (fb[d][0] > 0)]; print('begin-day disagreeing:', dis)
# effect of begin-day assignment on M day-1
def m_series(assign, only=False):
    out = []
    for d, r in stated.items():
        tg = d + dt.timedelta(1)
        if r['d1'] != tg or r['iss'] >= dt.datetime.combine(tg, dt.time()) or tg >= SETTLED or tg not in evdays: continue
        p = r['M'][0]
        o = int((fm_only[tg] if only else assign[tg][0]) > 0)
        out.append((p / 100, o))
    return out
def bss(s):
    n = len(s); f = sum(o for p, o in s) / n; return n, sum(o for p, o in s), 1 - (sum((p - o)**2 for p, o in s) / n) / (f*(1-f))
print('M day1 max-day (plan):', bss(m_series(flare)), ' begin-day:', bss(m_series(fb)), ' M-only (M1.0-M9.9, max-day):', bss(m_series(None, True)))
# bins for M-only
def bins_of(s):
    out = []
    for (a, b) in BINS:
        x = [(p, o) for p, o in s if a <= round(p * 100) <= b]; n = len(x)
        if n < 30: out.append((a, b, n, None)); continue
        k = sum(o for p, o in x); mp = sum(p for p, o in x) / n
        c = k / n; z = 1.96; den = 1 + z*z/n; ce = (c + z*z/(2*n)) / den; h = z*math.sqrt(c*(1-c)/n + z*z/(4*n*n)) / den
        out.append((a, b, n, 'ABOVE' if ce-h > mp else 'BELOW' if ce+h < mp else 'CONSISTENT'))
    return out
mo = bins_of(m_series(None, True)); print('M-only bins:', C.Counter(x[3] for x in mo if x[3]), mo)
# secondary satellite: days where M+ is reported by exactly one obs code while another obs code logged only <M that day
amb = 0
for d, dd in sat.items():
    if len(dd) > 1 and max(dd.values()) >= 5*10 + 0 and False: pass
amb = [d for d, dd in sat.items() if len(dd) > 1 and (max(dd.values()) >= 120) and (min(dd.values()) < 120)]   # M1.0 -> (12-... compute by code below
print('days where two XRA observers logged and only some reached M (ordinal scale):', len(amb))
