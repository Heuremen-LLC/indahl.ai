PAIRS = [
# HEU1-4 + HEU1-20 descriptions
("""<meta property="og:description" content="Superposition across time and entanglement across space are the same link. Measured on three IBM quantum chips in one evening, with the two times we.">""",
 """<meta property="og:description" content="Correlation across time and correlation across space follow the same cosine on the same chip, measured on IBM quantum processors on 24 September 2026. The readings that did not hold are kept on the page.">"""),
("""<meta name="description" content="Superposition across time and entanglement across space are the same link. Measured on three IBM quantum chips in one evening, with the two times we fooled ourselves left in.">""",
 """<meta name="description" content="Correlation across time and correlation across space follow the same cosine on the same chip, measured on IBM quantum processors on 24 September 2026. The readings that did not hold are kept on the page.">"""),
# HEU1-18
("""<p class="note">ibm_marrakesh, pairs 1-2 and 133-134. Replicated on ibm_kingston (pair 144-145; −0.813 vs −0.840 at π) and ibm_fez (−0.891 at π).</p>""",
 """<p class="note">ibm_marrakesh, pairs 1-2 and 133-134. Replicated at π on ibm_kingston and ibm_fez. Kingston space is −0.813 on pair 144-145. Kingston&rsquo;s other pair, 16-23, is excluded as a dead readout (its length alone reads 1.355, above the possible 1). Its space value at π is −0.159, and the mean of both kingston pairs would be −0.486. Kingston time is −0.840, the mean of qubits 1, 2 and 133 in the arrow run, not of pair 144-145. Fez space is −0.891, the mean of pairs 22-23 (−0.950) and 81-82 (−0.832). <a href="experiments/2026-09-24-temporal-spatial-correlations/verify_september_output.text">verify_september.py output</a></p>"""),
("""<p class="note">ibm_marrakesh, qubits 1, 2, 133. Replicated on ibm_kingston and ibm_fez (−0.925 / −0.919 at π).</p>""",
 """<p class="note">ibm_marrakesh, qubits 1, 2, 133. Replicated on ibm_kingston and ibm_fez (fez at π: −0.925 forward, −0.919 backward).</p>"""),
# HEU1-12 heading + HEU1-3 table
("""<h2>The five that came back textbook</h2>""", """<h2>What came back textbook</h2>"""),
("""<td>+0.0012 ± 0.0024 at zero wait: nothing</td>""",
 """<td>+0.0012 ± 0.0024 at zero wait (8 pairs): consistent with zero</td>"""),
("""<td>bell first +0.0124 ± 0.0046; bell last −0.0013 ± 0.0154. <strong>Fake #1:</strong> it was the order.</td>""",
 """<td>bell first +0.0124 ± 0.0046, bell last −0.0013 ± 0.0154. <strong>Cannot tell:</strong> the reversed arm reaches both 0 and +0.0124 within one standard error, so the effect was neither confirmed nor removed.</td>"""),
("""<td>χ² 19.4 on 20: no dependence at all</td>""",
 """<td>χ² 19.4 on 20 degrees of freedom: consistent with no phase dependence, within each pair&rsquo;s own fit error</td>"""),
("""<td>first run −0.0076 ± 0.0036; balanced rerun −0.0014 ± 0.0026. <strong>Fake #2:</strong> an unbalanced partner.</td>""",
 """<td>first run, partner unbalanced, −0.0076 ± 0.0036. Balanced rerun −0.0014 ± 0.0026: consistent with zero. <strong>Not confirmed:</strong> the two runs differ by less than two standard errors, so the imbalance is not shown to be the cause.</td>"""),
("""<p class="note">Numbers are entangled-minus-control differences, recomputed from the result files by""",
 """<p class="note">Numbers are entangled-minus-control differences, mean over pairs &plusmn; one standard error across pairs, recomputed from the result files by"""),
# HEU1-3 prediction record
("""<p>Twice a chip handed us a clean-looking ~1% effect. Once it was the order the circuits ran in; once an unbalanced partner qubit. Balanced reruns killed both, and both are in the table because a prediction record with the misses taken out is not a record. </p>""",
 """<p>Twice a chip handed us a clean-looking ~1% effect. The first did not hold when the circuit order was reversed: the reversed arm cannot tell, because its interval holds both zero and the first value. The second did not repeat once the partner qubit was balanced, where it reads consistent with zero. Neither effect was confirmed, and both are in the table because a prediction record with the misses taken out is not a record.</p>"""),
("""<p>This page found that <b>entanglement itself costs nothing extra</b>: an entangled pair loses the same coherence as a matched unentangled control (+0.0012 &plusmn; 0.0024 at zero wait), and the two runs that first looked like a ~1&thinsp;% extra were the circuit order and an unbalanced partner, removed by balanced reruns.</p>""",
 """<p>This page found <b>no extra cost from entanglement itself</b> that these runs resolve: an entangled pair&rsquo;s coherence loss is consistent with that of a matched unentangled control (+0.0012 &plusmn; 0.0024 at zero wait, one standard error over 8 pairs). The runs that first looked like a ~1&thinsp;% extra were not confirmed: with the circuit order reversed the reading cannot tell, and a balanced rerun reads consistent with zero.</p>"""),
]
