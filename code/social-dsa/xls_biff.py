"""xls_biff.py: minimal reader for legacy .xls (OLE2 compound file, BIFF8 records). Standard library only.
Returns {sheet_name: [[cell text, ...], ...]}. Reads cell text and numbers (LABELSST, LABEL, NUMBER, RK, MULRK, FORMULA cached values)."""
import struct

def _ole_stream(data, want=('Workbook', 'Book')):
    if data[:8] != b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': raise ValueError('not an OLE2 file')
    ss = 1 << struct.unpack_from('<H', data, 0x1E)[0]; mss = 1 << struct.unpack_from('<H', data, 0x20)[0]
    n_fat, dir_start = struct.unpack_from('<II', data, 0x2C)
    cutoff, mfat_start, n_mfat, dif_start, n_dif = struct.unpack_from('<IIIII', data, 0x38)
    sec = lambda n: data[(n + 1) * ss:(n + 2) * ss]
    difat = list(struct.unpack_from('<109I', data, 0x4C)); d = dif_start
    for _ in range(n_dif):
        if d >= 0xFFFFFFFA: break
        e = struct.unpack('<%dI' % (ss // 4), sec(d)); difat += list(e[:-1]); d = e[-1]
    fat = []
    for f in difat[:n_fat]: fat += struct.unpack('<%dI' % (ss // 4), sec(f))
    def chain(start):
        out, n, seen = [], start, set()
        while n < 0xFFFFFFFA and n not in seen: seen.add(n); out.append(n); n = fat[n]
        return out
    dirdata = b''.join(sec(n) for n in chain(dir_start)); entries = []
    for i in range(0, len(dirdata), 128):
        e = dirdata[i:i + 128]; nl = struct.unpack_from('<H', e, 0x40)[0]
        name = e[:max(0, nl - 2)].decode('utf-16-le', 'ignore'); typ = e[0x42]; start, size = struct.unpack_from('<II', e, 0x74)
        entries.append((name, typ, start, size))
    root = next(e for e in entries if e[1] == 5)
    for name, typ, start, size in entries:
        if typ == 2 and name in want:
            if size >= cutoff: return b''.join(sec(n) for n in chain(start))[:size]
            ministream = b''.join(sec(n) for n in chain(root[2]))
            mfat = []
            for n in chain(mfat_start): mfat += struct.unpack('<%dI' % (ss // 4), sec(n))
            out, n = [], start
            while n < 0xFFFFFFFA: out.append(ministream[n * mss:(n + 1) * mss]); n = mfat[n]
            return b''.join(out)[:size]
    raise ValueError('no Workbook stream')

def _records(wb):
    i = 0
    while i + 4 <= len(wb):
        rid, ln = struct.unpack_from('<HH', wb, i); yield i, rid, wb[i + 4:i + 4 + ln]; i += 4 + ln

def _rk(v):
    if v & 2: x = v >> 2; x = x - (1 << 30) if x & (1 << 29) else x
    else: x = struct.unpack('<d', struct.pack('<Q', (v & 0xFFFFFFFC) << 32))[0]
    return x / 100 if v & 1 else x

def _num(x):
    return str(int(x)) if isinstance(x, float) and x == int(x) and abs(x) < 1e15 else str(x)

def _sst(segs):
    """segs: SST record data followed by CONTINUE data segments."""
    out = []; si, pos = 0, 8
    total_unique = struct.unpack_from('<I', segs[0], 4)[0]
    def need(k):
        nonlocal si, pos
        if pos + k <= len(segs[si]): return
        if pos == len(segs[si]): si += 1; pos = 0
    def rd(k):
        nonlocal si, pos
        b = b''
        while k:
            if pos >= len(segs[si]): si += 1; pos = 0
            take = min(k, len(segs[si]) - pos); b += segs[si][pos:pos + take]; pos += take; k -= take
        return b
    while len(out) < total_unique and si < len(segs):
        if pos >= len(segs[si]):
            si += 1; pos = 0
            if si >= len(segs): break
        cch = struct.unpack('<H', rd(2))[0]; flags = rd(1)[0]; high = flags & 1
        runs = struct.unpack('<H', rd(2))[0] if flags & 8 else 0; ext = struct.unpack('<I', rd(4))[0] if flags & 4 else 0
        chars = []; left = cch
        while left:
            if pos >= len(segs[si]):
                si += 1; pos = 0; high = segs[si][0] & 1; pos = 1
            avail = (len(segs[si]) - pos) // (2 if high else 1); take = min(left, avail)
            raw = segs[si][pos:pos + take * (2 if high else 1)]; pos += len(raw)
            chars.append(raw.decode('utf-16-le' if high else 'latin-1', 'ignore')); left -= take
        rd(4 * runs); rd(ext); out.append(''.join(chars))
    return out

def xls_sheets(data):
    wb = _ole_stream(data); recs = list(_records(wb))
    sheets = []; sst = []; i = 0
    while i < len(recs):
        off, rid, d = recs[i]
        if rid == 0x0085:
            pos = struct.unpack_from('<I', d, 0)[0]; cch, fl = d[6], d[7]
            name = d[8:8 + cch * (2 if fl & 1 else 1)].decode('utf-16-le' if fl & 1 else 'latin-1', 'ignore'); sheets.append((name, pos))
        elif rid == 0x00FC:
            segs = [d]; j = i + 1
            while j < len(recs) and recs[j][1] == 0x003C: segs.append(recs[j][2]); j += 1
            sst = _sst(segs)
        i += 1
    out = {}
    for name, pos in sheets:
        cells = {}; pending = None
        for off, rid, d in recs:
            if off < pos: continue
            if rid == 0x000A and off > pos: break
            if rid == 0x00FD: r, c, _, k = struct.unpack_from('<HHHI', d); cells[(r, c)] = sst[k] if k < len(sst) else ''
            elif rid == 0x0203: r, c, _, x = struct.unpack_from('<HHHd', d); cells[(r, c)] = _num(x)
            elif rid == 0x027E: r, c, _, v = struct.unpack_from('<HHHI', d); cells[(r, c)] = _num(_rk(v))
            elif rid == 0x00BD:
                r, c0 = struct.unpack_from('<HH', d); n = (len(d) - 6) // 6
                for k in range(n): cells[(r, c0 + k)] = _num(_rk(struct.unpack_from('<I', d, 4 + k * 6 + 2)[0]))
            elif rid == 0x0204:
                r, c, _, cch = struct.unpack_from('<HHHH', d); fl = d[8]
                cells[(r, c)] = d[9:9 + cch * (2 if fl & 1 else 1)].decode('utf-16-le' if fl & 1 else 'latin-1', 'ignore')
            elif rid == 0x0006:
                r, c = struct.unpack_from('<HH', d); res = d[6:14]
                if res[6:8] == b'\xff\xff':
                    if res[0] == 0: pending = (r, c)
                    elif res[0] == 1: cells[(r, c)] = 'TRUE' if res[2] else 'FALSE'
                else: cells[(r, c)] = _num(struct.unpack('<d', res)[0])
            elif rid == 0x0207 and pending:
                cch = struct.unpack_from('<H', d)[0]; fl = d[2]
                cells[pending] = d[3:3 + cch * (2 if fl & 1 else 1)].decode('utf-16-le' if fl & 1 else 'latin-1', 'ignore'); pending = None
        if cells:
            nr = max(r for r, _ in cells) + 1; nc = max(c for _, c in cells) + 1
            out[name] = [[cells.get((r, c), '') for c in range(nc)] for r in range(nr)]
        else: out[name] = []
    return out

if __name__ == '__main__':
    import sys
    s = xls_sheets(open(sys.argv[1], 'rb').read())
    for k, v in s.items(): print(repr(k), len(v), 'rows')
