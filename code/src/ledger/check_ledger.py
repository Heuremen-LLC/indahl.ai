#!/usr/bin/env python3
"""Compare every surface with the ledger.

  check_claims.py            report drift; exit 1 if any
  check_claims.py --coverage also list numbers printed on a surface that no live row covers

Drift is:
  MISSING    a live row's snippet is not on a surface the row says it is on (the surface changed; the ledger was not edited first)
  ZOMBIE     a withdrawn or held row's snippet is still printed on a surface
  SOURCE     the row's source file is gone, or no longer contains the row's grep text (the number lost its producer)
  LIVEFIELD  (10 Nov 2026) a live_headline row's feed no longer carries the field its headline comes from (or a field its rule reads)
  LIVESTALE  a live_headline row's feed stamp is older than the desk's cadence x 1.5
  LIVEFEED / LIVESTAMP  the feed could not be read, or its stamp does not read as a time
  The live value is not compared: it moves on every read. A new value row is written by live_headlines.py run on a material change only.
Text is compared after stripping HTML/LaTeX markup and normalising dashes, spaces and minus signs.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import load, surface_path, ROOT, SURFACES


def norm(s):
    s = re.sub(r'<a class="rcpt"[^>]*>[^<]*</a>', '', s)   # 10 Nov 2026: a receipt link (ledger/receipts.py) is not page text, so it never splits a snippet
    s = re.sub(r'<a class="ent" href="[^"]*">([^<]*)</a><a class="fb nosig"[^>]*>Follow</a>', r'\1', s)   # 10 Nov 2026 evening: a Follow link beside a name (indahl-ai/entities.py) is not page text, and the name keeps its place
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = s.replace('\\us{}', ' µs').replace('\\us', ' µs').replace('\\%', '%').replace('\\,', ' ').replace('\\textmu', 'µ')
    s = re.sub(r'\\(texttt|emph|textbf|mathrm)\{([^}]*)\}', r'\2', s)
    s = s.replace('\\pm', '±').replace('$', '').replace('{', '').replace('}', '').replace('^\\circ', '°').replace('\\circ', '°')
    s = s.replace('−', '-').replace('–', '-').replace('—', '-').replace('\u2009', ' ').replace('\xa0', ' ')
    s = s.replace('\\n', ' ')
    return re.sub(r'\s+', ' ', s).strip()


_cache = {}
def text_of(key):
    if key not in _cache:
        p = surface_path(key)
        _cache[key] = norm(open(p, errors='ignore').read()) if os.path.exists(p) else None
    return _cache[key]


def main():
    rows = load(); drift = []
    for r in rows.values():
        if r['status'] == 'staged':   # 10 Nov: a new desk's row before its first ship; not checked either way until the desk flips it to live in its ship
            continue
        src = r['source']['file']; sp = src if src.startswith('/') else os.path.join(ROOT, src)
        if r['status'] == 'live':
            if not os.path.exists(sp) or r['source']['grep'] not in open(sp, errors='ignore').read():
                drift.append(('SOURCE', r['id'], src, r['source']['grep']))
        for s in r['surfaces']:
            t = text_of(s['surface'])
            if t is None:
                if r['status'] == 'live':   # 10 Nov: a held/withdrawn row whose page is not built (or gone) does not block a ship
                    drift.append(('MISSING', r['id'], s['surface'], 'surface file not found'))
                continue
            present = norm(s['text']) in t
            if r['status'] == 'live' and not present:
                drift.append(('MISSING', r['id'], s['surface'], s['text'][:90]))
            if r['status'] in ('withdrawn', 'held') and present:   # 3 Nov: a held row (out for a rescore) must not be printed either
                drift.append(('ZOMBIE', r['id'], s['surface'], s['text'][:90]))
    from live_headlines import check_rows   # 10 Nov 2026 (cold read row 12): headline numbers that move on every read
    drift += check_rows(rows)
    n_live = sum(1 for r in rows.values() if r['status'] == 'live')
    n_lh = sum(1 for r in rows.values() if r.get('kind') == 'live_headline' and r['status'] == 'live')
    print(f'ledger: {len(rows)} rows ({n_live} live, {n_lh} live headlines read against their feeds); drift: {len(drift)}')
    for d in drift:
        print('  %-8s %-28s %-26s %s' % d)
    if '--coverage' in sys.argv:
        num = re.compile(r'(?<![\w.])[+-]?\d+\.\d+')
        keys = list(SURFACES) + sorted({s['surface'] for r in rows.values() for s in r['surfaces'] if s['surface'].startswith('site:')})
        for k in keys:
            t = text_of(k)
            if t is None: continue
            covered = ' '.join(norm(s['text']) for r in rows.values() if r['status'] == 'live' for s in r['surfaces'] if s['surface'] == k)
            nums = num.findall(t); un = [x for x in nums if x not in covered]
            print(f'  coverage {k:<40} {len(nums) - len(un):>4} of {len(nums):>4} decimal numbers in a ledger row')
    sys.exit(1 if drift else 0)


if __name__ == '__main__':
    main()
