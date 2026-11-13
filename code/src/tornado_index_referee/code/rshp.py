"""Referee shapefile + dbf reader (own code). Returns list of (attrs dict, parts list of Nx2 float arrays)."""
import struct, zipfile
import numpy as np
def read(path):
    z = zipfile.ZipFile(path); nm = z.namelist()
    shp = z.read([n for n in nm if n.lower().endswith('.shp')][0]); dbf = z.read([n for n in nm if n.lower().endswith('.dbf')][0])
    nrec = struct.unpack_from('<I', dbf, 4)[0]; hlen, rlen = struct.unpack_from('<HH', dbf, 8)
    fields = []; p = 32
    while dbf[p] != 0x0D:
        fields.append((dbf[p:p+11].split(b'\0')[0].decode(), dbf[p+16])); p += 32
    attrs = []
    for i in range(nrec):
        r = dbf[hlen + i*rlen: hlen + (i+1)*rlen]; q = 1; d = {}
        for n, l in fields:
            d[n] = r[q:q+l].decode('latin-1').strip(); q += l
        attrs.append(d)
    geoms = []; p = 100
    while p < len(shp):
        clen = struct.unpack_from('>i', shp, p+4)[0]; rec = shp[p+8:p+8+2*clen]; p += 8 + 2*clen
        t = struct.unpack_from('<i', rec, 0)[0]
        if t == 0: geoms.append([]); continue
        np_, npt = struct.unpack_from('<ii', rec, 36)
        parts = list(struct.unpack_from('<%di' % np_, rec, 44)) + [npt]
        pts = np.frombuffer(rec, dtype='<f8', count=2*npt, offset=44+4*np_).reshape(-1, 2)
        geoms.append([pts[parts[k]:parts[k+1]] for k in range(np_)])
    assert len(attrs) == len(geoms)
    return [f for f, _ in fields], attrs, geoms
