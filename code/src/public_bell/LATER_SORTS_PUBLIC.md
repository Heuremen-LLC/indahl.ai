# Later sorts on public Bell-test data

Wayfinder & Bones, 29 Sept 2026. No guesses were written down before looking. Sources and licenses are in `README.md`, the code is in `code/`, and every number below is in `results/`.

## What we got

Five experiments have their raw records on the open web, and all five were downloaded (14 GB in total):

- **Innsbruck 1998 (Weihs).** Every photon detection, with its time tag, the setting and the detector that fired. Two archives totalling 1.1 GB on Zenodo. Used: the 21 good "longdist" runs (24 million detections, 0.5 million coincidences) and 3 long runs.
- **NIST 2015 (Shalm).** One record per 10-microsecond trial: both settings, and which of 16 laser pulses clicked on each side (a time stamp in 12.5 ns steps). Eight runs, 1.62 billion trials, 10.5 GB. This is the processed form. The raw time-tag dumps (about 48 GB) are over the size limit and were skipped.
- **Delft 2015 and 2016 (Hensen).** Every heralded attempt: herald click times in picoseconds, both random bits, and both readout click times. 4,746 + 3,918 attempts, of which 245 + 300 are the published Bell trials. A few hundred kB.
- **Munich 2017 (Rosenfeld).** 20,403 heralded atom pairs from the two public runs. This data only came back online on Zenodo last week.
- **Illinois 2013 (Christensen).** 4,450 one-second files of raw time tags, 110 million trials, 0.29 GB.

Not public: Vienna 2015, BIG Bell Test 2018 ("available upon reasonable request" from each lab), the cosmic Bell tests, and ETH 2023.

## The sort, as run

Inside each dataset, an earlier record was sorted by a later record, and the same earlier record was also sorted by the matching earlier record (the mirror):

- A trial's clicks, detection times or outcomes, sorted by the NEXT trial's settings on either side, and mirrored by the PREVIOUS trial's settings.
- One side's click sorted by the other side's next click (and previous click).
- In Innsbruck, which has no trials: each detection sorted by the next detection's setting on its own side and on the far side. Each coincidence sorted by the next coincidence's settings, and its timing sorted the same way.
- In Delft, the herald click times (the earliest records) sorted by the same trial's random bits, which come later, and mirrored by the previous trial's bits.

Each sort is conditioned on the records already in hand: the current trial's settings, plus the settings of the trial on the far side of the mirror. Innsbruck sorts are also conditioned on the gap to the neighbour and on the 1-second time block.

The null is a shuffle of the later record across trials within the same condition. It is exact, done 2,000 to 5,000 times. In Illinois the settings are held fixed for a whole second, so whole files were shuffled there, not trials.

Innsbruck also got "far" controls, where the key is taken 1,000 records away, to see what slow drift alone does.

Raw timestamps and outcomes were kept, not collapsed to a single statistic. The Bell correlation of the same trial was run as a positive control. It shows up hugely everywhere (for example, NIST likelihood-ratio 1.77 million on 54 degrees of freedom), so the machinery does see real dependence when it is there.

## What showed up

**448 sorts in the main family** (184 later, 184 earlier mirrors, 80 far controls):

- **Later sorts:** 12 at p < 0.05 where chance expects 9.2, and 2 at p < 0.01 where chance expects 1.8.
- **Earlier mirrors:** 10 and 3.

**Four survive correction** (Bonferroni and false-discovery rate agree). All four are the same Innsbruck effect, and it is two-sided: a detection's outcome is tied to the setting of the far side's nearest detection, whether that detection comes next or came before (z = 34 to 94). Removing every detection that has a far-side partner within ±50 ns makes all four vanish (shuffle p = 0.65, 0.87, 0.68, 0.99). So it is the already-known coincidence effect: in Innsbruck coincidences, one side's outcome rates move with the other side's setting (Bob's detector-1 share shifts by about 5 points with Alice's setting). It is not a later-record effect.

**One thing turned up in the effect-size pass, not in the planned tests:** at NIST, Bob's click rate is 0.53% ± 0.13% lower when Bob's PREVIOUS trial setting was 1 rather than 0.

- z = -4.1, and the sign is the same in 8 of 8 runs.
- A follow-up lag scan (48 directed estimates, lags -6 to +6, both sides) gives a Bonferroni p of 0.002.
- Lag -2 rebounds to +0.37% ± 0.13% (z = +2.9, 7 of 8 runs), which is not significant after correction.
- The settings themselves are uncorrelated from trial to trial (within 2e-5 of 0.5).
- Reading: Bob's modulator or electronics remember the last setting for about one trial, i.e. an ordinary earlier-to-later carry-over. The same scan on the later side (the next 1 to 6 settings) finds nothing: the largest |z| is 2.0 out of 24.
- NIST's paper handles memory with memory-robust statistics. We found no published test of it on these files.

## What came up empty

- **NIST later sorts:** the next trial's settings do not move either side's click rate beyond about ±0.3% (2 sigma, relative, all 8 runs pooled), and do not move detection times beyond about ±150 ps. The cross-side next click against previous click is +2.8% ± 1.8% against +5.4% ± 1.8%. Both are positive, and the difference is not significant. That fits both stations seeing the same slow brightness wander.
- **Innsbruck:** the next coincidence's settings sort neither the current outcomes nor the current timing (shuffle p = 0.08 to 0.89), and neither do the previous coincidence's settings. Own-side next setting and previous setting are both null.
- **Delft, Munich, Illinois:** nothing. The smallest p in each is between 0.009 and 0.03, which is what chance gives across their 88 sorts. Delft's herald click times are not sorted by the later random bits.

## Mistakes on the way (all caught, all fixed)

1. **Innsbruck bit order.** On the first pass I trusted the Zenodo text and swapped setting with outcome. That produced a "setting channel dead time" and a huge sort of the current Bell correlation by the next coincidence's settings (likelihood-ratio about 2,900). Checked against the group's own E-values, the bits are the other way round. With the fix plus 1-second blocks, it all goes to null.
   - The real instrument facts: after a click, that detector is blind for about 0.5 µs, back to about half at 1 to 2 µs, and fully back by about 10 µs. About 0.06% of clicks are twins (both detectors within 20 ns under one setting).
2. **Drift fakes sorts.** Without time-block conditioning, Innsbruck sorts on the next and the previous coincidence both lit up equally. That symmetric pattern is the tell for drift.
3. **Analytic chi-square lies in sparse tables.** Several Innsbruck and Illinois sorts had analytic p between 1e-14 and 1e-102 but shuffle p between 0.1 and 0.9. Only shuffle p-values are counted.
4. **Illinois trial-level shuffles are wrong.** The settings are held for a second, so trials inside one second are not independent. Trial-level p reached 4e-35, while file-level shuffle gives p = 0.009 to 0.9. This is the same trap a 2019 paper fell into and retracted (see below).
5. **Order inside an Innsbruck coincidence is not a clean "later".** Which side's time tag comes first is set mostly by fixed per-detector delays of about 1 ns. The "other side later" subset is therefore mostly a relabelling of the detector (outcome-1 share 0.28 against 0.60). It is kept only as a diagnostic.
6. **Smaller fixes:** a Munich sort was missing the current herald in its conditioning, and NIST's lag-1 cross-click sort was counted twice (it is the same pairs). Both were fixed before the final count.

Caveat on "later": Illinois settings were read from a stored 65,536-bit list, identical in every file. So the "next" setting already existed in memory before the earlier click. Everywhere else it was generated in real time.

## What earlier analysts said about these datasets

- **Nobody had run a next-trial sort** on any of these datasets. Closest was Clover (quant-ph/0304115, 2003), who conditioned Innsbruck coincidences on settings one light round trip earlier. He had only 19 usable pairs, and 8 showed his forbidden pattern. He called it inconclusive.
- **Innsbruck no-signalling and fair sampling.**
  - Adenier and Khrennikov (2007) found one side's rates depend on the far setting, and said either fair sampling or no-signalling fails.
  - Bigelow (0906.5093) quantified it: about 8 standard errors in longdist35 at the narrow window, shrinking with wider windows. In 17 of 31 runs, even the wide window still breaks some no-signalling condition by at least 3 SD. He also showed the counts fit a fair sample from a no-signalling table if detection efficiencies depend on setting and result.
  - De Raedt, Michielsen and colleagues (1112.2629, 2304.03962) report that S drops to 2 or below for windows over about 200 ns, and that no run passes no-signalling. That conflicts with Bigelow's window trend.
- **Innsbruck timing.** Morgan (1207.5775) and Larsson and co-authors explain the timing differences as fixed per-detector delays plus about 50 ps/s of clock drift. After correction S = 2.71.
- **Innsbruck randomness.** Hnilo's group found low-complexity, attractor-like structure in the coincidence sequences of some runs (longtime, longdist22, longdist35). The random setting sequences pass all tests. They blame clock drift. (The 2002 and 2007 papers were seen as abstracts only; the 2018 paper was read.)
- **Delft.**
  - Bednorz (1511.03509) found moderate no-signalling tension: p = 0.07 corrected, and 0.011 with a relaxed herald window.
  - Adenier and Khrennikov (1606.00784) found p = 0.0125 after moving the herald window.
  - Graft (1608.02404) argued that a shortfall of 00-setting trials comes from post-selection.
  - Delft's reply (Sci. Rep. 2016): the 19.8 million recorded settings give p = 0.57, and shifting windows around is a look-elsewhere trap.
- **NIST.**
  - The supplement reports 120 no-signalling tests spread roughly evenly (smallest p = 0.0017), and Alice's setting bias slightly above 1/2 in all six runs.
  - Their RNG output is a running parity of all earlier raw bits (verified in the supplement text).
  - Bednorz found p of about 0.049 corrected for no-signalling in pulses outside the window.
- **Illinois.**
  - Graft (1409.5158): counting all detections, not one per trial, removes the violation.
  - Christensen, Knill and co-authors (1503.07573) re-ran the data with one-second blocks as trials: 6.3 sigma instead of 7.7.
  - Liang and Zhang (1812.06236) reported no-signalling p = 3.2e-55, then retracted it themselves because the settings were not randomized trial by trial (verified). Bierhorst (1311.4488) showed that such blocks weaken the proof.
- **Munich.** No raw-data reanalysis was found. Bednorz and Gill used published counts only.
- **Gill (2209.00702)** reviews all of these and puts most past "signalling" findings down to drift acting as a hidden confounder. Our shuffle and block results agree with that.

## Bottom line

Across five open datasets and 448 sorts, no later record sorts an earlier one once drift, blocking and coincidence partners are handled. The one real ordering effect runs the ordinary way: NIST Bob's previous setting nudges his next click by half a percent.
