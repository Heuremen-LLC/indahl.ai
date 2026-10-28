#!/usr/bin/env python3
"""Recompute block hashes from header fields. Stdlib only. usage: verify_headers.py chain.jsonl [more.jsonl]
Header = version(4 LE) + prev hash(32) + merkle root(32) + time(4 LE) + bits(4 LE) + nonce(4 LE).
Prev hash is the hash of the next-older row, so each row proves the link to its parent.
Outcomes per chain: VALID (all recomputed hashes match and meet their own bits target), INVALID (a mismatch),
CANNOT_TELL (this script has no code for the chain's hash function, or a row is missing its parent)."""
import sys, json, hashlib, calendar, time
def sha256d(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def scrypt(b): return hashlib.scrypt(b, salt=b, n=1024, r=1, p=1, dklen=32)
ALGO = {"bitcoin":sha256d,"bitcoin-cash":sha256d,"bitcoin-sv":sha256d,"ecash":sha256d,"litecoin":scrypt,"dogecoin":scrypt}
def target(bits):
    e, m = bits >> 24, bits & 0x7fffff
    return m << (8*(e-3)) if e > 3 else m >> (8*(3-e))
def run(path):
    chain = path.split("/")[-1].rsplit(".",1)[0]
    rows = [r for r in map(json.loads, open(path)) if "hash" in r]
    if chain not in ALGO: return chain, "CANNOT_TELL", f"no hash function for {chain} in this script", len(rows)
    H = ALGO[chain]; ok = bad = nolink = 0; first_bad = None
    for i, r in enumerate(rows[:-1]):
        parent = rows[i+1]
        if parent["id"] != r["id"] - 1: nolink += 1; continue
        t = calendar.timegm(time.strptime(r["time"], "%Y-%m-%d %H:%M:%S"))
        hdr = (int(r["version"]).to_bytes(4,"little",signed=True) + bytes.fromhex(parent["hash"])[::-1] +
               bytes.fromhex(r["merkle_root"])[::-1] + t.to_bytes(4,"little") + int(r["bits"]).to_bytes(4,"little") + int(r["nonce"]).to_bytes(4,"little"))
        h = H(hdr)[::-1].hex()
        if h == r["hash"] and int(h,16) <= target(int(r["bits"])): ok += 1
        else:
            bad += 1; first_bad = first_bad or (r["id"], h, r["hash"])
    verdict = "INVALID" if bad else ("VALID" if ok else "CANNOT_TELL")
    return chain, verdict, f"{ok} headers recomputed and matched, {bad} mismatched, {nolink} without a parent row" + (f", first mismatch {first_bad}" if bad else ""), len(rows)
for p in sys.argv[1:]:
    c, v, d, n = run(p); print(f"{c}: {v}  ({n} rows) {d}")
