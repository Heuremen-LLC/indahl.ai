PAIRS = [
("<p>Twelve runs on six processors. The known-good",
 "<p>Every run is listed below, on ibm_kingston, ibm_marrakesh, ibm_fez, ibm_pittsburgh, ibm_phoenix and ibm_boston. The known-good"),
("""<a href="raw_hahn_ibm_marrakesh.npz">raw</a></td></tr>
<tr><td>fez</td><td>run 1</td>""",
 """<a href="raw_hahn_ibm_marrakesh.npz">raw</a></td></tr>
<tr><td>marrakesh</td><td>fresh record</td><td>10-23 19:44</td><td>0.5</td><td>1.015 [0.937, 1.130] CONSISTENT<br><small>73 of 153 below</small></td><td>0.958 [0.902, 1.016] CONSISTENT<br><small>83 of 150 below</small></td><td><a href="job_hahn_ibm_marrakesh_fresh.json">job</a> <a href="props_hahn_ibm_marrakesh_fresh.json">props</a> <a href="raw_hahn_ibm_marrakesh_fresh.npz">raw</a></td></tr>
<tr><td>fez</td><td>run 1</td>"""),
("""<a href="results_hahn_ibm_phoenix.text">phoenix</a>. The plain-named""",
 """<a href="results_hahn_ibm_phoenix.text">phoenix</a>, <a href="results_hahn_fresh_ibm_kingston.text">kingston fresh record</a>, <a href="results_hahn_fresh_ibm_marrakesh.text">marrakesh fresh record</a>, <a href="results_hahn_ibm_boston.text">boston</a>. The plain-named"""),
("""(<a href="results_hahn_fresh_ibm_kingston.text">output</a>). An earlier""",
 """(<a href="results_hahn_fresh_ibm_kingston.text">output</a>). Marrakesh&rsquo;s three runs (1, 2 and fresh record) pooled by qubit: 0.972 [0.929, 1.022] CONSISTENT (fixed fit), 0.889 [0.845, 0.936] BELOW (free fit) (<a href="results_hahn_fresh_ibm_marrakesh.text">output</a>). An earlier"""),
("""Marrakesh&rsquo;s fresh-record run waits for IBM to remeasure its T2 (as of 23 October).""",
 """Marrakesh: IBM remeasured its T2 in the record of 23 October 15:17 EDT, and the fresh-record run, on stated values 0.5 hours old, reads CONSISTENT under both fits (1.015 [0.937, 1.130] planned, 0.958 [0.902, 1.016] free), so marrakesh does not meet the rule. Its three runs pooled read CONSISTENT under the planned fit and BELOW under the free fit."""),
]
