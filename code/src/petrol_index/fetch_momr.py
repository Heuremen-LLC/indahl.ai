#!/usr/bin/env python3
"""fetch_momr.py: caches OPEC Monthly Oil Market Report PDFs under data/raw/momr/. Public files, no login, no key. Never re-fetches a cached file.
Usage: fetch_momr.py [first YYYY-MM] [last YYYY-MM]. Writes data/raw/momr_fetch_log.json (url tried, status) so a refusal is on record."""
import os, sys, time, json, subprocess, datetime
H = os.path.dirname(os.path.abspath(__file__)); D = H + '/data/raw/momr'; os.makedirs(D, exist_ok=True)
LOG = H + '/data/raw/momr_fetch_log.json'; log = json.load(open(LOG)) if os.path.exists(LOG) else {}
MN = ['january','february','march','april','may','june','july','august','september','october','november','december']
def pat(y, m):
    n = MN[m-1]; b = 'https://www.opec.org/assets/assetdb/'
    return [b + 'momr-%s-%d.pdf' % (n, y), b + 'MOMR-%s-%d.pdf' % (n, y), b + 'momr-%s-%d-1.pdf' % (n, y), b + 'momr-%s-%d.pdf' % (n[:3], y)]
def get(url, out):
    r = subprocess.run(['curl', '-sSL', '-m', '90', '-A', 'Mozilla/5.0 (Macintosh) Safari/605', '-o', out, '-w', '%{http_code} %{content_type}', url], capture_output=True, text=True)
    code = r.stdout.split(' ')[0]; ok = code == '200' and 'pdf' in r.stdout and open(out, 'rb').read(4) == b'%PDF'
    if not ok and os.path.exists(out): os.remove(out)
    return ok, r.stdout
def main():
    a = (sys.argv[1] if len(sys.argv) > 1 else '2017-01').split('-'); b = (sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().strftime('%Y-%m')).split('-')
    y, m = int(a[0]), int(a[1])
    while (y, m) <= (int(b[0]), int(b[1])):
        key = '%d-%02d' % (y, m); out = '%s/momr_%s.pdf' % (D, key)
        if not os.path.exists(out):
            for rnd in range(3):
                done = False
                for u in pat(y, m):
                    ok, info = get(u, out); log.setdefault(key, []).append([u, info, int(time.time())])
                    if ok: done = True; break
                    time.sleep(1)
                if done: break
                time.sleep(4)
            print(key, 'ok' if os.path.exists(out) else 'MISSING', flush=True)
            json.dump(log, open(LOG, 'w'), indent=1)
        m += 1
        if m == 13: y, m = y + 1, 1
main()
