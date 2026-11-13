#!/usr/bin/env python3
"""make_targets.py: writes data/targets.csv from the required production figures typed by eye from the OPEC statement images (see fetch_statements.py). Run gates on the typed values (arithmetic checks against printed increments)."""
import csv, os, sys
H = os.path.dirname(os.path.abspath(__file__)); P = 'https://www.opec.org/pr-detail/'; I = 'https://www.opec.org/assets/imagedb/pic/'
FULL = dict(Congo=277, **{'Equatorial Guinea': 70}, Gabon=177, Nigeria=1500, Azerbaijan=551, Bahrain=196, Brunei=83, Malaysia=401, Mexico=1753, Sudan=64, **{'South Sudan': 124})
EIGHT = ['Algeria', 'Iraq', 'Kuwait', 'Saudi Arabia', 'UAE', 'Kazakhstan', 'Oman', 'Russia']
# month -> (values in EIGHT order, statement slug, image id, table title as printed)
T = {
 '2025-05': ([919, 4049, 2443, 9200, 3015, 1486, 768, 9083], '244557-03-april-2025', '1743675427', 'Required Production Table (kbd), May 2025'),
 '2025-06': ([928, 4086, 2466, 9367, 3092, 1500, 775, 9161], '563-03-may-2025', '1746270556', 'June 2025 Required Production (kbd)'),
 '2025-08': ([948, 4171, 2518, 9756, 3272, 1532, 792, 9344], '569-05-july-2025', '1751707386', 'Required Production Tables (kbd), Aug 2025'),
 '2025-09': ([959, 4220, 2548, 9978, 3375, 1550, 801, 9449], '1518572-03-august-2025', '1754220274', 'Required Production Table (kbd), September 2025'),
 '2025-12': ([971, 4273, 2580, 10103, 3411, 1569, 811, 9574], '1574579-02-november-2025', '1762099998', 'December 2025 until March 2026 Required Production Table'),
 '2026-01': ([971, 4273, 2580, 10103, 3411, 1569, 811, 9574], '1574579-02-november-2025', '1762099998', 'December 2025 until March 2026 Required Production Table'),
 '2026-02': ([971, 4273, 2580, 10103, 3411, 1569, 811, 9574], '1574579-02-november-2025', '1762099998', 'December 2025 until March 2026 Required Production Table'),
 '2026-03': ([971, 4273, 2580, 10103, 3411, 1569, 811, 9574], '1574579-02-november-2025', '1762099998', 'December 2025 until March 2026 Required Production Table'),
 '2026-04': ([977, 4299, 2596, 10166, 3429, 1579, 816, 9637], '593-1-march-2026', '1772363311', 'April 2026 Required Production Table (kbd)'),
 '2026-05': ([983, 4326, 2612, 10228, 3447, 1589, 821, 9699], '597-5-april-2026', '1775398028', 'May 2026 Required Production Table (kbd)'),
 '2026-08': ([1001, 4405, 2660, 10416, None, 1618, 836, 9887], '1835609-5-july-2026', '1783246215', 'August 2026 Required Production Table (kbd), seven countries, no UAE'),
 '2026-09': ([1007, 4431, 2676, 10478, None, 1628, 841, 9949], '2033620-1-november-2026', '1793534438', 'December 2026 Required Production Table (kbd); the statement text says September 2026 required production is maintained for December 2026, so the table is the September 2026 level; seven countries, no UAE'),
}
INC = {'2026-04': 206, '2026-05': 206, '2026-08': 188, '2025-12': 137}   # printed Total of Production Increments
def months():
    y, m = 2024, 11
    while (y, m) <= (2026, 10):
        yield '%d-%02d' % (y, m); m += 1
        if m == 13: y, m = y + 1, 1
def gates():
    ok = True; msg = []
    def step(a, b, tot, tol=2):
        d = sum(x for x in b if x is not None) - sum(x for x, y in zip(a, b) if y is not None); return abs(d - tot) <= tol, d
    for cur, prev in (('2026-04', '2026-03'), ('2026-05', '2026-04')):
        r, d = step(T[prev][0], T[cur][0], INC[cur]); ok &= r; msg.append('%s minus %s = %d vs printed %d %s' % (cur, prev, d, INC[cur], 'ok' if r else 'FAIL'))
    r, d = step(T['2025-05'][0], T['2025-06'][0], 411); ok &= r; msg.append('2025-06 minus 2025-05 = %d vs printed 411 %s' % (d, 'ok' if r else 'FAIL'))
    r, d = step(T['2025-08'][0], T['2025-09'][0], 547); ok &= r; msg.append('2025-09 minus 2025-08 = %d vs printed 547 %s' % (d, 'ok' if r else 'FAIL'))
    # August 2026 against May 2026: three increments of 188-206 each is not a printed figure, so only the printed 188 is checked against the seven countries' August minus June, not available. Seven-country September step.
    r, d = step(T['2026-08'][0], T['2026-09'][0], 188 - 18 + 0, tol=70); msg.append('2026-09 minus 2026-08 (seven countries) = %d, no printed total, shown only' % d)
    return ok, msg
def main():
    ok, msg = gates()
    rows = []
    for mo in months():
        for c, v in FULL.items():
            if mo >= '2025-01': rows.append([c, mo, v, P + '28-05-dec-2024.html', I + '1738743572.png', 'Required Production Levels for 2025 and 2026 (38th ONOMM, Dec 2024; reaffirmed 41st ONOMM June 2026)'])
        if mo in T:
            vals, slug, img, title = T[mo]
            for c, v in zip(EIGHT, vals):
                if v is not None: rows.append([c, mo, v, P + slug + '.html', I + img + '.png', title])
    with open(H + '/data/targets.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['member', 'month', 'target_tbd', 'source_url', 'image_url', 'table']); w.writerows(rows)
    print(len(rows), 'target rows'); print('\n'.join(msg)); print('TARGET GATE', 'PASS' if ok else 'FAIL')
    import json; json.dump(dict(passed=ok, lines=msg), open(H + '/data/targets_gate.json', 'w'), indent=1)
    sys.exit(0 if ok else 1)
main()
