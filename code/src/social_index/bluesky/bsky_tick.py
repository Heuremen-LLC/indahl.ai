#!/usr/bin/env python3
"""bsky_tick.py: BLUESKY labels, a section of the SOCIAL desk (HERMES). See PLAN.md.
Replays the signed label stream of Bluesky's moderation service (keyless) into data/labels.sqlite from the highest stored seq,
checks signatures on a deterministic sample, counts 2024 and 2025 under the readings fixed in PLAN.md, and writes
data/bsky.json, summary_bluesky.json and section_bluesky.html. Read-only. Python standard library only. Installs no timer.
  python3 -I bsky_tick.py              fetch to the live head, verify, count, render
  python3 -I bsky_tick.py --no-fetch   verify, count and render from the store
  python3 -I bsky_tick.py --selftest   codec, signature and planted-world checks only"""
import os, sys, json, time, socket, ssl, base64, struct, hashlib, sqlite3, subprocess, tempfile, calendar, bisect, re, html
import datetime as D, collections as C, urllib.request

H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K

HOST = 'mod.bsky.app'; XRPC = '/xrpc/com.atproto.label.subscribeLabels'
LABELER = 'did:plc:ar7c4by46qjdydhdevvrndac'
UA = 'heuremen-social/0.1 (+https://indahl.ai/social; read-only label count)'
DB = 'data/labels.sqlite'
TAKEDOWN_VALS = ('!takedown', '!suspend')
WINDOW = 21            # rolling window (rows) for the in-order test, PLAN Addendum 1
ORDER_TOL = 86400000   # 24 hours in ms
DAY = 86400000; PAC = 8 * 3600000
SAMPLE_CUT = 2 ** 32 // 1000
REPORT_URL = 'https://bsky.social/about/blog/01-29-2026-transparency-report-2025'
OVERVIEW_URL = 'https://bsky.social/about/blog/01-29-2026-transparency-report-overview'
OZONE_URL = 'https://github.com/bluesky-social/atproto/blob/1ec24ff2a123e3ea9d125d0dea950a8ee3adfca4/packages/ozone/src/mod-service/index.ts#L1627-L1652'

# ---------------------------------------------------------------- DAG-CBOR
def _head(b, i):
    ib = b[i]; mt = ib >> 5; ai = ib & 31; i += 1
    if ai < 24: return mt, ai, i
    if ai == 24: return mt, b[i], i + 1
    if ai == 25: return mt, int.from_bytes(b[i:i + 2], 'big'), i + 2
    if ai == 26: return mt, int.from_bytes(b[i:i + 4], 'big'), i + 4
    if ai == 27: return mt, int.from_bytes(b[i:i + 8], 'big'), i + 8
    raise ValueError('cbor: unsupported additional info %d' % ai)

def cbor_decode(b, i=0):
    ai = b[i] & 31; mt, val, i = _head(b, i)
    if mt == 0: return val, i
    if mt == 1: return -1 - val, i
    if mt == 2: return bytes(b[i:i + val]), i + val
    if mt == 3: return bytes(b[i:i + val]).decode('utf-8'), i + val
    if mt == 4:
        out = []
        for _ in range(val):
            x, i = cbor_decode(b, i); out.append(x)
        return out, i
    if mt == 5:
        out = {}
        for _ in range(val):
            k, i = cbor_decode(b, i); v, i = cbor_decode(b, i); out[k] = v
        return out, i
    if mt == 6:
        x, i = cbor_decode(b, i); return ('tag', val, x), i
    if ai == 20: return False, i
    if ai == 21: return True, i
    if ai in (22, 23): return None, i
    if ai == 26: return struct.unpack('>f', val.to_bytes(4, 'big'))[0], i
    if ai == 27: return struct.unpack('>d', val.to_bytes(8, 'big'))[0], i
    raise ValueError('cbor: unsupported simple value %d' % ai)

def _hd(mt, n):
    if n < 24: return bytes([mt << 5 | n])
    if n < 256: return bytes([mt << 5 | 24, n])
    if n < 65536: return bytes([mt << 5 | 25]) + n.to_bytes(2, 'big')
    if n < 4294967296: return bytes([mt << 5 | 26]) + n.to_bytes(4, 'big')
    return bytes([mt << 5 | 27]) + n.to_bytes(8, 'big')

def cbor_encode(x):
    """Canonical DAG-CBOR: shortest heads, map keys ordered by encoded length then bytes."""
    if x is True: return b'\xf5'
    if x is False: return b'\xf4'
    if x is None: return b'\xf6'
    if isinstance(x, int): return _hd(0, x) if x >= 0 else _hd(1, -1 - x)
    if isinstance(x, bytes): return _hd(2, len(x)) + x
    if isinstance(x, str): e = x.encode('utf-8'); return _hd(3, len(e)) + e
    if isinstance(x, list): return _hd(4, len(x)) + b''.join(cbor_encode(v) for v in x)
    if isinstance(x, dict):
        ks = sorted(x, key=lambda k: (len(k.encode('utf-8')), k.encode('utf-8')))
        return _hd(5, len(ks)) + b''.join(cbor_encode(k) + cbor_encode(x[k]) for k in ks)
    if isinstance(x, tuple) and len(x) == 3 and x[0] == 'tag': return _hd(6, x[1]) + cbor_encode(x[2])
    raise TypeError('cbor: cannot encode %s' % type(x).__name__)

def parse_frame(m):
    """One websocket message: header then body. Returns (header, seq, [(label, raw label bytes)], body or None)."""
    h, i = cbor_decode(m, 0)
    if not isinstance(h, dict) or h.get('op') != 1 or h.get('t') != '#labels':
        body, _ = cbor_decode(m, i); return h, None, [], body
    mt, n, i = _head(m, i)
    if mt != 5: raise ValueError('body is not a map')
    seq = None; labels = []
    for _ in range(n):
        k, i = cbor_decode(m, i)
        if k == 'labels':
            mt2, cnt, i = _head(m, i)
            if mt2 != 4: raise ValueError('labels is not an array')
            for _ in range(cnt):
                s = i; L, i = cbor_decode(m, i); labels.append((L, bytes(m[s:i])))
        else:
            v, i = cbor_decode(m, i)
            if k == 'seq': seq = v
    return h, seq, labels, None

# ---------------------------------------------------------------- websocket (client side of RFC 6455, enough for this stream)
class WS:
    def __init__(self, host, path, ua, timeout=30):
        raw = socket.create_connection((host, 443), timeout=timeout)
        self.s = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ('GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\n'
               'Sec-WebSocket-Version: 13\r\nUser-Agent: %s\r\n\r\n') % (path, host, key, ua)
        self.s.sendall(req.encode())
        self.f = self.s.makefile('rb', buffering=1 << 20)
        status = self.f.readline().decode('latin1').strip()
        while True:
            l = self.f.readline()
            if l in (b'\r\n', b'\n', b''): break
        if ' 101 ' not in status + ' ': raise ConnectionError('handshake: ' + status)
    def _read(self, n):
        d = self.f.read(n)
        if d is None or len(d) < n: raise ConnectionError('socket closed')
        return d
    def _send(self, op, payload=b''):
        mask = os.urandom(4); n = len(payload)
        hdr = bytes([0x80 | op]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + n.to_bytes(2, 'big'))
        self.s.sendall(hdr + mask + bytes(c ^ mask[i % 4] for i, c in enumerate(payload)))
    def recv(self):
        buf = []
        while True:
            h = self._read(2); fin = h[0] & 0x80; op = h[0] & 0x0F; n = h[1] & 0x7F
            if n == 126: n = int.from_bytes(self._read(2), 'big')
            elif n == 127: n = int.from_bytes(self._read(8), 'big')
            if h[1] & 0x80:
                mk = self._read(4); data = bytes(c ^ mk[i % 4] for i, c in enumerate(self._read(n)))
            else: data = self._read(n)
            if op == 0x9: self._send(0xA, data); continue
            if op == 0xA: continue
            if op == 0x8:
                raise ConnectionError('close frame %s %r' % (int.from_bytes(data[:2], 'big') if len(data) >= 2 else None, data[2:200]))
            buf.append(data)
            if fin: return b''.join(buf)
    def close(self):
        try: self._send(0x8, (1000).to_bytes(2, 'big'))
        except Exception: pass
        try: self.s.close()
        except Exception: pass

# ---------------------------------------------------------------- ECDSA verification (secp256k1 and P-256), pure Python
CURVES = {
    'secp256k1': dict(p=2 ** 256 - 2 ** 32 - 977, a=0, b=7, n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
                      G=(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)),
    'p256': dict(p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF, a=-3, b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
                 n=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
                 G=(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296, 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5))}

def _jdbl(P, c):
    X, Y, Z = P; p = c['p']
    if Z == 0 or Y == 0: return (0, 1, 0)
    YY = Y * Y % p; S = 4 * X * YY % p; ZZ = Z * Z % p
    M = (3 * X * X + c['a'] * ZZ * ZZ) % p
    X3 = (M * M - 2 * S) % p
    return (X3, (M * (S - X3) - 8 * YY * YY) % p, 2 * Y * Z % p)

def _jadd(P, Q, c):
    if P[2] == 0: return Q
    if Q[2] == 0: return P
    p = c['p']; X1, Y1, Z1 = P; X2, Y2, Z2 = Q
    Z1Z1 = Z1 * Z1 % p; Z2Z2 = Z2 * Z2 % p; U1 = X1 * Z2Z2 % p; U2 = X2 * Z1Z1 % p
    S1 = Y1 * Z2 * Z2Z2 % p; S2 = Y2 * Z1 * Z1Z1 % p
    if U1 == U2: return _jdbl(P, c) if S1 == S2 else (0, 1, 0)
    Hh = (U2 - U1) % p; R = (S2 - S1) % p; HH = Hh * Hh % p; HHH = Hh * HH % p; V = U1 * HH % p
    X3 = (R * R - HHH - 2 * V) % p
    return (X3, (R * (V - X3) - S1 * HHH) % p, Hh * Z1 * Z2 % p)

def ecdsa_verify(curve, Q, z, r, s):
    c = CURVES[curve]; n = c['n']
    if not (1 <= r < n and 1 <= s < n): return False
    w = pow(s, -1, n); u1 = z * w % n; u2 = r * w % n
    G = (c['G'][0], c['G'][1], 1); Qj = (Q[0], Q[1], 1); GQ = _jadd(G, Qj, c); R = (0, 1, 0)
    for i in range(max(u1.bit_length(), u2.bit_length()) - 1, -1, -1):
        R = _jdbl(R, c); b1 = (u1 >> i) & 1; b2 = (u2 >> i) & 1
        if b1 and b2: R = _jadd(R, GQ, c)
        elif b1: R = _jadd(R, G, c)
        elif b2: R = _jadd(R, Qj, c)
    if R[2] == 0: return False
    p = c['p']; zi = pow(R[2], -1, p)
    return (R[0] * zi * zi % p) % n == r

B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58decode(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return b'\x00' * (len(s) - len(s.lstrip('1'))) + raw

def decode_multikey(mb):
    """did:key or multibase public key -> (curve, (x, y))."""
    if mb.startswith('did:key:'): mb = mb[8:]
    if not mb.startswith('z'): raise ValueError('not base58btc multibase')
    b = b58decode(mb[1:])
    if b[:2] == b'\xe7\x01': curve = 'secp256k1'
    elif b[:2] == b'\x80\x24': curve = 'p256'
    else: raise ValueError('unknown key type')
    key = b[2:]; c = CURVES[curve]; p = c['p']
    if len(key) == 33 and key[0] in (2, 3):
        x = int.from_bytes(key[1:], 'big'); y2 = (x ** 3 + c['a'] * x + c['b']) % p; y = pow(y2, (p + 1) // 4, p)
        if y * y % p != y2: raise ValueError('point not on curve')
        if (y & 1) != (key[0] & 1): y = p - y
    elif len(key) == 65 and key[0] == 4: x = int.from_bytes(key[1:33], 'big'); y = int.from_bytes(key[33:], 'big')
    else: raise ValueError('bad key length')
    return curve, (x, y)

def label_digest(L):
    return hashlib.sha256(cbor_encode({k: v for k, v in L.items() if k != 'sig'})).digest()

def verify_label(L, keys):
    """keys: [(name, curve, point)]. Returns (ok, key name, low_s). ok None when the label carries no 64-byte signature."""
    sig = L.get('sig')
    if not isinstance(sig, bytes) or len(sig) != 64: return None, None, None
    z = int.from_bytes(label_digest(L), 'big'); r = int.from_bytes(sig[:32], 'big'); s = int.from_bytes(sig[32:], 'big')
    for name, curve, Q in keys:
        if ecdsa_verify(curve, Q, z, r, s): return True, name, s <= CURVES[curve]['n'] // 2
    return False, None, s <= CURVES[keys[0][1]]['n'] // 2

def _dlen(n): return bytes([n]) if n < 128 else (bytes([0x81, n]) if n < 256 else bytes([0x82]) + n.to_bytes(2, 'big'))
def _dseq(b): return b'\x30' + _dlen(len(b)) + b
def _dint(v): b = v.to_bytes(v.bit_length() // 8 + 1, 'big'); return b'\x02' + _dlen(len(b)) + b

def openssl_verify(curve, Q, msg, sig):
    """Independent check with the openssl command line (ECDSA over SHA-256). True, False, or None when openssl is missing."""
    oid = bytes.fromhex('06052b8104000a') if curve == 'secp256k1' else bytes.fromhex('06082a8648ce3d030107')
    pt = b'\x04' + Q[0].to_bytes(32, 'big') + Q[1].to_bytes(32, 'big')
    der = _dseq(_dseq(bytes.fromhex('06072a8648ce3d0201') + oid) + b'\x03' + _dlen(len(pt) + 1) + b'\x00' + pt)
    pem = '-----BEGIN PUBLIC KEY-----\n' + base64.encodebytes(der).decode() + '-----END PUBLIC KEY-----\n'
    exe = next((e for e in ('/opt/homebrew/bin/openssl', '/usr/bin/openssl') if os.path.exists(e)), None)
    if not exe: return None
    with tempfile.TemporaryDirectory() as d:
        open(d + '/k.pem', 'w').write(pem); open(d + '/m.bin', 'wb').write(msg)
        open(d + '/s.der', 'wb').write(_dseq(_dint(int.from_bytes(sig[:32], 'big')) + _dint(int.from_bytes(sig[32:], 'big'))))
        p = subprocess.run([exe, 'dgst', '-sha256', '-verify', d + '/k.pem', '-signature', d + '/s.der', d + '/m.bin'], capture_output=True, text=True)
    return 'Verified OK' in p.stdout

# ---------------------------------------------------------------- time helpers
def ms_utc(y, m=1, d=1, h=0, mi=0, s=0): return calendar.timegm((y, m, d, h, mi, s)) * 1000
YS = {y: ms_utc(y) for y in range(2022, 2030)}
_TSRE = re.compile(r'^(\d{4})-(\d\d)-(\d\d)[T ](\d\d):(\d\d):(\d\d)(?:\.(\d+))?(Z|[+-]\d\d:?\d\d)?$')

def ts_ms(s):
    if not isinstance(s, str): return None
    try:
        d = D.datetime.fromisoformat(s)
        if d.tzinfo is None: d = d.replace(tzinfo=D.timezone.utc)
        return calendar.timegm(d.utctimetuple()) * 1000 + d.microsecond // 1000
    except ValueError:
        m = _TSRE.match(s)
        if not m: return None
        y, mo, dd, hh, mi, ss, fr, tz = m.groups()
        t = calendar.timegm((int(y), int(mo), int(dd), int(hh), int(mi), int(ss))) * 1000 + (int((fr + '000')[:3]) if fr else 0)
        if tz and tz != 'Z':
            sign = 1 if tz[0] == '+' else -1; tz = tz[1:].replace(':', ''); t -= sign * (int(tz[:2]) * 60 + int(tz[2:])) * 60000
        return t

def year_of(t):
    if t is None: return None
    for y in range(2029, 2021, -1):
        if t >= YS[y]: return y
    return D.datetime.fromtimestamp(t / 1000, D.timezone.utc).year

TIDV = {c: i for i, c in enumerate('234567abcdefghijklmnopqrstuvwxyz')}
def tid_ms(rkey):
    """Record keys that are timestamp identifiers carry their creation time. Returns ms or None."""
    if not rkey or len(rkey) != 13: return None
    n = 0
    for ch in rkey:
        v = TIDV.get(ch)
        if v is None: return None
        n = n * 32 + v
    if n >> 63: return None
    t = (n >> 10) // 1000
    return t if YS[2022] - 5 * 365 * DAY <= t < YS[2029] + 30 * 365 * DAY else None

def fmt_day(t): return time.strftime('%Y-%m-%d', time.gmtime(t / 1000))

# ---------------------------------------------------------------- store
SCHEMA = '''
CREATE TABLE IF NOT EXISTS label(seq INTEGER PRIMARY KEY, did INTEGER NOT NULL, coll INTEGER NOT NULL, rkey TEXT NOT NULL, cidh INTEGER NOT NULL,
  val INTEGER NOT NULL, neg INTEGER NOT NULL, cts INTEGER, exp INTEGER, src INTEGER NOT NULL, ver INTEGER, sig INTEGER NOT NULL,
  sup INTEGER NOT NULL DEFAULT 0, run INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS dids(id INTEGER PRIMARY KEY, s TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS colls(id INTEGER PRIMARY KEY, s TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS vals(id INTEGER PRIMARY KEY, s TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS srcs(id INTEGER PRIMARY KEY, s TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS sample(seq INTEGER PRIMARY KEY, raw BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS sigcheck(seq INTEGER PRIMARY KEY, ok INTEGER, keyname TEXT, low_s INTEGER, reencode_equal INTEGER, checked REAL);
CREATE TABLE IF NOT EXISTS odd(seq INTEGER, kind TEXT, detail TEXT, run INTEGER);
CREATE TABLE IF NOT EXISTS runs(run INTEGER PRIMARY KEY, started REAL, ended REAL, cursor_from INTEGER, last_seq INTEGER, frames INTEGER,
  reconnects INTEGER, stop TEXT, superseded INTEGER);
'''

def open_db(path=DB):
    con = sqlite3.connect(path, timeout=60)
    con.execute('PRAGMA journal_mode=WAL'); con.execute('PRAGMA synchronous=NORMAL'); con.execute('PRAGMA temp_store=FILE')
    con.executescript(SCHEMA)
    con.execute("INSERT OR IGNORE INTO colls(id, s) VALUES (0, '(account)'), (-1, '(other uri form)')")
    con.commit(); return con

class Interner:
    def __init__(self, con, table):
        self.con, self.t = con, table
        self.m = {s: i for i, s in con.execute('SELECT id, s FROM %s' % table)}
        self.next = max([i for i in self.m.values()] + [0]) + 1; self.new = []
    def __call__(self, s):
        i = self.m.get(s)
        if i is None:
            i = self.next; self.next += 1; self.m[s] = i; self.new.append((i, s))
        return i
    def flush(self):
        if self.new: self.con.executemany('INSERT INTO %s(id, s) VALUES (?, ?)' % self.t, self.new); self.new = []

def cid_hash(cid):
    return int.from_bytes(hashlib.blake2b(cid.encode(), digest_size=8).digest(), 'big', signed=True) if cid else 0

def sampled(seq): return int.from_bytes(hashlib.blake2b(seq.to_bytes(8, 'big'), digest_size=8).digest()[:4], 'big') < SAMPLE_CUT

def row_from_label(seq, L, run, I, odd):
    uri = L.get('uri') or ''
    if uri.startswith('did:'): did, coll, rkey = I['dids'](uri), 0, ''
    elif uri.startswith('at://'):
        parts = uri[5:].split('/', 2)
        did = I['dids'](parts[0]); coll = I['colls'](parts[1] if len(parts) > 1 and parts[1] else '(repo)'); rkey = parts[2] if len(parts) > 2 else ''
    else:
        did, coll, rkey = I['dids'](uri), -1, ''; odd.append((seq, 'uri form', uri[:12], run))
    cts = ts_ms(L.get('cts'))
    if cts is None: odd.append((seq, 'cts unreadable', repr(L.get('cts'))[:40], run))
    exp = ts_ms(L.get('exp')) if L.get('exp') is not None else None
    return (seq, did, coll, rkey, cid_hash(L.get('cid')), I['vals'](L.get('val') or ''), 1 if L.get('neg') is True else 0, cts, exp,
            I['srcs'](L.get('src') or ''), L.get('ver'), 1 if isinstance(L.get('sig'), bytes) else 0, 0, run)

def mark_superseded(con, run, log):
    """A key (src, uri, cid, val) served again at a higher seq marks the older stored row superseded (sup = new seq)."""
    con.execute('CREATE INDEX IF NOT EXISTS label_key ON label(did, coll, rkey, cidh, val, src)'); con.commit()
    new = con.execute('SELECT COUNT(*) FROM label WHERE run = ?', (run,)).fetchone()[0]; marked = 0; upd = []
    broken = con.execute('SELECT COUNT(*) FROM runs WHERE run < ? AND ended IS NULL', (run,)).fetchone()[0]
    if new > 1000000 or broken:
        prev = None; group = []
        for r in con.execute('SELECT did, coll, rkey, cidh, val, src, seq FROM label INDEXED BY label_key WHERE sup = 0 ORDER BY did, coll, rkey, cidh, val, src, seq'):
            k = r[:6]
            if k != prev:
                if len(group) > 1: upd += [(group[-1], s) for s in group[:-1]]
                prev = k; group = []
            group.append(r[6])
        if len(group) > 1: upd += [(group[-1], s) for s in group[:-1]]
    else:
        for (seq, did, coll, rkey, cidh, val, src) in con.execute('SELECT seq, did, coll, rkey, cidh, val, src FROM label WHERE run = ?', (run,)).fetchall():
            for (old,) in con.execute('SELECT seq FROM label WHERE did=? AND coll=? AND rkey=? AND cidh=? AND val=? AND src=? AND seq<? AND sup=0', (did, coll, rkey, cidh, val, src, seq)):
                upd.append((seq, old))
    for i in range(0, len(upd), 50000):
        con.executemany('UPDATE label SET sup = ? WHERE seq = ?', upd[i:i + 50000]); marked += len(upd[i:i + 50000])
    con.commit(); log('superseded marked: %d (new rows this run %d)' % (marked, new)); return marked

def fetch(con, log, limit=None, max_reconnects=60):
    I = {t: Interner(con, t) for t in ('dids', 'colls', 'vals', 'srcs')}
    run = (con.execute('SELECT MAX(run) FROM runs').fetchone()[0] or 0) + 1; started = time.time()
    last = con.execute('SELECT MAX(seq) FROM label').fetchone()[0] or 0; cursor_from = last
    con.execute('INSERT INTO runs(run, started, cursor_from) VALUES (?, ?, ?)', (run, started, cursor_from)); con.commit()
    frames = 0; reconnects = 0; buf = []; samp = []; odd = []; stop = None; last_cts = None; t_log = time.time(); f_log = 0
    def flush():
        for i in I.values(): i.flush()
        if buf: con.executemany('INSERT INTO label VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', buf)
        if samp: con.executemany('INSERT OR REPLACE INTO sample VALUES (?, ?)', samp)
        if odd: con.executemany('INSERT INTO odd VALUES (?, ?, ?, ?)', odd)
        con.execute('UPDATE runs SET last_seq = ?, frames = ?, reconnects = ? WHERE run = ?', (last, frames, reconnects, run)); con.commit()
        buf.clear(); samp.clear(); odd.clear()
    while stop is None:
        ws = None
        try:
            ws = WS(HOST, XRPC + '?cursor=%d' % last, UA, timeout=30)
            while True:
                m = ws.recv()
                try: h, seq, labels, body = parse_frame(m)
                except Exception as e:
                    odd.append((last, 'frame unreadable', '%s %s' % (type(e).__name__, m[:48].hex()), run)); continue
                if seq is None:
                    odd.append((last, 'frame', json.dumps([h, body], default=str)[:300], run))
                    if isinstance(body, dict) and body.get('error') == 'FutureCursor': stop = 'future cursor'; break
                    if isinstance(h, dict) and h.get('op') == -1: raise ConnectionError('error frame %r' % (body,))
                    continue
                if seq <= last: odd.append((seq, 'seq not increasing', str(last), run)); continue
                if len(labels) != 1: odd.append((seq, 'labels per frame', str(len(labels)), run))
                for L, raw in labels:
                    try: buf.append(row_from_label(seq, L, run, I, odd))
                    except Exception as e:
                        odd.append((seq, 'label unreadable', '%s %s' % (type(e).__name__, raw[:48].hex()), run)); continue
                    if sampled(seq): samp.append((seq, raw))
                    last_cts = ts_ms(L.get('cts')) or last_cts
                last = seq; frames += 1
                if len(buf) >= 20000: flush()
                if frames - f_log >= 500000:
                    now = time.time(); log('seq %d  cts %s  frames %d  %.0f per s' % (last, time.strftime('%Y-%m-%d %H:%M', time.gmtime((last_cts or 0) / 1000)), frames, (frames - f_log) / max(1e-6, now - t_log))); t_log, f_log = now, frames
                nowm = time.time() * 1000
                if last_cts and nowm - 60000 <= last_cts <= nowm + 60000: stop = 'live head'; break
                if limit and frames >= limit: stop = 'limit'; break
        except socket.timeout:
            nowm = time.time() * 1000
            if last_cts and nowm - 600000 <= last_cts <= nowm + 60000: stop = 'quiet at head'
            else: reconnects += 1; log('timeout far from head at seq %d, reconnecting' % last)
        except (ConnectionError, OSError, ssl.SSLError, ValueError) as e:
            reconnects += 1; log('connection: %s at seq %d (reconnect %d)' % (str(e)[:160], last, reconnects))
            if reconnects > max_reconnects: stop = 'too many reconnects'
            else: time.sleep(min(60, 2 * reconnects))
        finally:
            if ws: ws.close()
            flush()
    sup = mark_superseded(con, run, log)
    con.execute('UPDATE runs SET ended = ?, stop = ?, superseded = ? WHERE run = ?', (time.time(), stop, sup, run)); con.commit()
    log('fetch done: %d frames, last seq %d, stop: %s, reconnects %d' % (frames, last, stop, reconnects))
    return dict(run=run, frames=frames, last_seq=last, stop=stop, reconnects=reconnects, cursor_from=cursor_from)

# ---------------------------------------------------------------- signatures
def fetch_keys(log):
    keys = []; doc = audit = None
    for url, fn in (('https://plc.directory/' + LABELER, 'data/did_doc.json'), ('https://plc.directory/' + LABELER + '/log/audit', 'data/did_audit.json')):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                d = json.loads(r.read()); json.dump(d, open(fn, 'w'), indent=1)
        except Exception as e:
            log('plc read failed (%s), using stored copy' % e); d = json.load(open(fn)) if os.path.exists(fn) else None
        if fn.endswith('doc.json'): doc = d
        else: audit = d
    for vm in (doc or {}).get('verificationMethod', []):
        if vm['id'].endswith('#atproto_label'): keys.insert(0, ('#atproto_label (current DID document)', *decode_multikey(vm['publicKeyMultibase'])))
        elif vm['id'].endswith('#atproto'): keys.append(('#atproto (current DID document)', *decode_multikey(vm['publicKeyMultibase'])))
    seen = {k[2] for k in keys}
    for e in (audit or []):
        for name, dk in ((e.get('operation') or {}).get('verificationMethods') or {}).items():
            c, Q = decode_multikey(dk)
            if Q not in seen: keys.append(('%s (PLC log %s)' % (name, e.get('createdAt', '')[:10]), c, Q)); seen.add(Q)
    return keys

def verify_samples(con, keys, log):
    """Verifies sampled labels not yet checked. Returns the signature summary and the known-good result."""
    todo = con.execute('SELECT s.seq, s.raw FROM sample s LEFT JOIN sigcheck c ON c.seq = s.seq WHERE c.seq IS NULL ORDER BY s.seq').fetchall()
    out = []
    for seq, raw in todo:
        L, _ = cbor_decode(raw, 0); ok, kn, low = verify_label(L, keys)
        out.append((seq, None if ok is None else int(ok), kn, None if low is None else int(low), int(cbor_encode(L) == raw), time.time()))
    con.executemany('INSERT OR REPLACE INTO sigcheck VALUES (?,?,?,?,?,?)', out); con.commit()
    log('signatures checked this run: %d' % len(out))
    # known-good: a passing label, the same label with one byte of its value changed, and openssl on five labels
    kg = dict(passed=False, detail=[])
    rows = con.execute('SELECT s.seq, s.raw FROM sample s JOIN sigcheck c ON c.seq = s.seq WHERE c.ok = 1 ORDER BY s.seq LIMIT 5').fetchall()
    if rows:
        L0, _ = cbor_decode(rows[0][1], 0); t = dict(L0); v = t['val'].encode(); t['val'] = (bytes([v[0] ^ 1]) + v[1:]).decode('latin1')
        tampered_fails = verify_label(t, keys)[0] is False
        name, curve, Q = keys[0]; ossl = []
        for seq, raw in rows:
            L, _ = cbor_decode(raw, 0); ossl.append(openssl_verify(curve, Q, cbor_encode({k: x for k, x in L.items() if k != 'sig'}), L['sig']))
        ossl_tampered = openssl_verify(curve, Q, cbor_encode({k: x for k, x in t.items() if k != 'sig'}), t['sig'])
        kg['passed'] = bool(tampered_fails and all(x is True for x in ossl) and ossl_tampered is False)
        kg['detail'] = ['first sampled label passes (seq %d)' % rows[0][0], 'one byte of its value changed: %s' % ('fails' if tampered_fails else 'PASSES, check broken'),
                        'openssl on %d labels: %s' % (len(ossl), ', '.join('pass' if x else ('fail' if x is False else 'missing') for x in ossl)), 'openssl on the changed label: %s' % ('fails' if ossl_tampered is False else ossl_tampered)]
    n, ok, low, uns, reenc = con.execute('SELECT COUNT(*), SUM(ok = 1), SUM(low_s = 1), SUM(ok IS NULL), SUM(reencode_equal) FROM sigcheck').fetchone()
    bykey = dict(con.execute('SELECT keyname, COUNT(*) FROM sigcheck WHERE ok = 1 GROUP BY keyname').fetchall())
    yr = con.execute('''SELECT l.cts, c.ok FROM sigcheck c JOIN label l ON l.seq = c.seq''').fetchall()
    by_year = C.defaultdict(lambda: [0, 0])
    for cts, k in yr:
        y = year_of(cts); by_year[y][0] += 1; by_year[y][1] += 1 if k == 1 else 0
    return dict(sampled=n or 0, passed=ok or 0, low_s=low or 0, unsigned=uns or 0, reencoded_identical=reenc or 0, by_key=bykey,
                by_year={str(y): dict(sampled=a, passed=b) for y, (a, b) in sorted(by_year.items(), key=lambda kv: kv[0] or 0)},
                key_used=keys[0][0] if keys else None, known_good=kg)

# ---------------------------------------------------------------- counting (PLAN rules R1 to R7)
def analyze(con, labeler=LABELER, now_ms=None, years=(2024, 2025), window=WINDOW):
    now_ms = now_ms or int(time.time() * 1000)
    V = {s: i for i, s in con.execute('SELECT id, s FROM vals')}; VN = {i: s for s, i in V.items()}
    lab = con.execute('SELECT id FROM srcs WHERE s = ?', (labeler,)).fetchone(); lab = lab[0] if lab else -999
    cU = C.Counter(); cP = C.Counter(); c5 = C.Counter(); cE = C.Counter(); cX = C.Counter(); daily = C.Counter(); ooo = C.Counter()
    first_inorder = {}; other_src = 0; nrows = 0; nocts = 0
    import array
    SQ = array.array('q'); TS = array.array('q')
    for seq, coll, rkey, val, neg, cts, exp, src in con.execute('SELECT seq, coll, rkey, val, neg, cts, exp, src FROM label WHERE sup = 0 ORDER BY seq'):
        if src != lab: other_src += 1; continue
        if cts is None: nocts += 1; continue
        nrows += 1; a = 'a' if coll == 0 else ('c' if coll > 0 else 'o'); y = year_of(cts)
        cU[(y, val, neg, a)] += 1; cP[(year_of(cts - PAC), val, neg, a)] += 1
        daily[(cts // DAY, neg, VN.get(val) in TAKEDOWN_VALS)] += 1
        if exp is not None: cE[(y, val)] += 1; cX[(y, val)] += 1 if exp < now_ms else 0
        if neg:
            for Y in years:
                if cts >= YS[Y + 1]:
                    t = tid_ms(rkey) if a == 'c' else None
                    if t is None or t < YS[Y + 1]: c5[(Y, val, a)] += 1
        SQ.append(seq); TS.append(cts)
    # in-order test: a row is in order when its cts is within 24 hours of the median cts of the rows from i - half to i + half (truncated at the ends)
    n = len(TS); half = window // 2; srt = sorted(TS[0:min(n, half + 1)])
    for i in range(n):
        if i > 0:
            j = i + half
            if j < n: bisect.insort(srt, TS[j])
            k = i - half - 1
            if k >= 0: srt.pop(bisect.bisect_left(srt, TS[k]))
        cts = TS[i]; med = srt[len(srt) // 2]
        if abs(cts - med) <= ORDER_TOL:
            d = cts // DAY
            if d not in first_inorder: first_inorder[d] = SQ[i]
        else: ooo[year_of(cts)] += 1
    del SQ, TS, srt
    # S(day start): smallest in-order seq at or after the day, a suffix minimum over days
    S = {}; run_min = None
    for d in sorted(first_inorder, reverse=True):
        run_min = first_inorder[d] if run_min is None else min(run_min, first_inorder[d]); S[d] = run_min
    days = sorted(S)
    def S_at(t):
        d = t // DAY; i = bisect.bisect_left(days, d)
        return S[days[i]] if i < len(days) else None
    head_seq = con.execute('SELECT MAX(seq) FROM label').fetchone()[0] or 0
    c3 = {}; G = {}; rng = {}
    for Y in years:
        lo = S_at(YS[Y]); hi = S_at(YS[Y + 1]) or (head_seq + 1)
        rng[Y] = (lo, hi)
        if lo is None: c3[Y] = C.Counter(); G[Y] = 0; continue
        c3[Y] = C.Counter({(v, n, a): k for v, n, a, k in con.execute(
            "SELECT val, neg, CASE WHEN coll = 0 THEN 'a' WHEN coll > 0 THEN 'c' ELSE 'o' END, COUNT(*) FROM label WHERE sup = 0 AND src = ? AND seq >= ? AND seq < ? GROUP BY 1, 2, 3", (lab, lo, hi))})
        served_any = con.execute('SELECT COUNT(*) FROM label WHERE sup = 0 AND seq >= ? AND seq < ?', (lo, hi)).fetchone()[0]
        G[Y] = (hi - lo) - served_any
    # R6: distinct (uri, val) among R1 rows, from a pass in key order
    c6 = C.Counter(); prev = None; seen = set()
    con.execute('CREATE INDEX IF NOT EXISTS label_key ON label(did, coll, rkey, cidh, val, src)')
    for did, coll, rkey, val, cts in con.execute('SELECT did, coll, rkey, val, cts FROM label INDEXED BY label_key WHERE sup = 0 AND neg = 0 AND src = ? ORDER BY did, coll, rkey', (lab,)):
        k = (did, coll, rkey)
        if k != prev: prev = k; seen = set()
        y = year_of(cts)
        if y in years and (val, y) not in seen:
            seen.add((val, y)); c6[(y, val, 'a' if coll == 0 else ('c' if coll > 0 else 'o'))] += 1
    # sequence numbers used and served per day, for the live series
    series = []
    for i, d in enumerate(days):
        nxt = S[days[i + 1]] if i + 1 < len(days) else None
        series.append(dict(day=fmt_day(d * DAY), applied=daily[(d, 0, False)], negated=daily[(d, 1, False)], takedown_values=daily[(d, 0, True)] + daily[(d, 1, True)],
                           seq_used=(nxt - S[d]) if nxt else None, partial=(d == now_ms // DAY)))
    sup_n = con.execute('SELECT COUNT(*) FROM label WHERE sup != 0').fetchone()[0]
    other_uri = sum(v for (y, x, ng, a), v in cU.items() if a == 'o')
    exp25 = dict(with_exp=sum(v for (y, x), v in cE.items() if y == 2025 and VN.get(x) not in TAKEDOWN_VALS), expired=sum(v for (y, x), v in cX.items() if y == 2025 and VN.get(x) not in TAKEDOWN_VALS))
    return dict(V=V, VN=VN, cU=cU, cP=cP, c3=c3, c5=c5, c6=c6, cE=cE, cX=cX, G=G, rng=rng, ooo=ooo, other_src=other_src, served=nrows, nocts=nocts, exp25=exp25, other_uri=other_uri,
                series=series, head_seq=head_seq, superseded_stored=sup_n, years=years)

ALLV = '__all__'
def vids(A, names):
    if names == ALLV: return [i for s, i in A['V'].items() if s not in TAKEDOWN_VALS]
    return [A['V'][n] for n in names if n in A['V']]

def readings(A, names, Y, subj='any'):
    """Counts R1..R7 (and per-subject-kind splits) for value names and year Y. subj any or account."""
    vs = vids(A, names); kinds = ('a', 'c', 'o') if subj == 'any' else ('a',)
    def s(cnt, key_fn): return {k: sum(cnt[key_fn(v, k)] for v in vs) for k in kinds}
    R = {}
    R['R1'] = s(A['cU'], lambda v, k: (Y, v, 0, k))
    R['R2'] = s(A['cP'], lambda v, k: (Y, v, 0, k))
    R['R3'] = s(A['c3'].get(Y, C.Counter()), lambda v, k: (v, 0, k))
    negY = s(A['cU'], lambda v, k: (Y, v, 1, k)); R['R4'] = {k: R['R1'][k] + negY[k] for k in kinds}
    cred = s(A['c5'], lambda v, k: (Y, v, k)); R['R5'] = {k: R['R1'][k] + cred[k] for k in kinds}
    R['R6'] = s(A['c6'], lambda v, k: (Y, v, k))
    return R, A['G'].get(Y, 0)

def count_interval(R, G):
    tot = {k: sum(v.values()) for k, v in R.items()}; tot['R7'] = tot['R3'] + G
    return tot, min(tot.values()), max(tot.values())

def share_interval(R, G, side):
    sh = {}
    for k, v in R.items():
        den = v.get('a', 0) + v.get('c', 0); sh[k] = (v.get(side, 0) / den) if den else None
    a3, c3 = R['R3'].get('a', 0), R['R3'].get('c', 0); den = a3 + c3 + G; mine = a3 if side == 'a' else c3
    sh['R7 unserved as other side'] = (mine / den) if den else None; sh['R7 unserved as this side'] = ((mine + G) / den) if den else None
    vals = [x for x in sh.values() if x is not None]
    return sh, (min(vals) if vals else None), (max(vals) if vals else None)

WIDE = 'Takedowns and suspensions can be carried out on Bluesky servers outside this label stream, so the stated figure may cover more than the stream. Only a stream count above the stated figure can be read.'
ROWS = [
    dict(id='labels_2025', group='Labels applied', what='Labels applied in 2025', kind='count', V=ALLV, Y=2025, printed='16.49M', point=16490000, lo=16485000, hi=16495000, quote='labels_total'),
    dict(id='labels_2024', group='Labels applied', what='Labels applied in 2024', kind='count', V=ALLV, Y=2024, printed='5.5M', point=5500000, lo=5450000, hi=5550000, quote='labels_total'),
    dict(id='adult_detection', group='Labels applied', what='Adult content detection labels, 2025 (porn plus sexual)', kind='count', V=['porn', 'adult', 'sexual', 'suggestive'], Y=2025, printed='14.2M', point=14200000, lo=14150000, hi=14250000, quote='adult_detection'),
] + [dict(id='val_' + n.strip('!').replace('-', '_'), group='Labels by value, 2025', what=w, kind='count', V=v, Y=2025, printed=p, point=pt, lo=pt - h, hi=pt + h, quote='top_labels_table')
     for n, w, v, p, pt, h in (
        ('adult', 'adult (stream value porn)', ['porn', 'adult'], '10.79M', 10790000, 5000), ('suggestive', 'suggestive (stream value sexual)', ['sexual', 'suggestive'], '3.42M', 3420000, 5000),
        ('spam', 'spam', ['spam'], '761.77K', 761770, 5), ('nudity', 'nudity', ['nudity'], '389.44K', 389440, 5), ('needs-review', 'needs-review', ['needs-review'], '370.14K', 370140, 5),
        ('rude', 'rude', ['rude'], '295.38K', 295380, 5), ('sexual-figurative', 'sexual-figurative', ['sexual-figurative'], '152.58K', 152580, 5),
        ('graphic-media', 'graphic-media', ['graphic-media'], '127.46K', 127460, 5), ('!hide', '!hide', ['!hide'], '68.26K', 68260, 5), ('intolerant', 'intolerant', ['intolerant'], '60.20K', 60200, 5),
        ('self-harm', 'self-harm', ['self-harm'], '20.92K', 20920, 5), ('threat', 'threat', ['threat'], '15.86K', 15860, 5))] + [
    dict(id='share_content', group='Content or account', what='Share of 2025 labels on content rather than accounts', kind='share', V=ALLV, Y=2025, side='c', printed='96.57%', point=0.9657, lo=0.96565, hi=0.96575, quote='content_share'),
    dict(id='share_intolerant', group='Content or account', what='intolerant, share on content, 2025', kind='share', V=['intolerant'], Y=2025, side='c', printed='98%', point=0.98, lo=0.975, hi=0.985, quote='level_shares'),
    dict(id='share_threat', group='Content or account', what='threat, share on content, 2025', kind='share', V=['threat'], Y=2025, side='c', printed='100%', point=1.0, lo=0.995, hi=1.0, quote='level_shares'),
    dict(id='share_rude', group='Content or account', what='rude, share on content, 2025', kind='share', V=['rude'], Y=2025, side='c', printed='99%', point=0.99, lo=0.985, hi=0.995, quote='level_shares'),
    dict(id='share_needs_review', group='Content or account', what='needs-review, share on accounts, 2025', kind='share', V=['needs-review'], Y=2025, side='a', printed='100% (exclusively)', point=1.0, lo=1.0, hi=1.0, quote='needs_review_account'),
    dict(id='takedown_items', group='Takedowns', what='Items removed in 2025 (stream value !takedown)', kind='count_wide', V=['!takedown'], Y=2025, printed='2,446,334', point=2446334, lo=2446334, hi=2446334, quote='takedowns_items'),
    dict(id='takedown_accounts_2025', group='Takedowns', what='Account takedowns in 2025 (!takedown on accounts)', kind='count_wide', V=['!takedown'], Y=2025, subj='account', printed='2.08M', point=2080000, lo=2075000, hi=2085000, quote='account_takedowns'),
    dict(id='takedown_accounts_2024', group='Takedowns', what='Account takedowns in 2024 (!takedown on accounts)', kind='count_wide', V=['!takedown'], Y=2024, subj='account', printed='1.02M', point=1020000, lo=1015000, hi=1025000, quote='account_takedowns'),
    dict(id='suspensions_2025', group='Takedowns', what='Temporary suspensions in 2025 (!suspend)', kind='count_wide', V=['!suspend'], Y=2025, printed='13,192', point=13192, lo=13192, hi=13192, quote='temporary_suspensions'),
    dict(id='automated_share', group='Not in the stream', what='Share of labels applied by automated systems, 2025', kind='absent', printed='95.34%', point=0.9534, quote='automated_share',
         reason='The stream does not record whether a person or a system applied a label. The same holds for the report\'s "% Applied Manually" column.'),
    dict(id='reports_2025', group='Not in the stream', what='User reports in 2025', kind='absent', printed='9.97M', point=9970000, quote='reports',
         reason='The stream carries labels only. Reports are not published in it.'),
]

def build_rows(A, stated, gate_ok):
    out = []
    for spec in ROWS:
        r = dict(id=spec['id'], group=spec['group'], what=spec['what'], kind=spec['kind'], stated=spec['printed'], stated_point=spec['point'],
                 stated_range=[spec.get('lo'), spec.get('hi')], quote=stated['quotes'][spec['quote']]['quote'], source=stated['quotes'][spec['quote']]['url'])
        if spec['kind'] == 'absent':
            r.update(delivered=None, rule=None, interval=None, gap=None, outcome=K.CANNOT_TELL, reason_code=K.NO_INTERVAL_FORMABLE, reason=spec['reason']); out.append(r); continue
        R, G = readings(A, spec['V'], spec['Y'], spec.get('subj', 'any'))
        if spec['kind'] in ('count', 'count_wide'):
            tot, lo, hi = count_interval(R, G)
            r.update(readings=tot, delivered=tot['R1'], rule='R1: served rows, no negation, cts in the UTC calendar year', interval=[lo, hi],
                     interval_is='lowest to highest count across readings R1 to R7 fixed in the plan (rule spread, not a sampling interval)',
                     unserved_seq=G, gap=tot['R1'] - spec['point'], gap_interval=[lo - spec['point'], hi - spec['point']],
                     gap_rel=(tot['R1'] / spec['point'] - 1) if spec['point'] else None)
            zero = all(tot[k] == 0 for k in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6'))
        else:
            sh, lo, hi = share_interval(R, G, spec['side'])
            r.update(readings={k: (round(v, 6) if v is not None else None) for k, v in sh.items()}, counts={k: v for k, v in R.items()}, delivered=sh['R1'],
                     rule='R1: share among served rows, no negation, cts in the UTC calendar year', interval=[lo, hi],
                     interval_is='lowest to highest share across readings R1 to R7 fixed in the plan, R7 counting every unserved write on one side and then the other',
                     unserved_seq=G, gap=(sh['R1'] - spec['point']) if sh['R1'] is not None else None,
                     gap_interval=[lo - spec['point'], hi - spec['point']] if lo is not None else None)
            zero = all(sum(R[k].values()) == 0 for k in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6'))
        # 12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): K.read, closed edges. A row the stream never served is CANNOT_TELL NO_INTERVAL_FORMABLE, never an outcome called nothing returned.
        rc = None; r['zero'] = bool(zero)
        if zero: oc, rc, why = K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, 'The stream served no row of this value in the year under any reading.'
        elif spec['kind'] == 'count_wide':
            o_, _r = K.read(lo, hi, bound=spec['hi'])
            if o_ == K.ABOVE: oc, why = K.ABOVE, None
            else: oc, rc, why = K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, WIDE
        else:
            oc, rc = K.read(lo, hi, band=(spec['lo'], spec['hi'])); why = None
            if oc == K.CANNOT_TELL: why = 'The interval across readings reaches both sides of the stated figure, or past its edge.'
        BESIDE = {'val_graphic_media': [('gore', 'shown in the Bluesky app under the same name, Graphic Media')],
                  'val_adult': [('porn(self)', 'a different value name, seen in the stream')], 'val_suggestive': [('sexual(self)', 'a different value name, seen in the stream')],
                  'val_nudity': [('nudity(self)', 'a different value name, seen in the stream')], 'val_rude': [('rude:1714644703844', 'a different value name, seen in the stream')]}
        if spec['id'] in BESIDE:
            r['beside'] = []
            for bv, why in BESIDE[spec['id']]:
                Rg, _ = readings(A, [bv], spec['Y']); r['beside'].append(dict(value=bv, note=why + '. Reported beside the row and not added, as the plan sets.', R1=sum(Rg['R1'].values())))
        r['stated_inside_interval'] = (lo is not None and not (hi < spec['lo'] or lo > spec['hi']))
        r['outcome'] = oc; r['reason'] = why; r['reason_code'] = rc; out.append(r)
    if not gate_ok:
        out = K.apply_gate(False, out)
        for r in out: r['reason'] = 'The planted-world check failed, so every outcome is cannot tell. ' + (r.get('reason') or ''); r['reason_code'] = K.NO_INTERVAL_FORMABLE
    return out

# ---------------------------------------------------------------- planted world (known-good for the counter)
def _brute(rows, labeler_src, Y, vset, window=WINDOW):
    """Independent, slow implementation of the PLAN readings over a list of served-row dicts."""
    srv = sorted([r for r in rows if r['sup'] == 0 and r['src'] == labeler_src and r['cts'] is not None], key=lambda r: r['seq'])
    allsrv = sorted([r for r in rows if r['sup'] == 0], key=lambda r: r['seq'])
    def inY(t, y, off=0): return YS[y] + off <= t < YS[y + 1] + off
    R1 = sum(1 for r in srv if r['val'] in vset and not r['neg'] and inY(r['cts'], Y))
    R2 = sum(1 for r in srv if r['val'] in vset and not r['neg'] and inY(r['cts'], Y, PAC))
    half = window // 2; inorder = []
    for i, r in enumerate(srv):
        w = sorted(x['cts'] for x in srv[max(0, i - half):i + half + 1]); inorder.append(abs(r['cts'] - w[len(w) // 2]) <= ORDER_TOL)
    def S(t):
        c = [r['seq'] for r, ok in zip(srv, inorder) if ok and r['cts'] >= t]; return min(c) if c else None
    lo = S(YS[Y]); hi = S(YS[Y + 1]) or (max(r['seq'] for r in rows) + 1)
    R3 = sum(1 for r in srv if r['val'] in vset and not r['neg'] and lo <= r['seq'] < hi)
    R4 = R1 + sum(1 for r in srv if r['val'] in vset and r['neg'] and inY(r['cts'], Y))
    def cred(r):
        if r['coll'] != 0 and tid_ms(r['rkey']) is not None and tid_ms(r['rkey']) >= YS[Y + 1]: return False
        return True
    R5 = R1 + sum(1 for r in srv if r['val'] in vset and r['neg'] and r['cts'] >= YS[Y + 1] and cred(r))
    R6 = len({(r['did'], r['coll'], r['rkey'], r['val']) for r in srv if r['val'] in vset and not r['neg'] and inY(r['cts'], Y)})
    G = (hi - lo) - sum(1 for r in allsrv if lo <= r['seq'] < hi)
    return dict(R1=R1, R2=R2, R3=R3, R4=R4, R5=R5, R6=R6, R7=R3 + G)

def _tid(t_ms):
    n = (t_ms * 1000) << 10; s = ''
    for _ in range(13): s = '234567abcdefghijklmnopqrstuvwxyz'[n & 31] + s; n >>= 5
    return s

def planted_world(log=print):
    """A synthetic Ozone table: writes with overwrites, negations, re-labels, timezone edges, TID records, another src and takedown values.
    The counting code must return what the slow, independent implementation returns, and the gross truth must lie inside R3..R7."""
    import random
    rng = random.Random(20261110); con = open_db(':memory:'); ok = True
    vals = ['porn', 'rude', 'needs-review', '!takedown', '!suspend']
    for i, v in enumerate(vals, 1): con.execute('INSERT INTO vals VALUES (?, ?)', (i, v))
    con.execute('INSERT INTO srcs VALUES (1, ?), (2, ?)', (LABELER, 'did:plc:someoneelse')); con.execute("INSERT INTO colls VALUES (1, 'app.bsky.feed.post')")
    table = {}; seq = 0; writes = []; t = ms_utc(2024, 12, 20); end = ms_utc(2026, 1, 12)
    truth = C.Counter()
    while t < end:
        t += rng.randint(30000, 900000); seq += 1
        if rng.random() < 0.002: seq += rng.randint(1, 5)   # sequence skips
        did = rng.randint(1, 400); acct = rng.random() < 0.15; v = rng.choice([1, 1, 1, 2, 2, 3, 4, 5])
        rk = '' if acct else _tid(t - rng.randint(0, 40) * DAY); cidh = 0 if acct else rng.choice([11, 12])
        if not acct and rng.random() < 0.3: rk = _tid(ms_utc(2025, 3, 3) + did * 1000)   # shared records, so labels meet again
        key = (did, 0 if acct else 1, rk, cidh, v, 1)
        neg = 1 if (key in table and table[key][3] == 0 and rng.random() < 0.4) else 0
        if rng.random() < 0.01: key = (did, 0 if acct else 1, rk, cidh, v, 2)   # another src
        cts = t
        if rng.random() < 0.003: cts = t - 40 * DAY      # backdated row (out of order)
        if key in table: table[key] = None
        table[key] = (seq, key, cts, neg)
        if key[5] == 1 and not neg and YS[2025] <= t < YS[2026]: truth[v] += 1
        writes.append((seq, t))
    rows = []
    for key, val in table.items():
        s, k, cts, neg = val; rows.append(dict(seq=s, did=k[0], coll=k[1], rkey=k[2], cidh=k[3], val=k[4], neg=neg, cts=cts, exp=None, src=k[5], sup=0))
    for r in rows:
        con.execute('INSERT INTO label VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (r['seq'], r['did'], r['coll'], r['rkey'], r['cidh'], r['val'], r['neg'], r['cts'], r['exp'], r['src'], 1, 1, 0, 1))
    con.execute('INSERT INTO label VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (seq + 100, 1, 1, _tid(ms_utc(2025, 2, 2)), 11, 1, 0, ms_utc(2025, 2, 2), None, 1, 1, 1, seq + 200, 1))  # a superseded row we hold
    rows.append(dict(seq=seq + 100, did=1, coll=1, rkey=_tid(ms_utc(2025, 2, 2)), cidh=11, val=1, neg=0, cts=ms_utc(2025, 2, 2), exp=None, src=1, sup=seq + 200))
    con.commit()
    A = analyze(con, labeler=LABELER, now_ms=end, years=(2025,))
    names = {1: 'porn', 2: 'rude', 3: 'needs-review', 4: '!takedown', 5: '!suspend'}
    for vset in ([1], [2], [3], [4], [1, 2, 3]):
        want = _brute(rows, 1, 2025, set(vset)); R, G = readings(A, [names[v] for v in vset], 2025); got, lo, hi = count_interval(R, G)
        same = all(got[k] == want[k] for k in want); ok &= same
        g = sum(truth[v] for v in vset); inside = got['R3'] - 5 <= g <= got['R7'] + 60   # year-edge slack: leading gaps can fall before S(Y), a backdated first write can fall before S(Y+1)
        ok &= inside
        log(('OK   ' if same and inside else 'FAIL ') + 'planted %s: code %s  slow %s  gross truth %d in [R3, R7]' % ('+'.join(names[v] for v in vset), [got[k] for k in sorted(got)], [want[k] for k in sorted(want)], g))
    # timezone edge: a row at 2025-12-31 23:30 UTC is 2025 in both, a row at 2026-01-01 05:00 UTC is Pacific 2025 only
    c2 = open_db(':memory:'); c2.execute('INSERT INTO vals VALUES (1, ?)', ('rude',)); c2.execute('INSERT INTO srcs VALUES (1, ?)', (LABELER,))
    base = [(ms_utc(2025, 6, 1) + i * 600000) for i in range(30)]
    edge = [ms_utc(2025, 12, 31, 23, 30), ms_utc(2026, 1, 1, 5), ms_utc(2026, 1, 1, 6), ms_utc(2025, 1, 1, 3), ms_utc(2024, 12, 31, 23)]
    for i, tt in enumerate(sorted(base + edge)): c2.execute('INSERT INTO label VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (i + 1, i + 1, 0, '', 0, 1, 0, tt, None, 1, 1, 1, 0, 1))
    A2 = analyze(c2, now_ms=end, years=(2025,)); R, G = readings(A2, ['rude'], 2025); t1 = sum(R['R1'].values()); t2 = sum(R['R2'].values())
    tz_ok = (t1 == 30 + 2) and (t2 == 30 + 3)   # UTC 2025: base, Dec 31 23:30, Jan 1 03:00. Pacific 2025: base, Dec 31 23:30, Jan 1 05:00 and 06:00 UTC (Jan 1 03:00 UTC is Pacific 2024)
    ok &= tz_ok; log(('OK   ' if tz_ok else 'FAIL ') + 'timezone edges: UTC %d, Pacific %d (want 32 and 33)' % (t1, t2))
    log('PLANTED WORLD ' + ('PASSED' if ok else 'FAILED')); return ok

def selftest(log=print):
    ok = True
    def check(n, c):
        nonlocal ok; ok &= bool(c); log(('OK   ' if c else 'FAIL ') + n)
    x = {'ver': 1, 'src': 'did:plc:x', 'uri': 'at://did:plc:y/app.bsky.feed.post/3k', 'val': 'porn', 'neg': True, 'cts': '2025-01-01T00:00:00.000Z', 'sig': b'\x01' * 64, 'n': -300, 'big': 70000}
    check('cbor round trip', cbor_decode(cbor_encode(x))[0] == x)
    check('cbor key order is length first', list(cbor_decode(cbor_encode({'bb': 1, 'a': 2, 'ccc': 3}))[0]) == ['a', 'bb', 'ccc'])
    check('cts parse with Z and fraction', ts_ms('2025-01-01T00:00:00.123Z') == YS[2025] + 123 and ts_ms('2025-01-01T08:00:00+08:00') == YS[2025] and ts_ms('2025-01-01T00:00:00.123456789Z') == YS[2025] + 123)
    check('TID decode', abs(tid_ms(_tid(ms_utc(2025, 7, 1))) - ms_utc(2025, 7, 1)) < 2 and tid_ms('self') is None)
    # ECDSA known answer: a signature made with a key we derive here, checked by our verifier and by openssl
    c = CURVES['secp256k1']; d = 0x1F2E3D4C5B6A79880102030405060708090A0B0C0D0E0F101112131415161718; msg = b'heuremen known answer'
    def mul(k, P):
        R = (0, 1, 0); Pj = (P[0], P[1], 1)
        for i in range(k.bit_length() - 1, -1, -1):
            R = _jdbl(R, c)
            if (k >> i) & 1: R = _jadd(R, Pj, c)
        zi = pow(R[2], -1, c['p']); return (R[0] * zi * zi % c['p'], R[1] * zi * zi * zi % c['p'])
    Q = mul(d, c['G']); z = int.from_bytes(hashlib.sha256(msg).digest(), 'big'); k = 0x55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA55AA
    r = mul(k, c['G'])[0] % c['n']; s = pow(k, -1, c['n']) * (z + r * d) % c['n']
    if s > c['n'] // 2: s = c['n'] - s
    sig = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    check('ecdsa verifies a valid signature', ecdsa_verify('secp256k1', Q, z, r, s))
    check('ecdsa rejects a changed message', not ecdsa_verify('secp256k1', Q, z ^ 1, r, s))
    ov = openssl_verify('secp256k1', Q, msg, sig); check('openssl agrees on the valid signature (%s)' % ov, ov is True)
    check('openssl rejects a changed message', openssl_verify('secp256k1', Q, msg + b'!', sig) is False)
    cv, Qk = decode_multikey('did:key:zQ3shmV1BNcX17coaDbfen6zArEad6SCLT3jVWCbC6Y9iinTa'); check('labeler key decodes to a secp256k1 point', cv == 'secp256k1' and (Qk[1] ** 2 - Qk[0] ** 3 - 7) % c['p'] == 0)
    ok &= planted_world(log)
    log('SELFTEST ' + ('PASSED' if ok else 'FAILED')); return ok

# ---------------------------------------------------------------- render
def human(n):
    if n is None: return 'none'
    return '{:,}'.format(int(n))

def pct(x, d=2): return 'none' if x is None else ('%.' + str(d) + 'f%%') % (100 * x)
WORD = {K.ABOVE: 'above', K.BELOW: 'below', K.CONSISTENT: 'consistent', K.CANNOT_TELL: 'cannot tell'}
def ow(r): return WORD.get(r['outcome'], r['outcome']) + (' (%s)' % r['reason_code'] if r['outcome'] == K.CANNOT_TELL and r.get('reason_code') else '')   # 12 Nov 2026: the reason sits beside the word

def sparkline(series, w=640, h=96, today=None):
    today = today or time.strftime('%Y-%m-%d', time.gmtime())
    pts = [(s['day'], s['applied']) for s in series if s['day'] < today]
    if len(pts) < 2: return ''
    mx = max(v for _, v in pts) or 1; n = len(pts); top = 14
    X = lambda i: i * (w - 2) / (n - 1) + 1; Y = lambda v: h - 1 - v * (h - 1 - top) / mx
    grid = ['<line x1="0" y1="%d" x2="%d" y2="%d" stroke="currentColor" stroke-opacity="0.35" stroke-width="1" vector-effect="non-scaling-stroke"/>' % (h - 1, w, h - 1)]
    for i, (d, _) in enumerate(pts):
        if d.endswith('-01-01'):
            grid.append('<line x1="%.1f" y1="0" x2="%.1f" y2="%d" stroke="currentColor" stroke-opacity="0.2" stroke-width="1" vector-effect="non-scaling-stroke"/>'
                        '<text x="%.1f" y="10" font-size="10" fill="currentColor" fill-opacity="0.75">%s</text>' % (X(i), X(i), h, X(i) + 3, d[:4]))
    xy = ' '.join('%.1f,%.1f' % (X(i), Y(v)) for i, (_, v) in enumerate(pts))
    desc = 'Labels the stream serves today, per UTC day, %s to %s. Highest day: %s labels.' % (pts[0][0], pts[-1][0], human(mx))
    return ('<svg class="spark" viewBox="0 0 %d %d" width="100%%" height="%d" preserveAspectRatio="none" role="img" aria-label="%s"><title>%s</title>%s'
            '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke" points="%s"/></svg>') % (w, h, h, html.escape(desc), html.escape(desc), ''.join(grid), xy)

def render(rows, A, sig, fetchinfo, kg_ok, read_at=None):
    E = html.escape; now = read_at or time.time()
    by = C.OrderedDict()
    for r in rows: by.setdefault(r['group'], []).append(r)
    def cell_delivered(r):
        if r['kind'] == 'absent': return 'not in the stream'
        return pct(r['delivered']) if r['kind'] == 'share' else human(r['delivered'])
    def cell_interval(r):
        if r['kind'] == 'absent' or r['interval'] is None or r['interval'][0] is None: return ''
        lo, hi = r['interval']
        return ('%s to %s' % (pct(lo), pct(hi))) if r['kind'] == 'share' else ('%s to %s' % (human(lo), human(hi)))
    trs = []
    for g, rs in by.items():
        trs.append('<tr><th colspan="5">%s</th></tr>' % E(g))
        for r in rs:
            bes = [b for b in r.get('beside') or [] if b.get('R1')]
            name = r['what'] + ''.join(' (%s beside it, not added: %s)' % (b['value'], human(b['R1'])) for b in bes)
            trs.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                E(name), E(r['stated']), E(cell_delivered(r)), E(cell_interval(r)), E(ow(r))))
    series = A['series']; today = time.strftime('%Y-%m-%d', time.gmtime(now))
    full = [s for s in series if s['day'] < today]; latest = full[-1] if full else None
    rec_rows = ''.join('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
        s['day'], human(s['applied']), human(s['negated']), human(s['seq_used']) if s['seq_used'] is not None else 'open') for s in full[-7:])
    yr = C.Counter(); yn = C.Counter()
    for s in series: yr[s['day'][:4]] += s['applied']; yn[s['day'][:4]] += s['negated']
    yrows = ''.join('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (y, human(yr[y]), human(yn[y])) for y in sorted(yr))
    c = C.Counter(r['outcome'] for r in rows); first = series[0]['day'] if series else 'none'
    s25 = next(r for r in rows if r['id'] == 'labels_2025')
    measured = [r for r in rows if r['kind'] != 'absent' and not r.get('zero')]
    inside = [r['what'] for r in measured if r.get('stated_inside_interval')]
    above = [r['what'] for r in measured if not r.get('stated_inside_interval') and r['interval'][0] is not None and r['interval'][0] > r['stated_range'][1]]
    below = [r['what'] for r in measured if r['kind'] != 'count_wide' and not r.get('stated_inside_interval') and r['interval'][1] is not None and r['interval'][1] < r['stated_range'][0]]
    def lst(xs): return ', '.join(xs) if xs else 'none'
    e25 = A['exp25']
    sigline = ('We checked the signature of %s labels drawn by a fixed hash of the sequence number, about one in a thousand, across the whole stream, against the label key in the service&rsquo;s DID document, and %s passed.' % (human(sig['sampled']), human(sig['passed']))) if kg_ok else 'The signature check reads cannot tell, since its known-good step failed.'
    out = ['<section id="bluesky" class="social-section">', '<h2>Bluesky labels, counted from the signed stream</h2>']
    out.append('<p>Bluesky&rsquo;s 2025 Transparency Report states how many moderation labels Bluesky applied in 2025 and which ones. Bluesky&rsquo;s moderation service also serves every label it holds as a signed stream that anyone can replay from its first label in April 2023. We replay that stream, check its signatures, and read each stated figure against it under counting rules we fixed in our plan before the count.</p>')
    out.append('<p class="meta">Stream read to %s UTC, sequence number %s. %s</p>' % (time.strftime('%d %b %Y %H:%M', time.gmtime(now)), human(A['head_seq']), sigline))
    out.append('<div class="scroll"><table class="mtx"><thead><tr><th>Stated figure</th><th>Bluesky states</th><th>Stream, first reading</th><th>Range across our counting rules</th><th>Outcome</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(trs))
    out.append('<p class="bench-note">Bluesky states: the figure as printed in Bluesky&rsquo;s report, quoted with its source line in bluesky.json. Stream, first reading: labels the stream serves today with a creation time in the UTC calendar year, negated labels left out. Range across our counting rules: the lowest to the highest count over the readings fixed in our plan. The readings are the first reading, the same by the US Pacific year, the same by position in the stream&rsquo;s sequence, the first reading with negations dated in the year added, the first reading with later negations each credited with one label in the year, the first reading with labels on the same subject and value counted once, and the sequence-position reading with every sequence number of the year that the stream no longer serves credited to the row. The range is the spread of these rules, not a sampling interval, since every count is exact. Above means the whole range is above the stated figure, below means the whole range is below it, consistent means the whole range sits inside the stated figure&rsquo;s rounding, and cannot tell means neither. For takedowns only a stream count above the stated figure can be read, since takedowns can be made outside the stream. Outcomes in this table: %s.</p>' % ', '.join('%s %s' % (WORD[k], c[k]) for k in (K.ABOVE, K.BELOW, K.CONSISTENT, K.CANNOT_TELL, K.NOTHING_RETURNED) if c[k]))
    sus = next((r for r in rows if r['id'] == 'suspensions_2025'), None); sneg = A.get('neg25_suspend', 0)
    if sus and sus['delivered'] == 0 and sneg:
        out.append('<p>Temporary suspensions read 0 in the first reading, since every !suspend label dated 2025 that the stream still serves is a negation, and the first reading leaves negations out. The stream serves %s of these negations dated 2025, so the 0 does not mean the stream holds no suspensions for the year.</p>' % human(sneg))
    out.append('<p>The stated figure lies inside our range for: %s. The whole range is above the stated figure for: %s. The whole range is below it for: %s. Takedown rows are left out of that last list, since takedowns can be made outside the stream.</p>' % (E(lst(inside)), E(lst(above)), E(lst(below))))
    out.append('<p class="bench-note">Cannot tell carries one reason. NO_INTERVAL_FORMABLE covers a figure the stream does not record and a takedown or suspension count the stream can only floor. STRADDLES_EDGE covers a range that crosses an edge of the stated figure. Counts for the rows above: %s</p>' % E(K.req13([(r['outcome'], r.get('reason_code')) for r in rows], nothing_returned=0)['line']))
    out.append('<h3>Labels per day</h3>')
    out.append('<p>Labels the stream serves today, by the UTC day of their creation time, from %s, not counting the two takedown values. The latest full day, %s, has %s labels served and %s negations. A past day can lose labels later, since a label that is negated or applied again moves to the day of the new write.</p>' % (first, latest['day'] if latest else 'none', human(latest['applied']) if latest else 'none', human(latest['negated']) if latest else 'none'))
    out.append(sparkline(series, today=today))
    out.append('<div class="scroll"><table class="mtx small"><thead><tr><th>UTC day</th><th>Labels served</th><th>Negations served</th><th>Sequence numbers used</th></tr></thead><tbody>%s</tbody></table></div>' % rec_rows)
    out.append('<div class="scroll"><table class="mtx small"><thead><tr><th>Year</th><th>Labels served</th><th>Negations served</th></tr></thead><tbody>%s</tbody></table></div>' % yrows)
    out.append('<h3>How we read it</h3>')
    out.append('<p>Bluesky&rsquo;s moderation service keeps one row for each labelled subject and value. Its published code moves that row to a new sequence number when the label is negated or applied again, so a replay serves the latest write of each label and earlier writes leave gaps in the sequence. Of the sequence numbers the stream used in 2025, %s are no longer served. Our first reading counts what the stream serves today. Our highest reading counts every sequence number of the year, served or not. A stated figure between the two cannot be told apart by the stream as served. Of the 2025 labels, %s carry an expiry time and %s of those have expired. They count as applied. From our first replay on we keep every write we read, so later years can be counted with writes that a replay no longer shows. Labels are counted by value and by subject, and no labelled account is named here.</p>' % (human(s25.get('unserved_seq')), human(e25['with_exp']), human(e25['expired'])))
    out.append('<p class="meta">Sources: <a href="%s">Bluesky 2025 Transparency Report</a> and <a href="%s">its overview</a> (Bluesky, 29 January 2026). Stream: <code>wss://mod.bsky.app/xrpc/com.atproto.label.subscribeLabels</code>, the label stream of <a href="https://bsky.app/profile/moderation.bsky.app">Bluesky&rsquo;s moderation service</a>, read without a key. Signing key: <a href="https://plc.directory/did:plc:ar7c4by46qjdydhdevvrndac">the service&rsquo;s DID document</a>. How rows move: <a href="%s">Ozone source, createLabels</a>. Data: <a href="/social/bluesky.json">bluesky.json</a>.</p>' % (REPORT_URL, OVERVIEW_URL, OZONE_URL))
    out.append('</section>')
    return '\n'.join(x for x in out if x) + '\n'

def main():
    args = sys.argv[1:]; t0 = time.time()
    logf = open('data/tick.log', 'a')
    def log(m):
        line = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) + ' UTC  ' + m; print(line, flush=True); logf.write(line + '\n'); logf.flush()
    if '--selftest' in args: sys.exit(0 if selftest(log) else 1)
    gate_ok = planted_world(log)
    con = open_db(args[args.index('--db') + 1] if '--db' in args else DB); fi = None
    if '--no-fetch' not in args:
        lim = int(args[args.index('--limit') + 1]) if '--limit' in args else None
        fi = fetch(con, log, limit=lim)
    keys = fetch_keys(log); sig = verify_samples(con, keys, log); kg = sig['known_good']['passed']
    log('signature sample: %d checked, %d passed, known-good %s' % (sig['sampled'], sig['passed'], 'passed' if kg else 'FAILED'))
    log('counting'); A = analyze(con)
    stated = json.load(open('data/stated.json')); rows = build_rows(A, stated, gate_ok)
    runs = con.execute('SELECT run, started, ended, cursor_from, last_seq, frames, reconnects, stop, superseded FROM runs ORDER BY run').fetchall()
    first_run = runs[0] if runs else None
    meta = dict(updated=(json.load(open('summary_bluesky.json'))['updated'] if '--std2-rewrite' in args else time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())), stream='wss://%s%s' % (HOST, XRPC), labeler=LABELER, head_seq=A['head_seq'], served_rows=A['served'],
                superseded_rows_held=A['superseded_stored'], rows_other_src=A['other_src'], rows_without_cts=A['nocts'],
                out_of_order_by_year={str(k): v for k, v in sorted(A['ooo'].items(), key=lambda kv: kv[0] or 0)},
                year_seq_ranges={str(Y): dict(first_seq=lo, next_year_first_seq=hi, unserved_seq=A['G'][Y]) for Y, (lo, hi) in A['rng'].items()},
                expiring_2025=A['exp25'],
                signature=sig, planted_world='passed' if gate_ok else 'FAILED', plan='PLAN.md', runs=[dict(zip(('run', 'started', 'ended', 'cursor_from', 'last_seq', 'frames', 'reconnects', 'stop', 'superseded'), r)) for r in runs])
    v25 = C.Counter(); n25 = C.Counter()
    for (y, v, ng, a), n in A['cU'].items():
        if y == 2025: (n25 if ng else v25)[A['VN'][v]] += n
    frames_total = sum(r[5] or 0 for r in runs); rows_stored = con.execute('SELECT COUNT(*) FROM label').fetchone()[0]
    meta['counter_known_good_b'] = dict(frames_received=frames_total, rows_stored=rows_stored, equal=(frames_total == rows_stored),
                                        odd_by_kind=dict(con.execute('SELECT kind, COUNT(*) FROM odd GROUP BY kind').fetchall()))
    meta['rows_other_uri_form'] = A['other_uri']
    A['neg25_suspend'] = n25.get('!suspend', 0)
    meta['values_2025_served'] = dict(sorted(v25.items(), key=lambda kv: -kv[1])); meta['negations_2025_served'] = dict(sorted(n25.items(), key=lambda kv: -kv[1]))
    json.dump(dict(meta=meta, rows=rows, series=A['series']), open('data/bsky.json', 'w'), indent=1, ensure_ascii=False, default=str)
    read_at = time.time() if fi is not None else ((runs[-1][2] or runs[-1][1]) if runs else None)   # --no-fetch: the stream was last read when the last run ended
    oc = C.Counter(r['outcome'] for r in rows); lat = [s for s in A['series'] if s['day'] < time.strftime('%Y-%m-%d', time.gmtime(read_at or time.time()))]
    summ = dict(updated=meta['updated'], head_seq=A['head_seq'], served_rows=A['served'], first_day=A['series'][0]['day'] if A['series'] else None,
                latest_day=lat[-1] if lat else None, signature=dict(sampled=sig['sampled'], passed=sig['passed'], low_s=sig['low_s'], known_good=kg),
                outcomes=dict(oc), row_count=len(rows), gate_passed=bool(gate_ok), cannot_tell_by_reason=dict(C.Counter(r.get('reason_code') for r in rows if r['outcome'] == K.CANNOT_TELL)), req13=K.req13([(r['outcome'], r.get('reason_code')) for r in rows], nothing_returned=0),
                rows=[{k: r.get(k) for k in ('id', 'what', 'stated', 'delivered', 'interval', 'outcome', 'reason_code', 'reason')} for r in rows],
                series=[[s['day'], s['applied'], s['negated'], s['seq_used']] for s in A['series']])
    json.dump(summ, open('summary_bluesky.json', 'w'), indent=1, default=str)
    if '--no-render' not in args: open('section_bluesky.html', 'w').write(render(rows, A, sig, fi, kg, read_at))
    log('done in %.0f s: outcomes %s' % (time.time() - t0, dict(oc)))

if __name__ == '__main__': main()
