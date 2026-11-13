"""Referee check of the participation table: SPR schoolwide participation (ELA, Math) both years,
and whether Registered To Test / Not Tested are suppressed for the 26 schools in every test-file row."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.join(HERE, 'dl')
SPR2425 = sys.argv[1] if len(sys.argv) > 1 else None
CODES = ['03-0290-020', '03-0290-070', '03-1760-065', '03-4390-120', '13-2730-090', '13-3190-070', '17-2390-002',
         '17-2390-075', '17-2390-340', '17-5240-140', '23-3150-010', '23-3150-070', '25-2720-050', '25-3260-010',
         '25-3260-028', '25-4570-050', '25-4980-050', '27-0785-060', '27-3100-060', '31-4010-310', '39-5260-020',
         '39-5260-030', '39-5260-040', '80-6036-921', '80-6081-967', '80-7540-930']
S = set(CODES)
out = {'spr': {}, 'testfiles': {}}

# 1. test files: every row for the 26 schools
unsupp = []
nrows = 0
for p in sorted(glob.glob(os.path.join(DL, '*_23??.xlsx')) + glob.glob(os.path.join(DL, '*_24??.xlsx'))):
    b = os.path.basename(p)
    if b.startswith('spr'):
        continue
    for _, r, a in xl.rows(p):
        if r <= 3 or len(a) < 11:
            continue
        k = f'{a[0]}-{a[2]}-{a[4]}'
        if k in S:
            nrows += 1
            if a[8] not in ('*',) or a[9] not in ('*',):
                unsupp.append((b, r, k, a[5], a[6], a[7], a[8], a[9], a[10]))
out['testfiles'] = {'rows_checked': nrows, 'not_star': unsupp}
print('test-file rows for the 26 schools:', nrows, 'rows where registered or not-tested is not "*":', len(unsupp))
for u in unsupp[:40]:
    print('  ', u)


def spr(path, sheets, yearcol=None):
    res = {}
    for sh in sheets:
        hdr = None
        for _, r, a in xl.rows(path, sheet=sh):
            if hdr is None:
                if a and a[0] in ('CountyCode', 'County Code'):
                    hdr = a
                    print(sh, hdr)
                continue
            if len(a) < 5:
                continue
            k = f'{a[0]}-{a[2]}-{a[4]}'
            if k in S:
                res.setdefault(sh, []).append(dict(zip(hdr, a), _row=r))
    return res


s1 = spr(os.path.join(DL, 'spr2324.xlsx'), ['ELAParticipationPerformance', 'MathParticipationPerformance'])
for sh, rows in s1.items():
    for d in rows:
        if d.get('Student Groups') == 'Schoolwide':
            out['spr'].setdefault(d['CountyCode'] + '-' + d['DistrictCode'] + '-' + d['SchoolCode'], {})[sh[:3] + '_2324'] = (d['% of Students taking test'], d['Valid Scores'], d['_row'])
if SPR2425:
    s2 = spr(SPR2425, ['ELAParticipationPerformance', 'MathParticipationPerformance'])
    for sh, rows in s2.items():
        for d in rows:
            grp = d.get('StudentGroup') or d.get('Student Groups') or d.get('StudentGroups')
            yr = d.get('SchoolYear', '')
            if grp in ('Schoolwide', 'All Students') and yr in ('', '2024-25', '2024-2025'):
                k = d['CountyCode'] + '-' + d['DistrictCode'] + '-' + d['SchoolCode']
                pr = [v for kk, v in d.items() if 'articipation' in kk and 'School' in kk]
                out['spr'].setdefault(k, {})[sh[:3] + '_2425'] = (pr, d['_row'], {kk: v for kk, v in d.items() if kk not in ('CountyName', 'DistrictName')})
json.dump(out, open(os.path.join(HERE, 'out', 'particip.json'), 'w'), indent=1, default=str)
for k in CODES:
    print(k, out['spr'].get(k))
