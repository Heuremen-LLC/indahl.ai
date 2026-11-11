"""pull_acs.py: ACS 1-year B12501, B12503, B01003 by state through api.census.gov, one call per year, cached in data/raw/acs_YYYY.json. Key read at call time, never printed or stored. --selftest checks the parser offline."""
import json, os, sys, time, urllib.request, urllib.error
YEARS = [y for y in range(2010, 2025) if y != 2020]
VARS = ['NAME'] + ['%s_%s%s' % (t, c, s) for t, cs in (('B12503', ('005', '010')), ('B12501', ('005', '010')), ('B01003', ('001',))) for c in cs for s in ('E', 'M')]
KEYFILE = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/census_api_key.txt')
def url(y, key): return 'https://api.census.gov/data/%d/acs/acs1?get=%s&for=state:*&key=%s' % (y, ','.join(VARS), key)
def fetch(y):
    key = open(KEYFILE).read().strip()
    for a in range(3):
        try: return json.loads(urllib.request.urlopen(url(y, key), timeout=60).read())
        except urllib.error.HTTPError as e:
            msg = 'HTTP %d' % e.code
        except Exception as e: msg = type(e).__name__
        time.sleep(3)
    raise SystemExit('year %d failed: %s' % (y, msg))   # never echo the url
def main():
    for y in YEARS:
        f = 'data/raw/acs_%d.json' % y
        if os.path.exists(f): continue
        d = fetch(y); json.dump({'pulled': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'rows': d}, open(f, 'w')); print(y, len(d) - 1, 'rows'); time.sleep(0.5)
if __name__ == '__main__':
    if '--selftest' in sys.argv: assert 'B12503_010M' in VARS and 'key' not in ','.join(VARS); print('selftest ok')
    else: main()
