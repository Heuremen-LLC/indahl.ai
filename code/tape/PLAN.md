# TAPE: a public, hash-chained record of what we published and when, with a beacon. Plan, written before the first entry.

## What it does
Every 6 ticks of Nova's clock a script appends entries to one chain. Each entry carries the hash of the one before it, so changing any old entry breaks every later one. The chain, every leaf behind every entry, and the verifier are public. The tape page shows the chain newest first.

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
