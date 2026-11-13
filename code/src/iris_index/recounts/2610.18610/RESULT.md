# Recount result: arXiv 2610.18610v1 (Jev-ToM, HKUST). Plan + addendum committed before reading.
## A. CLEAN: overall equal-weight accuracy rebuilds for all 12 models to the printed digit (Jev 73.21, GPT-3.5-1106 71.62, GPT-5.6-Luna 70.85, ...).
## B. Priced (questions resampled within benchmark, 5,000 draws)
B1 Jev - GPT-3.5 +1.59 [+0.25, +2.89] ABOVE; Jev - GPT-5.6-Luna +2.36 [+0.98, +3.75] ABOVE. "Ranks first overall" holds.
B2 "Excluding controls, Jev 69.1% and GPT-3.5 70.9%": the only control marks in the release are 600 BigToM rows; dropping them gives
   Jev 72.29 vs GPT-3.5 70.46 (difference +1.83 [+0.55, +3.14]), which does not rebuild 69.1 / 70.9. Their control set is not
   identifiable from the released files: the "reversal" is CANNOT_TELL, neither confirmed nor priced.

## Referee rebuild (25 Oct, our script reversal.py): controls from `category` by prefix (ToMi memory*/reality*/*_no_tom*, Hi-ToM order-0*, BigToM *control*, FANToM tom:belief:accessible:choice) = 920. Excluding controls Jev 69.08 vs GPT-3.5 70.87 (paper exact); by family_id -1.79 [-3.54, -0.19]; all items +1.59 [+0.22, +2.94]. Our earlier CANNOT_TELL is WITHDRAWN (keyword filter; first rerun with whole-string matching found 732, also wrong).
