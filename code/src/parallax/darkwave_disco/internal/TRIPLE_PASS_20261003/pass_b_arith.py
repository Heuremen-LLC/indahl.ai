"""TRIPLE PASS, SEAT B (the witness, across firings) -- the arithmetic behind PASS_B_WITNESS.md.
Read-only: every input below is typed in from a read file or a ledger line (source in the comment beside it).
Nothing here opens a raw result, edits a file, or submits anything. Run: python3 pass_b_arith.py > pass_b_arith.txt
FRICTION rule used in PASS_B_WITNESS.md: two witnesses are in FRICTION when their +-width bars do not touch, |a - b| > wa + wb.
The gap is also printed in combined widths, sqrt(wa^2 + wb^2), for reference only."""
import math
import numpy as np

def pair(label, a, wa, b, wb, unit=''):
    gap = a - b; comb = math.sqrt(wa ** 2 + wb ** 2); touch = abs(gap) <= wa + wb
    note = '  (one side carries no width: only the other bar is used)' if (wa == 0 or wb == 0) else ''
    print(f'{label:<92s} {a:+.4f} +- {wa:.4f}  vs  {b:+.4f} +- {wb:.4f} {unit:<6s} gap {gap:+.4f}  bars {wa + wb:.4f}  '
          f'{gap / comb:+5.2f} comb.widths  {"touch" if touch else "FRICTION"}{note}')

print('=== 1. THE LOOK, OWN clock: level drops of the no-time arm converted to us on each job\'s own pooled level clock (derived here)')
# none_arm_three_chips.txt:6,27,48 (ON none arm); level clocks: run5_marrakesh.txt:83 (shared 223.4), run9_pittsburgh.txt:83 (shared 263.1),
# Kingston has no level clock in run 7 -> Run 1 tauF.shared 255.4 (all_three_chips.txt:157, same nine bits, 10/1 night)
for chip, d, w, tau in (('Marrakesh run 5', -0.0480, 0.0071, 223.4), ('Pittsburgh run 9', -0.0272, 0.0060, 263.1), ('Kingston run 7', -0.0204, 0.0053, 255.4)):
    t = -tau * math.log(1 + d); wt = tau * w / (1 + d)
    print(f'   {chip:<18s} level {d:+.4f} +- {w:.4f}  ->  {t:5.2f} +- {wt:4.2f} us on tau {tau} us   (/2.18 = {t / 2.18:4.2f})')
# hold run, one look at 150 us: arm minus nothing -0.0007 +- 0.0009 (hold_run.txt:13), nothing-done median 0.3546 0.3600 0.3497 (hold_run.txt:4)
L = np.mean([0.3546, 0.3600, 0.3497]); tau = -300 / math.log(L); t = tau * 0.0007 / L; wt = tau * 0.0009 / L
print(f'   hold run, one look at 150 us: level -0.0007 +- 0.0009 on nothing-done {L:.4f} (tau {tau:.1f} us) -> {t:.2f} +- {wt:.2f} us')
for n, said in ((3, 311.5), (9, 327.0)):
    print(f'   hold run, {n} looks, bit by bit "time the bit says" {said} us -> {(said - 300) / n:.2f} us per look')
for n, mids in ((3, (320.1, 312.4, 308.9)), (9, (336.3, 336.5, 337.7))):
    print(f'   hold run, {n} looks, middle bits per read ' + ' / '.join(f'{(m - 300) / n:.2f}' for m in mids) + ' us per look')

print('\n=== 2. THE LOOK, ratios with each OWN witness (WITNESS 2.3699 +- 0.0318 us, block of 9; LAID 2.180 us); derived here')
W, wW, M = 2.3699, 0.0318, 2.180
for lab, q, wq in (('pile-up (ledger 135)', 3.5, 0.2), ('jump per-job low', 3.20, 0), ('jump per-job high', 4.26, 0), ('jump each bit over 8 jobs', 3.23, 0),
                   ('tail over 3 jobs', 3.63, 0), ('hold 3 looks bit by bit', 3.83, 0), ('hold 9 looks bit by bit', 3.00, 0),
                   ('give-back at 0 us', 3.5313, 0.8737), ('give-back at 150 us', 3.5569, 0.9309), ('give-back at 270 us', 4.0507, 0.9397),
                   ('give-back job 112 at 270 us', 0.7272, 1.5266), ('give-back job 113 at 270 us', 6.8846, 1.8666),
                   ('none arm Pittsburgh run 9 (derived above)', 7.26, 1.62)):
    r1, r2 = q / M, q / W; w1 = wq / M; w2 = r2 * math.sqrt((wq / q) ** 2 + (wW / W) ** 2) if q else 0
    print(f'   {lab:<44s} {q:5.2f} +- {wq:4.2f} us   qubit/maker {r1:4.2f} +- {w1:4.2f}   qubit/witness {r2:4.2f} +- {w2:4.2f}')

print('\n=== 3. THE LEAKAGE CAP on each chip from the same jobs\' back-to-back arms (derived here)')
# model (ledger 1963): o_N + |u_N| = 2 sin^2(N e / 2) + (N/2) k ; inputs close_push.txt:2,3,5,6 ; rep_marrakesh_read1.txt:2,3,5,6 ; rep_kingston_read1.txt:2-6
arms = {'Pittsburgh (3 jobs)': ((0.0019, 0.0006), (0.0229, 0.0007), (-0.0020, 0.0007), (-0.0232, 0.0008)),
        'Marrakesh (1 job)': ((0.0063, 0.0013), (0.0147, 0.0014), (-0.0045, 0.0014), (-0.0148, 0.0013)),
        'Kingston (1 job)': ((0.0029, 0.0017), (0.0192, 0.0018), (-0.0071, 0.0014), (-0.0212, 0.0015))}
rng = np.random.default_rng(20261003)
for chip, (o2, o10, u2, u10) in arms.items():
    S2 = o2[0] - u2[0]; S10 = o10[0] - u10[0]; wS2 = math.hypot(o2[1], u2[1]); wS10 = math.hypot(o10[1], u10[1])
    disc = S10 - 5 * S2                                   # small-angle: 40 e^2 = S10 - 5 S2
    line = f'   {chip:<20s} S2 {S2:.4f} +- {wS2:.4f}   S10 {S10:.4f} +- {wS10:.4f}   S10 - 5 S2 = {disc:+.4f}'
    if disc > 0:
        es, ks = [], []
        for _ in range(20000):
            s2 = rng.normal(S2, wS2); s10 = rng.normal(S10, wS10)
            f = lambda e: 2 * math.sin(5 * e) ** 2 - 10 * math.sin(e) ** 2 - (s10 - 5 * s2)
            lo, hi = 0.0, math.radians(10)
            if f(lo) * f(hi) > 0: continue
            for _ in range(60):
                mid = (lo + hi) / 2
                if f(lo) * f(mid) <= 0: hi = mid
                else: lo = mid
            e = (lo + hi) / 2; es.append(math.degrees(e)); ks.append(100 * (s2 - 2 * math.sin(e) ** 2))
        line += f'   -> shortfall {np.mean(es):.3f} +- {np.std(es):.3f} deg, k {np.mean(ks):.3f} +- {np.std(ks):.3f} % per push ({len(es)} draws)'
    else:
        line += '   -> no real solution (two-push sum larger than a fifth of the ten-push sum)'
    line += f';  model-free bound k <= S10/5 = {100 * S10 / 5:.3f} +- {100 * wS10 / 5:.3f} % per push; shortfall if k = 0: {math.degrees(math.asin(math.sqrt(S10 / 2)) / 5):.3f} deg (ten pushes), {math.degrees(math.asin(math.sqrt(S2 / 2))):.3f} deg (two pushes)'
    print(line)

print('\n=== 4. THE HALFWAY START against the OFF-ON line, per chip (%, derived here; line = (OFF + ON)/2)')
for chip, off, on, mid in (('Pittsburgh push run (3 jobs)', (2.00, 0.16), (0.05, 0.13), (0.34, 0.14)),
                           ('Marrakesh run 141 (1 job)', (2.74, 0.28), (-0.16, 0.21), (1.17, 0.24)),
                           ('Kingston run 141 (1 job)', (2.87, 0.28), (-1.24, 0.24), (-0.06, 0.22))):
    ln = (off[0] + on[0]) / 2; wl = math.hypot(off[1], on[1]) / 2; o = mid[0] - ln; wo = math.hypot(mid[1], wl)
    print(f'   {chip:<30s} line {ln:+.3f} +- {wl:.3f}   halfway {mid[0]:+.2f} +- {mid[1]:.2f}   offset {o:+.3f} +- {wo:.3f} ({o / wo:+.1f} widths)')

print('\n=== 5. THE SPECTATOR\'S COUPLING, two jobs on the same roles (derived here)')
k2d = lambda khz: khz * 1e3 * 360 / 1e6           # kHz -> deg per us
print(f'   stopwatch run 81 (witness_run.txt:15): 4.5 kHz [3.4, 5.2] -> {k2d(4.5):.3f} deg/us [{k2d(3.4):.3f}, {k2d(5.2):.3f}] -> per 30 us {30 * k2d(4.5):.1f} [{30 * k2d(3.4):.1f}, {30 * k2d(5.2):.1f}] deg')
print(f'   stopwatch first 20 us (witness_run.txt:13): +33.9 deg -> {33.9 / 20:.3f} deg/us -> {33.9 * 1.5:.1f} deg per 30 us; second 20 us {28.1 * 1.5:.1f}; third {23.9 * 1.5:.1f}')
print(f'   run 121 (noname_read1.txt:77): 16.9023 +- 1.8085 deg per 30-us stretch -> {16.9023 / 30:.4f} +- {1.8085 / 30:.4f} deg/us -> {16.9023 / 30 / 0.36:.3f} +- {1.8085 / 30 / 0.36:.3f} kHz')
print(f'   run 121 fit grid wall (readnoname.py TH = +-0.6 rad per stretch): {math.degrees(0.6):.2f} deg per 30 us = {math.degrees(0.6) / 30:.3f} deg/us = {math.degrees(0.6) / 30 / 0.36:.2f} kHz')
print(f'   look-time free precession (close_looktime.txt:11): 3.1444 +- 0.0760 deg/us = {3.1444 / 0.36:.2f} +- {0.0760 / 0.36:.2f} kHz')

print('\n=== 6. FRICTION CHECKS (|a-b| > wa + wb)')
# THE LOOK, WITNESS clock, per job (close_looktime.txt:2,6) and wired / not wired (:3,:4,:7,:8)
pair('look by spectators, 9 looks: job 101 vs job 102', 2.4718, 0.0512, 2.2802, 0.0464, 'us')
pair('look by spectators, 9 looks: job 101 vs job 103', 2.4718, 0.0512, 2.3578, 0.0659, 'us')
pair('look by spectators, 9 looks: job 102 vs job 103', 2.2802, 0.0464, 2.3578, 0.0659, 'us')
pair('look by spectators, 3 looks: job 101 vs job 102', 2.4940, 0.1124, 2.1654, 0.1017, 'us')
pair('look by spectators, 3 looks: job 102 vs job 103', 2.1654, 0.1017, 2.3888, 0.1225, 'us')
pair('look by spectators, 3 looks: not wired vs wired', 2.4353, 0.0965, 2.2373, 0.0841, 'us')
pair('look by spectators, 9 looks: not wired vs wired', 2.3652, 0.0487, 2.3244, 0.0413, 'us')
pair('look by spectators, 9 looks (all) vs maker 2.180 (no width)', 2.3699, 0.0318, 2.180, 0.0, 'us')
# THE LOOK, OWN clock (close_giveback.txt:2,4,6; derived above)
pair('give-back, look at 0 us: job 111 vs job 112', 6.5260, 1.5081, 1.0228, 1.4946, 'us')
pair('give-back, look at 150 us: job 112 vs job 113', 1.3144, 1.5800, 5.9062, 1.5712, 'us')
pair('give-back, look at 270 us: job 112 vs job 113', 0.7272, 1.5266, 6.8846, 1.8666, 'us')
pair('one look at 150 us: give-back (3 jobs) vs hold run (3 jobs, derived us)', 3.5569, 0.9309, 0.57, 0.73, 'us')
pair('no-time arm, level: Marrakesh run 5 vs Kingston run 7', -0.0480, 0.0071, -0.0204, 0.0053)
pair('no-time arm, level: Marrakesh run 5 vs Pittsburgh run 9', -0.0480, 0.0071, -0.0272, 0.0060)
pair('no-time arm, level: Pittsburgh run 9 vs Kingston run 7', -0.0272, 0.0060, -0.0204, 0.0053)
pair('no-time arm in us (derived): Marrakesh run 5 vs Kingston run 7', 10.99, 1.67, 5.26, 1.38, 'us')
pair('no-time arm in us (derived): Pittsburgh run 9 (9 bits) vs pile-up 3.5 +- 0.2', 7.26, 1.62, 3.5, 0.2, 'us')
pair('bite at the short wait, ON: Pittsburgh Run 2 (night) vs Run 9 (morning)', -0.008, 0.012, -0.068, 0.019)
pair('bite at the short wait, ON: Pittsburgh Run 2 vs Kingston Run 2', -0.008, 0.012, -0.053, 0.014)
pair('bite at the short wait, ON: Pittsburgh Run 2 vs Marrakesh run 5', -0.008, 0.012, -0.079, 0.026)
# THE CROSSING, start 0 (close_push.txt:4; reads_new/hold_crossing.txt:20; noname_read1.txt:27; rep_*:4)
pair('crossing OFF: push all (3) vs Marrakesh', 0.0200, 0.0016, 0.0274, 0.0028)
pair('crossing OFF: push all (3) vs Kingston', 0.0200, 0.0016, 0.0287, 0.0028)
pair('crossing OFF: hold all (3) vs Kingston', 0.0217, 0.0017, 0.0287, 0.0028)
pair('crossing OFF: hold all (3) vs Marrakesh', 0.0217, 0.0017, 0.0274, 0.0028)
pair('crossing OFF: push all vs hold all', 0.0200, 0.0016, 0.0217, 0.0017)
pair('crossing OFF: run 121 A30_30 vs push all', 0.0126, 0.0032, 0.0200, 0.0016)
pair('crossing OFF: run 121 A30_30 vs hold all', 0.0126, 0.0032, 0.0217, 0.0017)
pair('crossing OFF: run 121 A30_30 vs Marrakesh', 0.0126, 0.0032, 0.0274, 0.0028)
pair('crossing OFF: run 121 A30_30 vs Kingston', 0.0126, 0.0032, 0.0287, 0.0028)
pair('crossing OFF: hold job 71 vs hold job 72', 0.0190, 0.0030, 0.0251, 0.0029)
pair('crossing OFF: push job 91 vs hold job 72', 0.0174, 0.0028, 0.0251, 0.0029)
pair('crossing OFF: push job 91 vs push job 92', 0.0174, 0.0028, 0.0213, 0.0030)
pair('crossing OFF: Marrakesh vs Kingston', 0.0274, 0.0028, 0.0287, 0.0028)
pair('same train, same emitters, run 121 seat 2: A30_30 vs WA (THREE_SEATS)', 0.0218, 0.0072, 0.0081, 0.0058)
pair('crossing OFF, one-clock: run 121 N2 vs A30_30 (same job)', 0.0245, 0.0025, 0.0126, 0.0032)
# start 1 (close_push.txt:7; hold_crossing.txt:21; noname_read1.txt:51; rep_*:7)
pair('|1> column: Kingston vs Pittsburgh push', -0.0124, 0.0024, 0.0005, 0.0013)
pair('|1> column: Kingston vs Pittsburgh hold', -0.0124, 0.0024, 0.0014, 0.0015)
pair('|1> column: Kingston vs Marrakesh', -0.0124, 0.0024, -0.0016, 0.0021)
pair('|1> column: Kingston vs run 121 B30_30 one-clock', -0.0124, 0.0024, -0.0022, 0.0031)
pair('|1> column: Kingston vs run 121 WB seat 2 (35 emitters)', -0.0124, 0.0024, -0.0094, 0.0052)
pair('|1> column: Kingston vs rung four 0.012158 (no width)', -0.0124, 0.0024, -0.012158, 0.0)
# halfway (close_push.txt:10, rep_*:10)
pair('halfway column: Pittsburgh vs Marrakesh', 0.0034, 0.0014, 0.0117, 0.0024)
pair('halfway column: Marrakesh vs Kingston', 0.0117, 0.0024, -0.0006, 0.0022)
pair('halfway column: Pittsburgh vs Kingston', 0.0034, 0.0014, -0.0006, 0.0022)
pair('halfway offset from line (%, derived): Pittsburgh vs Marrakesh', -0.685, 0.174, -0.12, 0.297)
pair('halfway offset from line (%, derived): Marrakesh vs Kingston', -0.12, 0.297, -0.875, 0.287)
# idle |0> 300 us (close_push.txt:11; noname_read1.txt:10; rep_*:11; all_three_chips.txt:128; run5/run9 F.OFF.w300)
pair('idle |0> 300 us: Marrakesh vs Kingston', -0.0043, 0.0013, 0.0026, 0.0014)
pair('idle |0> 300 us: Marrakesh vs Pittsburgh push', -0.0043, 0.0013, -0.0001, 0.0006)
pair('idle |0> 300 us: Kingston vs Pittsburgh push', 0.0026, 0.0014, -0.0001, 0.0006)
pair('idle |0> 300 us: Marrakesh run 141 vs Marrakesh run 5 (after a look)', -0.0043, 0.0013, -0.0023, 0.0027)
pair('idle |0> 300 us: Kingston run 141 vs Kingston Run 1 (10/1)', 0.0026, 0.0014, 0.0021, 0.0058)
# the below-zero depth and the 10-us variant inside run 121 (noname_read1.txt; THREE_SEATS)
pair('own-stretch, 10 pushes: A30_30 (150 bits) vs WA emitters (35)', -0.0097, 0.0051, -0.0216, 0.0102)
pair('own-stretch, 10-us |1> stretches: A30_10 150 bits vs 35 emitters', 0.0170, 0.0064, 0.0302, 0.0107)
# the qubit's |1> survival after 300 us, Pittsburgh (close_push.txt:12; close_giveback.txt:8; discarded_hold.txt:144; noname_read1.txt:6; run9 F.ON.w300)
pair('|1> kept at 300 us: push all vs hold all (means)', 0.3131, 0.0013, 0.3354, 0.0013)
pair('|1> kept at 300 us: push all vs give-back all', 0.3131, 0.0013, 0.3190, 0.0009)
pair('|1> kept at 300 us: give-back all vs hold all', 0.3190, 0.0009, 0.3354, 0.0013)
pair('|1> kept at 300 us: hold all vs run 121', 0.3354, 0.0013, 0.3286, 0.0030)
pair('|1> kept at 300 us: push all vs run 121', 0.3131, 0.0013, 0.3286, 0.0030)
pair('|1> kept at 300 us: give-back job 111 vs job 113', 0.3241, 0.0014, 0.3135, 0.0015)
pair('|1> kept at 300 us: push job 92 (14:26) vs give-back job 112 (14:27)', 0.3101, 0.0025, 0.3195, 0.0015)
pair('|1> kept at 300 us: Pittsburgh Run 2 (9 bits, one look) vs run 9 (9 bits, one look)', 0.351, 0.0127, 0.2808, 0.0144)
pair('|1> kept at 300 us: Marrakesh run 141 vs run 5 (9 bits, one look)', 0.1786, 0.0019, 0.2445, 0.0139)
pair('|1> kept at 300 us: Kingston run 141 vs Run 2 (9 bits, one look)', 0.2982, 0.0025, 0.2977, 0.0121)
# the two clocks: gap clock / level clock (ledger 1778; run9 ratio.shared; ledger 1831)
for lab, a, wa in (('Kingston Run 2', 0.60, 0.07), ('Phoenix Run 2', 0.68, 0.07), ('Marrakesh run 5', 0.6076, 0.0822), ('Pittsburgh run 9', 0.658, 0.0998),
                   ('Pittsburgh Run 2', 0.83, 0.11), ('Boston Run 2', 0.80, 0.11)):
    pair(f'gap/level: Pittsburgh jump run (8 jobs) vs {lab}', 0.775, 0.009, a, wa)
pair('gap/level: Kingston Run 2 vs Pittsburgh Run 2', 0.60, 0.07, 0.83, 0.11)
pair('gap/level: Kingston Run 2 vs Boston Run 2', 0.60, 0.07, 0.80, 0.11)
pair('gap/level: Pittsburgh Run 2 vs Pittsburgh run 9', 0.83, 0.11, 0.658, 0.0998)
pair('gap/level: Marrakesh run 5 vs Kingston Run 2', 0.6076, 0.0822, 0.60, 0.07)
# early / late clock with no look (lone_vs_tail.txt:16; noname_read1.txt:3,6 derived)
c10 = -10 / math.log(0.9463); w10 = c10 * 0.0019 / (0.9463 * -math.log(0.9463)); c300 = -300 / math.log(0.3286); w300 = c300 * 0.0030 / (0.3286 * -math.log(0.3286))
print(f'   run 121 stretch clocks (derived): 0-10 us {c10:.1f} +- {w10:.1f} us; 0-300 us {c300:.1f} +- {w300:.1f} us; ratio {c10 / c300:.3f} +- {(c10 / c300) * math.hypot(w10 / c10, w300 / c300):.3f}')
c30 = -30 / math.log(0.8609); c90 = -90 / math.log(0.6846)
print(f'   run 121 stretch clocks (derived): 0-30 us {c30:.1f} us; 0-90 us {c90:.1f} us; ratios to 0-300: {c30 / c300:.3f} / {c90 / c300:.3f}')
pair('early/late clock: run 121 (0-10 / 0-300, derived) vs jump two-clock 0.775', c10 / c300, (c10 / c300) * math.hypot(w10 / c10, w300 / c300), 0.775, 0.009)
# spectators: hand kept (close_looktime.txt:5,9,10), precession (:11)
pair('hand kept 30 us: job 102 vs job 103', 0.7744, 0.0103, 0.7484, 0.0107)
pair('hand kept 30 us: job 101 vs job 102', 0.7585, 0.0084, 0.7744, 0.0103)
pair('hand kept 9 looks: job 101 vs job 102', 0.8307, 0.0086, 0.8166, 0.0100)
pair('hand kept 3 looks: job 102 vs job 103', 0.9225, 0.0067, 0.9184, 0.0067)
pair('precession deg/us: job 103 vs job 101', 3.3403, 0.1154, 3.0349, 0.1459)
pair('precession deg/us: job 103 vs job 102', 3.3403, 0.1154, 3.0581, 0.1318)
pair('coupling deg per 30 us: stopwatch 4.5 kHz (lower quartile 3.4 as bar) vs run 121', 48.6, 48.6 - 36.7, 16.9023, 1.8085)
pair('coupling deg per 30 us: run 121 |theta| median vs run 121 |hd|/5 (THREE_SEATS)', 16.9023, 1.8085, 8.238, 0.481)
pair('witness-timed / laid: stopwatch 40-us arm (no width) vs run 121 t_W / 30.016', 35.6 / 40, 0.0, 14.63 / 30.016, 0.85 / 30.016)
# the band (band.txt:12)
for k, (b, wb) in enumerate(((0.025, 0.155), (0.021, 0.060), (0.004, 0.125)), 1):
    pair(f'band R^2 at cutoff 0.65: 9/28 echo vs 10/2 read {k}', 0.433, 0.222, b, wb)
pair('band R^2 at cutoff 0.67: 9/28 echo vs 10/2 read 3', 0.384, 0.256, 0.367, 0.281)
# being watched (witness_run.txt:20; THREE_SEATS end levels)
pair('emitter end level, run 121 same train: A30_30 (neighbours pushed) vs WA (frame-held witnesses)', 0.3696, 0.0067, 0.3559, 0.0042)
pair('emitter end level, run 121 same train: B30_30 vs WB', 0.6858, 0.0060, 0.6819, 0.0045)
pair('watched minus not: stopwatch (-0.0029 +- 0.0086) vs run 121 WA - A30_30', -0.0029, 0.0086, 0.3559 - 0.3696, math.hypot(0.0067, 0.0042))
# Rigetti (ledger 98-125): fall time from |2> (intervals as printed; +- taken as half the interval)
pair('Rigetti q0 fall time: alternating alone vs full room (us; bars = printed intervals)', 26.6, 0.8, 31.2, 1.2, 'us')
pair('Rigetti fall time: whole-chip inside (q9) vs outside (q0 readout)', 14.8, 5.3, 31.2, 1.3, 'us')
pair('Rigetti fall time: headline inside (q9) vs outside (us, outside has no width)', 20.9, 6.5, 24.2, 0.0, 'us')
pair('Rigetti pull deg/us: headline vs full room', -62.1, 0.6, -59.9, 0.0)
pair('Rigetti q0 start heat %: alone vs full (rotated)', 3.85, 0.36, 4.96, 0.38)
pair('Rigetti q0 start heat %: alone vs middle trio (rotated)', 3.83, 0.36, 2.23, 0.35)

print('\n=== 7. FIRST-STRETCH CLOCKS (us) from middle-bit levels, each job; derived here (no widths: the reads print none for these levels)')
clk = lambda t, a, b: -t / math.log(b / a)
# lone_vs_tail.txt:5 (ON, no look), :27 (MID, no look): printed stretch clocks 208 / 123 (lone_vs_tail.txt:16,38) -- re-derived as a check
print(f'   lone 10:18  ON  0-6.7 {clk(6.72, 1.0, 0.9682):6.1f}  6.7-20 {clk(13.25, 0.9682, 0.9201):6.1f}  20-60 {clk(40.0, 0.9201, 0.7855):6.1f}  60-300 {clk(240.0, 0.7855, 0.3277):6.1f}')
print(f'   lone 10:18  MID 0-6.7 {clk(6.72, 1.0, 0.9467):6.1f}  6.7-20 {clk(13.25, 0.9467, 0.8829):6.1f}  20-60 {clk(40.0, 0.8829, 0.7665):6.1f}  60-300 {clk(240.0, 0.7665, 0.3227):6.1f}')
# sides.txt:4-9 (levels at none / 6.7 / 20, one read 11:53)
for lab, a, b, c in (('S0', 0.4930, 0.4685, 0.4481), ('S120', 0.4927, 0.4700, 0.4423), ('S240', 0.4995, 0.4731, 0.4414), ('S180', 0.4964, 0.4669, 0.4440),
                     ('FAR', 0.5280, 0.5157, 0.4868), ('ON', 1.0, 0.9646, 0.9163)):
    print(f'   sides 11:53 {lab:<5s} 0-6.7 {clk(6.72, a, b):6.1f}  6.7-20 {clk(13.25, b, c):6.1f}')
# hold_run.txt:37-42 (turns read, 12:05)
for lab, a, b, c in (('1 qt', 0.4965, 0.4764, 0.4440), ('3 qt (far)', 0.5270, 0.5171, 0.4911), ('5 qt', 0.4653, 0.4380, 0.4166), ('9 qt', 0.4412, 0.4223, 0.4001),
                     ('ON 2 qt', 1.0, 0.9695, 0.9200), ('ON 6 qt', 0.9984, 0.9645, 0.9258)):
    print(f'   turns 12:05 {lab:<10s} 0-6.7 {clk(6.72, a, b):6.1f}  6.7-20 {clk(13.25, b, c):6.1f}')
print('   half-push 11:02-11:43 (printed, half_push.txt:17-20): one-half-push 139 114 131 | far side 1732 452 201 | ON 219 201 196 | ON by two halves 209 214 228')
print('   halfway early clock over ON early clock, each job: lone 123/208 = %.3f; half-push %.3f %.3f %.3f; sides S0 %.3f S120 %.3f S240 %.3f S180 %.3f; turns 1qt %.3f 5qt %.3f 9qt %.3f' % (
    123 / 208, 139 / 219, 114 / 201, 131 / 196, clk(6.72, .4930, .4685) / clk(6.72, 1, .9646), clk(6.72, .4927, .4700) / clk(6.72, 1, .9646),
    clk(6.72, .4995, .4731) / clk(6.72, 1, .9646), clk(6.72, .4964, .4669) / clk(6.72, 1, .9646), clk(6.72, .4965, .4764) / clk(6.72, 1, .9695),
    clk(6.72, .4653, .4380) / clk(6.72, 1, .9695), clk(6.72, .4412, .4223) / clk(6.72, 1, .9695)))
print('   ON early over ON late, no earlier look: lone 208/275 = %.3f; sides %.3f; turns %.3f; half-push (0-6.7 / 6.7-20) %.3f %.3f %.3f' % (
    208 / 275, clk(6.72, 1, .9646) / clk(13.25, .9646, .9163), clk(6.72, 1, .9695) / clk(13.25, .9695, .9200), 219 / 248, 201 / 258, 196 / 258))

print('\n=== 9. THE HALFWAY ARM AS A PROTRACTOR: back-to-back pushes on the halfway state, level change = sin(N e)/2 (the model of ledger 1974 / 149); derived here')
# close_push.txt:8,9 ; rep_marrakesh_read1.txt:8,9 ; rep_kingston_read1.txt:8,9  (MID p2 / p10 back-to-back minus no push)
prot = {}
for chip, p2, p10 in (('Pittsburgh (3 jobs)', (-0.0262, 0.0019), (-0.1138, 0.0019)),
                      ('Marrakesh (1 job)', (0.0017, 0.0030), (-0.0176, 0.0032)),
                      ('Kingston (1 job)', (-0.0190, 0.0036), (-0.0513, 0.0036))):
    out = []
    for N, (d, w) in ((2, p2), (10, p10)):
        s = -2 * d; ang = math.asin(s); e = math.degrees(ang) / N; we = math.degrees(2 * w / math.cos(ang)) / N
        out.append((e, we)); print(f'   {chip:<20s} {N:2d} pushes: halfway {d:+.4f} +- {w:.4f}  ->  e = {e:+.3f} +- {we:.3f} deg')
    prot[chip] = out
pair('shortfall deg, Pittsburgh: halfway 10 X vs halfway 2 X', prot['Pittsburgh (3 jobs)'][1][0], prot['Pittsburgh (3 jobs)'][1][1], prot['Pittsburgh (3 jobs)'][0][0], prot['Pittsburgh (3 jobs)'][0][1])
pair('shortfall deg, Marrakesh: halfway 10 X vs halfway 2 X', prot['Marrakesh (1 job)'][1][0], prot['Marrakesh (1 job)'][1][1], prot['Marrakesh (1 job)'][0][0], prot['Marrakesh (1 job)'][0][1])
pair('shortfall deg, Kingston: halfway 10 X vs halfway 2 X', prot['Kingston (1 job)'][1][0], prot['Kingston (1 job)'][1][1], prot['Kingston (1 job)'][0][0], prot['Kingston (1 job)'][0][1])
pair('shortfall deg, Pittsburgh: halfway 10 X vs OFF/ON two-parameter solve 1.476 +- 0.135', prot['Pittsburgh (3 jobs)'][1][0], prot['Pittsburgh (3 jobs)'][1][1], 1.476, 0.135)
pair('shortfall deg, 10 X halfway: Pittsburgh vs Marrakesh', prot['Pittsburgh (3 jobs)'][1][0], prot['Pittsburgh (3 jobs)'][1][1], prot['Marrakesh (1 job)'][1][0], prot['Marrakesh (1 job)'][1][1])
pair('shortfall deg, 10 X halfway: Pittsburgh vs Kingston', prot['Pittsburgh (3 jobs)'][1][0], prot['Pittsburgh (3 jobs)'][1][1], prot['Kingston (1 job)'][1][0], prot['Kingston (1 job)'][1][1])
pair('shortfall deg, 10 X halfway: Marrakesh vs Kingston', prot['Marrakesh (1 job)'][1][0], prot['Marrakesh (1 job)'][1][1], prot['Kingston (1 job)'][1][0], prot['Kingston (1 job)'][1][1])
for chip, S10, w10 in (('Marrakesh (1 job)', 0.0295, 0.0019), ('Kingston (1 job)', 0.0404, 0.0023)):
    e = math.radians(prot[chip][1][0]); k = (S10 - 2 * math.sin(5 * e) ** 2) / 5
    print(f'   {chip:<20s} with e from its own 10-X halfway arm, the ten-push mirror leaves k = {100 * k:.3f} +- {100 * w10 / 5:.3f} % per push')

print('\n=== 8. THE THREE-CHIP MEAN of the crossing with each Pittsburgh witness in turn (%, derived here)')
for lab, p, wp in (('push run 2.00', 2.00, 0.16), ('hold run 2.17', 2.17, 0.17), ('run 121 A30_30 1.26', 1.26, 0.32)):
    m = (p + 2.74 + 2.87) / 3; w = math.sqrt(wp ** 2 + 0.28 ** 2 + 0.28 ** 2) / 3
    print(f'   {lab:<22s} -> mean {m:.3f} +- {w:.3f}   (against 100/(12 pi) = {100 / (12 * math.pi):.4f}: gap {m - 100 / (12 * math.pi):+.3f}, {(m - 100 / (12 * math.pi)) / w:+.2f} widths)')
