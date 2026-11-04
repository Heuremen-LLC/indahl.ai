"""yf_gate.py -- block gate for the FRESH TEST driver (Sage, 4 Nov). For each FILE + FILE.ots: the proof's digest must equal sha256 of the file's current bytes,
every Bitcoin attestation's commitment must equal that block's merkle root as served by BOTH mempool.space and blockstream.info, and the block must be mined before NOW.
Exit 0 = pass. Exit 2 = refuse and wait (pending only, or API unreachable). Exit 1 = refuse (wrong file, merkle mismatch, block not before start).
Usage: yf_gate.py NOW_UNIX FILE [FILE ...]   env YF_API overrides https://mempool.space/api (used by the planted tests)."""
import sys, os, json, hashlib, urllib.request
from opentimestamps.core.timestamp import DetachedTimestampFile
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
from opentimestamps.core.serialize import StreamDeserializationContext
API = os.environ.get('YF_API', 'https://mempool.space/api'); API2 = os.environ.get('YF_API2', 'https://blockstream.info/api')   # two servers must agree (Sage)
def get(path, base=None):
    with urllib.request.urlopen((base or API) + path, timeout=20) as r: return r.read().decode()
now = int(sys.argv[1]); worst = 0
for f in sys.argv[2:]:
    digest = hashlib.sha256(open(f, 'rb').read()).digest()
    with open(f + '.ots', 'rb') as fh: d = DetachedTimestampFile.deserialize(StreamDeserializationContext(fh))
    if d.file_digest != digest: print(f'REFUSE: {f}.ots is a proof of different bytes (file changed or wrong proof)'); worst = max(worst, 1); continue
    btc = [(msg, a) for msg, a in d.timestamp.all_attestations() if isinstance(a, BitcoinBlockHeaderAttestation)]
    if not btc: print(f'WAIT: {f} has no Bitcoin attestation yet (pending only)'); worst = max(worst, 2); continue
    ok = False
    for msg, a in sorted(btc, key=lambda x: x[1].height):
        try:
            bh = get(f'/block-height/{a.height}').strip(); b = json.loads(get(f'/block/{bh}'))
            bh2 = get(f'/block-height/{a.height}', API2).strip(); b2 = json.loads(get(f'/block/{bh2}', API2))
        except Exception as e:
            print(f'WAIT: {f} block {a.height}: block API unreachable ({type(e).__name__})'); worst = max(worst, 2); break
        if bh2 != bh or b2['merkle_root'] != b['merkle_root']: print(f'REFUSE: {f} block {a.height}: the two block servers disagree'); worst = max(worst, 1); break
        if msg[::-1].hex() != b['merkle_root']: print(f'REFUSE: {f} block {a.height}: commitment does not match the merkle root'); worst = max(worst, 1); break
        if not b['timestamp'] < now: print(f'REFUSE: {f} block {a.height} mined {b["timestamp"]}, not before start {now}'); worst = max(worst, 1); break
        print(f'PASS: {f} block {a.height} merkle root matches, mined {b["timestamp"]} < start {now}'); ok = True; break
sys.exit(worst)
