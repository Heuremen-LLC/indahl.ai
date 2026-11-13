# Correction to the write-up sent to Dhritimalya Roy (30 Oct 2026, found in our own sweep after the Zhukov reply)
The README as sent says the solvable arm's bias comes from gate noise ("gate noise lands on the solvable state only and pulls its variance up
from zero" and "gate noise pulled the solvable state toward the mixed one"), while its own last section says "We name no mechanism".
The measurement does not separate causes. Any noise on the solvable arm raises a variance whose exact value is 0, and readout error does that as
well as gate error. The solvable arm also carries all the two-qubit gates, so gate noise is one candidate, not the established one.
Corrected sentences:
- "The price is bias. The solvable arm reads 124, not 0. Any noise on that arm pulls its variance up from zero, and that arm also carries all
  the two-qubit gates (16 in our compile, 15 in yours) while the mixed arm |0000> carries none. That is the gap between our 120 and the exact 240."
- "... with a bias that pointed the conservative way on this run: noise pulled the solvable state toward the mixed one, so our 120 understates
  the separation."
Numbers unchanged: 120.0 +- 40.1, 95% [41, 199], about 3 sigma. If Roy replies, this correction goes in the reply.
