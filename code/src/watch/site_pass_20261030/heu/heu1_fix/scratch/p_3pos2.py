D_OLD = "Jobs created 2–7 October 2026 (US Eastern), seven IBM processors: 305 jobs, 63 on 2 October, 43 on 4, 26 on 5, 48 on 6 and 125 on 7; three errored. The."
D_NEW = "The October 2026 campaign on IBM processors: every run with its job id and frozen scripts, the per-qubit data, and verify.py, which recomputes the published comparison."
PAIRS = [
('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'),
(f'<meta name="description" content="{D_OLD}">', f'<meta name="description" content="{D_NEW}">'),
(f'<meta property="og:description" content="{D_OLD}">', f'<meta property="og:description" content="{D_NEW}">'),
("""<p>Jobs created 2&ndash;7 October 2026 (US Eastern), seven IBM processors: 305 jobs, 63 on 2 October, 43 on 4, 26 on 5, 48 on 6 and 125 on 7; three errored. The 32 equal-idle jobs""",
 """<p>Jobs created 2&ndash;7 October 2026 (US Eastern) on IBM processors, with their scripts and the per-qubit data behind the October findings.</p>
<p>In all, 305 jobs ran on seven IBM processors: 63 on 2 October, 43 on 4, 26 on 5, 48 on 6 and 125 on 7, and three errored. The 32 equal-idle jobs"""),
("""<h2>Files</h2>""", """<h2>Files</h2>
<p>On this page, &plusmn; is one standard error of the pooled value: each processor&rsquo;s width is the spread of a 400-draw bootstrap over its untouched qubits, and the processors are combined by inverse variance (verify.py).</p>"""),
("""<td>on request, with the raw result arrays; runs.json carries each script&rsquo;s sha256.</td>""",
 """<td>on request, with the raw result arrays. runs.json carries each script&rsquo;s sha256.</td>"""),
]
