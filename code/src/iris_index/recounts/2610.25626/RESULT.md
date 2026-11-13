# Recount result: arXiv 2610.25626v1 (MapSteal). Plan committed before computing.
## A. Table 2 CLEAN from results/table2_per_run.csv (means and sample SDs over three seeds; e.g. 2B MedMCQA 47.87 +- 1.03, QEDKS 2B CTI-Bench
   65.48 +- 0.16). "Highest mean accuracy on 12 of 18 settings": 12 of 18, CLEAN. Item-level recount: CANNOT_TELL (answer keys not released).
## B. Priced, seeds as units (Welch interval, 3 v 3; Pristine is a single run)
MapSteal minus the best other method per setting: ABOVE on 2 of 18 (4B MedMCQA +1.27 [+0.03, +2.50]; 9B SecEval +1.14 [+0.06, +2.22]),
CONSISTENT on 15, BELOW on 1 (2B CTI-Bench -3.08 [-5.75, -0.40], QEDKS ahead). "Highest mean on 12 of 18" resolves as 2 of 18.
The paper's own text is already measured ("relative benefits vary across benchmarks and Student scales"); the count of 12 is the line
that does not survive the seed width.
Catch: my first pass mis-keyed the method names and compared against Pristine only (24/24 "wins"); rerun before booking, logged.
