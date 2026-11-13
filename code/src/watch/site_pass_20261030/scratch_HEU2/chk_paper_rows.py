import json, re, sys, os, html
ROOT = os.path.expanduser('~/bones-forge')
S = os.path.join(ROOT, 'watch/site_pass_20261030/scratch_HEU2')

def canon(s):
    s = s.replace('\ufb01','fi').replace('\ufb02','fl').replace('\ufb00','ff').replace('\ufb03','ffi').replace('\ufb04','ffl')
    s = s.replace('◦','°').replace('\u2212','-').replace('–','-').replace('—','-').replace('\u2009',' ').replace('\xa0',' ')
    s = s.replace('µ','μ')
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'(?<=[A-Za-z])-(?=[A-Za-z])', '', s)
    return s.lower()

def norm_tex(s):
    # same as check_ledger.norm
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = s.replace('\\us{}', ' µs').replace('\\us', ' µs').replace('\\%', '%').replace('\\,', ' ').replace('\\textmu', 'µ')
    s = re.sub(r'\\(texttt|emph|textbf|mathrm)\{([^}]*)\}', r'\2', s)
    s = s.replace('\\pm', '±').replace('$', '').replace('{', '').replace('}', '').replace('^\\circ', '°').replace('\\circ', '°')
    s = s.replace('−', '-').replace('–', '-').replace('—', '-').replace('\u2009', ' ').replace('\xa0', ' ')
    s = s.replace('\\n', ' ')
    return re.sub(r'\s+', ' ', s).strip()

pdf = open(os.path.join(S,'a-readout-is-not-an-idle.txt')).read()
P = canon(pdf)
rows=[json.loads(l) for l in open(os.path.join(ROOT,'ledger/ledger.jsonl'))]
miss=[]; tot=0
for r in rows:
    for s in r['surfaces']:
        if s['surface']=='paper':
            tot+=1
            t = canon(norm_tex(s['text']))
            if r['status']=='live' and t not in P:
                miss.append((r['id'], s['text']))
print('paper surface entries', tot, 'not found in PDF text', len(miss))
for m in miss: print(m[0],'||',m[1][:160].replace('\n',' '))
