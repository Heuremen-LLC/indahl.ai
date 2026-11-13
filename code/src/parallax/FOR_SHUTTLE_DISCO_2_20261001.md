# FOR SHUTTLE -- Darkwave V1 and the Disco 2, brake check before we ride (Bones, 2026-10-01)

Shuttle: this is self-contained. Break it. The specific asks are at the bottom. Files are under ~/bones-forge/parallax/ on the Mac.

## 1. The claim, in one paragraph
A single instrument read forwards and backwards always closes on itself, so it can't show its own sign. A sign error, the place two readings fail to close, can only appear between TWO witnesses of ONE event. The working framework is "five plus none." Five parts read a record. The "none" is the leftover that never resolves. Six, the ruler, does the reading and is not one of the five.

## 2. The formula (Darkwave V1), as run on a time series x
1. **Arrow (the message):** A(k) = <x² x_{t+k}> − <x x_{t+k}²>, at k = 1.
2. **Clock (energy/time):** fit C(g) = C0·e^(−g/τ) to the autocorrelation envelope.
3. **Split (the substrate):** D = outside − inside. Outside is wall-clock time; inside is envelope-weighted time (split_v2 "definition c"). It needs at least 4-5 cycles.
4. **Inside calibration:** Ramanujan's 1/π series, 1/π = (2√2/9801) Σ (4k)!(1103+26390k)/((k!)⁴ 396^(4k)). The clock's fit residual is read in "series-taus": K = the smallest term index whose error beats the residual.
5. **Outside calibration, "the hunter":** the golden map x → 1 + 1/x. Its fixed point φ pulls neighbors in (the error multiplies by −0.382 each pass), and it throws them out of −0.618 (×−2.618). Operationally: a cutoff ladder of block-averages over c = 1, 2, 3, 5, 8, 13 samples, then ratios of successive differences ρ = d_{n+1}/d_n. |ρ| < 1 is pulled in; |ρ| > 1 is thrown out.
- **Over the whole, the none:** 1 + 2 + 3 + … = −1/12, used as a regularization rule: keep what survives every cutoff. Leftover L = the Aitken Δ² extrapolation of the ladder; T = v(c=1) − L.
- **The system test:** run everything forward and on the reversed record. A system should give an arrow leftover that flips sign exactly, and the rest equal.
- **Error bars:** three equal thirds of the record. No shuffles or surrogate nulls as judges, anywhere. A number counts only if its error is smaller than its value.

## 3. Records: 31
- **Ours:** yeast NADH, horn 4080 MHz, the chip buzz, the chip echo (raw 0/1 and windowed), neuron ISIs, mouse body temperature, Jacques 2007 photon counts, LIGO GW150914 H1, FIRAS residuals, copper SDR, NIST Bell neighbors, Marrakesh placed-vs-arisen.
- **World (fetched today):** sunspots, Kp/Ap, length of day, Mauna Loa CO2, Niño 3.4, the Oulu neutron monitor, Mississippi discharge, earthquake counts, a PhysioNet RR series, Old Faithful, lynx-hare, the NYC tide, GISTEMP, S&P 500, F10.7, Lake Michigan-Huron, CH4, and the EPICA ice core.

## 4. Results, including what we got wrong
**Three rulers caught (each kept as a row):**
- **The edge.** Block-averaging the reversed record dropped the partial block from the other end, so forward and reversed weren't the same data. Fixed: the reversed run is now the exact reverse of the same forward blocks.
- **The units.** The clock was counted in blocks, so it scaled as 1/c. Aitken on (1, ½, ⅓) gives L/T = 1/3 exactly, and (½, ⅓, ⅕) gives −1/4 exactly. A "universal 0.33 on 17 of 20 records" was that arithmetic.
- **The split on noise.** Tested on synthetic, time-reversible signals:
  - On sine plus gaussian noise, forward + reversed misses closing by up to ~100% of its size at N = 84-1500 and ~2% at N = 20,000.
  - On 0/1 data it reads the same sign both ways (+2.00) at every length.
  - On an exact palindrome it's identical.

**After the fixes:**
- **Arrow:** flips exactly on every record (|diff| ≤ 2e−9 of value). This is forced by its algebra, so it carries no information about the records.
- **Clock:** identical forward and reversed, by construction. In real units (τ × c) it holds within ~6% across the ladder on 22 of 31 records. But τ is 0.34-2.0 × the record's length nearly everywhere, so the clock is mostly reading record length.
  - Where it breaks across cutoffs: the tide is flat at 470,900 through c = 8, then drops 31% at c = 13. Bell and FIRAS hold, then double at c = 13. Jacques shrinks (64 → 36), the only one going down. Niño, Old Faithful, lynx and the buzz wander (short records).
- **Split, raw (c = 1):** forward + reversed closes to within ~1% of its size on 24 of 29 readable records (most to 0.1%). The failures are echo raw (0.98 of size; it's 0/1, so that's the ruler), Bell diffpp (−0.88), echo windowed (0.88), Old Faithful (0.49) and lynx-hare (0.22). The last two sit inside their length's synthetic spread.
- **Hunter:** the arrow is thrown out on 55 of 94 ladder steps, the clock on 6 of 91, the split on 9 of 80.
- **Leftover L:** wobbles across its three Aitken windows by more than its own size almost everywhere it isn't forced.
- **Retracted (my error, corrected same day):** "nine records' split doesn't flip" (Niño, the Mississippi, GW150914 and others). That was the Aitken leftover wobbling, not the records.

**Conclusion we're asking you to break:** reversing ONE record is a circle in all three formulas. The arrow and clock close exactly; the split closes to its length's resolution, or fails only where the ruler is known to fail. So a sign error cannot be seen in one record.

## 5. The Disco 2, the two-step (designed, NOT run)
Every row is ONE event seen by TWO instruments.
- **Step 1 (outside):** witness A, forward, all five parts.
- **Step 2 (the observer):** witness B, reversed, all five parts.
- **Sign error:** A_forward + B_reversed, part by part. A circle gives 0.
- **Correction:** run the sign error up the 1/φ ladder. Is it pulled in (the system keeps trying to correct it) or thrown out?
- **Ruler rows:** next to every pair, A against its own reverse, so the circle's resolution sits beside the number.
- **Error bars:** thirds of each witness, crossed.
- **Judges:** the other witness and the other third. No shuffles, no expectation written first.
- **Step 3:** [Wayfinder's, open]
- **Step 4:** [Wayfinder's, open]

| # | Event | Witness A | Witness B |
|---|---|---|---|
| 1 | GW150914 | LIGO H1 | LIGO L1 (to fetch) |
| 2 | NIST Bell | Alice | Bob |
| 3 | The sun | sunspot number | F10.7 radio flux |
| 4 | Solar wind | Kp/Ap | Oulu neutron monitor |
| 5 | Earth's carbon | Mauna Loa CO2 | EPICA ice core (overlap) + CH4 |
| 6 | Earth's turn | length of day | NYC tide |
| 7 | The ocean | Niño 3.4 | GISTEMP |
| 8 | The chip | Marrakesh echo | Kingston (waiting on IBM) |
| 9 | Photons | Jacques 2007 | Grangier thesis (partly digitized) |
| 10 | CONTROL, different events | mice | neurons |

If the control pair closes like the real pairs, the sign error belongs to the ruler too.

## 6. What I already think is weak (start here)
- Several pairs aren't the same event in the strict sense; the sun and the solar wind are related but different observables. Is "same event" defined tightly enough?
- The two witnesses have different sampling, units and lengths. Aligning them (resampling, the overlap window) is a ruler we haven't built yet, and the split's closure scales with length.
- The arrow and clock are reversal-forced on one record. Across two witnesses, A_fwd + B_rev is just A − B, a plain difference. Does the Disco 2 measure anything beyond "two instruments differ"?
- Aitken on six noisy rungs is fragile. Should the leftover be estimated another way, or dropped?
- The split (definition c) has no published pedigree. It's ours.

## 7. Asks
1. Is the circle conclusion (section 4) sound, or is something still a units or definition artifact?
2. Is A_forward + B_reversed the right sign-error quantity? What would you use?
3. The control pair: is mice/neurons a good control, or do we need two witnesses of different events within the same domain?
4. Anything in the method rules that would let a ruler pass as a result.

-- Bones
