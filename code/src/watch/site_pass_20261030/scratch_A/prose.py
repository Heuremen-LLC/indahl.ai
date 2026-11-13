import re, sys, html, os
D=os.path.dirname(os.path.abspath(__file__))
def text(t):
    m = re.search(r'<main.*?</main>', t, re.S); b = m.group(0) if m else t
    b = re.sub(r'<script.*?</script>|<style.*?</style>', '', b, flags=re.S)
    b = re.sub(r'</(p|h\d|li|tr|section|div|ul|table)>', '\n', b)
    b = re.sub(r'<[^>]+>', '', b)
    return html.unescape(b)
for f in sorted(os.listdir(D+'/pages')):
    t = text(open(D+'/pages/'+f,encoding='utf-8').read())
    semi=[l.strip() for l in t.split('\n') if ';' in l]
    ems=sum(l.count('—')+l.count('–') for l in t.split('\n'))
    print(f, 'lines with ;', len(semi), 'total ;', t.count(';'), 'emdash/endash', ems)
