# TAPE: a public, hash-chained record of what we published and when, with a beacon. Plan, written before the first entry.

## What it does
Every 6 HST ticks (Heuremen Standard Time) a script appends entries to one chain. Each entry carries the hash of the one before it, so changing any old entry breaks every later one. The chain, every leaf behind every entry, and the verifier are public. The tape page shows the chain newest first.

## Entry kinds (fixed now)
1. **feeds**. Written every run. The leaves are the SHA-256 of the exact bytes each live desk feed served at that moment (/slug/live.json for every desk) and of headlines.json. A feed that cannot be read is a leaf with the word NOTHING_RETURNED in place of a hash.
2. **pages**. Written when at least one page changed since the last pages entry. The leaves are the SHA-256 of every built public page, taken from the sitemap, with asset version strings removed so a stylesheet change alone is not a page change.
3. **beacon**. Written every run. beacon = SHA-256 of the drand round randomness, the feeds root of the same run and the previous entry hash, joined as text with a colon. drand is the League of Entropy quicknet chain, latest round. If drand cannot be read, the entry says drand NOTHING_RETURNED and the beacon is built without it, never silently.

## The chain
Entry fields: n, t (UTC), kind, subject, root, prev, entry. entry is the SHA-256 of the canonical JSON (sorted keys, no spaces) of the other six fields. The first entry has prev of 64 zeros. The chain is append-only. A mistake is corrected by a later entry that says what it corrects, never by editing an old one.

## Merkle roots
Binary tree over SHA-256. A leaf is SHA-256 of the byte 0x00 followed by the leaf text. A node is SHA-256 of the byte 0x01 followed by the left and right child. An odd node at a level is carried up unchanged. Leaf text is the label, a tab, then the hash. Leaves are sorted by label.

## Anchoring
tape.jsonl is in the ARCHIVE manifest, so every OpenTimestamps stamp (every 24 ticks) anchors the whole tape up to that moment. The tape page shows the newest anchored head and which entries came after it.

## Verification
tape_verify.py recomputes the chain from the entries, every leaves file's root and every beacon from its inputs. The drand round is shown with its link so it can be checked against drand itself. The page links the verifier and the files.

## Uses
Beacon values seed our hand-check samples and shuffles. A seed must come from a beacon entry whose time is later than the plan that uses it.

## Known-good gate
Before the first entry the verifier is run on a synthetic chain. It must pass the clean chain, flag a planted change in an old entry, flag a planted change in one leaf, and flag a beacon that does not match its inputs. The gate result is committed with the first entry.

## Not claimed
That a page's content is true. That a feed's content was correct. That the tape existed before its first entry. That a beacon is unpredictable beyond the unpredictability of the drand round it uses. That an entry is anchored before an ARCHIVE stamp covers it.

## Not in this plan
Quantum bits from IBM. They arrive by addendum with their own known-good test of hardware bias on each processor, and never before.

## Addendum 1 (29 Oct, before the first receipt: VAULT)
A fourth entry kind and a public page where anyone can add a hash.
1. **commits**. Written when at least one receipt is waiting. The leaves are each waiting hash with the Unix second we received it. The root is the Merkle root of those leaves, built as above. The entry's number is then stored beside each hash so a receipt can say which entry holds it.
2. **What we receive.** Only a 64-character SHA-256 hash, from the visitor's own browser, when they press a receipt button. We store the hash and the time. We do not receive or store any file, any sealed file, any key, any file name or any network address. Limits: 20 receipts per address per hour and 3,000 a day in all, enforced with a one-way hash of the address and the hour that is deleted after three days.
3. **Sealing.** The browser encrypts a file to a chosen future round of the drand quicknet chain using tlock-js, with the chain hash and public key fixed in the code, so the release time rests on drand and not on us. The sealed file is saved on the visitor's computer and is never sent to us. We cannot scan, host, find or release it. A hash of the sealed file can be sent for a receipt, like any other.
4. **Not claimed.** That a receipt shows who made a file or that its content is true. That a sealed file is safe to hold or share. That a sealed file can be opened if drand stops publishing. That we can recover or remove any file, because we never hold one.
5. **Known-good.** Before the first receipt: a file sealed to a round about a minute ahead must not open before that round and must open, byte for byte, after it, in a browser; a hash must return a receipt and be found again by hash; a malformed hash, a second post of the same hash and the 21st post in an hour must behave as rules 2 and 1 say. The result is committed with the first receipt.

## Addendum 2 (29 Oct, before any quantum run: QBITS)
Quantum bits from IBM join the beacon as an extra input. The beacon's guarantee still rests on drand. The quantum bits add a second, independent source and a published measurement of how fair a superposed qubit is on each processor.
1. **qbits entry.** Written after a run. The leaves give the processor, the job id, the shots, the number of qubits, the SHA-256 of the raw bits file, the extracted value and the fairness reading. The root is the extracted value. The raw bits file is public.
2. **Extraction.** The extracted value is the SHA-256 of the raw bits in shot order, qubit order within a shot, packed eight to a byte. A hash is a heuristic extractor and we say so. We publish the raw bits and the measured bias and correlation so anyone can judge them.
3. **Beacon.** A beacon built after a qbits entry exists adds that entry's root as a fourth input: SHA-256 of the drand randomness, the feeds root, the previous entry and the newest qbits root, joined with colons. A beacon with no qbits entry behind it keeps the three-input form and its leaves say qbits_root NONE. The verifier handles both.
4. **What the run measures.** Three circuits on every qubit of one processor in one job: no gate (the readout of 0), an X gate (the readout of 1), and a Hadamard (the superposition whose measurement gives the bits). The Hadamard probability of a 1 is predicted from the first two as half of P(1 given 0) plus half of P(1 given 1). The reading is whether the delivered bits are fair and whether they match that prediction. One of four outcomes per processor: CONSISTENT with a fair coin, ABOVE (more ones than half), BELOW (fewer), CANNOT_TELL.
5. **Not claimed.** That the bits are unpredictable beyond what the raw data shows. That anyone but us can check that the bits came from the processor, because IBM does not publish our job records. We show the job id. That the extractor removes correlations, only that it hashes them with everything else.
6. **Limits.** One job per run on one processor. No run if the account's remaining seconds are under 300 or the estimate is over 20. The job is capped at 20 seconds of execution. Every run is listed in the plan folder with its estimate and its measured seconds.

## Addendum 3 (29 Oct, before the first use: receipts on headlines, seeds from the beacon)
1. **Receipt line.** Each page's headline block gains one line saying that the feed behind the number was last hashed onto the tape at entry N, with the first characters of that hash, linking to the tape. It claims only that the feed existed in that form at that entry. The summary feed carries, for each feed, its entry number and hash from the newest feeds entry.
2. **Seeds from the beacon.** A hand-check sample takes its seed from the first beacon entry whose time is later than the commit of the plan that names the sample. sample_seed.py prints that seed for a plan file and draws a sample of k items from n with it: item i is ranked by SHA-256 of the seed, a colon and i, and the k lowest ranks are taken. Anyone can recompute the draw from the plan commit time and the public tape. Samples already drawn with a fixed seed stay as they were and say so.
3. **Entry links.** Each entry in the live summary carries the address of its leaves file.

## Note 1 (29 Oct, on the first qbits entry)
The plan says a beacon's previous-entry input is the entry before it. It is the feeds entry of the same run, and that is the entry before it except in a run where a qbits entry was written between them, which happened once (entries 22 and 23). The verifier now checks the real rule: the beacon's inputs are the root and the entry hash of the newest feeds entry before it. The tape was not changed. A qbits entry's root is its extracted value, and the verifier checks that against the leaves and, when the raw bits file is present, against its hash. The tick now writes qbits entries before feeds so the two are always adjacent.

## Note (30 Oct 2026, from the site pass)
After each run the rider starts tape_push.py in the background. It commits and pushes only code/tape in the public mirror, so that the leaf links on the page open soon after an entry is written and not at the next release. Nothing else in the mirror is committed. The push is skipped when the public repository holds newer commits, and the release script then pushes the folder with the rest. No rule changed.
