#!/usr/bin/env python3
"""numcheck.py out/R1.json: every decimal number in each proposed 'new' text must appear in a source file under the folders named in 'evidence'."""
import json, re, os, sys, glob
def folders(ev):
    fs = set()
    for p in re.findall(r'(/Users/heuremen/[^\s,;\'")]+)', ev):
        p = p.rstrip('.')
        d = p if os.path.isdir(p) else os.path.dirname(p)
        while d and not os.path.isdir(d): d = os.path.dirname(d)
        if d and len(d) > 30: fs.add(d)
    for m in re.findall(r'(qia_runs/[\w.\-]+|public_mirror/[\w./\-]+|qia_leads/[\w./\-]+|arxiv_one_readout/[\w./\-]+)', ev):
        p = os.path.expanduser('~/bones-forge/') + m.rstrip('.')
        d = p if os.path.isdir(p) else os.path.dirname(p)
        if os.path.isdir(d) and len(d) > 40: fs.add(d)
    return fs
def text_of(fs):
    t = ''
    for d in fs:
        n = 0
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith(('.text', '.md', '.txt', '.json', '.py', '.jsonl', '.csv', '.html')):
                    p = os.path.join(root, f)
                    try:
                        if os.path.getsize(p) < 3e6: t += open(p, errors='ignore').read() + '\n'
                    except Exception: pass
                    n += 1
                    if n > 400: break
    return t
def toks(s):
    out = set()
    for m in re.finditer(r'(?<![\w.])[+\-−–]?\d*\.\d+(?:e[+-]?\d+)?|(?<![\w.,])\d{1,3}(?:,\d{3})+(?![\w])|(?<![\w.])\d{4,}(?![\w.])', s):
        out.add(m.group(0).lstrip('+-−–'))
    return out
if __name__ == '__main__':
    d = json.load(open(sys.argv[1]))
    for it in d['items']:
        new = it.get('new') or it.get('new_sub') or ''
        if not new: continue
        old = it.get('old') or it.get('old_sub') or ''
        ev = it.get('evidence', '')
        fs = folders(ev)
        corpus = text_of(fs) + ' ' + old + ' ' + ev
        miss = sorted(t for t in toks(new) if t not in corpus and t.replace(',', '') not in corpus)
        print(f"{it['finding']:6s} {it['id'][:30]:30s} {it['field']:16s} folders {len(fs)} missing {miss}")
