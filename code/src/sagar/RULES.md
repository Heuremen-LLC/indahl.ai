# SAGAR cell rules by paper type (frozen 12 Nov 2026, before any paper is read)

Sage signed the name and set the first lane (sage_referee 2026-11-12T20-38-01, MOVES). This file fixes which code can fire on which
paper type, and the prediction for the control arm. No paper had been read when it was written. Index by DOI and arXiv id, never by name.

## Slice 1
Papers citing the GWOSC open-data papers (2021SoftX..1300658A, 2023ApJS..267...29A, 2015JPhCS.610a2021V), published from
September 2015 to now: 1,042 in total (data/core_gwosc.json, data/index_seed.json).
- Outside arm: 1,003 papers. These are the first lane.
- Control arm: 39 LVK collaboration papers (over 100 authors, or a LIGO, Virgo or KAGRA collaboration author).
Work order is newest first.

## Paper types (assigned from title and abstract before the codes are read)
- R, reanalysis: re-derives event or population numbers from public strain or released posteriors.
- M, methods: a new search, pipeline or ML classifier benchmarked on public strain.
- T, theory or other: cites the open data but headlines no number recomputed from it.

## Which code can fire
| Code | R reanalysis | M methods | T theory |
|---|---|---|---|
| F1 reference built from the same pipeline or the paper's own injections | yes | yes (benchmark against own injections only) | n/a |
| F2 a single favourable value headlined and the distribution hidden ("up to", best event, best run). A median with a 90% credible interval is the convention, not F2 | yes | yes (best of N runs or seeds) | n/a |
| F3 a detection, tension or new-signal claim with no significance or interval | yes (echoes, lensing, deviations from GR) | yes (a detection claim) | n/a |
| F4 posteriors, samples, code or trigger list not released | yes | yes | n/a |
| F5 a headline does not recompute from the released data | recompute only | recompute only | n/a |
| F6 abstract against the paper's own table or figure | yes | yes | yes |
| F7 a simpler model or the standard pipeline does as well | recompute only | yes (against the matched filter) | n/a |

## Outcome rules
- Every paper gets PRESENT, ABSENT, CANNOT_TELL or NOT_APPLICABLE per code, with the scope searched written down (the 2.1 fix).
- No paper is named as faulty on the site without a quote and, for F5 and F7, a recompute receipt.
- Base rates are reported per code per type. A code that fires on nearly all or nearly none of a type is reported as not sorting.

## Prediction, written first
- Control arm (LVK): near-zero faults on F1, F2, F3 and F6. F4 is likely ABSENT, since LVK releases posteriors and strain.
- Outside arm: most faults expected on F4 (no posteriors or code released) and F3 (new-signal claims). F5 and F7 need recompute
  hours per paper, so they are run only on papers that ship enough to recompute.

## Purpose
SAGAR is a credibility and public-good desk, not revenue. Astrophysics has no obvious payer. It is not judged against the quant desk.

## Notes from the first re-reads (12 Nov, after batches 1 to 3; rules above unchanged)
- Agent F6 precision on re-read: 3 of 11 confirmed, 3 CANNOT_TELL, 5 cleared. Every agent PRESENT is re-read by Bones before use.
- 2.1 candidate for the standard: a paper that contradicts itself in its own text (abstract against body, both prose) is not covered by
  F6 as written, which needs a table, figure or file on one side.

## Control-arm reading (12 Nov evening): the prediction FAILS on slips
Same drafting and the same Bones re-read in both arms. Papers with at least one confirmed F2, F3, F5 or F6:
- LVK control: 3 of 12 = 0.25 [0.09, 0.53] (2610.29436 F6, 2506.21021 F5, 2410.16565 F5 and F2).
- Outside, batches 1 to 7: 14 of 84 = 0.17 [0.10, 0.26]. CORRECTED 12 Nov night: 12 of 84 = 0.14 [0.08, 0.23]; 2409.16196 and 2503.09731 carry only convention-F2, which is out of the counts.
The intervals overlap, so whether the arms differ is CANNOT_TELL. The prediction of near-zero faults on the control arm fails for
errata-class slips: a table percentage, a probability, a table row. Reading: SAGAR's codes find errata at similar rates in the
collaboration's own papers and in outside papers, so SAGAR pages are a list of checkable corrections, not a ranking of care or quality.
F1 fires on 7 of 8 non-T control papers by the code's text (own background is standard practice), so F1 is reported as not sorting.

## Sage verdict 12 Nov 21:34 (MOVES) and what changed
Wording: "checkable errata found in both arms; no difference detectable at 12 and 84 papers". Never "similar rates", never a quality
comparison between the collaboration and outside papers.
- The re-read was NOT blind to arm: Bones knew which papers were LVK. The control 12 were the newest 12 of the 34 LVK papers with an
  arXiv id; 22 LVK papers remain undrafted.
- Rule history (drafting instructions; the frozen cell table above never changed):
  - batches 1 to 3: original prompt;
  - batch 4: F1 narrowed (standard published background is not F1), version_read added;
  - batches 5, 6 and control_01: F6 restricted to text against the paper's own table, caption or file, prose against prose made
    CANNOT_TELL, F5 arithmetic on printed numbers allowed;
  - batches 7 to 10: F2 and F3 wording tightened, convention flag added.
  Control_01 ran under the batch 5 and 6 rules.
- The rate is a floor: the re-read checks only agent PRESENT cells. Agent recall is unmeasured.
- Pages: F1 and convention-F2 come off per-paper pages and appear once, as base-rate rows in the methods note.
- Before any page is public: a second reader who is not Bones on every PRESENT (or the page says the check is self-witnessed), an author
  notice with a fixed window (14 days), and quote, page, recompute and receipt on each item.
- The prose-against-prose finding is post hoc (spotted after the codes were written) and stays out of the rates.

## Severity tiers (frozen 12 Nov ~21:45, defined AFTER the first 23 PRESENT rows were seen)
- T1 arithmetic or typo: a printed number that does not follow from the paper's own printed numbers, with no claim built on it.
- T2 contradiction: the text and the paper's own table, caption, appendix or file disagree.
- T3 headline-affecting: the slip sits in, or sets, a number the abstract or conclusion relies on.
A row takes its highest tier. F2 (non-convention) and F3 are tiered T3 when the claim is in the abstract, otherwise T2.
- 2610.29436 T3 is PROVISIONAL: the 3.2e8 limit set by the SGC-D row has not yet been checked against the abstract and conclusion.

## Wayfinder, 12 Nov night: NO author notice window
The 14-day window is dropped (Wayfinder overrules; same flow as QIA). Flow: the second reader confirms, the page goes up, and the email
goes out with the link the same day. What protects the work stays: verbatim quote and page, recompute receipt, neutral copy
("a correction you can check"), and the correction and removal form on every page.

## T3 wording changed 12 Nov night (after Example A, 2603.29019, was tiered T2; Sage 23:03)
T3 now reads: the slip sits in, or sets, a headline number (a number the abstract states, or a result the conclusion states as the
paper's main result). A slip in a secondary interval the conclusion repeats, where the headline does not depend on it, is T2.
Old text: "a number the abstract or conclusion relies on". The rule text changed; no tier was changed to fit it.
