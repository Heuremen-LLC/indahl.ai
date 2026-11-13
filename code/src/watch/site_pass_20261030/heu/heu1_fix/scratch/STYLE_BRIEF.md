# Style pass on heuremen.org experiment pages (HEU1-10, 11, 12, 13, 20, 21), 30 Oct 2026

You edit ONLY the pages listed for you in your prompt, all under /Users/heuremen/bones-forge/heuremen.org/ (the site source tree; live is byte-identical).
Every page is already backed up at /Users/heuremen/bones-forge/archive/heuremen_heu1_backups/<same relative path>.pre-heu1-20261030. Never touch those backups.
Never run ledger/ship.sh, git, ledger.py add/set/on/off/withdraw, or anything that submits an IBM job or calls IBM. Do not create new files inside heuremen.org.
Edit with exact string replacement (python with assert count==1, or the Edit tool). No sed -i over whole files.

## The review
Read /Users/heuremen/bones-forge/watch/site_pass_20261030/heu/HEU1.md findings HEU1-10, 11, 12, 13, 20, 21 (the rest is handled elsewhere; do not change claims).

## What to do on each of your pages
1. HEU1-11 semicolons: no semicolon in visible page prose. Rewrite as plain separate sentences (or use commas/parentheses where that reads naturally).
   NEVER change a number, an interval, an outcome word (ABOVE, BELOW, CONSISTENT, CANNOT_TELL, cannot tell, consistent with zero, above zero,
   resolved, excluded, not decided...) or a claim while doing this. Keep every link. Not prose (leave alone): code, <code>/<pre> content,
   URLs, CSS, HTML entities (&rsquo; etc.), and quoted program output (literal lines copied from an output file).
   Semicolons inside parentheses usually become a comma or a second parenthesis or a separate sentence. Keep the meaning exact.
2. HEU1-10: add ONE sentence per page (a short <p> placed right after the lead paragraph, or under the first results heading) that states what
   brackets [lo, hi] and plus-minus (±) mean ON THAT PAGE. Read it from that page's own plan and code/outputs: find the percentile call
   (e.g. np.percentile(..., [2.5, 97.5]) = 95 %), the number of draws, and what is resampled (qubits, pairs, shots, copies). Copy-gap intervals
   are intervals on copy 0 minus copy 1. ± may be a standard error, a shot-noise standard deviation, a bootstrap spread: CHECK, do not assume.
   If the page prints no brackets and no ±, add nothing. If brackets on one page come from two different procedures, say both.
   Example: "On this page, brackets are 95&thinsp;% intervals from a 2000-draw bootstrap over qubits, and copy gaps are the same interval on copy 0 minus copy 1."
   Record the file and line you read it from.
3. HEU1-12: no count of our own things (jobs, runs, readings, claims, qubits, processors, chips, rows...) in the <title>, <h1>, any <h2>/<h3>,
   the lead paragraph (the first <p> of body text after the h1), or the meta description / og:description. Rewrite those lines without the count;
   the count can move into a later body sentence (keep it, unchanged, in the body). Dates are fine.
   Check with: cd /Users/heuremen/bones-forge/heuremen-specbook && python3 -c "import sys; sys.argv=['x']; import count_scan as c; [print(r) for r in c.scan(sys.argv[1:] or [PATHS])]"
   (or just import count_scan and call c.scan([your paths])).
4. HEU1-13: a "Claim N" (e.g. "Claim 4", "Claim 7", "claim 4") is named in words instead, in title, h1, description and body. Keep URLs/slugs as they are.
   Claim 4 = "the kick is not bigger with the measured qubits in 1". Claim 6 = "readouts cost untouched qubits coherence".
   Claim 7 = "readouts cost untouched Bell pairs entanglement".
5. HEU1-20: every <meta name="description"> and <meta property="og:description"> must be one or two complete plain sentences that describe the page
   (no cut-off "The." endings, no semicolons, no counts of our things, no link-list text). Description and og:description identical.
   Use &rsquo; or a plain apostrophe consistently with the page; keep it under about 200 characters.
6. HEU1-21: wrap every wide <table> in <div style="overflow-x:auto">...</div> (unless already wrapped), and add
   <meta name="viewport" content="width=device-width,initial-scale=1"> after <meta charset...> if the page has none.

## House style for anything you write
Plain sentences, no semicolons, neutral, no ranking words ("best", "remarkable", "clean win"...), "we/us/our" for our own work, no statements
about AI, no personal names, public copy says "read in full" and never "by hand", never the word "apparatus" in prose (file names and URL slugs
stay as they are), no count of our things in titles/headings/leads/descriptions.

## Ledger snippets (exact text that must stay on the page, compared after stripping tags, unescaping entities and normalising dashes/minus/spaces)
If your pages carry any, they are listed in your prompt. Keep each one verbatim. If you must change one (it contains a semicolon), say so in your
report with the old and new text. You may run the read-only check: python3 /Users/heuremen/bones-forge/ledger/check_ledger.py | grep <your page path>

## Self-check after each page (required)
python3 /Users/heuremen/bones-forge/watch/site_pass_20261030/heu/heu1_fix/scratch/numdiff.py <page path>
It compares visible body text with the backup: numbers and outcome words removed/added, hrefs, and semicolons before -> after.
Numbers or outcome words removed = you changed a reading: undo it. The only numbers you may add are those in your bracket sentence (95, draw counts)
or counts moved from a title/lead into the body (then they show as unchanged). Semicolons after must be 0 unless they are in code/quoted output
(say which). Also re-run python3 /Users/heuremen/bones-forge/watch/site_pass_20261030/heu/heu1_fix/scratch/semis.py <page path> (visible semicolons
outside <code>/<svg>, and meta-description semicolons).

## Report (your final message; it is all Bones sees)
For each page: semicolons before -> after; the bracket sentence you added and the source file:line it rests on; every title/h1/lead/description
change as "said / says now"; any Claim N renamed; tables wrapped / viewport added; any ledger snippet you had to change (old/new); anything you
could not fix and why. Keep it compact.
