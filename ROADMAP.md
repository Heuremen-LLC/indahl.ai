# Roadmap: what gets built next, in public

Every item is plan-first (the plan is committed before the data), live on the tick bus, with trend rows in this repository. A box ticks in the commit that finishes the item.

- [x] **arXiv version drift on every indexed study** ([live](https://indahl.ai/arxivdrift), [code](code/arxivdrift)). Flag when a later arXiv version changes the numbers or the claim we read, both versions shown. arXiv API, no key.
- [x] **Support windows against release activity** ([live](https://indahl.ai/support), [plan and two addenda](code/support/PLAN.md); an error in our first classifier caught by hand check before publishing). Stated end-of-life and support dates (endoflife.date) against actual release and support activity.
- [x] **Package claims against the files** ([PKGLICENSE live](https://indahl.ai/pkglicense): PyPI-stated license against the repository license, every disagreement opened by hand)
- [x] **Hugging Face license claims against the license files** ([live](https://indahl.ai/hflicense), [plan and four addenda](code/hflicense/PLAN.md): the planted-text gate and hand checks caught four reading errors before anything was shown). PyPI metadata (license, requires-python, stated contents) against what the release files hold.
- [x] **Older corners onto heuremen_kit** (Wilson interval moved to the kit in FORECAST, CADENCE, LAUNCH, CADA; an error in three of them found and corrected, see each plan). TIME, CADA, UPTIME, FORECAST, CADENCE move to the shared kit with summaries confirmed unchanged.
- [x] **Second seat for LINKROT** ([plan addendum 2](code/linkrot/PLAN.md)). Runner-network seat; a disagreement between seats reads BLOCKED.
- [x] **T1 and T2 rerun** (fez q148, plan note 4: T1 measured 0.82 then 1.05 microseconds against 5.86 published; T2 still unresolved, the echo decays faster than the first delay step; [results](https://indahl.ai/qia)). Interleaved circuits and delays sized to the measured T1 (fez q148 measured T1 0.82 microseconds against 5.86 published).
- [x] **Security claims against DNS records** ([SECRECORDS live](https://indahl.ai/secrecords), [plan and note](code/secrecords/PLAN.md): an HSTS preload header against its own requirements, an SPF record against the 10-lookup limit; every mismatch opened by hand and the SPF counts repeated with a second script).
- [x] **Stated model sizes against the weights** ([HFSIZE live](https://indahl.ai/hfsize), [plan, addendum and notes](code/hfsize/PLAN.md): a reader error and an inconsistency in the Hugging Face API found by hand before anything was shown).
- [x] **Vendor shutdown dates kept over time** ([CHANGE live](https://indahl.ai/change), [plan](code/change/PLAN.md)). Anthropic, OpenAI, Google and Cloudflare tables; every move, addition and removal logged. The test of whether stated dates hold fills as dates pass.
- [x] **Queue at each IBM processor** ([on QIA](https://indahl.ai/qia), [plan](code/qia-queue/PLAN.md)). Pending jobs hourly beside the waits our own jobs saw.
- [x] **Stopped trials in the last two years** ([TRIALS](https://indahl.ai/trials), [plan addendum 3](code/trials/PLAN.md)).
- [x] **Hash-chained archive of our records** ([plan](code/archive/PLAN.md)). OpenTimestamps proofs, Software Heritage, Internet Archive, and Zenodo copies of the repositories.
- [x] **Stated margin against later revision** ([REVISE live](https://indahl.ai/revise), [plan and note](code/revise/PLAN.md)). Monthly payroll first estimates against the BLS's stated interval, from the Philadelphia Fed's real-time data. No prices.
- [x] **The Fed's stated projection ranges against outcomes** ([FEDSEP live](https://indahl.ai/fedsep), [plan, addendum and notes](code/fedsep/PLAN.md)). September projections 2015 to 2025 against the 70 percent error ranges the Fed publishes. No rates or prices of ours.
- [x] **Every test side by side** ([STACK live](https://indahl.ai/stack), [plan and addendum](code/stack/PLAN.md)). The headline test of every live page in one table, ordered by outcome, no reading of its own.
- [x] **An outside seat reads our own pages** ([SEAT live](https://indahl.ai/seat), [plan](https://github.com/Heuremen-LLC/nodes/blob/main/drift/PLAN.md)). A GitHub runner compares every page with the repository and every feed with its limit.
- [x] **Install commands against resolution** ([PKGINSTALL live](https://indahl.ai/pkginstall), [plan, two addenda and a note](code/pkginstall/PLAN.md): a placeholder the reader missed and commands that did not install the project, both caught by hand before anything was shown).
- [x] **Our data as SQL tables** ([dataset heuremen-llc-data.heuremen_public](code/bigquery/README.md), [plan and addendum](code/bigquery/PLAN.md)). Every trend history, the hash chain and the STACK rows in BigQuery, readable by any signed-in Google account, row counts read back after each load.
- [x] **MLCommons AILuminate Safety results, kept and checked** ([AILUMINATE live](https://indahl.ai/ailuminate), [plan and note](code/ailuminate/PLAN.md)). The results page against its own reports, and every read kept so a later change to a published score shows. Release month against Hugging Face is next.
- [ ] **Queue against wait, the analysis** ([rule committed](code/qia-queue/PLAN.md), Note 1). Needs 7 days of hourly readings.
- [ ] **A second outside seat on a different network**. One runner is one seat.
- [x] **Model names against their weights** ([WEIGHTS live](https://indahl.ai/weights), [plan](code/weights/PLAN.md)). The most downloaded open-weight models read pass after pass. The first pass is read and the comparison starts with the second.
- [ ] **New Zenodo versions every month** (script written and tested; first scheduled run after the next release).
- [ ] **Amazon Braket deviations table**. Parked: needs a funded account.
- [ ] **Boston T1 and T2**. Job queued at IBM since the 29th, waits behind hundreds of pending jobs.
- [x] **Hospital price-transparency files** ([HPT live](https://indahl.ai/hpt), [plan and two addenda](code/hpt/PLAN.md)). The cms-hpt.txt at the root of each hospital website, the file it links, and the template header. Hand check found non-subjects in the list and eleven reading errors in the first read, both corrected in the addenda.
- [x] **Scheduled flight time against flown time** ([AIRLINE live](https://indahl.ai/airline), [plan and two addenda](code/airline/PLAN.md)). Bureau of Transportation Statistics record, January to August of 2019, 2025 and 2026, routes as the independent units, every ABOVE hand-checked on its largest routes.
- [ ] **ATLAS interconnection queues**. Large-load interconnection queues against announced data center MW, onsite generation permits, a live grid layer.
- [ ] **ISP broadband labels against M-Lab**. Access to the M-Lab tables works. A label states a typical speed for one plan, and M-Lab measures every plan of a network together, so a fair test needs single-plan providers or a plan mix we do not have. The plan will name which providers qualify before any measurement is read.
- [x] **Air quality sensors against EPA monitors** ([AIRQ live](https://indahl.ai/airq), [plan and note](code/airq/PLAN.md)). PurpleAir outdoor sensors within 200 metres of EPA continuous monitors, June to September 2025, against the EPA's own sensor performance targets.

Built and live: see `code/README.md` for every page and its folder.
