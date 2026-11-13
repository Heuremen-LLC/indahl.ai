import hashlib, struct, math, numpy as np
raw = open('headers.bin', 'rb').read(); N = len(raw) // 80
def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
u = np.empty(N); nonce = np.empty(N); ts = np.empty(N)
for i in range(N):
    h = raw[i * 80:(i + 1) * 80]; bits = struct.unpack('<I', h[72:76])[0]; t = (bits & 0xffffff) << (8 * ((bits >> 24) - 3))
    u[i] = int.from_bytes(dsha(h)[::-1], 'big') / t; nonce[i] = struct.unpack('<I', h[76:80])[0] / 2 ** 32; ts[i] = struct.unpack('<I', h[68:72])[0]
PHI = (1 + 5 ** .5) / 2
S = {'1/12': 1/12, '1/11': 1/11, '1/pi': 1/math.pi, '1/phi^2': 1/PHI**2, '1/phi': 1/PHI, '9/12': .75, 'pi/4': math.pi/4, '10/12': 10/12, '11/12': 11/12, '12/13': 12/13}
print(f'{N} blocks, heights 0-{N - 1}; u mean {u.mean():.5f} (uniform 0.5), u max {u.max():.6f} (must be <= 1)')
w = math.sqrt(0.01 * 0.99 / N)
for nm, x in (('u (hash/target)', u), ('nonce/2^32', nonce)):
    print(f'THE BONEFISH on {nm}: share within +-0.005 of each number (chance 0.0100 +- {w:.5f}):')
    print('   ' + ' | '.join(f'{k} {np.mean(np.abs(x - v) < 0.005):.4f} ({(np.mean(np.abs(x - v) < 0.005) - 0.01) / w:+.1f} w)' for k, v in S.items()))
iv = np.diff(ts) / 600; ep = (np.arange(1, N) % 2016) / 2016; uu = u[1:]
def rank(a): return np.argsort(np.argsort(a)).astype(float)
print('TIME, per era of 100,000 blocks: u deciles (each should be 0.100) | rank corr u~interval | u~epoch position')
for a in range(0, N, 100000):
    b = min(N, a + 100000); x = u[a:b]; dec = np.histogram(x, bins=10, range=(0, 1))[0] / len(x)
    m = slice(max(a - 1, 0), b - 1); ci = np.corrcoef(rank(uu[m]), rank(iv[m]))[0, 1]; ce = np.corrcoef(rank(uu[m]), rank(ep[m]))[0, 1]; wc = 1 / math.sqrt(b - a)
    print(f'   {a:7d}-{b - 1:7d}: deciles {" ".join(f"{d:.3f}" for d in dec)} | {ci:+.4f} ({ci / wc:+.1f} w) | {ce:+.4f} ({ce / wc:+.1f} w)')
