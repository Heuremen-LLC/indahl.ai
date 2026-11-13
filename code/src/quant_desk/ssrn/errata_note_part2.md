## 3. Results

### 3.1 Papers with a confirmed finding, by arm

A paper counts when at least one of F2, F3, F5 or F6 is confirmed on it. All intervals below are 95% Wilson score intervals for a proportion.

| Arm | Papers read | Papers with a confirmed finding | Proportion | 95% interval |
|---|---|---|---|---|
| Outside, batches 1 to 7 | 84 | 14 | 0.17 | [0.10, 0.26] |
| LVK control | 12 | 3 | 0.25 | [0.09, 0.53] |

The three control papers with a confirmed finding are 2610.29436 (F6), 2506.21021 (F5) and 2410.16565 (F5). The F2 row on that paper is the convention form, which is excluded from the pages and from the counts.

Our written prediction, made before any paper was read, was near-zero findings on F1, F2, F3 and F6 in the control arm. F5 was not in the prediction, and the counted set is F2, F3, F5 and F6. F1 is reported as not sorting, as section 2.4 states, and is not counted. The prediction failed for slips of the errata kind, such as a table percentage, a probability or a table row. Two of the three control papers are F5 findings, a code the prediction did not name.

The rates in this table are a re-read by Bones, an AI agent, of agent drafts. They are not two-reader counts. The prose-against-prose finding is post hoc, found in this slice after the codes were written, and is not in the rates.

### 3.2 The two arms: no difference detectable at these counts

The intervals overlap. Whether the arms differ is CANNOT_TELL. The wording we adopt is: checkable errata found in both arms, and no difference detectable at 12 and 84 papers. We do not read the result as a statement about the care or quality of any group of authors. The pages are a list of checkable corrections.

### 3.3 Tiers by arm

The table covers the same papers as the rates in section 3.1. For the outside arm these are batches 1 to 7, with 14 papers carrying a finding. Twelve of the 14 have a tier in the tier file. Two, 2409.16196 and 2503.09731, are F2 rows with no tier assigned yet. For the control arm, all 3 papers have a tier, counted from the counted codes only. Paper 2410.16565 has a convention-form F2 row, which is excluded from the pages, and an F5 row, which is counted. Its tier is therefore that of its F5 row.

| Arm | T1 | T2 | T3 | Tiered papers |
|---|---|---|---|---|
| Outside, batches 1 to 7 | 1 | 4 | 7 | 12 of 14 |
| LVK control | 2 | 0 | 1 | 3 of 3 |

No tier comparison between the arms is supported at 3 control papers. The control T3 row, 2610.29436, is provisional. Its limit, set by one row of a table, has not yet been checked against the abstract and conclusion, so its tier may change. Four further outside papers in later batches carry a tier and are outside the rates. Example C below is one of them.

### 3.4 Agreement between the two readers

The second reader returned verdicts on 20 items, the findings on the published pages. The two readers agreed on 19 of them. The 20 audited items are all findings on the published pages. They were chosen as every PRESENT row re-read by Bones in batches 1 to 10 plus control, after excluding F1, F4 and convention-F2. They are not every PRESENT behind the rates in section 3.1. The one disagreement is item 3, paper 2507.21566, which also carries a separate F3 finding in the re-read. On item 3 the text gives "DYS = 3.75" and Table I gives 3.76 for the same quantity. The second reader read the difference as a rounding convention and returned HOLDS_CONSISTENT. Under the two-reader rule that item is dropped and is not a finding on a page. The drafting reader had labelled it a minor F6.

The Wilson 95% interval for 19 of 20 is 0.76 to 0.99. Because the pages hold only items both readers had already passed, 19 of 20 is agreement on those items. It is not a recall or precision of the method in general. Agreement here means that the second reader reached the same verdict class as the drafting reader on the item's question. The second reader does not see the drafting verdict, but both readers are models of the same family, which is limit 5 below.

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

The index pages, with the verbatim quote, location, arithmetic and receipt for each item, are published at https://indahl.ai/sagar. The index is live and was published on 12 November 2026.
