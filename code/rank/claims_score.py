#!/usr/bin/env python3
"""RANK, New Jersey: public rank claims set against the US News lists read on 2026-11-10 (PLAN Addendum 1).
Each claim is matched by a quote fragment. For each, the stated rank, list and edition are written here as the quote states them, and the
edition and list are as the page names them (the pull agent's edition_named and list_named, read from each saved copy, which may name the edition outside the quoted sentence). The
record is the rank on the captured list (raw/nj_*_20261110.txt, raw/nu_20261110.txt). MATCH needs the stated rank, list and edition to equal
the record. A claim about an edition that was not read, or that names no edition, or names a list not read, is CANNOT_TELL.
Output: data/claims_scored.json. Heuremen LLC."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
C = json.load(open('public/nj_claims/claims.json', encoding='utf-8'))
RAW = {f: open(f, encoding='utf-8').read() for f in ('raw/nj_hs_20261110.txt', 'raw/nj_k8_20261110.txt', 'raw/nj_colleges_20261110.txt')}
def rec(file, needle):
    assert needle in RAW[file], (file, needle); return needle
# fragment -> (stated, record or None, outcome, reason)
T = [
 ('High Technology High School – Ranks #1', 'NJ rank 1, Best High Schools in New Jersey, 2025-2026', None, 'CANNOT_TELL', 'the 2025-2026 edition was not read'),
 ('Biotechnology High School – Ranks #6', 'NJ rank 6, Best High Schools in New Jersey, 2025-2026', None, 'CANNOT_TELL', 'the 2025-2026 edition was not read'),
 ('perennial is placed highly', 'national rank 33, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('the Woodbridge Academy was 70th', 'national rank 70, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('Engineering Technologies in Edis', 'top public high school in New Jersey, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('was ranked fifth in New Jersey', 'NJ rank 5, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('ranked fourth within New Jersey', 'NJ rank 4, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('named the No. 1 elementary school in New Je', 'NJ elementary rank 1, 2027', ('raw/nj_k8_20261110.txt', '#1;School 28;'), 'MATCH', ''),
 ('prestigious title of Best Elementary School', 'best elementary school in the state, no edition named', ('raw/nj_k8_20261110.txt', '#1;School 28;'), 'CANNOT_TELL', 'no edition named'),
 ('9TH BEST PUBLIC ELEMENTARY SCHOOL', 'NJ elementary rank 9 and NJ middle rank 14, 2025', None, 'CANNOT_TELL', 'the 2025 edition was not read'),
 ('ranked No. 2 among New Jersey elementary schools', 'NJ elementary rank 2, 2027', ('raw/nj_k8_20261110.txt', '#2;Milton Avenue School;'), 'MATCH', ''),
 ('Alexander Hamilton Elementary School ranked #8 in New Jersey', 'NJ elementary rank 8, edition named 2026-2027', ('raw/nj_k8_20261110.txt', '#9;Alexander Hamilton School;'), 'CANNOT_TELL',
  'the edition is named 2026-2027 and US News names its list 2027. The 2027 list read on 2026-11-10 shows rank 9'),
 ('#1 Best School District in Essex County', 'district rank in Essex County, 2025', None, 'CANNOT_TELL', 'a district list, not read'),
 ('top 4% of Elementary and Mid', 'top 4 percent in New Jersey, no edition named', None, 'CANNOT_TELL', 'no rank or edition named'),
 ('ranks No. 59 among 422 national universities', 'National Universities rank 59, 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#59 (tie);Stevens Institute of Technology;'), 'MATCH', ''),
 ('Overall U.S. News & World Report : No. 59 nationally', 'national rank 59, no edition named', ('raw/nj_colleges_20261110.txt', '#59 (tie);Stevens Institute of Technology;'), 'CANNOT_TELL', 'no edition named'),
 ('NJIT tied for No. 85 overall among national universities', 'National Universities rank 85 (tie), 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#85 (tie);New Jersey Institute of Technology;'), 'MATCH', ''),
 ('No. 40 position among the nation', 'top public universities rank 40', None, 'CANNOT_TELL', 'the top public schools list was not read'),
 ('Top 100 National University', 'top 100 National Universities, no edition named', None, 'CANNOT_TELL', 'no edition named'),
 ('placing NJIT No. 84', 'National Universities rank 84, page dated 2024-09-24', None, 'CANNOT_TELL', 'that edition was not read'),
 ('#14 top public university', 'top public universities rank 14', None, 'CANNOT_TELL', 'the top public schools list was not read'),
 ('Association of American Universities', 'National Universities rank 44, 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#44 (tie);Rutgers University--New Brunswick;'), 'MATCH', ''),
 ('#32 among America', 'top public universities rank 32', None, 'CANNOT_TELL', 'the top public schools list was not read'),
 ('It was also listed at #73 among national universities', 'National Universities rank 73, 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#73 (tie);Rutgers University--Newark;'), 'MATCH', ''),
 ('moved up to #43 from #46', 'a rank of 43 on a list the sentence does not name', None, 'CANNOT_TELL', 'list not named in the sentence'),
 ('Rutgers-Newark is #73 and Rutgers-Camden is #95', 'National Universities ranks 73 and 95, 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#95 (tie);Rutgers University--Camden;'), 'MATCH', ''),
 ('ranked Massachusetts Institute of Technology No. 1', 'Princeton rank 2, Best National Universities, 2027', ('raw/nj_colleges_20261110.txt', '#2;Princeton University;'), 'MATCH', ''),
 ('for the 13th consecutive year', 'National Universities rank 1, page dated 2023-09-18', None, 'CANNOT_TELL', 'that edition was not read'),
 ('No. 156 overall among national universities', 'National Universities rank 156, edition 2027 (up from 158 in 2026)', ('raw/nj_colleges_20261110.txt', '#156 (tie);Montclair State University;'), 'MATCH', ''),
 ('No. 79 among national public institutions', 'top public schools rank 79', None, 'CANNOT_TELL', 'the top public schools list was not read'),
 ('No. 84 among national public institutions', 'top public schools rank 84', None, 'CANNOT_TELL', 'the top public schools list was not read'),
 ('Monmouth placed No. 169 among 422 National Universities', 'National Universities rank 169, 2027 named on the page', ('raw/nj_colleges_20261110.txt', '#169 (tie);Monmouth University;'), 'MATCH', ''),
 ('No. 83 among Top Private National Universities', 'top private universities rank 83', None, 'CANNOT_TELL', 'the top private schools list was not read'),
 ('In their 2026 list', 'National Liberal Arts Colleges rank 85, edition named 2026 list', ('raw/nj_colleges_20261110.txt', '#85 (tie) Drew University, National Liberal Arts Colleges'), 'CANNOT_TELL',
  'the edition is named the 2026 list and US News names its list 2027. The 2027 list read shows rank 85 (tie)'),
 ('Drew ranked tied for 84', 'National Liberal Arts Colleges rank 84 (tie), page dated 2025-09', None, 'CANNOT_TELL', 'that edition was not read'),
 ('Best Colleges 2027', 'National Universities, Best Colleges 2027 (rank in the quote)', ('raw/nj_colleges_20261110.txt', '#156 (tie);Seton Hall University;'), None, ''),
 ('rose seven spots', 'an earlier edition', None, 'CANNOT_TELL', 'that edition was not read'),
 ('In the 2027 U.S. News & World Report rankings, Rowan', 'National Universities rank 191, 2027', ('raw/nj_colleges_20261110.txt', '#191 (tie);Rowan University;'), 'MATCH', ''),
 ('ranked Rowan #92 among public national universities', 'top public universities rank 92, page dated 2024-09-24', None, 'CANNOT_TELL', 'that list and edition were not read'),
]
out = []
for c in C:
    q = c['quote']; hit = [t for t in T if t[0] in q]
    assert len(hit) == 1, (c['school'], q[:80], len(hit))
    frag, stated, record, oc, why = hit[0]
    if oc is None:   # Seton Hall 2027: read the rank from the quote itself
        m = re.search(r'No\. (\d+)', q); stated = f'National Universities rank {m.group(1)}, Best Colleges 2027' if m else stated
        oc = 'MATCH' if m and m.group(1) == '156' else 'CANNOT_TELL'; why = '' if oc == 'MATCH' else 'no rank in the quote'
    rtxt = rec(*record) if record else ''
    q = re.sub(r'\s+([,:’\'])', r'\1', q).replace('U .S.', 'U.S.')
    if '•' in q: q = q.replace(' • ', ' … ').replace('•', '…')
    if q.startswith('Overall U.S. News & World Report: No. 59'): q = 'No. 59 nationally'
    out.append(dict(edition_named=c.get('edition_named'), list_named=c.get('list_named'), school=c['school'], publisher=c['publisher'], quote=q, url=c['url'], date_on_page=c.get('date_on_page'), stated=stated, record=rtxt, outcome=oc, reason=why))
assert len(out) == len(C)
json.dump(out, open('data/claims_scored.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(o['outcome'] for o in out))
