# AILUMINATE: what MLCommons publishes about its AILuminate Safety results, kept and checked. Plan, committed before the reports are parsed.

## The statements read (MLCommons, mlcommons.org/ailuminate/safety/results/ and the Detailed Results PDF of each system, published 29 October 2026)
1. The results page lists each system with a percentile score and a release month, and each system has a Detailed Results PDF reporting "an overall percentile score along with 12 sub-scores", "All scores are shown on a scale from 0 to 100".
2. "The composition of the reference set is fixed before a benchmark version is released, so new AI systems may be added to the results page without shifting the percentile scores of previously tested systems."
3. "The overall score weights all 12 categories equally."
4. "Released is the month in which the tested version first became publicly available, as downloadable weights or through a hosted service, whichever came first."
These are the benchmark's own statements. We make no claim about whether a system is safe, and we never rank systems.

## Data
The results page HTML and the public Google Drive folder it links for Detailed Results (listed through the folder's public embedded view, one PDF per system). The text of each PDF is read with pypdf. Nothing is run from the files. Raw copies of the page and the PDFs are kept with their SHA-256 hashes in data/raw.

## Tests (fixed now)
A. The page against its own reports. For every system, the overall percentile and the release month on the page are compared with the overall percentile and release month in the system's PDF, and the system type (open-weight model or guardrail) is compared. AGREE, DISAGREE, or NOTHING_RETURNED when a PDF cannot be read or parsed. Headline: the share DISAGREE among systems compared, with a Wilson 95 percent interval. Zero disagreement is the expectation. ABOVE if the lower end is above 0.05. CONSISTENT if the upper end is below 0.15. Otherwise CANNOT_TELL.
B. Published scores kept. Statement 2. Every score (overall and the 12 categories) and release month of every system is stored at each read with its time. A system is CHANGED when any of its values differs from the first value we stored, KEPT when none does. A system added after our first read has its own first value and is compared from there. Headline: the share CHANGED among systems that have been read at least twice, Wilson 95 percent. ABOVE if the lower end is above 0.05, CONSISTENT if the upper end is below 0.15 (with 27 systems this needs a read in which none changed, since 0 of 27 has an upper end of 0.125), otherwise CANNOT_TELL. The first read has nothing to compare with and returns NOTHING_RETURNED.
C. Equal weighting, descriptive only, no outcome. Statement 3 cannot be tested from percentiles alone, because the percentile of an average is not the average of percentiles. For every system the table prints the overall percentile, the mean of its 12 category percentiles and their difference, and the lowest and highest category percentile. The page says what this can and cannot show.
D. Release month, descriptive only, no outcome, for open-weight models that have a Hugging Face repository found by name and checked by hand: the month the repository was created beside the stated month. A repository can be created private before release and the stated month can come from a hosted service, so neither order is a contradiction. Rows with no repository are listed as none found.

## Known-good, run before the real read
The PDF parser is run on a planted text built from the layout of the Cogito report (overall plus 12 rows, an ordinal suffix of each kind: st, nd, rd, th) and must return the planted numbers; a text with 11 category rows must return NOTHING_RETURNED. The ordinal parser must read 1st, 2nd, 3rd, 11th, 12th, 13th, 21st, 100th. The first report (Cogito) is read by hand against the parser output.

## Hand check
Every DISAGREE row of test A is opened by hand. Ten systems chosen by seed 7 are checked by hand against their PDF for all 13 numbers.

## Not claimed
Anything about the safety of a system or the quality of the benchmark. That a change in a published score is an error: MLCommons can correct or add scores, and the page says the run is ongoing. That the release months are wrong.

## Note 1 (29 Oct, after the first read and the hand check)
First read at 29 Oct, all 27 systems on the page and all 27 reports parsed. Test A: 0 of 27 disagree (the overall percentile, release month and system type on the page equal those in each report), upper end 0.125, CONSISTENT. Test B: first read, NOTHING_RETURNED until a second read. Hand check: the 13 numbers of every report (overall and the 12 categories, in order) were read a second way, by position in the report text and with a check that the category labels appear in the planned order, and agree with the parser for all 27. The ten chosen by seed 7 are among them. Test D (release month against Hugging Face) is not built yet and needs a hand-checked name for each repository, so it waits for its own addendum.

## Addendum 1 (29 Oct, before any read of the page it concerns)
Test E, added: Candela's stated prices and terms, kept. MLCommons launched Candela, its paid testing service for the AILuminate benchmarks, on 29 October, with a getting-started page at mlcommons.org/candela/candela-getting-started/. Each read of that page stores the price table (benchmark, tier, member price, non-member price, as printed) and these statements, each as the exact sentence: "Official tests are run with an exclusive holdback set of prompts."; "The full test run takes about an hour, depending on your system's speed."; "These may not be publicly referenced." (annotated results); "These are the only ones that can be cited publicly." (official results); the sentence that begins "Automated signup and billing". A value is CHANGED when it differs from its first stored value and KEPT otherwise, listed with both values and the dates of the two reads. This is a record with no outcome and no STACK row. It prints what a service stated, not whether the statements are true, and we do not run any Candela test. The known-good is the table parser, which must return 18 price cells (9 rows of two) from a planted table of the page's markup and nothing from a page with no table.


## Addendum on cadence (29 Oct)
The repeat cadence is now every 24 ticks of the tick bus, about 2.3 hours, so that a change at the source shows within hours. The earlier cadence was a default chosen when the corner was built. Nothing else changes; each pass keeps the same read, the same politeness pauses and the same known-good checks.
