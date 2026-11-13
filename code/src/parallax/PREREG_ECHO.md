# THE ECHO RUN -- pre-registration (2026-09-28, written before any shot; Bones)
Wayfinder's hot take of the day: the CMB is a reverberation. So: measure the reverberation inside the freezer.
Every shot LOOKS FIRST (m0) before doing anything: what did the previous shot leave behind?
  E1 jobs: measure m0; X; measure m1   -> every shot follows a shot that ENDED IN 1
  E0 jobs: measure m0; measure m1      -> every shot follows a shot that ENDED IN 0 (control)
  shot spacing (rep_delay): 20, 50, 100, 250, 500, 1000, 2000 us; 1500 shots each; ibm_marrakesh, every even qubit, raw I/Q.
Fixed analysis: clouds from E0 m1 (prepared 0) and E1 m1 (prepared 1) at 2000 us; echo(delay) = P(m0 reads 1 | E1) - P(m0 reads 1 | E0).
 1. Does the echo shrink as the gap grows?  2. Fit echo = A*exp(-delay/tau) per qubit; compare tau to IBM's T1 for that qubit.
    tau ~ T1: the qubit's own memory (the tank). tau >> T1: something else holds the memory (the lens). tau << T1: the reset erases it.
No numeric prediction claimed. All numbers recorded.
