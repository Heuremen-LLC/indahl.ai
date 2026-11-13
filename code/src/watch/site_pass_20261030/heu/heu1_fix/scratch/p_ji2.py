D_OLD = "Every IBM job on our credentials in this period (546: 539 done, 5 errored, 1 cancelled, 1 queued; re-pulled 23 October by pull_job_index.py from every."
D_NEW = "Every IBM job and Rigetti task on our credentials from 24 September to 22 October 2026, as pulled from the providers, with the scripts that count them."
PAIRS = [
(f'<meta name="description" content="{D_OLD}">', f'<meta name="description" content="{D_NEW}">'),
(f'<meta property="og:description" content="{D_OLD}">', f'<meta property="og:description" content="{D_NEW}">'),
("""<p>Every IBM job on our credentials in this period (546: 539 done, 5 errored, 1 cancelled, 1 queued; re-pulled 23 October by <a href="pull_job_index.py">pull_job_index.py</a> from every key and instance, after the 22 October pull at 16:28 EDT held 520 and missed 26 jobs created that evening) and every Rigetti task (3035: 2899 completed, 116 cancelled, 20 failed), as pulled from the providers. The counts""",
 """<p>Every IBM job on our credentials in this period and every Rigetti task, as pulled from the providers.</p>
<p>The IBM file holds every job (546: 539 done, 5 errored, 1 cancelled, 1 queued), re-pulled 23 October by <a href="pull_job_index.py">pull_job_index.py</a> from every key and instance, after the 22 October pull at 16:28 EDT held 520 and missed 26 jobs created that evening. The Rigetti file holds every task (3035: 2899 completed, 116 cancelled, 20 failed). The counts"""),
("""(no equal-idle arm on untouched qubits; not used for the readout claims)""",
 """(no equal-idle arm on untouched qubits, so not used for the readout claims)"""),
("""(one readout per qubit; not used)""", """(one readout per qubit, not used)"""),
("""125 on 7, by US Eastern creation day; three errored)""", """125 on 7, by US Eastern creation day, and three errored)"""),
("""(the 16 to 17 UTC runs; 116 cancelled; 3035 in all, 25 September to 5 October; the 1310 of 5 October are not used)""",
 """(the 16 to 17 UTC runs, with 116 cancelled, out of 3035 in all, 25 September to 5 October, while the 1310 of 5 October are not used)"""),
]
