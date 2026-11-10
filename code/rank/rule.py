#!/usr/bin/env python3
"""RANK step two: the per-figure rule from PLAN.md (sealed b25e87f). One function, used for every school on every list.
  MATCH       same quantity, same year, equal after rounding the public figure to the precision US News prints
  MISMATCH    same quantity and year, different after that rounding
  CANNOT_TELL with a reason: year, not_found, definition, suppressed, floor_or_range_unsettled, paid_tier, not_printed
A floor US News prints (for example "> 95%") is settled by an exact public figure: MATCH if the figure is above the floor, MISMATCH if not.
A public figure that is itself binned or suppressed (for example ">95", "*") does not settle an exact US News figure: CANNOT_TELL.
Run this file to check the rule on synthetic rows with known answers. Standard library only. Heuremen LLC."""
import re
from decimal import Decimal, ROUND_HALF_UP

def _num(s):
    s = str(s).strip().replace(',', '').replace('%', '')
    return Decimal(s)

def decimals(s):
    s = str(s).strip().replace(',', '').replace('%', '')
    return len(s.split('.')[1]) if '.' in s else 0

def rnd(x, places):
    q = Decimal(1).scaleb(-places)
    return Decimal(x).quantize(q, rounding=ROUND_HALF_UP)

BIN = re.compile(r'^\s*(>=|<=|>|<|≥|≤)\s*([\d.]+)\s*%?\s*$')
RANGE = re.compile(r'^\s*([\d.]+)\s*-\s*([\d.]+)\s*$')
RATIO = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*:\s*1\s*$')
SUPP = {'*', '**', 'n<10', 'n/a', 'na', 'suppressed', '--', '-', 'a/v', 'tfs', '-1'}

def compare(usn, pub, usn_year, pub_year, same_quantity=True):
    """Return (outcome, reason). usn and pub are strings as printed and as published."""
    if usn is None or str(usn).strip().lower() in ('', 'n/a', 'a/v', '?'):
        return 'CANNOT_TELL', 'not_printed'
    if pub is None or str(pub).strip() == '':
        return 'CANNOT_TELL', 'not_found'
    if not same_quantity:
        return 'CANNOT_TELL', 'definition'
    if usn_year is None or pub_year is None or str(usn_year) != str(pub_year):
        return 'CANNOT_TELL', 'year'
    u, p = str(usn).strip(), str(pub).strip()
    if p.lower() in SUPP:
        return 'CANNOT_TELL', 'suppressed'
    mu, mp = BIN.match(u), BIN.match(p)
    if mp:   # the public figure is binned
        if mu and mu.groups() == mp.groups(): return 'MATCH', ''
        return 'CANNOT_TELL', 'floor_or_range_unsettled'
    if mu:   # US News prints a floor, public is exact
        op, lim = mu.group(1), Decimal(mu.group(2)); v = _num(p)
        ok = {'>': v > lim, '≥': v >= lim, '>=': v >= lim, '<': v < lim, '≤': v <= lim, '<=': v <= lim}[op]
        return ('MATCH', '') if ok else ('MISMATCH', '')
    ru, rp = RANGE.match(u), RANGE.match(p)
    if ru:
        if not rp: return 'CANNOT_TELL', 'definition'
        a = all(rnd(_num(rp.group(i)), decimals(ru.group(i))) == _num(ru.group(i)) for i in (1, 2))
        return ('MATCH', '') if a else ('MISMATCH', '')
    tu, tp = RATIO.match(u), RATIO.match(p)
    if tu:
        if not tp: return 'CANNOT_TELL', 'definition'
        return ('MATCH', '') if rnd(_num(tp.group(1)), decimals(tu.group(1))) == _num(tu.group(1)) else ('MISMATCH', '')
    try:
        uv, pv = _num(u), _num(p)
    except Exception:
        return 'CANNOT_TELL', 'definition'
    return ('MATCH', '') if rnd(pv, decimals(u)) == uv else ('MISMATCH', '')

if __name__ == '__main__':
    T = [  # usn, pub, uy, py, expected
        ('100%', '99.6', '2024', '2024', 'MATCH'), ('100%', '99.4', '2024', '2024', 'MISMATCH'), ('97%', '96.5', '2024', '2024', 'MATCH'),
        ('97%', '97', '2024', '2023', 'CANNOT_TELL'), ('> 95%', '97.2', '2024', '2024', 'MATCH'), ('> 95%', '94', '2024', '2024', 'MISMATCH'),
        ('100%', '>95', '2024', '2024', 'CANNOT_TELL'), ('> 95%', '>95%', '2024', '2024', 'MATCH'), ('100%', '*', '2024', '2024', 'CANNOT_TELL'),
        ('1520-1580', '1520-1580', 'f25', 'f25', 'MATCH'), ('1520-1580', '1510-1580', 'f25', 'f25', 'MISMATCH'), ('8:1', '8:1', 'f25', 'f25', 'MATCH'),
        ('8:1', '7.6:1', 'f25', 'f25', 'MATCH'), ('8:1', '7.4:1', 'f25', 'f25', 'MISMATCH'), ('4,561', '4561', 'f25', 'f25', 'MATCH'),
        ('4,561', '4562', 'f25', 'f25', 'MISMATCH'), ('6.1%', '6.08', '2025', '2025', 'MATCH'), ('3.96', '3.96', '2025', '2025', 'MATCH'),
        ('N/A', '97', '2024', '2024', 'CANNOT_TELL'), ('100%', '**', '2024', '2024', 'CANNOT_TELL'), ('4%', '4.4776', '2024', '2024', 'MATCH'), ('97%', '', '2024', '2024', 'CANNOT_TELL'),
    ]
    bad = 0
    for u, p, uy, py, exp in T:
        got = compare(u, p, uy, py)[0]
        if got != exp: bad += 1; print('FAIL', u, p, uy, py, 'expected', exp, 'got', got)
    print('rule self-test:', len(T) - bad, 'of', len(T), 'pass'); raise SystemExit(1 if bad else 0)
