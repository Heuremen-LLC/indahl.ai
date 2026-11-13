# 7_PUBLIC trace fixes, 3 October 2026

Every flag from the measurement-paper pass. Each block gives (1) what 7_PUBLIC.md says, (2) the evidence, (3) a verdict, (4) a replacement.
- Ledger lines are `THIRD_RUNG_20260928.md:<line>` (in ~/bones-forge/parallax/).
- Reads and code are `reads/<file>:<line>` and `code/<file>:<line>` (in darkwave_disco/for_indahl_ai/data/).
- 7_PUBLIC.md is quoted as of its 12:18 version. Only lines 7, 36 and 125 changed then; no numbers changed.
- "derived" marks arithmetic done here.

---

## A. Flagged as untraceable

### 1. "~1.9" -- TRACED NOW, but to a different quantity
1. 7_PUBLIC.md:68: "1.923 / the microsecond clock against the shot clocks, ~1.9;"
2. Evidence:
   - THIRD_RUNG_20260928.md:1304-1305: "a clock that counts microseconds (the carry) that stands ~1.9 series-taus apart" / "from the shot clocks."
   - THIRD_RUNG_20260928.md:1301: "carry - echo = +1.88 +/- 1.16 and GHZ - carry = -2.02 +/- 1.18".
   - The ~1.9 is restated at THIRD_RUNG_20260928.md:2036 (§167).
   - So the source is a *separation* in series-tau units, with a ±1.2 width (1.6-1.7σ). It is not a ratio of clocks. My earlier "untraceable" was wrong.
3. VERDICT: **CONFIRMED-WRONG**. A separation of 1.88 ± 1.16 is presented as a ratio matching 1.923, with its width dropped.
4. Replace: delete "1.923 / the microsecond clock against the shot clocks, ~1.9;". If kept, write "the microsecond clock sits +1.88 +- 1.16 series-taus from the shot clocks (a separation, not a ratio; §65)".

### 2. "0.760" as the qubit's two clocks
1. 7_PUBLIC.md:62: "4/3 and 3/4: the qubit's two clocks sit at 0.756 / 0.760 of each other."
2. Evidence:
   - 0.756 is traced. reads/lone_vs_tail.txt:16, "NO earlier look: 208 260 253 275", gives 208/275 = 0.756 (derived). THIRD_RUNG_20260928.md:1841 gives "208/275 = 0.76".
   - 0.760: no read gives a two-clock ratio of 0.760. The qubit's other two-clock ratio is "mean 0.775 +- 0.009" (THIRD_RUNG_20260928.md:1831).
   - Nearest 0.76 values elsewhere: the spectator hand, reads/close_looktime.txt:10, "hand kept through 30 us of laid time ... all +0.7604 +- 0.0057"; and the jumping-qubit ratio, reads/jump_run.txt:22, "MID on ON's sorting ... middle 0.763 +-0.023".
   - THIRD_RUNG_20260928.md:2024 lists "hand 11/12, 10/12, 9/12; two clocks 9/12" separately, and :2028 gives "4/3 <-> 3/4 (0.756, 0.760)". This suggests 0.760 is the hand, but does not prove it.
3. VERDICT: **CANNOT-TELL** where 0.760 comes from. As a two-clock value it is unsupported.
4. Replace: "4/3 and 3/4: the qubit's two clocks sit at 0.756 (one read, no earlier look) and 0.775 +- 0.009 (eight reads) of each other."

### 3. "all below 0.04 of a point"
1. 7_PUBLIC.md:35: "calibration residuals are reported (all below 0.04 of a point)."
2. Evidence:
   - THIRD_RUNG_20260928.md:2041: "16 markers, residual 0.0011" (Tang Fig. 3c).
   - THIRD_RUNG_20260928.md:2042: "digitized off the PDF's vectors" (Jacques), with no residual given.
   - "0.04 of a point" / "0.04 of": NOT FOUND. I looked in the ledger, the release's reads and code, and every *.md/*.txt/*.json/*.py under parallax/. LIGHT_SPLIT_20261001.md mentions residuals ("sub-pixel tick-label jitter") but gives no 0.04.
3. VERDICT: **CANNOT-TELL**. One residual is found (0.0011); the "all below 0.04" bound is not found.
4. Replace: "calibration residuals are reported (Tang et al. Fig. 3c: 0.0011 over 16 markers; §172)."

### 4. Neutron lifetime widths -- OUTSIDE-SOURCE
1. 7_PUBLIC.md:93: "Counting protons (NIST beam; Yue 2013): 887.7 +- 2.2 s. Counting electrons (J-PARC 2024): 877.2 +- 1.7 (+4.0 / -3.6) s. Counting what stays in a bottle (PDG average): 878.4 +- 0.5 s."
2. Evidence:
   - THIRD_RUNG_20260928.md:2038: "proton count 887.7 s (NIST BL2), electron count 877.2 s (J-PARC 2024), bottle 878.4 s (PDG); proton vs electron 1.197 +- 0.54 %, vs bottle 1.059 +- 0.26 %". It has central values only; the widths are NOT FOUND in any source (same search as item 3).
   - Published values, as supplied by the coordinator (not re-opened here): Yue 2013, 887.7 +- 1.2 stat +- 1.9 sys s; J-PARC arXiv 2412.19519, 877.2 +- 1.7 stat +4.0/-3.6 sys s; PDG, 878.4 +- 0.5 s.
   - Derived checks:
     - sqrt(1.2² + 1.9²) = 2.247, which is the "2.2".
     - Proton vs electron: 1.197 +- 0.537 %. This uses J-PARC's systematic symmetrized to 3.8; without the systematic the width would be 0.32 %.
     - Proton vs bottle: 1.059 +- 0.257 %.
     - Both percentages reproduce.
3. VERDICT: **CONFIRMED-RIGHT-BUT-UNTRACED (OUTSIDE-SOURCE)**.
4. Replace: "Counting protons (NIST beam; Yue 2013): 887.7 +- 1.2 (stat) +- 1.9 (sys) s. Counting electrons (J-PARC 2024, arXiv 2412.19519): 877.2 +- 1.7 (stat) +4.0 / -3.6 (sys) s. Counting what stays in a bottle (PDG average): 878.4 +- 0.5 s." Also add the widths to the ledger's next entry.

## B. Found only as ledger statements

### 5. "3.5 +- 0.2 us"
1. 7_PUBLIC.md:50: "The looked-at qubit's own ageing: 3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back."
2. Evidence:
   - The ledger states it: THIRD_RUNG_20260928.md:1905, "pile-up 3.5 +- 0.2 per look over 3 and 9 looks"; THIRD_RUNG_20260928.md:1928, "pile-up 3.5 +- 0.2, give-back 3.5-4.1".
   - The inputs are in reads/hold_run.txt:6 ("3 looks ... bit by bit: 311.5") and :7 ("9 looks ... bit by bit: 327.0"). Derived per look: 3.8 and 3.0 us. The median-qubit values give 3.0-6.7 us (3 looks) and 4.0-4.2 us (9 looks).
   - No read or script computes ±0.2.
   - Independent estimators agree with about 3.5 at the centre: reads/jump_rerack.txt:16, "none_ON 3.23 [2.36 4.97]" (per-read medians 3.20-4.26); and reads/close_giveback.txt:2,4,6 (3.5313 +- 0.8737, 3.5569 +- 0.9309, 4.0507 +- 0.9397).
   - Those give-back widths are dropped in 7_PUBLIC. One give-back read sits at about 1 us at all three positions: reads/close_giveback.txt:2 "+1.0228 +- 1.4946".
3. VERDICT: **CANNOT-TELL** for the ±0.2. The centre of 3.5 is consistent with the read estimators.
4. Replace: "The looked-at qubit's own ageing: 3.2-4.3 us per look (eight reads), and 3.5 / 3.6 / 4.1 +- 0.9 us wherever a single look sits (three reads that scatter beyond their widths)." Then recompute the ratios from it, with widths.

### 6. "closes to 0.002" (the park)
1. 7_PUBLIC.md:85: "A qubit parked in |0> doesn't age: bookkeeping per qubit closes to 0.002 three ways of parking."
2. Evidence:
   - The ledger states it: THIRD_RUNG_20260928.md:1905, "III THE PARK: ON-start parked arms close to bookkeeping within 0.002 bit by bit", plus the correction `"+0.007" middle-bit artifact`.
   - The read prints only median-qubit values: reads/hold_run.txt:21-23 give "+0.0065 +0.0054 +0.0086", "-0.0007 -0.0004 +0.0058" and "+0.0003 +0.0011 -0.0032".
   - The reader computes bookkeeping on the median qubit only, at code/readhold.py:35: "bk = [book(med(r['left']['N0']), nseg) for r in R]".
   - The per-qubit closure needs the raw results, which are not in the release.
   - A second park does close in the release: THIRD_RUNG_20260928.md:1903, "Correct bookkeeping (yardstick 0.7896): 0.0647 and 0.1346; measured (both hands averaged) 0.0648 and 0.1348" (reads/witness_run.txt:21-22; one read).
3. VERDICT: **CANNOT-TELL** (not reproducible from the release).
4. Replace line 85 (this also fixes item 14): "- **What the qubits showed.** A qubit parked in |0> doesn't age: three ways of parking close to bookkeeping within 0.002 per qubit (median qubit up to +0.0086), and an emitter parked after 20 / 40 us reads 0.0648 / 0.1348 against 0.0647 / 0.1346 (one read). The look stretches the qubit 1.48x against its witnesses; the photon ring over the horizon is 1.5. § 132, 134, 135 (the park); § 139 (the stretch)."

### 7. "2.17" (hold-run crossing)
1. 7_PUBLIC.md:69: "against Pittsburgh's crossing, 2.00 / 2.17."
2. Evidence:
   - The ledger states it: THIRD_RUNG_20260928.md:1905, "OFF start with ten pushes +0.0217 +- 0.0016 in three reads"; THIRD_RUNG_20260928.md:1926, "(hold run +0.0217: six reads, two runs)"; also code/push.py:2, "(+0.0217 +- 0.0016, three reads)".
   - The read prints median-qubit values only: reads/hold_run.txt:32, "+0.3548 +0.3502 +0.3472 ... bookkeeping ... 0.3394 0.3363 0.3422". That is +0.0154 / +0.0139 / +0.0050 (derived; THIRD_RUNG_20260928.md:1895 says the same).
   - reads/discarded_hold.txt:54 gives the mean-over-qubits level "+0.3751 (0.0013)" with no bookkeeping.
3. VERDICT: **CANNOT-TELL**. The mean-over-qubits value is not printed in any read.
4. Replace: "against Pittsburgh's crossing, 2.00 +- 0.16 (push run, three reads) / 2.17 +- 0.16 (hold run, three reads)."

### 8a. "0.26 +- 0.12 % per push" -- REPRODUCES
1. 7_PUBLIC.md:56: "Leakage is capped at 0.26 +- 0.12 % per push, against 2.96 % needed to fake it."
2. Evidence:
   - THIRD_RUNG_20260928.md:1963: "solve to: the push falls 1.48 +- 0.14 deg short, plus 0.26% +- 0.12 per push of everything that grows with the count (...); upper edge 0.49%". THIRD_RUNG_20260928.md:1970: "ten pushes: 5 and 5".
   - Recomputed from reads/close_push.txt:2,3,5,6 (OFF p2 +0.0019 +- 0.0006, OFF p10 +0.0229 +- 0.0007, ON p2 -0.0020 +- 0.0007, ON p10 -0.0232 +- 0.0008).
   - Model: o_N + |u_N| = 2 sin²(N e / 2) + (N/2) k. The 2-push and 10-push equations are solved exactly; widths come from 20,000 Gaussian redraws.
   - Result: shortfall 1.483 +- 0.136 deg, k = 0.256 +- 0.116 % per push, upper edge 0.489 %.
3. VERDICT: **CONFIRMED-RIGHT-BUT-UNTRACED**. It reproduces; the computation is not in the release.
4. Replace: leave (optionally add "(two- and ten-push arms of the same jobs)").

### 8b. "2.96 %"
1. 7_PUBLIC.md:56 (same sentence).
2. Evidence: THIRD_RUNG_20260928.md:1953, "TOGETHER they fit all three (2.00 / 0.05 / 0.33) only at 2.96% leakage per push and TLS strength 0.66". This is the reviewer's leakage-plus-TLS model, which is not in the release.
3. VERDICT: **CANNOT-TELL**.
4. Replace: "... against 2.96 % per push that a leakage-plus-TLS model needs to fit all three starts (§146)."

### 9. "7.5 % family-wise" -- REPRODUCES
1. 7_PUBLIC.md:14: "one arm in ten (7.5 % family-wise)". The same phrase is at 7_PUBLIC.md:56.
2. Evidence:
   - reads/noname_read1.txt:38: "A30_10: minus each-stretch-own-ruler book +0.0170(0.0064)".
   - THIRD_RUNG_20260928.md:2045: "A30_10 stays one arm in ten over 2 sigma (7.5 % family-wise)".
   - Family: code/readnoname.py:13, "CORE = ['A30_30', 'A10_30', 'A90_30', 'A30_10', 'A30_90', 'A30_30f', 'B30_30', 'B30_30f', 'N2', 'N6']". Only A30_10 has |z| > 2; the next is A10_30 at -1.96 (derived).
   - Computation:
     - z = 1.70 / 0.64 = 2.656; two-sided p = 0.0079.
     - Šidák 1 - (1 - p)^10 = 0.0763; Bonferroni 10p = 0.079.
     - With z rounded to 2.66: p = 0.0078, Šidák 0.0754.
     - So "7.5 %" uses the rounded z; unrounded it is 7.6 %.
   - Outside the family: reads/noname_read1.txt:72, "emitters started OFF, minus own-ruler book (both hand arms) -0.0216(0.0102)", which is -2.12σ (derived).
3. VERDICT: **CONFIRMED-RIGHT-BUT-UNTRACED** (reproduces at 7.5-7.6 %).
4. Replace: "(7.6 % family-wise over ten arms)", or leave.

## C. Flagged as mislabelled

### 10. "(six reads)" -- VERIFIED by coordinator
1. 7_PUBLIC.md:56: "Pittsburgh +2.00 +- 0.16 % (six reads)"
2. Evidence:
   - reads/close_push.txt:1: "THE PUSH RUN, ibm_pittsburgh, reads at 13:09 14:26 14:27".
   - reads/close_push.txt:4: "OFF s10 spread minus bookkeeping +0.0174 +- 0.0028 +0.0213 +- 0.0030 +0.0213 +- 0.0023 | all +0.0200 +- 0.0016".
   - The label came from THIRD_RUNG_20260928.md:1994, "Pittsburgh (six reads, two runs) +2.00 +- 0.16". The hold run's three reads are item 7.
3. VERDICT: **CONFIRMED-WRONG** (VERIFIED).
4. Replace: "Pittsburgh +2.00 +- 0.16 % (push run, three reads; the hold run's three reads give +2.17 +- 0.16)"

### 11. "frame-held spectator keeps 0.92"
1. 7_PUBLIC.md:62: "a frame-held spectator keeps 0.92 of its coherence through three looks"
2. Evidence:
   - The 0.92 is reads/close_looktime.txt:5: "hand kept through 3 looks (over the hand at no window) ... all +0.9209 +- 0.0040" (look-time run). Also THIRD_RUNG_20260928.md:1928: "Hands kept: 0.92 through 3 looks".
   - How those spectators were held:
     - code/looktime.py:4: "every bit wired to an emitter is held as a CLOCK (set half-way, left to tick, read on two hands a quarter-turn apart)".
     - code/looktime.py:87: "if Wt: qc.sx(Wt)".
     - code/looktime.py:95: "for q in Fr: qc.measure(q, regs[i][qs.index(q)])". Only far qubits get pulses in the window.
     - code/looktime.py:98: "if sp['hand'] == 'Y': qc.rz(math.pi / 2, Wt)". Nothing is applied before readout.
     - So they are free-running Ramsey clocks.
   - Frame-holding exists only in the no-name run:
     - code/noname.py:122: "if W: qc.rz(-math.pi / 2, W); qc.x(W); qc.rz(math.pi / 2, W)".
     - code/noname.py:16: "so its own frame turning cancels every round trip".
     - THIRD_RUNG_20260928.md:1948 says the same.
     - Those frame-held hands keep 0.16: THIRD_RUNG_20260928.md:2012, "THE WITNESSES, FRAME HELD STILL: hands keep 0.16 of their length after 300 us".
3. VERDICT: **CONFIRMED-WRONG**.
4. Replace: "a free-running spectator keeps 0.92 of its coherence (0.9209 +- 0.0040) through three looks at other qubits"

### 12. "0.59 of its later one"
1. 7_PUBLIC.md:62: "the halfway state's early decay at 0.59 of its later one"
2. Evidence:
   - THIRD_RUNG_20260928.md:2017: "the in-between's early clock against its later one, 123 against 208 = 0.59 (§119-§121)".
   - reads/lone_vs_tail.txt:38 (start MID, no earlier look): "123 190 283 277".
   - reads/lone_vs_tail.txt:16 (start ON, no earlier look): "208 260 253 275".
   - So 208 is the **|1> state's** early clock. The ratio 123/208 = 0.591 compares two states. The halfway state against its own later clock gives 123/277 = 0.44 (derived), or 0.263 per qubit (reads/lone_vs_tail.txt:43).
3. VERDICT: **CONFIRMED-WRONG** (the number is right; the description is wrong).
4. Replace: "the halfway state's early decay clock at 0.59 of the |1> state's (123 / 208 us, one read)"

### 13. Finding One cites §148
1. 7_PUBLIC.md:50: "§ 132, 139, 148."
2. Evidence:
   - §148 (THIRD_RUNG_20260928.md:1968-1972) has no look-timing measurement. Its only look mention is a design note at THIRD_RUNG_20260928.md:1971: "a look's cost per bit is already measured, ~3.5 us".
   - The look numbers sit at:
     - THIRD_RUNG_20260928.md:1859 (§125): "2.180 us".
     - THIRD_RUNG_20260928.md:1905 (§135): "pile-up 3.5 +- 0.2".
     - THIRD_RUNG_20260928.md:1928-1929 (§139): look-time, give-back, "~1.5x".
     - THIRD_RUNG_20260928.md:1893 (§132): "(3.5 us) each".
3. VERDICT: **CONFIRMED-WRONG**.
4. Replace: "§ 125, 132, 135, 139."

### 14. Finding Six's park line cites §139, §155
1. 7_PUBLIC.md:85: "... the photon ring over the horizon is 1.5. § 139, 155."
2. Evidence:
   - The park is at THIRD_RUNG_20260928.md:1884-1895 (§132), :1903 (§134) and :1905 (§135).
   - §139 supports only the 1.48x clause: THIRD_RUNG_20260928.md:1929, "the look makes the bit it looks at fade ~1.5x faster than its neighbours' time runs while the look lasts".
   - §155 (THIRD_RUNG_20260928.md:2005-2014) supports neither clause.
3. VERDICT: **CONFIRMED-WRONG**.
4. Replace: see item 6 (one line fixes both).

### 15. "qubits run in random groups of three"
1. 7_PUBLIC.md:31: "qubits run in random groups of three."
2. Evidence:
   - True for the nine-qubit runs only:
     - code/common.py:46: "N_GROUPS = 3 # groups of three per chip (9 qubits; qubits run in parallel, no QPU cost)".
     - code/common.py:136: "pool = [int(q) for q in np.random.default_rng(SEED_BLIND).permutation(int(n_qubits))[:3 * N_GROUPS]]".
     - THIRD_RUNG_20260928.md:1776: "blind bits (same seed as Pittsburgh: 12 26 46 103 106 108 112 141 144, all nine readable)".
   - Every whole-chip run, which supplies every finding's main numbers, uses code/push.py:78-79: "g = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]" and "'how': 'EVERY bit of the chip (no draw, no usability check)'". That is consecutive triples over all qubits, not random. The same helper is in pushrep, noname, looktime, hold, giveback, witness, tail, jump and lone.
3. VERDICT: **CONFIRMED-WRONG** for the runs the findings rest on.
4. Replace: "circuit order randomized from a recorded seed; the nine-qubit runs drew their qubits by a written seed, in three groups of three; the whole-chip runs drive and read every qubit."

---

**Extra, not in the three lists (not counted):**
- 7_PUBLIC.md:56 says "Prepared |1>: +0.05, -0.16, -1.24 +- 0.24." The values are right but two widths are dropped:
  - reads/close_push.txt:7: "all +0.0005 +- 0.0013".
  - reads/rep_marrakesh_read1.txt:7: "Marrakesh -0.0016 +- 0.0021".
  - reads/rep_kingston_read1.txt:7: "-0.0124 +- 0.0024".
- Replace: "Prepared |1>: +0.05 +- 0.13, -0.16 +- 0.21, -1.24 +- 0.24."

**Counts (16 verdicts, item 8 split into 8a and 8b):**
- CONFIRMED-WRONG: 7 (items 1, 10, 11, 12, 13, 14, 15).
- CONFIRMED-RIGHT-BUT-UNTRACED: 3 (item 4 as outside-source; 8a and 9 reproduce).
- CANNOT-TELL: 6 (items 2, 3, 5, 6, 7, 8b).
