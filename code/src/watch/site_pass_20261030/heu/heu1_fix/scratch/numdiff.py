"""numdiff.py FILE [FILE...]: compare visible text of each page with its backup: numbers, outcome words and hrefs that were removed or added."""
import re, html, sys, os, collections
ROOT='/Users/heuremen/bones-forge/heuremen.org'; B='/Users/heuremen/bones-forge/archive/heuremen_heu1_backups'
def visible(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<head>.*?</head>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace('−','-').replace('–','-').replace(' ',' ').replace('\xa0',' ')
    return s
NUM = re.compile(r'[+-]?\d[\d,]*(?:\.\d+)?')
OUT = re.compile(r'\b(ABOVE|BELOW|CONSISTENT|CANNOT[_ ]TELL|cannot tell|consistent with|above zero|below zero|above 0|below 0|not decided|excluded|resolved|not resolved)\b')
for f in sys.argv[1:]:
    rel = os.path.relpath(os.path.abspath(f), ROOT); b = os.path.join(B, rel + '.pre-heu1-20261030')
    old, new = open(b).read(), open(f).read()
    vo, vn = visible(old), visible(new)
    for name, rx in (('numbers', NUM), ('outcomes', OUT)):
        co, cn = collections.Counter(rx.findall(vo)), collections.Counter(rx.findall(vn))
        lost, gained = co - cn, cn - co
        if lost or gained: print(f'{rel} {name}: removed {dict(lost)} added {dict(gained)}')
    ho = collections.Counter(re.findall(r'href="([^"]+)"', old)); hn = collections.Counter(re.findall(r'href="([^"]+)"', new))
    if ho != hn: print(f'{rel} hrefs: removed {dict(ho-hn)} added {dict(hn-ho)}')
    print(f'{rel}: semicolons {vo.count(";")} -> {vn.count(";")}')
