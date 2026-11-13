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

Replication work re-runs a published result against data. This note describes a different check. It asks where a paper disagrees with itself. The places we look are text against the paper's own table, caption, appendix or released file, a printed number that does not follow from the paper's own printed numbers, a headline that is a single best value with the spread not beside it, and a claim with no significance or interval. The first measured slice is gravitational-wave papers that cite the open-data papers of the Gravitational Wave Open Science Center. The headline rates are agent drafts re-read by Bones, an AI agent (Claude Code). No human has read the findings yet. In that slice, 14 of 84 outside papers read so far carry at least one finding that survived the re-read, and 3 of 12 papers from the LVK collaboration, which we read as a control arm, carry one. The two arms show no difference detectable at these counts. A blind second reader, a model of the same family given neutral tasks without the drafting verdict, then checked the 20 items on the published pages, each one. It agreed on 19 and the one disagreement was dropped from the pages. The 20 are all findings on the published pages, chosen as every PRESENT row re-read by Bones in batches 1 to 10 plus control, after excluding F1, F4 and convention-F2. The 19 of 20 (Wilson 95% interval 0.76 to 0.99) is agreement on items both readers had already passed. It is not a recall or precision of the method in general. The rates come from the re-read by Bones alone. We freeze only the map of which code applies to which paper type before reading. The drafting instructions changed during the run, and we date the changes. The rates are a floor, and we state six limits. The quantitative-finance slice is running under the same pipeline, and its results will appear in a later version.

## 1. What is checked, and why replication misses it

### 1.1 Replication re-runs results against data

Two bodies of published work set the current standard for checking empirical finance. Chen and Zimmermann (Critical Finance Review, 2022) built Open Source Cross-Sectional Asset Pricing, a public set of code and data. Jensen, Kelly and Pedersen (NBER Working Paper w28432) studied factors across many countries. Both reproduce the large majority of published predictors. Each takes a paper's claim, rebuilds the result from public data, and compares the rebuilt number with the printed one.

These efforts answer the question of whether a result survives re-running. They are done openly and at scale. We do not repeat them.

### 1.2 The paper against itself

A paper can disagree with itself before any data is touched. A percentage in a table can fail to follow from the counts printed beside it. An interval in a caption can differ from the interval the paper's own released posterior gives. A row's components can fail to sum to the row's total. An abstract can headline the best of many runs with no spread beside it. None of these needs the original data to find. Replication checks whether the result rebuilds from data. It does not check whether the paper's own text, tables and captions agree with each other.

We call a place where a paper disagrees with itself an erratum candidate. The classification is for indexing. It is not an assessment of the study or its authors. A correction you can check is what we publish.

### 1.3 Scope of the claim

This note reports what a drafting agent, a re-read by Bones (an AI agent) and a second model reader found on a defined set of papers. It does not rank papers, authors or collaborations. It does not claim the papers' conclusions are wrong. In the worked example of section 3.4, the paper's headline bound recomputes from its released samples and only the caption interval does not.

## 1a. Related tools for checking papers

Several groups check published papers for internal errors. statcheck extracts reported test statistics from psychology papers and recomputes their p-values (Nuijten and colleagues). The GRIM test asks whether a reported mean is possible given integer data and the sample size (Brown and Heathers), and SPRITE extends that idea to reconstruct possible samples. The Black Spatula Project is an open-source effort that uses large language models to look for errors in published papers. As reported by Nature, the figures are about 500 papers, about 8 active developers and about 10 percent of flags wrong, and the project contacts authors privately rather than publishing. YesNoError applies a similar approach. As reported, it is crypto-funded and claimed 37,000 papers in two months. This note differs in three ways. Each listed finding requires agreement between two readers, the second a model. Arithmetic findings carry a recompute from the paper's own printed numbers or released data. And findings are published at a public index with a correction and removal form, starting in physics rather than psychology or medicine, with quantitative finance next.

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

The drafting reader is a language model agent that reads the paper text and proposes a cell for each code. Its F6 drafting precision on the first re-read was 3 of 11 confirmed, 3 CANNOT_TELL and 5 cleared. This figure is for F6 drafts specifically and not for the agent in general. Every agent PRESENT is re-read by Bones, an AI agent (Claude Code), before use. No human has read the findings yet.

The second reader is a blind model of the same family. It receives one item at a time. Each item is a neutral task, for example "Compare the D_YS value stated in the text for the massive graviton injection with the value in Table I", and it does not receive the drafting reader's verdict. It returns a verdict, verbatim quotes, its arithmetic, the innocent explanations it checked and a confidence. It was run on every finding on the published pages, which is 20 items. It was not run on every PRESENT that enters the rates in section 3.1. A finding is listed on a page only when both readers agree.

Each confirmed finding is placed in a severity tier. A row takes its highest tier.

- T1, arithmetic or typo: a printed number that does not follow from the paper's own printed numbers, with no claim built on it.
- T2, contradiction: the text and the paper's own table, caption, appendix or file disagree.
- T3, headline-affecting: the slip sits in, or sets, a number the abstract or conclusion relies on. F2 (non-convention) and F3 are tiered T3 when the claim is in the abstract and T2 otherwise.

For F5 and F7 a recompute receipt is required. A receipt states the data used, what the paper states, what was recomputed, the width of the recompute, the scope of what was and was not checked, and a script to reproduce it. No paper is named on a page without a verbatim quote and, for F5 and F7, a receipt.

The flow is as follows. A page is published and the authors are emailed the same day with the link to the page. A correction and removal form is on every page, and a page changes on request. Corrections were not offered to authors before publication. No human has read the findings yet. A real catch against our own work is fixed in public with credit.
