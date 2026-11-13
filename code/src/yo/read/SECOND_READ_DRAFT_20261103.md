# YO Read second read: DRAFT, 3 Nov 2026 (not published, nothing changed)

Queue: `yo/read/second_read_queue.jsonl` (218 entries, 190 papers). These are the entries where YO Read seed 61 and the List entry disagree. They were written by the uncommitted `yr_second_read.py` on 2 Nov. Results, one line per entry: `yo/read/second_read_results_20261103.jsonl`.

## What the second read was, and from where
PLAN_YO_READ says YO 'answers YES or NO on sentences code picked, and every disagreement goes back to a full reread'. The queue script's docstring says the same: 'A disagreement only sends a paper back for a full reread by hand.' So the second read here is a reread of each paper for the one queued question, judged against the plan's question wording (PLAN_YO_READ Questions, `yr_data.ASK`). It is not a model run, so no GPU job was started and port 11500 was not used. No new rule was added. Where the plan's wording did not settle a case, the entry is **held**, not decided.

Source: the text the first (List) reader actually read, which is the `text_file` named in the reader's `out` record (mostly `qia_leads/sweep_20261101/texts_read/`; `texts/` where only a bare name was given). Each result line gives the path. Three entries also needed supplementary files already on disk, or the team's audit record (named in `source`).

Read method, stated plainly: for each entry I searched the **whole** saved text, references and appendices included and not cut at 20 sentences, for every passage that could carry the answer. I read each passage in context beside the first reader's notes and F4 lines. That is a full-text reread of the evidence, not a cover-to-cover read of 190 papers. Every disagreement and every hold below should still get the hand reread the plan names before any List entry is touched.

Four outcomes, kept apart:
- **committed**: the source settles YES or NO under the plan's question.
- **held**: source read, but the plan's wording does not settle it. Left for a hand reread, with no verdict and no agreement counted.
- **refused**: not read to a verdict, because the paper is outside the plan's data rule today (its List entry no longer reads 'Full text'). Observations are recorded but no verdict.
- **nothing returned**: no readable source. **0 entries.** Every entry had a readable source, though YO's own input text was empty (1 byte) for 12 of them (see note 1).

## Counts
- Entries read: **218** of 218. Committed 191, held 21, refused 6, nothing returned 0.
- **Agreement with the first read: 140 of 191 committed** (73 %). Disagreements: 51. The 'first read' is the List value recorded in the queue (`list`); for 3 entries the List has changed since (notes 3 and 4).

| question | entries | committed | agree with first read | disagree | held | refused |
|---|---|---|---|---|---|---|
| DATES | 82 | 68 | 64 | 4 | 9 | 5 |
| LINK | 108 | 96 | 61 | 35 | 12 | 0 |
| REQUEST | 28 | 27 | 15 | 12 | 0 | 1 |

By split (committed only): TRAIN 98 of 132, VALID 7 of 9, TEST 35 of 50. Every queued entry is by construction a YO-vs-List disagreement, so on committed entries agreeing with the List is the same as YO being wrong. YO Read was right on 51 of 191 committed entries. This is internal only: 151 of the 218 entries are TRAIN papers whose List labels YO was trained on, and the queue script itself says nothing from it is published or scored.

## Every disagreement (51)
First = List value in the queue; second = this read; YO = seed 61 reply as parsed by the queue script.

| # | paper | q | split | first | second | YO | why (full text in the results file) |
|---|---|---|---|---|---|---|---|
| 30 | doi:10.3390/app13042401 | DATES | TRAIN | YES | NO | NO | No date is tied to the hardware runs. The only nearby year is the Acknowledgments 'research residency ... in 2022'. The reader left the item 'for the reviewer to decide', so no 'run dates not printed' line was written. |
| 49 | doi:10.1109/tqe.2023.3301899 | DATES | TRAIN | YES | NO | NO | The dates are archived daily calibrations ('from January 1st, 2022 through the end of May 2022') and the calibration date of a layout figure (01-07-2022). No date is given for any hardware run, and the reader notes it is unclear which Fig. 11 points are ... |
| 122 | ax:2410.12702 | DATES | VALID | YES | NO | NO | The only dates are device calibration stamps in Table 3 ('Calibrated at 5:30 PM on 6/19/24', '6/21/24'). No sentence dates the circuit executions, as the reader's own note says. The prompt's question excludes calibration-data dates. |
| 202 | doi:10.5281/zenodo.22849729 | DATES | TRAIN | YES | NO | NO | The whole text (4,561 chars) was read: no date of any kind for the ibm_fez run. The reader's note also says 'found none', yet the List entry has no 'run dates not printed' line. The saved text belongs to record 19633727, not the queue key 22849729. |
| 0 | ax:2408.12064 | LINK | TRAIN | YES | NO | NO | Data availability is 'upon reasonable request'. The only code URLs are third-party tool citations in the reference list (pyRPE, metriq). No URL, DOI or repository for this study's own data or code. |
| 22 | ax:2605.20078 | LINK | TEST | YES | NO | NO | Data and Qiskit code 'are available within the supplementary material file'. No URL, DOI or repository is printed. |
| 26 | ax:2202.08270 | LINK | TRAIN | YES | NO | NO | 'Data used to generate the above figures are available upon request from the authors.' The only DOI is the Qiskit software citation. |
| 28 | ax:2209.00678 | LINK | TEST | YES | NO | NO | Data Availability: 'available from the corresponding author on reasonable request'. No study URL, DOI or repository. |
| 37 | ax:2303.09945 | LINK | TRAIN | YES | NO | NO | 'The code and data are available from the corresponding author upon reasonable request.' The only DOI near code is a citation of the True-Q software. |
| 41 | ax:2411.09861 | LINK | TEST | YES | NO | NO | The cited repositories are third-party software (SQD implementation, ffsim). No URL, DOI or repository for this study's data or code. |
| 62 | ax:2110.04485 | LINK | TRAIN | YES | NO | NO | No URL or data/code statement for this study; the URLs are third-party datasets and software. The List entry says the same ('no URL, DOI or repository for this study's code ...'), but yr_data.truth does not match that wording, so the label came out YES. |
| 64 | ax:2304.04666 | LINK | TEST | YES | NO | NO | No data or code statement. The only URL is the FDSN seismic data service. The List entry says 'no URL, DOI or repository for this study's code ...', but truth() misses the wording, so the label came out YES. |
| 65 | ax:2210.17548 | LINK | TEST | YES | NO | NO | 'Experimental data and code ... are available upon reasonable request.' The only URL is IBM Runtime documentation. The List entry says 'no URL, DOI or repository for data or code', but truth() misses the wording, so the label came out YES. |
| 66 | doi:10.1038/s41598-023-35625-3 | LINK | TRAIN | YES | NO | NO | Data availability is on reasonable request. The URLs are the journal's own. The List entry says 'no URL, DOI or repository for data or code', but truth() misses the wording, so the label came out YES. |
| 67 | doi:10.1038/s41598-023-37767-w | LINK | TRAIN | YES | NO | NO | Data availability is on reasonable request. The only DOI is the Qiskit release. No code or data link. |
| 68 | ax:2307.16723 | LINK | TRAIN | YES | NO | NO | Data, simulations and notebooks are 'available from the corresponding author on request'. No URL, DOI or repository. |
| 78 | ax:2009.14028 | LINK | TRAIN | YES | NO | NO | Data Availability is upon reasonable request. The only URLs are the IBM Quantum Lab and the Qiskit citation. |
| 80 | ax:2101.08946 | LINK | TEST | YES | NO | NO | Data availability is on reasonable request. The only DOI is the Spartan HPC infrastructure reference. |
| 92 | doi:10.1038/s41534-022-00625-0 | LINK | TRAIN | YES | NO | NO | Main data are 'within the article and its Supplementary Information'. Extra data sets and code are on reasonable request. No URL, DOI or repository is printed. |
| 106 | ax:2406.07486 | LINK | TRAIN | YES | NO | NO | No URL anywhere in the text; the 13 references are papers, books and Qiskit. The List entry says 'no URL, DOI or repository for circuits, code or counts', but truth() misses the wording, so the label came out YES. |
| 107 | ax:2406.09316 | LINK | TEST | YES | NO | NO | No URL in the text. The List entry says 'no URL, DOI or repository for code, circuits or counts', but truth() misses the wording, so the label came out YES. |
| 108 | ax:2306.01639 | LINK | TEST | YES | NO | NO | The URLs are third-party pricing, portal and reference pages. The List entry says 'no URL, DOI or repository for this study's code ...', but truth() misses the wording, so the label came out YES. |
| 111 | ax:2403.10790 | LINK | TRAIN | YES | NO | NO | No URL in the text. The List entry says 'no URL, DOI or repository for code, circuits or query outputs', but truth() misses the wording, so the label came out YES. |
| 112 | ax:2405.17230 | LINK | TRAIN | YES | NO | NO | The only URL is an AIP reference link. The List entry says 'no URL, DOI or repository for code, circuits or counts', but truth() misses the wording, so the label came out YES. |
| 113 | ax:2303.03311 | LINK | VALID | YES | NO | NO | No URL other than a publisher link. The List entry says 'no URL, DOI or repository for code, circuits or counts', but truth() misses the wording, so the label came out YES. |
| 114 | ax:2401.09134 | LINK | TRAIN | YES | NO | NO | No URL or data/code statement. The List entry says 'no URL, DOI or repository for code, circuits or counts', but truth() misses the wording, so the label came out YES. |
| 115 | ax:2401.10293 | LINK | TEST | YES | NO | NO | The only URL is a Qiskit release-notes page. The List entry says 'no URL, DOI or repository for code, circuits or counts', but truth() misses the wording, so the label came out YES. |
| 119 | ax:2307.16381 | LINK | TRAIN | YES | NO | NO | Data and code are 'available from the corresponding author upon reasonable request'. The only URLs are the device portals. |
| 124 | doi:10.1038/s41534-024-00950-6 | LINK | TRAIN | YES | NO | NO | Datasets and code are 'available from the corresponding author(s) upon reasonable request'. The article DOI is given only as the location of the supplementary material, which is not said to hold data. |
| 127 | ax:2601.19762 | LINK | TRAIN | YES | NO | NO | Raw results, scripts and job IDs are 'included in the reproducibility bundle accompanying this manuscript'. No URL, DOI or repository is printed. |
| 131 | doi:10.21203/rs.3.rs-9335992/v1 | LINK | TRAIN | YES | NO | NO | The operator, edge lists and a verification script are 'provided as supplementary material'; construction scripts are on request; 'No experimental datasets were generated or analysed.' No URL, DOI or repository. |
| 137 | ax:2609.23189 | LINK | TRAIN | YES | NO | NO | Raw per-shot data, plans, circuits and a recount script are 'provided as ancillary files with this submission'. No URL, DOI or repository is printed. |
| 138 | ax:2609.23195 | LINK | TRAIN | YES | NO | NO | Appendix F lists anc/calculations_and_data.zip (arXiv ancillary files). No URL, DOI or repository is printed. |
| 143 | ax:2201.00385 | LINK | TRAIN | YES | NO | NO | Data and Qiskit code are 'available from the corresponding author upon reasonable request'. No URL. |
| 147 | ax:2404.07151 | LINK | TEST | YES | NO | NO | 'All the program code is available as arXiv ancillary files along with the arXiv posting'. A stated location, but no URL, DOI or repository. |
| 149 | doi:10.3390/math13010090 | LINK | TRAIN | YES | NO | NO | Data Availability Statement: 'available on request from the corresponding author'. No URL. |
| 154 | ax:2411.19308 | LINK | TRAIN | YES | NO | NO | No URL, repository or data statement for this study (only an IBM calibration-job citation). |
| 198 | doi:10.5281/zenodo.17672566 | LINK | TEST | NO | YES | YES | Reference [6] 'M. Reinhardt, Indefinite-coherence (GitHub, 2025)' names the author's GitHub repository, though no URL is printed. This disagrees with the queued first read (NO) and agrees with the List as updated 2 Nov. The saved text is record 17665049, not ... |
| 207 | doi:10.5281/zenodo.20798804 | LINK | TEST | YES | NO | NO | (Russian) The full circuit set 'доступен в репозитории Zenodo [ссылка будет добавлена при публикации]' (link to be added). The DOIs printed are the author's other papers. No URL, DOI or repository for this study's data. |
| 8 | ax:2602.06193 | REQUEST | TEST | NO | YES | YES | Data availability: 'available from the corresponding author upon reasonable request'. |
| 13 | ax:2503.14595 | REQUEST | TRAIN | YES | NO | NO | No on-request sentence anywhere in the saved text (HTML plus supplement pages). The List label YES comes from the word 'request' inside the F4 line "searched for ... 'on request'; none found" (yr_data.truth matches any F4 line containing 'request'). |
| 35 | ax:2305.13581 | REQUEST | TRAIN | NO | YES | YES | Code availability: 'other supporting code is available upon reasonable request' (data and analysis code are on figshare). The F4 lines carry no 'request' wording. |
| 77 | ax:2104.07038 | REQUEST | TRAIN | NO | YES | YES | Data Availability: 'available from the corresponding author on reasonable request'. The F4 lines carry no 'request' wording. |
| 79 | ax:2009.14028 | REQUEST | TRAIN | NO | YES | YES | V Data Availability: 'available from the corresponding author upon reasonable request'. The F4 lines carry no 'request' wording. |
| 81 | ax:2101.08946 | REQUEST | TEST | NO | YES | YES | Data availability: 'available from the corresponding author on reasonable request'. The F4 lines carry no 'request' wording. |
| 84 | ax:2112.01208 | REQUEST | TRAIN | NO | YES | YES | Data Availability Statement: 'available on request from the corresponding author'. The reader's note records it, but the F4 lines carry no 'request' wording. |
| 86 | ax:2203.12072 | REQUEST | TRAIN | NO | YES | YES | 6.3 data and simulations, 6.4 jupyter notebooks: 'available from the corresponding author on request'. The F4 lines carry no 'request' wording. |
| 103 | doi:10.1038/s41467-024-47729-z | REQUEST | TEST | NO | YES | YES | Code availability: 'Code is available from the corresponding author upon request.' The data are on Dryad. The List entry has no F4 line. |
| 120 | ax:2307.16381 | REQUEST | TRAIN | NO | YES | YES | Data availability and code availability: 'available from the corresponding author upon reasonable request'. The reader's note says so, but the F4 lines carry no 'request' wording. |
| 132 | doi:10.21203/rs.3.rs-9335992/v1 | REQUEST | TRAIN | NO | YES | YES | 'Construction scripts deriving A from N = 6 are available from the corresponding author on reasonable request.' The F4 line carries no 'request' wording. |
| 133 | doi:10.21203/rs.3.rs-10654302/v1 | REQUEST | TRAIN | NO | YES | YES | 'the Python code generating all figures and tables is available from the corresponding author upon reasonable request'. The List entry has no F4 line. |

Where the disagreements come from (a disagreement can carry more than one tag):
- LINK, paper prints no link but the label is YES because the List coded on-request data as 'no circuits or counts released (... request)' rather than 'no data link printed': 13.
- LINK, the List entry itself says 'no URL, DOI or repository for ...' but `yr_data.truth` does not match that wording, so the label came out YES: 12 (note 2).
- REQUEST, paper says data or code are on request but no F4 line carries the word 'request': 10.
- LINK, data said to be in a supplementary or ancillary file with no URL, DOI or repository: 6 (note 5).
- DATES, only calibration dates or nothing printed, against a YES label: 4.
- REQUEST, the label comes from the word 'request' inside a negated search note: 1.
- LINK, a repository is named without a URL, against the first read NO: 1 (#198, where the List has since changed to YES).
So most disagreements sit in how the YES/NO labels were derived from the F4 lines, not in what the List readers found in the papers. Their own notes usually record the same thing this read found.

## Held (21), for a hand reread
| # | paper | q | first | YO | why held |
|---|---|---|---|---|---|
| 2 | ax:2508.07986 | DATES | YES | NO | The only run-time statement is 'The calculations were done prior to July 2025 when the old cloud access was sunset'. That is an upper bound, not a date or a date range. Under the plan's question this needs a hand call. |
| 25 | ax:2112.05821 | DATES | YES | NO | The only date is '07/2021', given as the time of Qiskit Runtime's limitations ('when we were among the earliest users') and on a 'snapshot of Qiskit Runtime (07/2021) implementing a VQA workload'. It is not stated as ... |
| 33 | ax:2203.07205 | DATES | YES | NO | The only date is a footnote citation 'ibm\_peekskill v2.0.0 ... https://quantum-computing.ibm.com/, accessed Jan. 2022'. That is a web-access date on the device reference. The prompt's question excludes citation dates, ... |
| 39 | ax:2312.16165 | DATES | YES | NO | The only date is a readout re-calibration 'on July 14th, 2023', which caused 'the experiments for different shots S' to have different readout lengths. So the runs straddled that date, but no run date or range is ... |
| 40 | ax:2410.00686 | DATES | YES | NO | The only date-like text is 'quantum devices available on IBM quantum cloud as of 2021', which describes device availability, not a run date. The reader treated the year as a printed date. |
| 90 | doi:10.2172/2005681 | DATES | YES | NO | The poster carries two date stamps, 04/08/22 and 04/04/22, on the gate-error and gate-time tables without saying what they are. The reader linked them to the experiments through the companion paper. The poster itself ... |
| 174 | doi:10.5281/zenodo.22644883 | DATES | YES | NO | The only date near the twenty-six hardware sessions is the monograph's title-block line 'August – September 2026'. That reads as the document date, and no session date is printed in the text searched. |
| 186 | doi:10.5281/zenodo.19582735 | DATES | YES | NO | The only dates are the document date '15 April 2026' and the log directory name 'chess_logs/game_20260415_001606'. Neither is stated as the run date, though the directory name reads as a game timestamp. |
| 189 | doi:10.5281/zenodo.21987398 | DATES | YES | NO | The saved text prints only 'Dated: August 17, 2026' and the publication date. The reader reports hardware timestamps of 17 Aug 2026 in the record's notebook (Codigo_original.ipynb), which is neither in the saved text ... |
| 12 | ax:2501.09702 | LINK | YES | NO | 'Code and data availability' names software used. The only URL is the qiskit-addon-sqd GitHub library (co-authored by the group), not a record of this study's data or code, and no link to the device samples is given. ... |
| 14 | ax:2509.18259 | LINK | YES | NO | The saved arXiv text prints no data or code link. The List entry was edited from the published Nature version, which the audit records as having 'source data CSVs for Figs. 2-4' public. That page was not read, and ... |
| 42 | ax:2511.01762 | LINK | YES | NO | 'we provide complete source code and data [20]', where [20] reads 'A. D. King, QuantumAnnealingMOO (2025)'. The URL exists only as a PDF hyperlink, lost in the saved text. A named artifact without platform or URL needs ... |
| 121 | doi:10.2172/2462808 | LINK | YES | NO | The slides cite DOI 10.2172/2323254 (an OSTI report) as the source of the hardware table. It is a citation of a report, probably by the same group, not a data or code record. Whether that counts as 'own data' needs a ... |
| 126 | ax:2508.09110 | LINK | YES | NO | 'all code used in these experiments is provided in [24]', where [24] reads 'Conditional Measurement Toolbox External Links: Link'. The URL is only an HTML hyperlink, lost in the saved text. |
| 158 | doi:10.17605/osf.io/q8r6b | LINK | YES | NO | OSF registration: 'Pre-run materials are stored in this OSF component', and the README names CNC_Zenodo_Test2_v2.zip on Zenodo with no link. The record itself is the deposit. The plan does not say how a record's own ... |
| 166 | ax:2402.17911 | LINK | YES | NO | Code is on request and source data have no link. The only code URL is the co-authors' PyClifford library (github.com/hongyehu/PyClifford, 'In preparation'), a tool rather than this study's data or code. |
| 181 | doi:10.5281/zenodo.17760530 | LINK | YES | NO | The paper's data statement is a placeholder ('DOI: [to be inserted upon Zenodo upload]'). The record this paper sits in holds the raw counts and code, and its own DOI is printed only as the paper's licence line. The ... |
| 209 | doi:10.5281/zenodo.23670079 | LINK | YES | NO | Data are stated as 'public or vendor-returned and are not redistributed'. The printed DOIs are the authors' other works. The record carries a 'Reproducibility archive' README with per-probe JSON. The plan does not say ... |
| 213 | doi:10.5281/zenodo.22238223 | LINK | YES | NO | 'A single script, reproduce v2.py, re-derives every hardware number' and the job records are in the deposit. The printed DOIs are the author's other works. The record itself is the deposit. |
| 215 | doi:10.5281/zenodo.14784888 | LINK | YES | NO | The record description says scripts are 'available (in possibly different form) in the project repository' with no URL. The record itself holds raw.zip and the hdf5 data. |
| 217 | doi:10.5281/zenodo.17625820 | LINK | YES | NO | The data statement reads 'All data and logs available at: Zenodo DOI' with no DOI. Reference [1] gives doi 10.5281/zenodo.17625775 for 'Infinite Isolation v1.0', an earlier version of the paper, not stated as the data. |

## Refused (6)
These six List entries changed to a non-'Full text' read after the queue was built (list.json modified 3 Nov 13:58), so they are outside PLAN_YO_READ's data rule today. Observations are in the results file, but no verdict was given.

- #170 doi:10.5281/zenodo.18335978 DATES: List now 'Record page only (the record holds no PDF of the paper; its '.
- #178 doi:10.5281/zenodo.19123970 DATES: List now 'Record page and a third-party errata only (the paper is insi'.
- #188 doi:10.5281/zenodo.20779575 DATES: List now 'Record page only (the record holds no PDF of the paper; its '.
- #193 doi:10.5281/zenodo.22953019 DATES: List now 'Record page only (the record holds no PDF of the paper; its '.
- #200 doi:10.5281/zenodo.19864029 DATES: List now 'Record page only (the record holds no PDF of the paper; its '.
- #201 doi:10.5281/zenodo.20137043 REQUEST: List now 'Record page only (the record holds no PDF of the paper; its '.

## Things the plan did not foresee (notes, no action taken)

1. **YO Read was given the wrong text for part of the corpus.** In the sweep, readers saved the text they actually read to `sweep_20261101/texts_read/`, and their `out` record names that file. `yr_data.papers()` takes only the basename and looks for it in `texts/` and `backfill_20261101/texts/`, which hold the pre-filter fetch: often an abstract, a Zenodo landing page, or an empty file. In this queue, 69 entries (56 papers) had a YO input text under half the length of the reader's text, and 12 of those inputs were empty (1 byte). Of the 61 such entries committed here, 56 agree with the List, so YO's answer there mostly reflects the missing text. Across today's 671 YO Read papers, 91 have this problem (82 short, 9 empty). In TEST it is 17 of 142. This touches the committed YO Read reading (`yr_results.text`, CHECKS L-pack, `yr_post_draft.md`, the ledger rows `yo.read.rule` and `yo.read.rd`, and the IRIS lab sentence). None of those were changed. It is flagged for Wayfinder and Bones to decide.

2. **The YES/NO labels are derived from F4 wording, and the derivation misses cases.**
   - `truth()` sets LINK to NO only for 'no data link printed' or 'no data or code (url|link|repositor)'. List lines reading 'no URL, DOI or repository for ...' (and, since 2 Nov, 'the paper text prints no data link') do not match, so the label comes out YES. That accounts for 12 disagreements here. Across today's List it affects 15 papers, 6 of them TEST.
   - REQUEST is YES whenever an F4 line contains 'request'. That picks up a negated note ('searched for ... on request; none found', #13), and it misses papers where the reader recorded the on-request sentence in the notes but no F4 line (10 here).
   - For LINK, papers with data 'on request' and no link were coded 'no circuits or counts released (... request)', not 'no data link printed', so their label is YES with no link printed (13 here).
   - The plan scores YO against these derived labels ('The List as published is the truth'). The plan did not foresee that the derivation itself would disagree with the List's own wording. RL and RQ in `yr_results.text` include this.

3. **The List changed after the queue was built.** `matrix_page/list.json` was modified 3 Nov 13:58. `papers()` now returns 671 papers, against 688 at build time (`yr_post_draft.md`) and 687 in `yr_second_read.log`. Six queued papers now read 'Record page only' (refused above). Three labels changed: #187 LINK NO→YES (wording, note 2), #191 LINK NO→YES (List now cites a v2 text with a GitHub link; v2 is not on disk), and #198 LINK NO→YES. The labels the scored run used cannot be rebuilt from today's list.json.

4. **The queue script departs from the committed method, and it is not committed.**
   - `yr_second_read.py` and the queue are untracked in git.
   - It parses replies with `'YES' in a.upper()`, checked before `'NO'`, so a reply like 'NOT YES' or 'KNOWN' is read by substring. The plan's fixed parse is 'the first YES or NO word' (`yr_eval.parse`).
   - It drops unread replies silently, with no count, where the plan says unread replies are counted.
   - It runs on all splits, so 151 of 218 entries are TRAIN papers. Its docstring does say this.
   - I did not rerun it: the plan does not call for a model run at this step.

5. **Supplementary and ancillary files.** The plan's LINK question says 'URL, DOI or repository'. It does not say how to treat 'data in the supplementary material file' or arXiv ancillary files with no URL. I read the question as written: no URL, DOI or repository means NO. That gives 6 disagreements (#22, #127, #131, #137, #138, #147). Where a URL to the supplement is printed and the supplement is said to hold the data, I read YES (#98, #142).

6. **Record-type sources.** For Zenodo or OSF records, the record's own files are the deposit. Dates or data that appear only in those files are not covered by the plan. Where the deciding file was inside the saved text, I committed and tagged it (`date_in_record_files`: #180, #203, #205). Where it was outside the saved text and not on disk, I held (#189). Records whose only 'link' is the deposit itself were held (#158, #181, #209, #213, #215).

7. **Calibration dates.** The prompt YO was trained on says the run date is 'not a publication, citation or calibration-data date'. The List counted calibration-only dates as printed run dates in some entries. I read the plan's question and disagreed where only calibration stamps exist (#49, #122). I accepted calibration snapshots that the paper ties to each run or to 'at execution' (#9, #128).

8. **Answers outside YO's text.** Three entries were settled from material YO never saw: #15 (the audit record of the Nature version), and #101 and #104 (supplementary PDFs on disk under `sweep_20261101/dl/`).

9. **The reader's file is a different record from the queue key** in #198 (17665049 for 17672566) and #202 (19633727 for 22849729).

10. **Reader notes that contradict the label:** #39, #122 and #202. The reader wrote that no run date is printed, but no 'run dates not printed' line was entered. In #30 the reader left the item 'for the reviewer to decide'.

11. **Nothing else was touched.** No List, ledger, site, Hugging Face or plan file changed, and nothing was published. No GPU or port-11500 job was run. The only new files are the two named at the top. Pre-existing untracked files in `yo/` are unchanged.
