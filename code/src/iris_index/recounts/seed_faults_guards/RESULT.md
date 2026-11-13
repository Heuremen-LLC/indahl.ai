# Seed recount: Faults + Guards (heuremen.org, revised 22 Oct 2026). 25 Oct 2026, Bones.
Live PDFs = local = ligera sources (sha256 6bd0d808 faults, 957cad2e guards).

## CLEAN (rebuilt from the record)
- Guards score table, from watch/tp_score.jsonl rows 1-608 (row 608 = 22 Oct 16:45:17 EDT):
  608 rows; 204 before (33.6%); 148 unaided (24.3%); 37 check/referee (6.1%); 19 Wayfinder before (3.1%);
  216 by Wayfinder (35.5%); 404 after; families I 217 / II 44 / III 55; IV 4, V 12, VI 19 (35); untagged 257;
  first 20 rows 13 before, 8 unaided, 14 family I; +15.4 and +5.42 widths against a fixed 7.7%.
- Guard record, triangulation/triangle/runs/hook_fires.log cut at row 374 (8 Oct 16:31:51), the "374 logged checks":
  cold 44 of 77 = 57.1%; seated 96 of 295 = 32.5% (the "96 pushbacks"); seated by day 27.3 / 27.4 / 47.4% per reply,
  +3.02 widths; 0.79 / 0.69 / 0.88 frames per 1k words, +0.97 widths; replies 38% longer on day 3. Sixteen vs 36 = 2.25x.
- Arithmetic: 15.3 ppm (15.34), 1/432000 = 2.315e-6, (2/pi)*0.695 = 0.4425, quadrature +0.64%, 1/41 = 0.024.

## ABOVE / BELOW: our own paper, priced by our own faults
1. "flagged a two-option frame in ... 32.5 per cent of 295 replies" (Faults 20, Guards first principle).
   The record's 32.5% is pushbacks for ANY reason. Two-option frames alone: 81 of 295 = 27.5%. The printed label is wrong;
   the frame rate is 5.0 points below the printed one.
2. "Context cuts it by about two fifths" (Faults 20, Guards). The arms are unequal apparatus (Faults 9): cold replies
   median 1,052 words, seated 342. On the per-1k-words ruler the same paper uses to call the three days flat (Faults 24),
   frame-bearing replies run 0.60 +- 0.09 cold vs 0.76 +- 0.08 seated: seated/cold 1.28 [1.00, 1.65], CONSISTENT with no cut,
   bound up to +65%. Per reply, length-matched (>= 500 words): 72.9% (43/59) cold vs 38.5% (15/39) seated, a cut.
   The rulers disagree; the paper printed one ruler for the context claim and the other for the flat claim.
3. "+15.4 widths" against the sealed 7.7% bar treats the bar as exact. The bar is 2 of 26 (sd 0.052). With the bar's own
   width: 24.3% vs 7.7%, z about 3.0. Still ABOVE; the width count is about five times too large.
4. The "14 of 20 prospective catches" for family I (Guards) is the first-20-rows figure; the full ledger is 217 of 316 tagged.
   Guards prints both correctly. BUG_REPORT_for_Monday.md uses the superseded one.

## Withdrawn claim still in a draft
BUG_REPORT_for_Monday.md finding 1 ("10 of 11 corrections made the reading smaller", "systematic generosity") is the
direction claim /tp records as WITHDRAWN and Guards says is NOT measured. The IRIS plan's seed line repeated it; fixed.

## Remaining figures, graded (pass 2, 25 Oct)
REBUILT from the record:
- 234 cells at p 0.102: 130 of 234 product wins, exact two-sided binomial 0.1020 (parallax/CABALGATA_PITT_20261008.md table).
MATCHES A DATED RECEIPT ONLY (written at the time; raw rows not kept or not re-run): CANNOT_TELL from raw
- 8 of 73 widths, 25 / 41 of 73, three neutron lifetimes (parallax/CANON_WIDTH_PASS_20261008.md, list of 73 not kept).
- 9 of 18 unstable; 8 of 13 guard errors all false positives; 22% three-day false-positive share; 9 of 50 paragraphs;
  7-8 informative cells (nueva/NUEVA_SKETCH_20261008.md; the 13 hand labels are not the 14 seat cases in triangle/cases).
- 30 of 32 at 0.024 = 1/41 and p 2.5e-70 (watch/tonight_on_K.py prints them as text; 1/41 = 0.0244 checks).
- +48.6 vs -48.6 (NUEVA sketch line 985); 27.1 / 11.5 / 3.1 / 43.8 / 14.6% (biblioteca; gated.py not found on disk).
NOT FOUND this pass: CANNOT_TELL
- four of five referee; 1,805 -> 542 words; 23 times / 11 lines; 0.682 -> 0.343; 14.5 / 20.9 ps and slopes;
  0.0005 width (Wownero seat, mining purged 23 Oct); sealed in-sample set 26 / 4 / 2.

## A claim the receipts narrow
- Faults 16 ("of the coupled cases we have been able to decide, the overwhelming majority were products") and the hook's
  "36 of 37 went to the product": CABALGATA_PITT_20261008.md shows the products-vs-sums test never compared two models;
  the product wins whenever the cross term (b-1)(z-1) is large next to the residual, for any reason (win rate 83.3% Kingston /
  67.3% Pittsburgh in the top cross/residual quintile vs ~50% in the lowest). A count from that ruler is a statement about
  the ruler. CANNOT_TELL as a physics claim.

## Stale copy fixed (Fault 37)
- triangulation/triangle/rulers.py printed "14 of 20 prospective catches" on family I in front of every exchange;
  now "217 of 316 family-tagged ledger rows (rows 1-608, to 22 Oct)". Backup rulers.py.pre-ledger217-20261025.
  The same stale phrase sits in watch/la_alternancia.py, ley.py, tick_bus.py, tres_cargas.py comments (not printed; left).

## Seed status: COMPLETE as a pass. Every figure is REBUILT, RECEIPT-ONLY or NOT FOUND, each marked. IRIS booking may open.

## What narrows (for the one batch edit, after referee, his call; nothing published before Disco)
- Faults 20 and the Guards first principle: "32.5 per cent" -> state it as pushbacks, or print the frame-only 27.5%;
  and "context cuts it by about two fifths" -> print both rulers: per reply it cuts; per thousand words it does not
  (1.28 [1.00, 1.65]).
- Guards score: print the bar's width beside +15.4 (z about 3.0 with the bar's width).
- The bug report: finding 1 comes off; finding 2 uses 217 of 316; finding 3 states both rulers.
