"""cadence_score.py: the series step of cadence_index/cadence_tick.py (WORDS, interval_days() and pdate(), lines 8 to 32, and the series and
overdue loop, lines 70 to 95, with most_overdue = over[:20], line 108), as written. Ages are each portal file's own fetch time minus the stated
modified date, as the plan says, so the clock of the run plays no part. Reads data/portal_*.json, writes out.json."""
import re, json, os, datetime as D
PORTALS = ['CMS', 'CDC', 'HealthData.gov', 'Veterans Affairs', 'Energy', 'Labor', 'FEMA', 'HealthCare.gov', 'BLS']
WORDS = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'bi-weekly': 14, 'monthly': 30, 'bimonthly': 61, 'quarterly': 91, 'semiannual': 182, 'semiannually': 182, 'annually': 365, 'annual': 365, 'yearly': 365, 'biennial': 730, 'biennially': 730}
def interval_days(s, decimals=True):
    if not s: return None
    s = s.strip().lower()
    if s in WORDS: return WORDS[s]
    N = r'(\d+(?:[.,]\d+)?)' if decimals else r'(\d+)'
    m = re.fullmatch(r'r/p(?:%sy)?(?:%sm)?(?:%sw)?(?:%sd)?(?:t(?:%sh)?(?:%sm)?(?:%ss)?)?' % ((N,) * 7), s)
    if not m or not any(m.groups()): return None
    y, mo, w, d, h, mi, se = [float((x or '0').replace(',', '.')) for x in m.groups()]; return y * 365 + mo * 30 + w * 7 + d + h / 24 + mi / 1440 + se / 86400
def pdate(s):
    try:
        s = s.replace('Z', '+00:00'); d = D.datetime.fromisoformat(s) if 'T' in s or ' ' in s else D.datetime.fromisoformat(s + 'T23:59:59+00:00')
        return (d if d.tzinfo else d.replace(tzinfo=D.timezone.utc)).timestamp()
    except Exception: return None
over = []
for n in PORTALS:
    f = f'data/portal_{re.sub("[^a-z0-9]+", "_", n.lower())}.json'
    if not os.path.exists(f): continue
    P = json.load(open(f)); ser = {}
    for r in P['rows']:
        lk = r['landing']; lk = lk.get('accessURL') if isinstance(lk, dict) else lk; key = lk or ('id:' + str(r['id'])); r['landing'] = lk
        mt0 = pdate(r['modified']) if r.get('modified') else None
        if key not in ser or (mt0 or 0) > (ser[key][1] or 0): ser[key] = (r, mt0)
        elif (mt0 or 0) == (ser[key][1] or 0) and (interval_days(r['cadence']) or -1) > (interval_days(ser[key][0]['cadence']) or -1): ser[key] = (r, mt0)
    for r in [v[0] for v in ser.values()]:
        d = interval_days(r['cadence']); mt = pdate(r['modified']) if r.get('modified') else None
        if d is None or mt is None: continue
        I = max(d, 2); age = P['fetched'] - mt
        if age > 2 * I * 86400: over.append(dict(portal=n, title=r['title'], agency=r['agency'], cadence=r['cadence'], modified=r['modified'], age_days=round(age / 86400), ratio=round(age / 86400 / I, 1)))
over.sort(key=lambda x: -x['ratio'])
json.dump(dict(most_overdue=over[:20]), open('out.json', 'w'), indent=1)
