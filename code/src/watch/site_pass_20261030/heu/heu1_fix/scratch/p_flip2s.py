D_OLD = "Does the coherence that readouts cost untouched qubits come from a neighbour hidden in a level that reads as 0? Every measured qubit gets an X after."
D_NEW = "Does the coherence that readouts cost untouched qubits come from a neighbour hidden in a level that reads as 0? This second X-flip check builds its floor like for like and reads each processor separately."
PAIRS = [
(f'<meta name="description" content="{D_OLD}">', f'<meta name="description" content="{D_NEW}">'),
(f'<meta property="og:description" content="{D_OLD}">', f'<meta property="og:description" content="{D_NEW}">'),
("""<h2>Results, read by the committed analysis (<a href="results_flip.text">full output</a>)</h2>""",
 """<h2>Results, read by the committed analysis (<a href="results_flip.text">full output</a>)</h2>
<p>On this page, every interval named is a 95&thinsp;% interval from a 2000-draw bootstrap over qubits (analyze_flip.py).</p>"""),
("""<a href="fire_flip.text">fire log</a>; job records flipjob_ibm_*.json and IBM calibration at firing in this folder).""",
 """<a href="fire_flip.text">fire log</a>, and job records flipjob_ibm_*.json and IBM calibration at firing in this folder)."""),
("""F2 is consistent with zero at both N; F2c is consistent with zero""",
 """F2 is consistent with zero at both N, and F2c is consistent with zero"""),
("""96.52&thinsp;%; idle at N = 0, 4, 8:""",
 """96.52&thinsp;%, idle at N = 0, 4, 8:"""),
("""<b>neither branch of the rule</b> applies; reported as is.""",
 """<b>neither branch of the rule</b> applies, and the reading is reported as is."""),
("""<b>CANNOT_TELL</b> on kingston; the readings the analysis printed""",
 """<b>CANNOT_TELL</b> on kingston. The readings the analysis printed"""),
("""is excluded as the cause; fez and kingston cannot tell.""",
 """is excluded as the cause, and fez and kingston cannot tell."""),
("""submitted on 22 October at 09:58 (EDT); the marrakesh and fez jobs""",
 """submitted on 22 October at 09:58 (EDT), and the marrakesh and fez jobs"""),
("""so only kingston ran; the other two were fired afterwards.""",
 """so only kingston ran. The other two were fired afterwards."""),
]
