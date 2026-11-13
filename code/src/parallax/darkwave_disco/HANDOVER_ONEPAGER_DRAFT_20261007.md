# How one qubit's measurement reaches the rest of the chip: a clock-by-clock map

*Draft for a conversation, not for circulation. Heuremen, October 2026. Done with AI assistance. Read WITHDRAWALS_20261007.md first: what we took back, and the ruler behind each. Full ledger, calls, code and raw data on request.*

## What we did
We used idle qubits on commercial processors as clocks: each held half-way and read on two hands (phase and amplitude) against an idle arm of the same duration in the same job.
We used them to time measurements of other qubits on IBM Heron devices (Kingston, Pittsburgh, Fez, Marrakesh, Boston, Aachen, Phoenix) and Rigetti Cepheus-1-108Q, over several days.
Before its first shot, every run had its predictions written, SHA-256 hashed and OpenTimestamped, and its readings were scored against them. Misses are printed beside hits.

## What holds (after the same day's ruler checks)
1. **Each spectator has its own, steady response to a neighbour's measurement.**
   - Read per clock, the phase kick per measurement is that pair's own number: steady to about 7% read to read, and to ±2% as a chip over six reads.
   - A minority of spectators carry most of it (200-900 mrad per measurement on Kingston); most carry little.
   - Distance doesn't set it. On Pittsburgh, single measured qubits give each nearby spectator a repeatable kick of either sign, with no common fall-off.
2. **The kicks add.** A spectator's kick with many measured neighbours equals the sum of what each gives it alone (within ~20% on 8 of 9 spectators, three reads).
   - In phase units, the exposure dependence is about linear (exponent 1.1-1.2 ± 0.3 on two chips).
3. **The measured qubit's state doesn't change the measurement's own kick. All the state dependence is static ZZ on the coupler.** On two chips (Kingston, Pittsburgh):
   - Spectators with no coupler to a measured qubit respond the same to |0>, |1> and a superposition (per-clock |1>/|0> ratio 1.009).
   - Coupled spectators carry static ZZ, measured in the same job with no measurement: linear in hold time, half the size for a superposed neighbour (0.46-0.57), and zero without a coupler.
4. **ZZ and the measurement kick compose as a product, not a sum.** Turns add, hand shrinks multiply, with a cross term.
   - Most coupled cells can't tell the two apart through their own read-to-read noise: 72-90% sit within it.
   - Where the data can decide, the product wins 45 to 2, on both chips (Kingston 37 to 2, Pittsburgh 8 to 0).
5. **A spectator's apparent lean (reading the measurement as longer or shorter) follows its own detuning in the drive frame.**
   - The physical kick has one sign.
   - Read as time, it flips with the sign of the spectator's turn: eight runs, five chips.
   - Aliasing in our 10 µs reference windows mislabels a few fast spectators (2 of 58 on Kingston, 13 of 86 on Pittsburgh), and we now check this against idle arms.
6. **The measured qubits' own decay with repeated measurement sits below simple bookkeeping**: below zero on every heavy-hex run, every average, carried by most bits.

## What's open
- On Kingston, a spectator's kick tracks how long its coupled neighbour's own measurement runs (rank +0.64 over 12 coupled pairs). Fresh data on two other chips leans the same way but doesn't clear chance.
- **Which spectators carry large kicks.** The split is bimodal: on Kingston, 5 of 12 coupled spectators take 220-550 mrad per measurement and 7 take about zero, at the same ZZ.
  It isn't set by exposure, coupling strength, or the spectator's own T1, T2 or readout error. Frequency is the leading unread suspect, and a frequency-sweep arm would read it.

## What we'd ask
- Which of these a standard readout-crosstalk-plus-ZZ model already predicts.
- Whether the idle-clock method, with idle arms at matched times and per-clock pairing, is useful as a characterization tool in its own right.
