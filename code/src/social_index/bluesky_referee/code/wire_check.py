"""Referee wire check: reads short slices of the label stream with the referee's own websocket client, CBOR decoder and
secp256k1 ECDSA, and compares each served frame with the row the desk stored. Read-only on the desk store.
Does not import bsky_tick.py.  Usage: python3 -I wire_check.py DBPATH OUTJSON cursor1 cursor2 ... [--n N]
"""
import socket, ssl, os, base64, struct, json, sys, hashlib, sqlite3, calendar, datetime as D

HOST = 'mod.bsky.app'; PATH = '/xrpc/com.atproto.label.subscribeLabels'
UA = 'heuremen-referee/0.1 (read-only label check)'
KEY = 'zQ3shmV1BNcX17coaDbfen6zArEad6SCLT3jVWCbC6Y9iinTa'
LAB = 'did:plc:ar7c4by46qjdydhdevvrndac'

# ---------- CBOR (decode + canonical DAG-CBOR encode)
def dec(b, i):
    ib = b[i]; mt, ai = ib >> 5, ib & 31; i += 1
    if ai < 24: arg = ai
    elif ai == 24: arg = b[i]; i += 1
    elif ai == 25: arg = int.from_bytes(b[i:i+2], 'big'); i += 2
    elif ai == 26: arg = int.from_bytes(b[i:i+4], 'big'); i += 4
    elif ai == 27: arg = int.from_bytes(b[i:i+8], 'big'); i += 8
    else: raise ValueError('indefinite length')
    if mt == 0: return arg, i
    if mt == 1: return -1 - arg, i
    if mt == 2: return bytes(b[i:i+arg]), i + arg
    if mt == 3: return b[i:i+arg].decode('utf-8'), i + arg
    if mt == 4:
        out = []
        for _ in range(arg): x, i = dec(b, i); out.append(x)
        return out, i
    if mt == 5:
        out = {}
        for _ in range(arg):
            k, i = dec(b, i); x, i = dec(b, i); out[k] = x
        return out, i
    if mt == 6: x, i = dec(b, i); return ('tag', arg, x), i
    if mt == 7:
        return {20: False, 21: True, 22: None}.get(ai, ('simple', ai)), i
def hd(mt, n):
    if n < 24: return bytes([mt << 5 | n])
    for ai, w in ((24, 1), (25, 2), (26, 4), (27, 8)):
        if n < 256 ** w: return bytes([mt << 5 | ai]) + n.to_bytes(w, 'big')
def enc(x):
    if x is True: return b'\xf5'
    if x is False: return b'\xf4'
    if x is None: return b'\xf6'
    if isinstance(x, int): return hd(0, x) if x >= 0 else hd(1, -1 - x)
    if isinstance(x, bytes): return hd(2, len(x)) + x
    if isinstance(x, str): e = x.encode(); return hd(3, len(e)) + e
    if isinstance(x, list): return hd(4, len(x)) + b''.join(enc(y) for y in x)
    if isinstance(x, dict):
        ks = sorted(x, key=lambda k: (len(k.encode()), k.encode()))
        return hd(5, len(ks)) + b''.join(enc(k) + enc(x[k]) for k in ks)
    raise TypeError(type(x))

# ---------- secp256k1
P = 2**256 - 2**32 - 977; N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798; Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
def add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2 and (y1 + y2) % P == 0: return None
    l = (3 * x1 * x1 * pow(2 * y1, -1, P)) % P if p1 == p2 else ((y2 - y1) * pow(x2 - x1, -1, P)) % P
    x3 = (l * l - x1 - x2) % P; return (x3, (l * (x1 - x3) - y1) % P)
def mul(k, p):
    r = None
    while k:
        if k & 1: r = add(r, p)
        p = add(p, p); k >>= 1
    return r
def b58(s):
    A = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'; n = 0
    for c in s: n = n * 58 + A.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big'); return b'\x00' * (len(s) - len(s.lstrip('1'))) + raw
kb = b58(KEY[1:]); assert kb[:2] == b'\xe7\x01', kb[:2]
cx = int.from_bytes(kb[3:35], 'big'); cy = pow((cx ** 3 + 7) % P, (P + 1) // 4, P)
if (cy & 1) != (kb[2] & 1): cy = P - cy
Q = (cx, cy)
def verify(msg, sig):
    z = int.from_bytes(hashlib.sha256(msg).digest(), 'big'); r = int.from_bytes(sig[:32], 'big'); s = int.from_bytes(sig[32:], 'big')
    if not (0 < r < N and 0 < s < N): return False, False
    w = pow(s, -1, N); X = add(mul(z * w % N, (Gx, Gy)), mul(r * w % N, Q))
    return (X is not None and X[0] % N == r), s <= N // 2

# ---------- websocket
def ws_open(cursor):
    raw = socket.create_connection((HOST, 443), timeout=30); s = ssl.create_default_context().wrap_socket(raw, server_hostname=HOST)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(('GET %s?cursor=%d HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\nUser-Agent: %s\r\n\r\n' % (PATH, cursor, HOST, key, UA)).encode())
    buf = b''
    while b'\r\n\r\n' not in buf: buf += s.recv(4096)
    head, rest = buf.split(b'\r\n\r\n', 1); assert b' 101 ' in head.split(b'\r\n')[0], head[:80]
    return s, bytearray(rest)
def ws_msgs(s, buf):
    def need(k):
        while len(buf) < k:
            d = s.recv(65536)
            if not d: raise EOFError
            buf.extend(d)
    msg = bytearray()
    while True:
        need(2); b0, b1 = buf[0], buf[1]; ln = b1 & 127; o = 2
        if ln == 126: need(4); ln = struct.unpack('>H', buf[2:4])[0]; o = 4
        elif ln == 127: need(10); ln = struct.unpack('>Q', buf[2:10])[0]; o = 10
        need(o + ln); pay = bytes(buf[o:o+ln]); del buf[:o+ln]; op = b0 & 15
        if op == 9: mk = os.urandom(4); s.sendall(bytes([0x8A, 0x80 | len(pay)]) + mk + bytes(c ^ mk[j % 4] for j, c in enumerate(pay))); continue
        if op == 8: return
        msg += pay
        if b0 & 0x80: yield bytes(msg); msg = bytearray()

def ts(s):
    d = D.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None: d = d.replace(tzinfo=D.timezone.utc)
    return calendar.timegm(d.utctimetuple()) * 1000 + d.microsecond // 1000
def cidh(c): return int.from_bytes(hashlib.blake2b(c.encode(), digest_size=8).digest(), 'big', signed=True) if c else 0

def main():
    a = sys.argv[1:]; n = 2000
    if '--n' in a: j = a.index('--n'); n = int(a[j + 1]); del a[j:j + 2]
    db, outp = a[0], a[1]; curs = [int(x) for x in a[2:]]
    con = sqlite3.connect('file:%s?mode=ro' % db, uri=True)
    VN = dict(con.execute('SELECT id, s FROM vals')); DN = {}; CN = dict(con.execute('SELECT id, s FROM colls')); SN = dict(con.execute('SELECT id, s FROM srcs'))
    res = []
    for c0 in curs:
        s, buf = ws_open(c0); got = []
        for m in ws_msgs(s, buf):
            h, i = dec(m, 0); body, _ = dec(m, i)
            if h.get('op') != 1: got.append(('error', body)); break
            got.append((body['seq'], body['labels']))
            if len(got) >= n: break
        s.close()
        lo, hi = c0, got[-1][0] if got and got[-1][0] != 'error' else c0
        stored = {r[0]: r for r in con.execute('SELECT seq, did, coll, rkey, cidh, val, neg, cts, exp, src, sup FROM label WHERE seq > ? AND seq <= ?', (lo, hi))}
        st = dict(cursor=c0, frames=len(got), last=hi, stored_rows_in_range=len(stored), match=0, mismatch=[], not_stored=0, sig_ok=0, sig_bad=0, low_s=0, labels_per_frame_not_1=0,
                  stored_superseded_in_range=sum(1 for r in stored.values() if r[10]))
        for g in got:
            if g[0] == 'error': st['error'] = str(g[1])[:200]; continue
            sq, labels = g
            if len(labels) != 1: st['labels_per_frame_not_1'] += 1
            L = labels[0]; sig = L.get('sig')
            ok, low = verify(enc({k: v for k, v in L.items() if k != 'sig'}), sig) if isinstance(sig, bytes) else (False, False)
            st['sig_ok' if ok else 'sig_bad'] += 1; st['low_s'] += 1 if low else 0
            r = stored.pop(sq, None)
            if r is None: st['not_stored'] += 1; continue
            uri = L['uri']
            if uri.startswith('did:'): kind_ok = r[2] == 0; did = uri; rk = ''
            elif uri.startswith('at://'):
                parts = uri[5:].split('/', 2); did = parts[0]; rk = parts[2] if len(parts) > 2 else ''
                kind_ok = r[2] > 0 and CN.get(r[2]) == (parts[1] if len(parts) > 1 else None)
            else: kind_ok = r[2] == -1; did = uri; rk = ''
            if did not in DN: DN[did] = con.execute('SELECT id FROM dids WHERE s = ?', (did,)).fetchone()
            want = dict(did=(DN[did] or [None])[0] == r[1], kind=kind_ok, rkey=(rk == r[3]) or r[2] <= 0, cid=cidh(L.get('cid')) == r[4], val=VN.get(r[5]) == L['val'],
                        neg=int(L.get('neg') is True) == r[6], cts=ts(L['cts']) == r[7], exp=(r[8] is None) if L.get('exp') is None else ts(L['exp']) == r[8], src=SN.get(r[9]) == L['src'])
            if all(want.values()): st['match'] += 1
            else: st['mismatch'].append(dict(seq=sq, fields=[k for k, v in want.items() if not v]))
        st['stored_not_served'] = len(stored); st['stored_not_served_superseded'] = sum(1 for r in stored.values() if r[10])
        st['mismatch'] = st['mismatch'][:20]; res.append(st); print(json.dumps(st))
    json.dump(res, open(outp, 'w'), indent=1)
if __name__ == '__main__': main()
