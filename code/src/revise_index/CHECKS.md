
## 2026-11-12 10:29 Faults and Guards 2.0 migration of the REVISE outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the 122 thousand stated margin, the windows and the gate are untouched, the gate still passed on the planted 122, 123 and -123 series and the four hand-checked months
- II: n/a: no repeated item and no flips are counted, each month is one unit as before and no outcome is netted across counts
- III: holds: the signed revisions, medians and largest values of both counts compared equal before and after the migration, ABOVE for the benchmarked count and CANNOT_TELL for the third release keep their signs apart
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md, committed as 7516d6c before any reading under it, bound 0.10 with no band and a closed edge, Wilson 95 percent over months and the year bootstrap of 4,000 draws with seed 7, no tolerance invented
- VI: holds: four outcomes kept, CONSISTENT is no longer available for the point figure 0.10, CANNOT_TELL carries STRADDLES_EDGE, the both-alternatives test is not applied because the plan names no size that matters and the addendum says so
- R: holds: revise_tick.py re-run offline on the stored BLS table (sha 1f13e4eecc47) and flat file (sha 17ac1fb382b2), 13 of 120 third release now CANNOT_TELL STRADDLES_EDGE (was CONSISTENT), 25 of 120 benchmarked still ABOVE, every other number identical to the summary of 12 Nov 14:14
- P1: n/a: no quotation of any source is added, the stated 122 thousand is a constant already read from the BLS technical note
- P2: holds: the feed names the rule, the interval method and level for each count and the addendum, beside the table sha and the flat file sha it already carried
- P3: n/a: no setting labels of any source are touched, the column and series names are unchanged
- P4: holds: no cause is named, the added fields say only which closed reason a CANNOT_TELL carries and the REQ-13 count line
- P5: holds: each count says its interval, Wilson 95 percent over months or the bootstrap over calendar years with draws and seed, in the feed fields interval and interval_y
- P6: holds: the summary is the same counts with the reading under 2.0 beside the recorded outcome, no stronger than before
- P7: holds: ledger row revise.third is set first with this entry, the surface text of the pages (live.js, headline builder, build_site.py rule sentence) is edited after it, nothing is built or deployed from this session
- P8: cannot tell: the pages are not rendered in a browser and not served, nothing is deployed from this session, the rule sentence and live.js edits that follow this entry are checked by node and a text lint only
- P9: cannot tell: the page sentences that follow this entry are written after it, they are linted for semicolons and counts in headings at the end of the migration, the addendum itself has plain sentences and no semicolons
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, the interval over calendar years keeps its label as defined after the first read
- O1: holds: the rider revise_tick.py stays on the tick bus at its cadence, edited in place after a backup revise_tick.py.bak-20261112-std2, parsed and run once offline through the venv python with the BLS reads replaced by the stored files
- O2: holds: a failed gate prints and exits so no outcome is published, failed reads are counted apart in the req13 block (0 now) and are outside numerator and denominator
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the updated stamp of summary_revise.json and the history.jsonl line written by each completed pass, the offline test line was removed from history.jsonl again
- O5: holds: all paths in the rider are absolute or relative to its own folder as before, the KV put keeps PATH and the account id, the publish guard still blocks a non-tick run
- O6: n/a: no GPU job is started by this change
