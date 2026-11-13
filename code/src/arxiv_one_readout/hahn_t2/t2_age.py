"""t2_age.py CHIP -- prints the median age (h) of IBM's stated T2 now, read on the open instance of key 2. Read only, no job."""
import sys, statistics, datetime as dt
HERE = '/Users/heuremen/bones-forge/arxiv_one_readout/hahn_t2'; chip = sys.argv[1]
src = open(f'{HERE}/hahn.py').read(); old = "KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'open-instance'"; assert src.count(old) == 1
g = {'__name__': 'hahn_k2', '__file__': f'{HERE}/hahn.py'}; sys.argv = ['x']
exec(compile(src.replace(old, "KEYFILE, INSTANCE = '.ibm_quantum_key_2', 'open-instance'"), 'hahn.py', 'exec'), g)
p = g['service']().backend(chip).properties(); now = dt.datetime.now(dt.timezone.utc)
print('%.2f' % statistics.median([(now - q.date).total_seconds() / 3600 for qs in p.qubits for q in qs if q.name == 'T2']), p.last_update_date)
