"""Build MATRIX_v2.md from matrix_v2_results_v2.json (written by score_matrix_v2.py). Values verbatim from the scorer; four outcomes."""
import json,os
HERE=os.path.dirname(os.path.abspath(__file__)); d=json.load(open(os.path.join(HERE,'matrix_v2_results_v2.json')))
f=lambda v: 'n/a' if v is None or v[0]!=v[0] else '%.3f [%.3f, %.3f] n%d'%tuple(v[:4])
o=['# Recount Matrix: Language Models - v2 (4-option items + positive control; our seat; internal draft)','',
'Plan: PLAN_v2.md (addenda v2-1..v2-3). Gate: an order cell is read only if the positive control (pick the option listed FIRST) is followed in',
'>= 80% of items in BOTH orderings and the known-good copy check passes; otherwise CANNOT_TELL with the reason. Flip cells = share of items whose',
'answer changes under the carrier, minus the exact-copy floor. top-letter = share of answers on the most-used letter (0.25 = uniform).','',
'| model | known-good | positive control acc (A / rev) | top letter | reverse order flip | rotation flip | template B flip | truncated |','|---|---|---|---|---|---|---|---|']
for m,v in sorted(d.items()):
    oc=v['outcomes']
    o.append(f"| {m} | {'pass' if v['known_good'] else 'FAIL'} {f(v['copy_disagree'])} | {f(v['pc_acc_A'])} / {f(v['pc_acc_rev'])} | {v['top_letter_share']:.2f} | {f(v['mcq4_rev_flip_minus_floor'])} {oc['mcq4_rev_flip_minus_floor']} | {f(v['mcq4_rot_flip_minus_floor'])} {oc['mcq4_rot_flip_minus_floor']} | {f(v['mcq4_B_flip_minus_floor'])} {oc['mcq4_B_flip_minus_floor']} | {v['truncated_A'][0]} of {v['truncated_A'][1]} |")
o+=['','Reading so far: where the positive control passes (phi4-mini, mistral, falcon3), answers change with option order and rotation while the most-used',
'letter stays near uniform -> order sensitivity separated from letter fallback (the v1 limit). Models still running are partial.',
'Check (25 Oct): mistral reverse and rotation cells are equal (54 of 198 each) by count, not by construction: the two arms use different option',
'orders on every item and 114 of 200 raw replies differ.']
open(os.path.join(HERE,'MATRIX_v2.md'),'w').write('\n'.join(o)+'\n'); print('rows',len(d))
