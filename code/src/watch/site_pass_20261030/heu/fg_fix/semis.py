"""List semicolons in the visible text of an HTML file (entities decoded, style stripped), with line numbers."""
import re, html, sys
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read()
    body = s.split('</style>', 1)[1] if '</style>' in s else s
    off = s[:len(s) - len(body)].count('\n')
    n = 0
    for i, line in enumerate(body.split('\n')):
        t = html.unescape(re.sub(r'<[^>]+>', '', line))
        for m in re.finditer(';', t):
            n += 1; print(f'{f.split("/")[-1]}:{i + 1 + off}: ...{t[max(0, m.start() - 60):m.start() + 40]}...')
    print(f'{f}: {n} semicolons in visible text')
