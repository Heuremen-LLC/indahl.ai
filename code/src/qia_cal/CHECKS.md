
## 2026-10-30 10:01 Note 3: IBM readout shot count read per record (1,024 on fez and marrakesh); 24 runs re-read; duplicate chain entry; waiting list from both run files
packs: Q,P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is IBM's own figure with its own exact interval, built the same way as Note 1; the only change is n per record, read from the record before any re-read (plan Note 3 committed first by file time 13:57 UTC, re-reads appended about 14:00)
- II: holds: per-qubit outcomes kept, counts per quantity in each corrected entry; no net; the corrected and original entries both stay in the chain
- III: holds: direction words unchanged (from IBM's side); ABOVE and BELOW counts are given separately per quantity
- V: holds: two rulers side by side, old rule n=4,096 recomputed beside Note 3 on every run (dry run on fez run 1 reproduced the published file on 156 of 156 qubits)
- VI: holds: four outcomes per qubit per quantity; the corrected counts keep CONSISTENT and CANNOT_TELL
- R: fixed: Note 3 time first typed from memory as about 14:20 UTC, corrected to the file time 13:57 UTC before commit; shot evidence from the records (fez 312 of 312 multiples of 1/1024)
- QA: holds: IBM's readout figure is an assignment count; its shot count is now read from the record, not assumed
- QB: n/a: no idle arm in this change
- QC: holds: synth adds a null world with IBM counts out of 1,024; n inferred in 40 of 40; no chance calls; old rule also 0 in a pure null, stated in Note 3
- QD: holds: four outcomes; copies not combined; each run read on its own
- QE: holds: no mechanism named; Note 3 says the old extra calls are corrected, not explained
- QF: holds: entry numbers, job ids and times read from entries.jsonl and file times
- QG: caught: the fault was found by an outside-seat read (site pass lane B) of the live page, after publication; referee of this fix still to come
- P1: n/a: this change quotes nobody
- P2: holds: corrected files at /qia/cal/<job>n3.json, chain entries name the entry they correct
- P3: holds: the rule label in each entry names Notes 1 and 3 and the shot count used
- P4: holds: no cause named
- P5: holds: intervals stay exact 99.9% (readout) and 99.99% (T1), printed in the rule text
- P6: holds: no summary sentence changed on the page by this commit; the cal.js sentence is changed by the site pass with the same wording as Note 3
- P7: cannot tell: no ledger rows exist for the hourly panel (site pass B-30 asks for them); the panel feed is live, not shipped through ship.sh
- P8: holds: /qia/cal.json and /qia/cal/dbi9u26ne4hc73be5mhgn3.json answer 200 with the corrected counts
- P9: holds: plain sentences in Note 3
- P10: holds: Note 3 says it was written after the fez and marrakesh readings were published
- O1: holds: cal.py stays the same rider on the bus, no new job
- O2: holds: a second entry for a job is refused and printed, not silently dropped
- O3: n/a: no GPU used by the calibration
- O4: holds: checked by the live feed changing (fez off 51 to 45), not by a process
- O5: holds: paths built from the file location
- O6: n/a: no GPU job involved here

## 2026-10-30 11:35 Note 4: send a calibration job when IBM's readout or T1 figures changed since our last job on that processor, or 6 hours passed (was every hour)
packs: Q,P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the rule is set from the cost and change records before it runs (Note 4 written and committed before the first round under it); each job is still read against the IBM record it ran under, as Notes 1 and 3
- II: holds: no reading is folded; what is given up is stated in Note 4 (drift inside a long-lived record read every 6 hours instead of hourly)
- III: n/a: no sign or direction changes; the change is when a job is sent, not how it is read
- V: holds: the ruler per run is unchanged; the send rule compares the 4 IBM figures per qubit (T1, both readout probabilities, readout_error) rounded to 6 places
- VI: holds: due() returns sent / not sent with the reason printed; an unreadable or missing record sends (it never skips silently)
- R: holds: counts read from the record: 69 of 69 charged jobs billed 4 s (runs.jsonl 58 + runs_eu.jsonl 13, 2 still SENT); mirror spans 40.0 to 43.0 h per processor; changes aachen 3, boston 0, fez 4, kingston 9, marrakesh 2, phoenix 6, pittsburgh 5 (29)
- QA: holds: the trigger compares IBM's own published figures, record against record, not against our readings
- QB: n/a: no idle arm
- QC: holds: dry run with no IBM call: phoenix due (all 120 qubits' readout changed since the 11:40 UTC job), boston due (12.4 h), fez/kingston/marrakesh/pittsburgh/aachen not due; fez newest record equals its last job record on 156 of 156 qubits, so equal records compare equal
- QD: holds: four outcomes per run unchanged
- QE: holds: no mechanism named
- QF: holds: times from runs files and mirror file names
- QG: cannot tell: no outside referee on the send rule yet; it changes cadence only, every run still chained
- P1: n/a: nobody quoted
- P2: holds: the page sentence will point to PLAN.md Note 4 on GitHub when changed
- P3: holds: Note 4 names the rule and the 6-hour floor
- P4: holds: no cause named
- P5: n/a: no interval changes
- P6: cannot tell: the /qia calibration intro still says every hour; changed in the next site release, not in this commit
- P7: n/a: no ledger number changes
- P8: n/a: no new public file in this commit
- P9: holds: plain sentences in Note 4
- P10: holds: Note 4 says it was written on Wayfinder's question after the hourly runs, from their own records
- O1: holds: same rider on the tick bus; only which processors it sends to changes
- O2: holds: not-due processors are printed with the reason, not dropped silently
- O3: n/a: the calibration send uses no GPU on either machine
- O4: holds: the next round's printed due/not-due lines are the check, read from the bus log
- O5: holds: paths from H and B as before
- O6: n/a: no GPU job is started or queued by this change
