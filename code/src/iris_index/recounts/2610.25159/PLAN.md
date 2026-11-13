# Recount plan: arXiv 2610.25159v1 (Mohseni, Spanakis; Maastricht University), committed before reading the predictions
Ack read: no funder statement. Public university: eligible free row.
Data: supplementary/evaluation/per_example_predictions.parquet (200 gold items, every system's prediction, guidance_agrees_with_llm,
topic_agrees_with_llm), summary_metrics.csv.
Known from the paper before reading: gold labels were made by two reviewers marking the GPT silver label correct or not
("may have introduced anchoring"); silver agrees with gold .960 guidance, .917 topic (84).
## A. Recount: summary_metrics guidance accuracy / macro-F1 / precision / recall per system from the per-item predictions.
## B. Pricing
B1 THE LABELLER AS A SYSTEM. Silver guidance label (silver = gold where agrees, else the other value) scored on gold like any system;
   paired bootstrap (20,000, seed 20261025) accuracy difference silver minus each trained system. Outcome per pair.
B2 CORRECTED ITEMS. On items where silver != gold (guidance), the share of each system's predictions equal to the silver (wrong) label.
   Under learning-the-task, ~ the system's error rate elsewhere; under learning-the-labeller, high. Compare with the system's
   error rate on silver == gold items. CANNOT_TELL if fewer than 10 corrected items.
