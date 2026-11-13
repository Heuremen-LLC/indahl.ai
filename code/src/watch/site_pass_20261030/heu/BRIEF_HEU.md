# Site pass with the check block, 30 Oct 2026. Lane brief (read-only).

You are one lane of a full pass over the live site https://heuremen.org (Heuremen LLC). You READ ONLY: never edit, commit, deploy, send,
post or run anything that writes outside your own findings file. Your findings go to ~/bones-forge/watch/site_pass_20261030/<lane>.md
and are also your final answer. Bones verifies every finding by hand before anything is changed, so evidence matters more than volume.

## The checks (read these files in full first)
- ~/bones-forge/watch/checks/core.md   (I the none, II the gap, III the sign, V the ruler, VI four outcomes, R the record)
- ~/bones-forge/watch/checks/pack_P.md (public copy; every lane runs it)
- plus your lane's packs: pack_Q.md (quantum / QIA), pack_L.md (language-model evaluations), pack_O.md (live feeds and operations)
Ignore the "Conditional" and "Log the catch" lines in core.md; they are internal.

## What counts as a finding
- A number on a page that disagrees with its own source (the JSON feed the page loads, the released file, the paper it quotes, the
  ledger at ~/bones-forge/ledger/ledger.jsonl, or the build inputs in ~/bones-forge). Give page value, source value, source path.
- A quote in quotation marks that is not verbatim in its source. A figure that does not say where it lives. An interval with no level.
- A verdict word (above, below, consistent, cannot tell, beats, fails, wrong) stronger than the reading under it, or two outcomes where
  the reading has four. A cause or mechanism named where only a rule-out was measured. A post-hoc reading not labelled.
- A live section that does not fill: a script or feed that 404s, a "Loading." that never resolves, a time stamp older than its stated
  cadence, a broken link (internal or outbound), an image that fails.
- House style on public copy: plain sentences (no semicolons in page prose), no count of our own things in a title, heading, lead line
  or nav label, no statements about AI assistance, neutral (no religion, no nationalism), the company is "Heuremen LLC", no email
  addresses printed, no personal names of the site owner, no internal names (machine names, "Bones", internal codenames) leaking into
  public copy unless they are part of a published byline. Typos and broken HTML (unclosed tags, raw template markers, "undefined",
  "NaN", "null" rendered as text).
- Anything that would embarrass us in front of a reader who knows the field better than we do (assume they do).

## Method
Fetch pages live (curl -s with a cache-busting query like ?w=1). Use python3 -I for any script you write; keep scripts in your
lane's scratch folder ~/bones-forge/watch/site_pass_20261030/scratch_<lane>/. Many pages are generated: find the generator with grep
under ~/bones-forge (indahl-ai/, cloudflare-workers/heuremen-door/public/, qia_leads/matrix_page/, iris_index/matrix_page/, oy_index/,
the *_index folders) so the fix can be named at the source, not the built file. Cover EVERY page in your lane (script the sweep for
large lanes; then read a real sample by eye, at least 10 or all if fewer). Count what you could not check and say why, by page.

## Return format (markdown, this order)
1. COVERAGE: pages in lane, pages checked by script, pages read by eye, pages not checked with reason.
2. FINDINGS: one block each:
   - id: <lane>-<n> | check: <core or pack line, e.g. P5, I, Q19> | severity: wrong-number / wrong-claim / broken / style
   - where: URL (and section)
   - page says: short exact text (under 25 words)
   - source says: short exact text or value, with file path and line or JSON key
   - fix at source: file to change and the change
3. HOLDS: the checks you ran that found nothing, one line each with what you looked at.
Never print secrets, keys or tokens if you meet any; name the file only.

## heuremen.org specifics (read these, they override the general rules above where they differ)
- heuremen.org is the science site: the paper "A Readout Is Not an Idle" (a-readout-is-not-an-idle.pdf), Faults (faults.pdf), Guards (guards.pdf),
  the experiment data pages under /experiments/, the technical summary, what-we-measured, correlations and media pages.
- Sources: the site tree ~/bones-forge/heuremen.org/ (its pages are the sources unless a generator is named), the Faults and Guards sources in
  ~/bones-forge/ligera/ (FAULTS.html, GUARDS.html, render.sh), the run folders the experiment pages point to, the ledger
  (~/bones-forge/ledger/ledger.jsonl rows whose surfaces are heuremen.org pages or the PDFs; ~/bones-forge/ledger/ledger.py SURFACES lists them),
  ~/bones-forge/ledger/copies.json (which file is canonical for each PDF), and the Zenodo record (concept DOI 10.5281/zenodo.23169755).
- These are NOT findings on this site: the bylines "Wayfinder and Bones", and in the papers the two disclosure lines ("collaboration with inorganic
  intelligences" and "An AI assistant, Claude Code (Opus 5.5), was used"). Papers keep both lines by our rule. Everything else in the house style
  section applies, including no religion and no nationalism anywhere, and no semicolons in page prose we wrote.
- For a PDF, extract its text (python3 -I with pypdf from the qvenv: ~/bones-forge/qvenv/bin/python -I) and check every number against its source
  row, every quote against its source, every interval for its level, every claim for the four outcomes and for a cause named where only a rule-out
  was measured. Also check that the live PDF equals its canonical copy in copies.json (sha256).
