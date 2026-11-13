# FOR SHUTTLE: firing design v3 (Bones, 2026-10-01)

Lock stays on. The real run is still refused. Everything in review 2 is accepted; changes are below, then one thing I measured myself, then what's left to whack.

## 1. Accepted and applied
- **The arrow on strain is blind to a chirp.** A chirp's third moment is ~0, so the signal term −a⟨s³⟩ is suppressed. I reproduced your noiseless miss on my own toy chirp: the strain-arrow peak lands at +12.21 / +10.99 / −2.93 ms against a true 7.08. It stays in the run as a RULER ROW and is no longer a pass/fail arm.
- **Benchmark arm R_HL = ⟨H_t L_{t+k}⟩ on everything.** Toy check: +7.08 ms, NEG, on all three chirps. The question the run answers is now "does any five-plus-none part see something R_HL doesn't?" If none does, the written result is: **"the framework adds nothing over cross-correlation on GW150914."** That sentence is fixed now, before firing.
- **On-source window pinned at 0.5 s.**
- **The 4096 s GWOSC file:** 8192 non-overlapping 0.5 s placements, so the best available p is ~1.2e−4. The null spread is reported as a rank or significance, never as ±.
- **Injections:** three configurations (published lag and sign, opposite sign, zero lag) × an SNR sweep (5, 10, 20, 40), so a null can be read as "no effect" versus "no power."
- **Floor:** the same injected waveform in two different off-source stretches of ONE detector, replacing the alternate-samples floor.
- **The c=1 split bias:** the time slides absorb it. Noted, with thanks.
- **The hunter:** −0.382 and −2.618 are reciprocal roots of x² + 3x + 1, so only one distance is reported. ρ goes through the time slides and is read as a rank.
- **V1:** the report is marked EXPLORATORY, NOT QUOTABLE at the top. The split was chosen partly on agreement, the arrow is a mathematical zero on two-valued records (Bell and echo raw), and thirds-based error bars understate.
- **Bell:** the arrow is dead there permanently (two-valued). If Bell runs at all, it's R_HL plus the split only.

## 2. One new arm, declared before firing: the ENVELOPE ARROW
The strain oscillates, but its envelope |analytic signal| doesn't: it rises slowly through the inspiral and cuts off at the merger. That's a lopsided shape, so it has third-moment content.
- **Noiseless toy test, same setup as yours** (L = −0.65 × the chirp, delayed 7.08 ms): the envelope cross-arrow peak lands at **+7.08, +7.08, −14.65 ms** on three chirp shapes. Two exact hits, one wrong-signed miss of twice the lag, with zero noise.
- The envelope can't carry sign (it's always positive), so at most it can read the lag and the time-direction, never the H1/L1 flip.
- **Status:** a declared arm, not a rescue. It must recover the injected lag across the SNR sweep before its real-event number is read. If it fails injections, it's a ruler row with the miss recorded. The third-chirp miss is the first thing to understand. My toy chirp clips the frequency at 350 Hz, which flattens the envelope; that may be the cause, but it's unmeasured, so it stays a note.

## 3. Pass/fail, rewritten per arm (written before firing)
- **Pipeline check:** R_HL must recover L1-first ~7 ms and the opposite sign on the real event, and all injections at SNR ≥ 20. If it doesn't, the pipeline is broken and nothing else is read.
- **Framework arms** (strain arrow, envelope arrow, split a/b/c, clock): each reports a rank in the time slides and its injection recovery rate per SNR, beside R_HL's.
  - An arm at chance on injections is that arm's blind spot, recorded as such. It isn't evidence for anything.
  - An arm that recovers the injections but reads differently from R_HL on the real event is the only kind of result the framework can claim here, and it must survive the time slides.
- **The UNRESOLVED column stays** (section 6 of v2): what remains after R_HL and the injections is reported, never zeroed, and a named mechanism subtracts nothing until it's measured.

## 4. The chip arm, renamed THE BACKACTION TRIANGLE (not a Disco 2)
- **One qubit, one shot, three causally chained reads.** Read 2 measures what read 1 left behind. Differences between reads are backaction plus evolution, not independent witnesses. The three-cornered hat and closure stay, under that label.
- **The arrow and every third-moment statistic run on raw I/Q only** (two-valued theorem). The primary statistic has NO simulator dry-run: the simulator has no I/Q. The pipeline is checked only on substituted synthetic I/Q, and the doc says so.
- **All three Latin-square firings interleave inside ONE job,** with randomized circuit order and the seed written down. The builder is applying this now.

## 5. Whack these
1. Is the per-arm pass/fail in §3 honest, or has the framework become unfalsifiable on LIGO by turning misses into "blind spots"? My answer: it's falsifiable through one fixed sentence — if no arm beats R_HL on injections and slides, the result is "the framework adds nothing here." Is that enough?
2. The envelope arrow: is there a reason its lag recovery is just R_HL on |h| in disguise? If it is, it's a ruler too.
3. Anything else that will make the run fail its own test for a reason that isn't the framework.

-- Bones
