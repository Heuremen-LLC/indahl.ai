"""judge_counts.py: counts from our own pipeline's judge and orchestration logs (27 Oct 2026). Reads ~/bones-forge/autonomous_judge.log and triangulate.log, writes summary.json.
Counts only: no log text is read into the output, no item text, no identifiers. The logs are not published; this script and summary.json are.
30 Oct 2026 correction: each verdict line in the judge log carries a tag in parentheses, not an item id. The tag is the adapter name (freed-sage-v3, freed-sage-v3-armature)
or a short label of the form triangulated-<model>-<one to three hex characters>, which repeats by chance. The log has no field that identifies the item a verdict was made on.
The earlier outputs items_judged_more_than_once, of_those_with_differing_verdicts and differing_share_pct grouped on that tag and are removed. They did not measure how often
the judge repeats itself on the same item. Added: verdicts logged under the two adapter names, and rounds by number of asks made."""
import re, json, math, collections, os
H = os.path.expanduser('~/bones-forge/')
V = re.compile(r'^\[(\d\d:\d\d:\d\d)\] (KEEP|DISCARD|HOLD) \(([^)]*)\) -- kept=(\d+) discarded=(\d+) held=(\d+) errors=(\d+)')
def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0, c - h), 1), round(100 * min(1, c + h), 1))
runs = []; cur = None; per_tag = collections.Counter(); verdicts = collections.Counter()
ADAPTER = re.compile(r'^freed-sage-v\d+(-armature)?$')   # the tag is the adapter name for these; for the rest it is a short label that is not an item id
for l in open(H + 'autonomous_judge.log', errors='replace'):
    if 'autonomous judge starting' in l: cur = []; runs.append(cur); continue
    m = V.match(l)
    if m:
        verdicts[m.group(2)] += 1; per_tag[m.group(3)] += 1
        if cur is not None: cur.append(m.groups())
n = sum(verdicts.values()); err = sum(int(r[-1][6]) for r in runs if r)
on_adapter = sum(c for t, c in per_tag.items() if ADAPTER.match(t))
rounds = asks = forced = 0; by = collections.Counter(); per_round = collections.Counter(); cur_asks = None
for l in open(H + 'triangulate.log', errors='replace'):
    if re.search(r'\] round:', l):
        rounds += 1
        if cur_asks is not None: per_round[cur_asks] += 1
        cur_asks = 0
    m = re.match(r'\s+\[(ask_\w+)\]', l)
    if m:
        asks += 1; by[m.group(1)] += 1
        if cur_asks is not None: cur_asks += 1
        if '(forced' in l: forced += 1
if cur_asks is not None: per_round[cur_asks] += 1
out = dict(judge=dict(restarts=len(runs), verdicts=n, keep=verdicts['KEEP'], discard=verdicts['DISCARD'], hold=verdicts['HOLD'], errors_counter_sum=err, verdicts_under_adapter_names=on_adapter,
                      hold_share_pct=[round(100 * verdicts['HOLD'] / n, 1)] + list(wilson(verdicts['HOLD'], n)), discard_share_pct=[round(100 * verdicts['DISCARD'] / n, 1)] + list(wilson(verdicts['DISCARD'], n)), keep_share_pct=[round(100 * verdicts['KEEP'] / n, 1)] + list(wilson(verdicts['KEEP'], n))),
           orchestration=dict(rounds=rounds, rounds_with_three_asks=per_round[3], rounds_by_asks_made={str(k): per_round[k] for k in sorted(per_round)}, asks=asks, asks_by_model=dict(by), asks_forced=forced, forced_share_pct=[round(100 * forced / asks, 1)] + list(wilson(forced, asks))))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summary.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
