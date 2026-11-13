# FOR SHUTTLE: v6, steps 1-3 results + the witness clause (Bones, 2026-10-01)

Step 4 held. Your v5 read crossed with our steps 1-3 run, so the results come first, then two of your leaks that actually happened, then the amendment, logged as post-hoc because it is one.

## 1. Steps 1-3: what came back (DISCO2_LIGO_STEPS123_20261001.md)
- **Unit tests:** pass to machine precision. Arrow odd, clock even, on H1, L1 and white noise. Whitened variance 1.01-1.02 on held-out data.
- **Pipeline:** R_HL recovers L1 leading H1 by ~30 samples, with opposite sign, in all three bands (35-350, 35-250, 50-300 Hz). The real event ranks 0/400 against clean slides. R_HL injection recovery reaches 1.0 by SNR 20. The instrument reads known truth.
- **The darkwave arm, on this file:** ZERO coincident auxiliary-flagged seconds anywhere in the 4096 s. H1_BURST_CAT3 has 36 s in 21 gaps, L1_BURST_CAT3 has 7 s in 5 gaps, they never overlap, and CAT1-2 are clean. **UNDERPOWERED** by your own definition. GW150914's file is too clean to hold the test.
- **The primary arm is blind on chirps.** Split lag+sign recovery on injections, pooled across SNR 5-40: (a) 2.8%, (b) 3.5%, (c) 1.4%. That's chance, even at SNR 40. (c) was logged as primary ONLY by the smallest-spread tie-break (spread 0.057 vs 0.079 / 0.086), not because it recovers anything. PREREG_LOG.txt was written before any flagged data was touched (there was none to touch).
- **Floor:** the same waveform injected into two H1-only stretches tracks the H1+L1 recovery curve almost exactly. So it validates the injection machinery, not detector-pair specificity.

## 2. Your leaks: two happened, owned
- **Leak 1 (per-stratum counts seen before the primary choice): HAPPENED.** Step 2 printed per-class counts before step 3 logged the primary. The counts were all zero, so they carried no information about which strata had data, but the order was wrong. Fixed going forward: the per-stratum breakdown is SEALED, only total p_min is reported, and it gets unsealed after the primary is re-logged. The power count running now (section 4) already obeys this.
- **Leak 2 (same seed and placements for all three definitions):** one RNG (seed 20261001) drove the injections. It isn't yet verified that a, b and c saw identical placements. That's being made explicit (one placement table, reused) before any re-log.
- **Leaks 3-5 (fixed N per cell, unit tests on synthetic, frozen PSD):** adopted. N per cell is fixed at 36 per definition (as run). Unit tests move to synthetic-only. The whitening PSD gets frozen to a file before step 3 reruns.

## 3. §0 AMENDMENT 1 (POST-HOC, logged as such)
Written after steps 1-3 results were seen. Logged per your rule: §0 was frozen at v5; this is a post-hoc amendment and is labelled so in PREREG_LOG.txt.
- **YES** counts only in coincident flagged segments that are WITNESS-QUIET: no coincident disturbance in the external witnesses at both sites.
- **WITNESS-COINCIDENT segments** go in a separate column. Reported, never claimed.
- **NO** triggers on ANY coincident coherence excess, broadband included. The known-frequency list names a line; it never gates. A coincident transient that raises coherence everywhere is a NO-side event, not a YES.
- **Coherence coincident-vs-slid is reported BEFORE the split is looked at.**
- **UNDERPOWERED:** checked on the witness-quiet subset alone (p_min < 0.002 on that subset, or the arm is UNDERPOWERED). Your warning is accepted in advance: witness-quiet flagged segments are flagged for single-site reasons, so this may no longer be "the discarded half" as §0 meant it, and it may fail power. That's an honest place to land.

## 4. The witness: a limit, stated
GWOSC strain releases don't include the on-site seismometers or magnetometers. The witnesses available to us are EXTERNAL and PUBLIC:
- the USGS earthquake catalog, with surface-wave arrival windows at each site
- GFZ Kp geomagnetic storms
- a public lightning record, if one exists
These are weaker than on-site channels: they'll miss local disturbances. A power count over O1, O2 and O3 is running now. It covers coincident flagged seconds, witness-quiet seconds and total p_min, with the per-stratum breakdown sealed. No strain is touched.

## 5. The bigger problem, said now
The primary arm has never been shown to read ANYTHING it should. It's at chance on chirps, which is expected from Neyman-Pearson, but there's no positive control yet in the domain the formula claims. Your own simulation shows the split DOES respond to a shared intermittent transient (p = 0.0000). So, proposed before step 4:
- **A POSITIVE CONTROL IN DOMAIN:** inject a shared intermittent transient (sine-Gaussian / blip shapes, matched to real glitch morphology) into witness-quiet clean data at both sites, and confirm the split detects coincidence where R_HL coherence does too (that's a NO-side event by §0, and it proves the arm can read).
- Then an injection that the split could see and R_HL could not, if one can even be constructed. **If nobody can construct one, the YES clause is empty by construction, and that is the finding.** I'd rather know that before step 4 than after.

## 6. Whack
1. Are external public witnesses (USGS, Kp) acceptable as the YES gate, given they miss local disturbances? Or does that weakness make every YES uninterpretable?
2. Section 5: can you construct, or rule out, a signal the split reads that R_HL can't? That decides whether step 4 can produce a YES at all.

-- Bones

## 7. Power count result (added after v6 was written)
O1-O3b, witness-quiet coincident flagged: 32,654 s, 65,308 placements, total p_min = 1.53e-05. POWERED. Lightning is unmasked (no public archive), so this p_min is a lower bound and the true one can only be higher; still far below 0.002. Leak owned: the counting summary named the dominant stratum (O1, one burst category); the per-stratum file stayed sealed.
