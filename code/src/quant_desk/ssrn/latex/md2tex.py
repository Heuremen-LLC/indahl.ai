"""md2tex.py -- errata_note.md -> main.tex in the house revtex4-2 format (A Readout Is Not an Idle). Run, then tectonic main.tex."""
import re, sys, pathlib
SRC = pathlib.Path(__file__).resolve().parent.parent / 'errata_note.md'
OUT = pathlib.Path(__file__).resolve().parent / 'main_rev4_converted.tex'
s = SRC.read_text()
s = re.sub(r'^---\n.*?\n---\n', '', s, flags=re.S)
title = re.search(r'^# (.+)$', s, re.M).group(1)
abstract = s.split('## Abstract\n\n')[1].split('\n## ')[0].strip()
body = '## ' + s.split('## Abstract\n\n')[1].split('\n## ', 1)[1]
def esc(t):
    t = t.replace('\\', r'\textbackslash{}')
    for a, b in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        t = t.replace(a, b)
    t = t.replace(r'\textbackslash\{\}', r'\textbackslash{}')
    t = re.sub(r'`([^`]+)`', r'\\texttt{\1}', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'\\emph{\1}', t)
    t = re.sub(r'(https?://[^\s,)]+?)(?=[.,;)]?(\s|$))', r'\\url{\1}', t)
    t = re.sub(r'"([^"\n]+)"', r'``\1' + "''", t)
    for a, b in [('σ', r'$\sigma$'), ('β', r'$\beta$'), ('µ', r'$\mu$'), ('μ', r'$\mu$'), ('±', r'$\pm$'), ('−', r'$-$'), ('–', '--'), ('—', '---'),
                 ('≈', r'$\approx$'), ('∼', r'$\sim$'), ('≤', r'$\le$'), ('≥', r'$\ge$'), ('×', r'$\times$'), ('⊙', r'$_\odot$'), ('χ', r'$\chi$'), ('ι', r'$\iota$'), ('Λ', r'$\Lambda$'), ('é', r"\'e")]:
        t = t.replace(a, b)
    return t
out = []; lines = body.split('\n'); i = 0
while i < len(lines):
    L = lines[i]
    m = re.match(r'^(#{2,4}) (.+)$', L)
    if m:
        lvl = len(m.group(1)); txt = re.sub(r'^\d+[a-z]?(\.\d+)*\.?\s+', '', m.group(2))
        out.append({2: r'\section{%s}', 3: r'\subsection{%s}', 4: r'\paragraph*{%s}'}[lvl] % esc(txt)); i += 1; continue
    if L.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            if not re.match(r'^\|[\s:|-]+\|$', lines[i]): rows.append([esc(c.strip()) for c in lines[i].strip('|').split('|')])
            i += 1
        n = len(rows[0]); wide = n > 4 or max(len(c) for r in rows for c in r) > 30
        out.append(r'\begin{table*}[t]\centering\small' if wide else r'\begin{table}[t]\centering\small')
        out.append((r'\begin{tabularx}{\textwidth}{%s}\hline\hline' % ('>{\\raggedright\\arraybackslash}X' * n)) if wide else (r'\begin{tabular}{%s}\hline\hline' % ('l' + 'c' * (n - 1))))
        out.append(' & '.join(rows[0]) + r' \\ \hline')
        for r in rows[1:]: out.append(' & '.join(r) + r' \\')
        out.append(r'\hline\hline\end{tabularx}' if wide else r'\hline\hline\end{tabular}'); out.append(r'\end{table*}' if wide else r'\end{table}'); continue
    if re.match(r'^(- |\d+\. )', L):
        env = 'itemize' if L.startswith('- ') else 'enumerate'; out.append(r'\begin{%s}' % env)
        while i < len(lines) and re.match(r'^(- |\d+\. )', lines[i]):
            out.append(r'\item ' + esc(re.sub(r'^(- |\d+\. )', '', lines[i]))); i += 1
        out.append(r'\end{%s}' % env); continue
    if L.startswith('> '):
        out.append(r'\begin{quote}' + esc(L[2:]) + r'\end{quote}'); i += 1; continue
    out.append(esc(L)); i += 1
tex = r"""\documentclass[reprint,amsmath,amssymb,aps,superscriptaddress,nofootinbib]{revtex4-2}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{url}
\usepackage{tabularx,array}
\hypersetup{pdftitle={%s}}
\begin{document}
\title{%s}
\author{K. Indahl}
\email{Indahl@heuremen.com}
\affiliation{Heuremen LLC}
\date{November 12, 2026}
\begin{abstract}
%s
\end{abstract}
\maketitle
%s
\end{document}
""" % (title, esc(title), esc(abstract), '\n'.join(out))
OUT.write_text(tex); print('wrote', OUT)
