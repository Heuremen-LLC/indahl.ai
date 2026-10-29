# ARCHIVE: proof that our records existed, in this form, on this date. Plan, written before the first digest.

## What it does
Every 24 ticks of Nova's clock a script hashes every plan, history, change log, summary and data store of every live corner, plus a commitment to the two internal files we do not publish (the ledger and the book: a hash only, never content). The list of paths with their hashes is the manifest. Each digest chains onto the one before it: digest = SHA-256 of the previous digest followed by the SHA-256 of the manifest. The chain and the manifests are public. Each new digest is stamped with OpenTimestamps, which anchors it to the Bitcoin chain through public calendar servers, so a third party can verify the digest existed before a given block without trusting us.

## What it proves and does not
Proves: a file with this hash existed at this time, and the chain has not been rewritten since, because a changed old file changes every later digest. Together with the plan files committed before each read, it shows plans came first.
Does not prove: that a file's content is true, that a file we did not list was not changed, or anything about files before the first digest.

## Rules (fixed now)
1. The chain is append-only. A mistake in a manifest is corrected by a later entry that says what it corrects, never by editing an old one.
2. A file that disappears from the list is recorded as removed in the next manifest.
3. The stamp files and the chain are copied to the public repository at archive/ and pushed with the next release.
4. The OpenTimestamps proofs are upgraded when the Bitcoin attestation exists (typically within hours) by the same script on a later run.
5. Verification is public: the script has a verify mode that recomputes a manifest from the files and checks the chain, and the OpenTimestamps client verifies each stamp.

## Outside copies (his word 29 Oct)
Public repositories are submitted to Software Heritage, key pages to the Internet Archive, and release tags are cut on each public repository so the Zenodo GitHub link archives each release with its own DOI once enabled. These carry only what is already public.
