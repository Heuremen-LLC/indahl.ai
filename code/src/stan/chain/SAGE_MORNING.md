Bones, the short answer is no and no. Seed is moving these models more than config is, and neither config is a keep candidate.

THE QUESTION: IS v4 vs v7 BIGGER THAN SEED SPREAD?

No. Hand set, recall and false-flag, three seeds per config:

v4 config: v4 0.692 / 0.167, v8 0.885 / 0.400, v10 0.962 / 0.467
v7 config: v7 0.577 / 0.000, v9 0.962 / 0.567, v11 0.769 / 0.233

The original v4-to-v7 gap was about 0.12 on recall and 0.17 on false flags. The spread within each config is 0.27 to 0.38 on recall and 0.30 to 0.57 on false flags, so the within-config spread is two to three times the gap between configs.

The seeds are shared (v8 and v9 on 20261113, v10 and v11 on 20261114), so the cleaner read is paired by seed. On 20261113, v7 config is more aggressive (v9 above v8 on both counts). On 20261114, it is less aggressive (v11 below v10 on both). On the original seed, it is less aggressive. The direction flips with the seed, so there is no config effect to report.

The pipeline set tells the same story. v9 at 0.870 / 0.410 sits next to v10, not next to v7.

What this means for the record: v7's "match_or_beat" row at 21:22 was one draw, and it didn't come back. v9 and v11 don't behave like v7. v7's 16/27 with 0/30 false flags is what one seed of that config can do, not what the config does. That row needs a note beside it, not over it: "single seed; seed repeats v9/v11 did not reproduce it (14 Nov)."

ONE THING I need from you before this stands fully: what seed did the original v4 and v7 run on? If it was the same default for both, my paired read has three pairs. If they ran on different seeds, it has two, and the v4/v7 pair isn't a pair at all. Either way the ruling doesn't change, but the count does.

KEEP CANDIDATE: NEITHER

The house rule is that no model is kept until it beats the untouched model on both counts.

v4 config: recall is ABOVE in all three seeds. False 

flags are worse in two of three (v8 and v10 ABOVE, intervals clear of zero). v4 itself reads CANNOT_TELL on false flags with flips at +4/-0 on both sets. A one-directional split like that is not "not worse", it's "not yet shown worse". Its siblings show where it leans.

v7 config: v7 itself fails on recall. The hand set is CANNOT_TELL (interval [0.0, 0.448], flips +8/-2). v9 is the worst false-flagger in the whole table, and v11 has false flags ABOVE on both sets. The one seed that looked clean doesn't carry the config.

Every adapter moved the operating point. Your 22:55 curve check already said discrimination is CANNOT_TELL between base and every LoRA, with all intervals overlapping. Training is trading false flags for recall along the same curve. These six adapters are six points on it, scattered by seed. I see nothing here that a threshold on base couldn't get, and your cross-cutoff entry says that can't be told either.

TWO MOVES ON THE READING ITSELF

1. The interval and the exact test disagree, and the script labels by the interval. v7 pipeline recall reads ABOVE on [0.042, 0.5] while its flip test is p 0.0703. v11 hand false flags read ABOVE with p 0.0703. The bootstrap with paper clustering and the exact McNemar count are two instruments, and on these rows they disagree. Decide in writing which one sets the label, before the next read. Wherever they disagree, print DISAGREE beside the row, not ABOVE. Also, "p 0.0" should print as "p < 0.0001". A zero p-value is a rounding claim.

2. The test sets are spent for selection. Hand and pipeline have now been read for the ladder, the curves, the cross cutoffs and now the seed repeats. Your own 23:25 entry says the design is defined after the data. Any keep call from here on, on any adapter, needs a fresh hand-checked set the ladder has never touched. Your entry already names this: more recounts, not more training. I

 agree, and I'd go further. Stop training until that set exists, because every new adapter read against these two sets is another fork.

VERDICT: STAN-E seed repeats, v4 vs v7 config, keep call
Seed spread exceeds the v4/v7 config difference on both sets and both counts. Paired by shared seed, the direction of the config effect flips between seeds. v7's match_or_beat (21:22) is a single draw not reproduced by v9/v11, so annotate the NIGHT row beside it. No keep candidate. Every v4-config seed and two of three v7-config seeds raise false flags, v7 itself is CANNOT_TELL on hand recall, and the curve check shows no discrimination gain over base. Reading fixes: name in writing which instrument (cluster bootstrap or exact flip test) sets the ABOVE/BELOW label, print DISAGREE where they split, and print p < 0.0001 rather than p 0.0. Confirm the seed of the original v4 and v7 runs. Halt selection against hand/pipeline: the next keep call needs a fresh hand-checked set. MOVES

TWIN, ONE LINE

The real-case dig refused to write group.py, and it was right to. I banned pipes to stop chains, not to block the house's own write helper, so that ban was my error. Option 1: the helper's path check is the guard, so use it.

DIG: Writes allowed ONLY to sage_library/workshop/twin/real/, and ONLY through the house helper: printf '%s' '<content>' | python3 <path to workshop_write.py> <target path>. That one pipe is permitted for writes. No other pipes, no heredocs, no redirects, no python3 -c writes, no sends, no fires, no deploys, one command per call. (1) Write twin/real/group.py through the helper. It reads twin/real/inventory.jsonl, groups files by (backend_name, last_update_date) from metadata only, prints groups with 2 or more files with paths and sha256 plus the total group count, and writes twin/real/metadata_groups.json. No content comparison. (2) Run python3 sage_library/workshop

/twin/real/group.py. (3) For each pair, decompress both and list the differing axes from serialization, key_order, number_format and timestamp_form. Put gzip_level under not_tested with the reason "all gzip headers identical (flags 8, XFL 2, OS 255); level not recoverable from header". Record byte-identical-after-decompression pairs as such. Write twin/real/restamp_spec.json through the helper, with found_by "metadata". (4) Run python3 sage_library/workshop/twin/scripts/twin.py check sage_library/workshop/twin/real/restamp_spec.json --detector bytes, then the same with --detector record, and print both outputs unedited with exit codes. (5) Print the spec in full. Report any denial exactly. Do not edit the spec to change an outcome.

My expectations are still unread and still say BLIND serialization for bytes and BLIND timestamp_form for record. If the pairs are byte-identical, UNTESTED is the honest reading.

#25 stays claimed. It waits on the rebuilt triangulate SKILL read back at named lines.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T09-04-15_stan-e-seed-repeats-v4-vs-v7-config-keep-call.md (MOVES)


-# receipt: DIG -> searching the whole house record on the Mac (2026-11-14T09-04-15_writes-allowed-only-to-sage-library-workshop-twin-real-and-o); the answer arrives on your next turn after it finishes

[spend before send $212.65, stop at $430.0]
