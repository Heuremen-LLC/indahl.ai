# stampwatch: plan, written before any code

Heuremen LLC, 13 November 2026. Scope and referee conditions from Sage (outside referee). This file is committed and pushed before
stampwatch exists, so its git commit time on GitHub is the timestamp of the plan.

## What it detects

A label stops being bound to the content it attests. Two directions:

- **A. Label moved, content frozen.** A "last updated", "calibrated" or "verified at" stamp advances between two snapshots while the
  values it covers are unchanged.
- **B. Content moved, label carried.** The values change between two snapshots while a "verified" or "current" label stays, with no new
  evidence event.

It does not detect witnesses disagreeing on the same reading (a different tool), and it names no cause: it reports "stamp moved, value
and field date unchanged across n snapshots", never why.

## Input

A folder of snapshots of one feed, each a JSON file with its read time (from a manifest, else the file name, else refused), and a spec
naming: label paths; content groups (fields, with an optional per-field date path); declared-static fields (excluded by name, listed in
the output); quantized fields with their step; optional evidence paths (for direction B); an optional outside reference series.
Built-in adapter: IBM Qiskit BackendProperties (label last_update_date; per qubit T1, T2, readout_error, each with value and date).

## Rules, fixed now

1. Each snapshot keeps its raw copy, sha256 and read time. Unreadable snapshots are NOTHING_RETURNED and counted.
2. Consecutive snapshots are compared per label and per content group. Static fields never count as frozen.
3. Direction A, per field with its own date: the record stamp moved and the field's date and value are both unchanged: FROZEN_DATE.
   The field's date moved and its value is bitwise identical: RESTAMPED_IDENTICAL.
4. RESTAMPED_IDENTICAL is judged against a noise floor learned from the same feed's own history: for that field across all units, the
   share of date moves whose value came back bitwise identical. A unit (e.g. one qubit) is ABOVE when the exact 95 % (Clopper-Pearson)
   interval of its identical-share lies wholly above the feed's pooled share; CONSISTENT when wholly at or below; else CANNOT_TELL
   (TOO_WIDE_TO_RESOLVE). Units with fewer than 5 date moves are CANNOT_TELL (NO_INTERVAL_FORMABLE).
5. A quantized field whose value repeats is CANNOT_TELL unless an outside reference shows the value it should have had; with a reference,
   a repeat that the reference contradicts is ABOVE.
6. Direction B: content hash changed, label unchanged and no evidence path changed: CARRIED. With a changed evidence path: not flagged.
7. Outcomes per unit and per group: ABOVE, CONSISTENT, CANNOT_TELL with an outcome reason, NOTHING_RETURNED. Counts of each beside every
   share. No cause is named.

## Test set, fixed now

Positives:
- IBM Q6 (external): saved QIA records where last_update_date moves while T1 and T2 values and dates stay frozen. Headline positive.
- Planted synthetic feed: freezes planted at known snapshots in both directions, plus the hardest case, a field date restamped with a
  bitwise-identical value against a noisy history. Must recover every planted case at its snapshot.
- Two house positives (one quantized with an outside reference, one direction-B), named in a private annex, sha256
  e5b90d75da834ebc03cb69b849837b5db6cc6d107f69b7d7fef78390ddf56878. Recall only; never headlined.

Negatives:
- IBM qubits recalibrated normally (stamp, field dates and values all move): the large clean set.
- The quiet-day case of the quantized house feed (value repeats, the reference agrees).
- Declared-static IBM fields (num_qubits, backend_name, units).
- A direction-B slot that changed with a fresh evidence event (house annex).

Blind feed (nobody in the house has looked at it for this fault): Hugging Face model repositories, snapshotted over time: the
lastModified stamp as the label, the file list with each file's sha (blob id) as content. Chosen before any snapshot is read.

## Kill conditions, fixed now

- On the normal-recalibration negative set, if more than 1 % of qubit-field date moves are flagged ABOVE, the noise-floor rule is wrong:
  stampwatch then ships as "lazy restamps only" (FROZEN_DATE and CARRIED, no RESTAMPED_IDENTICAL), or not at all.
- Any ABOVE on the quiet-day quantized negative fails the quantized rule; it ships without rule 5 until fixed.
- Any planted case missed fails the build.

Results on the known positives are recall on cases we already know, not a hit rate. Only the blind feed can support a claim.
