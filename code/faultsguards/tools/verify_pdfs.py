#!/usr/bin/env python3
"""verify_pdfs.py: the built PDFs must carry the same text as the published ones, ignoring spacing and line breaks (kerning splits some numbers when text is extracted), and the same page count.
usage: verify_pdfs.py BUILD_DIR [PUBLISHED_DIR_OR_URL_PREFIX]   default prefix https://heuremen.org/"""
import os, re, sys, tempfile, unicodedata, urllib.request
import pypdf
def txt(p): r = pypdf.PdfReader(p); return len(r.pages), re.sub(r'\s+', '', unicodedata.normalize('NFKC', ''.join((pg.extract_text() or '') for pg in r.pages)))
def main():
    b = sys.argv[1]; pub = sys.argv[2] if len(sys.argv) > 2 else 'https://heuremen.org/'; ok = True
    for f in ('faults.pdf', 'guards.pdf'):
        if pub.startswith('http'):
            p = os.path.join(tempfile.mkdtemp(), f); urllib.request.urlretrieve(pub + f, p)
        else: p = os.path.join(pub, f)
        n1, t1 = txt(os.path.join(b, f)); n2, t2 = txt(p); same = t1 == t2 and n1 == n2; ok &= same
        print(f, 'pages', n1, n2, 'text', len(t1), len(t2), 'IDENTICAL' if same else 'DIFFERENT')
        if not same:
            for i, (x, y) in enumerate(zip(t1, t2)):
                if x != y: print('  first difference at', i, repr(t1[max(0, i - 30):i + 30]), '|', repr(t2[max(0, i - 30):i + 30])); break
    sys.exit(0 if ok else 1)
if __name__ == '__main__': main()
