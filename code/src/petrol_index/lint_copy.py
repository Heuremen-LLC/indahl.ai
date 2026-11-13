#!/usr/bin/env python3
"""lint_copy.py: house public-copy checks (same rules as census_vintages/lint_copy.py) on petrol_body.html and the headline line, plus a check that no price word appears. Exit 1 on any hit."""
import re, sys, html, os, json
H = os.path.dirname(os.path.abspath(__file__))
t = open(H + '/petrol_body.html').read() + ' ' + json.load(open(H + '/petrol_headline.json'))['line']
vis = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
heads = [html.unescape(re.sub(r'<[^>]+>', '', h)) for h in re.findall(r'(?is)<h[1-3][^>]*>(.*?)</h[1-3]>', t)]
rules = [(r';', 'semicolon'), (r'\bby hand\b', 'by hand'), (r'\bapparatus\b', 'apparatus'), (r'\b(AI|artificial intelligence|Claude|language model|LLM|assistant)\b', 'AI statement'),
         (r'\b(stale|wrong|error|errors|mistake|outdated|failed to|neglect|careless|sloppy)\b', 'judgement word'), (r'\b(caused|due to|owing to|thanks to|as a result of)\b', 'cause wording'),
         (r'\bbecause\b', 'because'), (r'\bI\b|\bmy\b', 'first person singular'), (r'(?i)\b(price|prices|pricing|\$|dollar|cheap|cost)\b', 'price word'),
         (r'(?i)\b(war|sanction|sanctions|embargo|government|regime|attack|politic\w*)\b', 'politics word'), (r'(?i)\b(violat\w*|cheat\w*|broke|breach\w*|non-?complian\w*)\b', 'accusation word')]
bad = 0
for pat, name in rules:
    for m in re.finditer(pat, vis):
        print(name + ': ...' + vis[max(0, m.start() - 80):m.end() + 80] + '...'); bad += 1
for h in heads:
    if re.search(r'\d', h): print('digit in heading:', h); bad += 1
print('hits', bad); sys.exit(1 if bad else 0)
