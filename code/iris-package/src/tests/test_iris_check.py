#!/usr/bin/env python3
"""Tests for iris_check.py and replycheck.py on the synthetic dataset in tests/data/, where the answers are planted. Run: python tests/test_iris_check.py"""
import os, sys, json, csv, glob, shutil, subprocess, tempfile, hashlib, unittest, re, time, importlib.util
from fractions import Fraction
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); TOOL = os.path.join(ROOT, 'iris_check.py'); D = os.path.join(H, 'data')
with open(os.path.join(D, 'PLANTED.json')) as f: PLANTED = json.load(f)
sp = importlib.util.spec_from_file_location('iris_check', TOOL); IC = importlib.util.module_from_spec(sp); sys.dont_write_bytecode = True; sp.loader.exec_module(IC)
def tail_ref(n, k):
    """exact two-sided p as a Fraction, built from integers only"""
    c = 1; tot = 1
    for i in range(k): c = c * (n - i) // (i + 1); tot += c
    return float(min(Fraction(1), 2 * Fraction(tot, 2 ** n)))
def run(*args, ok=True, script=TOOL):
    r = subprocess.run([sys.executable, '-B', '-X', 'dev', '-W', 'always', script, *args], capture_output=True, text=True)
    assert 'ResourceWarning' not in r.stderr, r.stderr
    if ok: assert r.returncode == 0, r.stderr
    return r
def latest(out, pat): return sorted(glob.glob(os.path.join(out, pat)))[-1]
def jload(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
def sha(p):
    with open(p, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()
def jl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows: f.write((r if isinstance(r, str) else json.dumps(r)) + '\n')
def readjl(path):
    with open(path, encoding='utf-8') as f: return [json.loads(l) for l in f if l.strip()]
def wcsv(path, rows, cols):
    with open(path, 'w', newline='', encoding='utf-8') as f: w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.data = os.path.join(self.tmp, 'data'); shutil.copytree(D, self.data); self.out = os.path.join(self.tmp, 'out'); self.sh = os.path.join(self.tmp, 'sheets'); os.makedirs(self.sh)
    def tearDown(self): shutil.rmtree(self.tmp)
    def rep(self, *a, **kw): return run('repeat', *a, '--id-field', 'id', '--correct-field', 'correct', '--out', self.out, **kw)
    def f(self, n): return os.path.join(self.data, n + '.jsonl')
    def report(self): return jload(latest(self.out, 'repeat_*.json'))
    # ---- planted answers
    def test_repeat_floor(self):
        self.rep(self.f('A1'), self.f('A2'), '--repeats'); r = self.report()['repeat_A'][0]; p = PLANTED['A1_vs_A2']
        self.assertEqual((r['right_to_wrong'], r['wrong_to_right'], r['net'], r['n_matched']), (p['right_to_wrong'], p['wrong_to_right'], p['net'], 400))
        self.assertAlmostEqual(r['repeat_floor'], p['repeat_floor'], places=4)
    def test_outcomes(self):
        for a, b, out in (('A1', 'B1', 'ABOVE'), ('B1', 'A1', 'BELOW'), ('A1', 'C1', 'CONSISTENT'), ('A1', 'E1', 'CANNOT_TELL')):
            shutil.rmtree(self.out, ignore_errors=True); self.rep(self.f(a), '--vs', self.f(b)); c = self.report()['comparison'][0]
            self.assertEqual(c['outcome'], out, (a, b, c)); self.assertEqual(c['n_matched'], 400)
            if (a, b) == ('A1', 'B1'): self.assertEqual((c['A_right_B_wrong'], c['A_wrong_B_right']), (60, 10)); self.assertLess(c['mcnemar_exact_p'], 1e-6)
            if (a, b) == ('A1', 'E1'): self.assertEqual((c['A_right_B_wrong'], c['A_wrong_B_right']), (14, 6)); self.assertAlmostEqual(c['mcnemar_exact_p'], 0.115318, places=5)
    def test_console_prints_n_and_discordant(self):
        r = self.rep(self.f('A1'), '--vs', self.f('B1')); self.assertIn('n matched 400', r.stdout); self.assertIn('discordant 60/10', r.stdout)
    def test_margin_moves_outcome(self):
        self.rep(self.f('A1'), '--vs', self.f('C1'), '--margin', '0.001'); self.assertEqual(self.report()['comparison'][0]['outcome'], 'CANNOT_TELL')
    def test_inputs_unchanged_and_hashed(self):
        before = sha(self.f('A1')); self.rep(self.f('A1'), self.f('A2')); self.assertEqual(before, sha(self.f('A1')))
        j = self.report(); self.assertTrue(all(i['sha256_before'] == i['sha256_after'] for i in j['inputs'])); self.assertEqual(j['inputs'][0]['sha256_before'], before)
        with open(latest(self.out, 'repeat_*.html')) as f: self.assertIn('unchanged', f.read())
    def test_out_inside_input_folder_refused(self):
        r = run('repeat', self.f('A1'), self.f('A2'), '--id-field', 'id', '--correct-field', 'correct', '--out', os.path.join(self.data, 'reports'), ok=False)
        self.assertNotEqual(r.returncode, 0); self.assertIn('inside the folder of an input', r.stderr); self.assertFalse(os.path.exists(os.path.join(self.data, 'reports')))
    def test_out_is_a_file_plain_error(self):   # item 10
        fl = os.path.join(self.tmp, 'afile'); open(fl, 'w').close()
        r = run('repeat', self.f('A1'), self.f('A2'), '--id-field', 'id', '--correct-field', 'correct', '--out', fl, ok=False)
        self.assertEqual(r.returncode, 1); self.assertIn('is a file', r.stderr); self.assertNotIn('Traceback', r.stderr)
    # ---- item 1 and 2: outcome rule
    def test_both_must_agree(self):   # 5 discordant one way in 400: the bootstrap interval leaves 0, the exact test (p 0.0625) does not
        base = {f'q{i}': True for i in range(400)}; other = dict(base)
        for i in range(5): other[f'q{i}'] = False
        c = IC.compare(base, other, sorted(base), 0.02, 2000, 1)
        self.assertGreater(c['ci95_low'], 0); self.assertGreater(c['mcnemar_exact_p'], 0.05); self.assertEqual(c['outcome'], 'CANNOT_TELL'); self.assertIn('disagree', c['reason'])
        other2 = dict(base)
        for i in range(8): other2[f'q{i}'] = False
        self.assertEqual(IC.compare(base, other2, sorted(base), 0.02, 2000, 1)['outcome'], 'ABOVE')   # 8 and 0: p 0.0078, interval above 0
    def test_consistent_needs_evidence(self):
        same = {f'q{i}': i % 2 == 0 for i in range(400)}
        c = IC.compare(same, dict(same), sorted(same), 0.02, 2000, 1); self.assertEqual((c['discordant'], c['outcome']), (0, 'CANNOT_TELL')); self.assertIn('no discordant', c['reason'])
        s15 = {f'q{i}': True for i in range(15)}; c = IC.compare(s15, dict(s15), sorted(s15), 0.02, 2000, 1); self.assertEqual(c['outcome'], 'CANNOT_TELL'); self.assertIn('fewer than 20', c['reason'])
        s20 = {f'q{i}': i < 10 for i in range(20)}; o = dict(s20); o['q0'] = False; o['q15'] = True   # 1 and 1 discordant, 20 matched, interval wider than the margin
        self.assertEqual(IC.compare(s20, o, sorted(s20), 0.5, 2000, 1)['outcome'], 'CONSISTENT')
    def test_resolved_small_difference_reads_above(self):
        n = 100000; x = {str(i): True for i in range(n)}; y = dict(x)
        for i in range(600): y[str(i)] = False          # A right, B wrong: 600
        for i in range(600, 900): x[str(i)] = False     # A wrong, B right: 300 (y is already True there)
        c = IC.compare(x, y, sorted(x, key=int), 0.02, 2000, 1)
        self.assertEqual((c['A_right_B_wrong'], c['A_wrong_B_right']), (600, 300)); self.assertAlmostEqual(c['diff_A_minus_B'], 0.003, places=6)
        self.assertEqual(c['outcome'], 'ABOVE')   # inside plus or minus 0.02, and still ABOVE because it is resolved
    # ---- item 3: exact test
    def test_mcnemar_matches_fraction_reference_small(self):
        for n in range(0, 61):
            for k in range(0, n // 2 + 1):
                ref = tail_ref(n, k)
                self.assertAlmostEqual(IC.mcnemar_exact(k, n - k), ref, places=14, msg=(n, k))
    def test_mcnemar_log_space_matches_exact_integer_reference(self):
        for n, k in ((2500, 1100), (2500, 1250), (5000, 2300), (30001, 14800), (20000, 9000)):
            ref = tail_ref(n, k)
            got = IC.mcnemar_exact(k, n - k); self.assertLessEqual(abs(got - ref), 1e-9 * max(ref, 1e-300) + 1e-15, (n, k, got, ref))
    def test_million_items_fast(self):
        n = 1000000; x = {str(i): True for i in range(n)}; y = dict(x)
        for i in range(200000): y[str(i)] = False                  # A right, B wrong: 200,000
        for i in range(200000, 420000): x[str(i)] = False          # A wrong, B right: 220,000 (y is True there)
        t = time.time(); c = IC.compare(x, y, sorted(x, key=int), 0.02, 2000, 1); dt_ = time.time() - t
        self.assertEqual(c['discordant'], 420000); self.assertLess(dt_, 40); self.assertEqual(c['outcome'], 'BELOW'); self.assertAlmostEqual(c['diff_A_minus_B'], -0.02, places=6)
        self.assertLess(IC.mcnemar_exact(200000, 220000), 1e-30); self.assertEqual(IC.mcnemar_exact(210000, 210000), 1.0)
        z = (209000 - 210000 + 0.5) / (420000 ** 0.5 / 2); ref = IC.math.erfc(abs(z) / 2 ** 0.5)
        self.assertLess(abs(IC.mcnemar_exact(209000, 211000) - ref) / ref, 5e-3)   # normal approximation agrees to a few parts in a thousand
    # ---- item 4: dropped items
    def test_dropped_items_reported_by_reason(self):
        base = readjl(self.f('A1')); rows = [dict(r) for r in base[:300]]
        rows[0]['id'] = 2.0; rows[1]['id'] = 7; rows[2]['id'] = '7.0'                    # ids that are not strings
        rows.append({'correct': True}); rows.append({'id': 'nc'}); rows.append({'id': 'nb', 'correct': 'maybe'}); rows.append(dict(rows[10]))
        jl(os.path.join(self.data, 'messy.jsonl'), rows[:5] + ['', ''] + rows[5:])
        c = self.rep(self.f('A2'), os.path.join(self.data, 'messy.jsonl')); self.assertIn('rows read 304 = usable 299 + missing id 1 + missing correct field 1 + unscored (null correct) 0 + not a boolean 1 + duplicate rows 2 (1 duplicate ids)', c.stdout); r = {x['run']: x for x in self.report()['runs']}['messy.jsonl']
        self.assertEqual((r['blank_lines'], r['missing_id_field'], r['missing_correct_field'], r['non_boolean_correct'], r['duplicate_rows'], r['duplicate_ids']), (2, 1, 1, 1, 2, 1))
        self.assertEqual((r['rows_read'], r['usable_items']), (304, 299)); self.assertTrue(r['ties_out'])   # 304 = 299 + 1 + 1 + 1 + 2
        self.assertEqual(r['rows_read'], r['usable_items'] + r['missing_id_field'] + r['missing_correct_field'] + r['non_boolean_correct'] + r['duplicate_rows'])
        self.assertEqual(r['ids_normalised_to_text'], 2); self.assertIn('nb', r['examples']); self.assertIn('nc', r['examples']); self.assertIn('line', r['examples'])
    def test_id_types_are_one_id(self):
        jl(os.path.join(self.data, 'x.jsonl'), [dict(id=i, correct=True) for i in range(30)]); jl(os.path.join(self.data, 'y.jsonl'), [dict(id=str(i), correct=(i % 2 == 0)) for i in range(30)])
        jl(os.path.join(self.data, 'z.jsonl'), [dict(id=float(i), correct=True) for i in range(30)])
        self.rep(os.path.join(self.data, 'x.jsonl'), os.path.join(self.data, 'y.jsonl'), os.path.join(self.data, 'z.jsonl')); rows = self.report()['repeat_A']
        self.assertEqual([r['n_matched'] for r in rows], [30, 30, 30])
    def test_pairs_use_their_own_intersection_and_warn(self):
        jl(os.path.join(self.data, 'short.jsonl'), readjl(self.f('A2'))[:100])
        r = self.rep(self.f('A1'), self.f('A2'), os.path.join(self.data, 'short.jsonl')); rows = {(x['run_a'], x['run_b']): x for x in self.report()['repeat_A']}
        self.assertEqual(rows[('A1.jsonl', 'A2.jsonl')]['n_matched'], 400); self.assertEqual(rows[('A1.jsonl', 'short.jsonl')]['n_matched'], 100)   # not cut to 100 across the board
        self.assertEqual(rows[('A1.jsonl', 'short.jsonl')]['left_out_a'], 300)
        self.assertIn('WARNING', r.stderr); self.assertIn('A1.jsonl loses 75.0%', r.stderr); self.assertTrue(self.report()['drop_warnings'])
        with open(latest(self.out, 'repeat_*.html')) as f: self.assertIn('WARNING', f.read())
    def test_row_counted_once_by_precedence(self):   # a row with a missing correct field is not also a duplicate, a row with no id is not also a missing correct field
        rows = [dict(id='a', correct=True), dict(id='a'), dict(id='b', correct=True), dict(correct=False), dict(id='c', correct='maybe'), dict(id='c', correct=True), dict(id='d', correct=None)]
        jl(os.path.join(self.data, 'p.jsonl'), rows); jl(os.path.join(self.data, 'p2.jsonl'), rows)
        self.rep(os.path.join(self.data, 'p.jsonl'), os.path.join(self.data, 'p2.jsonl')); r = {x['run']: x for x in self.report()['runs']}['p.jsonl']
        self.assertEqual((r['rows_read'], r['usable_items'], r['missing_id_field'], r['missing_correct_field'], r['non_boolean_correct'], r['duplicate_rows'], r['duplicate_ids']), (7, 3, 1, 1, 1, 0, 0))   # a, b and c are usable once each, id d is unscored
        self.assertEqual((r['usable_items'], r['unscored_null_correct']), (3, 1)); self.assertTrue(r['ties_out'])
    def test_warning_always_lists_ids_not_in_other_run(self):   # item 1
        rows = readjl(self.f('A2')); m = rows[:340] + [{'id': x['id']} for x in rows[340:380]]; jl(os.path.join(self.data, 'm.jsonl'), m)
        r = self.rep(self.f('A1'), os.path.join(self.data, 'm.jsonl')); w = self.report()['drop_warnings']; wm = [x for x in w if x.startswith('m.jsonl')][0]; wa = [x for x in w if x.startswith('A1.jsonl')][0]
        self.assertIn('missing correct field: 40', wm); self.assertIn('ids not in the other run: 0', wm); self.assertIn('ids not in the other run: 60', wa)
        self.assertIn('ids not in the other run: 60', r.stderr)
    def test_no_warning_at_or_below_five_percent(self):
        jl(os.path.join(self.data, 'few.jsonl'), readjl(self.f('A2'))[:381])   # 19 of 400 left out is 4.75%
        r = self.rep(self.f('A1'), os.path.join(self.data, 'few.jsonl')); self.assertNotIn('WARNING', r.stderr); self.assertEqual(self.report()['drop_warnings'], [])
        jl(os.path.join(self.data, 'few2.jsonl'), readjl(self.f('A2'))[:379])  # 21 of 400 is 5.25%
        r = self.rep(self.f('A1'), os.path.join(self.data, 'few2.jsonl')); self.assertIn('WARNING', r.stderr)
    # ---- sample, tally
    def sample(self, *extra): return run('sample', self.f('parser'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out, *extra)
    def sheet(self):
        with open(latest(self.out, 'sample_*.csv'), newline='', encoding='utf-8-sig') as f: return list(csv.DictReader(f))
    def test_sample_shape_seed_and_fields(self):
        self.sample(); rows = self.sheet(); self.assertEqual(len(rows), 30)
        for fam in ('good', 'bad', 'edge'): self.assertEqual(sum(r['label'] == fam for r in rows), 10)
        src = {x['id']: x for x in readjl(self.f('parser'))}
        for r in rows: self.assertEqual((r['reply'], r['extracted']), (src[r['id']]['reply'], src[r['id']]['pred']))
        first = {r['id'] for r in rows}; shutil.rmtree(self.out); self.sample(); self.assertEqual(first, {r['id'] for r in self.sheet()})
        shutil.rmtree(self.out); self.sample('--seed', '2'); self.assertNotEqual(first, {r['id'] for r in self.sheet()})
        self.assertIn('read', rows[0]); self.assertIn('misparsed', rows[0])
        with open(latest(self.out, 'sample_*.html')) as f: self.assertIn('more than 10% of its read rows', f.read())
    def test_sample_small_group_and_n(self):
        self.sample('-n', '70'); self.assertEqual(len(self.sheet()), 180)
        shutil.rmtree(self.out); self.sample('-n', '3'); self.assertEqual(len(self.sheet()), 9)
    def fill(self, rows, read='x'):
        for r in rows:   # the reader's verdict: the answer is the last number in the reply
            r['read'] = read; r['misparsed'] = 'x' if re.findall(r'\d+', r['reply'])[-1] != r['extracted'] else ''
        p = os.path.join(self.sh, 'filled.csv'); wcsv(p, rows, ['label', 'id', 'reply', 'extracted', 'read', 'misparsed']); return p
    def tally(self, p, ok=True, record=None):
        o2 = os.path.join(self.tmp, 'tally'); shutil.rmtree(o2, ignore_errors=True); r = run('sample', '--tally', p, '--out', o2, *(['--record', record] if record else []), ok=ok)
        return r, ({x['label']: x for x in jload(latest(o2, 'tally_*.json'))['tally']} if r.returncode == 0 else None)
    def test_tally_rule_on_planted_parser_errors(self):
        self.sample(); rows = self.sheet(); r, t = self.tally(self.fill(rows), record=latest(self.out, 'sample_*.json')); src = {x['id']: x for x in readjl(self.f('parser'))}
        self.assertEqual((t['good']['misparsed'], t['good']['reading']), (0, 'rate can be read'))
        self.assertEqual((t['bad']['misparsed'], t['bad']['reading']), (10, 'cannot tell (parser)'))
        k = sum(src[x['id']]['pred'] != str(int(x['id'].split('-')[1])) for x in rows if x['label'] == 'edge'); self.assertEqual(t['edge']['misparsed'], k)
        self.assertEqual(t['edge']['reading'], 'cannot tell (parser)' if k > 1 else 'rate can be read')
        self.assertIn('bad: 10 of 10 rows read, 0 unread, 10 mis-parsed -> cannot tell (parser)', r.stdout)   # printed on the console too
    def test_tally_boundaries_exact(self):   # more than 10% of read rows: 1 of 10 fine, 2 of 10 not, 1 of 9 not
        for n, k, want in ((10, 0, 'rate can be read'), (10, 1, 'rate can be read'), (10, 2, 'cannot tell (parser)'), (9, 1, 'cannot tell (parser)'), (20, 2, 'rate can be read'), (20, 3, 'cannot tell (parser)')):
            p = os.path.join(self.sh, f'b{n}_{k}.csv'); wcsv(p, [dict(label='L', id=i, reply='r', extracted='e', read='x', misparsed='x' if i < k else '') for i in range(n)], ['label', 'id', 'reply', 'extracted', 'read', 'misparsed'])
            self.assertEqual(self.tally(p)[1]['L']['reading'], want, (n, k))
    def test_tally_unread_rows(self):
        rows = [dict(label='L', id=i, reply='r', extracted='e', read='x' if i else '', misparsed='') for i in range(10)]; rows += [dict(label='M', id=i, reply='r', extracted='e', read='x', misparsed='') for i in range(10)]
        p = os.path.join(self.sh, 'u.csv'); wcsv(p, rows, ['label', 'id', 'reply', 'extracted', 'read', 'misparsed']); r, t = self.tally(p)
        self.assertEqual((t['L']['unread'], t['L']['reading']), (1, 'cannot tell (not read)')); self.assertEqual(t['M']['reading'], 'rate can be read'); self.assertIn('1 unread', r.stdout)
    def test_tally_accepts_words_and_names_bad_rows(self):
        cols = ['label', 'id', 'reply', 'extracted', 'read', 'misparsed']; words = ['ok', 'fine', '0', 'no', 'n', 'false', '', 'OK', 'Fine', ' no ']
        p = os.path.join(self.sh, 'w.csv'); wcsv(p, [dict(label='L', id=i, reply='r', extracted='e', read='x', misparsed=w) for i, w in enumerate(words)], cols)
        self.assertEqual(self.tally(p)[1]['L']['misparsed'], 0)
        p = os.path.join(self.sh, 'w2.csv'); wcsv(p, [dict(label='L', id=i, reply='r', extracted='e', read='x', misparsed=w) for i, w in enumerate(['x', 'bad', '1', 'wrong', 'X', 'misparsed'])], cols)
        self.assertEqual(self.tally(p)[1]['L']['misparsed'], 6)
        p = os.path.join(self.sh, 'w3.csv'); wcsv(p, [dict(label='L', id='a', reply='r', extracted='e', read='x', misparsed=''), dict(label='L', id='b7', reply='r', extracted='e', read='x', misparsed='maybe')], cols)
        r, _ = self.tally(p, ok=False); self.assertNotEqual(r.returncode, 0); self.assertIn("sheet row 3 (label 'L', id 'b7')", r.stderr); self.assertIn("'maybe'", r.stderr); self.assertNotIn('Traceback', r.stderr)
        for w in ('yes', 'y', 'f', 'Y', 'true'):   # ambiguous or unlisted, so each is an error that names the row
            p = os.path.join(self.sh, 'amb.csv'); wcsv(p, [dict(label='L', id='r1', reply='r', extracted='e', read='x', misparsed=w)], cols)
            r, _ = self.tally(p, ok=False); self.assertNotEqual(r.returncode, 0, w); self.assertIn("sheet row 2 (label 'L', id 'r1')", r.stderr)
        p = os.path.join(self.sh, 'w4.csv'); wcsv(p, [dict(label='L', id='u', reply='r', extracted='e', read='', misparsed='x')], cols); self.assertIn('read cell is blank', self.tally(p, ok=False)[0].stderr)
        p = os.path.join(self.sh, 'w5.csv'); wcsv(p, [dict(label='L', id='u', reply='r', extracted='e', read='yes', misparsed='')], cols); self.assertIn('read cell holds', self.tally(p, ok=False)[0].stderr)
    def test_tally_reads_utf8_with_bom(self):   # item 7
        p = os.path.join(self.sh, 'bom.csv')
        with open(p, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=['label', 'id', 'reply', 'extracted', 'read', 'misparsed']); w.writeheader(); w.writerow(dict(label='café', id=1, reply='r', extracted='e', read='x', misparsed=''))
        self.assertEqual(self.tally(p)[1]['café']['reading'], 'rate can be read')
    def test_csv_formula_cells_are_quoted(self):   # item 8
        jl(os.path.join(self.data, 'f.jsonl'), [dict(id=i, family=fam, reply=rep, pred=pr) for i, (fam, rep, pr) in enumerate([('=SUM(A1)', '=1+1', '-5'), ('ok', '+3', '@x'), ('ok', '\tTab', '\rCR'), ('ok', 'plain', 'plain')])])
        run('sample', os.path.join(self.data, 'f.jsonl'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out)
        rows = {r['id']: r for r in self.sheet()}
        self.assertEqual((rows['0']['reply'], rows['0']['extracted'], rows['0']['label']), ("'=1+1", "'-5", "'=SUM(A1)")); self.assertEqual((rows['1']['reply'], rows['1']['extracted']), ("'+3", "'@x"))
        self.assertEqual((rows['2']['reply'], rows['2']['extracted']), ("'\tTab", "'\rCR")); self.assertEqual(rows['3']['reply'], 'plain')
    def test_sample_counts_skipped_rows_and_none_labels(self):   # item 10
        jl(os.path.join(self.data, 's.jsonl'), [dict(id=1, family='a', reply='r', pred='p'), '', dict(id=2, reply='r', pred='p'), dict(id=3, family=None, reply='r', pred='p'), dict(id=4, family='a', reply='r'), '', dict(id=5, family='a', reply='r', pred='p'), dict(id=6, family='a', reply=None, pred='p')])
        r = run('sample', os.path.join(self.data, 's.jsonl'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out)
        sk = jload(latest(self.out, 'sample_*.json'))['skipped']
        self.assertEqual((sk['blank_lines'], sk['rows_skipped_missing_field'], sk['rows_with_null_label_shown_as_none'], sk['rows_read']), (2, 2, 2, 6))   # the JSON null reply of id 6 is missing, not the text null
        self.assertIn('blank lines 2', r.stdout); self.assertIn('skipped for a missing field 2', r.stdout); self.assertEqual({x['label'] for x in self.sheet()}, {'a', '(none)'}); self.assertNotIn('null', ' '.join(x['reply'] + x['extracted'] for x in self.sheet()))
    # ---- second referee
    def test_to_bool_accepts_listed_values(self):   # item 7
        for v in (True, 1, 1.0, 'TRUE', 't', 'Yes', 'y', 'correct', '1'): self.assertIs(IC.to_bool(v), True, v)
        for v in (False, 0, 0.0, 'false', 'F', 'no', 'N', 'incorrect', '0'): self.assertIs(IC.to_bool(v), False, v)
        for v in ('maybe', 2, 0.5, [], None, {}, ''): self.assertIsNone(IC.to_bool(v), v)
        jl(os.path.join(self.data, 'fl.jsonl'), [dict(id=i, correct=float(i % 2)) for i in range(30)]); jl(os.path.join(self.data, 'fl2.jsonl'), [dict(id=i, correct=bool(i % 2)) for i in range(30)])
        self.rep(os.path.join(self.data, 'fl.jsonl'), os.path.join(self.data, 'fl2.jsonl')); self.assertEqual(self.report()['repeat_A'][0]['flips'], 0)
    def test_tiny_p_shown_as_less_than(self):   # item 8
        x = {str(i): True for i in range(2000)}; y = {str(i): False for i in range(2000)}
        c = IC.compare(x, y, sorted(x, key=int), 0.02, 200, 1); self.assertEqual(c['mcnemar_exact_p'], '<1e-300'); self.assertEqual(c['outcome'], 'ABOVE')
        a, b = self.pair_dicts(); self.assertIsInstance(IC.compare(a, b, sorted(a), 0.02, 200, 1)['mcnemar_exact_p'], float)   # an ordinary p stays a number
    def pair_dicts(self):
        a = {f'q{i}': i % 3 != 0 for i in range(400)}; b = dict(a)
        for i in range(0, 120, 3): b[f'q{i}'] = True
        return a, b
    def test_upper_quantile_index(self):   # item 8
        self.assertEqual(IC.ci_bounds(list(range(2000))), (49, 1949)); self.assertEqual(IC.ci_bounds(list(range(1000))), (24, 974))
    def test_bootstrap_method_is_reported_above_5000(self):   # item 4
        n = 6000; x = {str(i): i % 2 == 0 for i in range(n)}; y = dict(x)
        for i in range(0, 300, 2): y[str(i)] = False
        jl(os.path.join(self.data, 'big_a.jsonl'), [dict(id=k, correct=v) for k, v in x.items()]); jl(os.path.join(self.data, 'big_b.jsonl'), [dict(id=k, correct=v) for k, v in y.items()])
        self.rep(os.path.join(self.data, 'big_a.jsonl'), '--vs', os.path.join(self.data, 'big_b.jsonl')); j = self.report()
        self.assertTrue(j['comparison'][0]['bootstrap'].startswith('count draws')); self.assertTrue(any('count draws' in m and 'Python version' in m and 'approximate' in m for m in j['meta']))
        self.assertEqual(j['comparison'][0]['outcome'], 'ABOVE')
        self.rep(self.f('A1'), '--vs', self.f('B1')); self.assertEqual(self.report()['comparison'][0]['bootstrap'], 'items resampled'); self.assertFalse(any('count draws' in m for m in self.report()['meta']))
    def test_tally_cp1252_sheet_gets_a_plain_instruction(self):   # item 5
        p = os.path.join(self.sh, 'cp.csv')
        with open(p, 'wb') as f: f.write('label,id,reply,extracted,read,misparsed\ncaf\u00e9,1,r,e,x,\n'.encode('cp1252'))
        r, _ = self.tally(p, ok=False); self.assertNotEqual(r.returncode, 0); self.assertIn('CSV UTF-8', r.stderr); self.assertNotIn('Traceback', r.stderr)
    def test_sample_csv_has_bom(self):   # item 6
        self.sample()
        with open(latest(self.out, 'sample_*.csv'), 'rb') as f: self.assertEqual(f.read(3), b'\xef\xbb\xbf')
    def test_formula_labels_round_trip_through_the_tally(self):   # item 6
        labs = ['=SUM(A1)', "'=x", 'plain', '-1']
        jl(os.path.join(self.data, 'fl3.jsonl'), [dict(id=f'{l}{i}', family=l, reply='r 5', pred='5') for l in labs for i in range(10)])
        run('sample', os.path.join(self.data, 'fl3.jsonl'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out)
        rows = self.sheet(); self.assertEqual({r['label'] for r in rows}, {"'=SUM(A1)", "''=x", 'plain', "'-1"})
        for r in rows: r['read'] = 'x'
        p = os.path.join(self.sh, 'fl3.csv'); wcsv(p, rows, ['label', 'id', 'reply', 'extracted', 'read', 'misparsed'])
        r, t = self.tally(p, record=latest(self.out, 'sample_*.json')); self.assertEqual(set(t), set(labs)); self.assertTrue(all(x['reading'] == 'rate can be read' for x in t.values()))
    def test_deleted_rows_are_caught_against_the_record(self):   # item 9
        self.sample(); rows = self.sheet(); rec = latest(self.out, 'sample_*.json'); gone = [r for r in rows if r['label'] == 'bad'][:3]; kept = [r for r in rows if r not in gone]
        p = self.fill(kept); r, t = self.tally(p, record=rec)
        self.assertEqual((t['bad']['rows'], t['bad']['rows_missing'], t['bad']['reading']), (7, 3, 'cannot tell (rows missing)')); self.assertEqual(t['good']['reading'], 'rate can be read')
        self.assertTrue(all(i['id'] in t['bad']['missing_ids_examples'] for i in gone[:3])); self.assertIn('3 rows missing', r.stdout)
        p = self.fill([r for r in rows if r['label'] != 'edge']); r, t = self.tally(p, record=rec); self.assertEqual((t['edge']['rows'], t['edge']['reading']), (0, 'cannot tell (rows missing)'))   # a whole label deleted
        p = self.fill(rows + [dict(rows[0])]); r, _ = self.tally(p, record=rec, ok=False); self.assertNotEqual(r.returncode, 0); self.assertIn('rows were added or copied', r.stderr)
        shutil.copy(rec, os.path.join(self.sh, 'filled.json')); r, t = self.tally(self.fill(kept)); self.assertEqual(t['bad']['reading'], 'cannot tell (rows missing)')   # record found beside the sheet by name
        shutil.rmtree(os.path.join(self.tmp, 'tally')); os.remove(os.path.join(self.sh, 'filled.json')); r, t = self.tally(self.fill(kept)); self.assertIn('NOTE: no sample record', r.stderr); self.assertEqual(t['bad']['reading'], 'cannot tell (parser)')   # without the record the missing rows cannot be seen, so the other rules decide
    def test_licence_text_matches_the_code(self):   # item 3
        root = os.path.dirname(H) if os.path.exists(os.path.join(os.path.dirname(H), 'LICENSE.txt')) else None
        if root is None: self.skipTest('LICENSE.txt is not beside the tests')
        with open(os.path.join(root, 'LICENSE.txt'), encoding='utf-8') as f: lic = f.read()
        for w in ('may be run, copied and changed by anyone, for any purpose', 'https://indahl.ai/iris', 'not permitted', 'keep their own terms', 'faultsguards'): self.assertIn(w, lic)
        with open(TOOL, encoding='utf-8') as f: self.assertIn('permits anyone to run, copy and change this code', f.read())
    # ---- real-data referee
    def test_flip_count_printed_and_share_named_by_what_the_user_marked(self):   # item 1
        r = self.rep(self.f('A1'), self.f('A2'))
        self.assertIn('flips 30: right->wrong 20, wrong->right 10, of 400 matched', r.stdout); self.assertIn('flip share between these runs 0.075', r.stdout); self.assertNotIn('repeat floor', r.stdout)
        j = self.report()['repeat_A'][0]; self.assertEqual((j['flips'], j['flip_share']), (30, 0.075)); self.assertNotIn('repeat_floor', j)
        shutil.rmtree(self.out); r = self.rep(self.f('A1'), self.f('A2'), '--repeats')
        self.assertIn('flips 30: right->wrong 20, wrong->right 10, of 400 matched', r.stdout); self.assertIn('repeat floor 0.075', r.stdout); self.assertEqual(self.report()['repeat_A'][0]['repeat_floor'], 0.075)
        with open(latest(self.out, 'repeat_*.html')) as f: self.assertIn('You marked these runs as repeats', f.read())
    def pooled(self, name, models, ids=40, flipk=0):
        rows = [dict(model=m, id=i, correct=(i + j + (flipk if i < flipk else 0)) % 2 == 0) for j, m in enumerate(models) for i in range(ids)]; p = os.path.join(self.data, name); jl(p, rows); return p
    def test_several_id_fields_are_joined_and_pooled_duplicates_give_a_hint(self):   # item 3 and 4
        a = self.pooled('pa.jsonl', ['m1', 'm2']); b = self.pooled('pb.jsonl', ['m1', 'm2'], flipk=3)
        r = run('repeat', a, b, '--id-field', 'id', '--correct-field', 'correct', '--out', self.out, ok=False)   # ids repeat across the two models in each file
        self.assertEqual(r.returncode, 1); self.assertIn('No items matched', r.stderr); self.assertIn('--id-field model id', r.stderr); self.assertIn('ids that repeat', r.stderr)
        shutil.rmtree(self.out, ignore_errors=True); r = run('repeat', a, b, '--id-field', 'model', 'id', '--correct-field', 'correct', '--out', self.out)
        self.assertEqual(self.report()['repeat_A'][0]['n_matched'], 80); self.assertEqual(self.report()['runs'][0]['usable_items'], 80)
    def test_no_match_exits_nonzero_with_the_reason(self):   # item 4
        jl(os.path.join(self.data, 'o.jsonl'), [dict(id=f'z{i}', correct=True) for i in range(30)])
        r = run('repeat', self.f('A1'), os.path.join(self.data, 'o.jsonl'), '--id-field', 'id', '--correct-field', 'correct', '--out', self.out, ok=False)
        self.assertEqual(r.returncode, 1); self.assertIn('No items matched between A1.jsonl and o.jsonl', r.stderr); self.assertTrue(self.report()['no_items_matched'])   # the report is still written
        shutil.rmtree(self.out); r = run('repeat', self.f('A1'), '--vs', os.path.join(self.data, 'o.jsonl'), '--id-field', 'id', '--correct-field', 'correct', '--out', self.out, ok=False)
        self.assertEqual(r.returncode, 1); self.assertIn('No items matched', r.stderr)
    def test_null_correct_is_unscored_and_not_a_warning(self):   # item 5
        rows = readjl(self.f('A2')); n = [dict(r) for r in rows]
        for r in n[:40]: r['correct'] = None
        jl(os.path.join(self.data, 'nulls.jsonl'), n); r = self.rep(self.f('A1'), os.path.join(self.data, 'nulls.jsonl')); j = self.report(); x = {q['run']: q for q in j['runs']}['nulls.jsonl']
        self.assertEqual((x['unscored_null_correct'], x['usable_items'], x['missing_correct_field'], x['non_boolean_correct']), (40, 360, 0, 0)); self.assertTrue(x['ties_out'])
        self.assertIn('unscored (null correct) 40', r.stdout); self.assertFalse([w for w in j['drop_warnings'] if w.startswith('nulls.jsonl')])   # its own nulls are not a warning
        m = [dict(r, correct=None) if i < 40 else (({'id': r['id']}) if i < 70 else r) for i, r in enumerate(rows)]; jl(os.path.join(self.data, 'nulls2.jsonl'), m)   # 40 unscored and 30 absent
        self.rep(self.f('A1'), os.path.join(self.data, 'nulls2.jsonl')); w = self.report()['drop_warnings']; wn = [x for x in w if x.startswith('nulls2.jsonl')][0]
        self.assertIn('missing correct field: 30', wn); self.assertIn('40 rows with a null correct field are unscored, reported separately and not counted here', wn); self.assertIn('of its 360 scored rows', wn)
    # ---- replycheck
    def test_replycheck_help_and_named_arguments(self):
        rc = os.path.join(ROOT, 'parser-check', 'replycheck.py')
        if not os.path.exists(rc): rc = os.path.join(ROOT, 'replycheck.py')
        r = run('--help', script=rc); self.assertIn('--out', r.stdout); self.assertIn('--model', r.stdout); self.assertIn('replycheck_out', r.stdout)
        r = run(script=rc, ok=False); self.assertEqual(r.returncode, 2); self.assertIn('required', r.stderr)
if __name__ == '__main__': unittest.main(verbosity=2)
