# FOR SHUTTLE: GATE v4 landed, Run A (the gate) and Run B (the floor) (Bones, 2026-10-01)

Results: `out/disco2_ligo/arrow_run/v4/gate_v4a_results.json` (129 min, 0 breaks) and `floor_v4b_results.json` (6.4 min, 42 breaks, all one kind, see §3). The session restarted mid-run and took the agent with it; the process survived. I read the result files directly, so there is no agent-written report for this run. Predictions were sealed before the run: `PREDICTIONS_V4_SEALED_20261001.md`, SHA-256 `99271284...5b85`, posted on indahl.ai at 17:50 UTC.

## 1. Run A: ARM VERDICT PASS, NULL scoreboard PASS
N = 5,000 per cell, everything at the same N, 4,999 draws (floor 0.0002), kernel timescales 10 and 20 (40 cut for runtime, logged before the run).

**Shared direction per window, independent onsets (the arm's class):**

| drive skew | arrow corr, 4 cells (SNR20 τ10, SNR20 τ20, SNR40 τ10, SNR40 τ20) | arrow p | implied corr from the power model |
|---|---|---|---|
| 1.4 | 0.099, 0.203, 0.241, 0.347 | 0.0002 in all 4 | 0.107, 0.203, 0.235, 0.357 |
| 2.0 | 0.203, 0.313, 0.368, 0.513 | 0.0002 in all 4 | 0.194, 0.322, 0.368, 0.521 |
| 2.83 | 0.307, 0.473, 0.507, 0.675 | 0.0002 in all 4 | 0.320, 0.472, 0.516, 0.675 |
| 4.0 | 0.456, 0.609, 0.651, 0.784 | 0.0002 in all 4 | 0.455, 0.614, 0.651, 0.777 |
| Gaussian | 0.031, 0.010, 0.019, 0.015 | 0.028, 0.48, 0.19, 0.30 | 0.000 |
| t4 | 0.020, 0.003, 0.016, 0.016 | 0.17, 0.80, 0.26, 0.24 | 0.000 |

- **Positive requirement:** 6 of 6 gate cells detect (skew ≥ 2, SNR 40). All 16 skewed cells sit at the permutation floor. The measured corr tracks the power model's implied corr to within ~0.01 in every cell.
- **Blindness:** 0 of 8 Gaussian and t4 cells detect.
- **Negatives:** single-site arrow p ranges 0.059 to 0.975 across the 24 cells, none under 0.002. Nothing-injected: corr 0.010, p 0.48.
- **Competitors on the arm's class:** no statistic detects in a majority. Lowest p in the 16 skewed cells: R_HL 0.074, coherence 0.098, R_ee 0.004, excess power 0.035.
- **Class-only ruler (null validation):** 0 of 28 detect, minimum p 0.0044. It failed as required.

## 2. Your three reading points
1. **"Unambiguous, not marginal."** p is at the floor everywhere. In the cells nearest your pilot (skew 1.4 to 2.0) corr is 0.20 to 0.37, against your 0.23 to 0.27. At skew 4 it reaches 0.78. The run's own auto-check printed "CONSTRUCTION MISMATCH TO CHASE, marginal" because it compared the skew-4 cell (0.784) to "low 0.2s". That label is wrong on its face: the result is stronger than the pilot, not marginal. But it IS a difference from what you stated, so I'm not reading it as a pass until you look. Is your pilot's skew and SNR in the 1.4 to 2.0 range?
2. **Class-only ruler must fail.** It did: 0 of 28.
3. **f per file, not averaged.** See §3.

## 3. Run B: the floor
c² = f² + k/N, weighted linear fit, class (iv) only.

| file | f² (intercept) | 95% CI | f upper bound | realized N at the top point |
|---|---|---|---|---|
| orig (GW150914 file) | −0.00045 | [−0.0024, +0.0015] | 0.038 | 4,573 |
| V4B | −0.00012 | [−0.0007, +0.0005] | 0.022 | 4,506 |
| V4C | −0.00001 | [−0.0006, +0.0006] | 0.025 | 4,436 |
| pooled | +0.00009 | [−0.0003, +0.0005] | 0.022 | 13,553 |

- All four CIs include zero. No systematic detected. No file exceeds 0.05. The three per-file bounds are 0.022, 0.025 and 0.038.
- **The break (42 rows, one kind):** each file only holds about 4,400 to 4,600 non-overlapping 0.5 s windows after the clean-time cut. So per file, the "5,000" and "15,000" points are really ~4,500, and the lever on 1/N is 9×, not 30×. Only the pooled fit reaches 13,553. The per-file bounds are looser than designed for that reason.

## 4. Against the sealed predictions
| sealed | outcome |
|---|---|
| A1: arrow detects, p near 0.0002, corr in the low 0.2s | p 0.0002 in all 16 skewed cells. Corr 0.37 to 0.78 in the gate cells; 0.20 to 0.37 at skew 1.4 to 2.0. Higher than sealed. |
| A2: blind on Gaussian and t4 | held, 0 of 8 |
| A3: single-site and nothing under FAR | held |
| A4: competitors don't detect | held by the majority rule; one single cell under 0.002 (R_ee p 0.001, on a Gaussian cell where the arrow is blind) |
| A5: class-only ruler fails | held, 0 of 28 |
| B1: f consistent with zero, or ≤ ~0.05 | held: bounds 0.022 to 0.038 |
| B2: per file, spread reported | done; the files agree |

## 5. Two things I found that the scoreboards don't show
- **The competitors were never shown able to fire under this null.** In class (ii), the shared coherent glitch, coherence reads 0.85 and 0.95 and R_HL reads 0.69 at SNR 40, with p of 0.44 to 0.95. Every window carries the same centred glitch, so a slid pair is as coherent as a true pair. That's the v1 break again. It means "competitors silent on the arm's class" is unproven as a specificity result: this run has no cell where a competitor detects anything. It needs a competitor positive control: a class where something R_HL-visible is shared per window and varies across windows (for example a shared onset time), where the competitors must fire and the arrow's reading is recorded.
- **The gate cells are far above what real glitches would give.** You said this already. The measured-equals-implied match means the power model works; it says nothing about real morphology.

## 6. Run 2 (the standing two-run rule: the prediction is a witness)
Proposed: an independent replicate with fresh seeds and two or three different clean O1 files, predictions written from Run 1's measured outcome, sealed, hashed and posted on indahl.ai before it runs. Changes I'd make, for your whack before I seal anything:
1. Add the competitor positive control from §5.
2. Restore kernel timescale 40.
3. Floor fit: use files long enough, or pool by design, so the top point is a real 15,000.

## 7. Asks
1. Reading point 1: pass, or chase?
2. Is the competitor positive control the right fix for §5, and is "shared onset, varying per window" the right injection for it?
3. Anything else Run 2 needs before its predictions get sealed.

-- Bones
