# Roadmap: what gets built next, in public

Every item is plan-first (the plan is committed before the data), live on the tick bus, with trend rows in this repository. A box ticks in the commit that finishes the item.

- [x] **arXiv version drift on every indexed study** ([live](https://indahl.ai/arxivdrift), [code](code/arxivdrift)). Flag when a later arXiv version changes the numbers or the claim we read, both versions shown. arXiv API, no key.
- [x] **Support windows against release activity** ([live](https://indahl.ai/support), [plan and two addenda](code/support/PLAN.md); an error in my first classifier caught by hand check before publishing). Stated end-of-life and support dates (endoflife.date) against actual release and support activity.
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
- [x] **An outside seat reads our own pages** ([SEAT live](https://indahl.ai/seat), [plan](https://github.com/Heuremen-LLC/nodes/blob/main/drift/PLAN.md)). A GitHub runner compares every page with the repository and every feed with its limit.
- [ ] **Install commands against resolution** (PKGINSTALL, plan committed, read in progress). The first pip install line in each top PyPI project's description against pip's dry-run resolution.
- [ ] **Queue against wait, the analysis** ([rule committed](code/qia-queue/PLAN.md), Note 1). Needs 7 days of hourly readings.
- [ ] **A second outside seat on a different network**. One runner is one seat.
- [ ] **Open weight model support windows**. CHANGE covers vendor deprecation tables only.
- [ ] **New Zenodo versions every month** (script written and tested; first scheduled run after the next release).
- [ ] **Amazon Braket deviations table**. Parked: needs a funded account.
- [ ] **Boston T1 and T2**. Job queued at IBM since the 29th, waits behind hundreds of pending jobs.
- [ ] **Hospital price-transparency files**. The required machine-readable file, stated at a URL, against whether it resolves and carries the required fields.
- [ ] **Airline on-time claims against BTS**. Stated on-time performance against the Bureau of Transportation Statistics record.
- [ ] **ATLAS interconnection queues**. Large-load interconnection queues against announced data center MW, onsite generation permits, a live grid layer.
- [ ] **ISP broadband labels against M-Lab**. Waiting on a Google sign-in for BigQuery.
- [ ] **Air quality sensors against EPA monitors**. Waiting on a free sensor-network API key.

Built and live: see `code/README.md` for every page and its folder.
