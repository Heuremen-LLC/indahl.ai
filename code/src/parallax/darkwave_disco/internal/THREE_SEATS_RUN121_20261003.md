# THREE SEATS ON ONE EVENT -- run 121, ibm_pittsburgh (the no-name shot)

script: `internal/three_seats_run121.py`  sha256 `e9fe06c0a7f3ed186c008dbfcc1b4e816d20f4c731bf7899fcaaabde094d9d10`  
made 2026-10-03T13:50:06-04:00 by Bones, internal. Read-only on the data, the frozen code and the ledger. Nothing was submitted anywhere.  
numbers in full: `internal/three_seats_run121_20261003.json`. Reader copy used: `internal/readnoname_copy_20261003.py` (byte-identical to the frozen reader).

**Clocks (The Stake).** LAID = our laid times on the maker's tick (realized stretches 9.984 / 30.016 / 89.984 us). WITNESS = the frame-held spectator's phase, in degrees. OWN = the emitter's own end level and its own fading rulers (R10/R30/R90/R300, same job). Every width is over shots (the reader's bootstrap, NB = 100) unless it says otherwise. A † marks a reading within one width of zero: too thin to read.

## Method

- **Data.** `run121_results.npz` (21 circuits x 216 shots x 156 bits, kerneled IQ points), sha256 matches `run121_meta.json` results_sha256. Roles from `reads/noname_roles.json` (Pittsburgh static wiring at fire; 39 emitters, 86 witnesses). Readable bits as the reader takes them (cloud separation > 4 widths): 6 unreadable (32, 37, 47, 137, 149, 155), leaving **75 witness-emitter pairs on 35 emitters** (the reader's 75 / 35). Dropped pairs: 155-154, 37-25, 148-149, 150-149, 48-47, 57-47, 46-47, 147-137, 127-137, 33-32, 31-32.
- **Level.** `readnoname.frame()`: every shot's IQ point projected on the line from the OFF cloud (F0) to the ON cloud (F1); a bit's level = mean over shots (0 = OFF cloud, 1 = ON cloud). Same function, same rule.
- **SEAT 1 (OWN, short clock)** = emitter end level minus `readnoname.book(start, [R_L per stretch], flip)`, where R_L is the same bit's ON-left-alone level at that stretch length (R10 / R30 / R90, clipped 0.02-1.2): the reader's "minus each-stretch-own-ruler book", per bit.
- **SEAT 2 (OWN, long clock)** = emitter end level minus `book(start, [R300^(L/300) per stretch], flip)` (R300 clipped 0.02-0.98): the reader's "minus one-clock book", per bit.
- **Arms where seats 1-2 are read (12).** The ten core arms (every bit pushed alike) and the two witness arms, where the emitter gets the same train as A30_30 (WA, started OFF) or B30_30 (WB, started ON) while its witnesses hold frame; there its level is the mean of the X-hand and Y-hand circuits and its own book uses R30 (clipped 0.02-0.999) for all ten stretches, exactly as the reader's witness section does. "pool" = equal-weight mean of a pair's twelve arms; "core" = mean of the ten core arms.
- **Arm names (from `noname.py`).** `A{off}_{on}`: start OFF; the FIRST stretch is OFF; stretches alternate OFF {off} us, ON {on} us, five of each, ten pushes (a push after every stretch), ends OFF. So **A30_10 = OFF stretches 30 us, ON stretches 10 us**. `f` = one more push at once at the end (ends flipped). `B30_30`: start ON, first stretch ON. N2 / N6: OFF start, 2 / 6 pushes, 30-us stretches. WA / WB: the witness arms (emitter as A30_30 / B30_30).
- **SEAT 3 (WITNESS).** Only the witness arms carry a witness reading: in every core arm the witness bits are pushed like everyone else and read on Z, so they carry no phase. The witness vector per start is v = (2 level_X - 1) + i (1 - 2 level_Y) from its two hand circuits (the reader's va, vb). Primary reading: the reader's half-difference, hd = angle(vb conj va) / 2, the part that flips with the emitter's start; it carries coupling x the emitter's signed ON time over the **5 LAID ON stretches** of each start, so **seat 3 = |hd| / 5, WITNESS degrees per LAID ON stretch**. It uses no emitter ruler, so it shares no OWN number with seats 1-2. Second reading: the reader's `fit_witness` coupling theta (deg per 30-us ON stretch) with the emitter's own R30 fading inside the model (OWN inside, WITNESS out), and the same fit with the chip-typical R30 (0.8875). hd lives in (-90, +90] deg, so |hd| / 5 has a ceiling at 18 deg per stretch (a reading past it folds back).
- **Equivalent time.** t_W = 30.016 us x (|hd|/5) / 16.9023 deg: the ON time per LAID 30.016-us ON stretch the witness reads if every pair had the reader's ensemble coupling (median |theta|, own fading). One constant for all pairs, so per pair t_W is seat 3 on another scale; per-pair coupling and per-pair ON time are not separated by this job (one stretch pattern in the witness arms).
- **Widths.** Shot bootstrap exactly as `readnoname.py` (seed 20261004, NB = 100, each of the 21 circuits resampled on its own, the pair list held fixed from the full data). Because the draws are the reader's own, the reader's run-121 read was rebuilt from the same resamples: **83 of 83 lines of `reads/noname_read1.txt` reproduced exactly** (value and width, 4 decimals). Correlations carry a second, labelled width over emitters (35 drawn with replacement, their witnesses with them, 2000 draws, seed 20261003), because pairs on one emitter share seats 1-2. Shot-order thirds (72 shots each) give each seat's agreement with itself.
- **Co-movement.** Pearson r across the 75 pairs (each pair once; an emitter with three witnesses counts three times), per arm and pooled; also Spearman and the 35-emitter version (seat 3 averaged over an emitter's witnesses) for the pooled seats.
- **Integrity.** Frozen code/reads checked against `for_indahl_ai/data/SHA256SUMS.txt` and the data against the meta before the read: all match; re-hashed after: unchanged; __pycache__ in the frozen code dir: none.

## Per arm: the pooled seats

Means over the 75 pairs (each pair's emitter, so an emitter counts once per witness), width over shots. "150 bits" = the reader's own all-readable-bit number for the same arm (seat 1 for WA/WB is the reader's 35-emitter line). Seat 3 exists only where a witness held frame.

| arm | what the emitter got (LAID) | LAID ON / total us | end level (OWN), pairs | SEAT 1 OWN short, pairs | SEAT 2 OWN long, pairs | SEAT 1 / SEAT 2, 150 bits (reader) | SEAT 3 WITNESS, deg per LAID ON stretch |
|---|---|---|---|---|---|---|---|
| A30_30 | start OFF, OFF 30 us / ON 30 us stretches, 10 pushes, ends OFF | 150.08 / 300.16 | +0.3696 (0.0067) | -0.0108 (0.0117)† | +0.0218 (0.0072) | -0.0097 (0.0051) / +0.0126 (0.0032) | -- |
| A10_30 | start OFF, OFF 10 us / ON 30 us stretches, 10 pushes, ends OFF | 150.08 / 200.00 | +0.4035 (0.0061) | -0.0378 (0.0139) | +0.0102 (0.0085) | -0.0139 (0.0071) / +0.0147 (0.0037) | -- |
| A90_30 | start OFF, OFF 90 us / ON 30 us stretches, 10 pushes, ends OFF | 150.08 / 600.00 | +0.2692 (0.0063) | -0.0195 (0.0122) | +0.0119 (0.0062) | -0.0007 (0.0054) / +0.0270 (0.0029) | -- |
| A30_10 | start OFF, OFF 30 us / ON 10 us stretches, 10 pushes, ends OFF | 49.92 / 200.00 | +0.1589 (0.0048) | +0.0289 (0.0117) | +0.0227 (0.0051) | +0.0170 (0.0064) / +0.0291 (0.0024) | -- |
| A30_90 | start OFF, OFF 30 us / ON 90 us stretches, 10 pushes, ends OFF | 449.92 / 600.00 | +0.6955 (0.0059) | +0.0090 (0.0115)† | +0.0034 (0.0071)† | -0.0062 (0.0046) / -0.0050 (0.0033) | -- |
| A30_30f | start OFF, OFF 30 us / ON 30 us stretches, 10 pushes + 1 at once, ends ON | 150.08 / 300.16 | +0.6494 (0.0057) | +0.0298 (0.0107) | -0.0029 (0.0067)† | +0.0091 (0.0052) / -0.0133 (0.0033) | -- |
| B30_30 | start ON, OFF 30 us / ON 30 us stretches, 10 pushes, ends ON | 150.08 / 300.16 | +0.6858 (0.0060) | +0.0179 (0.0087) | -0.0041 (0.0067)† | -0.0021 (0.0046) / -0.0022 (0.0031) | -- |
| B30_30f | start ON, OFF 30 us / ON 30 us stretches, 10 pushes + 1 at once, ends OFF | 150.08 / 300.16 | +0.3131 (0.0063) | -0.0190 (0.0090) | +0.0030 (0.0070)† | +0.0014 (0.0046) / +0.0015 (0.0032) | -- |
| N2 | start OFF, OFF 30 us / ON 30 us stretches, 2 pushes, ends OFF | 30.02 / 60.03 | +0.1210 (0.0046) | -0.0011 (0.0069)† | +0.0163 (0.0049) | -0.0012 (0.0034) / +0.0245 (0.0025) | -- |
| N6 | start OFF, OFF 30 us / ON 30 us stretches, 6 pushes, ends OFF | 90.05 / 180.10 | +0.2738 (0.0054) | -0.0112 (0.0105) | +0.0205 (0.0066) | -0.0058 (0.0052) / +0.0207 (0.0034) | -- |
| WA | start OFF, OFF 30 us / ON 30 us stretches, 10 pushes, ends OFF | 150.08 / 300.16 | +0.3559 (0.0042) | -0.0245 (0.0107) | +0.0081 (0.0058) | -0.0216 (0.0102) / -- | 8.24 (0.48), one reading for WA and WB together |
| WB | start ON, OFF 30 us / ON 30 us stretches, 10 pushes, ends ON | 150.08 / 300.16 | +0.6819 (0.0045) | +0.0140 (0.0074) | -0.0080 (0.0051) | +0.0118 (0.0076) / -- | 8.24 (0.48), one reading for WA and WB together |
| pool | all twelve arms, equal weight | -- | -- | -0.0020 (0.0041)† | +0.0086 (0.0025) | -- | -- |
| core | the ten core arms | -- | -- | -0.0014 (0.0045)† | +0.0103 (0.0028) | -- | -- |

Same rows over the 35 emitters (each once): A30_30 -0.0100 (0.0114) / +0.0213 (0.0071); A10_30 -0.0360 (0.0131) / +0.0104 (0.0079); A90_30 -0.0175 (0.0116) / +0.0119 (0.0061); A30_10 +0.0302 (0.0107) / +0.0228 (0.0050); A30_90 +0.0095 (0.0108) / +0.0073 (0.0067); A30_30f +0.0232 (0.0102) / -0.0081 (0.0067); B30_30 +0.0151 (0.0084) / -0.0061 (0.0065); B30_30f -0.0168 (0.0086) / +0.0044 (0.0067); N2 -0.0006 (0.0064) / +0.0160 (0.0047); N6 -0.0096 (0.0102) / +0.0208 (0.0065); WA -0.0216 (0.0100) / +0.0097 (0.0057); WB +0.0118 (0.0074) / -0.0094 (0.0052); pool -0.0019 (0.0038) / +0.0084 (0.0024); core -0.0012 (0.0042) / +0.0101 (0.0027) (seat 1 / seat 2, OWN).

**Seat 3 pooled (WITNESS):**

| reading | value (width over shots) |
|---|---|
| |hd|/5, mean over 75 pairs, WITNESS deg per LAID ON stretch | 8.238 (0.481) |
| |hd|/5, median over pairs | 8.014 (0.815) |
| signed hd/5, mean over pairs (the reader's half-difference line / 5) | -2.495 (0.989) |
| pairs with hd < 0 | 52 of 75 |
| pairs where |hd|/5 sits within one width of zero (too thin to read one by one) | 21 of 75 |
| |fitted coupling|, own fading, median, pair set held fixed (the reader's line, its witness set redrawn per resample: +16.9023 (1.8085)) | 16.902 (1.865) |
| |fitted coupling|, own fading, mean | 17.342 (1.032) |
| |fitted coupling|, chip-typical fading, median | 16.329 (1.557) |
| fitted coupling < 0 (own fading) | 42 of 75 |
| fit on the grid edge (|theta| >= 33 deg), own / typical fading | 4 / 3 pairs |
| own-fading and typical-fading fits more than 10 deg apart | 11 pairs |
| own-fading fit jumps > 10 deg from its full-data value in > 1/3 of shot resamples | 53 pairs (median jump fraction 0.47) |
| t_W, WITNESS-equivalent ON time per LAID 30.016-us ON stretch, mean / median | 14.63 (0.85) / 14.23 (1.45) us |
| t_W minus the LAID 30.016 us, mean (WITNESS minus LAID, per ON stretch) | -15.39 (0.85) us |
| the reader's own model, chip-typical OWN fading, at the 16.90-deg coupling: half-difference it books over 5 LAID ON stretches | 58.48 deg (11.70 per stretch; LAID-only, no fading: 84.51) |
| witness hand length, started OFF / ON (mean) | 0.1603 (0.0069) / 0.1625 (0.0074) |
| witness half-sum, its own leftover (mean, deg) | +0.596 (4.384) |

## Across pairs: how seat 3 moves with seats 1 and 2

Pearson r across the 75 pairs. First width over shots (the reader's resamples), second [in brackets] over emitters. Seat 3 here = |hd|/5 (WITNESS). Seat 3 is one reading per pair; each row pairs it with that arm's seats 1-2 (OWN). Last column: seat 1 against seat 2 in the same arm (they share the end level).

| arm | r(seat 3, seat 1) | r(seat 3, seat 2) | r(seat 1, seat 2) |
|---|---|---|---|
| A30_30 | -0.015 (0.115) [0.107]† | +0.030 (0.111) [0.112]† | +0.560 (0.115) [0.113] |
| A10_30 | +0.007 (0.107) [0.116]† | +0.127 (0.114) [0.107] | +0.432 (0.140) [0.128] |
| A90_30 | +0.079 (0.111) [0.114]† | +0.140 (0.116) [0.107] | +0.485 (0.131) [0.120] |
| A30_10 | +0.084 (0.097) [0.129]† | -0.006 (0.119) [0.099]† | +0.356 (0.137) [0.150] |
| A30_90 | -0.040 (0.103) [0.139]† | +0.015 (0.106) [0.139]† | +0.550 (0.105) [0.141] |
| A30_30f | +0.014 (0.110) [0.110]† | -0.027 (0.103) [0.103]† | +0.666 (0.114) [0.080] |
| B30_30 | -0.022 (0.105) [0.112]† | -0.074 (0.109) [0.123]† | +0.648 (0.103) [0.098] |
| B30_30f | +0.130 (0.101) [0.103] | +0.175 (0.103) [0.092] | +0.813 (0.070) [0.058] |
| N2 | +0.016 (0.115) [0.136]† | +0.069 (0.106) [0.155]† | +0.638 (0.100) [0.085] |
| N6 | -0.003 (0.105) [0.103]† | +0.054 (0.113) [0.127]† | +0.488 (0.121) [0.125] |
| WA | +0.065 (0.118) [0.097]† | +0.139 (0.113) [0.106] | +0.578 (0.116) [0.093] |
| WB | +0.001 (0.101) [0.097]† | -0.050 (0.103) [0.101]† | +0.637 (0.141) [0.068] |
| pool | +0.068 (0.111) [0.113]† | +0.120 (0.111) [0.093] | +0.660 (0.094) [0.104] |
| core | +0.061 (0.110) [0.116]† | +0.114 (0.114) [0.093]† | +0.625 (0.097) [0.107] |

Same table with seat 3 = the reader's fitted |coupling|, own fading (OWN R30 inside the fit):

| arm | r(|theta own|, seat 1) | r(|theta own|, seat 2) |
|---|---|---|
| A30_30 | +0.134 (0.124) [0.112] | +0.083 (0.105) [0.126]† |
| A10_30 | +0.113 (0.121) [0.101]† | +0.133 (0.112) [0.116] |
| A90_30 | +0.091 (0.115) [0.119]† | +0.024 (0.117) [0.141]† |
| A30_10 | +0.052 (0.102) [0.134]† | -0.099 (0.115) [0.104]† |
| A30_90 | -0.072 (0.110) [0.165]† | +0.018 (0.119) [0.141]† |
| A30_30f | -0.129 (0.122) [0.095] | -0.101 (0.108) [0.119]† |
| B30_30 | -0.009 (0.121) [0.113]† | +0.048 (0.122) [0.142]† |
| B30_30f | +0.084 (0.111) [0.133]† | +0.054 (0.109) [0.121]† |
| N2 | +0.030 (0.128) [0.123]† | -0.028 (0.127) [0.150]† |
| N6 | +0.024 (0.122) [0.123]† | -0.046 (0.116) [0.143]† |
| WA | +0.098 (0.112) [0.119]† | +0.060 (0.109) [0.138]† |
| WB | -0.109 (0.114) [0.111]† | -0.089 (0.102) [0.106]† |
| pool | +0.066 (0.120) [0.129]† | +0.025 (0.117) [0.112]† |
| core | +0.069 (0.122) [0.134]† | +0.030 (0.119) [0.110]† |

Pooled seats 1-2 against every seat-3 reading (Pearson over pairs; Spearman over pairs; Pearson over the 35 emitters):

| seat 3 reading (WITNESS) | r(.., seat 1 pool) | r(.., seat 2 pool) | Spearman seat 1 / seat 2 | 35 emitters seat 1 / seat 2 |
|---|---|---|---|---|
| |half-difference| / 5 | +0.068 (0.111) [0.113]† | +0.120 (0.111) [0.093] | +0.029 (0.110) / +0.141 (0.115) | +0.165 (0.152) [0.150] / +0.185 (0.158) [0.127] |
| |fitted coupling|, own fading | +0.066 (0.120) [0.129]† | +0.025 (0.117) [0.112]† | +0.054 (0.119) / +0.045 (0.114) | +0.117 (0.166) [0.167] / +0.052 (0.167) [0.158] |
| signed half-difference / 5 | +0.078 (0.110) [0.113]† | +0.082 (0.101) [0.134]† | +0.113 (0.112) / +0.123 (0.102) | +0.191 (0.155) [0.183] / +0.058 (0.151) [0.194] |
| |fitted coupling|, chip-typical fading | +0.015 (0.116) [0.120]† | +0.047 (0.115) [0.106]† | -0.011 (0.115) / +0.035 (0.119) | +0.058 (0.166) [0.174] / +0.110 (0.163) [0.159] |

**Largest |r| between a seat-3 reading and seat 1 or 2**, over every row of the three tables above (128 correlations computed in all; their shot widths run 0.086-0.167): signed hd/5 with seat 1, pool (35 emitters): +0.191 (0.155) [0.183]; |hd|/5 with seat 2, pool (35 emitters): +0.185 (0.158) [0.127]; |hd|/5 with seat 2, B30_30f: +0.175 (0.103) [0.092]; |hd|/5 with seat 1, pool (35 emitters): +0.165 (0.152) [0.150]; |theta typ| with seat 2, B30_30f: +0.145 (0.117) [0.102]; |hd|/5 with seat 2, pool (Spearman): +0.141 (0.115) [0.107].

**How much of each seat stands above its own shot noise.** SD across emitters (seats 1-2, the end level) or pairs (seat 3), against the noise of one reading two ways: the RMS of the shot-bootstrap widths, and the noise read from the differences between shot-order thirds (72 shots each, scaled to 216 shots), which uses no resampling at all. Last column: each seat against itself across the thirds (r for thirds 1-2, 1-3, 2-3).

| seat | SD across | RMS shot width (bootstrap) | noise from thirds | r across thirds |
|---|---|---|---|---|
| end level A30_30 (OWN), 35 emitters, for reference | 0.0583 | 0.0356 | 0.0405 | +0.45, +0.25, +0.08 |
| seat 1 pool (OWN), 35 emitters | 0.0236 | 0.0233 | 0.0230 | -0.24, +0.19, +0.07 |
| seat 2 pool (OWN), 35 emitters | 0.0175 | 0.0156 | 0.0173 | -0.14, +0.17, -0.04 |
| seat 1 A30_30 (OWN), 35 emitters | 0.0525 | 0.0654 | 0.0573 | +0.12, +0.04, -0.29 |
| seat 1 A30_10 (OWN), 35 emitters | 0.0751 | 0.0756 | 0.0782 | -0.18, -0.04, +0.17 |
| seat 1 B30_30 (OWN), 35 emitters | 0.0412 | 0.0498 | 0.0477 | +0.06, -0.17, +0.03 |
| seat 1 WA (OWN), 35 emitters | 0.0559 | 0.0596 | 0.0530 | +0.30, -0.13, +0.13 |
| seat 1 WB (OWN), 35 emitters | 0.0422 | 0.0441 | 0.0401 | +0.15, -0.08, +0.20 |
| seat 3 |hd|/5 (WITNESS deg), 75 pairs | 5.1809 | 3.8941 | 2.6895 | +0.11, +0.34, -0.01 |
| seat 3 |theta own| (WITNESS deg), 75 pairs | 10.5019 | 8.9198 | 5.6349 | +0.06, +0.12, -0.09 |
| seat 3 signed hd/5 (WITNESS deg), 75 pairs | 9.4510 | 8.2646 | 5.6249 | +0.22, +0.00, +0.02 |

The thirds' scaling (noise of one 72-shot reading / 3 in variance) holds for seats 1-2 (sums of levels) and runs low for seat 3, an angle of a short vector that saturates: the shot-bootstrap RMS width of |hd|/5 is 3.89 deg at 216 shots and 4.39 at 72 shots (ratio 1.13; 1/sqrt(shots) would give 1.73). By the witness hand length (mean of |va|, |vb|): 0.00-0.12 (25 pairs) 4.73 at 216 / 4.79 at 72; 0.12-0.20 (30 pairs) 3.91 at 216 / 4.36 at 72; 0.20-9.00 (20 pairs) 2.44 at 216 / 3.90 at 72. A reading spread evenly over 0-18 deg has SD 5.20. So for seat 3 the bootstrap width is the one used throughout.

Seat 3 inside one emitter: 30 emitters have two or three readable witnesses (70 pairs); their witnesses read the same shots of the same emitter. Seat 3 (|hd|/5, WITNESS deg per LAID ON stretch) spreads within an emitter by 5.07 (0.48), and the emitters' means spread by 3.38 (0.35); one pair's shot width there is 3.90.

The same push train read twice on each emitter (core arm vs witness arm), across the 35 emitters. End level (OWN, no book): A30_30 against WA r = +0.787 (0.085) [0.081]; B30_30 against WB r = +0.779 (0.084) [0.062]. Seat 1: +0.765 (0.073) [0.076] and +0.729 (0.089) [0.078]; seat 2: +0.629 (0.108) and +0.465 (0.139) (both arms' books are built from the same emitter's R30 / R300 shots, so the seat-1 and seat-2 retests carry the ruler's own shot noise twice). Seat-3 readings against each other: |hd|/5 with |theta own| r = +0.498 (0.089); |theta own| with |theta typ| r = +0.749 (0.095); |hd|/5 with the witness hand length r = +0.095 (0.082).

Within each shot-order third (72 shots; thirds 1, 2, 3), r(seat 3 WITNESS, pooled seat OWN) over the 75 pairs: |hd|/5 with pooled seat 1: +0.22, +0.07, +0.12; |hd|/5 with pooled seat 2: +0.25, +0.03, +0.03; |theta own| with pooled seat 1: -0.05, -0.03, +0.12; |theta own| with pooled seat 2: +0.07, -0.01, +0.18.

## Per pair: fingerprints (top and bottom 10 by pooled seat 1)

Spread = SD of the pair's seat across its twelve arms (OWN); "beyond" = the same after taking off the chip's own arm-to-arm pattern (the 35-emitter mean per arm); "noise-only" = the spread across the same twelve arms that shot noise alone draws (SD across arms of resample minus full data, RMS over the 100 resamples; the arms share their rulers, so their noise partly moves together and this keeps that). Pairs on one emitter share seats 1-2. Emitter grid place = (row on the doubled grid, column), see the map. "jump frac" = share of shot resamples in which the fitted coupling lands more than 10 deg from its full-data value.

| # | witness-emitter | emitter at | SEAT 1 pool OWN | SEAT 2 pool OWN | SEAT 3 |hd|/5 WITNESS deg / LAID stretch | theta own WITNESS deg (jump frac) | t_W WITNESS us / LAID 30.016 us | seat-1 spread raw / beyond / noise-only | seat-2 spread raw / beyond / noise-only |
|---|---|---|---|---|---|---|---|---|---|
| top 1 | 81-82 | (8, 2) | +0.0518 (0.0243) | +0.0520 (0.0158) | 7.11 (0.99) | -9.17 (10.79) (0.08) | 12.63 (1.75) | 0.0653 / 0.0733 / 0.0629 | 0.0693 / 0.0613 / 0.0349 |
| top 2 | 83-82 | (8, 2) | +0.0518 (0.0243) | +0.0520 (0.0158) | 6.84 (5.13) | +8.88 (19.09) (0.54) | 12.15 (9.11) | 0.0653 / 0.0733 / 0.0629 | 0.0693 / 0.0613 / 0.0349 |
| top 3 | 107-97 | (9, 7) | +0.0411 (0.0213) | +0.0635 (0.0151) | 11.37 (4.79) | +27.22 (22.60) (0.33) | 20.20 (8.50) | 0.0345 / 0.0222 / 0.0569 | 0.0426 / 0.0351 / 0.0349 |
| top 4 | 87-97 | (9, 7) | +0.0411 (0.0213) | +0.0635 (0.0151) | 14.67 (3.97) | -19.77 (19.72) (0.47) | 26.05 (7.05) | 0.0345 / 0.0222 / 0.0569 | 0.0426 / 0.0351 / 0.0349 |
| top 5 | 61-60 | (6, 0) | +0.0331 (0.0276) | -0.0002 (0.0153)† | 15.61 (3.94) | -22.92 (20.87) (0.54) | 27.72 (7.00) | 0.0826 / 0.0940 / 0.0786 | 0.0155 / 0.0137 / 0.0351 |
| top 6 | 49-38 | (3, 9) | +0.0289 (0.0316)† | +0.0174 (0.0213)† | 12.40 (4.56) | +27.50 (23.72) (0.41) | 22.01 (8.09) | 0.0927 / 0.0782 / 0.0662 | 0.0281 / 0.0342 / 0.0373 |
| top 7 | 29-38 | (3, 9) | +0.0289 (0.0316)† | +0.0174 (0.0213)† | 12.48 (2.22) | +27.50 (23.15) (0.57) | 22.17 (3.94) | 0.0927 / 0.0782 / 0.0662 | 0.0281 / 0.0342 / 0.0373 |
| top 8 | 67-66 | (6, 6) | +0.0278 (0.0246) | +0.0188 (0.0141) | 11.19 (4.81) | -14.61 (19.15) (0.71) | 19.86 (8.54) | 0.0536 / 0.0671 / 0.0705 | 0.0359 / 0.0341 / 0.0358 |
| top 9 | 65-66 | (6, 6) | +0.0278 (0.0246) | +0.0188 (0.0141) | 4.00 (5.13)† | +32.37 (23.28) (0.66) | 7.11 (9.11) | 0.0536 / 0.0671 / 0.0705 | 0.0359 / 0.0341 / 0.0358 |
| top 10 | 139-135 | (12, 15) | +0.0234 (0.0216) | +0.0130 (0.0161)† | 12.17 (3.09) | -25.50 (16.72) (0.18) | 21.62 (5.48) | 0.0396 / 0.0487 / 0.0649 | 0.0306 / 0.0327 / 0.0356 |
| ... | | | | | | | | | |
| bottom 10 | 1-0 | (0, 0) | -0.0269 (0.0173) | +0.0004 (0.0138)† | 8.14 (4.45) | -15.47 (20.93) (0.46) | 14.45 (7.90) | 0.0704 / 0.0537 / 0.0483 | 0.0170 / 0.0186 / 0.0328 |
| bottom 9 | 151-138 | (13, 11) | -0.0287 (0.0223) | -0.0062 (0.0152)† | 4.85 (4.21) | +32.09 (22.09) (0.52) | 8.62 (7.47) | 0.0468 / 0.0390 / 0.0575 | 0.0235 / 0.0233 / 0.0338 |
| bottom 8 | 131-138 | (13, 11) | -0.0287 (0.0223) | -0.0062 (0.0152)† | 12.96 (2.66) | +26.07 (22.63) (0.54) | 23.01 (4.73) | 0.0468 / 0.0390 / 0.0575 | 0.0235 / 0.0233 / 0.0338 |
| bottom 7 | 101-100 | (10, 0) | -0.0312 (0.0260) | -0.0068 (0.0170)† | 9.18 (4.09) | -13.75 (16.12) (0.27) | 16.31 (7.26) | 0.0718 / 0.0572 / 0.0586 | 0.0374 / 0.0346 / 0.0348 |
| bottom 6 | 125-117 | (11, 5) | -0.0318 (0.0191) | +0.0043 (0.0149)† | 17.01 (4.17) | -25.21 (22.70) (0.54) | 30.20 (7.41) | 0.0469 / 0.0449 / 0.0458 | 0.0410 / 0.0347 / 0.0330 |
| bottom 5 | 105-117 | (11, 5) | -0.0318 (0.0191) | +0.0043 (0.0149)† | 8.69 (4.97) | -30.08 (26.66) (0.55) | 15.44 (8.83) | 0.0469 / 0.0449 / 0.0458 | 0.0410 / 0.0347 / 0.0330 |
| bottom 4 | 71-70 | (6, 10) | -0.0372 (0.0223) | +0.0101 (0.0134)† | 17.62 (2.18) | +24.06 (24.68) (0.52) | 31.30 (3.87) | 0.0574 / 0.0448 / 0.0546 | 0.0489 / 0.0412 / 0.0339 |
| bottom 3 | 69-70 | (6, 10) | -0.0372 (0.0223) | +0.0101 (0.0134)† | 3.49 (3.35) | -6.59 (15.23) (0.25) | 6.20 (5.95) | 0.0574 / 0.0448 / 0.0546 | 0.0489 / 0.0412 / 0.0339 |
| bottom 2 | 5-4 | (0, 4) | -0.0434 (0.0194) | -0.0149 (0.0163)† | 10.70 (5.33) | +16.62 (21.61) (0.61) | 19.00 (9.46) | 0.0463 / 0.0460 / 0.0515 | 0.0480 / 0.0447 / 0.0358 |
| bottom 1 | 3-4 | (0, 4) | -0.0434 (0.0194) | -0.0149 (0.0163)† | 12.27 (2.44) | +27.50 (20.11) (0.25) | 21.78 (4.33) | 0.0463 / 0.0460 / 0.0515 | 0.0480 / 0.0447 / 0.0358 |

Over all 75 pairs: seat-1 spread raw median 0.0488, beyond the chip pattern median 0.0460, noise-only median 0.0582 (18 of 75 pairs, on 9 of 35 emitters, spread beyond the chip pattern by more than their noise-only spread); seat-2 spread raw median 0.0369, beyond 0.0347, noise-only 0.0345 (39 of 75 pairs above their noise-only spread). Chip pattern of seat 1 across the arms (35-emitter means, OWN): A30_30 -0.0100, A10_30 -0.0360, A90_30 -0.0175, A30_10 +0.0302, A30_90 +0.0095, A30_30f +0.0232, B30_30 +0.0151, B30_30f -0.0168, N2 -0.0006, N6 -0.0096, WA -0.0216, WB +0.0118.

## Where on the chip the pairs that move together sit

Each pair's share of the pooled correlation: c = z(seat 3) x z(pooled seat), z taken across the 75 pairs (the mean of c is r). Map marks each witness bit by its pair's c, in thirds of 25: `+` top third (seat 3 and the seat on the same side of their means: moving together), `o` middle third, `-` bottom third (on opposite sides). `E` emitter, `x` unreadable bit, `w` readable witness whose emitter is unreadable, `.` bit left alone. Rows: even rows are the 16-bit lines (q20r..20r+15), odd rows the four bridge bits under them. Layout: Pittsburgh's wiring as read at fire (`noname_roles.json` edges, identical to `layout_156_family.json`).

**Seat 3 with pooled seat 1** (r = +0.068 (0.111)):
```
             col 0 1 2 3 4 5 6 7 8 9 a b c d e f
q  0-15              E o . - E - o E - . - E - + E o
 bridges 16-19             .       o       -       -
q 20-35              . + E o + E - . . + . w x w + E
 bridges 36-39         .       x       E       o    
q 40-55              . + E - . . w x w + . . - E o .
 bridges 56-59             -       w       .       .
q 60-75              E + + E + - E + . + E - . o E o
 bridges 76-79         .       +       o       .    
q 80-95              . - E - o E + + o E - o E o . o
 bridges 96-99             +       E       o       E
q100-115             E - o E - o . + . . - E - o . o
 bridges 116-119       .       E       +       E    
q120-135             E + - E - - . w + E + - . + o E
 bridges 136-139           -       x       E       +
q140-155             . o E o o E o w w x w + . + E x
```
**Seat 3 with pooled seat 2** (r = +0.120 (0.111)):
```
             col 0 1 2 3 4 5 6 7 8 9 a b c d e f
q  0-15              E o . - E - o E - . - E - + E +
 bridges 16-19             .       -       -       -
q 20-35              . o E o + E - . . + . w x w + E
 bridges 36-39         .       x       E       -    
q 40-55              . o E o . . w x w + . . + E o .
 bridges 56-59             -       w       .       .
q 60-75              E - + E + - E + . o E o . + E o
 bridges 76-79         .       +       o       .    
q 80-95              . - E - o E + + o E o o E o . o
 bridges 96-99             -       E       -       E
q100-115             E - - E + o . + . . + E + o . o
 bridges 116-119       .       E       -       E    
q120-135             E + + E o - . w - E - - . + o E
 bridges 136-139           +       x       E       o
q140-155             . o E o - E + w w x w + . + E x
```

By region (3 x 3, placed by the emitter): mean c over the region's pairs, width over shots.

| rows | columns | pairs (emitters) | emitters | SEAT 3 |hd|/5 WITNESS deg | SEAT 1 pool OWN | SEAT 2 pool OWN | mean c, seat 3 x seat 1 | mean c, seat 3 x seat 2 |
|---|---|---|---|---|---|---|---|---|
| top (q0-55) | left (cols 0-4) | 7 (4) | 0, 4, 22, 42 | 10.38 (1.38) | -0.0093 (0.0127)† | +0.0014 (0.0089)† | -0.188 (0.324)† | -0.216 (0.278)† |
| top (q0-55) | centre (cols 5-10) | 7 (3) | 7, 25, 38 | 9.97 (1.60) | +0.0033 (0.0146)† | +0.0055 (0.0097)† | +0.195 (0.347)† | -0.105 (0.403)† |
| top (q0-55) | right (cols 11-15) | 10 (4) | 11, 14, 35, 53 | 6.66 (1.33) | +0.0029 (0.0105)† | +0.0015 (0.0081)† | -0.084 (0.265)† | +0.222 (0.325)† |
| middle (q56-99) | left (cols 0-4) | 6 (3) | 60, 63, 82 | 8.53 (1.46) | +0.0125 (0.0134)† | +0.0197 (0.0090) | +0.263 (0.432)† | -0.310 (0.428)† |
| middle (q56-99) | centre (cols 5-10) | 12 (5) | 66, 70, 85, 89, 97 | 7.62 (1.29) | +0.0020 (0.0110)† | +0.0167 (0.0064) | +0.277 (0.343)† | +0.626 (0.368) |
| middle (q56-99) | right (cols 11-15) | 6 (3) | 74, 92, 99 | 6.97 (1.23) | -0.0117 (0.0126)† | +0.0032 (0.0086)† | +0.083 (0.213)† | +0.221 (0.302)† |
| bottom (q100-155) | left (cols 0-4) | 10 (5) | 100, 103, 120, 123, 142 | 6.20 (1.10) | -0.0039 (0.0134)† | +0.0068 (0.0080)† | -0.168 (0.269)† | +0.133 (0.255)† |
| bottom (q100-155) | centre (cols 5-10) | 7 (3) | 117, 129, 145 | 7.10 (1.79) | -0.0179 (0.0119) | +0.0067 (0.0087)† | +0.026 (0.336)† | -0.258 (0.301)† |
| bottom (q100-155) | right (cols 11-15) | 10 (5) | 111, 119, 135, 138, 154 | 11.27 (1.08) | -0.0006 (0.0105)† | +0.0127 (0.0084) | +0.198 (0.257)† | +0.253 (0.229) |

Ten pairs with the largest c (seat 3 x pooled seat 1), with their raw seats: 87-97 at (9, 7) c +2.41 (1.36) [S3 14.67, S1 +0.0411]; 61-60 at (6, 0) c +2.26 (1.26) [S3 15.61, S1 +0.0331]; 69-70 at (6, 10) c +1.45 (1.05) [S3 3.49, S1 -0.0372]; 34-35 at (2, 15) c +1.37 (0.99) [S3 0.91, S1 -0.0235]; 77-85 at (8, 5) c +1.28 (1.09) [S3 1.70, S1 -0.0245]; 107-97 at (9, 7) c +1.18 (1.46) [S3 11.37, S1 +0.0411]; 29-38 at (3, 9) c +1.14 (0.84) [S3 12.48, S1 +0.0289]; 49-38 at (3, 9) c +1.12 (1.10) [S3 12.40, S1 +0.0289]; 64-63 at (6, 3) c +1.12 (0.75) [S3 1.30, S1 -0.0205]; 24-25 at (2, 5) c +1.06 (1.02) [S3 14.77, S1 +0.0166].

Ten pairs with the most negative c: 71-70 at (6, 10) c -2.87 (1.06) [S3 17.62, S1 -0.0372]; 125-117 at (11, 5) c -2.27 (1.05) [S3 17.01, S1 -0.0318]; 56-63 at (6, 3) c -1.51 (0.89) [S3 17.59, S1 -0.0205]; 3-4 at (0, 4) c -1.45 (0.80) [S3 12.27, S1 -0.0434]; 136-123 at (12, 3) c -1.21 (1.23) [S3 0.38, S1 +0.0156]; 26-25 at (2, 5) c -1.17 (1.11) [S3 1.03, S1 +0.0166]; 65-66 at (6, 6) c -1.10 (1.27) [S3 4.00, S1 +0.0278]; 131-138 at (13, 11) c -1.10 (0.87) [S3 12.96, S1 -0.0287]; 122-123 at (12, 3) c -1.09 (1.05) [S3 1.17, S1 +0.0156]; 5-4 at (0, 4) c -0.88 (1.46) [S3 10.70, S1 -0.0434].

## WHAT EACH SEAT READ

(written by hand from the tables above; every number is copied from them; plain words, no verdict)

**Seat 1, the emitter's short clock (OWN).** Over all twelve arms together, the 75 pairs' emitters end -0.0020 (0.0041) from what their own per-stretch rulers book (-0.0019 (0.0038) with each of the 35 emitters counted once), within one width of zero. Arm by arm it moves: +0.0289 (0.0117) on A30_10 (OFF 30 us / ON 10 us, LAID), +0.0298 (0.0107) on A30_30f, +0.0179 (0.0087) on B30_30, +0.0140 (0.0074) on WB; -0.0378 (0.0139) on A10_30 (OFF 10 / ON 30), -0.0245 (0.0107) on WA, -0.0195 (0.0122) on A90_30, -0.0190 (0.0090) on B30_30f. The same train on the same emitter, read in its core arm and in its witness arm, ends at OWN levels 0.3696 (0.0067) on A30_30 and 0.3559 (0.0042) on WA, and 0.6858 (0.0060) on B30_30 and 0.6819 (0.0045) on WB. Across the 35 emitters those end levels agree at r +0.787 (0.085) and +0.779 (0.084). One emitter's pooled seat 1 spreads across the 35 by 0.0236. Its own noise is 0.0233 (bootstrap) or 0.0230 (shot-order thirds), and it agrees with itself across thirds at r -0.24, +0.19, +0.07. Emitter by emitter, seat 1 is too thin to read in this job. The arm means are readable at the widths above.

**Seat 2, the emitter's long clock (OWN).** Over all twelve arms it reads +0.0086 (0.0025) over the pairs and +0.0084 (0.0024) over the 35 emitters. The arms whose emitter ends OFF read +0.0218 (0.0072) on A30_30, +0.0227 (0.0051) on A30_10, +0.0205 (0.0066) on N6, +0.0163 (0.0049) on N2, +0.0119 (0.0062) on A90_30, +0.0102 (0.0085) on A10_30, +0.0081 (0.0058) on WA, +0.0034 (0.0071) on A30_90 and +0.0030 (0.0070) on B30_30f. The arms whose emitter ends ON read -0.0029 (0.0067) on A30_30f, -0.0041 (0.0067) on B30_30 and -0.0080 (0.0051) on WB. Pooled seat 2 spreads across the 35 emitters by 0.0175, against a noise of 0.0156 (bootstrap) or 0.0173 (thirds), with r across thirds -0.14, +0.17, -0.04: too thin to read emitter by emitter. Within one arm, seat 1 and seat 2 move together across pairs at r +0.356 (A30_10) to +0.813 (B30_30f). Both are the same end level minus a book, so they share that level's shot noise.

**Seat 3, the witness (WITNESS).** The witness reads its emitter's ON time only as coupling x time, and only in the two witness arms. Over the 75 pairs, the half-difference between emitters started ON and started OFF reads |hd|/5 = 8.24 (0.48) WITNESS deg per LAID ON stretch, median 8.01 (0.82). Signed, it reads -2.50 (0.99), with 52 of 75 pairs negative. At the reader's ensemble coupling (16.90 WITNESS deg per 30-us ON stretch) that is 14.63 (0.85) us of ON time per LAID 30.016-us ON stretch, -15.39 (0.85) us against the LAID time. At that same coupling, the reader's own model with the chip-typical OWN fading books 11.70 deg per stretch (58.48 over the five), and with no fading it books 16.90 (84.51 over the five).
- Across pairs, seat 3 spreads by 5.18 deg per stretch against a shot width of 3.89. It agrees with itself across thirds at r +0.11, +0.34, -0.01.
- Witnesses of one emitter read the same shots of the same emitter, yet seat 3 spreads within an emitter by 5.07 (0.48). The emitters' means spread by 3.38 (0.35). For reference, 5.07 over the square root of the mean witness count (70 pairs / 30 emitters) is 3.32.
- Single cases: emitter 70 reads 3.49 through witness 69 and 17.62 through witness 71. Emitter 63 reads 1.30 through 64 and 17.59 through 56. Emitter 25 reads 14.77 through 24 and 1.03 through 26.
- 21 of 75 pairs read within one width of zero. The 25 pairs whose witness hand is shorter than 0.12 carry a width of 4.73 deg per stretch at 216 shots and 4.79 at 72, near the 5.20 of a reading spread evenly over 0-18. Those are too thin to read one by one.
- The reader's per-pair coupling fit (own fading) lands more than 10 deg from its full-data value in more than a third of shot resamples for 53 of 75 pairs. It sits on the fit grid's edge for 4 pairs and differs from the chip-typical-fading fit by more than 10 deg for 11. Its median over the pairs reads 16.90 (1.87) with the pair set held fixed, and +16.9023 (1.8085) in the reader's own line. It rises with |hd|/5 at r +0.498 (0.089).
- By chip region, seat 3 reads from 6.20 (1.10) deg per stretch (bottom-left) to 11.27 (1.08) (bottom-right) and 10.38 (1.38) (top-left).

**How seat 3 moves with seats 1 and 2.** Across the 75 pairs, arm by arm, r(WITNESS seat 3, OWN seat 1) runs from -0.040 (A30_90) to +0.130 (B30_30f), and r(seat 3, seat 2) from -0.074 (B30_30) to +0.175 (B30_30f). Shot widths run 0.097-0.119, and emitter-redraw widths 0.092-0.155. Pooled over arms: r(seat 3, seat 1) = +0.068 (0.111) [0.113], r(seat 3, seat 2) = +0.120 (0.111) [0.093]. 128 correlations were computed in all. The three largest:
- signed hd/5 with pooled seat 1 over the 35 emitters, +0.191 (0.155) [0.183];
- |hd|/5 with pooled seat 2 over the 35 emitters, +0.185 (0.158) [0.127];
- |hd|/5 with seat 2 on B30_30f over the 75 pairs, +0.175 (0.103) [0.092].
Inside each shot-order third, the pooled correlations read +0.22, +0.07, +0.12 with seat 1 and +0.25, +0.03, +0.03 with seat 2. Per emitter, seats 1 and 2 sit at their own shot-noise spread. Across pairs, the co-movement of the three seats is too thin to read in this job; the widths above are the ones this job gives.

**Where on the chip.** Two pairs carry the largest same-side share of the seat-3 / seat-1 correlation:
- 87-97 (emitter 97, bridge bit at grid (9, 7)): c +2.41 (1.36);
- 61-60 (grid (6, 0)): +2.26 (1.26).
The largest opposite-side shares:
- 71-70 (grid (6, 10)): -2.87 (1.06);
- 125-117 (grid (11, 5)): -2.27 (1.05).
Emitter 70's two witnesses sit at the two ends (+1.45 and -2.87). In the 3 x 3 regions, every regional mean c for seat 3 with seat 1 sits within one width of zero. For seat 3 with seat 2, middle-centre (emitters 66, 70, 85, 89, 97; 12 pairs) reads +0.626 (0.368) and bottom-right +0.253 (0.229); the other seven sit within one width. The middle band also carries the largest regional seat 2: +0.0197 (0.0090) middle-left, +0.0167 (0.0064) middle-centre (OWN).

**Fingerprints.** A pair's seat 1 spreads across its twelve arms by a median 0.0488 (0.0460 beyond the chip's own arm pattern), against a noise-only spread of 0.0582. Seat 2 spreads by 0.0369 (0.0347) against 0.0345. 18 of 75 pairs (9 of 35 emitters) spread beyond their noise-only spread on seat 1, and 39 of 75 on seat 2. The top of pooled seat 1 is emitter 82 (grid (8, 2)), at +0.0518 (0.0243), which is also near the top of seat 2 at +0.0520 (0.0158). Its seat-2 spread across arms is 0.0693, or 0.0613 beyond the chip pattern, against a noise-only 0.0349. Emitter 97 follows (+0.0411 (0.0213), seat 2 +0.0635 (0.0151)). The bottom is emitter 4 (grid (0, 4)) at -0.0434 (0.0194), with emitter 70 at -0.0372 (0.0223).

## Could not compute

- **Seat 3 on the ten core arms.** Those circuits push every bit alike, the witness bits included, and read every bit on Z, so no witness phase exists there. Seat 3 is one reading per pair, taken from WA and WB together, and each arm's co-movement row pairs that one reading with the arm's own seats 1-2.
- **Seat 3 for one start alone (WA by itself, WB by itself).** The two witness vectors give one half-difference and one half-sum (the witness's own leftover, +0.60 (4.38) deg on average). No circuit holds the witness while its emitter sits still, so a single start's reading cannot be split from that leftover.
- **The emitter's ON time in microseconds, pair by pair.** The witness reads coupling x ON time. The witness arms use one stretch pattern (30 / 30 us), so this job does not separate a pair's coupling from its emitter's ON time. t_W therefore puts one ensemble coupling on every pair and is seat 3 on another scale. The within-emitter spread of seat 3 (5.07 (0.48), against a shot width of 3.90) is read through one emitter's single ON time in the same shots, so it carries whatever differs between that emitter's witnesses (their couplings, and anything else witness-specific) plus shot noise.
- **Readings pair by pair.** Per-emitter seats 1-2 sit at their shot-noise spread (above), and 53 of 75 per-pair coupling fits jump by more than 10 deg in over a third of resamples. These are too thin to read one pair at a time; their widths are in the tables and in `three_seats_run121_20261003.json`.
- **What the shot widths do not carry.** The shot-bootstrap width of a correlation holds the shot noise only, not which 35 emitters this chip happens to offer. The emitter-redraw width [in brackets] stands beside each one. The pair set is held fixed through the resamples; the reader redraws its witness set per resample, which is why the coupling median carries 1.87 here and 1.81 in the reader's line.

