FONT = """<style>
@font-face{font-family:'Abril Fatface';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/abril-fatface-normal-804040b2.woff2) format('woff2')}
@font-face{font-family:'Cinzel';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/cinzel-normal-ef95296c.woff2) format('woff2')}
@font-face{font-family:'Cinzel';font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/cinzel-normal-ef95296c.woff2) format('woff2')}
@font-face{font-family:'Lora';font-style:italic;font-weight:400;font-display:swap;src:url(/fonts/lora-italic-e93da94d.woff2) format('woff2')}
@font-face{font-family:'Lora';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/lora-normal-6b102ab3.woff2) format('woff2')}
@font-face{font-family:'Lora';font-style:normal;font-weight:500;font-display:swap;src:url(/fonts/lora-normal-6b102ab3.woff2) format('woff2')}
@font-face{font-family:'Lora';font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/lora-normal-6b102ab3.woff2) format('woff2')}
</style>"""
PAIRS = [
("""<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Abril+Fatface&family=Cinzel:wght@400;600&display=swap" rel="stylesheet">""", FONT),
("""All three are what standard quantum mechanics predicts; the point of this page""",
 """All three are what standard quantum mechanics predicts. The point of this page"""),
("""<p>Every number on this page is drawn straight from the result files, which are linked at the bottom so you can rerun all of it yourself.</p>""",
 """<p>Every number on this page is drawn straight from the result files, which are linked at the bottom so you can rerun all of it yourself.</p>
<p>On this page, &plusmn; is one standard error: from the post-selected shot counts for the weak values, and across pairs for the entangled-minus-control differences. The correlator tables print single measured values, without an interval.</p>"""),
("""<p class="sticker">A rotation can be undone; a measurement cannot.</p>""",
 """<p class="sticker">A rotation can be undone. A measurement cannot.</p>"""),
("""The information didn&rsquo;t vanish; it moved into the link with its partner.""",
 """The information didn&rsquo;t vanish. It moved into the link with its partner."""),
("""(1 = fully its own, 0 = blank). ibm_marrakesh; replicated on ibm_kingston""",
 """(1 = fully its own, 0 = blank). ibm_marrakesh, replicated on ibm_kingston"""),
("""Two qubits have four slots; the fourth corner, 11, is never used, and it stays silent.""",
 """Two qubits have four slots. The fourth corner, 11, is never used, and it stays silent."""),
("""Hardware noise shrinks everything toward zero; the signs are the result.""",
 """Hardware noise shrinks everything toward zero, and the signs are the result."""),
("""that a standard noise model does not reproduce; see the <a""",
 """that a standard noise model does not reproduce. See the <a"""),
("""Two qubits have four basis states; we placed the box""",
 """Two qubits have four basis states, and we placed the box"""),
("""hardware noise shrinks weak values toward zero; this is nine standard errors below zero —""",
 """hardware noise shrinks weak values toward zero, and this is nine standard errors below zero —"""),
("""(ibm_marrakesh; the unused slot 10 leaked""",
 """(ibm_marrakesh. The unused slot 10 leaked"""),
("""The predictions were written in a running log during the session; that log&rsquo;s timestamps""",
 """The predictions were written in a running log during the session. That log&rsquo;s timestamps"""),
("""entanglement changes a qubit&rsquo;s memory; a later twist reaches the partner""",
 """entanglement changes a qubit&rsquo;s memory, and a later twist reaches the partner"""),
]
