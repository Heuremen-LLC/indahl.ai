"""Referee copy lint for the New Jersey section: our own text only (quotes removed)."""
import html, re, sys
src = open(sys.argv[1], encoding='utf-8').read()
lines = src.split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('<h2>New Jersey</h2>'))
end = next(i for i, l in enumerate(lines) if l.startswith('<h2>National Blue Ribbon'))
sec = '\n'.join(lines[start:end])
for h in re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', sec):
    if re.search(r'\d', h): print('DIGIT IN HEADING:', h)
t = re.sub(r'(?s)<[^>]+>', ' ', sec)
t = html.unescape(t)
own = re.sub(r'“.*?”', ' ', t)          # drop quoted school words
if ';' in own: print('SEMICOLON:', [own[max(0,m.start()-60):m.start()+20] for m in re.finditer(';', own)])
words = r'\b(because|due to|caused?|reason(?:s)?|in order to|motive|inflat\w*|gam\w+|mislead\w*|wrong|error|false|erroneous|prestigious|impressive|elite|top-tier|best|excellent|outstanding|strong|weak|poor|good|bad|suspicious|questionable|notabl\w+|remarkabl\w+|surprising\w*|only|just|merely|clearly|obviously|AI|Claude|assistant|language model|generated|Opus)\b'
for m in re.finditer(words, own, re.I):
    print('WORD:', m.group(0), '|', re.sub(r'\s+', ' ', own[max(0, m.start()-90):m.end()+60]))
