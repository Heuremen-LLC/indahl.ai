#!/usr/bin/env python3
"""build_arxiv.py -- SEVEN.md (the canon) -> arXiv LaTeX (main.tex) -> main.pdf, compiled locally with tectonic.
The canon stays the source of truth: every claim, number and caveat comes from SEVEN.md; this file only changes the form (title block, abstract,
numbered sections, math notation, a reference list, the AI-use statement in Methods, the sign-off). Run: python3 build_arxiv.py"""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, '..', 'SEVEN.md')
CHROME = ('/Users/heuremen/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell')
FIG_SVG = os.path.join(HERE, '..', '..', 'disco_figs', 'bh_rings_public.svg')

AUTHOR = 'Indahl'
AFFIL = 'Heuremen'
ABSTRACT = (r"We report seven findings from superconducting-qubit runs on IBM Heron-generation processors (ibm\_pittsburgh, ibm\_marrakesh, ibm\_kingston) "
            r"and on Rigetti hardware. Each finding gives what the qubits showed, with widths and read counts; published records from the rest of physics "
            r"that sit near the measured numbers, found after the numbers were in hand; and a call that could prove it wrong. A single formula ties the "
            r"seven. Three of the calls made in advance have been tested: two missed and one is undecidable. On 4 October 2026, three runs timed one "
            r"look, one train of pushes and one set of free clocks from three positions on three chips: the clocks beside a driven qubit timed a look "
            r"at 1.04--1.07 times the maker's stated length on all three chips, while the qubit's own decay, our method and the push crossing moved chip "
            r"by chip and job by job. We report where the record does not close alongside what it shows. No law or theory is claimed.")


def tex(s):
    s = s.replace('\\', r'\textbackslash{}')
    for a, b in (('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_'), ('$', r'\$'), ('§', r'\S{}')):
        s = s.replace(a, b)
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    s = re.sub(r'`(.+?)`', r'\\texttt{\1}', s)
    s = re.sub(r'"([^"]+)"', r"``\1''", s)
    s = s.replace('x -> 1 + 1/x', r'\(x \to 1 + 1/x\)')
    s = re.sub(r'\|([012+])>', r'\\(|\1\\rangle\\)', s)
    def out(fn):
        nonlocal s
        parts = re.split(r'(\\\(.*?\\\))', s)
        s = ''.join(p if i % 2 else fn(p) for i, p in enumerate(parts))
    out(lambda t: t.replace('+-', r'\(\pm\)'))
    out(lambda t: re.sub(r'(\d[\d.]*)(\s?|-)us\b', lambda m: m.group(1) + (r'\,' if m.group(2) == ' ' else m.group(2)) + r'\textmu s', t))
    out(lambda t: t.replace('->', r'\(\to\)'))
    out(lambda t: re.sub(r'sqrt(\d)', r'\\(\\sqrt{\1}\\)', t))
    out(lambda t: re.sub(r'\^(-?[\d.]+|n)', r'\\(^{\1}\\)', t))
    out(lambda t: re.sub(r'\bphi\b', r'\\(\\varphi\\)', t))
    out(lambda t: re.sub(r'\bpi\b', r'\\(\\pi\\)', t))
    out(lambda t: re.sub(r'\bzeta\b', r'\\(\\zeta\\)', t))
    out(lambda t: re.sub(r'(?<=[\s(])x(?=\s)', r'\\(\\times\\)', t))
    out(lambda t: t.replace('~', r'\(\sim\)').replace('<', r'\textless{}').replace('>', r'\textgreater{}'))
    return s


def blocks(md):
    """split SEVEN.md into (heading, lines) by '## ' headings"""
    out, cur = [], ('', [])
    for ln in md.split('\n'):
        if ln.startswith('## '): out.append(cur); cur = (ln[3:].strip(), [])
        else: cur[1].append(ln)
    out.append(cur); return out


def body(lines):
    o, inlist = [], False
    for ln in lines:
        t = ln.rstrip()
        if t.strip() in ('---', '') or t.startswith('[['):
            if inlist and t.strip() == '': pass
            continue
        if t.startswith('- '):
            if not inlist: o.append(r'\begin{itemize}'); inlist = True
            o.append(r'\item ' + tex(t[2:]))
        else:
            if inlist: o.append(r'\end{itemize}'); inlist = False
            o.append(tex(t) + '\n')
    if inlist: o.append(r'\end{itemize}')
    return '\n'.join(o)


REFS = [
    r'Planck Collaboration, Planck 2018 results. VI. Cosmological parameters, Astron.\ Astrophys.\ \textbf{641}, A6 (2020), arXiv:1807.06209.',
    r'A.~G.~Riess \emph{et al.}, A comprehensive measurement of the local value of the Hubble constant (SH0ES), Astrophys.\ J.\ Lett.\ \textbf{934}, L7 (2022), arXiv:2112.04510.',
    r'E.~Verlinde, Emergent gravity and the dark universe, SciPost Phys.\ \textbf{2}, 016 (2017), arXiv:1611.02269.',
    r"J.-S.~Tang \emph{et al.}, Realization of quantum Wheeler's delayed-choice experiment, Nature Photon.\ \textbf{6}, 600 (2012), arXiv:1204.5304.",
    r'V.~Jacques \emph{et al.}, Delayed-choice test of quantum complementarity with interfering single photons, Phys.\ Rev.\ Lett.\ \textbf{100}, 220402 (2008), arXiv:0801.0979.',
    r'J-PARC neutron lifetime (electron counting), 877.2\,s, arXiv:2412.19519.',
    r'A.~T.~Yue \emph{et al.}, Improved determination of the neutron lifetime, Phys.\ Rev.\ Lett.\ \textbf{111}, 222501 (2013).',
    r'Particle Data Group, Review of Particle Physics (neutron mean life average).',
    r'Caylor \emph{et al.}, hydrogen in the proton trap (2025), arXiv:2506.01682.',
    r'Gas pressure in the electron counter, Eur.\ Phys.\ J.\ A (2026), doi:10.1140/epja/s10050-026-01929-x.',
    r'B.~Fornal and B.~Grinstein, Dark matter interpretation of the neutron decay anomaly, Phys.\ Rev.\ Lett.\ \textbf{120}, 191801 (2018).',
    r'S.~W.~Hawking, Black hole explosions?, Nature \textbf{248}, 30 (1974).',
    r'P.~C.~W.~Davies, The thermodynamic theory of black holes, Proc.\ R.\ Soc.\ Lond.\ A \textbf{353}, 499 (1977).',
    r'D.~N.~Page, Information in black hole radiation, Phys.\ Rev.\ Lett.\ \textbf{71}, 3743 (1993).',
    r'H.~B.~G.~Casimir, On the attraction between two perfectly conducting plates, Proc.\ K.\ Ned.\ Akad.\ Wet.\ \textbf{51}, 793 (1948).',
    r'S.~K.~Lamoreaux, Demonstration of the Casimir force in the 0.6 to 6 \textmu m range, Phys.\ Rev.\ Lett.\ \textbf{78}, 5 (1997).',
    r'J.~Barbour, \emph{The Janus Point} (Basic Books, 2020).',
    r'Event Horizon Telescope Collaboration, First M87 Event Horizon Telescope results. I, Astrophys.\ J.\ Lett.\ \textbf{875}, L1 (2019).',
    r'Event Horizon Telescope Collaboration, First Sagittarius A* Event Horizon Telescope results. I, Astrophys.\ J.\ Lett.\ \textbf{930}, L12 (2022).',
]


def figure_pdf():
    out = os.path.join(HERE, 'rings.pdf'); htmlp = os.path.join(HERE, '_rings.html')
    svg = open(FIG_SVG, encoding='utf-8').read()
    open(htmlp, 'w').write('<!doctype html><html><head><style>@page{size:960px 600px;margin:0}html,body{margin:0}svg{width:960px;height:600px;display:block}</style></head><body>' + svg + '</body></html>')
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={out}', 'file://' + htmlp], capture_output=True)
    os.remove(htmlp); return os.path.exists(out)


def main():
    md = open(SRC, encoding='utf-8').read(); B = blocks(md); sec = {h: l for h, l in B}
    seven = [ln[2:] for ln in sec['The seven'] if ln.startswith('- ')]
    intro = [ln for ln in sec['The seven'] if ln.strip() and not ln.startswith('- ') and ln.strip() != '---']
    order_front = ['Status, up front', 'How to read this', 'Terms']
    findings = [h for h, _ in B if re.match(r'^(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN) -- ', h)]
    has_fig = figure_pdf()
    L = [r'\documentclass[11pt]{article}', r'\usepackage[margin=1in]{geometry}', r'\usepackage{amsmath,amssymb}', r'\usepackage{textcomp}',
         r'\usepackage{graphicx}', r'\usepackage[hidelinks]{hyperref}', r'\usepackage{enumitem}', r'\setlist{itemsep=2pt,topsep=4pt}',
         r'\title{Seven}', r'\author{' + AUTHOR + r'\\ \small ' + AFFIL + '}', r'\date{4 October 2026 (working draft)}', r'\begin{document}', r'\maketitle',
         r'\begin{abstract}' + ABSTRACT + r'\end{abstract}', '',
         r'\section{The seven}', r'\begin{enumerate}[label=\textbf{\arabic*.}]'] + [r'\item ' + tex(x) for x in seven] + [r'\end{enumerate}', body(intro)]
    for h in order_front: L += [r'\subsection*{' + tex(h) + '}', body(sec[h])]
    L += [r'\section{Methods}', body(sec['Methods']),
          r"\paragraph{Use of AI.} An AI model (Anthropic's Claude) designed the runs with the author, wrote the run and analysis code, and drafted this text. "
          r'Every number traces to a read file and a ledger entry; the author takes responsibility for every line.']
    L += [r'\section{The formula}', r'\subsection*{The Bonefish}', body(sec['The Bonefish (the formula)']), r'\subsection*{Darkwave (the recursion)}', body(sec['Darkwave (the recursion)'])]
    L += [r'\section{The findings}']
    for h in findings:
        L += [r'\subsection{' + tex(h.split(' -- ', 1)[1].title() if False else h.replace(' -- ', ' --- ')) + '}', body(sec[h])]
        if h.startswith('SIX') and has_fig:
            L += [r'\begin{figure}[h]\centering\includegraphics[width=0.8\linewidth]{rings.pdf}\caption{The rings around a non-spinning black hole, measured around in $\pi R$.}\end{figure}']
    for h, _ in B:
        if h.startswith('4 OCTOBER'): L += [r'\section{4 October 2026: one look, one push, one clock, from three positions}', body(sec[h])]
    for h, _ in B:
        if h.startswith("WHERE THE RECORD"): L += [r'\section{Where the record does not close}', body(sec[h])]
    L += [r'\section{Calls already tested}', body(sec[[h for h, _ in B if h.startswith('CALLS ALREADY')][0]]),
          r'\section{What is closed, what is open}', body(sec["WHAT'S CLOSED, WHAT'S OPEN"]),
          r'\section*{Data availability}', body(sec['DATA AND ERRORS']),
          r'\section*{Acknowledgments}', r'Made with AI assistance (see Methods). \par\medskip Wayfinder and Bones',
          r'\begin{thebibliography}{99}'] + [rf'\bibitem{{r{i}}} {r}' for i, r in enumerate(REFS, 1)] + [r'\end{thebibliography}', r'\end{document}']
    open(os.path.join(HERE, 'main.tex'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    r = subprocess.run(['tectonic', '-X', 'compile', 'main.tex'], cwd=HERE, capture_output=True, text=True)
    print('tectonic rc', r.returncode); print('\n'.join((r.stderr or r.stdout).splitlines()[-12:]))


if __name__ == '__main__':
    main()
