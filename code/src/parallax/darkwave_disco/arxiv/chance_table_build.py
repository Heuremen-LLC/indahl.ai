#!/usr/bin/env python3
import math, csv, statistics as st, re, json

LN4 = math.log(4.0)
PHI = (1 + 5 ** 0.5) / 2
K1483 = PHI * 11 / 12          # 1.48324
R1211 = 12 / 11

def p_band(w):
    """two-sided: read ratio within +-w of called, log-uniform over [1/2,2]"""
    if w >= 1: return 1.0
    return min(1.0, math.log((1 + w) / (1 - w)) / LN4)

def p_below(x):
    """one-sided: P(X <= x), X log-uniform on [0.5, 2]"""
    if x <= 0.5: return 0.0
    if x >= 2.0: return 1.0
    return math.log(x / 0.5) / LN4

def sd(v): return st.stdev(v)

# ---------- derived widths from read files ----------
txt = open('/Users/heuremen/bones-forge/parallax/darkwave_disco/for_indahl_ai/data/reads_20261004/time_wide_fez_reads123_20261004.txt').read()
reads = re.split(r'THE TIME RUN', txt)[1:]
fez = {}
for spc in (10, 30, 70, 100):
    per = []; sg = []
    for r in reads:
        vals = []; s = []
        for c in 'abc':
            m = re.search(r'OFF spread @\s*%d us minus ONE, copy %s\s+([+-]\d\.\d+) \+- (\d\.\d+)' % (spc, c), r)
            vals.append(float(m.group(1)) * 100); s.append(float(m.group(2)) * 100)
        per.append(st.mean(vals)); sg.append(math.sqrt(sum(x * x for x in s)) / 3)
    mean = st.mean(per); s_reads = sd(per)
    resamp = math.sqrt(sum(x * x for x in sg)) / 3
    fez[spc] = (mean, math.sqrt(s_reads ** 2 + resamp ** 2))

fez_WO = [1.0384, 0.9947, 1.0385]; fez_TO = [1.3955, 1.7983, 1.4276]; fez_TW = [1.3438, 1.8079, 1.3746]
fez_cnt = [0.872, 0.855, 0.807]
bos_WO = [1.0425, 1.1236, 1.0673]; bos_TO = [1.3362, 1.4901, 1.2185]; bos_TW = [1.2818, 1.3262, 1.1417]
ph_WO = [0.9775, 0.9902, 1.0537]; ph_TW = [1.5285, 1.2862, 1.2203]

def part(name, kind, called, read, **kw):
    d = dict(name=name, kind=kind, called=called, read=read); d.update(kw); return d

def band_part(name, called, read, w_abs=None, unknown=False, **kw):
    return part(name, 'band', called, read, w_abs=w_abs, unknown=unknown, **kw)

def ratio_part(name, called, vals):
    return band_part(name, called, st.mean(vals), w_abs=sd(vals))

R = {}
R[1] = dict(file='five_slope.py (frozen script; code_20261004/five_slope.py)', sha='0e245906ff3519c1', cat='land', outcome='LAND',
  hashed='No width stated in the hashed script ("keeps its slope"; called depths -0.12/-0.58/-0.97 % at 2/6/10 pushes). Ledger §203 (not hashed): "within about one combined width of Pittsburgh\'s, depth below zero from 6 pushes"',
  wstatus='ASSUMED', rule='min',
  src='THIRD_RUNG_20260928.md:2137-2141 (§203): Pittsburgh -0.00106 +- ~0.0008, Fez -0.00182 +- 0.00027, width = sqrt(0.0008^2+0.00027^2); five_slope.py:1-4',
  parts=[band_part('slope per push', -0.00106, -0.00182, w_abs=math.hypot(0.0008, 0.00027)),
         part('depth below zero at 6 pushes', 'sign', 0, -0.0050, held=True)],
  note='Width not in the hash; taken from ledger §203 wording and the quoted +- values (0.9 widths, as the paper). Slope band covers w=0.80 of the called value, so the band part is capped at 1. Sign part 0.5 (read -0.0050 at 6 pushes). Slope and depth are one measurement: min rule.')
R[2] = dict(file='five_slope_kingston2.py (frozen script; code_20261004/five_slope_kingston2.py)', sha='d087500138bcddba', cat='edge', outcome='MISS',
  hashed='No width stated in the hashed script; ledger §235 (not hashed): "each within ~1 combined width of Pittsburgh"',
  wstatus='ASSUMED', rule='min',
  src='THIRD_RUNG_20260928.md:2284-2288 (§235): Kingston -0.00198 +- 0.00035, width = sqrt(0.0008^2+0.00035^2); five_slope_kingston2.py:1-4',
  parts=[band_part('slope per push', -0.00106, -0.00198, w_abs=math.hypot(0.0008, 0.00035)),
         part('depth below zero at 6 pushes', 'sign', 0, -0.0067, held=True)],
  note='1.05 widths: on the edge, strict MISS. Width assumed as for row 1. Band part capped at 1 (w=0.82); sign 0.5; min rule.')
R[3] = dict(file='TWO_CALL_CEPHEUS_20261004.txt', sha='8156c88650870b97', cat='miss', outcome='MISS',
  hashed='None. The hashed file states five sizes and no landing criterion or width; Table 17\'s header (one combined width) is the paper\'s, not the file\'s',
  wstatus='UNKNOWN', rule='product',
  src='calls/TWO_CALL_CEPHEUS_20261004.txt:5-9; read: standoff/time20261004/two_raw.txt (ALL, OFF g lines); THIRD_RUNG_20260928.md:2273 (§232)',
  parts=[band_part('1.000 us', 8.33, 0.42, unknown=True), band_part('2.618 us', 5.15, 2.46, unknown=True),
         band_part('6.854 us', 3.18, 1.74, unknown=True), band_part('17.944 us', 1.97, 0.80, unknown=True),
         band_part('46.979 us', 1.22, -1.98, unknown=True)],
  note='Units: percent excess over own decay. No width in the hash. Copy-to-copy spreads in two_raw.txt differ by spacing and are not the call\'s width. At every w up to 10 % all five parts miss by more than the width. Product over five spacings (distinct quantities); the min rule would give 0.029 (w=2 %) / 0.145 (w=10 %).')
R[4] = dict(file='IBM_FEZ_CALLS_20261004.txt', sha='dad0ff67e62953ed', cat='miss', outcome='MISS',
  hashed='"within one combined width (reads\' spread and resampling)"',
  wstatus='DERIVED', rule='product',
  src='calls/IBM_FEZ_CALLS_20261004.txt:2-3,9; read: reads_20261004/time_wide_fez_reads123_20261004.txt (OFF spread @ N us minus ONE, copies a/b/c, lines 34/48/62/69, 233/247/261/268, 432/446/460/467); THIRD_RUNG_20260928.md:2302-2306 (§239)',
  parts=[band_part('10 us', 3.18, fez[10][0], w_abs=fez[10][1]), band_part('30 us', 1.97, fez[30][0], w_abs=fez[30][1]),
         band_part('70 us', 1.22, fez[70][0], w_abs=fez[70][1]), band_part('100 us', 0.75, fez[100][0], w_abs=fez[100][1])],
  note='Units: percent. Width computed from the file: sqrt(sd of the three read means^2 + mean resampling^2), each read = mean of copies a/b/c. Reproduces the ledger\'s 5.99/3.08/1.69/1.43 (+-0.3-0.4). Product over four spacings; min rule would give the largest single part.')
R[5] = dict(file='IBM_FEZ_CALLS_20261004.txt', sha='dad0ff67e62953ed', cat='miss', outcome='MISS',
  hashed='"within one combined width (reads\' spread and resampling)", each of three ratios',
  wstatus='DERIVED', rule='min',
  src='calls/IBM_FEZ_CALLS_20261004.txt:4,9; read: reads_20261004/look_3and9_fez_20261004.txt:1-3 (3-and-9 W/O, T/O, T/W); width = sample sd of the three reads (as the paper scores); THIRD_RUNG_20260928.md:2302-2306',
  parts=[ratio_part('witness/maker', 1.09, fez_WO), ratio_part('qubit/maker', 1.62, fez_TO), ratio_part('qubit/witness', 1.48, fez_TW)],
  note='Resampling width is not printed for the ratios; read spread only (as in the paper\'s "2.6 widths"). T/O = (T/W)(W/O) exactly, so the three parts are not independent: min rule.')
R[6] = dict(file='IBM_FEZ_CALLS_20261004.txt', sha='dad0ff67e62953ed', cat='land', outcome='LAND',
  hashed='"within one combined width (reads\' spread and resampling)"',
  wstatus='DERIVED', rule='single',
  src='calls/IBM_FEZ_CALLS_20261004.txt:6,9; read: reads_20261004/look_3and9_fez_20261004.txt:1-3 (T/W 1.3438/1.8079/1.3746); THIRD_RUNG_20260928.md:2302-2304 (§239)',
  parts=[ratio_part('qubit/witness', 1.5, fez_TW)],
  note='Width = read spread 0.26 (sd of three reads); resampling not folded in. The width is 17 % of the called value.')
R[7] = dict(file='IBM_FEZ_CALLS_20261004.txt', sha='dad0ff67e62953ed', cat='miss', outcome='MISS',
  hashed='"within one combined width (reads\' spread and resampling)"',
  wstatus='DERIVED', rule='single',
  src='calls/IBM_FEZ_CALLS_20261004.txt:7-9; read: THIRD_RUNG_20260928.md:2305-2306 (§239: 0.872/0.855/0.807, mean 0.844); width = sd of the three reads',
  parts=[band_part('hand kept 27 looks / laid time', 0.750, 0.844, w_abs=sd(fez_cnt))],
  note='Per-read values from ledger text (three digits); the per-read file for the fez count is not in the release data. Mean taken as the printed 0.844.')
bo = st.mean(bos_WO) / R1211
R[8] = dict(file='GOD_TAX_CALL_BOSTON_20261004.txt', sha='47a0377895b3a632', cat='miss', outcome='MISS',
  hashed='Outside leg: "below 1 by more than one combined width (read spread and resampling)". Inside leg: "within +-3 % of 1"',
  wstatus='DERIVED', rule='product',
  src='calls/GOD_TAX_CALL_BOSTON_20261004.txt:3-4; read: out/qubit_fifth_run/data/reads/look_3and9_boston_20261004.txt:1-3; THIRD_RUNG_20260928.md:2371-2375 (§254)',
  parts=[part('outside leg (W/O)/(12/11)', 'below', 1.0, bo, ref=1.0, width=sd(bos_WO) / R1211),
         band_part('inside leg (T/W)/(phi x 11/12), called 1', 1.0, st.mean(bos_TW) / K1483, w_abs=0.03)],
  note='Outside-leg width = sd of three W/O reads / (12/11) = 0.038 (spread only; resampling not printed). Threshold = 1 - width; interval [0.5,2]. Inside leg stated +-3 %. The legs are different ratios and are multiplied; both contain W, so the min rule (0.043) is given as the alternative. Read 0.988 is 0.3 widths below 1.')
R[9] = dict(file='ONE_SIX_CALL_BOSTON_20261004.txt', sha='bd7b491793c91d75', cat='miss', outcome='MISS',
  hashed='"each within one combined width (read spread and resampling)"',
  wstatus='DERIVED', rule='min',
  src='calls/ONE_SIX_CALL_BOSTON_20261004.txt:3-4; read: out/qubit_fifth_run/data/reads/look_3and9_boston_20261004.txt:1-3; THIRD_RUNG_20260928.md:2371-2373 (§254)',
  parts=[ratio_part('witness/maker', 1.09, bos_WO), ratio_part('qubit/maker', 1.62, bos_TO), ratio_part('qubit/witness', 1.48, bos_TW)],
  note='Widths = sd of three reads (0.042 / 0.136 / 0.096), reproduces §254. Resampling not folded in. Parts algebraically linked (T/O = T/W x W/O): min rule.')
R[10] = dict(file='ONE_SIX_CALL_BOSTON_20261004.txt', sha='bd7b491793c91d75', cat='miss', outcome='MISS',
  hashed='"within one combined width"',
  wstatus='DERIVED', rule='single',
  src='calls/ONE_SIX_CALL_BOSTON_20261004.txt:4; read: out/qubit_fifth_run/data/reads/look_3and9_boston_20261004.txt:1-3; THIRD_RUNG_20260928.md:2373 (§254: 2.6 widths)',
  parts=[ratio_part('qubit/witness', 1.5, bos_TW)],
  note='Width = sd of three T/W reads (0.096).')
w11 = math.hypot(0.00029, math.hypot(0.00027, 0.00035) / 2)
R[11] = dict(file='FIVE_THREE_CALL_BOSTON_20261004.txt', sha='bfe1b824ccf45368', cat='partly', outcome='MISS',
  hashed='"within one combined width of the ibm_fez / ibm_kingston mean, -0.00190"; sign clauses need no width',
  wstatus='DERIVED', rule='min',
  src='calls/FIVE_THREE_CALL_BOSTON_20261004.txt:2-3; read: out/qubit_fifth_run/data/reads/five_slope_boston_20261004.txt (own interval 6 pushes -0.00354; slope -0.00139 +- 0.00029; 90-us -0.00148; one exp -0.00139); THIRD_RUNG_20260928.md:2394-2398 (§258: 1.4 widths)',
  parts=[part('depth below zero at 6 pushes', 'sign', 0, -0.0035, held=True),
         part('slope negative under all three rulers', 'sign', 0, -0.00139, held=True),
         band_part('own-interval slope vs -0.00190', -0.00190, -0.00139, w_abs=w11)],
  note='Width = sqrt(0.00029^2 + sigma_mean^2), sigma_mean = sqrt(0.00027^2+0.00035^2)/2 for the fez/kingston mean; gives the printed 1.4 widths. First two clauses hold, third misses: strict MISS. Same slope under three rulers and the depth: min rule (product would be 0.07).')
R[12] = dict(file='FIVE_THREE_CALL_BOSTON_20261004.txt', sha='bfe1b824ccf45368', cat='miss', outcome='MISS',
  hashed='"within one combined width (the reads\' spread)"',
  wstatus='UNKNOWN', rule='single',
  src='calls/FIVE_THREE_CALL_BOSTON_20261004.txt:4-5; read: reads_20261005/three_looks_minus_time_boston_20261005.txt (32 looks 1.000/0.901/0.991 by class; mean of 3 reads only); THIRD_RUNG_20260928.md:2394-2398',
  parts=[band_part('hand kept 32 looks / laid time', 0.750, 0.991, unknown=True)],
  note='The reads\' spread for the 32-look median is not printed in any file (the file gives means of three reads per class; the paper row gives no N widths). Raw job results exist (fire/ibm_boston/run451-453) but the reader was lost (§258) and was not rebuilt. Read 0.991 is the median of the three class values. Misses for any width under 0.24 (32 %).')
R[13] = dict(file='BONEFISH_NUMBERS_BOSTON_20261004.txt', sha='89397820188cf2a9', cat='miss', outcome='MISS',
  hashed='"lands if the fitted pace sits within 0.073 + its own fit width"',
  wstatus='HASHED', rule='single',
  src='calls/BONEFISH_NUMBERS_BOSTON_20261004.txt:2-3; read: THIRD_RUNG_20260928.md:2400-2403 (§259: 1.217 +- 0.104)',
  parts=[band_part('ladder pace (rungs/e-fold)', 0.921, 1.217, w_abs=0.073 + 0.104)],
  note='Width 0.073 (hashed scatter) + 0.104 (fit width of the read). 1.67 widths. On the fit width alone: 2.85.')
R[14] = dict(file='BONEFISH_NUMBERS_BOSTON_20261004.txt', sha='89397820188cf2a9', cat='edge', outcome='MISS',
  hashed='"within one width" (not defined further)',
  wstatus='DERIVED', rule='single',
  src='calls/BONEFISH_NUMBERS_BOSTON_20261004.txt:4-5; read: out/qubit_fifth_run/data/reads/five_slope_boston_20261004.txt (slope -0.00139 +- 0.00029); THIRD_RUNG_20260928.md:2394-2398 (§258: 1.0 width)',
  parts=[band_part('own-interval slope per push (rung 9)', -0.00110, -0.00139, w_abs=0.00029)],
  note='Width = the read\'s printed +-0.00029. Distance 0.00029 = 1.0 widths: on the edge, strict MISS.')
R[15] = dict(file='TOMORROW_CALLS_20261005.txt', sha='eb98f85caf8e170c', cat='lands-with-spread', outcome='MISS',
  hashed='"within one combined width (round spread and resampling)" (hashed). The readout-model spread was added after (ledger §257)',
  wstatus='HASHED', rule='single',
  src='calls/TOMORROW_CALLS_20261005.txt:3-5; read: standoff/time20261004/sealA_band_two_days_20261005.txt:5 (day 2 rounds 0.6382/0.6313/0.6243, mean 0.6313, combined 0.0064, +2.08 widths); THIRD_RUNG_20260928.md:2384-2392 (§256, §257: readout-model combined 0.025, 0.53 widths)',
  parts=[band_part('emitters |2> at 4 us, others half-way', 0.618, 0.6313, w_abs=0.0064, w_alt=0.025)],
  note='Hashed width 0.0064 (round spread and refit resampling): 2.08 widths, MISS. With the readout-model spread counted, width 0.025 (w_rel 0.040, p 0.058): 0.53 widths, lands. Hashed width used for the strict column.')
R[16] = dict(file='PHOENIX_CALL_20261005.txt', sha='93514fc06e84f143', cat='land', outcome='LAND',
  hashed='"spectator / maker below 12/11 (the maker look), printed with its width" (threshold only)',
  wstatus='HASHED', rule='single',
  src='calls/PHOENIX_CALL_20261005.txt:6; read: reads_20261005/look_3and9_phoenix_20261005.txt:1-3 (W/O 0.9775/0.9902/1.0537); THIRD_RUNG_20260928.md:2408-2412 (§261)',
  parts=[part('spectator/maker below 12/11', 'below', R1211, st.mean(ph_WO), ref=R1211, width=sd(ph_WO))],
  note='Interval [0.5,2] (ratio around 1). With [called/2, 2 x called] = [0.545,2.182] the threshold fraction is exactly 0.5. Read 1.0071 is 2.05 widths (sd of three reads 0.041) below 12/11. Phoenix row.')
R[17] = dict(file='PHOENIX_CALL_20261005.txt', sha='93514fc06e84f143', cat='miss', outcome='MISS',
  hashed='"within +-4 % of phi x 11/12 = 1.4832" (no clock-ratio factor)',
  wstatus='HASHED', rule='single',
  src='calls/PHOENIX_CALL_20261005.txt:5; read: reads_20261005/look_3and9_phoenix_20261005.txt:1-3 (T/W 1.5285/1.2862/1.2203); THIRD_RUNG_20260928.md:2408-2412 (§261)',
  parts=[band_part('qubit/spectator', K1483, st.mean(ph_TW), w_abs=0.04 * K1483)],
  note='Mean of three reads 1.345 is -9.3 %; read 1 alone (1.5285, +3.1 %) is inside. Strict rule uses the three-read mean. Phoenix row.')
w18 = math.hypot(0.00030, sd([0.00058, 0.00091, 0.00155]))
R[18] = dict(file='PHOENIX_CALL_20261005.txt', sha='93514fc06e84f143', cat='partly', outcome='MISS',
  hashed='"within one combined width of rung 8 = -0.00177; below zero from 6 pushes; negative under all three rulers" with "every ruler in the width"',
  wstatus='DERIVED', rule='min',
  src='calls/PHOENIX_CALL_20261005.txt:4,8; read: reads_20261005/five_slope_phoenix_20261005.txt; THIRD_RUNG_20260928.md:2408-2412 (§261: -0.00058 +- 0.00030 own, -0.00091, -0.00155; +0.0019 at 6; 2.1 widths)',
  parts=[band_part('own-interval slope vs rung 8', -0.00177, -0.00058, w_abs=w18),
         part('depth below zero at 6 pushes', 'sign', 0, 0.0019, held=False),
         part('negative under all three rulers', 'sign', 0, -0.00058, held=True)],
  note='Width = sqrt(0.00030^2 + sd of the three ruler slopes^2) = 0.00058 -> 2.06 widths (ledger: 2.1). Slope and depth miss; ruler-sign holds. Parts are one slope read three ways: min rule. Phoenix row.')
R[19] = dict(file='PHOENIX_CALL_20261005.txt', sha='93514fc06e84f143', cat='unreadable', outcome='EXCLUDED',
  hashed='"within one combined width of 9/12 = 0.750"',
  wstatus='UNKNOWN', rule='single', excluded=True,
  src='calls/PHOENIX_CALL_20261005.txt:7; THIRD_RUNG_20260928.md:2408-2415 (§261: floor over floor, kept 0.07-0.23 by 12-16 looks)',
  parts=[band_part('hand kept 32 looks / laid time', 0.750, None, unknown=True)],
  note='Unreadable by this ruler (the free clocks reach the floor). Excluded from S, H and the tail. If it were scored the p would be 0.029 (w=2 %) to 0.145 (w=10 %). Phoenix row.')
w20 = 0.049 / 2.18 / R1211
x20 = 1.0639 / R1211
R[20] = dict(file='TOMORROW_CALLS_20261005.txt', sha='eb98f85caf8e170c', cat='land', outcome='LAND',
  hashed='"below 1 by more than one resampling width" (ibm_pittsburgh, 5 Oct)',
  wstatus='DERIVED', rule='single',
  src='calls/TOMORROW_CALLS_20261005.txt:2-3; read: reads_20261005/look_3and9_pittsburgh_oct5_20261005.txt:1 (W 3-and-9 2.319 +- 0.049 us, maker 2.18, W/O 1.0639); THIRD_RUNG_20260928.md:2447-2452 (§269: 1.2 widths)',
  parts=[part('(spectator/maker)/(12/11)', 'below', 1.0, x20, ref=1.0, width=w20)],
  note='Width = resampling width of W/maker = 0.049/2.18/(12/11) = 0.0206 (the hashed wording is "one resampling width"). Threshold 1 - width, interval [0.5,2]. The 1-9 fit read 0.964 is not used.')
R[21] = dict(file='TIME_LEG_T2T1_CALL_20261005.txt', sha='abcc6db23328e666', cat='miss', outcome='MISS',
  hashed='"within +-4 % of 1.4832" for (T/W) x max(1, T2:T1)',
  wstatus='HASHED', rule='single',
  src='calls/TIME_LEG_T2T1_CALL_20261005.txt:5-6; read: reads_20261005/look_3and9_pittsburgh_oct5_20261005.txt:1 (T/W 1.2168 x T2:T1 1.138 = 1.385; 1-9 fit 1.2886 x 1.138 = 1.466); THIRD_RUNG_20260928.md:2447-2452 (§269)',
  parts=[band_part('(T/W) x max(1,T2:T1)', K1483, 1.2168 * 1.138, w_abs=0.04 * K1483)],
  note='-6.6 % on the 3-and-9 slope (0.7 of the read\'s own width, T +- 0.27 us); the 1-9 fit gives -1.1 %. Strict rule: the 3-and-9 value named in the call text. One read.')

# ---------------- COMPUTE ----------------
def eval_part(p, wover=None):
    k = p['kind']; out = {}
    if k == 'band':
        c, r = p['called'], p['read']
        unknown = p.get('unknown') and wover is None
        w_abs = None if unknown else (wover * abs(c) if wover is not None else p.get('w_abs'))
        out['w_abs'] = w_abs
        out['w_rel'] = None if unknown else w_abs / abs(c)
        out['p_chance'] = None if unknown else p_band(w_abs / abs(c))
        if r is not None:
            d = abs(r / c - 1)
            out['d_rel'] = d
            out['d_widths'] = None if unknown else abs(r - c) / w_abs
            out['p_close'] = p_band(d)
        else:
            out['d_rel'] = out['d_widths'] = out['p_close'] = None
        if p.get('w_alt'):
            out['p_chance_alt'] = p_band(p['w_alt'] / abs(c)); out['d_widths_alt'] = abs(r - c) / p['w_alt']
    elif k == 'below':
        ref, width, r = p['ref'], p['width'], p['read']
        norm = abs(ref - 1.0) < 1e-9
        thr = ref - width if norm else ref
        out['w_abs'] = width if norm else None
        out['w_rel'] = width / ref if norm else None
        out['p_chance'] = p_below(thr)
        out['d_rel'] = abs(r / ref - 1)
        out['d_widths'] = (ref - r) / width
        out['p_close'] = p_below(r)
    else:
        out['w_abs'] = out['w_rel'] = out['d_rel'] = out['d_widths'] = None
        out['p_chance'] = 0.5
        out['p_close'] = 0.5 if p['held'] else 1.0
    return out

def combine(vals, rule):
    if rule == 'product':
        pr = 1.0
        for v in vals: pr *= v
        return pr
    return min(vals)

def row_eval(n, wover=None, force_rule=None, assumed_over=None):
    r = R[n]; ev = []
    for p in r['parts']:
        wo = None
        if p.get('unknown'): wo = wover
        elif assumed_over is not None and r['wstatus'] == 'ASSUMED' and p['kind'] == 'band': wo = assumed_over
        ev.append(eval_part(p, wo))
    rule = force_rule or r['rule']
    if rule == 'single': rule = 'min'
    pc = combine([e['p_chance'] for e in ev], rule) if all(e['p_chance'] is not None for e in ev) else None
    pcl = combine([e['p_close'] for e in ev], rule) if all(e['p_close'] is not None for e in ev) else None
    return ev, pc, pcl

def p_for(n, wunk=0.10, force_rule=None, assumed=None):
    if R[n].get('excluded'): return None
    if R[n]['wstatus'] == 'UNKNOWN':
        return row_eval(n, wover=wunk, force_rule=force_rule)[1]
    return row_eval(n, force_rule=force_rule, assumed_over=assumed)[1]

def pb_tail(ps, H):
    dp = [1.0] + [0.0] * len(ps)
    for p in ps:
        nd = [0.0] * (len(ps) + 1)
        for k in range(len(ps) + 1):
            if dp[k] == 0: continue
            nd[k] += dp[k] * (1 - p)
            if k + 1 <= len(ps): nd[k + 1] += dp[k] * p
        dp = nd
    return sum(dp[H:])

def fisher(pcs):
    k = len(pcs); x = -2 * sum(math.log(p) for p in pcs)
    h = x / 2; s = sum(h ** i / math.factorial(i) for i in range(k))
    return x, math.exp(-h) * s, k

ALL = [n for n in range(1, 22) if not R[n].get('excluded')]
NOPH = [n for n in ALL if n not in (16, 17, 18, 19)]
def landset(ns): return sum(1 for n in ns if R[n]['outcome'] == 'LAND')

def S_tail(ns, **kw):
    ps = [p_for(n, **kw) for n in ns]
    H = landset(ns)
    return sum(ps), H, pb_tail(ps, H)

results = {}
for lab, ns in (('all', ALL), ('noph', NOPH)):
    results[lab] = dict(
        head=S_tail(ns, wunk=0.10), low=S_tail(ns, wunk=0.02), high=S_tail(ns, wunk=0.10),
        assumed_low=S_tail(ns, wunk=0.02, assumed=0.02), assumed_high=S_tail(ns, wunk=0.10, assumed=0.10),
        allmin=S_tail(ns, wunk=0.10, force_rule='min'), allprod=S_tail(ns, wunk=0.10, force_rule='product'))

table = []
for n in range(1, 22):
    r = R[n]
    ev_base, pc_base, pcl = row_eval(n)
    if r['wstatus'] == 'UNKNOWN':
        ev10, pc10, _ = row_eval(n, wover=0.10); ev02, pc02, _ = row_eval(n, wover=0.02)
    else:
        ev10, pc10, pc02 = ev_base, pc_base, None
    table.append((n, r, ev_base, pc10, pc02, pcl, ev10))

def fish(ns):
    pcs = [t[5] for t in table if t[0] in ns]
    x, pv, k = fisher(pcs)
    return dict(pcs=sorted(pcs), x=x, p=pv, k=k, lt=sum(1 for p in pcs if p < 0.5), expect=k / 2)
F_all = fish(ALL); F_noph = fish(NOPH)

def cats(ns):
    c = {}
    for n in ns: c[R[n]['cat']] = c.get(R[n]['cat'], 0) + 1
    return c
CAT_all = cats(range(1, 22))
CAT_noph = cats([n for n in range(1, 22) if n not in (16, 17, 18, 19)])

def fmt(x, nd=4):
    if x is None: return ''
    if isinstance(x, str): return x
    if x != 0 and abs(x) < 1e-3: return '%.3e' % x
    return ('%.' + str(nd) + 'g') % x

def sci(x):
    if x is None: return 'n/a'
    return ('%.3e' % x) if x < 1e-3 else ('%.4f' % x)

def joinf(vals, nd=4): return ' | '.join(fmt(v, nd) if v is not None else '-' for v in vals)

csvp = '/Users/heuremen/bones-forge/parallax/darkwave_disco/arxiv/CHANCE_TABLE_20261005.csv'
cols = ['row', 'paper_category', 'd_rel', 'd_widths', 'p_close_parts', 'p_close', 'p_close_rule',
        'call_file', 'sha16', 'called', 'read', 'width_as_hashed', 'w_abs', 'w_rel', 'width_status', 'width_source',
        'outcome_strict', 'p_chance', 'p_chance_w2pct', 'p_chance_w10pct', 'p_chance_parts', 'p_basis', 'note']
csvrows = []; mdrows = []
for n, r, ev, pc10, pc02, pcl, ev10 in table:
    parts = r['parts']
    called = ' | '.join(('%s: %s' % (p['name'], fmt(p['called'], 6))) if p['kind'] != 'sign' else ('%s: sign negative' % p['name']) for p in parts)
    reads_ = ' | '.join(fmt(p['read'], 6) if p['read'] is not None else 'unreadable' for p in parts)
    unk = r['wstatus'] == 'UNKNOWN'
    if unk:
        w_abs_s = 'UNKNOWN (2 % / 10 % of called: ' + ' | '.join('%s / %s' % (fmt(0.02 * abs(p['called']), 3), fmt(0.10 * abs(p['called']), 3)) for p in parts) + ')'
        w_rel_s = 'UNKNOWN (0.02 / 0.10)'; dw = 'UNKNOWN'
        pcp = joinf([e['p_chance'] for e in ev10], 4) + ' (w=10 %)'
    else:
        w_abs_s = joinf([e['w_abs'] for e in ev]); w_rel_s = joinf([e['w_rel'] for e in ev])
        if n == 16:
            w_abs_s = 'none stated (threshold only); read sd of three W/O reads 0.0408 used for d_widths'; w_rel_s = 'none stated (0.0374 of 12/11 if the read sd is used)'
        dw = joinf([e['d_widths'] for e in ev], 3)
        pcp = joinf([e['p_chance'] for e in ev], 4)
    dr = joinf([e['d_rel'] for e in ev], 4)
    pcl_parts = joinf([e['p_close'] for e in ev], 4)
    rule = r['rule'] if len(parts) > 1 else 'single part'
    kinds = []
    for p in parts:
        if p['kind'] == 'band': kinds.append('two-sided ratio within +-w: ln((1+w)/(1-w))/ln4, interval [called/2, 2 x called]')
        elif p['kind'] == 'below':
            kinds.append('one-sided: fraction of log-uniform [0.5,2] below %s' % ('1 - width' if abs(p['ref'] - 1) < 1e-9 else '12/11 (=%.4f)' % R1211))
        else: kinds.append('sign: 0.5')
    basis = '; '.join(dict.fromkeys(kinds)) + ('; parts combined by %s rule' % rule if len(parts) > 1 else '')
    excl = r.get('excluded')
    csvrows.append(dict(row=n, paper_category=r['cat'], d_rel=dr, d_widths=dw, p_close_parts=pcl_parts, p_close=fmt(pcl, 5),
        p_close_rule=rule, call_file=r['file'], sha16=r['sha'], called=called, read=reads_, width_as_hashed=r['hashed'],
        w_abs=w_abs_s, w_rel=w_rel_s, width_status=r['wstatus'], width_source=r['src'], outcome_strict=r['outcome'],
        p_chance='EXCLUDED' if excl else fmt(pc10, 5), p_chance_w2pct=fmt(pc02, 4) if unk else '', p_chance_w10pct=fmt(pc10, 4) if unk else '',
        p_chance_parts=pcp, p_basis=basis, note=r['note']))
    mdrows.append((n, r, dr, dw, pcl_parts, pcl, rule, called, reads_, w_abs_s, w_rel_s, pc10, pc02, pc10, pcp, unk, basis))

with open(csvp, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for rr in csvrows: w.writerow(rr)

ra, rn = results['all'], results['noph']
L = []
L.append('# Per-call chance table, 5 October 2026')
L.append('')
L.append('Sources: calls/*.txt (sha256 checked against the printed first 16 hex), the Table 17 rows of MEASUREMENT_PAPER_20261004.md (line 426 on), the read files under parallax/out/qubit_fifth_run/data/reads, for_indahl_ai/data/reads_20261004, reads_20261005, standoff/time20261004, and THIRD_RUNG_20260928.md §203-§269. Null: the read is log-uniform over a factor of two either side of the called value. Built by /tmp/chance_table_build.py.')
L.append('')
L.append('Column order: the continuous score first (d_rel, d_widths, p_close), then the paper\'s six-category verdict, then the strict binary outcome and p_chance. Parts of a multi-part call are listed with " | ". width_status: HASHED = number or percent in the hashed text; DERIVED = hashed wording ("one combined width") with the number taken from the read files; ASSUMED = the hashed text states no width and one was taken from the ledger; UNKNOWN = no width found.')
L.append('')
L.append('## Table 1: continuous score, paper category, strict outcome, chance')
L.append('')
L.append('| row | d_rel (per part) | d_widths (per part) | p_close (per part) | p_close (row; rule) | paper category | strict | p_chance (row) | p_chance (per part) | width_status |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
for (n, r, dr, dw, pclp, pcl, rule, called, reads_, wa, wr, pm, plo, phi, pcp, unk, basis) in mdrows:
    pch = 'excluded' if r.get('excluded') else (('%s (UNKNOWN: %s at 2 %%, %s at 10 %%)' % (sci(pm), sci(plo), sci(phi))) if unk else sci(pm))
    L.append('| %d | %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s |' % (n, dr, dw, pclp, sci(pcl), rule, r['cat'], r['outcome'], pch, pcp, r['wstatus']))
L.append('')
L.append('## Table 2: calls, numbers, widths, sources')
L.append('')
L.append('| row | call file | sha16 | called | read | width as hashed | w_abs | w_rel | width source | p_basis | note |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|')
for (n, r, dr, dw, pclp, pcl, rule, called, reads_, wa, wr, pm, plo, phi, pcp, unk, basis) in mdrows:
    L.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n, r['file'], r['sha'], called, reads_, r['hashed'].replace('|', '/'), wa, wr, r['src'].replace('|', '/'), basis, r['note'].replace('|', '/')))
L.append('')
rowname = {t[0]: t[5] for t in table}
def sorted_list(ns): return ', '.join('row %d: %s' % (n, sci(rowname[n])) for n in sorted(ns, key=lambda n: rowname[n]))
L.append('## Continuous score: sorted p_close')
L.append('')
L.append('All %d readable rows, ascending: %s.' % (len(ALL), sorted_list(ALL)))
L.append('')
L.append('Without Phoenix (%d rows), ascending: %s.' % (len(NOPH), sorted_list(NOPH)))
L.append('')
L.append('| set | k | X2 = -2 sum ln p_close | chi-square p at 2k df | rows with p_close < 0.5 | k/2 |')
L.append('|---|---|---|---|---|---|')
L.append('| all readable rows | %d | %.3f | %s | %d | %.1f |' % (F_all['k'], F_all['x'], sci(F_all['p']), F_all['lt'], F_all['expect']))
L.append('| without Phoenix (rows 16-19) | %d | %.3f | %s | %d | %.1f |' % (F_noph['k'], F_noph['x'], sci(F_noph['p']), F_noph['lt'], F_noph['expect']))
L.append('')
L.append('## Strict binary against summed chance')
L.append('')
L.append('| set | rows scored | H (LAND) | S = sum p_chance | P(X >= H), exact Poisson-binomial |')
L.append('|---|---|---|---|---|')
L.append('| all rows (UNKNOWN rows 3, 12 at the 10 %% bound) | %d | %d | %.4f | %s |' % (len(ALL), ra['head'][1], ra['head'][0], sci(ra['head'][2])))
L.append('| without Phoenix (rows 16-19) | %d | %d | %.4f | %s |' % (len(NOPH), rn['head'][1], rn['head'][0], sci(rn['head'][2])))
L.append('')
L.append('Sensitivity of S and P(X >= H):')
L.append('')
L.append('| variant | all rows S | all rows P | without Phoenix S | without Phoenix P |')
L.append('|---|---|---|---|---|')
def line(lab, key):
    L.append('| %s | %.4f | %s | %.4f | %s |' % (lab, ra[key][0], sci(ra[key][2]), rn[key][0], sci(rn[key][2])))
line('UNKNOWN rows (3, 12) at w = 2 %', 'low')
line('UNKNOWN rows (3, 12) at w = 10 %', 'high')
line('UNKNOWN rows and ASSUMED rows (1, 2) at w = 2 %', 'assumed_low')
line('UNKNOWN rows and ASSUMED rows (1, 2) at w = 10 %', 'assumed_high')
line('every multi-part row by min rule (UNKNOWN at 10 %)', 'allmin')
line('every multi-part row by product rule (UNKNOWN at 10 %)', 'allprod')
L.append('')
def catline(c):
    order = ['land', 'edge', 'partly', 'lands-with-spread', 'miss', 'unreadable']
    return ', '.join('%d %s' % (c.get(k, 0), k) for k in order if c.get(k, 0))
L.append('## Summary sentences')
L.append('')
s1 = 'In the paper\'s six categories the 21 rows are %s; without rows 16-19 the 17 rows are %s.' % (catline(CAT_all), catline(CAT_noph))
s2 = 'On the continuous score, p_close over the %d readable rows has X2 = %.2f (chi-square p = %s at %d degrees of freedom) with %d rows below 0.5 where %.1f are expected by chance, and over the %d rows without Phoenix X2 = %.2f (p = %s at %d degrees of freedom) with %d rows below 0.5 where %.1f are expected.' % (
    F_all['k'], F_all['x'], sci(F_all['p']), 2 * F_all['k'], F_all['lt'], F_all['expect'], F_noph['k'], F_noph['x'], sci(F_noph['p']), 2 * F_noph['k'], F_noph['lt'], F_noph['expect'])
s3 = 'On the strict binary column H = %d of %d readable rows landed against S = %.2f summed chance with P(X >= H) = %s, and without Phoenix H = %d of %d against S = %.2f with P(X >= H) = %s (UNKNOWN widths of rows 3 and 12 at their 10 %% bound).' % (
    ra['head'][1], len(ALL), ra['head'][0], sci(ra['head'][2]), rn['head'][1], len(NOPH), rn['head'][0], sci(rn['head'][2]))
s4 = 'With the UNKNOWN widths of rows 3 and 12 set to 2 %% and to 10 %%, S runs %.2f to %.2f and P(X >= H) runs %s to %s over all rows, and S runs %.2f to %.2f and P(X >= H) runs %s to %s without Phoenix.' % (
    ra['low'][0], ra['high'][0], sci(ra['low'][2]), sci(ra['high'][2]), rn['low'][0], rn['high'][0], sci(rn['low'][2]), sci(rn['high'][2]))
for s in (s1, s2, s3, s4):
    L.append(s); L.append('')
L.append('## Assumptions and flags')
L.append('')
L.append('- UNKNOWN: row 3 (the hashed file states no criterion or width), row 12 (the reads\' spread of the 32-look median is not printed in any file; raw job results exist but the reader was lost, §258), row 19 (unreadable, excluded). For rows 3 and 12 p is given as a range at w = 2 % and 10 %; the headline S and P use the 10 % bound.')
L.append('- ASSUMED: rows 1 and 2 (the hashed frozen scripts say "keeps its slope" with no number or width; the width is the ledger\'s "about one combined width", computed as sqrt(0.0008^2 + read sigma^2) from the Pittsburgh +- ~0.0008 and the read\'s +-). The called slope -0.00106 is the ledger\'s value for the hashed depths -0.12 / -0.58 / -0.97 %.')
L.append('- DERIVED widths (hashed wording gives "one combined width"; the number is from the read files): rows 4-11, 13, 14, 18, 20. Ratio rows 5-10 use the sample sd of the three reads (the paper\'s own scoring; resampling widths are not printed for ratios, §254). Row 4 adds the mean resampling width in quadrature. Row 11 adds the called value\'s own spread and row 18 the three-ruler spread, as the ledger does.')
L.append('- Row 15: the hashed width is round spread plus refit resampling, 0.0064 (2.08 widths); with the readout-model spread, 0.025 (0.53 widths). The strict column and p_chance use 0.0064.')
L.append('- Rows 1, 2, 5, 9, 11, 18 (one measurement read several ways, or algebraically linked ratios): parts combined by the min rule, the largest joint chance the parts allow. Rows 3, 4, 8 (distinct quantities): product. The sensitivity table gives S and P with every multi-part row on the min rule and on the product rule.')
L.append('- Band parts with w >= 0.6 (rows 1, 2 slope bands) are capped at 1 by the stated formula; against the null interval [0.5x, 2x] the exact value is 0.92.')
L.append('- Row 16 interval [0.5, 2] (ratio around 1); with [called/2, 2 x called] the p is 0.5000. Rows 8 and 20 outside legs are one-sided on the ratio normalised by 12/11, threshold 1 - width, interval [0.5, 2]. p_close for one-sided rows is P(X <= read) on the same interval; p_close for sign parts is 0.5 if the sign held and 1 if not; p_close for band parts is the band formula at w = d_rel, capped at 1.')
L.append('- Rows 8 (inside leg), 17 and 21 d_widths use the call\'s stated percent as the unit (the paper\'s "0.7 of its own width" for row 21 uses the read\'s width).')
L.append('- Phoenix rows 16-19: the two rulers on row 18 differ 2.7x; held out in the second set of numbers.')
open('/Users/heuremen/bones-forge/parallax/darkwave_disco/arxiv/CHANCE_TABLE_20261005.md', 'w').write('\n'.join(L) + '\n')

print(json.dumps({k: {kk: [round(x, 6) if isinstance(x, float) else x for x in vv] for kk, vv in v.items()} for k, v in results.items()}, indent=1))
print('FISHER all', F_all['k'], round(F_all['x'], 3), F_all['p'], F_all['lt']); print('FISHER noph', F_noph['k'], round(F_noph['x'], 3), F_noph['p'], F_noph['lt'])
for n, r, ev, pc10, pc02, pcl, ev10 in table:
    print(n, r['outcome'], 'p_chance', None if pc10 is None else round(pc10, 5), None if pc02 is None else round(pc02, 7), 'p_close', round(pcl, 4) if pcl is not None else None,
          'dw', [None if e['d_widths'] is None else round(e['d_widths'], 2) for e in ev], 'drel', [None if e['d_rel'] is None else round(e['d_rel'], 3) for e in ev])
print(CAT_all, CAT_noph)
