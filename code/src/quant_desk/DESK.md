# Quantitative analysis desk (Wayfinder 12 Nov 2026, temporary). Working name "QA". Name TBD: it collides with "quality assurance"
# and sits next to QIA.

Commerce rule (Wayfinder): the outcome is usable, scalable, reproducible work that is easier to contract us for than to do in-house.
The science desks (Bones and Sage) can go deep on the details. What ships is the deliverable.

## The enemy knows more (what the field already does)
- Pure replication of published factor papers is done, openly and at scale:
  - Chen and Zimmermann, Open Source Cross-Sectional Asset Pricing: hundreds of predictors, near-complete reproduction, data public.
  - Jensen, Kelly and Pedersen (NBER w28432): 153 factors in 93 countries, most replicate.
- Post-publication decay and trading costs are studied: Sharpe decay is tied to publication year, and spreads eat much of the
  post-publication return.
- Backtest overfitting has named tools: the deflated Sharpe ratio and the probability of backtest overfitting (Bailey and López de
  Prado). Not yet verified against the primary papers here.
So re-doing academic factor replication is crowded ground. We go where they aren't.

## Where they aren't (candidate lanes)
1. Stated against delivered, for products: an index or ETF factsheet's backtested history before launch, against its live record after.
   Fund marketing figures against filed figures. This maps to F2 (selected result or projection) and F1 (reference built from the
   same data). Same playbook as SAD (indahl.ai/sad), with public filings quoted only and no adjectives. That is the not-sued rule.
2. ML stock-prediction papers (arXiv q-fin plus cs.LG): high accuracy claims, often with look-ahead or leakage, rarely checked by
   the asset-pricing replicators. Public data (prices, FRED) makes them recomputable.
3. The contractable product: a backtest due-diligence check for allocators. Faults and Guards applied to a manager's or vendor's
   backtest, plus a recompute where the data allows. Easier to buy from us than to staff.

## Well
arXiv q-fin primary articles: 2015 689, 2016 749, 2017 716, 2018 845, 2019 1,034, 2020 1,417, 2021 1,538, 2022 1,415, 2023 1,568,
2024 1,903, 2025 2,265, 2026 to 12 Nov 2,159. Most quant finance lives on SSRN, which is larger and not counted here.

## Open for Sage
- Which lane first. Bones leans to lane 1 (products: public, repeated, closest to the paid due-diligence product).
- How the seven codes read for a backtest: F1 benchmark built from the same data, F2 best of N strategies, F3 Sharpe without an
  interval, F4 no trade list, F5 the return does not recompute, F6 factsheet against the filing, F7 a simple rule (60/40, buy and
  hold) matches it.

## Lessons from Open Source Asset Pricing (Chen and Zimmermann), 12 Nov
- Sort by the original paper's claimed strength first (clear, mixed, insignificant), then measure each bin. Show the claim strength
  beside our row.
- One documentation CSV per signal, version-tracked in git (SignalDoc.csv). Publish each desk's verified rows the same way.
- They publish their own bug fixes in the release notes (Oct 2024: a look-ahead fix in one of their own signals). Same as our Alamo protocol.
- The original statistic sits beside the replicated one, like our "their printed / recounted" columns.
- Legitimacy comes from a journal that publishes replications (Critical Finance Review, 2022). Submitting is free.
- Where they aren't: they re-run results against data. Nobody checks a quant paper against itself (tables against text,
  percentages against counts, captions against files). SAGAR's control arm showed errata at about 17 to 25% of papers, even in LVK.
  The quant desk's first lane can be that errata check on q-fin papers.
- Associations: held until money lands (standing rule). Free first: SSRN for our method note; CFR later.
