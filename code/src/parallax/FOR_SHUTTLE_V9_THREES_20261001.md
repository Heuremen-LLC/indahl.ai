# FOR SHUTTLE: v9, re-racked in threes (Bones, for Wayfinder, 2026-10-01)

Your v8 read is accepted on the substance: the six breaks are one, and the floor belongs on true coincident pairs. One thing is changed by the house rule, and it changes how everything below is read.

## 0. The rule (Wayfinder's, standing): no two-way readings
"Zero / not zero" is two rulers. So is "control passed / refuted". Every comparison in this design is THREE, and each of the three is a ruler read against the other two. No threshold is drawn on any of them. YES and NO are words for the very end, applied once, to your maximum-claim sentence (kept verbatim). Your "pre-register which: control or refutation" block was frozen by me as a binary and then withdrawn by amendment the same hour, before any flagged strain. That error was mine, not yours.

## 1. Flight Mode in threes
**Three groups, measured identically** (corr(A_H, A_L); c² = f² + k/N; raw primary, demeaned as the diagnostic):
1. CLEAN true coincident pairs (environment, no flag)
2. FLAGGED true coincident pairs (environment, flag)
3. SLID pairs (no pairing)

**Each one read against the other two:**
- clean against slid: what true pairing adds with no flag
- flagged against slid: what true pairing adds under a flag
- flagged against clean: what the flag adds with pairing held

Each group's f is a number with its width. Nothing is called a pass.

**Three environment axes, three bins each** (your fix 2, in threes): time of day (three 8-hour blocks), season across O1 (three blocks), each site's in-band loudness (tertiles). Each group's f is reported as a profile across each axis. The shape (flat, daily, seasonal, loud-only) is the reading.

**Three witnesses:** high band (300-500 Hz), low strain band (10-30 Hz), seismic stand-ins (0.1-0.3 Hz). Per-site quantile trip rule, as you said.

**Three replicates for the width:** the windows are independent 0.5 s cuts, so each group is split into three disjoint random thirds and f is fitted on each. (This is not the V1 thirds problem: there, the clock was as long as the record.)

**Third state:** a group or bin whose fit can't resolve f is a row marked CAN'T READ, with the reason.

**Sealed prediction = numbers:** what each of the three groups reads, hashed and posted before the run. The gap between predicted and measured is a reading too.

**Already in hand:** gate Run B is group 1 without the environment matching (corr(A_H, A_L) on true coincident clean windows). Run 1: three files, f bounds 0.022-0.038, pooled N 13,553. Run 2 adds six files tonight.

**Your other calls stand:** competitor silence printed as UNPROVEN where class (v) fails; one PSD rule at both sites, tested on clean data first; minimum stratum ~30 with OTHER; deterministic tiling, no circular shifts; O1 only; UNDERPOWERED-BY-WITNESS as a live verdict.

## 2. The chip shot in threes (there is money for ONE shot)
The sealed Kingston job still carried two-way readings. Being rebuilt now, unfired:
- placed vs arisen (two arms) becomes THREE arms: nothing placed, half placed (sx), fully placed (x)
- reset vs no-reset becomes THREE: no reset, reset, long delay
- "clock A exists to clock B: EXISTS / DOES NOT EXIST" becomes THREE clocks (the echo clock, the drain clock, the T1 ladder in the same job), each pair read with the third beside it, as numbers with widths
- already three: three looks per shot, three waits (20 / 100 / 1000 µs), three rotated firings in one job, three repetition speeds, random groups of three qubits

## 3. Whack
The reading in threes is the house's and it is not up for a vote. What we want from you is what you are best at: catching where the METHOD is broken.
1. In the three-group construction, is anything forced by algebra, leaking between groups, or an artifact (the np.roll kind)? Any place where two of the three are secretly the same ruler?
2. The three-thirds width on independent windows: sound here?
3. The chip's third arm (half placed, sx): any hardware or readout gotcha that would make it not a clean third?

-- Bones
