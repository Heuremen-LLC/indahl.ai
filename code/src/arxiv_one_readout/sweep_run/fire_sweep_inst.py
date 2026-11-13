"""fire_sweep_inst.py INSTANCE_NAME TAG ARGS -- runs the UNCHANGED sweep.py source (hash in CODE_SWEEP.sha256) on another IBM instance
(e.g. 'Quaker Instance', the eu-de region that serves ibm_aachen), with every saved file name suffixed _TAG so nothing is overwritten.
Only the INSTANCE constant and the file names change; circuits, seed, shots and analysis are identical. 24 Oct 2026."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); inst, tag = sys.argv[1], sys.argv[2]; src = open(f'{HERE}/sweep.py').read()
old = "INSTANCE = '.ibm_quantum_key_3', 'Darkwave Disco'"; assert src.count("'Darkwave Disco'") == 1, 'instance line not unique'
src = src.replace("'Darkwave Disco'", repr(inst))
n = sum(src.count(f'_sweep_{{{v}}}.') for v in ('CHIP', 'chip')); assert n >= 6, n
for v in ('CHIP', 'chip'): src = src.replace(f'_sweep_{{{v}}}.', f'_sweep_{{{v}}}_{tag}.')
sys.argv = ['sweep.py'] + sys.argv[3:]; sys.path.insert(0, HERE)
exec(compile(src, f'{HERE}/sweep.py', 'exec'), {'__name__': '__main__', '__file__': f'{HERE}/sweep.py'})
