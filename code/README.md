# Code

Scripts behind the tables on indahl.ai. Free to read, run and cite with attribution. See LICENSE.txt in the repository root.

- `model/` builds and checks the model and hardware claims sources, one claims checker per source.
- `iris/` holds the Faults and Guards bench (items, runner, scorer), the Falcon training plan and scripts, and the model claims round for SmolLM2.
- `coin/` collects block records from public explorers, recomputes block hashes from header fields, and checks a chain's stated claims against its own record. It reads public data only.
- `mirror/` mirrors the calibration IBM publishes and audits each record against itself, with an independent recount script.
- `checks/` is the check block: the required fields every reading of ours answers before it is committed or published, the tool that writes and checks an entry, and a git pre-commit gate with a self-test.
- `t1t2-check/` measures T1 and a Hahn echo T2 together on chosen qubits with your own IBM account and compares the ratio with 2. It prints the estimated QPU seconds first and does not submit without --yes.
- `*/history.jsonl` in each live corner's folder (and `mirror/audit_history.jsonl`, `mirror/ibm_history.jsonl`) is one row of that corner's published numbers every few hours, added only when something changed. Each commit is a point on the trend.

Each plan file is committed before the run it describes. Run any script with `python3 -I` from its own folder.

<!-- live-index -->
## Live pages

- [qia-queue/](qia-queue/): QIA: queue at each IBM processor, hourly - https://indahl.ai/qia
- [archive/](archive/): Hash chain of our records, OpenTimestamps proofs and the Zenodo copies - https://indahl.ai/
- [time/](time/): TIME: public time servers, stated against delivered - https://indahl.ai/time
- [coin/](coin/): COIN: Ravencoin against its own whitepaper, with trends - https://indahl.ai/coin
- [cada/](cada/): CADA: public DNS filters against fresh abuse reports - https://indahl.ai/cada
- [uptime/](uptime/): UPTIME: vendor status pages against independent probes - https://indahl.ai/uptime
- [forecast/](forecast/): FORECAST: stated chance of precipitation against what happened - https://indahl.ai/forecast
- [cadence/](cadence/): CADENCE: stated update schedules against delivered - https://indahl.ai/cadence
- [trials/](trials/): TRIALS: ClinicalTrials.gov results due against results posted - https://indahl.ai/trials
- [launch/](launch/): LAUNCH: stated launch time against the time it flew - https://indahl.ai/launch
- [linkrot/](linkrot/): LINKROT: stated code links against live - https://indahl.ai/linkrot
- [mirror/](mirror/): QIA: IBM published calibration, mirrored, audited and tracked for stability - https://indahl.ai/qia
- [t1t2-check/](t1t2-check/): QIA: the T1 and T2 joint-measurement check - https://indahl.ai/qia
- [iris/](iris/): IRIS: language-model evaluations, Faults and Guards bench, lab queue - https://indahl.ai/iris
- [model/](model/): MODEL: vendor claims and model claims against published results - https://indahl.ai/hermes/model
- [atlas/](atlas/): ATLAS: built infrastructure, stated against delivered - https://indahl.ai/atlas
- [arxivdrift/](arxivdrift/): ARXIVDRIFT: Indexed arXiv studies against the version that stands now, live. - https://indahl.ai/arxivdrift
- [support/](support/): SUPPORT: Stated support windows against release activity, live. - https://indahl.ai/support
- [pkglicense/](pkglicense/): PKGLICENSE: Package licenses against repository licenses, live. - https://indahl.ai/pkglicense
- [hflicense/](hflicense/): HFLICENSE: Hugging Face stated licenses against license files, live. - https://indahl.ai/hflicense
- [hfsize/](hfsize/): HFSIZE: Hugging Face model names against the weights, live. - https://indahl.ai/hfsize
- [change/](change/): CHANGE: Vendor shutdown dates, read over time, live. - https://indahl.ai/change
- [secrecords/](secrecords/): SECRECORDS: Security headers and mail records against their own rules, live. - https://indahl.ai/secrecords
- [seat/](seat/): SEAT: An outside seat reads our own pages, live. - https://indahl.ai/seat
- [pkginstall/](pkginstall/): PKGINSTALL: PyPI install commands against resolution, live. - https://indahl.ai/pkginstall
- [stack/](stack/): STACK: Every test side by side, live. - https://indahl.ai/stack
- [revise/](revise/): REVISE: Payroll first estimates against the stated margin, live. - https://indahl.ai/revise
- [fedsep/](fedsep/): FEDSEP: The Fed's stated projection ranges against outcomes, live. - https://indahl.ai/fedsep
- [airline/](airline/): AIRLINE: Scheduled flight time against flown flight time per airline, live. - https://indahl.ai/airline
- [weights/](weights/): WEIGHTS: Open-weight model names against their weight files, pass after pass, live. - https://indahl.ai/weights
- [hpt/](hpt/): HPT: Hospital price-transparency files against the rule, live. - https://indahl.ai/hpt
- [ailuminate/](ailuminate/): AILUMINATE: MLCommons AILuminate Safety results, kept and checked, live. - https://indahl.ai/ailuminate
- [airq/](airq/): AIRQ: Air sensors against the EPA's own targets, live. - https://indahl.ai/airq
- [campus/](campus/): CAMPUS: The documents behind the OY page, kept over time, live. - https://indahl.ai/campus
- [hosts/](hosts/): HOSTS: Open-weight models, their hosts, quantization and uptime, live. - https://indahl.ai/hosts
- [tape/](tape/): TAPE: A public hash chain of every page and live feed, with a beacon value in each run. - https://indahl.ai/tape
- [api/](api/): API and MCP server - https://indahl.ai/api
- [kit/](kit/): The shared instrument pieces every corner uses - https://indahl.ai/
- [replies/](replies/): Right of reply: posted responses beside the rows they answer - https://indahl.ai/
- [progress/](progress/): The trend-row rider that writes history.jsonl in each folder - https://indahl.ai/
- [faultsguards](https://github.com/Heuremen-LLC/faultsguards): the Faults and Guards as a Python package. Live: https://indahl.ai/iris
<!-- /live-index -->
