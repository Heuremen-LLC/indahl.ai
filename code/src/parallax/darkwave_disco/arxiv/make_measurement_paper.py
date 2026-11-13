#!/usr/bin/env python3
"""make_measurement_paper.py -- the measurement paper for arXiv (Shuttle's split, 2026-10-04), built from the 3 October in-house draft:
the push-train excess and the control that removes it lead; the old and new Pittsburgh readout ratios both stay; the retracted-simulation model rows are out;
the 4 October runs go in from reads_20261004/paper_tables_20261004.md (generated from the jobs, not typed). Every edit is an exact-match replacement, checked.
Output: MEASUREMENT_PAPER_20261004.md (+ OPEN_QUESTIONS_20261004.md, internal)."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, '..', 'internal', 'MEASUREMENT_PAPER_DRAFT_20261003.md')
TAB = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/paper_tables_20261004.md'
s = open(OLD, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: raise SystemExit(f'expected {n} match(es), found {c}: {a[:100]!r}')
    s = s.replace(a, b)


# ---- the generated tables
T = open(TAB, encoding='utf-8').read()
def table_after(header_start):
    i = T.index(header_start); lines = T[i:].split('\n')[1:]
    out = []; started = False
    for ln in lines:
        if ln.startswith('|'): out.append(ln); started = True
        elif ln.startswith('**') and not started: out.append(ln)
        elif started and ln.strip() == '' and out and out[-1].startswith('|'):
            nxt = T[T.index('\n'.join(out[-1:])) + len(out[-1]):].lstrip('\n')
            if nxt.startswith('**ibm_kingston**') and header_start.startswith('## Table E'): out.append(''); started = False; continue
            break
        elif started and not ln.startswith('|'): break
    return '\n'.join(out).strip()
TA0 = table_after('## Table A-0'); TA1 = table_after('## Table A-1'); TB = table_after('## Table B'); TC = table_after('## Table C'); TD = table_after('## Table D')
iE = T.index('## Table E'); TE = '\n'.join(l for l in T[iE:].split('\n')[2:] if l.strip()).strip()
TE = TE.replace('**ibm_kingston**', '\n**ibm_kingston**\n').replace('**ibm_marrakesh**', '**ibm_marrakesh**\n')
JOBS = [l for l in T.split('\n') if l.startswith('Job IDs:')][0]

# ---- front matter
rep(s.split('\n')[0], '# A few-percent excess after spaced X-gate trains on three superconducting processors, the decay-bookkeeping control that removes it, and one readout timed three ways')
rep('**[AUTHOR -- real name at submission, his call]**', '**Wayfinder and Bones**')
rep('*Draft of 3 October 2026. Internal; not posted.*', '*Draft of 4 October 2026, for the verification pass. Not posted.*')
rep('Times of day are EDT on 2026-10-02 unless stated.', 'Times of day are EDT on 2026-10-02 unless stated; the 4 October runs are marked, and their read files and code are tagged [reads_20261004/<file>] and [code_20261004/<file>].')
a0 = s.index('## Abstract'); a1 = s.index('(Sources for every abstract number')
ABS = ('On three IBM Heron processors, a qubit prepared in |0> and given ten X gates separated by idle intervals ends with more |1> population than one-exponential '
       'decay bookkeeping allows: +1.3 to +3.3% at 30-us intervals across sixteen jobs, rising to +5.8% at 5 us and falling to about zero at 150 us. A qubit prepared in '
       '|1> moves by about as much the other way at short intervals. The excess survives our controls for excitation during |0> intervals, for leakage (back-to-back '
       'trains cap any error that grows with the gate count at 0.26 ± 0.12% per gate) and for shot-to-shot carry-over. It does not survive the bookkeeping: against each '
       "qubit's own decay curve measured in the same job it lies between −1.8% and +0.3% at intervals of 20 us and longer. The decay is faster than one exponential at "
       'short times on most qubits, and the decay time wanders by up to ~7 us between jobs. We report the excess as accounted for by non-exponential decay; at 5-10 us, '
       'where our curve is interpolated, a residual of up to +3.4% remains. We also time one readout three ways (the vendor\'s stated duration, spectator qubits, the '
       "measured qubit's own decay): spectator/vendor 1.04-1.07 on three chips, measured-qubit/vendor 1.40-1.74. On one chip an earlier analysis gave 1.087 and 1.61 "
       'for the same readout; we report both and the method shift. Intervals in |0> add no resolved decay; spectators read a neighbour\'s |1> time, and on Rigetti a '
       'neighbour in |2> pulls a spectator by −62.1 ± 0.6 deg/us; on both vendors a minority of qubits carry |2> population in three behaviours.')
s = s[:a0] + '## Abstract\n\n' + ABS + '\n\n' + s[a1:]

i0 = s.index('## 1 Introduction'); i1 = s.index('No new physics is claimed.')
INTRO = '''## 1 Introduction

The vendor of a superconducting processor publishes per-qubit numbers -- a measurement duration, relaxation times, couplings -- and experiments usually time their events with those numbers and book-keep their populations with one exponential decay per qubit. Here we report what happened when we did that and then tested the bookkeeping.

**The main result is a negative one.** A qubit prepared in |0> and given ten X gates separated by idle intervals ends with a few percent more |1> population than one-exponential decay bookkeeping allows, on three chips, in sixteen jobs over two days. It passes the controls for excitation, leakage and shot-to-shot carry-over listed in Section 3.1. It disappears when the bookkeeping uses each qubit's own decay curve measured in the same job: the decay right after preparation is faster than one exponential, and the excess is the size of that difference. We lead with it because it is a worked example of a few-percent excess that every other control we ran left standing, and because the control that removes it costs a handful of extra circuits in the same job.

Alongside it we report five measurements made with the same harness:

1. **The look.** One readout timed by three clocks: the vendor's stated duration; spectators evolving across a block of readouts on other qubits; and the decay the measured qubit shows per readout. On one chip two analysis methods give ratios 4-13% apart; we give both (Section 3.2).
2. **The park.** Whether a qubit's decay advances while it sits in |0> (Section 3.3).
3. **The witness.** Ramsey spectators reading a neighbour's |1> time; free spectators read through repeated readouts of other qubits at one, two and three or more links; and on Rigetti a neighbour in |2> (Section 3.4).
4. **The third level.** Per-qubit |2> populations at the start of a shot on two vendors, in three behaviours (Section 3.5).

'''
s = s[:i0] + INTRO + s[i1:]
rep('the run headers list outcome categories only [code/push.py; code/noname.py; code/hold.py; code/looktime.py; code/giveback.py; code/witness.py], so every test below is post hoc.',
    'the run headers list outcome categories only [code/push.py; code/noname.py; code/hold.py; code/looktime.py; code/giveback.py; code/witness.py], and the 4 October runs carry none [code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py], so every test below is post hoc.')
rep('*Median qubit*: the median over qubits (the ledger\'s "middle bit").',
    '*Median qubit*: the median over qubits (the ledger\'s "middle bit"). *Driven spectator*: a spectator whose emitter is held in |1>. *Free spectator*: a qubit held on the equator with no emitter driven (4 October).')

# ---- section renumbering of the old text (before new text goes in): old 3.1->3.2, 3.2->3.3, 3.3->3.4, 3.4->3.5, 3.5->3.1
s = s.replace('Sections 3.1-3.5', 'SECS_ALL').replace('Sections 3.3-3.4', 'SECS_34')
for old, new in (('3.1', 'X2'), ('3.2', 'X3'), ('3.3', 'X4'), ('3.4', 'X5'), ('3.5', 'X1')):
    s = re.sub(rf'(Section|section) {re.escape(old)}\b', rf'\1 {new}', s)
    s = s.replace(f'### {old} ', f'### {new} ')
s = re.sub(r'\b(Section|section) X(\d)', r'\1 3.\2', s); s = re.sub(r'### X(\d) ', r'### 3.\1 ', s).replace('SECS_ALL', 'Sections 3.1-3.5').replace('SECS_34', 'Sections 3.4-3.5')

# ---- methods
rep('- **ibm_marrakesh, ibm_kingston**: IBM Heron [§24]. [TO FILL: processor revision and qubit count.] ibm_fez (Heron [§24]) appears only in Sections 3.4-3.5.',
    '- **ibm_marrakesh, ibm_kingston**: 156 qubits each, Heron revision 2, 176-link coupling maps read at fire on 2026-10-04 [reads_20261004/ibm_marrakesh_config_timing_lookwide.json; reads_20261004/ibm_kingston_config_timing_lookwide.json]. Stated measurement duration 2.684 us (ibm_marrakesh) and 2.180 us (ibm_kingston; and ibm_pittsburgh again), read on 2026-10-04 after each readout-timing run\'s first job had landed [reads_20261004/ibm_marrakesh_maker_look_length_20261004.json; reads_20261004/ibm_kingston_maker_look_length_20261004.json; reads_20261004/ibm_pittsburgh_maker_look_length_20261004.json]. ibm_fez (Heron [§24]) appears only in Sections 3.4-3.5.')
rep('| Push run, replication (pushrep.py) | kingston | 141 (one job of three planned) | 17:27:27, landed 17:30:03 | 14 × 400 | 147 | 3.5 |',
    '| Push run, replication (pushrep.py) | kingston | 141 (one job of three planned) | 17:27:27, landed 17:30:03 | 14 × 400 | 147 | 3.5 |\n'
    '| Push train, interval swept, decay read three times per job (time_wide.py) | marrakesh, kingston / pittsburgh | 301-303 (3 each) / 361 (one job) | 2026-10-04 10:07-10:21 / 11:11 | 50 × 300 | 136-138 / 142-147 / 149 | 3.1 |\n'
    '| Readout timing, wide (look_wide.py) | marrakesh / kingston / pittsburgh | 311-313 / 331-333 (3 each) / 351 (one job) | 2026-10-04 10:26-10:31 / 10:41-10:51 / 11:09 | 37 × 400 | 77-86 spectators, 28-31 measured qubits | 3.2 |\n'
    '| Free spectators (count_wide.py) | marrakesh / kingston | 321-323 / 341-343 (3 each) | 2026-10-04 10:33-10:39 / 10:55-11:04 | 34 × 300 | 119-121 spectators | 3.4 |')
s = s.replace('| 3.5 |\n| Push train', '| 3.1 |\n| Push train')
s = re.sub(r'\| (3\.[1-5]) \|$', lambda m: '| ' + m.group(1) + ' |', s, flags=re.M)
rep('§145, §152, §153]. Earlier IBM jobs', '§145, §152, §153; reads_20261004/paper_tables_20261004.md; code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py; §182-§191]. ' + JOBS.replace('Job IDs:', '4 October job IDs:') + '. Earlier IBM jobs')
rep('so the spectator\'s own frame rotation cancels over each pair of intervals while its emitter\'s |1> time accumulates ("frame-held") [code/noname.py; §145].',
    'so the spectator\'s own frame rotation cancels over each pair of intervals while its emitter\'s |1> time accumulates ("frame-held") [code/noname.py; §145]. In the 4 October readout-timing runs the same seed and rule are applied to each chip\'s coupling map read at fire, giving 39 emitters, 86 spectators and 31 far qubits on all three chips [reads_20261004/lookwide_roles_ibm_pittsburgh.json; code_20261004/look_wide.py]. In the free-spectator runs no emitter is driven: every qubit that is not a far qubit is put on the equator and read on two axes after the block, and is labelled afterwards by its number of links to the nearest far qubit [code_20261004/count_wide.py; code_20261004/readwitness_wide.py].')
rep('- **each interval\'s own**: q_L = P(L), the level of the qubit prepared in |1> and left L = 10, 30 or 90 us, measured in the same job (interval-length job only) [code/readnoname.py].',
    '- **each interval\'s own**: q_L = P(L), the level of the qubit prepared in |1> and left L = 10, 30 or 90 us, measured in the same job (interval-length job only) [code/readnoname.py];\n'
    '- **curve** (4 October): q_L read off the same job\'s |1>-idle levels at 0, 30, 100, 300 and 600 us, log-linear between points; each of the three copies of those arms gives its own curve and the tables average the three [code_20261004/readtime.py]. Below 30 us this curve is an interpolation, not a measurement.')
rep('Values are means over readable qubits unless marked "median qubit".', 'Values are means over readable qubits unless marked "median qubit"; the 4 October readers use 30-60 bootstrap resamples [code_20261004/paper_tables.py].')

# ---- the retracted-simulation rows: out
rep('(d) The back-to-back cap, 0.26 ± 0.12% per gate (0.49% at two widths), against 2.96% per gate needed by a leakage-plus-TLS model to fit all three starts [§146, §147]; x2 cancels',
    '(d) The back-to-back cap, 0.26 ± 0.12% per gate (0.49% at two widths) [§147]; x2 cancels')
rep(' (e) A leakage-only model misses start 0 by 5.6 widths and start 1 by 6.5; a TLS-only model misses by 8.4 and 6.1 [§146]. (f) The extra-X identity', ' (e) The extra-X identity')
rep('the leakage and TLS model comparisons, ', '')

# ---- results: reorder (3.1 = the push train first)
r0 = s.index('### 3.2 The look'); r_push = s.index('### 3.1 The push-train excess'); r_end = s.index('---\n\n## 4 Limitations')
push = s[r_push:r_end]; rest = s[r0:r_push]
push = push.replace('### 3.1 The push-train excess (a negative result)', '### 3.1 The push-train excess and the control that removes it')
SWEEP = f'''
**The excess swept over interval length (4 October).** Every qubit of ibm_marrakesh and ibm_kingston (three jobs each) and ibm_pittsburgh (one job): starts 0, 1 and halfway, ten X gates each preceded by an interval of 5, 10, 20, 30, 45, 70, 100 or 150 us, one readout at the end. In the same jobs: the qubit's decay from |1> read at 30, 100, 300 and 600 us in three copies placed by the shuffled circuit order, an idle |0> at 300 and 600 us, an echo, and back-to-back trains [code_20261004/time_wide.py]. The 30-us row repeats the 2 October circuit. The tables below give start 0 and start 1 against one-exponential and curve bookkeeping [reads_20261004/paper_tables_20261004.md].

**TBL_A0.** Ten X gates, each after an interval; start 0; level minus bookkeeping (mean of three jobs, or one job on ibm_pittsburgh).

{TA0}

**TBL_A1.** The same, start 1.

{TA1}

Against one exponential, start 0 at 30 us reads +0.0302 ± 0.0020 (ibm_marrakesh) and +0.0325 ± 0.0019 (ibm_kingston), against +0.0274 ± 0.0028 and +0.0287 ± 0.0028 in their single 2 October jobs, and +0.0171 ± 0.0028 on ibm_pittsburgh (one job). The excess grows as the interval shortens, to +0.058 at 5 us on ibm_marrakesh and ibm_kingston and +0.027 on ibm_pittsburgh, and start 1 moves by about as much the other way at 5-20 us. Back-to-back trains in the same jobs move starts 0 and 1 by +1.0 to +1.2% and −1.0 to −1.1% for ten gates on all three chips; the halfway start moves +2.8% (ibm_marrakesh), −1.1% (ibm_kingston) and +2.6% (ibm_pittsburgh).

**TBL_B.** X gates back to back (4 October): level minus the no-gate arm.

{TB}
'''
anchor = '[reads/rep_marrakesh_read1.txt; reads/close_push.txt; §152].'
assert push.count(anchor) == 1; push = push.replace(anchor, anchor + '\n' + SWEEP)
assert push.count('**Non-exponential decay.**') == 1; push = push.replace('**Non-exponential decay.**', "**The control that removes it: each qubit's own decay.**")
CURVE = f'''
**The same control on three chips (4 October).** Against each job's own decay curve, the start-0 excess at intervals of 20 us and longer reads −0.0182 to −0.0120 on ibm_marrakesh, −0.0063 to +0.0033 on ibm_kingston, and −0.0064 to +0.0034 on ibm_pittsburgh (one job); start 1 reads −0.0156 to −0.0018, −0.0033 to +0.0027 and −0.0035 to +0.0028 (tables above). At 5 and 10 us a residual remains: +0.0191 / +0.0040 (ibm_marrakesh), +0.0337 / +0.0195 (ibm_kingston) and +0.0108 / +0.0073 (ibm_pittsburgh) for start 0, with the opposite sign for start 1; there the curve is interpolated between its 0- and 30-us points (Section 2.6). The decay is faster than one exponential qubit by qubit, not only in the mean: at 30 us a qubit's |1> level sits below the exponential through its own 300-us level on 72-84% of qubit-copies on ibm_marrakesh and ibm_kingston (medians −0.020 to −0.036) and on 62% on ibm_pittsburgh (median −0.008), and above it at 600 us on 57-74% [reads_20261004/decay_bend_per_qubit_20261004.txt]. The decay time itself moves: the three copies give 168-183 us on ibm_marrakesh, 260-270 us on ibm_kingston and 294-297 us on ibm_pittsburgh; within a job the copies differ by up to 10 us (about two widths), and job means move by up to ~7 us between jobs minutes apart. The idle |0> arms read +0.0037 to +0.0080 after 300 us on ibm_marrakesh and ibm_kingston and +0.0004 on ibm_pittsburgh, against start-0 excesses of +0.030 and +0.033 at 30 us against one exponential [reads_20261004/paper_tables_20261004.md].

**TBL_C.** The decay clock read three times per job (copies a, b, c): decay time from the 300-us level (median qubit); idle |0>; echo.

{TC}
'''
anchor2 = 'We take the excess against one-exponential bookkeeping to be accounted for by non-exponential decay.'
assert push.count(anchor2) == 1; push = push.replace(anchor2, anchor2 + '\n' + CURVE)
old_na = "Not accounted for here, with one job each and no own-interval arms: ibm_kingston's start-1 column (−0.0124 ± 0.0024) and the chip-to-chip halfway start (Table 6)."
assert push.count(old_na) == 1
push = push.replace(old_na, "ibm_kingston's start-1 column, −0.0124 ± 0.0024 in its single 2 October job, reads −0.0133 ± 0.0017 against one exponential and −0.0004 ± 0.0022 against its own curve in the three 4 October jobs at 30 us. Not accounted for: the chip-to-chip halfway start (Table 6 and TBL_B) and the 5-10-us residual above.")
LOOK = f'''
**The same look on three chips, and a second method (4 October).** The readout-timing protocol was rebuilt to time the look three ways in one job. Spectators beside emitters held in |1> are read after blocks of 1, 2, 3, 4, 6 and 9 readouts on far qubits and after delays of 0-240 us; the time per readout is the slope over block size of each spectator's phase, converted to time on its own delay curve. The far qubits themselves are prepared in |1>, read 1-9 times, and their fall converted to time on their own decay over 10, 20 and 40 us; the time per readout is again the slope over block size [code_20261004/look_wide.py; code_20261004/readlook_wide.py].

**TBL_D.** One readout timed three ways in one job, per job (4 October).

{TD}

On ibm_pittsburgh the same readout timed by the earlier method (Ratios, above) and by this one gives spectator / vendor 1.087 ± 0.015 and 1.040 ± 0.022 (−4.3%), measured qubit / vendor 1.61 ± 0.09 and 1.405 ± 0.103 (−12.7%), and measured qubit / spectator 1.48 ± 0.09 and 1.351 ± 0.103 (−8.7%) [derived here]. The earlier method takes the measured qubit's time from blocks of 3 and 9 readouts inside a 300-us idle and the spectators' from blocks of 3 and 9; the new one fits the slope over 1-9 readouts. A ratio that moves this much with the method is reported here as a measurement of the method as much as of the chip. With the new method, spectator / vendor stays at 1.040-1.072 on three chips while measured qubit / vendor ranges 1.40-1.74; on ibm_marrakesh the spectator time rose job by job (2.760, 2.803, 2.846 us), on ibm_kingston it held (2.312-2.337 us).
'''
anchor3 = '[derived here from §135 and reads/close_looktime.txt; widths propagated as independent].'
assert rest.count(anchor3) == 1; rest = rest.replace(anchor3, anchor3 + '\n' + LOOK)
FREE = f'''
**Free spectators through repeated readouts of other qubits (4 October).** With no emitter driven, every qubit that is not a far qubit was held on the equator through blocks of 1-32 readouts on the 31 far qubits and through delays of 0-120 us (three jobs on each of ibm_marrakesh and ibm_kingston; 119-121 readable spectators) [code_20261004/count_wide.py]. The table gives the contrast kept, relative to no delay, by links to the nearest far qubit, and the readout duration timed on these spectators as in Section 3.2.

**TBL_E.** Free spectators (4 October), mean of three jobs per chip.

{TE}

A block of k readouts costs these spectators about what k times the vendor's duration of delay costs them (on ibm_marrakesh, 12 readouts, about 32 us, keep 0.34-0.45 against 0.39-0.49 after 30 us of delay). On both chips the spectators two links from the nearest far qubit time the readout shortest (1.26 ± 0.16 us against 1.64-1.82 on ibm_marrakesh; 0.82 ± 0.16 us against 1.56-1.82 on ibm_kingston), and on ibm_marrakesh they also keep the least contrast. Free spectators time the readout shorter than the vendor's duration on both chips; spectators beside emitters held in |1> time it longer (Section 3.2). What the two-link seats are in the coupling map was not examined.
'''
anchor4 = 'difference +0.0020 ± 0.0032 deg [reads/close_looktime.txt].'
assert rest.count(anchor4) == 1; rest = rest.replace(anchor4, anchor4 + '\n' + FREE)
s = s[:r0] + push + rest + s[r_end:]

# ---- limitations, data, open questions
l1 = s.index('1. **Replication depth.**'); l2 = s.index('2. **Comparisons within jobs only.**')
s = s[:l1] + ('1. **Replication depth.** The push train with intervals swept and the decay read in the same jobs has three jobs on each of ibm_marrakesh and ibm_kingston and one on ibm_pittsburgh (4 October). The interval-length job with own-interval arms (2 October) is one of three planned (runs 122-123 frozen, not fired) [§157], and the spectator stopwatch one of three [reads/witness_run.txt]. The 4 October readout-timing run has one job on ibm_pittsburgh, and the free-spectator run none there. Every own-interval number of 2 October and every frame-held spectator number rests on one job.\n') + s[l2:]
rep('6. **Earlier analyses.**', '6. **Method dependence.** On ibm_pittsburgh two analysis methods give readout-timing ratios 4-13% apart for the same readout (Section 3.2); both are given, and no ratio here is offered as a match to any constant.\n7. **The curve bookkeeping below 30 us** is interpolated between the 0- and 30-us points; the 5-10-us residuals of Section 3.1 rest on it.\n8. **Earlier analyses.**')
rep('[SHA256SUMS.txt; all 83 entries re-checked against the files for this draft]', '[SHA256SUMS.txt; 118 entries]')
rep('- **fire_logs/** (3 files; fire_logs_after.txt is empty);', '- **fire_logs/** (fire_logs_after.txt is empty; the 4 October fire logs are fire_logs_time.txt, fire_logs_look.txt, fire_logs_witness.txt);\n- **reads_20261004/**, **code_20261004/**: the 4 October tables (generated from the jobs), per-chip dumps, role maps, configuration and duration reads, the decay-bend read, and the run and reader scripts;\n- [TO FILL: a DOI archive (for example Zenodo) for the release and for the correction log, so the links outlive a personal domain.]')
oq = s.index('## OPEN QUESTIONS FOR THE AUTHORS')
open(os.path.join(HERE, 'OPEN_QUESTIONS_20261004.md'), 'w', encoding='utf-8').write('# Open questions for the measurement paper (internal; carried from the 3 October draft, with 4 October notes)\n\n4 October: #6 answered (both methods printed, no matches claimed); #7 partly (4 October job IDs in Section 2.4; processor revision and qubit count for ibm_marrakesh and ibm_kingston read); #11 partly (ibm_kingston start 1 read three times against its own curve).\n\n' + s[oq:])
s = s[:oq].rstrip().rstrip('-').rstrip() + '\n'

# ---- 4 October, the second vendor: Rigetti Cepheus (§192-§217), and ibm_fez (§202-§203)
rep('on Rigetti a neighbour in |2> pulls a spectator by −62.1 ± 0.6 deg/us; on both vendors a minority of qubits carry |2> population in three behaviours.',
    'on Rigetti a neighbour in |2> pulls a spectator by −62.1 ± 0.6 deg/us (28 September) and −35 to −41 deg/us (4 October); on both vendors a minority of qubits carry |2> population in three behaviours. '
    'On Rigetti Cepheus the same train with every qubit driven gives +2.5 to +12.7% against one exponential and +1.6 to +7.3% against each qubit\'s own curve, while ten back-to-back gates alone move |0> by +7.6%, and that gate error rises from about 6% to about 10% when the neighbours are held on the equator instead of at rest. '
    'Spectators one link away read the time emitters spend in |2> during a train on the |1>-|2> pair at 0.8-1.5 times the time booked from the emitters\' own decay; and the state of the spectators at readout scales the emitters\' |2> reading by 0.81 at every delay, while the shape of the decay is unchanged.')
rep('- **Rigetti Cepheus-1-108Q** through Amazon Braket with pulse access; 563 tasks from 2026-09-25 to 2026-09-28 [§28, §154].',
    '- **Rigetti Cepheus-1-108Q** through Amazon Braket with pulse access; 563 tasks from 2026-09-25 to 2026-09-28 [§28, §154] and 680 tasks on 2026-10-04 [§192-§217; rigetti_20261004/braket_ledger.json].')
rep('we give both (Section 3.3).', 'we give both (Section 3.2).'); rep('sits in |0> (Section 3.4).', 'sits in |0> (Section 3.3).'); rep('and on Rigetti a neighbour in |2> (Section 3.5).', 'and on Rigetti a neighbour in |2> (Section 3.4).')
rep("4. **The third level.** Per-qubit |2> populations at the start of a shot on two vendors, in three behaviours (Section 3.1).\n",
    "4. **The third level.** Per-qubit |2> populations at the start of a shot on two vendors, in three behaviours (Section 3.5).\n"
    "5. **The second vendor, 4 October.** The push train with every qubit of Rigetti Cepheus driven, the same train on the |1>-|2> pair read by spectators, the spectators' |2> ruler measured round to round, and the readout cross-talk between spectators and emitters in both directions (Section 3.6).\n")
FEZ = '''
**A second chip for the slope with gate count (ibm_fez, 4 October, one job).** Start 0, an X gate after every 30-us interval, 2, 6 and 10 gates, every readable qubit (133), against three bookkeepings from the same job: each interval's own decay +0.0058 / −0.0050 / −0.0087, slope −0.00182 ± 0.00027 per gate; the 90-us level scaled +0.0252 / +0.0160 / +0.0067, slope −0.00231 ± 0.00028; one exponential through the 300-us level +0.0500 / +0.0463 / +0.0302, slope −0.00247 ± 0.00029 [reads_20261004/five_slope_fez_20261004.txt; reads_20261004/five_slope.py; reads_20261004/freeze_ibm_fez_run371.json; §202-§203]. On ibm_pittsburgh (2 October, own interval) the slope was −0.00106 ± ~0.0008.
'''
s = s.replace('\n### 3.2 The look', FEZ + '\n### 3.2 The look', 1)
rep('What the two-link seats are in the coupling map was not examined.',
    'What the two-link seats are in the coupling map was not examined. With the original reader, the readout duration timed on free spectators is 0.62 us in five groups on two chips (ibm_kingston: emitter seats at two and at three or more links, and two of the two-link contrast bands; ibm_marrakesh: the one-link low-contrast band), carried by q35 and q47 (ibm_marrakesh) and q99, q117 and q153 (ibm_kingston); two further readers are kept beside it (medians over all spectators 1.47 / 2.29 / 2.81 us on ibm_marrakesh, 1.45 / 2.22 / 2.35 us on ibm_kingston) [reads_20261004/the_062_rows_20261004.txt; §199-§200]. We report the recurrence as read.')
CEPH = '''
### 3.6 Rigetti Cepheus, 4 October: the train on two pairs of levels and the spectators' readout

Every qubit is in every circuit; each qubit's |1>-|2> transition is driven by a 32-ns DRAG-Gaussian pulse on its |1>-|2> frame with a per-qubit amplitude (99 of 107 qubits reach |2>; median amplitude 0.155 against 0.150 on 28 September, per-qubit change median 0.000 [rigetti_20261004/tune_vs_0928.txt]); populations of |1> and |2> are solved per qubit from a plain read and a swap-then-flip read on an eight-sequence readout model calibrated in the same batch [code_20261004/rigetti_time.py; code_20261004/readrigetti_time.py; code_20261004/rigetti_gamble.py]. 900 shots per circuit, 1500 per calibration circuit. No outcome was written for any run [§192-§217].

**The push train, every qubit driven.** Ten X gates after intervals of 1, 3, 8 and 20 us from |0>: +0.127 / +0.110 / +0.066 / +0.025 against one exponential through 30 us, +0.073 / +0.048 / +0.037 / +0.016 against each qubit's own decay curve read in the same batch (0.83 / 0.63 / 0.33 at 3 / 10 / 30 us against 0.90 / 0.69 for one exponential); |2> 0.005-0.014 in every arm [rigetti_20261004/read1_raw_nocut.txt; §193]. Ten X gates back to back move |0> by +0.076 and |1> by −0.068: on this chip the gate error is the size of the excess. A second batch 188 s later repeats the short intervals and moves the long ones (20 us, own curve +0.016 -> +0.029) [rigetti_20261004/read2_raw_nocut.txt; §194]. The excess against the own curve depends on the readout-quality band (3 us: +0.041 / +0.053 tight, +0.026 / −0.008 middle, −0.028 / −0.013 loose, two batches); against one exponential it is +0.07 to +0.13 in every band [§194].

**The gate error and the neighbours.** Seven emitters at least five links apart, ten X gates back to back, their 22 neighbours at rest, driven in step, or held on the equator, interleaved, three rounds 3 minutes apart, each round with its own readout calibration: read-1 fraction 0.0643 / 0.0641 / 0.0584 (neighbours at rest), 0.0646 / 0.0656 / 0.0560 (driven in step), 0.1102 / 0.1010 / 0.1038 (on the equator) [rigetti_20261004/triB_raw.txt; §206]. Readout models were steady (r0 0.995-0.997).

**A spectator beside a |2> neighbour, all three clocks in one batch.** q0 at rest, in |1> or in |2> for 0.5-6 us; q0's own |2> population 0.893 / 0.888 / 0.847 / 0.733 / 0.586; q9 (one link) moves by −36.1 / −34.6 / −41.4 deg/us at 0.5 / 1 / 2 us with q0 in |2>, q1 by −27.5 / −19.4 / −21.0; with q0 in |1>, q1 −8.5 / −7.8 / −5.9 and q9 +0.5 / +5.9 / +1.7; 101 spectators three or more links away: medians −0.6 to +1.6 [rigetti_20261004/triA_raw.txt; §205]. q9's pull is −35 to −41 deg/us here against −62.1 ± 0.6 on 28 September (Section 3.4).

**Spectators reading a train on the |1>-|2> pair.** The seven emitters, prepared in |1> or |2>, receive ten |1>-|2> swaps over L = 1, 2 and 4 us; every other qubit is a free spectator. References at each L: emitters held in |1> and held in |2>. The time the emitters spend in |2>, as a spectator reads it, is (turn in the train − turn held in |1>) / ((turn held in |2> − turn held in |1>) / L); it is set beside the time laid (5 intervals of L/10) and the time booked from the emitters' own decay from |2> and from |1> read in the same batch [code_20261004/rigetti_triangle_d.py; code_20261004/readrigetti_triangle_d.py].

**TBL_R1.** Time in |2> during a ten-swap train on the |1>-|2> pair: laid, booked from the emitters' own decay, and read by the 22 spectators one link away (median and quartiles; where the wrapped and unwrapped readings differ both are given, with the quartiles of the unwrapped) [rigetti_20261004/triD_raw.txt].

| Start | L (us) | Laid (us) | Booked (us) | Spectators, 1 link (us) | Pull, level 2 minus level 1 (deg/us) |
|---|---|---|---|---|---|
| from 1 | 1 | 0.50 | 0.48 | 0.56 [0.36, 0.80] | −6.87 |
| from 1 | 2 | 1.00 | 0.91 | 0.92 [0.64, 1.04] | −7.31 |
| from 1 | 4 | 2.00 | 1.68 | 1.48 / 1.83 [0.55, 2.13] | −2.96 / −3.93 |
| from 2 | 1 | 0.50 | 0.49 | 0.64 [0.42, 0.81] | −6.87 |
| from 2 | 2 | 1.00 | 0.96 | 1.03 [0.80, 1.42] | −7.31 |
| from 2 | 4 | 2.00 | 1.85 | 2.09 [0.96, 2.50] | −2.96 / −3.93 |

At two links the pull is within ±1.5 deg/us of zero and the spectators' quartiles straddle zero. Each push adds 32 ns not counted in the laid column (0.16 us at half weight over ten pushes). A |0> start (the swap has nothing to act on) reads −0.20 / +0.07 / −0.78 us at one link. Across a second batch with 4, 10 and 20 swaps at each L, spectator-read over booked time is 0.86 / 1.30 / 1.16, 1.08 / 1.20 / 1.22, 1.15 / 1.47 / 1.14 (start |1>, N = 4 / 10 / 20, L = 1 / 2 / 4 us) and 0.80 / 1.54 / 1.28, 1.22 / 1.25 / 1.31, 1.04 / 1.46 / 1.24 (start |2>): no order with N, and the L = 2 us column is the highest in all six; the booked time repeats between the batches within 0.03 us, and the emitters' end state follows N (start |1>, |2> population after the train 0.15-0.19, 0.28-0.35, 0.35-0.38 for N = 4, 10, 20) [rigetti_20261004/triE_raw.txt; §211].

**The spectators' |2> ruler, round to round.** Emitters held at rest, in |1> or in |2> for 0.25-6 us, three rounds 3 minutes apart, each with its own readout calibration; the populations come from the same shots. Per unit population, the one-link spectators' |2> pull is −4.9 to −17.6 deg/us over windows and rounds (median −9.7, quartiles −11.2 and −8.0; at 4 us −8.0 / −9.3 / −8.1, at 0.5 us −17.6 / −15.2 / −7.4), the |1> pull −3.9 to +3.3 (median −1.1); the spectators' own drift between rounds (emitters at rest) is −1.2 to +3.7 deg/us; the populations repeat within 0.01-0.04 [rigetti_20261004/triF_raw.txt; §213].

**The spectators' state in the emitters' readout.** The emitters held in |2> for 0.5, 2 and 4 us, with every other qubit at rest; on the equator during the delay and rotated back by a full turn; on the equator and rotated by a further quarter turn (as in the runs above); in |1> throughout; or at rest during the delay and put in |1> just before readout. Populations are solved with three readout models: the shared calibration (every qubit runs the eight sequences), and emitter-only calibrations with the other qubits at rest or in |1> [code_20261004/rigetti_triangle_g.py; rigetti_20261004/triG_raw.txt; §215].

**TBL_R2.** The emitters' |2> population by the other qubits' state; three readout models (shared / emitter-only, others at rest / emitter-only, others in |1>).

| Other qubits | 0.5 us | 2 us | 4 us |
|---|---|---|---|
| at rest | 0.897 / 0.889 / 0.990 | 0.824 / 0.814 / 0.910 | 0.709 / 0.696 / 0.784 |
| equator, turned back | 0.817 / 0.801 / 0.894 | 0.715 / 0.697 / 0.781 | 0.638 / 0.621 / 0.700 |
| equator, quarter turn | 0.805 / 0.790 / 0.880 | 0.714 / 0.696 / 0.782 | 0.635 / 0.618 / 0.697 |
| in 1 throughout | 0.719 / 0.698 / 0.778 | 0.668 / 0.648 / 0.728 | 0.572 / 0.554 / 0.624 |
| in 1 at readout only | 0.731 / 0.711 / 0.795 | 0.678 / 0.657 / 0.736 | 0.577 / 0.556 / 0.630 |

The other qubits' state at readout, not during the delay, sets the reading (|1> throughout and |1> at readout only agree within 0.012; the two equator arms agree within 0.012 and sit between rest and |1>). The ratio to the rest arm is 0.815 / 0.823 / 0.814 (|1> at readout only) at every delay, and the decay shape, 4 us over 0.5 us, is 0.78-0.80 in all five arms. The matched model (others in |1>) takes about 40% of the difference. With the emitters in |1> the shift runs the other way (|1> population 0.935 -> 0.945, |2> 0.031 -> 0.018 at 0.5 us). In the opposite direction, emitters put in |1> or |2> at readout move the spectators' read by −3.0 to +2.2 deg (medians), and the pairing of read axes used throughout this section shifts the |2>-held arm by at most 0.75 deg/us at one link [rigetti_20261004/triH_raw.txt; §217].
'''
s = s.replace('\n---\n\n## 4 Limitations', '\n' + CEPH + '\n---\n\n## 4 Limitations', 1)
assert s.count('### 3.6 Rigetti Cepheus') == 1
rep('7. **The curve bookkeeping below 30 us**', '7. **Rigetti, one day.** Section 3.6 rests on one day of 680 tasks on one chip; the spectators\' |2> ruler moves 30-50% between rounds at a single delay, and the emitters\' readout depends on the other qubits\' state at readout (TBL_R2).\n8. **The curve bookkeeping below 30 us**')
s = s.replace('\n8. **Earlier analyses.**', '\n9. **Earlier analyses.**', 1)
rep('[SHA256SUMS.txt; 118 entries]', '[SHA256SUMS.txt; RELEASE_N entries]')
rep('- **reads_20261004/**, **code_20261004/**: the 4 October tables (generated from the jobs), per-chip dumps, role maps, configuration and duration reads, the decay-bend read, and the run and reader scripts;',
    '- **reads_20261004/**, **code_20261004/**: the 4 October tables (generated from the jobs), per-chip dumps, role maps, configuration and duration reads, the decay-bend read, and the run and reader scripts;\n'
    '- **rigetti_20261004/**: every 4 October Rigetti batch as raw shots (.npz), the read outputs, the per-qubit tuning, the coupling map, and the task lists (task IDs with the account number blanked);')
N = sum(1 for _ in open(os.path.join(HERE, '..', 'for_indahl_ai', 'data', 'SHA256SUMS.txt')))
s = s.replace('RELEASE_N entries', f'{N} entries')
rep(" [TO FILL: ...] marks what the sources do not hold.", " The 5 October files are tagged [reads_20261005/<file>] and [code_20261005/<file>].")
rep('The data release (links at submission) holds,', 'The data release, archived at Zenodo (doi:10.5281/zenodo.23169756), holds,')
rep('- [TO FILL: a DOI archive (for example Zenodo) for the release and for the correction log, so the links outlive a personal domain.]',
    '- **reads_20261005/**, **code_20261005/**, **rigetti_20261005/**: the 5 October reads, run and reader scripts (with the provenance check), and every 5 October Rigetti batch as raw shots;\n'
    '- **calls/**, **freeze/**, **run_index/**, **early/**: every hashed call with its sha256 and OpenTimestamps proof, the freeze records, the job and task index, and the 24-29 September run folders;\n'
    '- **trail/**: a copy of the correction log (thetrailtothepast.com) as of the archive date, so the corrections outlive the domain;')


# ---- 4 October evening (§228-§235)
rep('spectator/vendor 1.04-1.07 on three chips, measured-qubit/vendor 1.40-1.74.',
    'spectator/vendor 1.02-1.07 on three chips (three jobs each), measured-qubit/vendor 1.26-1.74; with a readout tone we lay ourselves on a second vendor, spectator/laid is 0.97-1.01.')
rep('On ibm_pittsburgh (2 October, own interval) the slope was −0.00106 ± ~0.0008.',
    'On ibm_kingston (one job, 144 qubits, a third chip): +0.0038 / −0.0067 / −0.0120 against each interval\'s own decay, slope −0.00198 ± 0.00035; −0.00178 ± 0.00031 against the 90-us level; −0.00104 ± 0.00031 against one exponential [reads_20261004/five_slope_kingston_20261004.txt; code_20261004/five_slope_kingston2.py; §235]. On ibm_pittsburgh (2 October, own interval) the slope was −0.00106 ± ~0.0008. On ibm_pittsburgh\'s two further 4 October jobs of the swept train, start 0 against one exponential reads +0.0347 / +0.0332 (10 us), +0.0240 / +0.0196 (30 us), +0.0069 / +0.0111 (100 us), and against the curve within ±0.008 past 20 us [reads_20261004/time_wide_pittsburgh_reads123_20261004.txt; §229].')
rep('on ibm_kingston it held (2.312-2.337 us).',
    'on ibm_kingston it held (2.312-2.337 us). On ibm_pittsburgh\'s three jobs: spectator / vendor 1.040 / 1.039 / 1.018, measured qubit / vendor 1.405 / 1.415 / 1.259 [reads_20261004/look_wide_pittsburgh_reads123_20261004.txt; §228].\n\n**The same three clocks on a readout we lay ourselves (Rigetti Cepheus).** A 1-us tone on seven qubits\' readout lines, then 0.5 us for the resonator to empty, is one look of laid length 1.5 us; every other qubit is a spectator whose frame is detuned by 100 kHz, and the look is one pulse block spanning all 107 qubits (a first run without that fence let the spectators skip the tone and timed only the shared 0.5 us; §231). A look with the tone at zero is the timing check: the spectators read it at 1.4937 us (0.996). At tone strengths 0.03 / 0.045 / 0.06: spectator / laid 0.994 / 1.008 / 0.968, measured qubit / laid 1.024 / 1.024 / 0.879 [rigetti_20261004/lookTri2_raw.txt; code_20261004/rigetti_look_triangle.py; §234]. The 2-7% by which spectators read IBM\'s readout beyond the vendor\'s stated duration does not appear when the duration is laid by us.')
rep('We report the recurrence as read.',
    'We report the recurrence as read. On ibm_pittsburgh\'s free spectators (three jobs, same reader) no group reads 0.62 us; the nearest are 0.56 and 0.53, in the two-link class [reads_20261004/witness_seats_kingston_pittsburgh_20261004.txt; code_20261004/readwitness_seats.py; §230].')
rep('at one link [rigetti_20261004/triH_raw.txt; §217].',
    'at one link [rigetti_20261004/triH_raw.txt; §217].\n\n**After a recalibration.** Cepheus recalibrated at 18:02Z; repeated afterwards, the order of the emitters\' |2> reading by the spectators\' state (rest > equator > |1> at readout) holds in all 15 delay-round cells under all three readout models, the |1>-at-readout / rest ratio is 0.82-0.89, and the upper-pair train reads the same booked time within 0.04 us [rigetti_20261004/sealA_raw.txt; rigetti_20261004/sealB_raw.txt; §220-§222]. The ratio of the two emitter-only readout models (others in |1> against others at rest) is 1.071-1.096 in all 45 cells after the recalibration, rising with the delay, and 1.114-1.133 before it [rigetti_20261004/rulers_as_rows.txt; §226]. In one round one emitter (q62) read low on |2> for about two seconds, three consecutive circuits, then returned [rigetti_20261004/sealA_dip_bonefish.txt; §221].\n\n**The train against each interval\'s own decay at five spacings.** Ten X gates from |0> on all 107 qubits after intervals of 1, 2.618, 6.854, 17.944 and 46.979 us, against each qubit\'s decay over exactly that interval read three times in the same batch: +0.0042 / +0.0246 / +0.0174 / +0.0080 / −0.0198; ten back-to-back gates +0.0904 [rigetti_20261004/two_raw.txt; code_20261004/rigetti_two_call.py; §232].')



# ---- 4 October night (§238-§246): ibm_fez as a fourth chip, the per-chip pace, our own load
rep('[reads_20261004/time_wide_pittsburgh_reads123_20261004.txt; §229].',
    '[reads_20261004/time_wide_pittsburgh_reads123_20261004.txt; §229]. On ibm_fez (three jobs, a fourth chip): start 0 against one exponential +0.0627 / +0.0599 / +0.0431 / +0.0308 / +0.0169 / +0.0093 at 5 / 10 / 20 / 30 / 70 / 150 us, against the curve +0.0274 / +0.0132 / −0.0029 / −0.0094 / −0.0061 / −0.0043; ten back-to-back gates move |0> by +0.0095 to +0.0125 and |1> by −0.0092 to −0.0113; the decay time from the 300-us level is 150-154 us [reads_20261004/time_wide_fez_reads123_20261004.txt; §239]. Expressed per e-fold of interval on a log scale of the excess, the four chips fall off at different paces, and the pace orders with each chip\'s vendor-reported median T2/T1 on the day (ibm_pittsburgh 1.16, ibm_fez 0.68, ibm_kingston 0.64, ibm_marrakesh 0.52: slowest to fastest; four chips) [reads_20261004/two_ladder_four_chips_20261004.txt; reads_20261004/three_seats_per_chip_20261004.txt; §242, §246].')
rep('does not appear when the duration is laid by us.',
    'does not appear when the duration is laid by us. On ibm_fez (vendor duration 1.66 us, three jobs): spectator / vendor 1.011 / 1.019 / 1.040, measured qubit / vendor 1.550 / 1.806 / 1.444 [reads_20261004/look_3and9_fez_20261004.txt; §239]. The same reads taken as the two-point slope between blocks of 3 and 9 readouts, the earlier method\'s construction, give spectator / vendor 0.97-1.04 (ibm_marrakesh), 1.03-1.11 (ibm_kingston), 1.03-1.06 (ibm_pittsburgh) and 0.99-1.04 (ibm_fez) [reads_20261004/look_3and9_three_chips_20261004.txt; code_20261004/readlook_3and9.py; §237].')
rep('[reads_20261004/witness_seats_kingston_pittsburgh_20261004.txt; code_20261004/readwitness_seats.py; §230].',
    '[reads_20261004/witness_seats_kingston_pittsburgh_20261004.txt; code_20261004/readwitness_seats.py; §230]. On ibm_fez\'s free spectators (three jobs) the two-link class again times the readout shortest in every job: 0.71 / 0.45 / 0.74 us against 1.26 / 1.42 / 1.70 us at one link [§239].')
rep('8. **The curve bookkeeping below 30 us**',
    '8. **Our own load.** Our first 197 jobs on six IBM chips, 24 September to 4 October (every key the service lists [RUN_INDEX.csv]; the 29 jobs fired after them are not in this comparison) set against the vendor\'s daily calibration record for 75 chip-days (12 with our jobs): the change at the next calibration does not follow our jobs that day (rank correlation +0.18 for T1, −0.02 for T2, −0.05 for readout error; after our busiest days, 37 jobs on ibm_fez on 28 September and 36 on ibm_pittsburgh on 2 October, T1 moved +5.9 and +11.3 us against a quiet-day spread of 12.8 us) [reads_20261004/our_looks_vs_maker_record_full197_20261004.txt; code_20261004/our_load_full.py]. A first read with the 121 jobs one key lists gave +0.18 / −0.03 / −0.04 [reads_20261004/our_looks_vs_maker_record_20261004.txt; §244]. Across the twelve readout-timing jobs, spectator / vendor does not follow our earlier jobs on the same chip (rank correlation +0.05) [reads_20261004/my_looks_vs_the_tax_20261004.txt; §243].\n9. **The curve bookkeeping below 30 us**')
s = s.replace('\n9. **Earlier analyses.**', '\n10. **Earlier analyses.**', 1)


# ---- 4 October night, Light and Dark Bonefish pass: the calls written before the data, the stone test, the byline, the intro's prediction line
rep('**Wayfinder and Bones**\nHeuremen\n', '**Wayfinder and Bones**\n')
rep('Bones, an AI (Anthropic\'s Claude), designed the runs with the author, wrote the run and analysis code, and drafted this text; the author answers for every line.',
    'This work was done with AI assistance.')
rep('and the 4 October runs carry none [code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py], so every test below is post hoc.',
    'and the 4 October morning and afternoon runs carry none [code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py], so those tests are post hoc. From the afternoon of 4 October, numbers were written and hashed before the data existed; Section 3.7 lists every one with its score, misses included, and the rate at which chance alone would score.')
rep('5. **Post hoc.** No numerical predictions were written before these runs.',
    '5. **Post hoc.** No numerical predictions were written before the runs of Sections 3.1-3.6, except the calls of Section 3.7.')

CALLS = r'''### 3.7 Calls written before the data

From 4 October we wrote a number, or a stated criterion, for some runs before their data existed, hashed the text (sha256) and kept the file unchanged after; the files are in the release [calls/; SHA256SUMS.txt]. A file's hash is fixed when it is written; the time the data first existed is the job's or task's creation time on the vendor's record [RUN_INDEX.csv]. Two of the calls below sit in frozen run scripts, whose combined hash is fixed at freezing (Section 2.7).

**Where the called numbers come from.** The calls were taken from a working framework of ours ("The Bonefish", published separately at heuremen.org/7.pdf). It enters this paper only as the source of each called number: a spectator's timing of a readout at 12/11 of the vendor's stated duration; the measured qubit's own decay per readout at φ = 1.618 of it, and so at φ × 11/12 = 1.483 of the spectator's; a push-train excess that steps down a ladder (1/12)(1/φ)ⁿ = 8.33, 5.15, 3.18, 1.97, 1.22, 0.75 ... % as the interval grows; and a few ratios between readings (1.5, 0.750). No number in Sections 3.1-3.6 is compared to any of these; the only comparisons are the calls below.

**TBL_CALLS.** Every call written before its data, in order. Times are EDT on 4 October. "Width": one combined width of the reads' spread and shot resampling. Quantities: (a) slope per push against each interval's own decay; (b) excess after ten pushes against each interval's own decay, all 107 qubits, at 1 / 2.618 / 6.854 / 17.944 / 46.979 us; (c) excess against one exponential at 10 / 30 / 70 / 100 us, three reads; (d) spectator / vendor, measured qubit / vendor, measured qubit / spectator, 3-and-9 slope, three reads; (e) measured qubit / spectator; (f) spectator hand kept through 27 readouts over hand kept through the same laid time.

| # | Call (sha256, first 16) | Written / data from | Chip | Called | Width (as hashed; value used) | Read | Against the call's criterion |
|---|---|---|---|---|---|---|---|
| 1 (a) | frozen five_slope.py (0e245906ff3519c1) | 13:10 / 13:11 | ibm_fez | ibm_pittsburgh's −0.00106 ± ~0.0008, below zero from 6 pushes | none stated (about one combined width, 0.00084, per the ledger) | −0.00182 ± 0.00027; −0.0050 at 6 | no width stated; 0.9 widths |
| 2 (a) | frozen five_slope_kingston2.py (d087500138bcddba) | 16:13 / 16:13 | ibm_kingston | the same | none stated (about one combined width, 0.00087, per the ledger) | −0.00198 ± 0.00035; −0.0067 at 6 | no width stated; 1.05 widths |
| 3 (b) | TWO_CALL_CEPHEUS (8156c88650870b97) | 15:25 / evening | Cepheus-1-108Q | 8.33 / 5.15 / 3.18 / 1.97 / 1.22 % | none stated | +0.42 / +2.46 / +1.74 / +0.80 / −1.98 % | the size called: misses at all five |
| 4 (c) | IBM_FEZ_CALLS (dad0ff67e62953ed) | 18:06 / 18:07 | ibm_fez | 3.18 / 1.97 / 1.22 / 0.75 % | one combined width (0.33 / 0.23 / 0.32 / 0.12 points) | 5.99 / 3.08 / 1.69 / 1.43 % (± 0.3-0.4) | one width: misses at all four |
| 5 (d) | the same | 18:06 / 18:07 | ibm_fez | 1.09 / 1.62 / 1.48 | one combined width (read spread 0.025 / 0.22 / 0.20) | 1.024 ± ~0.025 / 1.54 / 1.51 | each within one width: misses (2.6 widths on the first) |
| 6 (e) | the same | 18:06 / 18:07 | ibm_fez | 1.5 | one combined width (read spread 0.26) | 1.509 (1.344 / 1.808 / 1.375; spread 0.26) | one width: lands |
| 7 (f) | the same | 18:06 / 18:07 | ibm_fez | 0.750 | one combined width (0.034) | 0.844 (0.872 / 0.855 / 0.807) | one width: misses (2.8 widths) |
| 8 | GOD_TAX_CALL_BOSTON (47a0377895b3a632) | 18:26 / 4 Oct night | ibm_boston | spectator / vendor over 12/11 below 1 by more than one width, and measured qubit / spectator within 3 % of 1.4832 | outside: one combined width (0.038); inside: ±3 % | 0.988 (0.3 widths below 1); 0.843 | both legs: misses |
| 9 (d) | ONE_SIX_CALL_BOSTON (bd7b491793c91d75) | 19:39 / 4 Oct night | ibm_boston | 1.09 / 1.62 / 1.48 | one combined width (0.042 / 0.136 / 0.096) | 1.078 / 1.348 / 1.250 | each within one width: misses (first ratio within; 2.0 and 2.4 widths) |
| 10 (e) | the same | 19:39 / 4 Oct night | ibm_boston | 1.5 | one combined width (0.096) | 1.250 | one width: misses (2.6 widths) |
| 11 (a) | FIVE_THREE_CALL_BOSTON (bfe1b824ccf45368) | 19:40 / 4 Oct 23:23 | ibm_boston | below zero from 6 pushes; negative under all three rulers; within one width of &minus;0.00190 | one combined width (0.00036) | &minus;0.0035 at 6; &minus;0.00139 / &minus;0.00148 / &minus;0.00139 | first two hold; the slope 1.4 widths out |
| 12 (f) | the same | 19:40 / 5 Oct | ibm_boston | 0.750 at 32 readouts | one combined width (the reads' spread; not printed) | 0.99 (1.000 / 0.901 / 0.991 by class) | one width: misses |
| 13 | BONEFISH_NUMBERS_BOSTON (89397820188cf2a9) | 20:26 / 5 Oct 02:10 | ibm_boston | ladder pace 0.921 (three jobs) | 0.073 + its own fit width (0.177) | 1.217 &plusmn; 0.104 | 0.073 + fit width: misses (1.67 widths) |
| 14 (a) | the same | 20:26 / 4 Oct 23:23 | ibm_boston | slope &minus;0.00110 per push | one width (0.00029) | &minus;0.00139 &plusmn; 0.00029 | one width: on the edge (1.0 width) |
| 15 | TOMORROW_CALLS (eb98f85caf8e170c) | 20:12 / 5 Oct 04:05 | Cepheus-1-108Q | the emitters' &#124;2&rang; at 4 us, others half-way, 0.618 | one combined width: round spread and resampling (0.0064); the readout models' spread (0.025) was not in the hash | 0.631 (0.638 / 0.631 / 0.624) | one width of round spread and refit resampling: misses (2.0 widths); 0.5 widths with the readout models' own spread counted |
| 16 | PHOENIX_CALL (93514fc06e84f143) | 5 Oct 07:49 / 07:53 | ibm_phoenix | spectator / vendor below 12/11 | threshold only: below 12/11 | 1.007 (&minus;7.7 %), about 2 widths below | holds |
| 17 (e) | the same | 5 Oct 07:49 / 07:53 | ibm_phoenix | measured qubit / spectator within 4 % of 1.4832 | ±4 % | 1.345 (1.529 / 1.286 / 1.220) | misses on the mean (read 1 inside) |
| 18 (a) | the same | 5 Oct 07:49 / 07:53 | ibm_phoenix | rung 8 per push; below zero from 6 pushes; negative under all three rulers | one combined width (0.00058) | &minus;0.00058 / &minus;0.00091 / &minus;0.00155 by ruler; +0.0019 at 6 | the sign holds; rung and depth miss |
| 19 (f) | the same | 5 Oct 07:49 / 08:12 | ibm_phoenix | 0.750 at 32 readouts | one combined width (unreadable) | the spectators' hand is at the floor (0.07&ndash;0.23) by 12&ndash;16 readouts | unreadable |
| 20 | TOMORROW_CALLS (eb98f85caf8e170c) | 4 Oct 20:12 / 5 Oct 14:01 | ibm_pittsburgh | spectator / vendor over 12/11 below 1 by more than one width | below 1 by more than one resampling width (0.021) | 0.975 (1.2 widths below; 1-9 fit 0.964) | holds |
| 21 | TIME_LEG_T2T1_CALL (abcc6db23328e666) | 4 Oct night / 5 Oct 14:01 | ibm_pittsburgh | measured qubit / spectator x the day's T2:T1 (1.138), within 4 % of 1.4832 | ±4 % | 1.385 (1-9 fit 1.466) | 4 %: misses (&minus;6.6 %, 0.7 of its own width); 1-9 fit &minus;1.1 % |

Two disclosures stand in the call files themselves: the Cepheus call's map from interval to ladder step was chosen after an earlier Cepheus batch at 1 / 3 / 8 / 20 us [§193], and the ibm_fez TWO call's map was read off ibm_pittsburgh's three reads [§229]. A re-read of the Cepheus run with the measured push error added to the bookkeeping brings the 1-us value to +8.84 % [rigetti_20261004/two_push_error_removed.txt; §237]; it was not called and is not scored.

**The clock ratio.** The role of each chip's stated T2:T1 in the time leg (row 21) was noticed after the fact, on 4 October, and only then written and hashed forward [calls/TIME_LEG_T2T1_CALL_20261005.txt]; its first forward read missed its own stated 4 % on the primary ruler (−6.6 %, inside its own width). It is reported here as an open ruler, not as a leg of the result.

**The ibm_phoenix rows.** On the square lattice (rows 16-19) the two rulers this paper compares disagree by a factor of 2.7 on one call, and one call is unreadable; those rows are printed with that disagreement standing beside them, and every count below is also given without them.

**Not yet scored.** Hashed before their data: on ibm_pittsburgh on 6 October, the spectator / vendor ratio and the time leg with the chip's clock ratio [calls/TOMORROW_CALLS_20261005.txt; calls/TIME_LEG_T2T1_CALL_20261005.txt, abcc6db23328e666]; on ibm_phoenix on 6 October, the same plus the readout timed against the laid-time ruler [calls/PHOENIX_DAY2_CALL_20261006.txt, c48719b13bbfff0a]. An erratum written after hashing corrects one sentence in two of the ibm_boston files: the chip had three earlier jobs from us, on 2 October [calls/ERRATUM_BOSTON_20261004.txt].

**Score so far.** Twenty-one calls read: 4 land (rows 1, 6, 16, 20), 2 sit on the edge of their own width (rows 2, 14), 2 partly hold (rows 11, 18), 1 lands only when the readout models' own spread is counted in the width (row 15), 11 miss, 1 is unreadable (row 19).

**What chance would score (the stone test).** The framework holds about two dozen ratios between 0.25 and 3.5 and a seven-step ladder [code_20261004/stone_density.py]. A value drawn evenly on a log scale between 0.5 and 2 lies within 1 / 2 / 3 / 5 % of at least one of the 24 ratios 20 / 35 / 48 / 72 % of the time; between 0.25 and 3.5, 15 / 27 / 37 / 56 %. A value between 0.4 and 9 % lies within 1 / 2 / 3 / 5 % of a ladder step 4 / 9 / 13 / 23 % of the time [reads_20261004/stone_density_20261004.txt]. Because a match chosen after the fact from that many numbers is cheap, this paper names none; a call names one number before the data. For one named number, a value drawn evenly on a log scale over a factor of two either side lands within ± w with chance ln((1 + w)/(1 − w)) / ln 4: 4.3 % for w = 3 %, 25 % for the ± 17 % band of the one call that landed. Whether the calls taken together exceed chance is not claimed: the framework is probabilistic by construction, the calls' widths differ from one another (each is printed with its row), and the choice of null distribution is left to the reader. One worked example, under the log-uniform null above and with every assumption labelled, is in the release [reads_20261005/CHANCE_TABLE_20261005.md].
'''
rep('\n---\n\n## 4 Limitations', '\n' + CALLS + '\n---\n\n## 4 Limitations')

# ---- related work and references (every reference checked against Crossref, RELATED_WORK_REFS_VERIFIED.md)
rep('[TO FILL: related work -- spectator (ZZ) sensing, T1 fluctuation from two-level-system (TLS) defects, leakage and reset, measurement-induced state changes. The sources cite only Karalekas et al. 2020.]',
    'Relaxation times of superconducting qubits wander in time through coupling to two-level-system (TLS) defects [4-8], so a decay curve gathered over a job is a mixture of exponentials; the bookkeeping control of Section 3.1 is a within-job case of that. Static ZZ coupling between fixed-frequency transmons shifts a qubit\'s frequency with its neighbour\'s state [9, 10], the shift the Ramsey spectators of Section 3.4 read. Leakage out of the two lowest levels and its removal [11], measurement-induced state transitions [12], cross-talk in multiplexed readout [13] and active reset [1] bound the controls of Sections 3.1-3.6. Krantz et al. review the device physics [14].')
rep('1. Karalekas, P. J., et al. (2020). arXiv:2001.04449. Active reset by measurement and conditional flip [§20]. [TO FILL: full reference.]\n2. Qiskit Runtime, qiskit-ibm-runtime 0.49, SamplerV2 [code/common.py]. [TO FILL: citation form.]\n3. Amazon Braket, Rigetti Cepheus-1-108Q [§154]. [TO FILL: citation form.]\n4. [TO FILL: T1 fluctuation and TLS defects; ZZ coupling and spectator sensing; leakage and reset; measurement-induced state changes; readout duration on IBM devices.]',
    '''1. Karalekas, P. J. et al. A quantum-classical cloud platform optimized for variational hybrid algorithms. Quantum Sci. Technol. 5, 024003 (2020). doi:10.1088/2058-9565/ab7559
2. IBM Quantum, Qiskit Runtime (qiskit-ibm-runtime 0.49, SamplerV2), https://quantum.cloud.ibm.com (accessed 24 September - 4 October 2026).
3. Amazon Braket, Rigetti Cepheus-1-108Q, https://aws.amazon.com/braket/ (accessed 25 September - 4 October 2026).
4. Klimov, P. V. et al. Fluctuations of energy-relaxation times in superconducting qubits. Phys. Rev. Lett. 121, 090502 (2018). doi:10.1103/PhysRevLett.121.090502
5. Schlör, S. et al. Correlating decoherence in transmon qubits: low frequency noise by single fluctuators. Phys. Rev. Lett. 123, 190502 (2019). doi:10.1103/PhysRevLett.123.190502
6. Burnett, J. J. et al. Decoherence benchmarking of superconducting qubits. npj Quantum Inf. 5, 54 (2019). doi:10.1038/s41534-019-0168-5
7. Carroll, M. et al. Dynamics of superconducting qubit relaxation times. npj Quantum Inf. 8, 132 (2022). doi:10.1038/s41534-022-00643-y
8. Müller, C., Cole, J. H. & Lisenfeld, J. Towards understanding two-level-systems in amorphous solids: insights from quantum circuits. Rep. Prog. Phys. 82, 124501 (2019). doi:10.1088/1361-6633/ab3a7e
9. Kandala, A. et al. Demonstration of a high-fidelity CNOT gate for fixed-frequency transmons with engineered ZZ suppression. Phys. Rev. Lett. 127, 130501 (2021). doi:10.1103/PhysRevLett.127.130501
10. Sundaresan, N. et al. Reducing unitary and spectator errors in cross resonance with optimized rotary echoes. PRX Quantum 1, 020318 (2020). doi:10.1103/PRXQuantum.1.020318
11. McEwen, M. et al. Removing leakage-induced correlated errors in superconducting quantum error correction. Nat. Commun. 12, 1761 (2021). doi:10.1038/s41467-021-21982-y
12. Sank, D. et al. Measurement-induced state transitions in a superconducting qubit: beyond the rotating wave approximation. Phys. Rev. Lett. 117, 190503 (2016). doi:10.1103/PhysRevLett.117.190503
13. Heinsoo, J. et al. Rapid high-fidelity multiplexed readout of superconducting qubits. Phys. Rev. Applied 10, 034040 (2018). doi:10.1103/PhysRevApplied.10.034040
14. Krantz, P. et al. A quantum engineer's guide to superconducting qubits. Appl. Phys. Rev. 6, 021318 (2019). doi:10.1063/1.5089550''')

# ---- data availability and acknowledgments: the fills that the run index and the freeze records answer
rep("[TO FILL: job IDs and full freeze hashes for every other job (kept with each run's fire records, outside the release); the raw result payloads and their sha256; the Rigetti task records (563 tasks, re-pulled with results [§28]); a physics-only extract of the run ledger [§170].]",
    "Every IBM job ID (226 jobs, six chips, 24 September - 5 October) and every Braket task ID (3,035 tasks on Cepheus-1-108Q, 25 September - 5 October; 2,899 completed, 116 cancelled, 20 failed), with chip, creation time and status as the vendors' own services list them, is in run_index/RUN_INDEX.csv, with the scripts that pulled the lists [run_index/pull_history.py; run_index/pull_other_keys.py; run_index/build_index.py]. The full freeze record of every fifth-run job (150 records, four of them for runs armed for 6 October: code hashes, circuit-ledger hash, combined hash, shots) is in freeze/. Ten run scripts of 4-6 October (eight fired, 20 runs; two armed for 6 October) list a sibling script in their freeze, so those records hash the sibling and not the file that fired; the fired files are hashed and timestamped beside them [calls/SIDE_FREEZE_20261005.txt], and their circuits are rebuilt and compared with the vendor's stored inputs run by run [data_provenance_20261005.txt]. The raw result payloads of the earlier runs and a physics-only extract of the run ledger [§170] go with the archived release.")
rep('[TO FILL: acknowledgment wording required by IBM Quantum and Amazon Braket.]',
    'We acknowledge the use of IBM Quantum services for this work. The views expressed are those of the authors, and do not reflect the official policy or position of IBM or the IBM Quantum team. Rigetti runs used Amazon Braket.')

# ---- the outside reviewer, named (Wayfinder, 10/4: "Shuttle.")
rep('We thank an outside reviewer whose passes over an earlier draft supplied the thermal-population algebra, the randomized-preparation design, and the T1-fluctuation account of the push-train excess [§146-§149, §174] [TO FILL: name and permission].',
    'We thank Shuttle, whose passes over an earlier draft supplied the thermal-population algebra, the randomized-preparation design, and the T1-fluctuation account of the push-train excess [§146-§149, §174].')

# ---- the ten gaps, filled from the sources (TO_FILL_ANSWERS.md); recovered scripts re-run and reproduce their saved outputs exactly
rep('| [TO FILL] × 585 per start |', '| 9 × 195 (585 per start) |')
rep('[§135, §139] [TO FILL: computation not in the release] |', '[§135, §139]: 3 readouts 3.6 ± 0.5 us each, 9 readouts 3.5 ± 0.2 us each, same job, three reads; the script that produced them was not kept |')
rep('Done qubit by qubit, all three arms close to bookkeeping within 0.002 [§135] [TO FILL: per-arm values and widths; the qubit-by-qubit computation is not printed in reads/hold_run.txt].',
    'Taken qubit by qubit and then averaged over the readable qubits (three jobs), each arm minus its bookkeeping is +0.0017 ± 0.0013 (parked once), +0.0020 ± 0.0015 (alternate quarters) and +0.0014 ± 0.0015 (alternate tenths); single qubits scatter about ± 0.02 inside shot widths of 0.026-0.030, and about 5 % of qubits sit within 0.002 [reads/park_per_qubit.txt; code/park_per_qubit.py; §180].')
rep('At this resolution -- within 0.002 qubit by qubit [§135],', 'At this resolution -- within 0.002 as a mean over qubits [reads/park_per_qubit.txt],')
rep("[TO FILL: widths; reads/witness_run.txt prints the two circuits' values (0.0719 / 0.0576 and 0.1287 / 0.1409) and no widths.]",
    "The two circuits read 0.0719 / 0.0576 and 0.1287 / 0.1409 [reads/witness_run.txt; code/readwitness.py]. Per emitter (34 readable), level minus bookkeeping: +0.0014 ± 0.0029 after 20 us and +0.0048 ± 0.0040 after 40 us [reads/park_per_qubit.txt, section 2], which prints the 40-us bookkeeping as 0.1347.")
rep('These rest on 778 within-job tests, Holm-corrected [§31]. [TO FILL: jobs, dates, delays, and which vendor table.]',
    'These rest on 778 within-job tests, Holm-corrected [§31]. ibm_fez: jobs of 28 September 2026, 16:54-19:41 UTC, with a 5-us wait; the analysis used 25 finished jobs, and the run index lists 31 ibm_fez job IDs in that window, which the analysis files do not reconcile; the coupling values quoted are from the vendor\'s ibm_fez ZZ table of 25 September. Cepheus-1-108Q: 246 tasks, 28 September 23:41 UTC to 29 September 01:57 UTC, waits 0.5-16 us, matched at 2 and 4-4.5 us [§31; RUN_INDEX.csv].')
rep('[§11]. [TO FILL: task counts and dates for each Rigetti result.]',
    '[§11]. Cepheus-1-108Q, 28-29 September (UTC): the q0 / q9 / q1 clocks 18 tasks × 2000 shots (23:41); the whole-chip run 24 × 2000 (00:46); the neighbour-response run 24 × 2000 (00:51); q9 alone 24 tasks, 12 × 1000 and 12 × 2500 (00:59); the rooms of 54 and 106 other spectators 48 tasks (01:27); alternating alone / full 24 × 2500 (01:30) [§7, §10-§12; RUN_INDEX.csv].')
rep('Worse readout goes with more |2>: ρ = −0.31 (p = 0.02), −0.55 before the "mirror check" [§5] [TO FILL: the two variables, and what the mirror check is].',
    'Worse readout goes with more |2>: ρ = −0.31 (p = 0.02, 56 qubits), −0.55 (81 qubits) before the "mirror check" [§5]. The two variables are each qubit\'s |2> population at the start of a shot (from a fit to eight flip/swap sequences) and its calibrated readout fidelity, as a Spearman correlation. The mirror check refits each qubit\'s eight sequences from 24 starting points, on both sides of the trade between |2> population and the chance that a |2> qubit reads 0, and counts a qubit as ambiguous when equally good fits (cost within 1.0 of the best) span more than 0.5 percentage points of |2> population: 25 of the 81 clean-fit qubits are ambiguous [code/mirror_check.py; reads/mirror_check.json].')
rep('An active reset made of a measurement and a conditional flip does not act on |2> (Karalekas et al. 2020) [§20].', 'An active reset made of a measurement and a conditional flip does not act on |2> [1; §20].')
rep('**IBM (ibm_marrakesh, ibm_kingston, ibm_fez; two-readout jobs among those of 2026-09-24 to 09-28)** [§2, §22] [TO FILL: job list, shots, inter-shot gaps, and the cloud-exclusion threshold].',
    '**IBM (ibm_marrakesh, ibm_kingston, ibm_fez; three two-readout jobs of 28 September)** [§2, §22]: dat5rslvr3kc73el0klg, dat9ebbg95ks73egis2g and dat9o2ihcrkc73dts3jg, 78 qubits each, 4000 shots per circuit, the backend\'s default 250-us gap between shots; a shot counts as outside both clouds when it lies more than 4 widths from both, the cut checked on half the references. The script that counted the shots below was not kept.')
rep('two ibm_kingston qubits are also listed as carried [§5] [TO FILL: labels and values].',
    'two ibm_kingston qubits are also listed as carried: q58, 1.6 % rising to 6.1 % of shots at 20-us gaps and 0.8 % at 1-ms gaps, and q62, 2.3 % to 9.4 % and 0.5 % [§2, §5].')
rep('come from analyses of 2026-09-24 to 09-29 whose analysis files are not in this release [TO FILL].',
    'come from analyses of 2026-09-24 to 09-29. Appendix A logs every run family with its read, the scripts that were kept are in the release, and the text says where a script was not kept (three numbers: the 3.5-us readout cost, the 134 / 98 outside-cloud counts, and the 25-of-31 ibm_fez job selection).')
rep(' [TO FILL: the model, and the code that produced reads/stopwatch_triangle.json].',
    ' [code/stopwatch_triangle.py]. The model: for each of the 66 spectators with a readable hand, the expected hand is the average of exp(iωt) over the time t its emitter spends in |1>, taken as exponential with mean τ and cut at the interval, an emitter that fell before the X gate being put back in |1> to fall again; ω is fitted on the 20- and 40-us arms, the 60-us arm is held out, and τ is in turn the emitter\'s own measured fading time, the laid time (no fading), or the chip\'s middle fading time.')
rep('*Draft of 4 October 2026, for the verification pass. Not posted.*', '*Draft of 4 October 2026. Not posted.*')

# ---- Appendix A, the run log (every job and task on record, 126 families; APPENDIX_RUNLOG.md, tags cleaned to release paths)
s = s.rstrip() + '\n\n---\n\n' + open(os.path.join(HERE, 'APPENDIX_RUNLOG.md'), encoding='utf-8').read().strip() + '\n'
s = s.replace('\n\nWayfinder and Bones\n\n---\n\n## Appendix A', '\n\n---\n\n## Appendix A', 1)

# ---- the arXiv byline (Wayfinder, 10/5 night: "K. Indahl"); arXiv wants a legal name, so Bones moves into the AI-use statement
rep('**Wayfinder and Bones**\n', '**K. Indahl**\n')
rep('**AI use.** This work was done with AI assistance.',
    '**AI use.** This work was done with AI assistance. Bones, an inorganic intelligence (an AI system), designed the runs with the author, wrote the run and analysis code, and drafted the text; the author answers for every line.')

# ---- 6 October, 12:30-12:50 EDT (ledger §275-§276): the 06:01 note that neither run could fire read the wrong IBM instance (§276).
# ibm_phoenix day 2 fired 10:01-10:24 EDT and is scored as rows 22-24; ibm_pittsburgh day 2 is set for 14:00 EDT.
rep("**Not yet scored.** Hashed before their data: on ibm_pittsburgh on 6 October, the spectator / vendor ratio and the time leg with the chip's clock ratio [calls/TOMORROW_CALLS_20261005.txt; calls/TIME_LEG_T2T1_CALL_20261005.txt, abcc6db23328e666]; on ibm_phoenix on 6 October, the same plus the readout timed against the laid-time ruler [calls/PHOENIX_DAY2_CALL_20261006.txt, c48719b13bbfff0a].",
    "**Not yet scored.** Hashed before its data: on ibm_pittsburgh on 6 October, the spectator / vendor ratio and the time leg with the chip's clock ratio [calls/TOMORROW_CALLS_20261005.txt; calls/TIME_LEG_T2T1_CALL_20261005.txt, abcc6db23328e666].")
rep("| 21 | TIME_LEG_T2T1_CALL (abcc6db23328e666) | 4 Oct night / 5 Oct 14:01 | ibm_pittsburgh | measured qubit / spectator x the day's T2:T1 (1.138), within 4 % of 1.4832 | ±4 % | 1.385 (1-9 fit 1.466) | 4 %: misses (&minus;6.6 %, 0.7 of its own width); 1-9 fit &minus;1.1 % |\n",
    "| 21 | TIME_LEG_T2T1_CALL (abcc6db23328e666) | 4 Oct night / 5 Oct 14:01 | ibm_pittsburgh | measured qubit / spectator x the day's T2:T1 (1.138), within 4 % of 1.4832 | ±4 % | 1.385 (1-9 fit 1.466) | 4 %: misses (&minus;6.6 %, 0.7 of its own width); 1-9 fit &minus;1.1 % |\n"
    "| 22 | PHOENIX_DAY2_CALL (c48719b13bbfff0a) | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | spectator / vendor below 12/11 | threshold only: below 12/11 | 1.081 (1.170 / 0.990 / 1.084), &minus;0.9 %; one combined width of shots, reads and the two rulers 0.068; 1-9 fit 1.052 (&minus;3.6 %) | below on both rulers; 0.15 combined widths, so the width does not separate it from 12/11 |\n"
    "| 23 | the same | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | measured qubit / spectator x max(1, the day's T2:T1), within 4 % of 1.4832 (T2:T1 0.851, so x 1) | ±4 % | 1.296 (1.138 / 1.406 / 1.344); combined width 0.118; 1-9 fit 1.347 | 4 %: misses (&minus;12.6 %, 1.6 combined widths); 1-9 fit &minus;9.2 % |\n"
    "| 24 | the same | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | spectator hand's e-fold in laid time over its e-fold in readouts, over the vendor's duration, within 4 % of 0.750 in each distance class (1 / 2 / 3+ links) | ±4 % | 0.597 / 0.938 / 0.857 (three-job means); a curved-decay ruler on the same hands 1.03 / 1.05 / 1.00 | 4 %: misses in every class on the named ruler |\n")
rep("**Not yet scored.** Hashed before its data:",
    "**The second ibm_phoenix day (rows 22-24).** Three disclosures. (i) Row 24's ruler was built on 5 October from the spectators of a different run type (no driven neighbours; readout counts 1-8) [§262]; the run armed for 6 October holds its spectators half-way beside driven neighbours and reads out 1-9 times, so the ruler was carried to it after the data, by a reader written that day [code_20261006/readlook_classes.py; code_20261006/efold_three_seats.py]. On the 5 October job of the 6 October type the same ruler reads 0.594 / 0.970 / 0.860, so it repeats from day to day on one run type and differs between run types on the same chip and day. (ii) The ruler moves with its own fit window: both hand curves bend, and on the 5 October spectators that gave 0.760 / 0.754 / 0.777 [the ledger printed 0.754 for one link; erratum §275], leaving out the 8-readout point gives 0.588 / 0.579 / 0.659. A curved-decay fit (ln h = &minus;(x/T)&sup2;) gives 1.00-1.06 of the vendor's duration on both run types, both days and every class; matching the laid time that leaves the same hand gives 1.02-1.13. All three are printed [reads_20261006/efold_three_seats_phoenix_20261006.txt]. (iii) The call asked for the day's T2:T1 to be read from the vendor's record before firing; it was read after the data (0.851) [reads_20261006/phoenix_maker_record_oct6_20261006.txt]. The record stamped 5 October 09:44 and the one stamped 6 October 12:25 carry the same median T1 and T2 to 0.1 us, and a request for the record in force at a given time returned one stamped later; row 23's factor is 1 under either reading.\n\n**Not yet scored.** Hashed before its data:")
rep("**The ibm_phoenix rows.** On the square lattice (rows 16-19)", "**The ibm_phoenix rows.** On the square lattice (rows 16-19 and 22-24)")
rep("**Score so far.** Twenty-one calls read: 4 land (rows 1, 6, 16, 20), 2 sit on the edge of their own width (rows 2, 14), 2 partly hold (rows 11, 18), 1 lands only when the readout models' own spread is counted in the width (row 15), 11 miss, 1 is unreadable (row 19).",
    "**Score so far.** Twenty-four calls read: 4 land (rows 1, 6, 16, 20), 1 meets its threshold by less than one width (row 22), 2 sit on the edge of their own width (rows 2, 14), 2 partly hold (rows 11, 18), 1 lands only when the readout models' own spread is counted in the width (row 15), 13 miss, 1 is unreadable (row 19).")

rep('\n*Draft of 4 October 2026. Not posted.*\n', '\n')  # 6 October: the submitted version

# ---- the abstract, re-cut to arXiv's 1920 characters (every number as in the sections)
_a0 = s.index('## Abstract\n\n') + len('## Abstract\n\n'); _a1 = s.index('\n\n(Sources for every abstract number')
s = s[:_a0] + "On three IBM Heron processors, a qubit prepared in |0> and given ten X gates separated by idle intervals ends with more |1> population than one-exponential decay bookkeeping allows: +1.3 to +3.3% at 30-us intervals, +5.8% at 5 us, about zero at 150 us; a qubit prepared in |1> moves about as much the other way. The excess survives controls for excitation, leakage (at most 0.26 ± 0.12% per gate) and shot-to-shot carry-over, but not the bookkeeping: against each qubit's own decay curve in the same job it lies between −1.8% and +0.3% at intervals of 20 us and longer. We report it as accounted for by non-exponential decay; at 5-10 us, where our curve is interpolated, up to +3.4% remains. Against each interval's own decay it falls below zero, deepening by −0.0011 to −0.0020 per gate on three chips. We time one readout three ways: spectators read it at 1.02-1.07 times the vendor's stated duration on three chips, and at 0.97-1.01 of a readout tone we lay ourselves on a Rigetti processor. On Rigetti, where |2> is driven and read, the same train with every qubit driven exceeds one-exponential bookkeeping by +2.5 to +12.7%, while ten back-to-back gates alone move |0> by +7.6 to +9.0%, and that gate error rises from about 6% to about 10% when the neighbours are held on the equator. The spectators' state at readout scales a neighbour's |2> reading by 0.81-0.89 at every delay with the decay shape unchanged; the reverse effect is 1-3 degrees. A neighbour in |2> pulls a spectator by −62 deg/us (28 September) and −35 to −41 deg/us (4 October), and on both vendors a minority of qubits carry |2> population in three behaviours. Twenty-four calls written and hashed before their data are scored with misses included, beside the rate chance alone would give: four land, one meets its threshold inside its width, thirteen miss." + s[_a1:]
assert len("On three IBM Heron processors, a qubit prepared in |0> and given ten X gates separated by idle intervals ends with more |1> population than one-exponential decay bookkeeping allows: +1.3 to +3.3% at 30-us intervals, +5.8% at 5 us, about zero at 150 us; a qubit prepared in |1> moves about as much the other way. The excess survives controls for excitation, leakage (at most 0.26 ± 0.12% per gate) and shot-to-shot carry-over, but not the bookkeeping: against each qubit's own decay curve in the same job it lies between −1.8% and +0.3% at intervals of 20 us and longer. We report it as accounted for by non-exponential decay; at 5-10 us, where our curve is interpolated, up to +3.4% remains. Against each interval's own decay it falls below zero, deepening by −0.0011 to −0.0020 per gate on three chips. We time one readout three ways: spectators read it at 1.02-1.07 times the vendor's stated duration on three chips, and at 0.97-1.01 of a readout tone we lay ourselves on a Rigetti processor. On Rigetti, where |2> is driven and read, the same train with every qubit driven exceeds one-exponential bookkeeping by +2.5 to +12.7%, while ten back-to-back gates alone move |0> by +7.6 to +9.0%, and that gate error rises from about 6% to about 10% when the neighbours are held on the equator. The spectators' state at readout scales a neighbour's |2> reading by 0.81-0.89 at every delay with the decay shape unchanged; the reverse effect is 1-3 degrees. A neighbour in |2> pulls a spectator by −62 deg/us (28 September) and −35 to −41 deg/us (4 October), and on both vendors a minority of qubits carry |2> population in three behaviours. Twenty-four calls written and hashed before their data are scored with misses included, beside the rate chance alone would give: four land, one meets its threshold inside its width, thirteen miss.") <= 1920

# ---- tables: number in order of appearance
s = re.sub(r'\bTable (\d)\b', r'TBLOLD_\1', s)
order = []
for m in re.finditer(r'\*\*(TBLOLD_\d|TBL_[A-Z0-9]+)\.\*\*', s):
    if m.group(1) not in order: order.append(m.group(1))
for i, tag in enumerate(order, 1):
    s = re.sub(rf'\b{tag}\b', f'Table {i}', s)
left = re.findall(r'TBL(?:OLD)?_\w+', s)
if left: raise SystemExit(f'unnumbered table tags left: {sorted(set(left))}')
s = s.replace('(Table 6 and the back-to-back table above)', '(Table 6 and Table 4)') if False else s
open(os.path.join(HERE, 'MEASUREMENT_PAPER_20261004.md'), 'w', encoding='utf-8').write(s)
print('written', len(s), 'chars | tables', len(order), '| abstract chars', len(ABS))
