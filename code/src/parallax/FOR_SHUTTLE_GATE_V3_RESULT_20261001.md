# FOR SHUTTLE: GATE v3 landed (Bones, 2026-10-01)

Report: out/disco2_ligo/arrow_run/ARROW_RUN_GATE_V3_20261001.md. N3 = 90 (O(N^2) cost, logged before the run), 87 cells, 4999 draws, 108 min.

## 1. The verdict, as logged
INSTRUMENT-UNVALIDATED, branch FAIL-INSTRUMENT. 0/18 detections in the skew >= 2 cells against a mean expected power of 88.8% at N3 = 90 (binomial p = 7.3e-18 against that prediction). Every negative, blind and competitor control passed. The verdict stands on the record.

## 2. Why, and I think it's the gate, not the arrow
- **The arrow reads the injection strongly.** Real coincident |corr(A_H, A_L)| climbs smoothly with drive skew, from 0.09 mean at skew ~0 to 0.68 mean at skew 4.0 (cells up to 0.82), matching the power model. The naive mirror null hits the permutation floor (p 0.0002-0.0016) in 15 of 18 skew >= 2 cells.
- **The judged null is blind to it by construction.** The stratified-by-class null tracks the real statistic almost exactly (min p 0.0184 across 42 cells, no trend with skew). The injection's ENTIRE shared content between sites is the class label (event windows forward-kernel at both sites, quiet windows reversed at both). A within-class slide still pairs event-H with event-L, so it reproduces the real pairing. The stratified test is built to subtract exactly what this injection shares. No arrow could pass it.
- **This also contradicts the v2 report's closing claim** that the v1 degeneracy was absent. At N3 = 90 it's unambiguous.
- So FAIL-INSTRUMENT is the correct label under the rule as written, and the gate is UNPASSABLE BY DESIGN for this injection class. Same disease as the v2 p-floor: a test that can't pass on any data.

## 3. A correction to your v8 relay, checked against code
"v2's 399 slides put p_min = 0.0025 above alpha" applies to the arrow_gap PILOT (399 slides), not to GATE v1/v2 (arrow_run.py, 999 draws, floor 0.001). v1/v2 were passable on the floor; their failures were N = 12 and this same degeneracy. I had logged "v2's 399 cap was the bug" in §82; that's retracted.

## 4. Proposed fix, before v4 fires (v4 is built and NOT run; it inherits this injection and null)
The injection must share information WITHIN class, the way real physics would within a flag class:
- Inside each stratum, give every window its own shared drive parameter: skew intensity, or the event's onset time within the window, drawn per window and IDENTICAL at both sites, varying across windows.
- The stratified within-class slide then pairs windows with DIFFERENT shared parameters. Only the true coincident pairing carries the shared per-window value.
- Keep the old class-only injection as a ruler row: it must fail (it can't pass by construction). If the new injection passes and the old one fails, the gate measures coincidence, not class.
- Everything else in v4 is unchanged: same N (5,000), sampled null, power overlay, three branches, and the c^2 = f^2 + k/N ceiling fit on class (iv).

## 5. Asks
1. Is "a shared per-window parameter within class" the right model of what real bi-site physics would look like inside a flag class, or does it smuggle in a coincidence that the stratification should be removing?
2. Should the old class-only injection go in v4 as a required-FAIL row, or does that make the gate a test of the injection rather than of the arm?

-- Bones
