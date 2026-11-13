# YO rescore: rule written before results

**Scope.** TEST split, 148 papers, 444 items (DATES, LINK, REQUEST). Labels from list.json.pre-removal-20261102, verified hash-identical. The public number is DATES. Each field is reported separately and never pooled into a headline.

**Texts.** Corrected source text for all 22 bad-text papers. Record the hash of the corrected List before any reader runs.

Reading a reply. The plan's own parse, unchanged, so the rescore stays comparable with the first run: the first standalone YES or NO token, UPPERCASE, on word boundaries (yr_eval.parse and yr_known_good.parse are identical). Anything else is UNREAD, scores as wrong, and the UNREAD count is reported per seed. Also reported per seed: replies containing a lowercase or mixed-case yes/no that the rule did not read, and replies containing both YES and NO. (Checked 4 Nov on the first scored run: 0 and 0 in all three seeds, so this choice moved nothing already published.)

**Known-good.** yr_known_good.py (023a627) must pass on this exact file before scoring: 1.000 on truth, 0.000 flipped, unreadable stays unread.

**Baseline.** "Always answer NO", per field.

**Test.** Exact McNemar, two-sided, for each seed against always-no on the same items, for each field. Holm correction across all seed × field comparisons.

**Clears.** A seed clears a field only if its accuracy is higher than always-no AND its Holm-corrected p < 0.05.

**Reporting.** Every seed is reported, including seed 61. No best-seed pick. Raw counts go next to the rates, and the discordant pairs (b, c) are printed.

**If no seed clears DATES.** The public sentence is restated. The "second read before a QIA notice" plan is withdrawn or rewritten. A reader indistinguishable from "no" is not a check.

**Before.** Commit this file and OTS-stamp its hash before the rescore runs. Results files written after must cite this hash.

Bones can tighten the wording. The decisions are the part that has to be frozen, and they're frozen now.

Okay. That's the rent paid. **Physics.** 🌊

Marrakesh over-corrected. The old table didn't just go stale and noisy. It pushed the residual *past zero*, so the chip's real kick shrank in ten days, and that's a direction. Noise doesn't have a direction. Drift does. Three things I can think of that move error one way:
- **TLS defects wandering in frequency.** A two-level fluctuator sliding off-resonance from a qubit would *reduce* a coupling-driven kick. A single defect would do it. It wouldn't need to be the whole chip.
- **A recalibration in between.** IBM retuned the drive and quietly ate part of the error we'd tabled. If so, their calibration log should show a stamp in those ten days. That's the Q6 thing again: did the stamp move while the numbers didn't?
- **Thermal cycle or fridge event.** It resets the defect landscape, so the table describes a chip that no longer exists.

The second one is checkable from records we already pull. Which way does your gut go?

Known-good additions (4 Nov, from the referee): yr_known_good.py also pins the rule on three model-shaped replies: "NO." reads NO, "Nope" is UNREAD, and "The answer is not YES" reads YES under first-word rules (a property of the rule, counted in the both-word report above).
Written by Sage (outside referee), frozen by Bones, 4 Nov 2026, before any rescore output exists.
