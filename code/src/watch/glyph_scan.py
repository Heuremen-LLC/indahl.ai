#!/usr/bin/env python3
"""glyph_scan.py -- EVERY CHARACTER ON THE SITE, CHECKED. (Bones, 9 Oct 2026.)

Wayfinder: "are theses supposed to be boxes? (phi - psi) / sqrt5 -- it didn't come out but next to
phi and psi is a square box on the ecuaciones page on the website." Then: "bro, wtf man. i'm going to
go re-scan everything on the site, you do the same."

WHAT HAPPENED. Binet's formula wants a superscript n: F(n) = (phi^n - psi^n)/sqrt5. The HTML carried
`&#x207F;`'s evil twin -- `&#x2E3F;`, U+2E3F CAMEL, a rare editorial mark almost no font carries. So
it rendered as a box, on a public page, in FIVE source files, feeding THREE live PDFs. It was found by
a human reading the page, which is the check of last resort and the one that should never be the first
to fire.

WHY NO EXISTING CHECK CAUGHT IT. The house's own render trap says "verify by grepping the HTML for
leftover format specifiers and for each computed number BEFORE rendering" -- both about NUMBERS. A
wrong-but-valid HTML entity passes every numeric check, renders without error, and produces a glyph no
font has. There was no character-level check at all.

THE TEST, and it is deliberately not a blacklist. A blacklist of bad codepoints only ever catches the
ones already known, and U+2E3F was not on anyone's list. So instead: a WHITELIST of ranges whose
coverage is established in the fonts these pages actually use, and EVERYTHING ELSE is surfaced for a
human to look at. That inverts the burden -- an unusual character has to earn its place rather than
sneak in.

AND A SECOND, INDEPENDENT SEAT: the rendered PDFs carry ToUnicode maps naming every codepoint their
fonts actually map. A character that is in the HTML and NOT in the PDF's map did not render. Two
checks that fail differently: the whitelist catches a character nobody vetted, the font map catches a
character that was vetted and still did not make it.

    python3 glyph_scan.py
    python3 glyph_scan.py --strict     # non-zero exit if anything is flagged, for a hook
"""
import argparse
import glob
import os
import re
import sys
import unicodedata
import zlib
from collections import Counter, defaultdict

HOME = os.path.expanduser('~')
SOURCES = [os.path.join(HOME, 'bones-forge/ligera/*.html'),
           os.path.join(HOME, 'bones-forge/heuremen.org/*.html'),
           os.path.join(HOME, 'bones-forge/heuremen.org/**/*.html')]
PDFS = os.path.join(HOME, 'bones-forge/heuremen.org/*.pdf')

# RANGES WHOSE COVERAGE IS ESTABLISHED in the fonts these pages use. Anything outside is SURFACED,
# not condemned -- the point is that a human sees it once, not that the scanner knows what is right.
SAFE = [
    (0x00A0, 0x00FF, 'Latin-1 Supplement'),
    (0x0100, 0x017F, 'Latin Extended-A'),
    (0x0370, 0x03FF, 'Greek'),
    (0x2010, 0x2027, 'typographic punctuation (dashes, quotes, ellipsis)'),
    (0x2030, 0x205E, 'per-mille, primes, superscripts/subscripts'),
    (0x2070, 0x209F, 'superscripts and subscripts'),
    (0x20A0, 0x20BF, 'currency'),
    (0x2190, 0x21FF, 'arrows'),
    (0x2200, 0x22FF, 'mathematical operators'),
    (0x2500, 0x257F, 'box drawing'),
    (0x25A0, 0x25FF, 'geometric shapes'),
]
# codepoints seen and deliberately kept, with the reason -- an allowlist of exceptions, each NAMED.
# A silenced warning is how the box survived; a named exception is a decision someone can audit.
KEPT = {
    0x27E8: 'MATHEMATICAL LEFT ANGLE BRACKET -- the bra in Dirac notation, used 89x across the '
            'physics pages. Covered by the system math fonts; verified rendering in bonefish.html.',
    0x27E9: 'MATHEMATICAL RIGHT ANGLE BRACKET -- the ket, same family, same verification.',
}


def safe(cp):
    for lo, hi, _ in SAFE:
        if lo <= cp <= hi:
            return True
    return cp in KEPT


def source_files():
    out = []
    for pat in SOURCES:
        out += glob.glob(pat, recursive=True)
    return sorted(set(out))


def entities(text):
    """EVERY entity resolves to a character, named as well as numeric.

    The bug lived in a numeric one -- &#x2E3F; is seven ASCII characters, so no raw byte scan would
    see it -- and the first version of this function therefore parsed numeric entities only. Then I
    wrote the Dirac ket on the bonefish page as `&rang;` and the gate passed it without ever seeing
    a U+27E9, because a NAMED entity went straight through. Same hole, one spelling over.

    So html.unescape does the work: it resolves both forms, and anything it produces above ASCII is
    a character the page will try to draw."""
    import html as _html
    out = []
    for m in re.finditer(r'&(?:#x[0-9a-fA-F]+|#\d+|[a-zA-Z][a-zA-Z0-9]{1,31});', text):
        try:
            u = _html.unescape(m.group(0))
        except Exception:
            continue
        for ch in u:
            if ord(ch) > 127:
                out.append(ord(ch))
    return out


def pdf_codepoints(path):
    """every unicode codepoint the PDF's fonts actually map, parsed from the ToUnicode CMaps.

    THE FIRST VERSION HAD A FALSE PASS, which is worse than having no scanner at all: it reported
    el-reloj.pdf as "all source codepoints present" while that very PDF was the broken 08 Oct build
    with no U+207F glyph anywhere in it. The cause was a loose regex for bfrange triples run over
    the WHOLE decompressed stream, which swept up any three hex groups it found and expanded them
    into ranges. Measured on that file: 91 real codepoints inflated to 389 invented ones, and
    U+207F fabricated as PRESENT.

    So the CMap is parsed properly and only inside its own blocks:
        beginbfchar  ... endbfchar   -> <src> <dst> pairs
        beginbfrange ... endbfrange  -> <lo> <hi> <dst>  or  <lo> <hi> [ <d1> <d2> ... ]
    Nothing outside those blocks is read as a mapping, because outside them the hex is glyph data,
    widths, or anything else that happens to look like a pair.
    """
    try:
        raw = open(path, 'rb').read()
    except Exception:
        return None
    found = set()
    for m in re.finditer(rb'stream\r?\n(.*?)endstream', raw, re.S):
        try:
            d = zlib.decompress(m.group(1))
        except Exception:
            continue
        for blk in re.finditer(rb'beginbfchar(.*?)endbfchar', d, re.S):
            for mm in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', blk.group(1)):
                h = mm.group(2)
                # a destination may be several UTF-16BE units; take each
                for i in range(0, len(h) - 3, 4):
                    try:
                        found.add(int(h[i:i + 4], 16))
                    except Exception:
                        pass
        for blk in re.finditer(rb'beginbfrange(.*?)endbfrange', d, re.S):
            body = blk.group(1)
            for mm in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', body):
                try:
                    lo, hi = int(mm.group(1), 16), int(mm.group(2), 16)
                    base = int(mm.group(3)[:4], 16)
                    if 0 <= hi - lo < 65536:
                        found.update(range(base, base + (hi - lo) + 1))
                except Exception:
                    pass
            for mm in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*\[(.*?)\]', body, re.S):
                for one in re.finditer(rb'<([0-9a-fA-F]+)>', mm.group(3)):
                    h = one.group(1)
                    for i in range(0, len(h) - 3, 4):
                        try:
                            found.add(int(h[i:i + 4], 16))
                        except Exception:
                            pass
    return found


def gate(path):
    """THE RENDER GATE. Exit non-zero if this ONE source is unfit to render.

    The box reached a public page because the house's render procedure verified NUMBERS -- format
    specifiers and computed values -- and nothing verified CHARACTERS. And when I did write a
    character check it only ran when I remembered to run it, which is the same failure one level up.
    So this is the thing the render line calls, and a refusal stops the PDF being built at all.

    It checks the SOURCE, not the output, because at this point there is no output yet -- that is
    the whole value of a gate over a scan.
    """
    if not os.path.exists(path):
        print(f'  GATE: {path} does not exist')
        return 2
    s = open(path, encoding='utf-8', errors='replace').read()
    seen = Counter()
    for ch in s:
        if ord(ch) > 127:
            seen[ord(ch)] += 1
    for cp in entities(s):
        if cp > 127:
            seen[cp] += 1
    bad = {cp: n for cp, n in seen.items() if not safe(cp)}
    print(f'  GATE  {os.path.basename(path)}   {len(seen)} non-ASCII codepoints, '
          f'{len(bad)} unvetted')
    if not bad:
        print(f'    FIT TO RENDER.')
        return 0
    for cp, n in sorted(bad.items(), key=lambda kv: -kv[1]):
        try:
            nm = unicodedata.name(chr(cp))
        except ValueError:
            nm = '<unnamed>'
        print(f'    U+{cp:04X} x{n:<4} {nm}')
    print(f'    REFUSED. Either fix it, or add the codepoint to KEPT in glyph_scan.py with the')
    print(f'    reason it belongs -- a named exception, not a silenced warning.')
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--file', help='check ONE source and exit non-zero if it is unfit to render. '
                                   'Per-source on purpose: the site-wide scan flags deliberate '
                                   'emoji on the kids pages, so a whole-site gate would either '
                                   'cry wolf forever or get switched off.')
    a = ap.parse_args()
    if a.file:
        return gate(a.file)
    files = source_files()
    print(f'  GLYPH SCAN -- {len(files)} html sources\n')
    where = defaultdict(set)
    counts = Counter()
    for f in files:
        try:
            s = open(f, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        for ch in s:
            if ord(ch) > 127:
                counts[ord(ch)] += 1
                where[ord(ch)].add(os.path.basename(f))
        for cp in entities(s):
            if cp > 127:
                counts[cp] += 1
                where[cp].add(os.path.basename(f) + ' (entity)')
    flagged = {cp: n for cp, n in counts.items() if not safe(cp)}
    print(f'  {len(counts)} distinct non-ASCII codepoints in the sources, '
          f'{len(flagged)} outside the vetted ranges\n')
    if flagged:
        print('  FLAGGED -- outside every vetted range. Each needs a human look once:')
        for cp, n in sorted(flagged.items(), key=lambda kv: -kv[1]):
            try:
                nm = unicodedata.name(chr(cp))
            except ValueError:
                nm = '<unnamed>'
            print(f'    U+{cp:04X}  x{n:<4} {nm}')
            for w in sorted(where[cp])[:4]:
                print(f'              {w}')
    else:
        print('  nothing outside the vetted ranges.')
    print(f'\n  THE VETTED RANGES (coverage established, not assumed safe forever):')
    for lo, hi, nm in SAFE:
        used = sum(n for cp, n in counts.items() if lo <= cp <= hi)
        if used:
            print(f'    U+{lo:04X}-{hi:04X}  {nm:<48} {used} uses')

    # SECOND SEAT: did every source character survive into the rendered PDF?
    print(f'\n  SECOND SEAT -- source characters missing from the rendered PDF fonts')
    pairs = [('las-ecuaciones.pdf', 'LAS_ECUACIONES.html'),
             ('el-picnic.pdf', 'EL_PICNIC_public.html'),
             ('el-reloj.pdf', 'EL_RELOJ_public.html'),
             ('la-siete.pdf', 'LA_SIETE.html'),
             ('ligera.pdf', 'LIGERA.html'),
             ('el-rastro.pdf', 'EL_RASTRO.html')]
    bad_any = False
    for pdf, src in pairs:
        pp = os.path.join(HOME, 'bones-forge/heuremen.org', pdf)
        sp = os.path.join(HOME, 'bones-forge/ligera', src)
        if not (os.path.exists(pp) and os.path.exists(sp)):
            print(f'    {pdf:<22} skipped (missing {"pdf" if not os.path.exists(pp) else "source"})')
            continue
        have = pdf_codepoints(pp)
        if have is None:
            print(f'    {pdf:<22} unreadable')
            continue
        s = open(sp, encoding='utf-8', errors='replace').read()
        want = {ord(c) for c in s if ord(c) > 127} | {c for c in entities(s) if c > 127}
        miss = sorted(c for c in want if c not in have)
        age = os.path.getmtime(pp)
        import time as _t
        st = _t.strftime('%d %b %H:%M', _t.localtime(age))
        if miss:
            bad_any = True
            print(f'    {pdf:<22} built {st}   {len(miss)} MISSING:')
            for c in miss:
                try:
                    nm = unicodedata.name(chr(c))
                except ValueError:
                    nm = '<unnamed>'
                print(f'        U+{c:04X}  {nm}')
        else:
            print(f'    {pdf:<22} built {st}   all {len(want)} source codepoints present')
    if bad_any:
        print(f'\n    A codepoint in the source and NOT in the PDF\'s font map did not render.')
        print(f'    That is the box, and this is the check that would have caught it.')
    if a.strict and (flagged or bad_any):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
