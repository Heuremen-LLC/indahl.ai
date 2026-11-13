#!/usr/bin/env python3
"""posthoc_daycheck.py: DEFINED AFTER THE DATA (10 Nov 2026). TikTok's published daily statement totals from the DSA database download
page (platform filter, platform_id 30) against TikTok's per-day totals in the complete aggregates. Sizes the days that failed the
committed day check (KG3-days). Writes data/posthoc_daycheck.json. Committed outcomes are not changed by this file."""
import os, re, json, html, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'data', 'raw', 'dsa_pages'); os.makedirs(D, exist_ok=True)
UA = 'heuremen-social/0.1 (+https://indahl.ai/social)'
pub = {}
for page in range(1, 60):
    f = os.path.join(D, 'tiktok_p30_page%d.html' % page)
    if not os.path.exists(f) or time.time() - os.path.getmtime(f) > 6 * 3600:
        u = 'https://transparency.dsa.ec.europa.eu/explore-data/download?platform_id=30&page=%d' % page
        b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60).read()
        open(f, 'wb').write(b); time.sleep(1)
    tx = open(f, encoding='utf8', errors='ignore').read()
    tx = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', tx, flags=re.S); tx = html.unescape(re.sub(r'<[^>]+>', ' ', tx)); tx = re.sub(r'\s+', ' ', tx)
    got = {k: int(v.replace(' ', '')) for k, v in re.findall(r'(20\d\d-\d\d-\d\d) ((?:\d{1,3} )*\d{1,3}) zip', tx)}
    if not got:
        break
    pub.update(got)
    if min(got) <= '2023-09-01':
        break
import duckdb
con = duckdb.connect()
agg = {str(d): int(n) for d, n in con.execute("select created_day, sum(n) from read_parquet('%s') group by 1" % os.path.join(H, 'data', 'raw', 'dsa_tiktok', 'complete_*.parquet')).fetchall()}
days = sorted(pub)
rows = [dict(day=d, published=pub[d], aggregate=agg.get(d, 0), diff=agg.get(d, 0) - pub[d]) for d in days]
off = [r for r in rows if r['published'] and abs(r['diff']) > 0.01 * r['published']]
exact = sum(1 for r in rows if r['diff'] == 0)
out = dict(defined_after_the_data=True, source='https://transparency.dsa.ec.europa.eu/explore-data/download?platform_id=30', pages_read=page,
           days=len(rows), first=days[0] if days else None, last=days[-1] if days else None, exact=exact, off_by_more_than_1pct=off,
           check_days={d: next((r for r in rows if r['day'] == d), None) for d in ('2026-02-09', '2026-02-10', '2026-02-11', '2026-02-12', '2026-05-30', '2026-05-31', '2026-09-29', '2026-09-30', '2026-10-01', '2026-10-02', '2026-10-03')},
           shortfall_30sep_2oct=sum(max(0, r['published'] - r['aggregate']) for r in rows if r['day'] in ('2026-09-30', '2026-10-01', '2026-10-02')),
           published=pub, differing_days=[r for r in rows if r['diff'] != 0])
json.dump(out, open(os.path.join(H, 'data', 'posthoc_daycheck.json'), 'w'), indent=1)
print('days', out['days'], 'exact', out['exact'], 'off >1%', len(out['off_by_more_than_1pct']), 'differing', len(out['differing_days']))
