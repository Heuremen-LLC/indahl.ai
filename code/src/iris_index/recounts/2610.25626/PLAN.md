# Recount plan: arXiv 2610.25626v1 (MapSteal; Li, Zhang (UConn), Dong (Florida State)), committed before computing
Ack read: no funder statement in the PDF. Public universities: eligible free row.
Released: per-item letter predictions for every run, and results/table2_per_run.csv (accuracy per method x student x benchmark x seed).
Answer keys are NOT released (downloaded by script; some restricted): an item-level recount is CANNOT_TELL from the release.
## A. Recount Table 2 means and sample SDs from table2_per_run.csv; compare with the printed table.
## B. Pricing, seeds as the units (three per method)
B1 "Highest mean accuracy on 12 of 18 settings": for each setting, MapSteal minus the best other method, with a Welch interval on 3 v 3
   seeds (t, df from Welch-Satterthwaite, 95%). Count settings where MapSteal leads ABOVE, where it is CONSISTENT, where it trails BELOW.
   Pristine (one run) is compared as a fixed value with MapSteal's seed interval.
