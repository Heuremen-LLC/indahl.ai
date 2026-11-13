"""RUN 2 -- TWO LOOKS ("the echo", one earlier look). Three STARTS x three WAITS = 9 circuits. Each: START, LOOK, WAIT, LOOK.
Raw I/Q on both looks. Spec: ../../QUBIT_THREE_RUNS_APPROVED_20261001.md.
  python run2.py --dry-run [--chip NAME --box B] | --list-circuits | --print-estimate
  python run2.py --fire --chip NAME --box B [--prediction-file P  (OURS only)] --confirm-submit"""
from common import *

def specs():
    return [{'key': f'{s}|w{w}', 'start': s, 'pre_waits_us': [0, w]} for s in STARTS for w in WAITS_US]

if __name__ == '__main__':
    run_main(2, specs, __doc__)
