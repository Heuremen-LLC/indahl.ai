"""Referee's minimal BIFF8 .xls reader (independent of the pipeline's xls_biff.py). Returns {sheet: {(row, col): value}}."""
import struct, sys

def cfb_stream(data, want='Workbook'):
    ssz = 1 << struct.unpack_from('<H', data, 30)[0]
    mssz = 1 << struct.unpack_from('<H', data, 32)[0]
    nfat = struct.unpack_from('<I', data, 44)[0]
    dir0 = struct.unpack_from('<I', data, 48)[0]
    mini_cut = struct.unpack_from('<I', data, 56)[0]
    minifat0 = struct.unpack_from('<I', data, 60)[0]
    difat0 = struct.unpack_from('<I', data, 68)[0]
    ndifat = struct.unpack_from('<I', data, 72)[0]
    difat = list(struct.unpack_from('<109I', data, 76))
    s = difat0
    for _ in range(ndifat):
        off = 512 + s * ssz
        vals = struct.unpack_from('<%dI' % (ssz // 4), data, off)
        difat += list(vals[:-1]); s = vals[-1]
    fat = []
    for fs in difat[:nfat]:
        off = 512 + fs * ssz
        fat += list(struct.unpack_from('<%dI' % (ssz // 4), data, off))
    def chain(start):
        out = []; s = start
        while s < 0xFFFFFFFA and len(out) < 10**7:
            out.append(s); s = fat[s]
        return out
    def read(start, size=None):
        b = b''.join(data[512 + s * ssz: 512 + (s + 1) * ssz] for s in chain(start))
        return b[:size] if size is not None else b
    d = read(dir0)
    ents = []
    for i in range(len(d) // 128):
        e = d[i * 128:(i + 1) * 128]
        nl = struct.unpack_from('<H', e, 64)[0]
        name = e[:max(0, nl - 2)].decode('utf-16-le', 'ignore')
        typ = e[66]; start = struct.unpack_from('<I', e, 116)[0]; size = struct.unpack_from('<I', e, 120)[0]
        ents.append((name, typ, start, size))
    root = ents[0]
    for name, typ, start, size in ents:
        if name in (want, 'Book') and typ == 2:
            if size >= mini_cut:
                return read(start, size)
            ministream = read(root[2], root[3])
            minifat = []
            for s in chain(minifat0):
                minifat += list(struct.unpack_from('<%dI' % (ssz // 4), data, 512 + s * ssz))
            out = []; s = start
            while s < 0xFFFFFFFA:
                out.append(ministream[s * mssz:(s + 1) * mssz]); s = minifat[s]
            return b''.join(out)[:size]
    raise ValueError('no workbook stream')

def rk(v):
    mult = v & 1; isint = v & 2
    if isint: x = float(v >> 2) if not (v & 0x80000000) else float((v >> 2) - (1 << 30))
    else: x = struct.unpack('<d', struct.pack('<Q', (v & 0xFFFFFFFC) << 32))[0]
    return x / 100 if mult else x

def read_xls(path):
    wb = cfb_stream(open(path, 'rb').read())
    recs = []; i = 0
    while i + 4 <= len(wb):
        t, n = struct.unpack_from('<HH', wb, i); recs.append((t, i, wb[i + 4:i + 4 + n])); i += 4 + n
    sheets = []; sst = []
    # SST with CONTINUE
    for k, (t, off, b) in enumerate(recs):
        if t == 0x0085:
            pos = struct.unpack_from('<I', b, 0)[0]; cch = b[6]; fl = b[7]
            name = b[8:8 + cch].decode('latin-1') if fl == 0 else b[8:8 + 2 * cch].decode('utf-16-le')
            sheets.append((name, pos))
        if t == 0x00FC:
            parts = [b]; j = k + 1
            while j < len(recs) and recs[j][0] == 0x003C: parts.append(recs[j][2]); j += 1
            nuniq = struct.unpack_from('<I', parts[0], 4)[0]
            pi, p = 0, 8
            def need(nb):
                nonlocal pi, p
                if p >= len(parts[pi]): pi += 1; p = 0
            for _ in range(nuniq):
                need(3)
                cur = parts[pi]
                cch = struct.unpack_from('<H', cur, p)[0]; fl = cur[p + 2]; p += 3
                runs = ext = 0
                if fl & 8: runs = struct.unpack_from('<H', cur, p)[0]; p += 2
                if fl & 4: ext = struct.unpack_from('<I', cur, p)[0]; p += 4
                chars = []; left = cch; wide = fl & 1
                while left > 0:
                    cur = parts[pi]
                    if p >= len(cur):
                        pi += 1; cur = parts[pi]; wide = cur[0] & 1; p = 1
                    avail = (len(cur) - p) // (2 if wide else 1)
                    take = min(left, avail)
                    seg = cur[p:p + take * (2 if wide else 1)]
                    chars.append(seg.decode('utf-16-le') if wide else seg.decode('latin-1'))
                    p += take * (2 if wide else 1); left -= take
                skip = 4 * runs + ext
                while skip > 0:
                    cur = parts[pi]
                    if p >= len(cur): pi += 1; p = 0; continue
                    s_ = min(skip, len(cur) - p); p += s_; skip -= s_
                sst.append(''.join(chars))
    out = {}
    offs = sorted((pos, name) for name, pos in sheets)
    for idx, (pos, name) in enumerate(offs):
        end = offs[idx + 1][0] if idx + 1 < len(offs) else len(wb)
        cells = {}
        pending = None
        for t, off, b in recs:
            if off < pos or off >= end: continue
            if t == 0x00FD: r, c, _, isst = struct.unpack_from('<HHHI', b, 0); cells[(r, c)] = sst[isst]
            elif t == 0x0203: r, c, _ = struct.unpack_from('<HHH', b, 0); cells[(r, c)] = struct.unpack_from('<d', b, 6)[0]
            elif t == 0x027E: r, c, _, v = struct.unpack_from('<HHHI', b, 0); cells[(r, c)] = rk(v)
            elif t == 0x00BD:
                r, c0 = struct.unpack_from('<HH', b, 0); n = (len(b) - 6) // 6
                for q in range(n): cells[(r, c0 + q)] = rk(struct.unpack_from('<I', b, 4 + q * 6 + 2)[0])
            elif t == 0x0204:
                r, c, _, cch = struct.unpack_from('<HHHH', b, 0); fl = b[8]
                cells[(r, c)] = b[9:9 + cch].decode('latin-1') if not fl & 1 else b[9:9 + 2 * cch].decode('utf-16-le')
            elif t == 0x0006:
                r, c, _ = struct.unpack_from('<HHH', b, 0); res = b[6:14]
                if res[6:8] == b'\xff\xff':
                    if res[0] == 0: pending = (r, c)
                    else: cells[(r, c)] = res[2]
                else: cells[(r, c)] = struct.unpack('<d', res)[0]
            elif t == 0x0207 and pending:
                cch = struct.unpack_from('<H', b, 0)[0]; fl = b[2]
                cells[pending] = b[3:3 + cch].decode('latin-1') if not fl & 1 else b[3:3 + 2 * cch].decode('utf-16-le'); pending = None
        out[name] = cells
    return out

def rows_of(cells):
    if not cells: return []
    R = max(r for r, c in cells) + 1; C = max(c for r, c in cells) + 1
    return [[cells.get((r, c), '') for c in range(C)] for r in range(R)]

if __name__ == '__main__':
    wbk = read_xls(sys.argv[1])
    for name, cells in wbk.items():
        print('== sheet', name, len(cells), 'cells')
        for row in rows_of(cells)[:int(sys.argv[2]) if len(sys.argv) > 2 else 4]:
            print('   ', [x for x in row][:22])
