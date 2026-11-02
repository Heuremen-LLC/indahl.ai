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
        self.rep(self.f('A1'), self.f('A2')); r = self.report()['repeat_A'][0]; p = PLANTED['A1_vs_A2']
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
        self.rep(self.f('A2'), os.path.join(self.data, 'messy.jsonl')); r = {x['run']: x for x in self.report()['runs']}['messy.jsonl']
        self.assertEqual((r['blank_lines'], r['missing_id_field'], r['missing_correct_field'], r['non_boolean_correct'], r['duplicate_ids_left_out']), (2, 1, 1, 1, 1))
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
    def test_no_warning_at_or_below_five_percent(self):
        jl(os.path.join(self.data, 'few.jsonl'), readjl(self.f('A2'))[:381])   # 19 of 400 left out is 4.75%
        r = self.rep(self.f('A1'), os.path.join(self.data, 'few.jsonl')); self.assertNotIn('WARNING', r.stderr); self.assertEqual(self.report()['drop_warnings'], [])
        jl(os.path.join(self.data, 'few2.jsonl'), readjl(self.f('A2'))[:379])  # 21 of 400 is 5.25%
        r = self.rep(self.f('A1'), os.path.join(self.data, 'few2.jsonl')); self.assertIn('WARNING', r.stderr)
    # ---- sample, tally
    def sample(self, *extra): return run('sample', self.f('parser'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out, *extra)
    def sheet(self):
        with open(latest(self.out, 'sample_*.csv'), newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
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
    def tally(self, p, ok=True):
        o2 = os.path.join(self.tmp, 'tally'); r = run('sample', '--tally', p, '--out', o2, ok=ok)
        return r, ({x['label']: x for x in jload(latest(o2, 'tally_*.json'))['tally']} if r.returncode == 0 else None)
    def test_tally_rule_on_planted_parser_errors(self):
        self.sample(); rows = self.sheet(); r, t = self.tally(self.fill(rows)); src = {x['id']: x for x in readjl(self.f('parser'))}
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
        cols = ['label', 'id', 'reply', 'extracted', 'read', 'misparsed']; words = ['ok', 'y', 'yes', '0', 'no', 'n', 'false', 'f', '', 'OK']
        p = os.path.join(self.sh, 'w.csv'); wcsv(p, [dict(label='L', id=i, reply='r', extracted='e', read='x', misparsed=w) for i, w in enumerate(words)], cols)
        self.assertEqual(self.tally(p)[1]['L']['misparsed'], 0)
        p = os.path.join(self.sh, 'w2.csv'); wcsv(p, [dict(label='L', id=i, reply='r', extracted='e', read='x', misparsed=w) for i, w in enumerate(['x', 'bad', '1', 'wrong', 'X'])], cols)
        self.assertEqual(self.tally(p)[1]['L']['misparsed'], 5)
        p = os.path.join(self.sh, 'w3.csv'); wcsv(p, [dict(label='L', id='a', reply='r', extracted='e', read='x', misparsed=''), dict(label='L', id='b7', reply='r', extracted='e', read='x', misparsed='maybe')], cols)
        r, _ = self.tally(p, ok=False); self.assertNotEqual(r.returncode, 0); self.assertIn("sheet row 3 (label 'L', id 'b7')", r.stderr); self.assertIn("'maybe'", r.stderr); self.assertNotIn('Traceback', r.stderr)
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
        jl(os.path.join(self.data, 's.jsonl'), [dict(id=1, family='a', reply='r', pred='p'), '', dict(id=2, reply='r', pred='p'), dict(id=3, family=None, reply='r', pred='p'), dict(id=4, family='a', reply='r'), '', dict(id=5, family='a', reply='r', pred='p')])
        r = run('sample', os.path.join(self.data, 's.jsonl'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out)
        sk = jload(latest(self.out, 'sample_*.json'))['skipped']
        self.assertEqual((sk['blank_lines'], sk['rows_skipped_missing_field'], sk['rows_with_null_label_shown_as_none'], sk['rows_read']), (2, 1, 2, 5)); self.assertIn('blank lines 2', r.stdout.replace('| ', '')) if False else None
        self.assertIn('blank lines 2', r.stdout); self.assertIn('skipped for a missing field 1', r.stdout); self.assertEqual({x['label'] for x in self.sheet()}, {'a', '(none)'})
    # ---- replycheck
    def test_replycheck_help_and_named_arguments(self):
        rc = os.path.join(ROOT, 'parser-check', 'replycheck.py')
        if not os.path.exists(rc): rc = os.path.join(ROOT, 'replycheck.py')
        r = run('--help', script=rc); self.assertIn('--out', r.stdout); self.assertIn('--model', r.stdout); self.assertIn('replycheck_out', r.stdout)
        r = run(script=rc, ok=False); self.assertEqual(r.returncode, 2); self.assertIn('required', r.stderr)
if __name__ == '__main__': unittest.main(verbosity=2)
