"""Shared loaders for the Caldwell gift (our code; their trace files read as JSON data)."""
import json, os, glob, collections, math
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
JUDGES = ['claude-sonnet-5', 'gemini-3.7-flash', 'muse-glimmer-30b', 'inkling-small', 'gpt-5.4-mini-2026-03-17', 'deepseek-v4-flash']
PRINTED = {'claude-sonnet-5': (80.8, 1.392), 'gemini-3.7-flash': (75.2, 0.186), 'muse-glimmer-30b': (70.2, 0.140), 'inkling-small': (69.3, 0.126),
           'gpt-5.4-mini-2026-03-17': (68.7, 0.136), 'deepseek-v4-flash': (63.5, 0.029)}
def load(judge):
    """{(pr, decl, rep): {'initial': row, 'final': row}} and the set of declarations seen in the file"""
    P = collections.defaultdict(dict)
    for l in open(os.path.join(T, 'hf_traces', 'data', 'traces_%s.jsonl' % judge)):
        r = json.loads(l); x = r['extra']
        P[(x['pr_number'], x['declaration_name'], x['replicate'])][x['variant']] = {'score': x['score'], 'pt': r['final_metrics']['total_prompt_tokens'], 'ct': r['final_metrics']['total_completion_tokens']}
    return P
def pairs(P):
    """complete pairs only: (pr, decl, rep) -> 'aligned' | 'tie' | 'inverted'"""
    out = {}
    for k, v in P.items():
        if 'initial' in v and 'final' in v:
            d = v['final']['score'] - v['initial']['score']; out[k] = 'aligned' if d > 0 else ('tie' if d == 0 else 'inverted')
    return out
def binom2(k, n):
    if n == 0: return 1.0
    k = min(k, n - k); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
