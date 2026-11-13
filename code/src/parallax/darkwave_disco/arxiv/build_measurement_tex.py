#!/usr/bin/env python3
"""build_measurement_tex.py -- MEASUREMENT_PAPER_20261004.md -> measurement/main.tex -> main.pdf (tectonic).
Form only: headings, paragraphs, lists, tables, math notation. The markdown is the source of truth."""
import os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'MEASUREMENT_PAPER_20261004.md'); OUTD = os.path.join(HERE, 'measurement')
UNI = [('χ²', r'\(\chi^2\)'), ('φ', r'\(\varphi\)'), ('ⁿ', r'\(^n\)'), ('±', r'\(\pm\)'), ('−', r'\(-\)'), ('×', r'\(\times\)'), ('²', r'\(^2\)'), ('π', r'\(\pi\)'), ('σ', r'\(\sigma\)'),
       ('χ', r'\(\chi\)'), ('→', r'\(\to\)'), ('Δ', r'\(\Delta\)'), ('√', r'\(\surd\)'), ('ρ', r'\(\rho\)'), ('⟩', r'\(\rangle\)'), ('⟨', r'\(\langle\)'), ('µ', r'\textmu{}'), ('–', '--'), ('τ', r'\(\tau\)'), ('ω', r'\(\omega\)'), ('ö', r'\"o'), ('ü', r'\"u')]


def tex(s):
    s = s.replace('&#124;', '\x00').replace('\\', r'\textbackslash{}')
    for a, b in (('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_'), ('$', r'\$'), ('§', r'\S{}'), ('^', r'\^{}')):
        s = s.replace(a, b)
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\emph{\1}', s)
    s = re.sub(r'`(.+?)`', r'\\texttt{\1}', s)
    s = re.sub(r'"([^"]+)"', r"``\1''", s)
    s = re.sub(r'\|([012+])>', r'\\(|\1\\rangle\\)', s)
    for a, b in UNI: s = s.replace(a, b)
    s = re.sub(r'(\d[\d.]*)(\s?|-)us\b', lambda m: m.group(1) + (r'\,' if m.group(2) == ' ' else m.group(2)) + r'\textmu s', s)
    s = re.sub(r'(?<=\s)us\b', r'\\textmu s', s)
    s = s.replace('->', r'\(\to\)').replace('~', r'\(\sim\)').replace('<', r'\textless{}').replace('>', r'\textgreater{}')
    s = s.replace('[', '{[}').replace(']', '{]}').replace('\x00', r'\textbar{}')
    return s


def table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\|\s*-', r)]
    n = max(len(r) for r in cells)
    body = [' & '.join(tex(c) for c in r + [''] * (n - len(r))) + r' \\' for r in cells]
    if max(len(c) for r in cells for c in r) > 45:                      # long cells wrap instead of shrinking the whole table
        body = [x.replace(r'\_', r'\_\allowbreak{}') for x in body]       # long call names break at their underscores
        cols = ''.join('l' if max(len(r[i]) if i < len(r) else 0 for r in cells[1:]) <= 12 else r'>{\raggedright\arraybackslash}X' for i in range(n))
        t = r'\begin{xltabular}{\linewidth}{' + cols + '}\n\\hline\n' + body[0] + '\n\\hline\n\\endhead\n' + '\n'.join(body[1:]) + '\n\\hline\n\\end{xltabular}'
        return r'\par\smallskip\noindent{\scriptsize\setlength{\tabcolsep}{3pt}' + t + r'}\par\smallskip'
    t = r'\begin{tabular}{' + 'l' * n + '}\n\\hline\n' + body[0] + '\n\\hline\n' + '\n'.join(body[1:]) + '\n\\hline\n\\end{tabular}'
    return r'\par\smallskip\noindent\resizebox{\linewidth}{!}{' + t + r'}\par\smallskip'


def main():
    L = open(SRC, encoding='utf-8').read()
    for e, u in (('&minus;', '−'), ('&ndash;', '–'), ('&plusmn;', '±'), ('&rang;', '⟩'), ('&lang;', '⟨'), ('&phi;', 'φ'), ('&times;', '×'), ('&micro;', 'µ')): L = L.replace(e, u)
    L = L.split('\n')
    title = L[0][2:].strip(); i = 1
    out = []; para = []; lst = None; rows = []
    def flush():
        nonlocal para
        if para: out.append(tex(' '.join(x.strip() for x in para)) + '\n'); para = []
    def endlist():
        nonlocal lst
        if lst: out.append(r'\end{' + lst + '}'); lst = None
    author = affil = ''
    while i < len(L) and not L[i].startswith('## '):
        t = L[i].strip()
        if t.startswith('**') and not author and t.endswith('**'): author = t.strip('*')
        elif t == 'Heuremen': affil = t
        elif t.startswith('*Draft'): date = t.strip('*')
        elif t and not t.startswith('---'): para.append(t)
        i += 1
    front = tex(' '.join(para)); para = []
    in_abs = False
    for ln in L[i:]:
        t = ln.rstrip()
        if t.startswith('|'):
            flush(); endlist(); rows.append(t); continue
        if rows: out.append(table(rows)); rows = []
        if t.startswith('## ') or t.startswith('### '):
            flush(); endlist()
            if in_abs: out.append(r'\end{abstract}'); in_abs = False
            h = t.lstrip('#').strip()
            if h == 'Abstract': out.append(r'\begin{abstract}'); in_abs = True; continue
            h = re.sub(r'^\d+(\.\d+)?\s+', '', h)
            if h in ('Acknowledgments', 'References'):
                out.append(r'\section*{' + tex(h) + '}'); continue
            if h.startswith('Appendix A'):
                out.append(r'\appendix\section{' + tex(h.split('. ', 1)[1]) + '}'); continue
            if t.startswith('### ') and h in ('Totals by vendor and day', 'Families, in date order'):
                out.append(r'\subsection*{' + tex(h) + '}'); continue
            out.append((r'\section{' if t.startswith('## ') else r'\subsection{') + tex(h) + '}'); continue
        if t.strip() in ('', '---'):
            flush()
            if t.strip() == '---': endlist()
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', t); b = re.match(r'^- (.*)', t)
        if m or b:
            flush(); kind = 'enumerate' if m else 'itemize'
            if lst != kind: endlist(); out.append(r'\begin{' + kind + '}'); lst = kind
            out.append(r'\item ' + tex((m or b).group(2 if m else 1))); continue
        if lst and ln.startswith('   '): out[-1] += ' ' + tex(t.strip()); continue
        endlist(); para.append(t)
    flush(); endlist()
    if rows: out.append(table(rows))
    doc = [r'\documentclass[11pt]{article}', r'\usepackage[margin=1in]{geometry}', r'\usepackage{amsmath,amssymb,textcomp,graphicx,tabularx,array,xltabular}', r'\usepackage[hidelinks]{hyperref}',
           r'\usepackage{enumitem}', r'\setlist{itemsep=2pt,topsep=4pt}', r'\sloppy', r'\title{' + tex(title) + '}', (r'\author{' + tex(author) + (r'\\ \small ' + tex(affil) if affil else '') + '}'),
           r'\date{4 October 2026 (draft for verification)}', r'\begin{document}', r'\maketitle', r'\noindent{\small ' + front + r'}\par\medskip'] + out + [r'\end{document}']
    os.makedirs(OUTD, exist_ok=True); open(os.path.join(OUTD, 'main.tex'), 'w', encoding='utf-8').write('\n'.join(doc) + '\n')
    r = subprocess.run(['tectonic', '-X', 'compile', 'main.tex'], cwd=OUTD, capture_output=True, text=True)
    print('tectonic rc', r.returncode); print('\n'.join(l for l in (r.stderr or r.stdout).splitlines() if 'error' in l.lower() or 'Overfull' in l)[:2000])


if __name__ == '__main__':
    main()
