# Ledger operations for HEU1 (30 Oct 2026). Each op is a list of argv for ledger.py (CHECKS placeholder = Bones's check entry).
H='heuremen.org/experiments/2026-10-22-hahn-t2/'
LR='heuremen.org/experiments/2026-10-22-length-repeat/'
RA='heuremen.org/experiments/2026-10-22-readout-audit/'
SEP='heuremen.org/experiments/2026-09-24-temporal-spatial-correlations/verify_september_output.text'
IX='site:index.html'; TS='site:technical-summary.html'; WW='site:what-we-measured.html'
HP='site:experiments/2026-10-22-hahn-t2/index.html'; LP='site:experiments/2026-10-22-length-run/index.html'
CP='site:correlations.html'; P3='site:experiments/2026-10-04-three-positions/index.html'
CR='site:experiments/calibration-records/index.html'; RP='site:experiments/2026-10-22-readout-audit/index.html'
F1='site:experiments/2026-10-22-flip-check/index.html'; JI='site:experiments/job-index/index.html'
WHY_S='HEU1-11 (30 Oct site pass): semicolon in page prose rewritten as plain punctuation; number, interval and outcome unchanged'
WHY_H='HEU1-1 (30 Oct site pass): marrakesh fresh-record Hahn run (job dbdri2npc3tc739kmgag) added to the table; range now spans three runs'
OPS = []
def offon(rid, surf, snippets, why):
    OPS.append(['off', rid, surf, '--why', why])
    for s in snippets: OPS.append(['on', rid, surf, s])
# --- 1. surfaces whose snippet changed (off, then every snippet of that row on that surface back on)
offon('bill.r10.concurrence_repeat', IX, ['+0.0051 [+0.0005, +0.0126], first run +0.0070', '0.005 to 0.009 less concurrence'], WHY_S)
offon('bill.r10.concurrence_repeat', TS, ['+0.0051 [+0.0005, +0.0126], +0.0070 in the first run', '0.005 to 0.009 less concurrence'], WHY_S)
offon('paper.distance.d34', IX, ['0.81, 1.77 and 1.30 degrees per readout (fez, kingston, marrakesh, over 15 qubits, every interval above 0)'], WHY_S)
offon('paper.distance.d34', TS, ['0.81, 1.77 and 1.30&deg; per readout (fez, kingston, marrakesh, over 15 qubits, every interval above 0)'], WHY_S)
offon('paper.distance.d34_n15', IX, ['(3.458 degrees, over 10 qubits)', 'at five or more couplings (92 qubits)'], WHY_S)
offon('paper.growth.k8_minus_k2.fez', IX, ['(+0.036, &minus;0.008, +0.294 degrees, at most 14, 6 and 24% of the kick)'], WHY_S)
offon('paper.growth.k8_minus_k2.fez', TS, ['(+0.036, &minus;0.008, +0.294&deg;, at most 14, 6 and 24% of the kick)'], WHY_S)
offon('paper.kick21.ratio_R0', IX, ['(1.17 to 1.20, plan hashed locally)'], WHY_S)
offon('paper.restart.vs72idle.fez', IX, ['+0.028 [&minus;0.038, +0.085] (ibm_fez, whose 72-idle arm had shifted copies)'], WHY_S)
offon('paper.restart.vs72idle.fez', TS, ['+0.028 [&minus;0.038, +0.085] (fez, whose 72-idle arm had shifted copies)'], WHY_S)
offon('paper.runs.rig_oct4', JI, ['680 of 1162 Rigetti tasks are used here (the 16 to 17 UTC runs, with 116 cancelled,'], WHY_S)
OPS.append(['set', 'paper.runs.control_times', '--field', 'source.grep', '--to',
  'The plan and circuits were pushed to GitHub at 23:00:47 UTC. IBM created the first job (ibm_kingston, dbck8c9gv2cc73eahbc0) at 23:01:05. The analysis script was pushed at 23:02:19. That first job finished at 23:02:31.',
  '--why', 'HEU1-11 (30 Oct site pass): control-run order-of-events sentence split at its semicolons; times and job id unchanged',
  '--evidence', 'heuremen.org/experiments/2026-10-21-control-run/index.html'])
# --- 2. Hahn: the 13th run (HEU1-1)
for rid in ('hahn.marrakesh.run1.fixed', 'hahn.marrakesh.run2.fixed'): offon(rid, IX, ['marrakesh 0.907 to 1.015'], WHY_H)
for rid in ('hahn.marrakesh.run1.free', 'hahn.marrakesh.run2.free'): offon(rid, IX, ['0.892 to 0.958'], WHY_H)
OPS.append(['set', 'hahn.fit_model_spread', '--field', 'source.grep', '--to', 'largest |planned - free| over the thirteen runs 0.120 (boston)',
  '--why', WHY_H + '; hahn_table.py output regenerated with thirteen runs (the 23 Oct 16:17 output of the same script)', '--evidence', H + 'results_hahn_table.text'])
OPS.append(['set', 'hahn.age_range', '--field', 'value', '--to', '0.5', '--why', WHY_H + ' (stated T2 median age 0.5 h at run)', '--evidence', H + 'results_hahn_table.text', '--checks', '$CHECKS'])
OPS.append(['set', 'hahn.age_range', '--field', 'lo', '--to', '0.5', '--why', 'same', '--evidence', H + 'results_hahn_table.text', '--checks', '$CHECKS'])
OPS.append(['set', 'hahn.age_range', '--field', 'claim', '--to', 'Stated T2 median age at run time across the thirteen Hahn runs: marrakesh fresh-record run 0.5 h to boston 34.3 h',
  '--why', WHY_H, '--evidence', H + 'results_hahn_table.text'])
OPS.append(['set', 'hahn.age_range', '--field', 'source.grep', '--to', 'stated T2 median age at run 0.5 h', '--why', WHY_H, '--evidence', H + 'results_hahn_table.text'])
offon('hahn.age_range', IX, ['0.5 to 34.3 hours old'], WHY_H)
ADDS = []
def add(rid, claim, value, lo, hi, unit, outcome, src, grep, ons):
    a = ['add', rid, '--claim', claim, '--value', value]
    if lo is not None: a += ['--lo', lo, '--hi', hi]
    if unit: a += ['--unit', unit]
    a += ['--outcome', outcome, '--source', src, '--grep', grep]
    for s, t in ons: a += ['--on', s, t]
    a += ['--checks', '$CHECKS']; OPS.append(a)
add('hahn.marrakesh.fresh.fixed', 'Hahn T2, marrakesh fresh-record run (23 Oct, stated T2 0.5 h old): delivered/stated, planned fit', '1.015', '0.937', '1.130', '', 'CONSISTENT',
    H + 'results_hahn_table.text', 'FIXED 1.015 [0.937, 1.130] -> CONSISTENT (73 of 153 below stated)',
    [(HP, '1.015 [0.937, 1.130] CONSISTENT'), (IX, 'marrakesh 0.907 to 1.015')])
add('hahn.marrakesh.fresh.free', 'Hahn T2, marrakesh fresh-record run (23 Oct): delivered/stated, free-asymptote fit (defined after the data)', '0.958', '0.902', '1.016', '', 'CONSISTENT',
    H + 'results_hahn_table.text', 'FREE 0.958 [0.902, 1.016] -> CONSISTENT (83 of 150 below stated)',
    [(HP, '0.958 [0.902, 1.016] CONSISTENT'), (IX, '0.892 to 0.958')])
add('hahn.marrakesh.fresh.age', 'Hahn T2, marrakesh fresh-record run: stated T2 median age at run time', '0.5', None, None, 'h', 'RECORD',
    H + 'results_hahn_table.text', 'stated T2 median age at run 0.5 h', [(HP, 'on stated values 0.5 hours old')])
add('hahn.marrakesh.pooled3.fixed', 'Hahn T2, marrakesh runs 1, 2 and fresh record pooled by qubit, planned fit', '0.972', '0.929', '1.022', '', 'CONSISTENT',
    H + 'results_hahn_fresh_ibm_marrakesh.text', '3 run(s) pooled by qubit, FIXED 1/2   : median 0.972 [0.929, 1.022]', [(HP, '0.972 [0.929, 1.022] CONSISTENT')])
add('hahn.marrakesh.pooled3.free', 'Hahn T2, marrakesh runs 1, 2 and fresh record pooled by qubit, free-asymptote fit', '0.889', '0.845', '0.936', '', 'BELOW',
    H + 'results_hahn_fresh_ibm_marrakesh.text', '3 run(s) pooled by qubit, FREE asymptote: median 0.889 [0.845, 0.936]', [(HP, '0.889 [0.845, 0.936] BELOW')])
# --- 3. length repeats (HEU1-7)
add('length.kingston_repeat_n4', 'Kingston readout-instruction repeat 1 (1000 shots): measure_2/measure kick ratio at 4 readouts, copies disagree', '1.007', '0.811', '1.203', '', 'CANNOT_TELL',
    LR + 'results_kingston_repeat.text', 'R2 ratio k(L2)/k(L1) N=4: 1.007 [0.811, 1.203]  (per readout 1, proportional 0.633) -> CANNOT_TELL (copies disagree)',
    [(IX, '1.01 [0.81, 1.20]'), (TS, '1.01 [0.81, 1.20]'), (LP, '1.007 [0.811, 1.203]')])
add('length.kingston_repeat_gap4', 'Kingston readout-instruction repeat 1: copy gap of the measure kick at 4 readouts (excludes 0, so CANNOT_TELL)', '+0.038 to +0.441', '+0.038', '+0.441', 'deg', 'CANNOT_TELL',
    LR + 'results_kingston_repeat.text', 'copy gap [+0.038, +0.441] -> CANNOT_TELL (copies disagree)', [(LP, 'copy gap [+0.038, +0.441]')])
for surf, snip in ((IX, '1.01 [0.80, 1.37]'), (TS, '1.01 [0.80, 1.37]'), (LP, '1.008 [0.799, 1.372]')): OPS.append(['on', 'length.kingston_repeat_n8', surf, snip])
OPS.append(['on', 'length.kingston_r2_n4', LP, '0.946 [0.750, 1.171]']); OPS.append(['on', 'length.kingston_r2_n8', LP, '0.981 [0.773, 1.284]'])
OPS.append(['on', 'length.kingston_r2_n4', WW, '0.95 [0.75, 1.17]']); OPS.append(['on', 'length.kingston_r2_n8', WW, '0.98 [0.77, 1.28]'])
OPS.append(['on', 'length.fez_r2', LP, '0.938 [0.802, 1.173]']); OPS.append(['on', 'length.fez_r2', LP, '0.879 [0.710, 1.103]'])
for rid, val, lo, hi, f, grep in (
    ('length.kingston_repeat_kg8', '-2.685', '-3.488', '-1.877', 'results_kingston_repeat.text', 'R1 kick N=8 L1: -2.685 [-3.488, -1.877] deg/readout'),
    ('length.kingston_r2_kg8', '-2.812', '-3.790', '-2.093', 'results_kingston_r2.text', 'R1 kick N=8 L1: -2.812 [-3.790, -2.093] deg/readout'),
    ('length.fez_r2_kg8', '-1.531', '-2.034', '-1.214', 'results_fez_r2.text', 'R1 kick N=8 L1: -1.531 [-2.034, -1.214] deg/readout')):
    add(rid, 'Readout-instruction repeat known-good: measure kick at 8 readouts (' + f.split('_')[1] + ')', val, lo, hi, 'deg/readout', 'BELOW', LR + f, grep,
        [(LP, '&minus;' + val[1:] + ' [&minus;' + lo[1:] + ', &minus;' + hi[1:] + ']')])
OPS.append(['on', 'bill.r8.kick_control', LP, 'fez &minus;1.62 [&minus;2.08, &minus;1.18]'])
OPS.append(['on', 'paper.kick_control.kingston', LP, 'kingston &minus;2.86 [&minus;3.55, &minus;2.09]'])
# --- 4. fitted-rate cut (HEU1-17)
V='heuremen.org/experiments/2026-10-04-three-positions/verify_output.text'
add('campaign.fitted_rate_cut', 'October fitted-rate reading: the rate > 4 deg/us cut keeps 284 of 524 untouched-qubit readings', '284 of 524', None, None, '', 'COUNT',
    V, '30 of 284 above the cut', [(TS, 'That cut keeps 284 of the 524 readings'), (P3, '284 of the 524 readings')])
add('campaign.fitted_rate_nocut', 'October fitted-rate reading without the cut: pooled 1.0405, one constant does not fit (chi2/dof 2.22, p = 0.038)', '1.0405', None, None, 'ratio', 'RECORD',
    V, 'pooled 1.0405   chi2/dof 2.22   p = 0.0384', [(TS, 'all 524 give 1.0405'), (TS, '(&chi;&sup2;/dof 2.22, p = 0.038)'), (P3, 'all 524 readings give 1.0405 pooled'), (P3, '(&chi;&sup2;/dof 2.22, p = 0.038)')])
OPS.append(['on', 'paper.rig.fitted_rate_ratio', P3, '1.0207&nbsp;&plusmn;&nbsp;0.0092 pooled over seven processors, 2.2 standard errors from 1: cannot tell'])
# --- 5. correlations caption (HEU1-18) and floor count
add('sept.kingston_pair16_23_excluded', '24 Sep: kingston pair 16-23 excluded as dead readout (alone length 1.355 > 1); its space value at pi -0.159; both-pair mean -0.486', '-0.159', None, None, '', 'RECORD',
    SEP, 'the other kingston pair 16-23 is excluded in the lab log (dead readout, space at pi = -0.159); mean of both pairs would be -0.486',
    [(CP, 'Its space value at π is −0.159, and the mean of both kingston pairs would be −0.486')])
add('sept.kingston_pair16_23_alone', '24 Sep: kingston pair 16-23 alone length 1.355 (impossible > 1), the reason for its exclusion', '1.355', None, None, '', 'RECORD',
    SEP, 'pair 16-23 excluded as dead readout (alone length 1.355, impossible >1)', [(CP, 'its length alone reads 1.355')])
add('sept.fez_space_pairs', '24 Sep: fez space correlator at pi by pair, 22-23 and 81-82 (mean -0.891)', '-0.9502 / -0.8320', None, None, '', 'RECORD',
    SEP, 'pair values -0.9502, -0.8320', [(CP, 'pairs 22-23 (−0.950) and 81-82 (−0.832)')])
OPS.append(['on', 'site.tech_sept_floor', CP, '+0.0012 ± 0.0024 at zero wait (8 pairs)'])
# --- 6. calibration records (HEU1-16)
OPS.append(['on', 'bill.r5.restamp', CR, '4,204 of 4,204 entries are identical across 14 record pairs'])
add('calrec.restamp_oct23', 'Restamp check, 22-23 Oct pairs (fez, kingston, marrakesh): 1,549 of 1,549 T1/T2 entries identical in value and date', '1549', None, None, 'entries', 'RECORD',
    'heuremen.org/experiments/calibration-records/restamp_check/results_restamp_oct23.text', 'these pairs 1549 of 1549', [(CR, 'hold 1,549 entries, all identical in value and date')])
# --- 7. flip-check run 1 page (HEU1-9)
add('flip2.kingston_knowngood', 'X-flip run 2, kingston known-good: unheralded idle flip failure above the like-for-like floor at N = 0 and 4 (failed)', '+0.1541 / +0.1835', None, None, 'percentage points', 'ABOVE',
    'heuremen.org/experiments/2026-10-22-flip-check-run2/results_flip.text', 'KNOWN-GOOD idle N=0: unheralded idle flip failure minus unheralded CAL 0X floor +0.1541% [+0.0526, +0.2560] -> ABOVE -> FAIL',
    [(F1, '(+0.1541 and +0.1835 percentage points above the floor at N = 0 and 4)')])
# --- 8. plain page (HEU1-8)
OPS.append(['on', 'decay.repeat_range', WW, 'inside the simulated 95th percentile of shot noise alone in 8 of 9 runs'])
# --- 9. readout audit page (HEU1-19)
for chip, f, job, r1, p10, p01, r3, extra in (
    ('fez', 'results_ro_ibm_fez.text', 'dbdaf6s24mrc73cl3phg', ('0.923', '0.889', '0.951', 'BELOW'), ('0.915', '0.761', '1.024'), ('0.961', '0.911', '1.002'), '1 of 2', ''),
    ('kingston', 'results_ro_ibm_kingston.text', 'dbdaf99gv2cc738hnmo0', ('1.008', '0.959', '1.047', 'CONSISTENT'), ('1.083', '0.999', '1.256'), ('0.963', '0.930', '1.009'), '1 of 1', ''),
    ('marrakesh', 'results_ro_ibm_marrakesh.text', 'dbdafboc77vs7387no5g', ('1.067', '0.953', '1.380', 'CONSISTENT'), ('1.065', '0.772', '1.338'), ('0.990', '0.909', '1.223'), '14 of 14', ''),
    ('marrakesh_repeat', 'results_ro_ibm_marrakesh_run2.text', 'dbdahc8c77vs7387nsqg', ('1.078', '0.979', '1.238', 'CONSISTENT'), ('0.971', '0.761', '1.464'), ('1.013', '0.922', '1.150'), '13 of 14', '')):
    add('ro.' + chip + '.r1', 'Readout audit, ' + chip.replace('_', ' ') + ' (job ' + job + '): delivered / stated readout_error, median over 156 qubits', r1[0], r1[1], r1[2], '', r1[3],
        RA + f, 'median over 156 qubits: %s [%s, %s] vs 1 -> %s' % r1, [(RP, 'R1 %s [%s, %s] %s' % r1)])
    add('ro.' + chip + '.p10', 'Readout audit, ' + chip.replace('_', ' ') + ': delivered / stated P(1|0)', p10[0], p10[1], p10[2], '', 'CONSISTENT',
        RA + f, 'P(1|0): delivered / stated median %s [%s, %s] -> CONSISTENT' % p10, [(RP, 'P(1|0) %s [%s, %s] CONSISTENT' % p10)])
    add('ro.' + chip + '.p01', 'Readout audit, ' + chip.replace('_', ' ') + ': delivered / stated P(0|1)', p01[0], p01[1], p01[2], '', 'CONSISTENT',
        RA + f, 'P(0|1): delivered / stated median %s [%s, %s] -> CONSISTENT' % p01, [(RP, 'P(0|1) %s [%s, %s] CONSISTENT' % p01)])
for chip, f, n, r1, r3 in (('fez', 'results_iso_ibm_fez.text', '2', ('-0.0000', '-0.0001', '+0.0001', 'CONSISTENT'), '1 of 2'),
                           ('kingston', 'results_iso_ibm_kingston.text', '1', ('-0.0022', '-0.0022', '-0.0022', 'BELOW'), '0 of 1'),
                           ('marrakesh', 'results_iso_ibm_marrakesh.text', '14', ('-0.0019', '-0.0080', '+0.0020', 'CONSISTENT'), '11 of 14')):
    snip = ('isolated minus all-qubit P(1|0) &minus;0.0022 BELOW, on one qubit' if chip == 'kingston' else
            'isolated minus all-qubit P(1|0) &minus;%s [&minus;%s, %s] CONSISTENT' % (r1[0][1:], r1[1][1:], r1[2]))
    add('ro.iso.' + chip, 'Readout audit, isolated read of IBM-stated zeros, ' + chip + ': isolated minus all-qubit P(1|0), median over ' + n + ' qubit(s)', r1[0], r1[1], r1[2], '', r1[3],
        RA + f, 'median over %s qubits: %s [%s, %s] -> %s' % ((n,) + r1), [(RP, snip)])
OPS.append(['on', 'bill.zeros.iso_vs_allq', RP, '&minus;0.0024 [&minus;0.0048, +0.0001] CONSISTENT'])
for rid, f, grep, snip in (
    ('ro.fez.r3', 'results_ro_ibm_fez.text', '(0 of 4096): 1; their delivered P(1|0) median 0.0037', 'R3: 1 of 2 stated zeros above the bound'),
    ('ro.kingston.r3', 'results_ro_ibm_kingston.text', '(0 of 4096): 1; their delivered P(1|0) median 0.0026', 'R3: 1 of 1 stated zero above the bound'),
    ('ro.marrakesh.r3', 'results_ro_ibm_marrakesh.text', '(0 of 4096): 14; their delivered P(1|0) median 0.0073', 'R3: 14 of 14 stated zeros above the bound, delivered median 0.0073'),
    ('ro.marrakesh_repeat.r3', 'results_ro_ibm_marrakesh_run2.text', '(0 of 4096): 13; their delivered P(1|0) median 0.0067', 'R3: 13 of 14 stated zeros above the bound, delivered median 0.0067'),
    ('ro.iso.fez.r3', 'results_iso_ibm_fez.text', 'above 0.00073: 1 of 2; delivered median 0.0022', 'R3: 1 of 2 above the bound'),
    ('ro.iso.kingston.r3', 'results_iso_ibm_kingston.text', 'above 0.00073: 0 of 1; delivered median 0.0003', 'R3: 0 of 1 above the bound'),
    ('ro.iso.marrakesh.r3', 'results_iso_ibm_marrakesh.text', 'above 0.00073: 11 of 14; delivered median 0.0056', 'R3: 11 of 14 above the bound, delivered median 0.0056')):
    add(rid, 'Readout audit R3: IBM-stated P(1|0) = 0 qubits whose delivered P(1|0) Wilson 95 % lower bound is above 0.00073 (' + f + ')', snip.split(': ')[1].split(' ')[0] + ' of ' + snip.split(' of ')[1].split(' ')[0], None, None, '', 'COUNT', RA + f, grep, [(RP, snip)])
