"""common.py: builds a Faults/Guards item module from the round 2 template with a new story and new seeds (same machinery as make_rounds.py)."""
import os, sys, random, types
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R2SRC = open(os.path.join(B, 'faultsbench_r2', 'items.py')).read()
def story(plural, sing, sets, verb, unit, doc, nchoices, p3range, p4counts):
    S = sing.lower()
    return (f'Two {plural} were tested on {sets}.', f'{sing} A', f'{sing} B', f'Is {sing} A better than {sing} B?',
            f'A {S} {verb}. Report the {S}\'s accuracy.', f'{doc}: "{{k}} of {{n}} {unit} is {{shown}}%."',
            f'The same {S} was retrained under {{s}} random seeds. Held-out accuracies:', f'Report the {S}\'s accuracy as one number.', nchoices, p3range, p4counts)
def items_source(t, s1, s2):
    pairs = [("random.Random(20261027)", f"random.Random({s1})"), ("random.Random(26102028)", f"random.Random({s2})"),
             ("Two screening tools were run on the same held-out set. Tool A:", t[0] + " " + t[1] + ":"), ("Tool B:", t[2] + ":"), ("Is Tool A better than Tool B?", t[3]),
             ("A classifier labelled {it['k']} of {it['n']} held-out cases correctly. Report the classifier's accuracy.", t[4].replace('{k}', "{it['k']}").replace('{n}', "{it['n']}")),
             ("A methods section says: \\\"{it['k']} of {it['n']} cases is {it['shown']}%.\\\"", t[5].replace('"', '\\"').replace('{k}', "{it['k']}").replace('{n}', "{it['n']}").replace('{shown}', "{it['shown']}")),
             ("The same network was retrained from scratch under {len(it['xs'])} random initialisations. Held-out accuracies:", t[6].replace('{s}', "{len(it['xs'])}")),
             ("Report the network's accuracy as one number.", t[7]), ("[30, 45, 70, 90, 120, 150]", str(t[8])), ("R2.randint(150, 500)", f"R2.randint({t[9][0]}, {t[9][1]})"), ("[6, 7, 9, 12]", str(t[10]))]
    s = R2SRC
    for a, b in pairs:
        assert a in s, a[:50]; s = s.replace(a, b)
    return s
def items_module(t, s1, s2):
    m = types.ModuleType('items_tmp'); exec(compile(items_source(t, s1, s2), 'items_tmp', 'exec'), m.__dict__); return m

def train_seeds(si, rep):
    s1 = 20280001 + 17 * (3 * si + rep); return s1, s1 + 5
