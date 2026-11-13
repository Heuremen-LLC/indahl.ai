"""Referee read of CDS B1 totals and C9/C1 context from re-pulled PDFs."""
import re, sys, pymupdf
for p in sys.argv[1:]:
    d = pymupdf.open(p)
    t = '\n'.join(pg.get_text() for pg in d)
    i = t.find('B1')
    m = re.search(r'Total all undergraduates[^\n]*\n?([^\n]*\n){0,6}', t, re.I)
    print('==', p, 'pages', len(d))
    for mm in re.finditer(r'(Total all undergraduates|Total undergraduate students|Total all students|Fall 20\d\d|Total first-time, first-year)', t, re.I):
        print('  ', repr(t[mm.start():mm.start()+160]))
        if mm.start() > 40000: break
