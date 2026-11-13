# YO v5 post, draft for the referee (1 Nov 2026)

## A. Rows added to the results table (yo2_result.json, shown on indahl.ai/iris/lab), after the YO v4 block and before YO v3. Columns: comparison | difference (95 % band over test records) | outcome

1. "YO v5 continued training YO v4 on records whose qubits were all calibrated at once, so that every qubit in a record shows the same date (same-date records). It was trained twice, with seeds 47 and 48, both fixed in the plan before any data was built, and each run was scored once on YO v4's test records and on a new test set of same-date records. Planned readings first:" | "" | ""
2. "Same-date records older than 24 hours, stale qubits found out of 2,320: YO v4 2,240, seed 47 2,312, seed 48 2,297. Each seed minus YO v4." | "+0.031 [+0.008, +0.059], +0.025 [−0.002, +0.055]" | "above, cannot tell"
3. "Same-date records younger than 24 hours, qubits flagged out of 2,400, none of them stale: YO v4 0, seed 47 0, seed 48 0." | "0.000 [0.000, 0.000] for both seeds" | "consistent, consistent"
4. "Records whose 8 qubits all sit 20 to 50 hours from their stamp, stale qubits found out of 928: YO v4 905, seed 47 928, seed 48 902. Each seed minus YO v4." | "+0.025 [+0.000, +0.054], −0.003 [−0.043, +0.034]" | "cannot tell, cannot tell"
5. "Record audit on the everyday mix of records: YO v4 0.990, seed 47 0.988, seed 48 0.987." | "−0.002 [−0.013, +0.008], −0.003 [−0.011, +0.005], inside the 0.02 margin" | "consistent, consistent"
6. "Of the qubits flagged as stale, the number truly stale: YO v4 1,127 of 1,128, seed 47 1,172 of 1,197, seed 48 1,124 of 1,133." | "−0.020 [−0.046, −0.001], −0.007 [−0.023, +0.000]" | "below, cannot tell"
7. "Four-outcome verdict out of 400: YO v4 390, seed 47 392, seed 48 354." | "+0.005 [−0.010, +0.020], −0.090 [−0.121, −0.058]" | "cannot tell, below"
8. "CANNOT_TELL items given another verdict, out of 100: YO v4 5, seed 47 8, seed 48 45." | "" | ""
9. "New IBM records that arrived after the plan was committed, read the way the live reader reads them: 15 records, and YO v4, seed 47 and seed 48 were each exact on all 15." | "" | ""
10. "Plan rule: YO v5 replaces YO v4 only if both seeds find more of the same-date stale qubits, flag no more of the young ones, and are not below YO v4 on the four readings above it. Seed 47 is below on the flags it gets right and seed 48 on the verdicts, so YO v4 stays the model at work and YO v5 is reported as tried." | "" | ""
11. "Defined after the data: on YO v4's test items seed 47 missed none of the stale qubits (YO v4 missed 45) and flagged 25 that were not stale (YO v4 flagged 1). YO v4's own three seeds flagged 1, 25 and 8." | "" | ""
12. "Defined after the data: item by item against YO v4, seed 47 was exactly right where YO v4 was not on 6 audit items and wrong where YO v4 was right on 9 (of 390), on verdicts 6 and 4 (of 400), and on same-date items 10 and 4 (of 590)." | "" | ""

## B. The YO one-liner on indahl.ai/iris/lab gains a sentence after "...where YO v2 found 403.":
"YO v5, trained further on records whose qubits were all calibrated at once, found 2,312 and 2,297 of 2,320 such stale qubits with its two seeds, where YO v4 found 2,240, but one seed lost precision and the other lost verdicts, so YO v4 stays at work."

## C. Model card (huggingface.co/indahl/YO), new short section "YO v5, tried":
"YO v5 continued training YO v4 on records whose qubits were all calibrated at once, with two seeds fixed in the plan before any data was built (PLAN_YO_V5.md). On a new test set of such records it found 2,312 and 2,297 of 2,320 stale qubits, where YO v4 found 2,240, and flagged none of the 2,400 qubits younger than a day. On YO v4's own test set seed 47 flagged 25 qubits that were not stale (YO v4 flagged 1, and, defined after the data, YO v4's own three seeds flagged 1, 25 and 8) and seed 48 gave a verdict to 45 of 100 items that had none (YO v4 gave 5). By the rule written before training YO v4 stays the model at work."
