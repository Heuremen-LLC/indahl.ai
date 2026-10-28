#!/usr/bin/env python3
"""Recompute Bitcoin block hashes from the 80-byte header fields. Stdlib only. usage: verify_btc_headers.py btc_headers.jsonl
Checks per row: sha256d(header) == id, hash <= target(bits), and each row's previousblockhash == the older row's id.
Outcome VALID / INVALID, never a bare pass."""
import sys, json, hashlib
rows = [r for r in map(json.loads, open(sys.argv[1])) if "id" in r]
def sd(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def tgt(bits):
    e, m = bits >> 24, bits & 0x7fffff
    return m << (8*(e-3)) if e > 3 else m >> (8*(3-e))
ok = hbad = pbad = lbad = 0; first = None
for i, r in enumerate(rows):
    hdr = (r["version"].to_bytes(4,"little",signed=True) + bytes.fromhex(r["previousblockhash"])[::-1] + bytes.fromhex(r["merkle_root"])[::-1]
           + r["timestamp"].to_bytes(4,"little") + r["bits"].to_bytes(4,"little") + r["nonce"].to_bytes(4,"little"))
    h = sd(hdr)[::-1].hex()
    if h != r["id"]: hbad += 1; first = first or (r["height"], h, r["id"]); continue
    if int(h,16) > tgt(r["bits"]): pbad += 1; continue
    if i+1 < len(rows) and rows[i+1]["id"] != r["previousblockhash"]: lbad += 1; continue
    ok += 1
print(("VALID" if ok and not (hbad or pbad or lbad) else "INVALID"), f"rows={len(rows)} hash_ok={ok} hash_mismatch={hbad} above_target={pbad} broken_link={lbad}", first or "")
