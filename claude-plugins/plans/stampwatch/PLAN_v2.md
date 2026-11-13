# stampwatch: plan amendment v2, before code

Heuremen LLC, 13 November 2026. This amends PLAN.md (commit f570f1f), which stays as it was. Every change below answers the outside
referee's pre-code pass (verdict MOVES). Nothing has been coded and no blind snapshot has been read for the fault.

## Witness

The plan's outside witness is its push to GitHub (recorded in the repository's public events). A commit's own date is set by whoever
commits and is self-witnessed.

## Observations and outcomes are separate

- **FROZEN_RECORD:** the label moved and every content group under it is unchanged.
- **FROZEN_DATE:** the label moved, this field's own date and value are unchanged, and other fields under the label moved.
- **CARRIED:** direction B, content hash changed, label unchanged, no evidence change.
These are reported as counts (fields, units, snapshots), not as outcomes. Only FROZEN_RECORD is headlined. For IBM records the output
says "the record's per-field dates show the field was not remeasured": a finding about the label, never about the vendor.

Outcomes (ABOVE, CONSISTENT, CANNOT_TELL with an outcome reason, NOTHING_RETURNED) come only from rules 4 and 5.

## Rule 4, replaced: event-level reading

- Each RESTAMPED_IDENTICAL event (a field's date moved and its value is bitwise identical) is tested against its field's floor: the
  share of date moves of that field whose value came back bitwise identical.
- The floor is per field always. It is per backend where that backend has at least 200 date moves of the field in the floor window,
  else the field's cross-backend floor, and the output says which.
- The floor is learned leave-one-unit-out (a unit never sets its own floor) and only from the floor window, records stamped
  2026-05-04 to 2026-09-14, which excludes every test pair.
- The floor's own n and exact 95 % interval are printed. Each event's p-value is the binomial probability of an identical value at
  the floor's upper bound. Events are flagged with Benjamini-Hochberg at q = 0.05 over all events in the run.
- A floor of zero identicals in n moves uses the upper bound of its exact interval, never zero.
- Unit summaries (k flagged of n moves) are printed beside the events and are not outcomes.
- Shot-quantized fields (readout_error, prob_meas0_prep1, prob_meas1_prep0) are not under rule 4. They go under rule 5 with step
  1/shots where the shot count is known, else they are listed as not tested.
- Not tested, written now: unit-level habitual restamping as an outcome (the alternative reading).

## Rule 6, amended

A changed evidence path whose content hash changed: not flagged. An evidence path whose stamp moved and whose content is unchanged is
itself checked under direction A.

## Test set, replaced where the referee found a set that could not fail

Positives:
- IBM Q6, defined by rule: consecutive saved records of one backend, stamp moved by more than 24 h, T1 and T2 values and dates unchanged
  on at least 95 % of qubits. The code lists the pairs it finds. The referee's dig counted 14 pairs and 4,204 unchanged entries, and
  noted 30 files against 25 hashes. The code's own list and hashes are printed before any reading and reconciled against that count;
  a difference is reported, not resolved by hand.
- Planted synthetic feed, one case per axis: whole record frozen; some fields frozen under a moved label; a field date restamped with
  an identical value against a noisy history; a quantized repeat contradicted by the reference; a quantized repeat agreed by the
  reference (must not flag); direction B with no evidence change; direction B with only the evidence stamp touched; duplicate
  snapshots with one stamp; a missing read time (refused). Every case must come out as planted, or the build fails.
- House positives (private annex, sha256 e5b90d75...): HELD. They are notes, not files. They are scored only after the quantized case
  has GFZ Potsdam's observed Kp for 2026-09-30 fetched with a receipt (not a forecast) and the house row pinned by id, and the
  direction-B case has its real rows. The annex is then re-hashed and the new sha published beside the old one.

Negatives:
- Every field date move in IBM record pairs chosen by stamp gap (more than 24 h) and field dates moved on most qubits, taken as they
  are, including any value that came back identical: the remeasured pairs boston 09-19 to 09-21, boston 09-26 to 10-02, marrakesh 09-21
  to 10-22 18:21, and every further pair the same rule selects outside the floor window. Pairs are not chosen by whether values
  changed.
- The quiet-day quantized case (house annex, held as above).
- Configuration test, not a negative: declared-static fields (num_qubits, backend_name, units) are excluded by rule 2 and listed.

## Kill condition, replaced

Before reading, the negative set's n and the expected false-flag count under the floor are published. If more than 1 % of events in
the negative set are flagged after the Benjamini-Hochberg correction, rule 4 is wrong: stampwatch then ships as "lazy restamps only"
(FROZEN_RECORD, FROZEN_DATE and CARRIED counts, no RESTAMPED_IDENTICAL), or not at all. Any planted case not recovered fails the build.

## Blind feeds

- Hugging Face model repositories: lastModified against every file's blob id, the 200 most downloaded models frozen by rule at
  2026-11-13T17:26:38Z. Labelled here as a feed whose label is coupled to content by construction: expected near zero, it tests false
  positives. Direction B cannot appear in it. Results name no repository as at fault. Collector snap_hf.py, sha256 38f8c207aef4aea0fb86298efbff3db391ee8da7701451f1b3634f6e757560eb.
- open.canada.ca CKAN (data.gov's CKAN API answered 404 on 13 Nov 2026, so the Canadian federal portal, same CKAN shape): dataset
  metadata_modified and resource last_modified, against a sha256 of each CSV resource we fetch ourselves. 50 datasets drawn by
  random.Random(seed = f570f1f's full hash) from the first 1000 CSV datasets by metadata_created. Collector snap_ckan.py, sha256 0d62c83c4ffbadc406d71bd6f7dda91fa6787dfce33bafbe9256f48a1aa6f099.
Both collect only until the code and this amendment are referee'd.
