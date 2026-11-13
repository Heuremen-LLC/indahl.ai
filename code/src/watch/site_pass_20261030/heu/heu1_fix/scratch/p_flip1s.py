D_OLD = "Claim 6 (readouts cost untouched qubits coherence) survived keeping only shots in which every measured neighbour sat in its 0 cluster. Left open: a."
D_NEW = "The claim that readouts cost untouched qubits coherence survived keeping only shots in which every measured neighbour sat in its 0 cluster. This first X-flip check asks whether a neighbour hidden in a level that reads as 0 could explain it."
PAIRS = [
(f'<meta name="description" content="{D_OLD}">', f'<meta name="description" content="{D_NEW}">'),
(f'<meta property="og:description" content="{D_OLD}">', f'<meta property="og:description" content="{D_NEW}">'),
("""<p>Claim 6 (readouts cost untouched qubits coherence) survived keeping only shots""",
 """<p>The claim that readouts cost untouched qubits coherence survived keeping only shots"""),
("""Plan, circuits and analysis pushed before any job; results are read below by the committed analysis.</p>""",
 """Plan, circuits and analysis were pushed before any job, and results are read below by the committed analysis.</p>"""),
("""<h2>Results of run 1: the known-good check failed on all three processors</h2>""",
 """<h2>Results of run 1: the known-good check failed on fez, kingston and marrakesh</h2>
<p>On this page, brackets are 95&thinsp;% intervals from a 2000-draw bootstrap over qubits (analyze_flip.py).</p>"""),
("""<a href="fire_flip.text">fire log</a>; job records flipjob_ibm_*.json in this folder).""",
 """<a href="fire_flip.text">fire log</a>, and job records flipjob_ibm_*.json in this folder)."""),
("""should sit at the calibration floor; it sat above it""",
 """should sit at the calibration floor. It sat above it"""),
("""(every interval above zero; full output).""",
 """(every interval above zero, full output)."""),
("""and is not used); under the plan&rsquo;s own rule a failed known-good""",
 """and is not used). Under the plan&rsquo;s own rule a failed known-good"""),
("""(unheralded in both arms); its plan, code and synthetic tests were committed""",
 """(unheralded in both arms). Its plan, code and synthetic tests were committed"""),
]
