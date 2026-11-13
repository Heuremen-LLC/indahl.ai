"""shpread.py: minimal reader for the polygon shapefiles in a zip (shp + dbf), standard library only. Used by tornado_tick.py."""
import struct, zipfile, io
def _dbf(b):
    n, hl, rl = struct.unpack('<xxxxIHH', b[:12]); fields = []; p = 32
    while b[p] != 0x0D:
        name = b[p:p + 11].split(b'\0')[0].decode(); t = chr(b[p + 11]); ln = b[p + 16]; fields.append((name, t, ln)); p += 32
    out = []; p = hl
    for i in range(n):
        rec = b[p:p + rl]; p += rl; q = 1; d = {}
        if rec[:1] == b'*': continue
        for name, t, ln in fields:
            v = rec[q:q + ln].decode('latin-1').strip(); q += ln; d[name] = v
        out.append(d)
    return [f[0] for f in fields], out
def _shp(b):
    p = 100; shapes = []
    while p < len(b):
        num, clen = struct.unpack('>ii', b[p:p + 8]); p += 8; rec = b[p:p + clen * 2]; p += clen * 2
        st = struct.unpack('<i', rec[:4])[0]
        if st == 0: shapes.append([]); continue
        if st not in (5, 15, 25): raise ValueError('shape type %d not a polygon' % st)
        nparts, npts = struct.unpack('<ii', rec[36:44]); parts = list(struct.unpack('<%di' % nparts, rec[44:44 + 4 * nparts]))
        o = 44 + 4 * nparts; pts = struct.unpack('<%dd' % (2 * npts), rec[o:o + 16 * npts])
        xy = [(pts[2 * i], pts[2 * i + 1]) for i in range(npts)]; parts.append(npts)
        shapes.append([xy[parts[i]:parts[i + 1]] for i in range(nparts)])
    return shapes
def read_zip(path):
    """Returns (field names, [dict(record, rings=[[(lon, lat), ...], ...])])."""
    z = zipfile.ZipFile(path); names = z.namelist()
    shp = next(n for n in names if n.lower().endswith('.shp')); dbf = next(n for n in names if n.lower().endswith('.dbf'))
    fn, recs = _dbf(z.read(dbf)); shapes = _shp(z.read(shp))
    if len(recs) != len(shapes): raise ValueError('dbf %d records, shp %d shapes' % (len(recs), len(shapes)))
    for r, s in zip(recs, shapes): r['rings'] = s
    return fn, recs
