PAIRS = [
("""<meta name="description" content="IBM’s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001 (the record notes). The October records.">""",
 """<meta name="description" content="IBM’s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001, with the scripts that read them.">"""),
("""<meta property="og:description" content="IBM’s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001 (the record notes). The October records.">""",
 """<meta property="og:description" content="IBM’s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001, with the scripts that read them.">"""),
("""<p>IBM&rsquo;s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001 (the record notes). The October records the other rows use are saved beside each run, in that run&rsquo;s folder.</p>""",
 """<p>IBM&rsquo;s own calibration records as we pulled them, behind the record notes of the Quantum Idle Audit QIA-2026-001 (<a href="https://indahl.ai/quantum-idle-audit.pdf">the audit, PDF</a>). The notes are numbered as in that PDF. The October records the other notes use are saved beside each run, in that run&rsquo;s folder.</p>"""),
("""<li>Rows 3 and 4 (T1 and T2 dates, kingston and marrakesh, records stamped 26 to 28 September):""",
 """<li>Record notes 4 and 5 (T1 and T2 dates, kingston and marrakesh, records stamped 26 to 28 September):"""),
("""<li>Row 5 (T1 and T2 under a new record stamp):""",
 """<li>Record note 6 (T1 and T2 under a new record stamp):"""),
("""compares every qubit: all 2,655 T1 and T2 entries (9 record pairs, including a third phoenix record of 6 October) keep the same value and the same measurement date under the new stamp (<a href="restamp_check/compare_restamp.py">script</a>, <a href="restamp_check/results_restamp.text">output</a>).</li>""",
 """compares every qubit: all 2,655 T1 and T2 entries of 16 September to 6 October (9 record pairs, including a third phoenix record of 6 October) keep the same value and the same measurement date under the new stamp (<a href="restamp_check/compare_restamp.py">script</a>, <a href="restamp_check/results_restamp.text">output</a>). Five more record pairs of 22 and 23 October, on fez, kingston and marrakesh, hold 1,549 entries, all identical in value and date (<a href="restamp_check/compare_oct23.py">script</a>, <a href="restamp_check/results_restamp_oct23.text">output</a>). In all, 4,204 of 4,204 entries are identical across 14 record pairs, 16 September to 23 October, the figure the audit prints.</li>"""),
("""<li>Row 6 (zz on five live edges):""", """<li>Record note 7 (zz on five live edges):"""),
("""<li>Record notes 2 to 4, 7 and 8: <a href="record_notes.py">record_notes.py</a> (<a href="results_record_notes.text">output</a>).</li>""",
 """<li>Record notes 3 to 5, 8 and 9: <a href="record_notes.py">record_notes.py</a> (<a href="results_record_notes.text">output</a>). The script&rsquo;s own header still numbers them 2 to 4, 6 and 7, from an earlier version of the audit.</li>
<li>A same-hour read of every qubit&rsquo;s readout error against IBM&rsquo;s stated readout fields, 22 October: <a href="/experiments/2026-10-22-readout-audit/">readout audit</a>.</li>"""),
]
