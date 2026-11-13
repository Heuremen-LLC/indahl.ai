# Scout: new public indexes for indahl.ai (12 Nov 2026)

Research only. Nothing built, nothing contacted. All counts below were pulled on 11 Nov 2026 from public APIs (Zenodo, Dryad, OSF, Figshare, Crossref, OpenAlex). The arXiv API returned empty bodies all session, so no arXiv counts are given.

## Read this first: what the counts are and are not
Every count below is a keyword or metadata hit, not an eligible-study count. None of these studies has had its acknowledgments read. Eligible volume is therefore an upper bound. Zenodo counts use type=dataset and, where marked, access_status=open. Zenodo queries with OR are loose full-text matches, so I used quoted phrases.

One rule needs the owner's call before any index of areas B is started. The house rule excludes funding by defence, military, intelligence or government agencies of any country. Read literally, NSF, NIH, ERC, UKRI and DFG are government agencies. Ecology, psychology, seismology and most open data journals are mostly government-funded, so a strict reading would delete most of areas B. A narrow reading (defence, military, intelligence only) keeps them. Crossref funder metadata makes either reading automatable: 3,199 of 5,723 Scientific Data papers since 2024 carry a funder record, and the funder names are machine-readable. Papers with no funder record would still need an acknowledgments read.

## Verified numbers table
- Crossref, since 1 Jan 2024: Scientific Data 5,723 papers (3,199 with a funder record); Data in Brief 3,526 (2,209 with funder); Earth System Science Data 952 (771 with funder). Totals ever: Scientific Data 9,153 DOIs; Data in Brief 13,066; ESSD 2,394; GigaScience 1,585; Journal of Open Psychology Data 98.
- Dryad: 73,174 datasets in the whole repository. Query hits: ecology 29,816; coral 924; camera trap 485; psychology 458; bird song 256; seismic 127.
- OSF: 66,384 PsyArXiv preprints; 314,082 registrations; 4,178 projects whose description mentions replication; 151 data-category projects with replication in the title. The OSF API cannot filter preprints by data-link availability (tried has_data_links and data_links, both rejected), so the data-link subset must be found by fetching each preprint record.
- Zenodo datasets: earthquake 2,553; GNSS or GPS station 1,129; exoplanet or light curve 646; LLM and outputs 649; seismic waveform 260; open education or learning analytics 292; bioinformatics benchmark 149; replication package 293; psychology replication 60.
- Zenodo datasets, quantum-adjacent, quoted phrases: IBM Quantum 206; trapped ion 56; transmon 52; nitrogen-vacancy 49; superconducting qubit 47; qubit with raw data 44; quantum key distribution 42; Rigetti 29; optical tweezer 25; IQM 19; randomized benchmarking 12; quantum computer with counts 9; quantum random number 7; two-level system 6; Amazon Braket 5. Summing the non-IBM lines gives about 350 with overlaps.
- Figshare datasets (API caps a page at 100): superconducting qubit 55; trapped ion 100 or more; NV center 49; quantum random number 25; IQM 22; Rigetti 2; two-level system 100 or more.
- OpenAlex open-access English articles since 2023 (papers, not data-released): superconducting qubit 19,160; nitrogen-vacancy 36,320; quantum random number generator 24,592; neutral atom tweezer array 1,032. This shows paper volume is large but only a few percent release data.

## Ranking (volume x ease of automated screen x visibility)

### 1. Data-paper journals index (Scientific Data, Earth System Science Data, Data in Brief, GigaScience)
Verified: 10,201 papers since 2024 across the first three (5,723 + 3,526 + 952), 16,000 or more ever for these journals plus GigaScience.
Why it fits: every paper in these journals exists to release a dataset, so the raw-files rule is satisfied by definition. Each paper states figures in its Technical Validation or Data Records section: number of files, number of records, total size, date range, sample counts. Those are exactly the stated figures the house method recounts.
Where: Crossref API (metadata, funder, license, relation links to the data DOI), then Zenodo, Figshare, Dryad, GitHub or institutional repositories for the files. Formats are mostly CSV, NetCDF, GeoTIFF, Parquet, HDF5.
Screen: the easiest of all candidates. Crossref returns funder names and funder DOIs per paper, language is English by journal policy, and the data link is in the metadata. Company-authored papers can be flagged by affiliation.
First cheap recount: stated record count or file count in the Data Records section against the repository file listing (Zenodo and Figshare list file names, sizes and checksums by API, no downloads needed). Outcomes: CONSISTENT when counts match, ABOVE or BELOW with the width when the paper states more or fewer files than are deposited, CANNOT_TELL when the repository is closed or the figure is not stated.
Visibility: researchers search "[topic] dataset" constantly and data-paper titles are written for that search. A list with title, link, file list and classification is useful before any recount. This is also the broadest net for the flagged first question, since earth science, health and materials data papers all appear.
Risk: Data in Brief is mostly small supplements and many entries are company or lab data with thin stated figures. Start with Scientific Data and ESSD.

### 2. Earth and station data (earthquake, seismic, GNSS, climate station)
Verified: Zenodo 2,553 earthquake datasets, 1,129 GNSS or GPS station datasets, 260 seismic waveform datasets; plus ESSD 2,394 papers ever.
Why it fits: waveform and station files are standard formats (miniSEED, SAC, RINEX, NetCDF, CSV) and papers state counts that can be recounted from the files with no compute: number of stations, number of events, record length, sampling rate, completeness percentage.
Where: Zenodo API, ESSD via Crossref, PANGAEA, IRIS and EarthScope, FDSN web services for the public networks.
Screen: moderate. Much of seismology is funded by government geological surveys or defence-linked monitoring, so the funder screen removes a real share. Crossref funder fields plus a name list works.
First recount: stated station count or event count against the station file or catalog row count; stated record completeness against gaps in the released files.
Visibility: strong. "earthquake dataset" and "seismic data download" are high-intent searches by students and engineers.

### 3. Ecology and evolution datasets on Dryad
Verified: 73,174 Dryad datasets; 29,816 ecology hits; 485 camera-trap, 924 coral, 256 bird-song hits.
Why it fits: Dryad requires a README and a data file per paper, almost always CSV or Excel, and the API returns a related-works link to the paper DOI, the file list and file sizes. Papers state sample sizes, plot counts and individual counts that can be recounted by counting rows.
Where: Dryad API v2 (search, per-dataset files, authors, funders field). Formats CSV, XLSX, R scripts.
Screen: easy to automate because Dryad records carry a funding field, but ecology is heavily NSF, NERC, ERC and agency funded. Under the broad government-agency reading this index nearly empties; under the narrow reading it is large.
First recount: stated n (individuals, sites, observations) in the abstract or methods against the row count of the main data file.
Visibility: moderate to high. Ecologists search by species and region, and every dataset page is long-tail search traffic.

### 4. Psychology on OSF and PsyArXiv (replication data)
Verified: 66,384 PsyArXiv preprints, 4,178 OSF projects mentioning replication, 314,082 registrations, 458 psychology hits on Dryad.
Why it fits: this is the original reproducibility field. Papers state N, effect size and test statistics, and the released CSV allows recomputation of the mean, N after exclusions and the test statistic in a few lines.
Where: OSF API v2 (nodes, preprints, registrations, file listings via the storage links), PsyArXiv, Journal of Open Psychology Data.
Screen: harder than 1 to 3. OSF has no funder field and no data-link filter, so every candidate needs a metadata fetch and an acknowledgments read from the PDF. Volume is large but screening cost per study is highest.
First recount: reported N and group means against the released CSV; reported exclusions against the rows removed.
Visibility: very high, since replication results draw attention, but this is also the crowded area with existing projects (Many Labs, SCORE) so the List adds less than elsewhere.

### 5. Qubit-adjacent non-IBM bundle (superconducting, trapped ion, NV, photonics, QRNG, QKD)
Verified: about 350 keyword hits on Zenodo datasets (non-IBM lines summed, with overlaps) and about 300 on Figshare (capped pages), against 19,160 open-access superconducting-qubit papers since 2023. Only a small fraction release raw data.
Why it fits: this is the owner's home field and the QIA reader already searches it. Released files are HDF5, CSV, NumPy or Matlab files of T1, T2, Ramsey, randomized benchmarking decays and spectroscopy sweeps. A stated T1 or fidelity can be refit from the released decay curve in seconds, which is the same recount as QIA applied to non-IBM devices.
Where: Zenodo, Figshare, Dryad, GitHub, Nature Portfolio and PRX Quantum source-data files. Vendor-posted public records: IBM calibration (already used), Rigetti and IQM and OQC pages, Amazon Braket device properties through the Braket API, Quantinuum and IonQ published specs. I did not verify the format or continuity of the non-IBM vendor records and recommend checking before relying on them. Braket is closed to us per the standing note, so existing public data only.
Screen: moderate. Quantum hardware is among the most defence-funded fields (DARPA, AFOSR, ARO, IARPA, national labs), so the funder screen removes a large share and the eligible count may be half or less of the hits. Crossref funder names catch most of it.
First recount: refit a stated T1 or T2 from the released decay trace and report the difference with its width; second, recount stated randomized-benchmarking error per gate from the released survival data.
Visibility: small audience but the right one, and it feeds the QIA brand. Lowest volume of the five, highest fit.

## Not ranked, with reasons
- Astronomy catalogs: 646 Zenodo exoplanet or light-curve datasets, but catalogs are usually released by survey teams and hosted by MAST, VizieR and CDS, so Zenodo undercounts. Funding is almost entirely government (NASA, ESA), so it is only viable under the narrow reading. Worth a second look if area 2 works.
- Bioinformatics benchmark releases: 149 Zenodo hits. Many need compute to recount. Low volume.
- Open education research: 292 Zenodo hits. Fits the OY division, small and mixed file formats, strong ties to existing OY pages. A good small add-on to the OY desk.
- LLM evaluation outputs: 649 Zenodo hits. Already covered by the IRIS plan.
- Two-level-system loss, QRNG, Rigetti, Braket on their own: single-digit to 29 Zenodo hits each. Only worthwhile folded into candidate 5.

## Suggested order
Build candidate 1 first with Scientific Data and ESSD only: Crossref gives the whole list and the funder screen in one pass, the file lists come from the repository APIs, and the first recount needs no downloads. Candidate 5 is the cheapest to run in parallel because the owner already has the qubit recount code from QIA.
