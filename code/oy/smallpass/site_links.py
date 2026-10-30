"""site_links.py (30 Oct 2026, site pass F-8): for every roster school, which form of its site answers: https://domain or https://www.domain.
An HTTP answer of any status counts (a bot wall still opens for a reader); a DNS, certificate or timeout failure does not. Output site_links.json."""
import json, os, ssl, socket, urllib.request, urllib.error, concurrent.futures as F
H = os.path.dirname(os.path.abspath(__file__)); S = json.load(open(os.path.join(H, '..', 'schools.json')))
UA = {'User-Agent': 'Mozilla/5.0 (compatible; heuremen-oy/0.1; +https://indahl.ai/oy)'}
def probe(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA, method='GET'), timeout=20); return str(r.status)
    except urllib.error.HTTPError as e: return str(e.code)
    except Exception as e: return 'fail:' + type(e).__name__ + ':' + str(getattr(e, 'reason', e))[:60]
def one(d):
    b = probe('https://' + d); w = probe('https://www.' + d) if not d.startswith('www.') else b
    link = ('https://' + d) if not b.startswith('fail') else (('https://www.' + d) if not w.startswith('fail') else None)
    return d, dict(bare=b, www=w, link=link)
doms = sorted({s['domain'] for s in S})
with F.ThreadPoolExecutor(8) as ex: R = dict(ex.map(one, doms))
json.dump(R, open(os.path.join(H, 'site_links.json'), 'w'), indent=0)
print(len(R), 'domains;', sum(1 for v in R.values() if v['link'] and v['link'].startswith('https://www.')), 'use www;', sum(1 for v in R.values() if not v['link']), 'neither answers')
for d, v in R.items():
    if not v['link'] or v['bare'].startswith('fail'): print(' ', d, v)
