# Plan addendum for Faults and Guards 2.0, IRIS LAB (12 November 2026)

Written on 12 November 2026 before any reading under Faults and Guards version 2.0.0. The plan (PLAN_IRIS_INDEX.md) and the FaultsBench round plans name no size that matters, no band, no edge convention, no interval level for the outcome words and no reason list. The audit of 12 November 2026 therefore could not judge this desk. This addendum decides them. The author of this addendum decided every value below. None was fixed by the original plans.

## What is unchanged

Data, sources, items, prompts, replies, scoring code and tests are unchanged beyond the outcome rule. The original PLAN_IRIS_INDEX.md and every round plan and CODE.sha256 are not edited. Every outcome recorded earlier stands under the rules it named, and the 2.0 reading is printed beside it.

## Reading 1: the guard effect

Quantity read: for one model and one Fault family in one round, the paired difference in the share of items that commit the Fault, Guard wording minus plain prompt, over the items read in both arms.

- Null: 0.
- Size that matters: 0.10, ten percentage points of the share, in both directions.
- Band: [-0.10, +0.10]. The size that matters and the band edge are the same number.
- Edge convention: closed at both edges.
- Outcomes: ABOVE means the whole interval lies above +0.10 (the Guard wording raises the fault). BELOW means the whole interval lies below -0.10 (the Guard wording cuts the fault). CONSISTENT means the whole interval lies inside the band and does not reach both the null and a size that matters. Anything else is CANNOT_TELL.
- Interval method: percentile bootstrap over the paired items, 2,000 draws, seed 7, 95 percent, the 50th and 1,950th of the 2,000 sorted draws. This is the method each round's score.py already coded and committed before any reply was read.
- Rates of the Fault by arm are descriptive. They carry a Wilson interval at 95 percent and no outcome word.

## Reading 2: a recount of a paper, cell by cell

A cell is an exact row-level read of a printed value against the value rebuilt from the paper's own code and outputs. No sampling is involved, so the interval has zero width. The band is the printed value plus or minus half of its last printed digit, with closed edges. A rebuilt value inside the band is CONSISTENT. This replaces the word CLEAN, which is retired as an outcome. A rebuilt value above the band is ABOVE and below it is BELOW, and the gap and its width are printed. Where the paper's own table is built from a sample, the cell is read with the interval method the paper names or, if it names none, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.

## How this desk's CANNOT_TELL causes map to the closed reasons

- The repeat gate or the family control failed (the instrument failed its known-good check): NO_INTERVAL_FORMABLE. The planned quantity is not formed because the readings are not trusted enough to take an interval from.
- Fewer than 10 item pairs read in both arms: TOO_WIDE_TO_RESOLVE. The floor of 10 is the one the round scoring already used. A reading below a desk's minimum sample is TOO_WIDE_TO_RESOLVE.
- Code or outputs of a paper incomplete so that a cell cannot be rebuilt: NO_INTERVAL_FORMABLE.
- An interval that overlaps the band edge: STRADDLES_EDGE.
- An interval that holds the null and the size that matters: TOO_WIDE_TO_RESOLVE, whatever else it touches.

## Failed reads

A fetch or parse that fails is NOTHING_RETURNED, a status of the read, and is outside the numerator and the denominator. It is never an outcome. A guard effect that cannot be computed is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.

## Counts beside the reading

Beside every share of cells the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason (REQ-13), built with the kit's req13.
