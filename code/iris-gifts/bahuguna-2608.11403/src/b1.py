#!/usr/bin/env python3
"""B1 (PLAN, committed before this ran): Section 8 answer-rate interval, sample-level Wilson against problem-level cluster bootstrap."""
import json, os, math, collections, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'zenodo', 'derived__samples.jsonl')
v2 = [r for r in (json.loads(l) for l in open(T)) if str(r['run_id']).startswith('margin-v2')]
k = sum(r['extracted_answer'] is not None for r in v2); n = len(v2); tr = sum(bool(r['truncated']) for r in v2)
z = 1.96; p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
print('margin-v2: %d samples, %d answered (%.4f), %d truncated (%.4f), %d problems' % (n, k, p, tr, tr / n, len({r['problem_id'] for r in v2})))
print('sample-level Wilson 95%%: [%.4f, %.4f]   (printed [0.8747, 0.9090]; matches to four places)' % ((c - h) / d, (c + h) / d))
byp = collections.defaultdict(lambda: [0, 0])
for r in v2: byp[r['problem_id']][0] += r['extracted_answer'] is not None; byp[r['problem_id']][1] += 1
A = np.array(list(byp.values()), float)
for seed in (42, 1, 2):
    i = np.random.default_rng(seed).integers(0, len(A), size=(10000, len(A))); s = A[i].sum(1)
    print('problem-level cluster bootstrap, seed %d: [%.4f, %.4f]' % ((seed,) + tuple(np.percentile(s[:, 0] / s[:, 1], [2.5, 97.5]))))
print('samples per problem: min %d, median %d, max %d' % (A[:, 1].min(), np.median(A[:, 1]), A[:, 1].max()))

# Referee pass (30 Oct): the counts in full, and the bootstrap under the paper's other stated setup (1,000 iterations, seed 42), since the
# paper states two (Section 2: 1,000 iterations, seed 42; disclosures 13 and 16: 10,000 replicates, no seed). The 79 problems are the
# budget-stopped lowest-id slice the paper describes, not a random draw, so neither interval speaks for the benchmark.
ta = sum(bool(r['truncated']) and r['extracted_answer'] is not None for r in v2)
print('truncated with an answer still extracted: %d (so 1,253 - 364 is not 1,119); unanswered and truncated: %d of %d unanswered' % (ta, sum(bool(r['truncated']) and r['extracted_answer'] is None for r in v2), n - k))
i = np.random.default_rng(42).integers(0, len(A), size=(1000, len(A))); s = A[i].sum(1)
print('problem-level cluster bootstrap, 1,000 iterations, seed 42: [%.4f, %.4f]' % tuple(np.percentile(s[:, 0] / s[:, 1], [2.5, 97.5])))
