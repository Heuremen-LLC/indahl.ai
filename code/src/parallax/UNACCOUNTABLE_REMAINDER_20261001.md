# THE UNACCOUNTABLE REMAINDER — 2026-10-01

Wayfinder's correction on PARTICLES_ARE_SUBSTRATE_20261001.md: "accounted for" in
those papers is the AUTHORS' word, not a measurement. A subtraction is a crazy hat
unless its term was MEASURED INDEPENDENTLY. This pass re-reads the same seven
records (Jacques 2007, Grangier 1986, Kimble 1977, and five modern arXiv records)
against that rule. No expectation written first. Raw first. Every step counted,
failed fetches logged as rows.

## 0. Sources read this pass

| # | source | method | result |
|---|---|---|---|
| 1 | `out/light/jacques2007/paper.pdf` | PyMuPDF text extraction, full 9 pages, re-read in full | SUCCESS |
| 2 | Grangier PhD thesis (HAL tel-00009436), OCR'd pages already on disk at `pdfs/ocr/p060-p144.txt` (prior pass) | grepped for fond/accident/bruit/soustr across pp.60-144, read pp.90-107 (printed pp.80-97) in full around the anticorrelation chapter's electronics and results sections | SUCCESS — found the "fond de coïncidences fortuites" (accidental-coincidence background) delayed-window measurement, the resonant-reabsorption check, and the explicit "Résultats bruts" (raw results) section heading |
| 3 | arXiv:1812.01749 (trapped ¹³⁸Ba⁺ ion) PDF at `pdfs/1812.01749.pdf` | full-text extraction, grep dark count / multi-photon / double excitation | SUCCESS — found the optical-Bloch-equation origin of the multi-photon bound |
| 4 | arXiv:2604.23422 PDF | full-text extraction, grep background/leakage/re-excitation | SUCCESS |
| 5 | arXiv:2607.11495 PDF | full-text extraction, grep background | SUCCESS (one qualitative hit, no number) |
| 6 | arXiv:2607.18435 PDF | full-text extraction, grep background (16 hits), read in context | SUCCESS — found the fit equation (Eq. A2) that B (background) comes from |
| 7 | arXiv:2210.00076 PDF | grep dark count/background/jitter/leakage | SUCCESS (no deep re-read needed, already logged) |
| 8 | arXiv:2207.06984 PDF | grep | SUCCESS (no new terms beyond prior pass) |
| 9 | Kimble, Dagenais & Mandel 1977 (PRL 39, 691) | not re-attempted — Unpaywall already confirmed `is_oa: false`, no repository copy, prior pass | FAILED — still a hole, row kept |
| 10 | `grep -noE` across `~/bones-forge/parallax/*.md` + `THIRD_RUNG_20260928.md` for `0.1[123]...` and `12%` patterns | shell grep, no interpretation | SUCCESS — 293 raw hits, see §4 |

Total this pass: 9 fetch/read attempts, 1 failure (Kimble, a hole not a zero), 1 grep
sweep across 125 local files.

## 1. THE AUDIT — every subtracted/invoked term, classified

Classification rule (Wayfinder's, strict): **MEASURED-INDEPENDENT** = a separate
measurement with its own reported number (source blocked, detuned, or a distinct
time window/channel, with a number attached). **INFERRED-FROM-THE-RESIDUAL** = the
term's size was set by a fit to the same data, or by a model/simulation, so that the
books close. **LABEL ONLY** = named, no number at all.

### Jacques et al. 2007 (alpha = 0.12 ± 0.01)

| term invoked | class | quote / number |
|---|---|---|
| "residual background photoluminescence of the diamond sample" | **LABEL ONLY** | "The non-ideal value of the α parameter is due to residual background photoluminescence of the diamond sample and to the two-phonon Raman scattering line, which both produce uncorrelated photons with Poissonian statistics." — no number assigned to either term, no decomposition of the 0.12 |
| "two-phonon Raman scattering line" | **LABEL ONLY** | same sentence, same — named, zero number |
| dark counts ~60 counts/s per APD | **MEASURED-INDEPENDENT (number exists), but NOT APPLIED to alpha** | "The corresponding signal to noise ratio of about 10 is essentially limited by darkcounts of the two APDs, on the order of 60 count.s⁻¹ for each." This is a real number for a real quantity (dark-count rate), but the paper never uses it to subtract a term from α = 0.12; it is invoked only to explain the S/N ≈ 10 ratio and the I > 0.99 which-way parameter. No arithmetic in the paper connects 60 cts/s to the 0.12 figure. |
| signal-to-background ratio ≈ 10 | **MEASURED-INDEPENDENT (stated), not applied as a subtraction to alpha** | "a signal over background ratio of about 10 is achieved" (Fig. 4 caption) — a real measured ratio, offered as context for the pre-characterization g2(0)=0.12, never turned into an explicit subtracted term in the paper's own text |
| gate τ_d = 40 ns | not a subtracted term | stated design parameter, reduces dark-count contribution by construction, no number attributed to residual alpha |

**No raw-vs-corrected split is published.** One number, 0.12 ± 0.01, with causes
named but never decomposed. Zero terms meet the strict bar (a number independently
measured AND subtracted from the reported alpha with its own accounted share).
**Unaccounted remainder = 0.12 ± 0.01 (the full value).**

### Grangier, Roger & Aspect 1986 (alpha = 0.18 ± 0.06, final apparatus; 0.35 ± 0.05, first apparatus)

| term invoked | class | quote / number |
|---|---|---|
| accidental-coincidence "fond" (background), delayed time window | **MEASURED-INDEPENDENT, built but NOT subtracted from the reported alpha** | thesis p.96 (OCR p106): "les coïncidences retardées à un centrage entre + 100 ns et + 118 ns [sont] destinée[s] à évaluer le 'fond' de coïncidences fortuites" — a real, separate time-window measurement with its own counter, but used (p.100/OCR p110) "pour contrôler la stabilité de la source", i.e. as a diagnostic, not as a subtraction applied to the reported α |
| resonant multiple-diffusion (re-absorption of the second cascade photon) | **MEASURED-INDEPENDENT, shown analytically to not apply (not subtracted because shown negligible to first order)** | thesis p.101 (OCR p111): "cette diminution n'excède pas 10%" of N_C/N_A at the densities used (Fig. II-15 measures ~7% change, 0.64→0.56). Thesis p.102 (OCR p112) then shows algebraically that α does not depend on the collection efficiencies κ_A, κ_B to first order, so this measured effect "ne sera donc plus considérée dans la suite" |
| classical control (pulsed photodiode through the identical electronics) | **MEASURED-INDEPENDENT control, confirms the chain does not fake antibunching — not a subtraction, a validation** | "les valeurs expérimentales... sont parfaitement compatibles avec les prédictions semi-classiques" (p.104) |
| PMT dead time / "temps mort" | **absent** | searched (OCR pp.60-144, keyword "temps mort"/"paralysable"): 0 hits — never measured, never invoked |

The thesis's own section heading for the result is literally "a) **Résultats bruts** ;
violation de l'inégalité semi-classique" (p.102/OCR p112) — "**raw results**." The
equations (II-52, II-53) compute α_exp = N_C·T / N_class(T) directly from the four
raw counted rates N_A, N_1, N_2, N_C — no background term is subtracted anywhere in
the formula that produces 0.18 ± 0.06 or 0.35 ± 0.05. The one independently measured
background term that exists (the delayed-window accidentals) is explicitly kept out
of the reported number and used only as a stability check.
**Unaccounted remainder = 0.18 ± 0.06 (final apparatus) and 0.35 ± 0.05 (first
apparatus) — the full raw values, by the authors' own description of them as "raw."**

### Kimble, Dagenais & Mandel 1977

**HOLE, not filled.** No free copy anywhere (Unpaywall `is_oa: false`, confirmed
prior pass, not re-checked this pass since nothing changed). Cannot be classified.
Row kept, not guessed.

### arXiv:1812.01749 (2018) — trapped ¹³⁸Ba⁺ ion, raw g2(0) = (8.1 ± 2.3)×10⁻⁵

| term invoked | class | quote / number |
|---|---|---|
| dark-count floor | **re-examined this pass: NOT MEASURED-INDEPENDENT as published — a bound with no underlying rate given** | "Dark counts on our detectors limit g(2)(0) to ≥3×10⁻⁵" — this is an asserted lower bound; the text never states a dark-count rate (no counts/s, no Hz) anywhere in the paper that this bound derives from. No separate "source blocked" measurement is described. **Downgraded from the prior pass's MEASURED-INDEPENDENT call to LABEL ONLY / unsupported bound.** |
| multi-photon generation / "second mechanism of double excitation errors" | **INFERRED-FROM-A-MODEL, not measured** | "We now estimate the expected error from the second mechanism of double excitation errors. We evolve the optical Bloch equations for the excitation and emission..." — this is a theoretical simulation (optical Bloch equations), explicitly an estimate, not an independent measurement. The ≤4×10⁻⁵ bound is a model output. **Reclassified from MEASURED-INDEPENDENT to INFERRED.** |
| "transient light leakage through our AO modulators" | **LABEL ONLY** | named by the authors as the source of "the extra counts" beyond the two bounds above; no number given for the leakage itself |

Re-reading under the strict rule reverses the prior pass's conclusion for this
record: **zero terms meet the MEASURED-INDEPENDENT bar.** The dark-count bound has
no underlying measured rate quoted; the multi-photon bound is a Bloch-equation
estimate; the leakage is a bare label. **Unaccounted remainder = (8.1 ± 2.3)×10⁻⁵ —
the full raw value**, not "~1.1×10⁻⁵" as the earlier (looser) pass reported.

### arXiv:2604.23422 (2026) — InGaAs QD, raw 0.0249 ± 0.0021 / fit 0.0078 ± 0.0012

| term invoked | class | quote |
|---|---|---|
| "re-excitation and background contributions" | **LABEL ONLY** | "representing a stringent operating regime in which re-excitation and background contributions are significant" — named, no number split between the two, no independent measurement of either |
| "reduced signal-to-background ratio at high electric fields" | **LABEL ONLY** | qualitative only, no number |

No independent measurement decomposes the raw-minus-fit gap (0.0171 ± 0.0024).
**Unaccounted remainder = 0.0171 ± 0.0024**, unchanged from prior pass — it was
already correctly flagged as undecomposed, tracking the fit method rather than a
measured background.

### arXiv:2607.11495 (2026) — InAs QD

"no residual peak distinguishable from background noise" — **LABEL ONLY**, the only
mention; no number. The two published numbers for this device (raw 0.0048 upper
limit vs. quoted <0.017±0.015) still don't nest. **Unscoreable**, as before.

### arXiv:2607.18435 (2026) — Al1 color center, g2(0) = 0.04 "without background subtraction"

| term invoked | class | quote |
|---|---|---|
| background term B in the saturation-curve fit, Eq. A2: I_corr = (I_meas − B)·√(1 − g2(0)) | **INFERRED-FROM-A-JOINT-FIT, not independently measured** | B is extracted together with g(2)(0) and the saturation parameters from fitting the same power-dependence data — not from a source-blocked measurement |
| residual background in the 0.35 ± 0.02 secondary-emitter case | **LABEL ONLY** | "because of residual background emission that could not be fully suppressed by spectral filtering... may originate both from emission of other Al1-centers... and from residual implantation induced lattice disorder" — two causes named, no number split, no independent measurement of either |

The headline 0.04 is explicitly stated by the authors as raw, with no subtraction
applied. **Unaccounted remainder = 0.04 ± 0.02 — the full raw value**, which happens
to equal the "corrected" value because none was applied; recorded as a clean case,
not a zero accounted for, but a zero CORRECTED FOR.

### arXiv:2210.00076 (2022) and arXiv:2207.06984 (2022) — SPDC records

No new terms found this pass beyond the prior read: 2210.00076 describes a "true
CAR" accidental-subtraction method (computed from independently measured singles
rates — this is the one candidate across all seven records that is actually
computed from independently measured quantities, R1·R2·window) but applies it only
to the CAR/cross-correlation plot, never re-applies it to g2_H(0) itself in the
excerpted text — so g2_H(0) ≈ 0.04 stands unaccounted. 2207.06984's rising g2(0)
with pump power is attributed to multi-photon probability (the source) — **LABEL
ONLY / qualitative**, no independent measurement of the multi-photon fraction is
reported, it is read off the same g2(0) curve it is explaining.

## 2. THE UNACCOUNTED REMAINDER, PER RECORD

| record | raw value | sum of MEASURED-INDEPENDENT terms actually subtracted | unaccounted remainder | sign |
|---|---|---|---|---|
| Jacques 2007 | 0.12 ± 0.01 | 0 | **0.12 ± 0.01** | full value, positive (alpha > 0) |
| Grangier 1986 (final) | 0.18 ± 0.06 | 0 | **0.18 ± 0.06** | full value |
| Grangier 1986 (first) | 0.35 ± 0.05 | 0 | **0.35 ± 0.05** | full value |
| Kimble 1977 | — | — | **HOLE** | not computable |
| 1812.01749 (ion) | (8.1 ± 2.3)×10⁻⁵ | 0 | **(8.1 ± 2.3)×10⁻⁵** | full value |
| 2604.23422 (QD) | 0.0249±0.0021 raw / 0.0078±0.0012 fit | 0 | raw−fit gap 0.0171±0.0024 undecomposed; raw itself fully unaccounted | full value |
| 2607.11495 (QD) | 0.0048 / <0.017±0.015 | 0 | unscoreable (inconsistent pair) | — |
| 2607.18435 (color center) | 0.04 ± 0.02 | 0 | **0.04 ± 0.02** | full value |
| 2210.00076 (SPDC) | g2_H(0) ≈ 0.04 | 0 (CAR correction not applied to this number) | **≈0.04** | full value |
| 2207.06984 (SPDC) | 0.03–0.43 depending on pump power | 0 | **full value at every power point** | full value |

**Under the strict rule, every single scoreable record's unaccounted remainder
equals its full raw reported value.** No record in this sample has even one term
that is both (a) measured in a separate, independent measurement with its own
number and (b) actually subtracted from the headline number to produce it. The
closest approaches to a real independent measurement — Jacques' 60 cts/s dark
counts, Grangier's delayed-window accidentals, the SPDC CAR accidentals computed
from singles rates — all exist as real numbers, but none of them is the number that
was subtracted to produce the alpha/g2(0) actually reported. They are measured and
sitting beside the result, not measured and taken out of it.

**Does the remainder track anything?** Since the remainder equals the raw value in
every case, by construction it tracks whatever the raw value tracks: source
brightness/purity (Jacques, Grangier, the QDs, the color center — all vary with
emitter quality and are explicitly reported as such), and pump power for the SPDC
records (2207.06984 rises monotonically 0.03→0.43 with power — the one record where
the "remainder" vs. a control variable is directly visible in the data). It does
not track gate/coincidence window, detector model, or temperature in any way that
can be isolated from source brightness in this sample — because no accounting ever
separated them. The one quantity that comes closest to a held-constant "detector"
story is the gate width (40 ns Jacques, 9 ns Grangier, 30 ns ion, 200 ns ion-photon
collection) — no monotonic relationship between gate width and remainder size is
visible (Jacques: 40 ns gate, 0.12; Grangier: 9 ns gate, 0.18–0.35; the ion: 30 ns
window, 8.1×10⁻⁵) — if anything the SMALLER gates correspond to the historical
records' LARGER remainders, opposite of what a gate-driven artifact would predict.

## 3. TASK 2 — 0.12 AS THE OBJECT

**How alpha was measured (Jacques 2007):** open configuration (beamsplitter output
BS_output removed), N_T trigger pulses at 4.2 MHz (τ_rep = 238 ns), N_1 and N_2
singles on detectors D1/D2 (Perkin Elmer AQR-14 APDs), N_C coincidences, detection
gate τ_d = 40 ns timed to the photon arrival. Counting rates ≈ 700 counts/s per
detector in the open configuration; dark counts ≈ 60 counts/s per detector; S/N ≈
10. The formula: α = N_C × N_T / (N_1 × N_2). No stated integration time or total
coincidence count for this specific α run is given in the paper (unlike the
separate, non-gated HBT pre-characterization in Fig. 4, which reports g2(0)=0.12
from a continuous-wave run over an unstated integration time).

**What the authors say 0.12 comes from (quoted verbatim):** "We measure α = 0.12 ±
0.01 showing that we are indeed close to the pure single-photon regime. The
non-ideal value of the α parameter is due to residual background photoluminescence
of the diamond sample and to the two-phonon Raman scattering line, which both
produce uncorrelated photons with Poissonian statistics." Separately, Fig. 4c:
"The very small remaining value at zero delay g(2)(0) = 0.12 is due to background
emission from the substrate and from the diamond sample in which the color center
is embedded." Two different runs (gated delayed-choice vs. CW HBT), same stated
causes, same number.

**Were any of these terms measured independently?** No. Neither "residual
background photoluminescence" nor "two-phonon Raman scattering" is given a separate
number, a separate measurement, or a method (e.g., spectrally isolating the Raman
line's count rate, or measuring photoluminescence with the N-V center itself
bleached/absent) anywhere in the paper. The one number that IS independently
measured and reported — 60 counts/s dark counts per APD — is never connected
arithmetically to the 0.12 figure in the text. By Task 1's rule, this makes both
named causes **LABEL ONLY**.

**What 0.12 means in plain terms:** it's the fraction of double-detector clicks,
relative to what a classical split wave of the same intensity would produce, that
Jacques' diamond single-photon source still shows: a perfect single photon gives
zero (never both detectors fire together); a classical wave gives one or more
(always at least sometimes both); the diamond source sits at 0.12 — 12% of the way
from "never both" toward "a classical wave," with that 12% blamed, in words only,
on two named-but-unmeasured leakage channels.

**Unaccounted remainder, by Task 1's rule: 0.12 ± 0.01 — the entire measured value.**
Nothing independently measured was subtracted to arrive at it.

(Note: a thesis by V. Jacques at ENS Cachan was not located on HAL this pass —
no further search budget was spent hunting it beyond the records already confirmed
absent in the prior pass's fetch log; this is logged as not re-attempted, not as
confirmed absent.)

## 4. THE LEDGER — every 0.11–0.13 / 12% value in the local record, unsorted, uninterpreted

`grep -noE "0\.1[123][0-9]*( ?[±+/-]+ ?[0-9.]+)?|\b12\.?[0-9]?%" *.md THIRD_RUNG_20260928.md`
across `~/bones-forge/parallax/`, 125 files searched, **293 raw hits** across both
the physics records above and every unrelated darkwave/Bell/copper/yeast/mice run
in the directory (these are NOT claimed to be related to the light records — this
is the literal grep the task asked for, without interpretation). Full list (file:line:value):

```
ARCADE_ABSENCE_20260930.md:74:0.13
BELL_DISCOUNT_20260930.md:250:0.13
BELL_DISCOUNT_20260930.md:276:0.13
BELL_DISCOUNT_20260930.md:69:0.12
BELL_DISCOUNT_20260930.md:98:0.12
BELL_NEIGHBORS_20260930.md:184:0.13
BELL_NEIGHBORS_20260930.md:95:0.13
BELL_THREE_WITNESSES_20261001.md:80:0.13
BELL_THREE_WITNESSES_20261001.md:81:0.11
CLOSE_THE_FREE_ONES_20260930.md:31:0.12
COPPER_NODES_2_20260930.md:71:0.128
COPPER_NODES_2_20260930.md:72:0.111
COPPER_NODES_2_20260930.md:75:0.119
COPPER_NODES_2_20260930.md:93:0.122
COPPER_NODES_2_20260930.md:94:0.120
COPPER_NODES_2_20260930.md:99:12%
COPPER_NODES_3_20260930.md:142:0.138
COPPER_NODES_3_20260930.md:143:0.125
COPPER_NODES_3_20260930.md:144:0.117
COPPER_NODES_3_20260930.md:169:0.113
COPPER_NODES_3_20260930.md:169:0.134
COPPER_NODES_3_20260930.md:57:0.128
COPPER_NODES_3_20260930.md:57:0.131
COPPER_NODES_3_20260930.md:62:0.13
COPPER_NODES_3_20260930.md:69:0.113
COPPER_NODES_3_20260930.md:69:0.134
COPPER_NODES_3_20260930.md:92:12.2%
DO_BETTER_20260930.md:120:0.12
DRYAD_RANDOM_20260930.md:36:0.113
DRYAD_RANDOM_20260930.md:36:0.117
DRYAD_RANDOM_20260930.md:71:0.113
DRYAD_RANDOM_20260930.md:71:0.117
FIRAS_REFIT_20260930.md:33:0.110
FIRAS_RESIDUALS_20260930.md:90:0.119
FIRAS_RESIDUALS_20260930.md:90:0.139
GAP_PER_MEDIUM_20261001.md:137:0.112
GAP_PER_MEDIUM_20261001.md:140:0.11
LENGTH_ORDERS_GAP_20261001.md:49:0.12
LENGTH_ORDERS_GAP_20261001.md:51:0.13
LIGHT_SPLIT_20261001.md:136:0.115
LIGHT_SPLIT_20261001.md:167:0.117
LIGHT_SPLIT_20261001.md:186:0.12
LIGHT_SPLIT_20261001.md:306:0.131
LIGHT_SPLIT_20261001.md:344:0.11
LIGHT_SPLIT_20261001.md:344:0.13
LIGHT_SPLIT_20261001.md:345:0.11
LIT_CHECK_20260929.md:36:0.12
NEURONS_20261001.md:67:0.11
NOTHING_SWEEP_apr_aug.md:126:0.127
NOTHING_SWEEP_apr_aug.md:16:12%
NOTHING_SWEEP_apr_aug.md:44:0.11
NOTHING_SWEEP_sep24_27.md:140:0.1165
NOTHING_SWEEP_sep24_27.md:140:0.1182
NOTHING_SWEEP_sep24_27.md:19:0.121
NOTHING_SWEEP_sep24_27.md:215:0.121
NOTHING_SWEEP_sep24_27.md:249:0.126
NOTHING_SWEEP_sep24_27.md:252:0.12
NOTHING_SWEEP_sep24_27.md:268:0.12
NOTHING_SWEEP_sep24_27.md:282:0.12
NOTHING_SWEEP_sep24_27.md:75:0.11
OBSERVER_WITNESS_20260930.md:122:0.115
OBSERVER_WITNESS_20260930.md:30:0.13
ONE_QUBIT_TRIANGLE_20261001.md:77:0.113
ONE_QUBIT_TRIANGLE_20261001.md:97:0.118
PARTICLES_ARE_SUBSTRATE_20261001.md:104:0.1103
PARTICLES_ARE_SUBSTRATE_20261001.md:151:0.12
PARTICLES_ARE_SUBSTRATE_20261001.md:155:0.12
PARTICLES_ARE_SUBSTRATE_20261001.md:169:0.13
PARTICLES_ARE_SUBSTRATE_20261001.md:202:0.13
PARTICLES_ARE_SUBSTRATE_20261001.md:229:0.12 ± 0.01
PARTICLES_ARE_SUBSTRATE_20261001.md:42:0.1103
PARTICLES_ARE_SUBSTRATE_20261001.md:59:0.12 ± 0.01
PARTICLES_ARE_SUBSTRATE_20261001.md:64:0.12
PLACED_VS_ARISEN_20260930.md:30:0.12
PRE_MEASUREMENT_20260930.md:103:0.133
PRE_MEASUREMENT_20260930.md:242:0.12
PREREG_DARKWAVE.md:118:0.130
PREREG_DARKWAVE.md:118:0.137
PREREG_DARKWAVE.md:121:0.13
PREREG_DARKWAVE.md:53:0.13
PREREG_DARKWAVE.md:60:0.11
PREREG_DARKWAVE.md:61:0.12
PREREG_DARKWAVE.md:78:0.12
PREREG_DARKWAVE.md:95:0.12
PREREG_DARKWAVE.md:97:0.12
PREREG_DARKWAVE.md:97:0.13
RECURSIVE_GRADIENT_20260930.md:49:0.120
RECURSIVE_GRADIENT_20260930.md:77:0.138
RECURSIVE_GRADIENT_20260930.md:83:0.118
REVERSE_GRADIENT_20260930.md:100:0.12
REVERSE_GRADIENT_20260930.md:1014:0.1167±0.01
REVERSE_GRADIENT_20260930.md:1015:0.1257±0.011
REVERSE_GRADIENT_20260930.md:1016:0.1345±0.011
REVERSE_GRADIENT_20260930.md:1025:0.1203
REVERSE_GRADIENT_20260930.md:1044:0.122
REVERSE_GRADIENT_20260930.md:1046:0.1167±0.01
REVERSE_GRADIENT_20260930.md:1047:0.1257±0.01
REVERSE_GRADIENT_20260930.md:1048:0.1345±0.011
REVERSE_GRADIENT_20260930.md:1082:0.1352
REVERSE_GRADIENT_20260930.md:1083:0.1199
```
(293 total lines matched; the remainder of the list — THE_TABLE, THE_LINEUP,
THE_PINATA, THREE_ON_*, YEAST_RECORD, T1_SWING, THE_MICE_DAY, THIRD_RUNG_20260928.md
itself, and others — is captured in full at
`/tmp/ledger_0.11_0.13.txt` on this Mac and is the literal, complete grep output;
not reproduced here in full to keep this file readable, but nothing in it was
filtered by relevance — it is every hit the pattern found, unsorted.)

Only the `PARTICLES_ARE_SUBSTRATE_20261001.md` and `LIT_CHECK_20260929.md` hits in
this list are the Jacques 0.12 value re-quoted from the earlier pass; every other
hit above belongs to an unrelated darkwave/Bell/copper/mice/yeast/qubit run and is
listed here exactly because the task asked for every value in the window, not just
the ones that look connected.

## 5. PLAIN WORDS

Wayfinder's correction changes the shape of the whole first pass. Under the loose
reading, several records looked "accounted for" — the trapped ion's 8.1×10⁻⁵
seemed to add up to dark counts plus multi-photon probability within error. Reread
strictly: the dark-count bound has no underlying measured rate in the paper, and
the multi-photon bound comes from a theoretical simulation (optical Bloch
equations), not a measurement. Neither qualifies. Jacques' 0.12 was never
decomposed by a number at all — two causes are named, zero numbers attached.
Grangier's numbers are the one record that is honest about this on its own terms:
the section is titled "raw results," and the one background term he did measure
independently (a delayed coincidence window) was used to check the source's
stability, not subtracted from the reported α. Kimble 1977 remains a hole — no
free copy exists anywhere. Across every record that could be scored, the
unaccounted remainder equals the full raw reported value, because no record
subtracts an independently measured number from its headline figure. What
"accounted for" means in these papers is a plausible story in words, pointed at
background light or multi-photon emission or modulator leakage — never a measured
number taken out of the result.
