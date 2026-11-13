"""Referee re-pull of CCD 2024-25 grade 9-12 enrollment and lunch counts via the Urban Institute API."""
import json, os, subprocess, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'HeuremenRANK-referee/0.1 (+https://indahl.ai/oy)'
IDS = {
    'Bergen County Academies': '340147000250', 'BCTHS Teterboro': '340147000262',
    'McNair': '340783002778', 'Edison Academy': '341008000395', 'Woodbridge Academy': '341008003428',
    'High Technology HS': '341750006095', 'Biotechnology HS': '341750006121',
    'Allied Health': '341804000584', 'Info Technology': '341804006134', 'UCMHS': '341804000214',
}


def get(url):
    out = subprocess.run(['curl', '-sS', '-A', UA, url], capture_output=True, text=True, timeout=120).stdout
    return json.loads(out)


res = {}
for name, nid in IDS.items():
    r = {'ncessch': nid}
    tot = 0
    for g in (9, 10, 11, 12):
        j = get(f'https://educationdata.urban.org/api/v1/schools/ccd/enrollment/2024/grade-{g}/?ncessch={nid}&race=99&sex=99')
        rows = [x for x in j.get('results', []) if x.get('race') == 99 and x.get('sex') == 99]
        e = rows[0]['enrollment'] if rows else None
        r[f'g{g}'] = e
        tot += e if isinstance(e, int) and e >= 0 else 0
    r['g9_12'] = tot
    j = get(f'https://educationdata.urban.org/api/v1/schools/ccd/directory/2024/?ncessch={nid}')
    d = j['results'][0]
    r.update({k: d.get(k) for k in ('school_name', 'enrollment', 'free_lunch', 'reduced_price_lunch', 'free_or_reduced_price_lunch')})
    res[name] = r
    print(name, r)
json.dump(res, open(os.path.join(HERE, 'out', 'ccd_repull.json'), 'w'), indent=1)
