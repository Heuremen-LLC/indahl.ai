# BUILD_SITE_TODO_B (lane B), 30 Oct 2026
Why this file exists: the intro paragraphs of the QIA panels (the cal, queue and T1 and T2 sections) are string literals in indahl-ai/build_site.py (around lines 1980 to 1990, inside the `PAGES['/qia'].replace(_aq, ...)` block), not in qia_leads/matrix_page/qia_body.html where the findings put them. My brief allowed build_site.py only for the /qia/list and /qia/key titles and the study loop, so these four text fixes are not applied. Each one is an exact string replacement that occurs once in the current file (checked). Where a script of mine already says the same thing in the panel, it is noted. I can apply them if you say so.

1. B-4 and B-7, `<section id="cal">` first paragraph. After "If your job ran near one of ours, this is what your qubits were doing." add:
   " One job per processor is kept in flight, so a processor with a job waiting in IBM&rsquo;s queue shows its older reading beside the time the newer job was sent. The two interval rules were set after the first aachen run was read and before any US run was read."
   (B-7 itself is your fix in cal.py. The sentence is true today because of PLAN.md Note 2. cal.js already prints the rules sentence in the panel note.)
2. B-14, T1 and T2 section. Replace
   "The plan and its notes were committed before the results were read."
   with
   "The plan was committed before the results were read. Notes 3, 4 and 6 were written after some results were read."
   (t1t2.js already prints the longer version in the panel note, with which result each note followed.)
3. B-16(b), queue section. Replace
   "How many jobs IBM reports waiting at each processor, read once an hour, beside how long our own jobs waited there."
   with
   "How many jobs IBM reports waiting at each processor, read about every 12 minutes, beside how long our own jobs waited there."
   (qia_queue/PLAN.md Addendum 29 Oct: every 2 ticks, about 12 minutes. history.jsonl last reads 13:09 and 13:22 UTC on 30 Oct.)
4. B-2 context, not a build_site.py change: the gate table caption is in qia_body.html (done).

Also for whoever owns the first-screen headline block (watch/headlines.py, build_site.py headline bake), B-29: the baked copy keeps "waiting 21 min so far" for hours. Leave "so far" waits out of the baked block, or bake the ship time next to them. headline.js already replaces the block in a browser. Not mine.
