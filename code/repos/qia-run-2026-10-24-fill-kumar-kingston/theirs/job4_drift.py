"""job4_drift.py - probe factorial replicate on another day/layout."""
from common import *
args = get_args(); name, chain, rep = resolve(args)
backend = get_backend(args, name)
tim = Timing(backend.target, use_mcm2="measure_2" in backend.target.operation_names, layout=chain)
run_job("job4", [("probe", build("probe", FACTORIAL, 20, tim, args.seed + 4), layout_for("probe", chain))], args, shots=1000, s_per_exec=args.s_per_exec)
