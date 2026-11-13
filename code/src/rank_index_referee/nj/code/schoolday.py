"""Referee read of SPR SchoolDay, both years, for the 26 schools."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__)); import xl
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(HERE, 'code', 'particip.py')).read()
S = set(x.strip().strip("'") for x in src.split('CODES = [')[1].split(']')[0].replace('\n', '').split(','))
out = {}
for tag, path in (('2324', os.path.join(HERE, 'dl', 'spr2324.xlsx')), ('2425', sys.argv[1])):
    hdr = None
    for _, r, a in xl.rows(path, sheet='SchoolDay'):
        if hdr is None:
            if a and a[0] == 'CountyCode': hdr = a; print(tag, hdr)
            continue
        if len(a) > 4 and f'{a[0]}-{a[2]}-{a[4]}' in S:
            out.setdefault(a[5], {}).setdefault(tag, []).append({h: v for h, v in zip(hdr, a) if h not in ('CountyCode','CountyName','DistrictCode','DistrictName','SchoolCode','SchoolName')})
json.dump(out, open(os.path.join(HERE, 'out', 'schoolday.json'), 'w'), indent=1)
for k, v in out.items(): print(k, '|', v.get('2324'), '|', v.get('2425'))
