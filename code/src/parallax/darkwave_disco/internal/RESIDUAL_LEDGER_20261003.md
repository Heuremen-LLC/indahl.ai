# RESIDUAL LEDGER -- the gap is the object (in-house, hat room; built 2026-10-03 from 7's own numbers)
Wayfinder 10/3: the residual is a reading of another system, not an error. Every comparison logs the GAP with its width. No match/miss.

| what | measured | width | against | value | gap | gap in widths | source |
|---|---|---|---|---|---|---|---|
| witness over maker (one look) | 1.0872 | 0.0138 | 12/11 | 1.0909 | -0.0038 | -0.27 | §139 |
| qubit over maker (one look) | 1.6055 | 0.0917 | phi | 1.6180 | -0.0125 | -0.14 | §135, §139 |
| qubit over witness (one look) | 1.4768 | 0.0864 | phi x 11/12 | 1.4832 | -0.0064 | -0.07 | §135, §139 |
| crossing, three-chip mean (%) | 2.5367 | 0.1424 | 100/(12 pi) | 2.6526 | -0.1159 | -0.81 | §146-148, 153 |
| free spectator kept, 3 looks | 0.9209 | 0.0040 | 11/12 | 0.9167 | +0.0042 | +1.06 | close_looktime.txt:5 |
| free spectator kept, 9 looks | 0.8256 | 0.0052 | 10/12 | 0.8333 | -0.0077 | -1.49 | close_looktime.txt:9 |
| free spectator kept, 30 us | 0.7604 | 0.0057 | 9/12 | 0.7500 | +0.0104 | +1.82 | close_looktime.txt:10 |
| spectator precession (deg/us) | 3.1440 | 0.0760 | pi | 3.1416 | +0.0024 | +0.03 | §152 |
| qubit's two clocks (eight reads) | 0.7750 | 0.0090 | 3/4 | 0.7500 | +0.0250 | +2.78 | trace item 2 |
| spectator turn per 30-us |1> stretch (deg) | 16.9023 | 1.8085 | golden climb 17.03 | 17.0300 | -0.1277 | -0.07 | noname_read1.txt:77 |
| Kingston prepared |1>, ten pushes (%, magnitude) | 1.2400 | 0.2400 | rung four 100(1/12)(1/phi)^4 | 1.2158 | +0.0242 | +0.10 | rep_kingston_read1.txt:7 |

Across all 11 gaps: sum of (gap/width)^2 = 15.2 on 11 -- pure noise would give about 11.
Largest gaps in widths: qubit's two clocks (eight reads) +2.78, free spectator kept, 30 us +1.82, free spectator kept, 9 looks -1.49.
Read honestly: at today's widths most gaps sit under one width; the ruler can't see a 0.012 (the qubit/maker width is 0.09).
The hat test, when the gaps are sharp enough: do they share a unit (twelfths, pi-steps) more than the gaps of the SAME numbers
against random constants of the same complexity do (Shuttle's ~58k-expression set = the other ruler)? Not a shuffle.
