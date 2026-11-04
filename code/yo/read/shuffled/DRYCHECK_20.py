import sys, re; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
from mlx_lm import load, generate
from yo2_data import render
m, t = load('Qwen/Qwen3-1.7B')
Q = ['Does the paper print a date or date range of its own quantum hardware runs (not a publication, citation or calibration-data date)? Answer only YES or NO.',
     'Does the paper print a URL, DOI or repository for its own data or code (not a citation of another work)? Answer only YES or NO.']
S = [['We ran all circuits on ibm_fez on 12 March 2025.', 'Results are shown in Fig. 2.'], ['The code is at https://github.com/example/demo.', 'We thank the reviewers.'],
     ['Data are available from the authors.', 'The device has 27 qubits.'], ['No hardware was used.', 'Simulations used Qiskit Aer.'], ['Experiments took place in May 2024.', 'See Table 1.']]
rx = re.compile(r'\b(YES|NO)\b'); n = ok = 0
for q in Q:
    for s in S:
        for k in (0, 1):
            if n >= 20: break
            p = f'You read sentences picked from a quantum-hardware paper (reference list removed). {q}\nSentences:\n' + '\n'.join(f'{i+1}. {x}' for i, x in enumerate(s[::(1 if k == 0 else -1)]))
            o = generate(m, t, prompt=render(p), max_tokens=8, verbose=False); a = rx.search(o or ''); n += 1; ok += bool(a)
            print(n, repr(o[:40]), '->', a.group(1) if a else 'OFF-FORMAT')
print(f'parsed {ok} of {n}')
