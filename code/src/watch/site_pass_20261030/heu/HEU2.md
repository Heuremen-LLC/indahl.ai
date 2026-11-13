# HEU2: the three PDFs on heuremen.org and the Zenodo record. 30 Oct 2026, read only.

Lane brief: ~/bones-forge/watch/site_pass_20261030/heu/BRIEF_HEU.md. Checks run: core.md (I, II, III, V, VI, R), pack_P (all), pack_Q (paper only).
Scratch: ~/bones-forge/watch/site_pass_20261030/scratch_HEU2/ (extracted text, scripts, Zenodo JSON, arXiv abstracts).
Nothing was edited, committed, deployed or sent. No keys or tokens were met.

## 1. COVERAGE

Pages in lane: 3 PDFs (paper 17 pp, Faults 14 pp, Guards 11 pp, 42 pages) and the Zenodo concept record 10.5281/zenodo.23169755.

File identity (the "same file or say which differs" check):
- Live https://heuremen.org/a-readout-is-not-an-idle.pdf, faults.pdf, guards.pdf (all HTTP 200, GitHub Pages, last-modified 29 Oct 01:44 GMT) are byte-identical to the canonical files named in ~/bones-forge/ledger/copies.json (heuremen.org/*.pdf) and to ~/bones-forge/public_mirror/heuremen.org/*.pdf.
  sha256 paper 9f8919920ae8665f2db83fe7152dd5b03b8ee15ca4395bbbfc21c5b870d59555, Faults 7c9107e9d59187790681c3842bc66de4ffbdb156c1af9d3c6f3380e2a9bf934c, Guards 9a723119d30f03c3fbb34a0e5935c8fef604074bd3063e85c5281645005d7e94.
- Faults and Guards also equal the listed copies ligera/FAULTS.pdf and ligera/GUARDS.pdf. All three PDFs were rendered 25 Oct 14:05 EDT (PDF CreationDate 18:05 UTC) from ligera/FAULTS.html, ligera/GUARDS.html and arxiv_one_readout/main.tex (main.tex mtime 25 Oct 09:26).
- Paper PDF inside the Zenodo v5 code zip (paper/A_Readout_Is_Not_an_Idle.pdf) and ~/Desktop/A_Readout_Is_Not_an_Idle_zenodo_v5/paper/ are the same sha256 as the live PDF. main.tex in the zip is the same sha256 as arxiv_one_readout/main.tex (8c90136e...).
- Differs, text identical: arxiv_one_readout/main.pdf (sha 9765dece..., same size, CreationDate 13:26 UTC vs 18:05 UTC, all 17 pages of extracted text equal). copies.json lists no copy for the paper (copies: []) although three byte-identical copies exist.
- Differs, older: ~/Desktop/A_Readout_Is_Not_an_Idle.pdf (22 Oct, 16 pages, sha 764bd571...) is not the live paper. Not served. Worth deleting so it is not sent by mistake.
- ~/Desktop/arxiv_submission_20261025.tar.gz: main.tex is the repo main.tex up to the bibliography, with the .bbl inlined after. Same text.
- Zenodo (public API, read at 15:15 UTC): concept 23169755 resolves to latest v5.0.0, record 23662284, DOI 10.5281/zenodo.23662284, published 2026-10-26. Five versions: 1.0.0 (23169756, 21 Oct), 2.0.0 (23568984, 22 Oct), 3.0.0 (23575204, 22 Oct), 4.0.0 (23600831, 23 Oct), 5.0.0. Latest has two files: A_Readout_Is_Not_an_Idle_code_and_results_v5.zip (10,175,739 B, md5 76105217f9be28a85277aa200abc1e3e) and A_Readout_Is_Not_an_Idle_raw_v5.zip (2,952,263,113 B, md5 3b27d8ff52cf622c3c84e111ae307304). I downloaded the code zip (md5 matches the API). Both md5 equal the files in ~/Desktop/ZENODO_v5_UPLOAD/. Raw zip listed locally, not re-downloaded (110 entries, 101 under experiments/, 9 under extra/).
- Code zip against the site tree ~/bones-forge/heuremen.org/experiments/: every data file is identical. 41 files differ, all index.html (pages edited since the zip was built on 26 Oct). 154 files exist only in the tree (TERMS.txt footers, the raw .npz that live in the raw zip, two __pycache__ files that are not served, 404 on the live site).

Checked by script:
- All 3 PDFs: full text extracted (qvenv pypdf), semicolon, name, email, AI-wording, typo and internal-name scans.
- Paper against the ledger: 404 paper-surface entries (318 live rows) in ledger.jsonl all found in the PDF text (two entries are split by a page break in the PDF text, both present). check_ledger.py (read-only, -B): drift 0, paper 1162 of 1167 decimals in a row. No withdrawn row (33) is printed in any of the three PDFs. 958 decimals in the PDF text: 891 inside a row, 67 outside (29 arXiv or DOI ids, 4 literature numbers, 9 Fig. 2 labels, the rest page-break splits of covered rows or abstract ranges that restate body rows). Each of the 38 non-id ones was checked by hand.
- 400 of 404 snippets: every printed number found in the row's source file, with rounding or x100 allowed. The 11 tokens that failed were traced by hand (all held, see HOLDS).
- Guards score table recomputed from watch/tp_score.jsonl rows 1 to 608. Faults and Guards day figures recomputed from triangulation/triangle/runs/hook_fires.log (first 374 rows).
- All 76 unique URLs in the paper's link annotations fetched: 60 return 200 (all heuremen.org experiment pages and all arXiv pages), 16 publisher DOIs return 403 to a script (APS and AIP bot block, none 404). Faults and Guards carry no links.

Read by eye: all 42 pages of extracted text, the four figure captions, Tables I to III cell by cell.

Not checked, with reason:
- Figure images (fig1 to fig4 rasters and vector shapes): only the text layer and captions were read.
- Journal volume, page and year of the 37 references: titles and arXiv ids of the 29 references that carry an arXiv id were compared with arxiv.org (one title mismatch, HEU2-6); journal fields were not parsed (publisher DOIs return 403).
- Raw .npz data and the raw Zenodo zip contents: listed, not opened.
- Faults and Guards figures that have no record in the tree (listed in HEU2-15) cannot be checked, and the documents say so in their footer ("No instance is reported with the run that produced it").
- Other pages of heuremen.org, indahl.ai: other lanes.

## 2. FINDINGS

### Paper (a-readout-is-not-an-idle.pdf)

- id: HEU2-1 | check: P4, P6, VI | severity: wrong-claim
  - where: paper p.10, Table III, row "Extra elapsed time", Outcome cell
  - page says: "extra time at most 4, 1 and 12% (fez, kingston, marrakesh; bound defined after the data; excludes it on kingston only)"
  - source says: the clause "excludes it on kingston only" is Check D, which asks whether a longer readout can account for the coherence loss, not the phase kick: ~/bones-forge/heuremen.org/experiments/2026-10-21-control-run/results_check_d.text (kingston N=2 and N=4 EXCLUDED, N=8 and fez and marrakesh NOT EXCLUDED) and CHECK_D_EXTRA_TIME.md.text line 1. The paper's own Sec. III D adds the second check that excludes extra time for the coherence loss on fez (+0.010) and marrakesh (+0.012), so the table clause is also incomplete. Table III's caption says the table is about the phase kick and that coherence causes are in III D. The abstract and conclusion say an extra readout time above 4, 1 and 12% is excluded on all three.
  - why it matters: a reader of the table row reads "extra time is excluded as the cause of the kick on kingston only", which contradicts the abstract's "is not an advance along each qubit's own precession". No ledger row covers the phrase.
  - fix at source: ~/bones-forge/arxiv_one_readout/main.tex line 188: delete "; excludes it on kingston only" from the phase-kick row (or move it to a coherence row with the 39-minus-1 result). Rebuild, ship.

- id: HEU2-2 | check: P5 | severity: wrong-claim
  - where: paper abstract (p.1) and Secs. III F, G, H, I, J (pp.11 to 14)
  - page says: "−54.93 ± 1.28 and −38.64 ± 1.62 ◦/µs (shot noise only)"; "exponent 0.823 ± 0.012"; "+0.0200 ± 0.0016"; "1.47 ± 0.12 ◦"; "+0.0427±0.0182"; "width 0.104%, upper edge at two widths 0.47%"
  - source says: no level is given anywhere in the paper for these. Sec. II C defines only the 95% bootstrap intervals (brackets) and sigma = 95% width / 3.92. The sources show three different things behind "±": bootstrap widths with NB=200 (heuremen.org/experiments/2026-10-21-measurements/gate_trains/results_xtrain.text header and note 6), "sample SD of 3 jobs" (.../cost/results.text, exponent 0.01218), and "shot noise only" for Rigetti. "widths" (and "two widths apart") is used in III G, H, I without definition. The ±0.224 on fez ("the three reads spread by ±0.224") is the SD of three reads (.../measured_qubit/results.text).
  - fix at source: main.tex Sec. II C, add one sentence: "Values written ± in Secs. III F to III J are one standard deviation: bootstrap (200 resamples) for X-gate trains and the gate terms, SD of three jobs for the decay exponent and the per-processor spreads, shot noise for the Rigetti rates; a width is that standard deviation." Check each against its verify script first.

- id: HEU2-3 | check: R | severity: wrong-claim
  - where: paper p.4, Sec. II D
  - page says: "job lists re-pulled on 22 October from every account and instance"
  - source says: the final IBM job list was re-pulled on 23 October. ~/bones-forge/heuremen.org/experiments/job-index/index.html line 20: "re-pulled 23 October by pull_job_index.py from every key and instance, after the 22 October pull at 16:28 EDT held 520 and missed 26 jobs created that evening". Same in pull_job_index.py docstring (lines 1 to 3), ledger row jobindex.ibm_total ("re-pulled 23 Oct") and the Zenodo README ("546 jobs, re-pulled 23 October").
  - fix at source: arxiv_one_readout/main.tex line 68: "re-pulled on 23 October, after a 22 October pull that missed 26 jobs". Add a ledger row first.

- id: HEU2-4 | check: R, P2 | severity: wrong-claim
  - where: paper p.16, Sec. VI Data availability
  - page says: "raw IQ files and the raw files behind the other 2 to 11 October measurements ... are available on request"
  - source says: Zenodo v5 raw zip holds experiments/2026-10-21-iq-run/iqraw_ibm_fez.npz, iqraw_ibm_kingston.npz, iqraw_ibm_marrakesh.npz (listing of ~/Desktop/ZENODO_v5_UPLOAD/A_Readout_Is_Not_an_Idle_raw_v5.zip, md5 equal to the record), and the record README says "per-shot files of the pairs, IQ, flip-check, reach and length runs" are in the record. The 2026-10-07-equal-idle folder has no raw file in either zip.
  - fix at source: main.tex Sec. VI: "raw IQ files of the 7 October runs ...". (As written, a reader is told the IQ run files must be requested.)

- id: HEU2-5 | check: P1 | severity: style
  - where: paper p.14, Sec. IV, Hidden levels
  - page says: "the printed output reads “excluded” for kingston at 8 readouts"
  - source says: ~/bones-forge/heuremen.org/experiments/2026-10-22-flip-check/results_flip.text line 150: "is EXCLUDED as the cause (to the extent the X-flip catches it)". Upper case in the source.
  - fix at source: main.tex, write “EXCLUDED”.

- id: HEU2-6 | check: P1 | severity: style
  - where: paper p.17, reference [23]
  - page says: "A compilation framework for quantum circuits with mid-circuit measurement error awareness (2025), arXiv:2511.10921"
  - source says: arxiv.org/abs/2511.10921 current title (v2): "MERA: A Mid-Circuit-Measurement Error-Aware Compilation Framework for Quantum Circuits". The paper's title is the v1 title.
  - fix at source: arxiv_one_readout/refs.bib entry for arXiv:2511.10921.

- id: HEU2-7 | check: P9 (no AI statements beyond the two disclosure lines) | severity: style
  - where: paper p.9 to 10 (Sec. III D) and p.16 (Acknowledgments)
  - page says: "a re-reading by an outside referee (an AI reviewer agent)"; "Independent reviewer agents (AI), run without access to our conclusions, checked the claims of the 21 and 22 October runs against the raw data before submission"
  - source says: the brief allows only "collaboration with inorganic intelligences" and "An AI assistant, Claude Code (Opus 5.5), was used". These two sentences are further statements about AI.
  - fix at source: main.tex: "(an outside referee)"; acknowledgments: "An outside referee, run without access to our conclusions, ...". Bones' call, the paper is already on Zenodo v5.

- id: HEU2-8 | check: P9 (no email, no personal name of the owner; bylines Wayfinder and Bones) | severity: style
  - where: paper p.1 author line and footnote; Zenodo
  - page says: "K. Indahl 1, ∗" and "∗ Indahl@heuremen.com" (also a mailto: link annotation on p.1)
  - source says: house rule and memory: bylines "Wayfinder and Bones" only, no email printed. Same name elsewhere: Zenodo record creators "Indahl, Wayfinder" and "Bones"; Zenodo README.md in the code zip and ledger/zenodo_README.md: 'Phase, Coherence and Entanglement Costs ... on IBM Processors" (K. Indahl)'.
  - fix at source: main.tex author block; ledger/zenodo_README.md; Zenodo record metadata. Needs his word because arXiv usually wants a real name and a contact.

- id: HEU2-9 | check: P9 (plain sentences) | severity: style
  - where: whole paper
  - page says: 253 semicolons in pp.1 to 16 (14 in the abstract alone), e.g. "(qubits that precess the other way are kicked the same way; an extra readout time above 4, 1 and 12% of the stated length is excluded ...; a bound defined after the data)"
  - source says: no semicolons in page prose we wrote (brief) and feedback-plain-punctuation (25 Oct). The paper was frozen 25 Oct 09:26.
  - fix at source: main.tex. Decide whether the paper is exempt; if not, this is a full rewrite pass and a new Zenodo version.

### Faults (faults.pdf) and Guards (guards.pdf)

- id: HEU2-10 | check: R, V | severity: wrong-number
  - where: Faults p.8 entry 24; Guards p.7 item 22
  - page says: "One guard's catch rate over three days, same data, two denominators: per reply it read 27.3% → 27.4% → 47.4%, a collapse on the third day at +3.02 widths, resolved. Per thousand words it read 0.79 → 0.69 → 0.88 — +0.97 widths, nothing happened."
  - source says: the two series have different numerators. From triangulation/triangle/runs/hook_fires.log, first 374 rows, seated rows by day (6, 7, 8 Oct): replies 33 / 186 / 76, "PUSHED BACK" 9 / 51 / 36, "Two-lane" 9 / 42 / 30, words 11,349 / 60,678 / 34,113.
    Pushbacks per reply 27.3 / 27.4 / 47.4 %. Two-option frames per reply 27.3 / 22.6 / 39.5 %. Frames per 1,000 words 0.79 / 0.69 / 0.88. Pushbacks per 1,000 words 0.79 / 0.84 / 1.06.
    So 27.3/27.4/47.4 is pushbacks for any reason (96 of 295 = 32.5%), 0.79/0.69/0.88 is frames only (81 of 295 = 27.5%). iris_index/recounts/seed_faults_guards/RESULT.md lists both series as one clean pair and item 1 there says the 32.5% is pushbacks, not frames. Faults entries 20 and 41 and Guards p.1 already use the frame numerators (27.5%, 0.79/0.69/0.88), so the entry-24 example no longer matches them. The third-day figure also rose, it did not "collapse".
    A same-numerator recount keeps a contrast but not the printed numbers: frames, day 3 against days 1 and 2, about +2.7 widths per reply and +0.9 to +1.1 per 1,000 words (plain two-proportion and Poisson z, my own quick calculation); pushbacks, about +3.2 per reply and +1.1 per 1,000 words. I did not reproduce the document's "widths" definition, so the printed +3.02 and +0.97 are not reproduced either.
  - fix at source: ligera/FAULTS.html (entry 24) and ligera/GUARDS.html (item 22): use one numerator (frames) in both rows and state it, replace "a collapse" with "a rise", print the width definition.

- id: HEU2-11 | check: P2, R | severity: wrong-number
  - where: Guards p.1, third paragraph
  - page says: "So the guards are not thirty-eight separate checks"
  - source says: Guards numbers 39 procedures (1 to 39, PDF pp.3 to 9; ligera/GUARDS.html has 39 numbered headings, item 39 "Business copy passes a tone gate that refuses persuasion").
  - fix at source: ligera/GUARDS.html line 25: "thirty-nine" (or drop the count, see HEU2-18).

- id: HEU2-12 | check: P2, R | severity: wrong-number
  - where: Guards p.9, item 36
  - page says: "The eight family headings — not the forty-four modes — are injected at the top of every exchange"
  - source says: Faults numbers 45 modes (1 to 45; ligera/FAULTS.html has 45 numbered headings, 44 and 45 were added later and sit out of order). Eight families is right.
  - fix at source: ligera/GUARDS.html line 172: "forty-five".

- id: HEU2-13 | check: P6, VI (a bound is not "nothing") | severity: wrong-claim
  - where: Faults p.13 entry 41; Guards p.1 and p.9 item 36; Faults p.8 entry 24; Guards p.7 item 22
  - page says: "The corrections landed individually and changed the rate not at all." / "That was measured and it does not work." / "discipline was measured and it does not improve" / "moved the underlying rate not at all" / "nothing happened"
  - source says: the reading under these is three daily values (0.79, 0.69, 0.88 per 1,000 words, day 3 at +0.97 widths) and the document's own sentence "No improvement that clears its own width", which is CONSISTENT with no change and with some change, and no bound is printed. The 25 Oct outside referee (iris_index/recounts/seed_faults_guards/REFEREE_OWN.md) adds: the "two-lane" label also counts "bare verdict" and "two-branch if" hits that are not two-option reductions, the 374-row cut is the scanner's tuning set, the scanner rule changed on 7 Oct inside the window, and 36 seated rows are rewrites within 3 minutes of a pushback.
  - fix at source: ligera/FAULTS.html entry 41, ligera/GUARDS.html "first principle" and item 36: "no change that clears its own width over three days", print the bound, drop "does not work / does not improve / not at all".

- id: HEU2-14 | check: P4, VI | severity: wrong-claim
  - where: Faults p.6 heading and text of entry 20; Guards p.1
  - page says: heading "...and it is a compression artifact, not ignorance"; "Reducing a situation to two options is what compression does to a thing with three states, and knowing better does not stop it"; Guards: "It never removes it, because reducing three states to two is what compression does"
  - source says: what was measured is 57.1% (44 of 77 cold long replies) against 27.5% (81 of 295 seated replies), arms with no common length range (cold median 1,052 words, seated 342). The same page says "we cannot tell whether context reduces it". REFEREE_OWN.md: logit of frame on log(words) plus seated = +0.21 [−0.46, +0.89], CANNOT_TELL. No test of "compression" as the mechanism exists in the record. Pack P4: a cause named where only a rule-out was measured.
  - fix at source: ligera/FAULTS.html entry 20 heading and last sentences; ligera/GUARDS.html "And it is not ignorance" paragraph: state the two rates and that context did not remove it; drop the mechanism or label it a reading defined after the data.

- id: HEU2-15 | check: P2, R | severity: wrong-claim
  - where: Guards p.7 item 25; Faults p.14 entry 45 ("about 1,805 words of copy before, 542 after"); Guards p.9 item 39 ("catches that morning's version 23 times", "fired on 11 lines of the approved site"); Faults p.2 entry 1 ("14.5 ps ... 20.9 ps", slopes "−1.8 to −2.9")
  - page says: Guards 25: "correctly rejects deliberate faults four times in five"
  - source says: iris_index/recounts/seed_faults_guards/RESULT.md ("NOT FOUND this pass") lists "four of five referee; 1,805 -> 542 words; 23 times / 11 lines; 14.5 / 20.9 ps and slopes". The 25 Oct edit (ligera/FAULTS.pre-drop2-20261025.html against FAULTS.html) removed "four of five" from Faults entry 27 and the "0.0005 width" from both documents, but Guards item 25 still prints "four times in five". I grepped watch/, ligera/, nueva/, parallax/, triangulation/, iris_index/ for the other four and found no record. (Found and held: the quote "You name the processors. We name the figures worth checking." is verbatim in watch/tp_score.jsonl row 658; 0.682 to 0.343 is in nueva/NUEVA_SKETCH_20261008.md lines 147 and 289; sealed 26/4/2 is in watch/tp_score.py lines 41 to 47.)
  - fix at source: ligera/GUARDS.html item 25: drop "four times in five" like Faults 27. Either find the receipts for the rest or print them as "from a dated note, raw rows not kept".

- id: HEU2-16 | check: R | severity: wrong-claim
  - where: Faults p.1 header and p.14 footer; Guards p.1 header and p.11 footer
  - page says: "revised 22 October 2026"
  - source says: the text was edited after that date: entry 45 added 23 Oct (ligera/FAULTS.html.pre-tone-20261023 against .pre-recount-20261025), numbers and wording changed 25 Oct 08:49 (recount) and 25 Oct 14:05 (drop2): entry 20, 16, 41, the Guards score table interval and Fisher p, entries 24 and 27. PDFs rendered 25 Oct 18:05 UTC.
  - fix at source: ligera/FAULTS.html and GUARDS.html header and footer "revised 25 October 2026" (or leave the date and state the rule).

- id: HEU2-17 | check: P9 (company name) | severity: style
  - where: Faults p.1 and p.14, Guards p.1 and p.11
  - page says: "Wayfinder and Bones, Heurémen — 10 October 2026" and, in the footer line directly above "Heuremen LLC", "Wayfinder and Bones, Heurémen, 10 October 2026"
  - source says: the company is "Heuremen LLC" (brief).
  - fix at source: ligera/FAULTS.html and ligera/GUARDS.html byline and footer line: "Heuremen LLC".

- id: HEU2-18 | check: P9 (no count of our things in a lead line) | severity: style (borderline)
  - where: Faults p.1 lead paragraph; Guards p.1 lead paragraph and third paragraph; Faults p.14 footer
  - page says: Faults: "This document replaces three earlier ones"; Guards: "two of them are recorded as having been removed"; "Both documents replace three earlier ones"; "thirty-eight separate checks"; Faults footer "a running list of failure modes in eight families"
  - source says: feedback-no-counts-in-titles (23 Oct): no count of our things in a title, heading, lead or label. The titles and headings are clean. The lead paragraphs carry counts.
  - fix at source: ligera/FAULTS.html, GUARDS.html lead paragraphs. Bones' call whether "lead paragraph" is in scope.

- id: HEU2-19 | check: P9 (plain sentences, word choice) | severity: style
  - where: Faults and Guards
  - page says: 17 semicolons in Faults, 20 in Guards (e.g. "Ask what the statistic does under the null as n grows; if it grows, the threshold must grow with it."); "apparatus" 3 times in Faults, 7 in Guards ("An unequal apparatus across the columns being compared", "The apparatus is equalised across every column"); "hand-labelled cases" (Faults 23).
  - source says: no semicolons (brief); feedback-no-apparatus (25 Oct): say setup or name the thing. "apparatus" and "hand-" are outside the brief's list, noted for completeness.
  - fix at source: ligera/FAULTS.html, GUARDS.html.

### Zenodo record (10.5281/zenodo.23169755, v5.0.0)

- id: HEU2-20 | check: P4, P6 | severity: wrong-claim
  - where: Zenodo v5 description ("Method" sentence) and README.md in the code zip ("Method in one line")
  - page says: "Each mid-circuit readout is compared with an idle of exactly the published readout length, on the same qubits, in the same job." README: "circuits run twice per job; medians over qubits with 95 % bootstrap intervals (2000 resamples)"
  - source says: paper Intro and Sec. II B: "exactly in the 21–22 October runs; within 0.24% on the 16-sample grid in the 7 October runs"; the 7 October copies are separate jobs, not two circuits in one job; the Rigetti runs and the 2 to 11 October measured-qubit, decay and X-train runs have no readout-against-idle arm. The record's description generalises the 21–22 October method to every folder. The description also states "the readout turns the phase, costs coherence and costs Bell pair concurrence" without the paper's limits (fez coherence on a copy-gap reading, selected shots can bias the loss upward, excitation and leakage not excluded as the whole cost on fez and kingston).
  - fix at source: ledger/zenodo_README.md (the one maintained copy, carried by ledger/build_zenodo.sh) and the record description (edit in Zenodo): "for the 21 and 22 October runs", add "selected shots can bias the loss upward".

- id: HEU2-21 | check: P1 | severity: style
  - where: Zenodo record metadata, keywords
  - page says (API): keywords include "quantum measuremen"
  - source says: typo (missing t). The record's keywords also differ from the ones in ~/Desktop/ZENODO_v5_FORM.txt ("superconducting qubits; mid-circuit measurement; crosstalk; IBM Quantum; dephasing; entanglement; weak measurement"); the record has: superconducting qubits, quantum measuremen, readout duration, spectator qubits, measurement-induced dephasing, IBM Quantum, Rigetti, quantum hardware characterization.
  - fix at source: edit the published record's metadata in Zenodo (does not need a new version); bring the form file in line.

- id: HEU2-22 | check: P7 | severity: style
  - where: ~/bones-forge/ledger/ledger.py SURFACES and ledger.jsonl
  - page says: surface 'zenodo' = ~/Desktop/ZENODO_v4_FORM.txt
  - source says: the live record is v5 (ZENODO_v5_FORM.txt). The one live row on that surface (abs.kick4, "1.7 to 2.4 degrees per readout on four processors") is in the v4 form; the live v5 description has no kick number. check_ledger.py --coverage: faults 1 of 40 decimal numbers in a row, guards 1 of 31 (3 live rows each), so the Faults and Guards figures are largely outside the ledger.
  - fix at source: ledger.py SURFACES['zenodo'] to the v5 form; add rows for the Faults and Guards figures that have a record (HEU2-10 series, 217 of 316, 216 of 608, 96 pushbacks, 57.1/27.5).

- id: HEU2-23 | check: P8 | severity: style (low)
  - where: paper PDF metadata
  - page says: no /Title or /Author in the paper PDF (Creator "LaTeX with hyperref"); Faults and Guards carry /Title.
  - source says: browser tab shows the file name.
  - fix at source: main.tex \hypersetup{pdftitle=...}.

## 3. HOLDS

- File identity: live = canonical = ligera copies = public_mirror = Zenodo v5 paper PDF (paper), live = canonical = ligera copies (Faults, Guards). See COVERAGE for hashes and the one stale Desktop PDF.
- Zenodo: latest = v5.0.0 = concept DOI target; both file md5 equal to the upload folder; description names seven processors (six at 156 qubits, ibm_phoenix 120) as the paper does; period 24 Sep to 23 Oct and Rigetti 25 Sep to 5 Oct as the paper does; code-zip data files identical to the site tree.
- Ledger (I, R, P7): check_ledger.py drift 0; every one of the 404 paper-surface snippets is in the PDF; no withdrawn row printed in any PDF.
- Headline kick: 1.73 [1.29, 2.21], 2.41 [1.96, 3.58], 2.13 [1.44, 2.79], 1.79 [1.16, 2.66] equal results_kick.text lines 4, 9, 14, 19 (21-readout-vs-idle). Planned ratio R0 1.1658 to 1.2035 and rate-cut 0.947 to 1.100 equal results_prereg.text and results_kick.text. Control run −1.6180 [−2.0847, −1.1786], −2.8638 [−3.5519, −2.0896] equal results_prereg.text; Fig. 2 labels match.
- Sec. III B: K=1 bounds 0.1519 and 0.0903, copy-gap marrakesh −0.029 [−0.154, +0.100], K=10 0.13/0.28/0.23 (8 to 10%), 11.4% fez repeat, |1⟩ G values +0.178, +0.9226, kingston +0.066 and repeat +0.049 [−0.098, +0.132] ("about 0.1" uses the −0.098 end, correct for a larger kick in |1⟩).
- Table II: all 25 arms and the prose counts recounted from the printed table (13 of 14 kingston arms below zero overall, 12 of 14 within two couplings, 18 of 25 arms within two couplings, ranges −0.26 to −0.58, −0.69 to −1.38, 0.33 to 3.13); rows equal summary_table.text.
- Raw-readout coherence (iq-run results_iq.text): kingston +0.0056 and +0.0062, marrakesh +0.0087 and +0.0205 pooled, N=2 values +0.0054, +0.0074, +0.0042; outside-cluster 0.2 to 0.4% and 1.8%; 97 to 99% shots kept. Pairs: fez +0.0070, marrakesh +0.0093, kingston +0.0100 [+0.0040, +0.0138], differences 0.0088/0.0104/0.0065.
- Readout-instruction run and repeats: ratios 0.58/0.51 (marrakesh), 0.920, 1.008 [0.799, 1.372], 0.946 and 0.981 (kingston), 0.938 and 0.879 (fez); lengths 1.884/1.380/1.340 µs and ratios 0.702/0.633/0.807 equal results_*.text.
- Echo: −1.504 [−2, −0.9481], −3.243, +0.4473 [+0.317, +0.5649], −0.09438 [−0.1753, −0.005838] equal results_dd.text "[all]" rows.
- Floors: 6.0% and 5.6% (reach synth_results.text), 10 of 210 = 4.8%, 20 of 396 = 5.1%, 32 of 528 = 6.1% (job-index/tallies.text), 3 of 147 and 7 of 147 arithmetic.
- Gate trains: verify_xtrain.py results show the four DIFFERS rows are all already handled in the PDF (31 to 94% from results_ratio_three_jobs.text; −0.011 on pittsburgh 4 Oct; width 0.010).
- Rigetti arithmetic: 38.64/54.93 = 0.70; 54.93 − 38.64 = 16.3 ± 2.1; mean rise +0.0427; t = 2.34 on 6 d.o.f. below 2.447.
- Run-time facts: control run submitted 23:01:05 UTC (kingston), plan pushed 23:00:47 (index.html), plan hashed 51 s before the first 21 Oct job (14:52:48 to 14:53:39), Qiskit 2.5.2 and runtime 0.49.0 (readout-vs-idle index.html), Table I job counts (job-index/tallies.text: 563, 12, 305, 32, 48, 65, 54 reproduce).
- Literature (P1, Q36), compared with the arXiv abstracts or full text: Hothem (22%, 38%, 26 times, ibmq_algiers), Kumar (bLM = +0.0007, [−0.0033, +0.0049], drift rule, diagnostic not certification), Kan et al. ref [36] (21% and 38% X-memory, Z memory +2.6% overlapping intervals, 0.079 rad/µs, residual ZZ, ibm_phoenix Nighthawk r2), Govia (ibm_peekskill, coherent Z-phase by Stark shift, delay-rb), Smith (Heron r3 ibm_boston, measure_2, ancillary GHZ coherence loss), Tong (three-fold), Zhong, Hoyau, Gao, Montañez-Barrera (10 QPUs, IBM/IQM/Quantinuum). No misquote.
- Four outcomes in the paper: reading checked for folded signs and for one-sided tests; the abstract and conclusion print bounds (4, 1, 12%; 0.15 and 0.09; 14, 6, 24%), the planned ratio above 1 is shown rather than hidden, post-hoc labels ("defined after the data") are on every reading in the abstract, Sec. III and Sec. IV. No cause named in the paper where only a rule-out was measured (mechanism stated as open).
- Quotes in the paper: one quoted program output (HEU2-5). Quoted writer output in Faults 45 ("curt and arrogant", "You name the processors. We name the figures worth checking.") is verbatim in watch/tp_score.jsonl row 658.
- Guards score table recomputed from watch/tp_score.jsonl rows 1 to 608: 608 rows, 204 before (33.6%), 148 unaided (24.3%), 37 (6.1%), 19 (3.1%), 216 by the human partner (35.5%), 404 after, families 217/44/55 and 4/12/19, untagged 257, first 20 rows 13 before, 8 unaided, 14 family I; exact 95% 0.9 to 25.1% (2 of 26) and 19 to 64% (8 of 20); Fisher p 0.058 and 0.012. All equal the PDF. Faults "217 of the 316" = 217+44+55. 96 pushbacks, 295 replies, 57.1% (44 of 77), 27.5% (81 of 295) and 32.5% (96 of 295) equal hook_fires.log. 36 against 16 is 2.25 times. 27.1/11.5/3.1/43.8/14.6 = 26/11/3/42/14 of 96. 15.3 ppm, 1/432000, 1/41 and (2/π)·0.695 = 0.4425 checked by arithmetic; σy(T/2) = 2a/π derived.
- Neutral: no religion or nationalism words in any PDF; no internal machine, codename or key names in any PDF; no email in Faults or Guards; no typos found by dictionary scan (British spelling throughout); no raw template markers, "NaN", "undefined" or "??" in any PDF.
- Links: no broken link in the paper (HTTP 200 for all heuremen.org and arXiv URLs; 16 publisher DOIs answer 403 to a script only).
- Faults and Guards say in their own footers that no instance is reported with its run, so their unreceipted figures are a stated limit, not a hidden one (but see HEU2-15).
