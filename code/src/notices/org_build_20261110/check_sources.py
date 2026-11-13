"""check_sources.py (10 Nov 2026): fetches each FOUND contact's source_url and checks the address is on that page
(plain text, mailto, or Cloudflare data-cfemail decoded). Writes source_check.json slug -> seen/unseen/error."""
import json, glob, re, urllib.request, html, concurrent.futures as CF, os
H = os.path.dirname(os.path.abspath(__file__))
C = [c for f in sorted(glob.glob(H + '/contacts_*.json')) for c in json.load(open(f)) if c['state'] == 'FOUND']
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
def cf(h):
    k = int(h[:2], 16); return ''.join(chr(int(h[i:i+2], 16) ^ k) for i in range(2, len(h), 2))
def one(c):
    try:
        s = urllib.request.urlopen(urllib.request.Request(c['source_url'], headers={'User-Agent': UA, 'Accept-Language': 'en'}), timeout=30).read().decode('utf-8', 'ignore')
    except Exception as e: return c['slug'], 'error: ' + str(e)[:80]
    s = html.unescape(s); dec = ' '.join(cf(x) for x in re.findall(r'data-cfemail="([0-9a-f]+)"', s)) + ' ' + ' '.join(cf(x) for x in re.findall(r'/cdn-cgi/l/email-protection#([0-9a-f]+)', s))
    t = (s + ' ' + dec).lower().replace('&#64;', '@').replace('%40', '@')
    return c['slug'], 'seen' if c['email'].strip().lower() in t else 'unseen'
with CF.ThreadPoolExecutor(10) as ex: r = dict(ex.map(one, C))
json.dump(r, open(H + '/source_check.json', 'w'), indent=1)
import collections; print(collections.Counter(v.split(':')[0] for v in r.values()))
for k, v in r.items():
    if v != 'seen': print(k, v)
