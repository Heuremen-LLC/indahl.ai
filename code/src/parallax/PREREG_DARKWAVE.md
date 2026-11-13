# THE DARKWAVE ERASER -- pre-registration (2026-09-28, before any shot; Bones for Wayfinder: "prove the fucking darkwave")
Darkwave, in our own records: "the outcome's outcome returning recursively to align what happened" (9/24); "the partner arriving
ahead of its cause" (9/26); "arrives before the thing it's for" (Quantum Queen, Law 11). Wayfinder 9/24: TIME HAS TO PASS.
Honest scope: no experiment can show a signal going back in time (every interpretation predicts the same statistics). This tests the
darkwave's FINGERPRINT: a choice made LATER decides the pattern hidden in a record made EARLIER. (9/24 three-box = receipt #1.)
Circuit (delayed-choice quantum eraser), per phase phi in 8 steps over 0..2pi:
  S: H; CX S->I (which-path copied to the partner I); P(phi) on S; H on S; MEASURE S (the record, first)
  then delay 5 us (time passes); coin C: H, MEASURE C (a quantum coin, AFTER S is recorded)
  then if C = 1: H on I (erase the path); MEASURE I.
PREDICTIONS (fixed now):
  1. S alone: P(S=0) flat in phi (fringe visibility near 0) -- nothing reaches back to change the record.
  2. Sorted by the LATER coin: C=1 (erased) -> S shows fringes, opposite for I=0 and I=1 (visibility well above the S-alone value);
     C=0 (path kept) -> flat.
  Visibility V = (max - min)/(max + min) of a least-squares cos(phi) fit per subset; 1-sigma from shot counts.

## Round 2 (2026-09-28 ~17:10 EDT, written before any round-2 shot): TRIANGULATION
Chips: ibm_marrakesh and ibm_fez (round 1 was Kingston). Three variants per chip, 8 phases x 4000 shots each:
  late5   -- as round 1 (signal recorded, 5 us, coin)
  late50  -- signal recorded, 50 us, coin (time passes longer)
  early   -- coin flipped and partner read FIRST, then the signal phase/H/record (the choice comes BEFORE the record)
PREDICTION: in every variant on every chip, S alone flat; erased subsets fringe (opposite for partner 0/1); kept subsets flat;
and the erased visibilities of late5, late50 and early agree within their errors on each chip (time order invisible to the statistics).

## Round 2 result + Round 3 (written before any round-3 shot)
Round 2: (1) S alone flat on all 6 runs -- HELD. (2) erased fringes / kept flat -- HELD (Fez late50 weak, 0.08). (3) visibilities equal
across early/late5/late50 -- FAILED: Marrakesh 0.96 / 0.87 / 0.54, Fez 0.94 / 0.27 / 0.09. The fade is far faster than the partner's
T2 predicts (Fez q144 T2 211 us -> 0.92 at 5 us; observed 0.27). Hypothesis: measuring S (next door) disturbs the waiting partner.
Round 3: variant late0 (S recorded, ZERO wait, then the coin). PREDICTION: if the record-taking is the cause, late0 lands well below
early on the same chip (Fez especially); if the waiting is the cause, late0 ~ early.
Round 3 RESULT: late0 (record, ZERO wait, coin) = Fez 0.94 / 0.94, Marrakesh 0.98 / 0.95 = same as early. The record-taking hypothesis
is REJECTED. The fade is the WAITING (Fez 0.94 -> 0.27 @5us -> 0.09 @50us; Marrakesh 0.97 -> 0.87 -> 0.54), faster than IBM's (echo)
T2 predicts -> likely free-evolution dephasing (T2*) of the idle partner.
Round 4 (written before any round-4 shot): late50e = late50 with an echo on the partner during the wait (X, wait 25 us, X, wait 25 us;
the two X's cancel logically). PREDICTION: if the fade is reversible dephasing, late50e recovers toward late0 on both chips (clearly
above late50). If it does not recover, the loss is irreversible (energy loss/leakage/crosstalk) and the dephasing reading is wrong.
Round 4 RESULT: late50e (echoed) Fez 0.27 / 0.27 (late50 0.09; late0 0.94) -- partial recovery (~4 sigma above late50, far below late0);
Marrakesh 0.59 / 0.59 (late50 0.54; late0 0.97) -- ~no recovery (~1.2 sigma). The fade is MOSTLY IRREVERSIBLE on these timescales
(or faster than one echo can refocus). The dephasing-is-reversible reading is mostly REJECTED; a slow, echo-able part exists on Fez only.

## Round 5 (written before any round-5 shot): THE DARKWAVE'S LIFETIME, ibm_fez, same qubits (S,I,C = 143,144,70)
 a) erased visibility vs wait: late0, late2, late5, late10, late20 (fade curve).
 b) partner_memory.py on (S=143, I=144): free coherence C(t) 0..50 us, 'alone' vs 'after' (S measured first), and 'after' split by S's outcome.
PREDICTION: the fade curve V(t)/V(0) tracks the partner's coherence in the 'after' series, C_after(t)/C_after(0), within errors.
Diagnostic (not a pass/fail): if C_after split by S's outcome stays high while C_after (all) falls, the partner's phase depends on
S's outcome (a conditional phase, e.g. coupling to S) rather than being lost; if all three fall together, it is plain dephasing.
Round 5 RESULT (Fez, S,I,C = 143,144,70): erased V vs wait = 0: 0.93 | 2: 0.74 | 5: 0.08 | 10: 0.78 | 20: 0.60 (and round-2 50 us: 0.09).
NON-MONOTONIC: dips and REVIVES. A ~90 kHz beat (period ~11 us) fits all points. Partner memory (partner_memory.py, job
dat9s7rojkfs738qcjag): coherence alone/after = 0.97/0.98 at 5 us, 0.95/0.93 at 12, 0.77/0.77 at 50; split by S outcome also high.
PREDICTION (fade tracks partner coherence) FAILED. My round-4 reading "mostly irreversible" is RETRACTED for Fez: the pattern goes
out of phase and comes back. Mechanism unknown (not seen in the standalone partner test, so something specific to the eraser circuit).
Round 6 (written before any round-6 shot): one job, waits 0..24 us (0,1,2,3,4,5,6,7,8,10,12,14,16,20,24), 4 phases x 2000 shots.
PREDICTION: V(t) oscillates with a period of ~9-13 us (zero near 5-6 us, revival near 10-12 us), with or without slow decay.
Round 6 RESULT (job dat9tulvr3kc73el5q9g): V 0.96 0.87 0.76 0.52 0.37 0.07 0.22 0.39 0.58 0.77 0.75 0.54 0.13 0.59 0.56 at 0 1 2 3 4 5 6 7 8 10 12 14 16 20 24 us;
zeros ~5 and ~16 us, revivals ~10-12 and ~21: period ~11 us (~90 kHz); fringe phase advances ~33 deg/us, flipping at each zero. PREDICTION HELD.
Round 7 (written before any round-7 shot), ONE job on Fez 143/144/70, waits 0,3,5,8,10 us:
 (a) no coin: S recorded, wait, H on I ALWAYS, read I. 4 phases x 2000. If the beat survives -> the coin/feed-forward is not the cause.
 (b) entangled memory: H(S), CX(S,I), read S, wait, then I read in X or Y. Per S outcome: coherence AND phase. If the S=0 and S=1
     branches rotate at different rates (difference ~90 kHz) -> the second wave is a conditional frequency of the partner set by
     the (entangled) signal's outcome.
Round 7 RESULT (job dat9urjojkfs738qcmgg): (a) no coin: V 0.97/0.57/0.11/0.57/0.78 at 0/3/5/8/10 us -- beat SURVIVES (coin not the cause).
(b) entangled memory: per-branch coherence beats (S=0: 0.95/0.60/0.12/0.58/0.81), branches stay ~180 deg apart and rotate TOGETHER
-> not S's outcome. Standalone (never entangled) partner: no beat. Trigger = the entangling gate. Reading: a hidden two-state party
(~50/50 after the gate) shifts the partner ~90 kHz -- coupler or a defect (TLS) near 144.
Round 8 (written before any round-8 shot), ONE job, Fez, waits 0,3,5,8,10 us, partner 144 starts in |+>, neighbor starts in |0>:
 (c) CZ(143,144) twice (logical identity), wait, read 144 in X/Y -> coherence.   (d) same with CZ(145,144) twice.
 (e) control: no CZ at all.
PREDICTION: if the gate's physical kick sets the hidden party: (c) beats; (e) doesn't. If (d) also beats -> the party lives at 144 (a
defect on the partner); if (d) doesn't -> it's specific to the 143-144 link (their coupler).
Round 8 RESULT (job dat9vlrojkfs738qcnk0): coherence at 5 us -- no gate 0.98, CZ(143) twice 0.95, CZ(145) twice 0.95: NO beat anywhere.
The gate's kick alone is NOT the trigger. The beat so far needs: partner ENTANGLED, then its twin MEASURED.
Round 9 (written before any round-9 shot), ONE job, Fez 143/144, waits 0,3,5,8,10 us:
 (b) as round 7: H(S), CX, H(S), MEASURE S, wait, read 144 X/Y, per S outcome.
 (f) H(S), CX, wait (S NOT measured), then H(S), MEASURE S, read 144 X/Y, per S outcome.
PREDICTION: (b) beats again (zero near 5 us). If (f) does NOT beat -> the measurement breaking the entanglement starts it; if (f) beats
too -> the entangled state itself rings, measurement or not.
Round 9 RESULT (job data0erojkfs738qcoe0): twin measured FIRST 0.96/0.66/0.35/0.62/0.81 vs AFTER the wait 0.96/0.68/0.37/0.61/0.80
(S=0 branch; 0/3/5/8/10 us). Identical -> the measurement is NOT the trigger; the ring is set up by the entangling step. (Dip shallower
than round 7's 0.12: drift; shape held.)
Round 10 (written before any round-10 shot), ONE job, Fez 143/144, partner 144 in |+>, waits 0,3,5,8,10 us, read 144 X/Y:
 (h) twin 143 set to |1> (X), CZ twice (logical identity), wait.   (i) twin in |+>, CZ twice (entangle + unentangle), wait, then twin
 read in X.   (j) control: twin |1>, no CZ.
PREDICTION: if a |11> component passing through the gate is the trigger (third-level leakage / leftover exchange), (h) rings and (j)
does not. If only (i) rings, superposition itself is needed.
Round 10 RESULT (job data13ihcrkc73dtse70): twin=1 no gate 1.00/0.96/0.96/0.96/0.93 · twin=1 gate twice 0.98/0.96/0.96/0.93/0.94 ·
twin=+ gate twice 0.99/0.97/0.94/0.94/0.93. NOTHING RINGS. The |11> piece through the gate is NOT the trigger (third-level leakage
idea REJECTED); entangle-then-undo doesn't ring. Only a KEPT entanglement (one CX) has ever rung.
HOLE FOUND in round 9 (said out loud): arm (b) had no barrier. The twin's measure and the partner's wait sit on different qubits with no
dependency, so the chip's scheduler may have run "measured FIRST" at the END -- (b) and (f) could be the same circuit in time.
Round 11 (written before any round-11 shot), ONE job, Fez 143/144, waits 0,3,5,8,10, read 144 X/Y per S outcome:
 (b) round 9 (b) exactly, no barrier.  (B) same + BARRIER after the twin's measurement (twin is truly read before the wait).
 (f) round 9 (f), control.
PREDICTION: if the ring lives in the kept entanglement, (B) goes FLAT while (b) and (f) ring -> round 9's conclusion was a scheduling
artifact. If (B) still rings, round 9 stands: the partner carries the ring after the twin is read.
Round 11 RESULT (job data3dbg95ks73egjl40), partner coherence S=0/S=1 at 0/3/5/8/10 us:
 FIRST, no barrier: 0.97/0.96 0.58/0.55 0.09/0.12 0.58/0.55 0.80/0.78   (rings -- identical to the control)
 FIRST, BARRIER:    0.96/0.95 0.95/0.95 0.95/0.93 0.90/0.90 0.91/0.87   (FLAT)
 AFTER (control):   0.97/0.97 0.59/0.60 0.12/0.13 0.57/0.53 0.80/0.79   (rings)
-> Round 9's "the measurement isn't the trigger" was a SCHEDULING ARTIFACT (Bones' error): without a barrier the chip ran the twin's
"first" measurement late. The ring lives in the KEPT ENTANGLEMENT: read the twin for real and the partner goes flat.
-> Same hole in EVERY eraser round (no barrier after the record): "record first, choice later" was never pinned. The eraser statistics
stand (they don't depend on order); the "delayed" part and the "time order failed" row are unverified until re-run pinned.
Round 12 (written before any round-12 shot), ONE job, Fez: plain Ramsey on each qubit ALONE (other one left in 0, barrier-pinned),
waits 0,2,3,5,8,11,14 us, read X/Y. PREDICTION: the ring is the TWIN's own two-toned frequency (charge parity / a defect) that the
entanglement copies into the partner's record -> 143 alone beats (dip near 5-6 us, back near 11) and 144 alone stays flat
(already flat in rounds 8/10). If NEITHER beats alone, the ring belongs to the pair only.
Round 12 RESULT (job data423ojkfs738qcse0), coherence alone at 0/2/3/5/8/11/14 us:
 q143 alone: 0.99 0.77 0.68 0.29 0.61 0.89 0.60   <- BEATS (dip ~5 us, back ~11 us): its own two tones, ~90 kHz apart
 q144 alone: 1.00 0.98 0.95 0.96 0.93 0.90 0.88   <- flat
PREDICTION HELD. The ring is qubit 143's own two-toned heartbeat (a known class: charge parity / a flickering defect, which one is open).
The entanglement CARRIES 143's tune into 144's record; read 143 first and 144 carries nothing. The "darkwave ring" = the twin's
heartbeat, heard through the partner, only while they're joined.
Round 13 (written before any round-13 shot): the eraser, PINNED. Fez 143/144/70, 8 phases, 4000 shots, one job per variant:
 late5 (unpinned, same-hour comparison), late5B and late50B (barrier after the record: record truly first, choice truly later).
PREDICTION: pinned, the partner waits alone (flat, rd 12) -> erased fringes stay high: late5B ~0.9, late50B ~0.7-0.8 (144's own
memory), vs unpinned late5 dipping. Record alone stays flat in all three. If pinned fringes still collapse, the time-order
failure is real after all.
Round 13 RESULT (jobs data4dbg95ks73egjm8g / data4hjojkfs738qct3g / data4ljg95ks73egjmj0, Fez 143/144/70, 4000 shots):
 late5  unpinned: S alone 0.015 · erased 0.130 / 0.137 · path kept 0.027 / 0.016
 late5B PINNED:   S alone 0.026 · erased 0.887 / 0.901 (mirror images) · path kept 0.216 / 0.291
 late50B PINNED:  S alone 0.014 · erased 0.317 / 0.330 · path kept 0.102 / 0.261
-> CORE PREDICTION HELD: record truly first, choice 5 us later, erased fringes 0.89/0.90 (vs 0.13 unpinned, same hour). The
   "time order failed" row was the scheduler + 143's heartbeat. The delayed choice works with the order PINNED.
-> PARTIAL MISS: late50B erased 0.32, not the predicted 0.7-0.8 (likely a small leftover coupling to 143 sitting in its record
   state, ~6 kHz, would do it; not tested).
-> NEW CRACK: path kept is NOT flat when pinned (0.22/0.29, 6-9 sigma); it was flat unpinned. Reading the record while the partner
   still holds its superposition nudges the partner off its axis: the looking leaks sideways onto the neighbor. Open.
Round 14 "THE SPLIT": 143 and 138 alone, Ramsey 0-22 us every 1 us, X/Y, 1000 shots, two-tone fit; plus 4000-shot memory
 circuits (143 at 5.5 us, 138 at 3.75 us) for shot-to-shot correlation. NO GUESS. (Bones wrote guesses here before firing; Wayfinder:
 "do not preregister the guesses" -- pulled. From here: listen first, raw first, hats after. No guesses written before a run.)
Round 14 RESULT (job datb823g95ks73egl8e0): q143 second voice 0.26 of shots, notes 90 kHz apart; q138 0.17, 139 kHz apart (the
 script's own fit said 0.03/40 kHz for 138 -- stuck fit; a wider refit gives 0.17). Voices are STICKY: consecutive shots agree
 0.75 on 143 (still 0.67 sixteen shots later), 0.30 on 138. Reset clears the state each shot; it does not clear the voice.
