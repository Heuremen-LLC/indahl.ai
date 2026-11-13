
## 2026-11-12 10:33 Faults and Guards 2.0 migration of the CADENCE per-series outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the interval table, the two-day floor, the series rule and the Addendum 2 parsing are untouched
- II: n/a: no repeated item is counted, each series is one unit and none is netted across portals
- III: holds: the counts of series behind, on schedule and unreadable compared equal before and after for all eight portals (633 of 1,229 behind, 596 on schedule, 195 cannot tell), the most overdue list is identical
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md committed as 09b142f before any reading under it, an exact margin of zero width (O1) against a one-sided bound of zero with no tolerance, and the word BELOW keeps its meaning of behind, Wilson 95 percent for the share unchanged
- VI: holds: four outcomes kept, the old on-schedule series read ABOVE the bound and never CONSISTENT, unreadable series read CANNOT_TELL NO_INTERVAL_FORMABLE (195), the both-alternatives test is not applied since there is no null and no size that matters
- R: holds: cadence_tick.py re-run offline with the network refused on the stored portal files of 12 Nov, no number moved, at_bound is 0 in every portal, FEMA listed apart as NOTHING_RETURNED (1 failed read), req13 line 1 NOTHING_RETURNED, CANNOT_TELL 195 of 1424 (195 NO_INTERVAL_FORMABLE)
- P1: n/a: no quotation of any source is added
- P2: holds: each portal row carries the rule string, the reading counts and the causes of cannot tell, the addendum names the margin and the bound
- P3: n/a: no setting labels of any source are touched, portal and cadence words are unchanged
- P4: holds: no cause is named, a late modified date is still not called a failure to inform
- P5: holds: the per series reading says it is an exact figure with no interval, the share behind says Wilson 95 percent
- P6: holds: the summary is the same counts with a reason added, the page still says on schedule and behind in plain words and adds that no series reads consistent
- P7: holds: ledger rows cadence.total and cadence.total.old_rule keep their counts (633) so none is set, the stack desk still reads the consistent field, which is kept equal to on_cadence and documented in legacy_fields, page text edits follow this entry, nothing is deployed
- P8: cannot tell: the pages are not rendered in a browser and not served, nothing is deployed from this session, live.js was checked with node --check
- P9: cannot tell: the page sentences are written after this entry and linted by the site gate at the end of the migration, the addendum has plain sentences without semicolons
- P10: holds: the addendum is dated 12 Nov 2026, written before the reading under the new rule, and says the choice of the margin scale over the age scale is the owner's call
- O1: holds: the rider cadence_tick.py stays on the tick bus at its cadence, edited in place after a backup cadence_tick.py.bak-20261112-std2, parsed and run once offline with urlopen refused
- O2: holds: a portal that could not be read stays NOTHING_RETURNED and is listed apart by name, a failed fetch still sets the state back so it is tried again, nothing is counted as an outcome
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the updated stamp of summary_cadence.json and the portal read stamps, the offline test restored data/state.json, heads.jsonl and linkcheck.json from copies
- O5: holds: all paths in the rider are absolute or relative to its own folder as before, the KV put keeps PATH and the account id, the publish guard still blocks a non-tick run
- O6: n/a: no GPU job is started by this change
