D_OLD = "Does the phase kick on untouched qubits come once per readout, or does it grow with the length of the readout pulse? Each processor has two readout."
D_NEW = "Does the phase kick on untouched qubits come once per readout, or does it grow with the length of the readout pulse? This run compares two readout instructions of different length on the same processor."
PAIRS = [
(f'<meta name="description" content="{D_OLD}">', f'<meta name="description" content="{D_NEW}">'),
(f'<meta property="og:description" content="{D_OLD}">', f'<meta property="og:description" content="{D_NEW}">'),
("""(dbd4pu0c77vs7387cihg); IBM&rsquo;s calibration at firing saved beside each.""",
 """(dbd4pu0c77vs7387cihg), with IBM&rsquo;s calibration at firing saved beside each.</p>
<p>On this page, brackets are 95&thinsp;% intervals from a 2000-draw bootstrap over qubits, and copy gaps are the same interval on copy 0 minus copy 1 (analyze_len.py)."""),
("""so they differ in more than length; and a kick that does not depend on the instruction could come""",
 """so they differ in more than length. A kick that does not depend on the instruction could also come"""),
("""The run narrows the mechanism; it does not name it.""",
 """The run narrows the mechanism, and it does not name it."""),
("""matches the control run (known-good met); each copy alone gives a close ratio (0.600 and 0.586 against 0.576 at 4 readouts; 0.450 and 0.465 against 0.508 at 8); the compiled schedule has no padding.""",
 """matches the control run (known-good met). Each copy alone gives a close ratio (0.600 and 0.586 against 0.576 at 4 readouts, and 0.450 and 0.465 against 0.508 at 8). The compiled schedule has no padding."""),
("""more than equal idles at 8 readouts; that is within what IBM&rsquo;s stated""",
 """more than equal idles at 8 readouts, which is within what IBM&rsquo;s stated"""),
("""+0.038 [0.020, 0.047]; it is above 0 at 4 readouts too.""",
 """+0.038 [0.020, 0.047]. It is above 0 at 4 readouts too."""),
]
