"""fetch_headers.py -- every Bitcoin block header from genesis to the tip, over the Bitcoin P2P protocol (getheaders, 2000 per message), exactly as light wallets
sync. Each header's previous-hash link and its proof of work are checked before it is kept. Writes headers.bin (80 bytes per block, height order)."""
import hashlib, os, random, socket, struct, sys, time
MAGIC = bytes.fromhex('f9beb4d9'); OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'headers.bin')
def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def varint(n): return bytes([n]) if n < 0xfd else (b'\xfd' + struct.pack('<H', n) if n <= 0xffff else b'\xfe' + struct.pack('<I', n))
def read_varint(b, i):
    x = b[i]
    if x < 0xfd: return x, i + 1
    if x == 0xfd: return struct.unpack_from('<H', b, i + 1)[0], i + 3
    if x == 0xfe: return struct.unpack_from('<I', b, i + 1)[0], i + 5
    return struct.unpack_from('<Q', b, i + 1)[0], i + 9
def msg(cmd, payload): return MAGIC + cmd.encode().ljust(12, b'\0') + struct.pack('<I', len(payload)) + dsha(payload)[:4] + payload
def recv_msg(s):
    h = b''
    while len(h) < 24:
        c = s.recv(24 - len(h))
        if not c: raise ConnectionError('closed')
        h += c
    cmd = h[4:16].rstrip(b'\0').decode(); n = struct.unpack('<I', h[16:20])[0]; p = b''
    while len(p) < n:
        c = s.recv(min(65536, n - len(p)))
        if not c: raise ConnectionError('closed')
        p += c
    return cmd, p
def target(bits): return (bits & 0xffffff) << (8 * ((bits >> 24) - 3))
def connect():
    seeds = ['seed.bitcoin.sipa.be', 'dnsseed.bluematt.me', 'seed.bitcoinstats.com', 'seed.bitcoin.jonasschnelli.ch', 'seed.btc.petertodd.net', 'seed.bitcoin.sprovoost.nl']
    ips = []
    for d in seeds:
        try: ips += [a[4][0] for a in socket.getaddrinfo(d, 8333, socket.AF_INET)]
        except Exception: pass
    random.shuffle(ips)
    for ip in ips[:20]:
        try:
            s = socket.create_connection((ip, 8333), timeout=20)
            addr = struct.pack('<Q', 0) + b'\0' * 10 + b'\xff\xff' + socket.inet_aton(ip) + struct.pack('>H', 8333)
            ver = struct.pack('<iQq', 70016, 0, int(time.time())) + addr + struct.pack('<Q', 0) + b'\0' * 16 + struct.pack('>H', 0) + struct.pack('<Q', random.getrandbits(64)) + varint(14) + b'/bonefish:0.1/' + struct.pack('<i', 0) + b'\0'
            s.sendall(msg('version', ver)); got_ver = got_ack = False
            while not (got_ver and got_ack):
                cmd, p = recv_msg(s)
                if cmd == 'version': got_ver = True; s.sendall(msg('verack', b''))
                elif cmd == 'verack': got_ack = True
            print('connected', ip, flush=True); return s
        except Exception as e: print('peer', ip, 'failed:', e, flush=True)
    raise SystemExit('no peer')
GENESIS = bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c')
heads = [GENESIS]
if os.path.exists(OUT):
    raw = open(OUT, 'rb').read(); heads = [raw[i:i + 80] for i in range(0, len(raw), 80)]
assert dsha(heads[0])[::-1].hex() == '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
s = connect(); last = time.time()
while True:
    loc = b''.join(dsha(heads[i])[:32] for i in (len(heads) - 1,))
    s.sendall(msg('getheaders', struct.pack('<I', 70016) + varint(1) + loc + b'\0' * 32))
    while True:
        cmd, p = recv_msg(s)
        if cmd == 'ping': s.sendall(msg('pong', p))
        elif cmd == 'headers': break
    n, i = read_varint(p, 0); new = 0
    for _ in range(n):
        h = p[i:i + 80]; i += 80; _, i = read_varint(p, i)
        if h[4:36] != dsha(heads[-1]): raise SystemExit(f'broken link at height {len(heads)}')
        bits = struct.unpack('<I', h[72:76])[0]
        if int.from_bytes(dsha(h)[::-1], 'big') > target(bits): raise SystemExit(f'bad proof of work at height {len(heads)}')
        heads.append(h); new += 1
    if time.time() - last > 20 or new < 2000:
        open(OUT, 'wb').write(b''.join(heads)); last = time.time(); print('height', len(heads) - 1, flush=True)
    if new < 2000: break
print('done: tip height', len(heads) - 1)
