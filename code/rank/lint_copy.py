#!/usr/bin/env python3
"""lint_copy.py: house public-copy checks on the visible text of neo.html (quoted JPL text is checked too, so a hit inside a quote is read and cleared in CHECKS.md) (main content only). Prints every hit; exit 1 on any."""
import re, sys, html, os
H = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(H, sys.argv[1] if len(sys.argv) > 1 else 'rank_body.html')).read()
main = t
vis = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<script.*?</script>', ' ', main)))
vis = re.sub(r'\s+', ' ', vis)
heads = [html.unescape(re.sub(r'<[^>]+>', '', h)) for h in re.findall(r'(?is)<h[1-3][^>]*>(.*?)</h[1-3]>', t)]
rules = [(r';', 'semicolon'), (r'\bby hand\b', '"by hand" (house: read in full)'), (r'\bapparatus\b', 'apparatus'),
         (r'\b(AI|artificial intelligence|Claude|language model|LLM|assistant)\b', 'AI statement'),
         (r'\b(stale|wrong|error|errors|mistake|outdated|failed to|neglect|careless|sloppy)\b', 'judgement word'),
         (r'\b(caused|due to|owing to|thanks to|as a result of)\b', 'cause wording'),
         (r'\bbecause\b', 'because (check no cause is named for a gap)'), (r'\bI\b|\bmy\b', 'first person singular')]
bad = 0
for pat, name in rules:
    for m in re.finditer(pat, vis):
        ctx = vis[max(0, m.start() - 90):m.end() + 90]
        print(f'{name}: ...{ctx}...'); bad += 1
for h in heads:
    if re.search(r'\d', h): print('count or digit in a heading:', h); bad += 1
print('hits', bad)
sys.exit(1 if bad else 0)
