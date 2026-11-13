import re
GREEK = {'geq':'≥','leq':'≤','Lambda':'Λ','varepsilon':'ε','min':'min','max':'max','log':'log','alpha':'α','beta':'β','gamma':'γ','delta':'δ','epsilon':'ε','lambda':'λ','sigma':'σ','phi':'φ','chi':'χ','pi':'π','nu':'ν','mu':'μ','theta':'θ','omega':'ω','tau':'τ','rho':'ρ'}
def tex_plain(s):
    t = s.replace('$', '')
    t = re.sub(r'\b([A-Z]) (\d) \1_\{\2\}', r'\1\2', t)
    t = re.sub(r'\\text\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\mathbb\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\{\\bf ([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\bm\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\overline\{([^{}]*)\}', lambda m: m.group(1) + '\u0304', t)
    t = re.sub(r'\\([A-Za-z]+)', lambda m: GREEK.get(m.group(1), '\\' + m.group(1)), t)
    t = re.sub(r'_\{([^{}]*)\}', lambda m: '_' + m.group(1), t)
    t = re.sub(r'\^\{([^{}]*)\}', lambda m: '^' + m.group(1), t)
    t = re.sub(r'(?<=[A-Za-z0-9])_(\d)(?!\d)', r'\1', t)          # N_2 -> N2, F_2 -> F2
    t = re.sub(r'(?<=[A-Za-z])_\{?(\d)\}?', r'\1', t)
    t = t.replace('$', '')
    t = t.replace('---', '\u2014').replace('--', '\u2013')
    return t
if __name__ == '__main__':
    for x in ['Accuracy-Cost Trade-offs for Reference VQE Calculations of H$_2$ on IBM', 'Exact Quantum Algebraic Preimage Inversion of $\\text{Keccak-f}[25]$ via Parallel Cubic HOBO Decomposition and $\\mathbb{F}_2$ Linear', 'Extending ... $N_2$ and Fe-S', 'Floquet prethermalization of ${\\bf Z}_2$ lattice', 'via $n$--Qubit GHZ States', 'Hayden--Preskill recovery', 'string breaking in a $Z_2$ lattice', '$\\sigma$-VQE: Excited', 'Informational Shielding Constant \\lambda = 0.181:', 'For each data point we report the minimum \\overline{p}^{\\bm{d}}_{N,\\alpha} found', 'using the segment finding efficiency \\epsilon_{segments} and the fake rate f_{segmen', 'The Quantum Computer\'s Compass --- Entanglement', 'T 1 T_{1}']:
        print(repr(tex_plain(x)))
