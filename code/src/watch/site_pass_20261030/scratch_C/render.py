import re, sys, glob, os, html, collections
from html.parser import HTMLParser
sys.path.insert(0, '.')
import parse as P
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
VOID = {'meta', 'link', 'br', 'img', 'hr', 'input', 'source', 'path', 'circle', 'polygon', 'rect', 'line', 'use', 'stop', 'wbr', 'col'}
class V(HTMLParser):
    def __init__(s):
        super().__init__(); s.stack = []; s.errs = []
    def handle_starttag(s, tag, attrs):
        if tag not in VOID: s.stack.append(tag)
    def handle_startendtag(s, tag, attrs): pass
    def handle_endtag(s, tag):
        if tag in VOID: return
        if s.stack and s.stack[-1] == tag: s.stack.pop()
        elif tag in s.stack:
            while s.stack and s.stack[-1] != tag:
                s.errs.append('unclosed <%s>' % s.stack.pop())
            s.stack.pop()
        else: s.errs.append('stray </%s>' % tag)
issues = collections.defaultdict(list)
MARK = re.compile(r'\{\{|\}\}|\{%|%\}|<\?|\$\{|\{[a-z_]+\}|%s\b|%\(|\bundefined\b|\bNaN\b|\bnull\b|\bNone\b|\bTODO\b|\bTBD\b|\bXXX\b|\bFIXME\b|\blorem\b|\[object|\binf\b|\bnan\b', re.I)
for n, p in pages.items():
    t = p['raw']
    v = V(); v.feed(t); v.close()
    if v.errs or v.stack: issues[n].append(('html', v.errs[:3], v.stack[:3]))
    body = p['body']
    txt = P.text(body)
    for m in MARK.finditer(txt):
        issues[n].append(('marker', m.group(0), txt[max(0, m.start()-50):m.end()+50]))
    # raw (non-text) markers in html source in main
    for m in re.finditer(r'\{\{|\}\}|\{%|%\}|\$\{|<\?', p['main']):
        issues[n].append(('rawmarker', m.group(0), p['main'][max(0, m.start()-40):m.end()+40]))
    # empty sections
    for k, vv in p['sections'].items():
        if k != '_head' and not P.text(vv).strip(): issues[n].append(('empty', k))
        if k != '_head' and len(P.text(vv)) < 4: issues[n].append(('tiny', k, P.text(vv)))
    # mojibake / odd chars
    for m in re.finditer(r'Ã.|â€|Â|�|´[a-z]|`[a-z]', txt):
        issues[n].append(('mojibake', m.group(0), txt[max(0, m.start()-40):m.end()+40]))
    # double escapes
    if re.search(r'&amp;(?:amp|lt|gt|quot|[a-z]+);', body): issues[n].append(('doubleescape', re.findall(r'&amp;[a-z]+;', body)[:3]))
    # unescaped < or & in text
    if re.search(r'&(?![a-zA-Z#0-9]+;)', body): issues[n].append(('bare&', re.findall(r'.{20}&(?![a-zA-Z#0-9]+;).{20}', body)[:2]))
    # double spaces / trailing space etc
    # semicolons in prose (house style)
    # empty href
    if re.search(r'href=""', p['raw']): issues[n].append(('emptyhref',))
    # doubled words
    for m in re.finditer(r'\b(\w{3,})\s+\1\b', txt, re.I):
        issues[n].append(('doubleword', m.group(0)))
    # doubled punctuation
    for m in re.finditer(r'\.\.(?!\.)|,,|;;|\.\s*\.(?!\.)|:\s*\.|\(\s*\)|\[\s*\]', txt):
        issues[n].append(('punct', m.group(0), txt[max(0, m.start()-40):m.end()+40]))
    # unbalanced brackets in each section
    for k in ('Published', 'Measured or recounted', 'QIA Calibration', 'How'):
        s = P.text(p['sections'][k])
        if s.count('(') != s.count(')'): issues[n].append(('paren-unbalanced', k, s.count('('), s.count(')'), s[:120]))
        if s.count('[') != s.count(']'): issues[n].append(('bracket-unbalanced', k, s.count('['), s.count(']'), s[:120]))
        if (s.count('“') != s.count('”')) or (s.count('"') % 2): issues[n].append(('quote-unbalanced', k, s.count('“'), s.count('”'), s.count('"'), s[:140]))
        if s.count("'") % 2 and "'" in s: issues[n].append(('apos-odd', k, s.count("'")))
print('pages with issues', len(issues))
cnt = collections.Counter(i[0] for v in issues.values() for i in v)
print(cnt)
import json
json.dump({k: [list(map(str, i)) for i in v] for k, v in issues.items()}, open('render_issues.json', 'w'), indent=1, ensure_ascii=False)
for kind in ('html', 'marker', 'rawmarker', 'empty', 'tiny', 'mojibake', 'doubleescape', 'bare&', 'emptyhref', 'doubleword', 'punct', 'paren-unbalanced', 'bracket-unbalanced', 'quote-unbalanced'):
    print('\n==', kind)
    for n, v in issues.items():
        for i in v:
            if i[0] == kind: print('  ', n, i[1:])
