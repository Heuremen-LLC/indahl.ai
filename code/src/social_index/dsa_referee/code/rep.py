"""Referee's own reader for report CSV members (zip or plain CSV). Prints rows matching patterns. Standard library only."""
import sys, zipfile, csv, io, re, os
def members(path):
    out = {}
    if path.lower().endswith('.zip'):
        z = zipfile.ZipFile(path)
        for n in z.namelist():
            if n.endswith('/') or '__MACOSX' in n: continue
            out[n] = z.read(n)
    else:
        out[os.path.basename(path)] = open(path, 'rb').read()
    return out
def rows(b):
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try: t = b.decode(enc); break
        except UnicodeDecodeError: continue
    first = t.split('\n', 1)[0]
    d = ';' if first.count(';') > first.count(',') else ','
    return list(csv.reader(io.StringIO(t, newline=''), delimiter=d))
if __name__ == '__main__':
    path, mpat, rpat = sys.argv[1], sys.argv[2], sys.argv[3]
    hdr = len(sys.argv) > 4
    for n, b in members(path).items():
        if not re.search(mpat, n, re.I): continue
        rs = rows(b)
        print('==', n, len(rs), 'rows')
        if hdr:
            for i, r in enumerate(rs[:3]): print('  H%d' % i, r[:30])
        for i, r in enumerate(rs):
            line = ' | '.join(r)
            if re.search(rpat, line, re.I): print('  %4d: %s' % (i, [c for c in r][:24]))
