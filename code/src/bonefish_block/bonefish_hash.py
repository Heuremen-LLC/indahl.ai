"""bonefish_hash.py -- 6 Oct 2026, Wayfinder and Bones. Backward Bonefish on Bitcoin, offline, no wallet, no pool, no money.
Claim under test (Wayfinder): Bitcoin rides The Bonefish, so Bonefish-chosen nonces find low hashes right away.
For each real block header (the public record), the nonce is replaced by Bonefish nonces built from the block BEFORE it
(the outside = previous winning nonce; rules fixed in this file before any hashing), the header is double-SHA256'd exactly as
Bitcoin does, and the hash is read as leading zero bits (Bitcoin's 'how close to the target'). The other ruler: random nonces
on the same header. A block at today's difficulty needs ~79 leading zero bits. Also scored: does any rule land the REAL winning
nonce (circular distance / 2^32; chance = window)."""
import hashlib, json, math, struct, sys, time, urllib.request
import numpy as np
PHI = (1 + 5 ** .5) / 2; M = 2 ** 32
SEVEN = {'12/11': 12/11, '13/12': 13/12, 'phi': PHI, '1/phi': 1/PHI, 'phi*11/12': PHI*11/12, 'pi': math.pi, '1/pi': 1/math.pi,
         '9/12': .75, '10/12': 10/12, '11/12': 11/12, '4/3': 4/3, '3/2': 1.5, '1/ln(phi^2)': 1/math.log(PHI**2), '1.3': 1.3}
CONTROL = {'c1.123': 1.123, 'c1.57': 1.57, 'c1.9': 1.9, 'c0.7': 0.7}
def rules(prev, height):
    r = {f'prev x {k}': int(prev * v) % M for k, v in {**SEVEN, **CONTROL}.items()}
    r['weyl phi*height'] = int(M * ((height * PHI) % 1)); r['weyl pi*height'] = int(M * ((height * math.pi) % 1))
    r['ladder (1/12)(1/phi)^n'] = int(M * (1/12) * (1/PHI) ** (height % 12)) % M
    return r
def zeros(h80):
    d = hashlib.sha256(hashlib.sha256(h80).digest()).digest()[::-1]
    n = int.from_bytes(d, 'big'); return 256 - n.bit_length()
def get(u): return urllib.request.urlopen(u).read()
if __name__ == '__main__':
    B = json.load(open('blocks.json')); N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    rng = np.random.default_rng(20261006); res = {}; rnd = []; real_hit = {}; checks = 0
    for i in range(len(B) - N, len(B)):
        b, p = B[i], B[i - 1]
        hx = get(f"https://mempool.space/api/block-height/{b['height']}").decode(); hdr = bytes.fromhex(get(f'https://mempool.space/api/block/{hx}/header').decode())
        assert zeros(hdr) >= 70, 'header read wrong'; checks += 1
        for k, n in rules(p['nonce'], b['height']).items():
            res.setdefault(k, []).append(zeros(hdr[:76] + struct.pack('<I', n)))
            d = abs(n - b['nonce']); real_hit.setdefault(k, []).append(min(d, M - d) / M)
        for n in rng.integers(0, M, 200): rnd.append(zeros(hdr[:76] + struct.pack('<I', int(n))))
        time.sleep(0.1)
    rnd = np.array(rnd)
    print(f'{N} real blocks ({B[-N]["height"]}-{B[-1]["height"]}), real headers checked (each real hash >= 70 zero bits: {checks}/{N}); target today ~79 bits')
    print(f'RANDOM ruler: {len(rnd)} hashes, mean {rnd.mean():.3f} zero bits, best {rnd.max()}, share >= 8 bits {np.mean(rnd >= 8):.4f} (theory 1/256 = 0.0039)')
    for k, v in res.items():
        v = np.array(v); hd = np.array(real_hit[k])
        print(f'  {k:24} mean {v.mean():.3f} +- {v.std()/len(v)**.5:.3f} | best {v.max():2d} bits | real nonce within 1%: {np.mean(hd < .01):.3f} (chance 0.020) | median dist {np.median(hd):.3f} (chance 0.250)')
