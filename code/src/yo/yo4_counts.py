"""yo4_counts.py -- the counts behind the planned readings R1 and R3 on TEST4 (same definitions as yo4_compare.py)."""
import sys; sys.path.insert(0, '/Users/heuremen/bones-forge/yo')
import yo4_compare as Y
for n in ('yo_v4', 'yo_v3', 'yo_v2'):
    ev = Y.load(n); w = [x for i in Y.items if Y.items[i]['job'] == 'A' and Y.WIN(i) for x in Y.qubits(i, ev) if x[0] and x[1]]
    qa = [x for i in Y.items if Y.items[i]['job'] == 'A' for x in Y.qubits(i, ev)]
    print(f'{n} R1 found {sum(x[2] for x in w)} of {len(w)} | R3 flagged {sum(x[2] for x in qa)}, truly stale {sum(x[0] for x in qa if x[2])}')
