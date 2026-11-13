"""Fetch a page with the house research User-Agent, save HTML and text, print matches.

Usage: python3 -I wgrab.py URL OUTPREFIX [regex ...]
"""
import sys, re, html, subprocess

UA = "HeuremenLLC-research/1.0 (https://indahl.ai)"
url, out = sys.argv[1], sys.argv[2]
keys = sys.argv[3:]
r = subprocess.run(['curl', '-sL', '-A', UA, '-m', '40', '-w', '\n__HTTP__%{http_code}', url],
                   capture_output=True)
raw = r.stdout.decode('utf8', 'ignore')
code = raw.rsplit('__HTTP__', 1)[-1].strip()
h = raw.rsplit('\n__HTTP__', 1)[0]
open(out + '.html', 'w').write(h)
t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
open(out + '.txt', 'w').write(t)
print('HTTP', code, 'chars', len(t))
for k in keys:
    ms = list(re.finditer(k, t, re.I))
    print('##', k, 'hits', len(ms))
    for m in ms[:3]:
        print('>>', t[max(0, m.start() - 250):m.start() + 400])
        print()
