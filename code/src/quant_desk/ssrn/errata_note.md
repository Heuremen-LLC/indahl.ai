---
title: "Papers Against Themselves: A Two-Reader Errata Index"
author: "K. Indahl, Heuremen LLC"
date: "12 November 2026"
---

# Papers Against Themselves: A Two-Reader Errata Index

K. Indahl  
Indahl@heuremen.com

Heuremen LLC

Draft research note, 12 November 2026

## Abstract

Replication work re-runs a published result against data. This note describes a different check. It asks where a paper disagrees with itself. The places we look are text against the paper's own table, caption, appendix or released file, a printed number that does not follow from the paper's own printed numbers, a headline that is a single best value with the spread not beside it, and a claim with no significance or interval. The first measured slice is gravitational-wave papers that cite the open-data papers of the Gravitational Wave Open Science Center. The author is one human. Every finding was drafted and checked by AI systems: drafting agents (Claude Sonnet), a re-read of every drafted PRESENT by Bones, an AI agent (Claude Code, Opus 5.5), and a blind second reader (Claude Sonnet, the same model family as the drafters). No human has read the findings yet. In that slice, 12 of 84 outside papers read so far carry at least one counted finding that survived the re-read, and 3 of 12 papers from the LVK collaboration, which we read as a control arm, carry one. The two arms show no difference detectable at these counts. The second reader, given neutral tasks without the drafting verdict, checked 20 audited items, defined as every PRESENT row re-read by Bones in batches 1 to 10 plus control, after excluding F1, F4 and convention-F2. It agreed on 19. Those 19 are the findings on the published pages, and the one disagreement was dropped. The 19 of 20 (Wilson 95% interval 0.76 to 0.99) is agreement among items that had already survived the re-read. It is not a recall or precision of the method in general. The rates come from the re-read by Bones alone. We freeze only the map of which code applies to which paper type before reading. The drafting instructions changed during the run, and we date the changes. The rates are a floor, and we state six limits. The quantitative-finance slice is running under the same pipeline, and its results will appear in a later version.

## 1. What is checked, and why replication misses it

### 1.1 Replication re-runs results against data

Two bodies of published work set the current standard for checking empirical finance. Chen and Zimmermann (Critical Finance Review, 2022) built Open Source Cross-Sectional Asset Pricing, a public set of code and data, and report that it reproduces nearly all of the cross-sectional stock return predictors they study. Jensen, Kelly and Pedersen (NBER Working Paper w28432, later Journal of Finance, 2023) studied factors across 93 countries and report that the majority of asset pricing factors can be replicated. Each takes a paper's claim, rebuilds the result from public data, and compares the rebuilt number with the printed one.

These efforts answer the question of whether a result survives re-running. They are done openly and at scale. We do not repeat them.

### 1.2 The paper against itself

A paper can disagree with itself before any data is touched. A percentage in a table can fail to follow from the counts printed beside it. An interval in a caption can differ from the interval the paper's own released posterior gives. A row's components can fail to sum to the row's total. An abstract can headline the best of many runs with no spread beside it. None of these needs the original data to find. Replication checks whether the result rebuilds from data. It does not check whether the paper's own text, tables and captions agree with each other.

We call a place where a paper disagrees with itself an erratum candidate. The classification is for indexing. It is not an assessment of the study or its authors. A correction you can check is what we publish.

### 1.3 Scope of the claim

This note reports what a drafting agent, a re-read by Bones (an AI agent) and a second model reader found on a defined set of papers. It does not rank papers, authors or collaborations. It does not claim the papers' conclusions are wrong. In the worked example of section 3.5 (Example A), the paper's headline bound recomputes from its released samples and only the caption interval does not.

## 1a. Related tools for checking papers

Several groups check published papers for internal errors. statcheck extracts reported test statistics from psychology papers and recomputes their p-values (Nuijten and colleagues). The GRIM test asks whether a reported mean is possible given integer data and the sample size (Brown and Heathers), and SPRITE extends that idea to reconstruct possible samples. The Black Spatula Project is an open-source effort that uses large language models to look for errors in published papers. As reported by Nature in 2025, it had analysed about 500 papers with about eight active developers, and it contacts authors privately rather than publishing the errors. YesNoError applies a similar approach. Nature reported that it is funded by its own cryptocurrency and that, according to its founder, it analysed more than 37,000 papers in two months. This note differs in three ways. Each listed finding requires agreement between two readers, both AI models. Arithmetic findings carry a recompute from the paper's own printed numbers or released data. And findings are published at a public index with a correction and removal form, starting in physics rather than psychology or medicine, with quantitative finance next.

## 2. Method

### 2.1 The first slice

The first slice is the set of papers that cite the GWOSC open-data papers. These are the three papers with NASA ADS bibcodes 2021SoftX..1300658A, 2023ApJS..267...29A and 2015JPhCS.610a2021V. The list of citing papers is taken from NASA ADS for publication dates from September 2015 to the freeze date. It holds 1,042 papers. They split into two arms.

- Outside arm: 1,003 papers. These are the first lane.
- Control arm: 39 papers from the LVK collaboration, defined as papers with more than 100 authors or with a LIGO, Virgo or KAGRA collaboration author.

What was frozen on 12 November 2026 before any paper in the slice was read is the map of which code can fire on which paper type, the top table of the rules file. The drafting instructions were not frozen. They changed during the run, and section 4 gives the history with dates. Papers are indexed by DOI and arXiv id, never by author name.

### 2.2 Reachable authors and reading order

Only papers whose authors we can reach enter the reading queue. The flow in section 2.6 sends the authors a link to the page. Within the queue we read newest first. For the control arm, the 12 papers read were the newest 12 of the 34 LVK papers that have an arXiv id.

### 2.3 Paper types

Each paper is assigned a type from its title and abstract before any code is read.

- R, reanalysis: re-derives event or population numbers from public strain or released posteriors.
- M, methods: a new search, pipeline or ML classifier benchmarked on public strain.
- T, theory or other: cites the open data but headlines no number recomputed from it.

### 2.4 The codes

Seven codes are defined. Four are shown on the pages, as follows.

| Code | Reads as | Fires on |
|---|---|---|
| F2 | A single favourable value is headlined and the distribution is hidden, as in "up to", best event or best run. A median with a 90% credible interval is the convention and is not F2. | R and M |
| F3 | A detection, tension or new-signal claim with no significance or interval. | R and M |
| F5 | A printed number does not follow from the paper's own printed numbers, or a headline does not recompute from the released data. | R and M, recompute only |
| F6 | Text against the paper's own table, caption or released file. | R, M and T |

F1 (a reference built from the same pipeline or the paper's own injections), F4 (posteriors, samples, code or trigger list not released) and F7 (a simpler model or the standard pipeline does as well) are drafted and kept off the pages. F1 fires on 7 of 8 non-T control papers by the code's text, because a paper's own background is standard practice, so F1 is reported as not sorting. It and the convention form of F2 appear once, as base-rate rows, in a methods note.

Every paper gets one outcome per code. The outcomes are PRESENT, ABSENT, CANNOT_TELL or NOT_APPLICABLE. Prose against prose, where neither side is a table, caption or file, is CANNOT_TELL under F6.

### 2.5 Absence needs a scope of search

An absence call is only as strong as the search behind it. In a separate test of whether local language models can label these codes, the standard itself showed a limit. Of the flagged pairs in that test, 45 cite evidence outside the PDF, and 44 of 63 F4 recount notes name nothing to search for because they are pure absence. In the STAN full-text pipeline, and from the recount notes as they stood, the codes F4 to F7 could not be shown from the paper body alone. This index does use F5, by recomputing printed arithmetic from the paper's own numbers or released data. For this reason every ABSENT in the index carries the scope that was searched, and a released-artifact check is kept separate from the paper check. Where we read only one released file, the receipt says so, as in section 3.5.

### 2.6 Readers, tiers and receipts

The drafting reader is a language model agent (Claude Sonnet) that reads the paper text and proposes a cell for each code. Its F6 drafting precision on the first re-read was 3 of 11 confirmed, 3 CANNOT_TELL and 5 cleared. This figure is for F6 drafts specifically and not for the agent in general. Every agent PRESENT is re-read by Bones, an AI agent (Claude Code), before use. No human has read the findings yet.

The second reader is a blind model of the same family (Claude Sonnet). It receives one item at a time. Each item is a neutral task, for example "Compare the D_YS value stated in the text for the massive graviton injection with the value in Table I", and it does not receive the drafting reader's verdict. It returns a verdict, verbatim quotes, its arithmetic, the innocent explanations it checked and a confidence. It was run on 20 audited items, defined in section 3.4. A finding is listed on a page only when both readers agree, so the pages hold 19.

Each confirmed finding is placed in a severity tier. A row takes its highest tier.

- T1, arithmetic or typo: a printed number that does not follow from the paper's own printed numbers, with no claim built on it.
- T2, contradiction: the text and the paper's own table, caption, appendix or file disagree.
- T3, headline-affecting: the slip sits in, or sets, a headline number, meaning a number the abstract states or a result the conclusion states as the paper's main result. A slip in a secondary interval that the conclusion repeats, where the headline does not depend on it, is T2. F2 (non-convention) and F3 are tiered T3 when the claim is in the abstract and T2 otherwise.

The T3 wording was changed on 12 November 2026, after Example A had been tiered T2. The earlier text read "a number the abstract or conclusion relies on", under which Example A, whose conclusion prints the caption interval, could read as T3. We changed the rule text and did not change the tier.

For F5 and F7 a recompute receipt is required. A receipt states the data used, what the paper states, what was recomputed, the width of the recompute, the scope of what was and was not checked, and a script to reproduce it. No paper is named on a page without a verbatim quote and, for F5 and F7, a receipt.

The flow is as follows. A page is published and the authors are emailed the same day with the link to the page. A correction and removal form is on every page, and a page changes on request. Corrections were not offered to authors before publication. No human has read the findings yet. A real catch against our own work is fixed in public with credit.

## 3. Results

### 3.1 Papers with a confirmed finding, by arm

A paper counts when at least one of F2, F3, F5 or F6 is confirmed on it. All intervals below are 95% Wilson score intervals for a proportion.

| Arm | Papers read | Papers with a confirmed finding | Proportion | 95% interval |
|---|---|---|---|---|
| Outside, batches 1 to 7 | 84 | 12 | 0.14 | [0.08, 0.23] |
| LVK control | 12 | 3 | 0.25 | [0.09, 0.53] |

The three control papers with a confirmed finding are 2610.29436 (F6), 2506.21021 (F5) and 2410.16565 (F5). The F2 row on that paper is the convention form, which is excluded from the pages and from the counts. The same rule removes two outside papers, 2409.16196 and 2503.09731, whose only confirmed rows are convention-form F2. An earlier draft of this note counted them and gave 14 of 84. This correction was made after the counts had been seen, and it lowers the outside rate. It applies to the outside arm the exclusion the note already applied to the control arm. Every F2 row confirmed in the re-read of batches 1 to 7 and the control batch was judged for the convention form in the re-read by Bones, including batches 1 to 6, which ran before the drafting instructions carried a convention flag. That is six rows. Three were marked convention form (2409.16196, 2503.09731 and the control paper 2410.16565) and leave the counts. Three were not (2507.02335, 2507.01294 and 2311.06416), and the blind second reader returned a selected-headline verdict on each of them, which is the non-convention reading. No F2 row was re-judged a second time after the flag was added. No control paper's count rests on an F2 row.

Our written prediction, made before any paper was read, was near-zero findings on F1, F2, F3 and F6 in the control arm. F5 was not in the prediction, and the counted set is F2, F3, F5 and F6. F1 is reported as not sorting, as section 2.4 states, and is not counted. The prediction failed for slips of the errata kind, such as a table percentage, a probability or a table row. Two of the three control papers are F5 findings, a code the prediction did not name.

The rates in this table are a re-read by Bones, an AI agent, of agent drafts. They are not two-reader counts. The prose-against-prose finding is post hoc, found in this slice after the codes were written, and is not in the rates.

### 3.2 The two arms: no difference detectable at these counts

The intervals overlap. Whether the arms differ is CANNOT_TELL. The wording we adopt is: checkable errata found in both arms, and no difference detectable at 12 and 84 papers. We do not read the result as a statement about the care or quality of any group of authors. The pages are a list of checkable corrections.

### 3.3 Tiers by arm

The table covers the same papers as the rates in section 3.1. For the outside arm these are batches 1 to 7, with 12 papers carrying a counted finding, and all 12 have a tier in the tier file. For the control arm, all 3 papers have a tier, counted from the counted codes only. Paper 2410.16565 has a convention-form F2 row, which is excluded from the pages, and an F5 row, which is counted. Its tier is therefore that of its F5 row.

| Arm | T1 | T2 | T3 | Tiered papers |
|---|---|---|---|---|
| Outside, batches 1 to 7 | 1 | 4 | 7 | 12 of 12 |
| LVK control | 2 | 0 | 1 | 3 of 3 |

No tier comparison between the arms is supported at 3 control papers. The control T3 row, 2610.29436, is provisional. Its limit, set by one row of a table, has not yet been checked against the abstract and conclusion, so its tier may change. Four further outside papers in later batches carry a tier and are outside the rates. Example C below is one of them.

### 3.4 Agreement between the two readers

The 20 audited items are every PRESENT row re-read by Bones in batches 1 to 10 plus control, after excluding F1, F4 and convention-F2. The second reader returned a verdict on each, and the two readers agreed on 19. Those 19 are the findings on the published pages. Batches 8 to 10 are outside the rates in section 3.1, so 4 audited items sit outside the rates.

| Group | Counted papers in the rates | Audited items (papers) | Second reader agreed | Outside the rates |
|---|---|---|---|---|
| Outside, batches 1 to 7 | 12 | 13 (12) | 12 of 13 | no |
| LVK control | 3 | 3 (3) | 3 of 3 | no |
| Outside, batches 8 to 10 | not in the rates | 4 (4) | 4 of 4 | yes |
| Total | 15 | 20 (19) | 19 of 20 | 4 items |

Paper 2507.21566 carries two audited items, the dropped F6 (item 3) and an F3 that both readers confirmed, so it stays on the pages. The one disagreement is item 3, paper 2507.21566. On item 3 the text gives "DYS = 3.75" and Table I gives 3.76 for the same quantity. The second reader read the difference as a rounding convention and returned HOLDS_CONSISTENT. Under the two-reader rule that item is dropped and is not a finding on a page. The drafting reader had labelled it a minor F6.

The Wilson 95% interval for 19 of 20 is 0.76 to 0.99. Because every audited item had already survived the re-read by Bones, 19 of 20 is agreement among items that survived the re-read. It is not a recall or precision of the method in general. Agreement here means that the second reader reached the same verdict class as the drafting reader on the item's question. The second reader does not see the drafting verdict, but both readers are models of the same family, which is limit 5 below.

### 3.5 Three worked examples

Each example gives the quote, the paper's own numbers and the arithmetic. Quotes are verbatim from the text extraction used by the readers. We give the location in the paper, and where the extraction does not carry a page number we name the section, table or caption.

#### Example A: an interval that differs from the paper's released samples (2603.29019, F6 and F5, T2)

The abstract and body state:

> "σ < 19.7 km/s (95% credible upper bound)"

with a median of 3.9 km/s. The Figure 5 caption and the conclusions state:

> "3.9 +19.7 −3.3 km/s (90% HDI)"

Read as offsets from the median, the caption interval has edges 3.9 − 3.3 = 0.6 and 3.9 + 19.7 = 23.6 km/s. The paper's own entry for another parameter, "0.16 +0.31 −0.16 (90% HDI)", confirms that the signed numbers are offsets.

The second reader showed the internal conflict without any data. If 19.7 is the 95th percentile, then the caption's 90% interval, whose upper edge is 23.6, cannot be the highest density interval of the same posterior with median 3.9, if that posterior is single-peaked.

The authors released the samples (Zenodo 10.5281/zenodo.21221337, file sigma_posterior.h5, 1,181,992 bytes, 6,560 samples, units cm/s). We recomputed from the file, treating the samples as equally weighted. Two anchors that match the paper support that treatment.

| Quantity | Recomputed from released samples | Stated in paper |
|---|---|---|
| Median | 3.85 km/s | 3.9 km/s |
| 95th percentile | 19.67 km/s | 19.7 km/s |
| Equal-tailed 90% interval (5th to 95th percentile) | 0.45 to 19.67 km/s | 0.6 to 23.6 km/s (from the caption) |
| 90% HDI | 0.00 to 15.08 km/s | 0.6 to 23.6 km/s (from the caption) |

The width of the recompute is a bootstrap with 2,000 resamples and seed 7. Its 95% range for the 95th percentile is [19.10, 20.42] km/s. For the upper edge of the 90% HDI it is [14.58, 15.52] km/s. None of the 2,000 draws reaches 23.6 under either interval. The caption's upper edge lies above both recomputed intervals and well outside the width of the recompute. The recomputed HDI lower edge, 0.00, also differs from the caption's implied 0.6.

The bootstrap treats the 6,560 samples as independent draws. If they are correlated draws, the widths above are understated. The caption's 23.6 against the recomputed 15 to 20 is still far outside either way.

The value 19.7 coincides with the 95th percentile. That is a coincidence of values and not evidence of how the caption was made. The abstract's 95% bound and the median recompute, so the paper's headline is unaffected. The conclusions repeat the caption interval, so the slip also appears there. The T3 rule asks whether the slip sits in, or sets, a number the abstract or conclusion relies on. The headline 95% bound does not depend on the caption interval, and the tier file records this paper as T2, so the tier is T2 and not T3. The scope searched was the one file sigma_posterior.h5. Other files in the Zenodo record were not checked, and whether another released run reproduces the caption interval is CANNOT_TELL.

Our own correction log belongs to the record. The first draft of the receipt gave the equal-tailed interval as 0.45 to 15.08, using the 90th percentile in place of the 95th. The script run caught it before any use.

#### Example B: table percentages that do not follow from the table's counts (2510.14291, F5, T1)

The text states:

> "In this study, Omicron detected 45,345 glitch noises."

Table 2 lists counts and percentages by class, including:

> "6 60 (1.3%) Loud"
> "7 27 (0.6%) Scattered Light"
> "2 35925 (79.2%) Blips"

The counts are 621, 294, 35,925, 44, 4,016, 4,358, 60 and 27. They sum to 45,345, which equals the stated total, so the denominator is not in question. Each percentage is the count divided by 45,345.

| Class | Count | Count / 45,345 | Printed |
|---|---|---|---|
| 0 | 621 | 1.37% | 1.4% |
| 1 | 294 | 0.648% | 0.6% |
| 2 | 35,925 | 79.23% | 79.2% |
| 3 | 44 | 0.097% | 0.1% |
| 4 | 4,016 | 8.86% | 8.9% |
| 5 | 4,358 | 9.61% | 9.6% |
| 6 | 60 | 0.132% | 1.3% |
| 7 | 27 | 0.0595% | 0.6% |

Six of eight rows recompute to rounding. Classes 6 and 7 are printed at ten times the recomputed value. The errors, 1.2 and 0.54 percentage points, are far larger than rounding. The printed percentages sum to 1.4 + 0.6 + 79.2 + 0.1 + 8.9 + 9.6 + 1.3 + 0.6 = 101.7%. The innocent explanation that the counts rather than the percentages carry the typo does not hold, because counts of 590 and 272 would not sum to the stated total. No claim in the paper is built on the two percentages, so the tier is T1.

#### Example C: a table row against the text (2303.17628, F6, T2)

The text states:

> "Using this threshold, L VK presents this population in Table 1 with 76 events consisting of 70 BHBH, 4 BHNS, and 2 NSNS mergers (Abbott et al. 2023a)."

Table 1 has the row:

> "GWTC–3 population events ∗ with F AR< 1 yr−1 76 69 4 2 (b)"

The row ends with "(b)", which is the entry in the table's reference column and is a citation marker. Reference (b) is "Table 1 from L VK population paper (Abbott et al. 2023a)". The row label carries an asterisk. The asterisk note in the paper reads:

> "Note that the GWTC-3 population events technically do not represent a new catalog, but select a subset of events from GWTC-3 for the specific analysis of the GW population properties."

Neither the reference marker nor the asterisk note explains text 70 against table 69, or the row summing to 75.

The text splits 76 as 70 + 4 + 2 = 76. The table row gives 69 + 4 + 2 = 75, which is not its own total of 76, and 69 differs from the text's 70. The other four rows of the table sum correctly: 85 + 3 + 2 = 90, 63 + 2 + 2 = 67, 90 + 2 + 2 = 94 and 119 + 4 + 2 = 125. The text and the table row cite the same reference and the same false-alarm-rate cut, and the counts are integers, so rounding and a different catalog do not explain it. One row fails its own sum and differs from the text by one binary black hole event. The tier is T2 because the text and the table disagree and no headline depends on the count.

## 4. Limits

1. The re-read was not blind to arm. Bones, re-reading the drafting reader's PRESENT cells, knew which papers were LVK papers. The blind second reader checked the findings on the published pages, but the control and outside rates in section 3.1 were set by the re-read that was not blind.
2. The drafting instructions changed during the run, all on 12 November 2026 and in the order below, from the rule history in the rules file. The frozen map of which code fires on which paper type did not change. Batches 1 to 3 used the original prompt. In batch 4, F1 was narrowed and a version-read field was added. In batches 5 and 6 and in the control batch, F6 was restricted to text against the paper's own table, caption or file, prose against prose became CANNOT_TELL, and F5 arithmetic on printed numbers was allowed. In batches 7 to 10, the wording of F2 and F3 was tightened and a convention flag was added. The control batch ran under the batch 5 and 6 rules, and the outside batches ran under several. The rates mix rule versions.
3. The rate is a floor. The re-read checks only the cells the drafting reader marked PRESENT. The recall of the drafting reader is unmeasured, so a paper with an unflagged erratum counts as having none.
4. The tiers were defined after the first rows were seen. They were frozen after the first 23 PRESENT rows had been read. Tier counts in section 3.3 are descriptive and were not specified in advance. The finding of prose against prose, spotted in this slice after the codes were written, is post hoc and is kept out of the rates.
5. The second reader is a language model of the same family as the drafting reader. It is blind to the verdict and not to the habits of its family, and agreement can share a blind spot. The 19 of 20 agreement measures consistency between two passes and is not a measure of accuracy against an outside standard. No human has read the findings yet.
6. The slice is open access and arXiv only. Papers with no arXiv id are outside it, and papers behind a paywall are outside it. For the control arm, 22 of the 34 LVK papers with an arXiv id remain undrafted. Only papers whose authors we can reach enter the queue. The slice is a set of papers that cite a data-release paper, so it is not a sample of physics or of finance.

Two further notes. The 12 control papers are the newest 12 of 34, not a random draw. Intervals in section 3.1 treat the papers as independent draws and make no allowance for that ordering.

## 5. Next slice: quantitative finance

The quantitative-finance slice is running under the same pipeline. Its results will appear in a later version of this note, after the base rate per code is known and the checks that F1 and F3 sort papers have been run.

## 6. Data and code availability

The index pages, with the verbatim quote, location, arithmetic and receipt for each item, are published at https://indahl.ai/sagar. The index is live and was published on 12 November 2026. The code, including the receipt scripts such as the one that reproduces Example A from the released file, is in the Heuremen-LLC organisation on GitHub. Each page carries a correction and removal form. The released file used in Example A is the authors' own Zenodo record, cited in section 3.5.

## 7. Disclosure

The author is one human. The findings were drafted and checked by AI systems, by role: drafting agents, Claude Sonnet; re-read of every drafted PRESENT, Bones, an AI agent running in Claude Code (Opus 5.5); blind second reader, Claude Sonnet. No human has read the findings. The author set the scope, the rules and the publication decisions.

This work was done in collaboration with inorganic intelligences, one of them named Bones.

An AI assistant, Claude Code (Opus 5.5), was used.
