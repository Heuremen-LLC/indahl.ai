
## 2026-10-30 10:16 Site pass D-1, D-10, D-26: judge tags are not items (withdrawal), verdicts under adapter names, rounds with three asks, training sessions split at the 26 Aug validation fix
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the old 'seen more than once' gate grouped by a log tag that is not an item id (tag audit: 2 adapter names, 16 one-character buckets, 6 chance repeats of 175 short labels); the withdrawn rows go, the new counts use no such gate
- II: holds: counts are plain totals per class from the log, nothing netted; the 1,240 is printed beside the 1,779 total
- III: n/a: counts without a sign or a direction in this reading
- V: holds: the ruler is a count read from the log and from training_counts/summary.json; the old interval on 24 buckets is removed with the rows
- VI: holds: the withdrawn reading becomes no reading at all, not a consistent; the training split prints both periods
- R: holds: numbers read from judge_counts/summary.json (verdicts_under_adapter_names 1240, rounds_with_three_asks 6347) and training_counts/summary.json (before_fix 85 of 90, after_fix 0 and 7 of 9), fix date 2026-08-26 from train_continuous.sh
- L1: n/a: no parser of model replies is involved, these are log line counts
- L2: holds: the counts were read after the tag audit, no rate was published before it
- L3: n/a: no vendor setup compared in these counts
- L4: n/a: no machine-to-machine claim made by these rows
- L5: holds: recount from our own released log files with our script, keys matched by the summary field names
- L6: holds: verdict lines that name an item uuid all read FAILED, leaving in queue, stated in the audit file
- L7: n/a: no gold set scored here
- L8: n/a: no paired comparison in these counts
- L9: n/a: no prompt in these counts
- L10: holds: the adapter name is reported as a name, not as an item
- L11: n/a: nothing substituted for these counts
- L12: n/a: no referee or labeller output is shown in these rows
- P1: n/a: no quotes in these five rows
- P2: holds: each row names its summary file and key
- P3: holds: labels say adapter names, rounds with three asks, sessions before and after the 26 August fix
- P4: holds: no cause named for the judge or training figures
- P5: n/a: these five rows carry counts without intervals
- P6: holds: the page says the judge figures are not item-level agreement
- P7: holds: ledger first (these adds), then the pages ship through ship.sh
- P8: cannot tell: the rebuilt IRIS pages are checked after the release build
- P9: holds: plain sentences, read in full wording
- P10: fixed: the page did not label the split; it now says the split was defined after the pooled counts were read
