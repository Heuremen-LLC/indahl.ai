"""job2_core.py - all three benchmarks x factorial settings, 20 twirls x 1000 shots."""
from common import *
args = get_args(); name, chain, rep = resolve(args)
backend = get_backend(args, name)
tim = Timing(backend.target, use_mcm2="measure_2" in backend.target.operation_names, layout=chain)
groups = [(b, build(b, FACTORIAL, 20, tim, args.seed), layout_for(b, chain)) for b in ("probe", "teleport", "ghz")]
run_job("job2", groups, args, shots=1000, s_per_exec=args.s_per_exec)
