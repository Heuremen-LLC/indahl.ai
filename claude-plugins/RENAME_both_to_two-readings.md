# Rename plan: indahl-both -> indahl-two-readings (13 Nov 2026)

Why: "both" says nothing on a directory card. The skill holds two competing explanations open (A, B, BOTH, NEITHER, OPEN)
until evidence separates them. "two-readings" says that in two words. Same pattern as slack -> margin tonight.

When: after the directory review of the current indahl-both submission clears (Wayfinder submitted it 13 Nov). Renaming while
it is in review would void that review. Withdraw-and-resubmit is his click, same as slack.

## Steps (all from the record, same as the margin rename, about 10 minutes)
1. Archive: tar src/both and plugins/both to ~/bones-forge/archive/claude-plugins-both-before-two-readings-<date>.tgz.
2. Move: src/both -> src/two-readings, commands/both.md -> commands/two-readings.md, skills/both -> skills/two-readings.
3. Text inside the skill: plugin name indahl-both -> indahl-two-readings, skill name both -> two-readings, title "Both" -> "Two readings".
   KEEP the four-state word BOTH (one of A / B / BOTH / NEITHER / OPEN): it is an outcome name, not the skill name. So no blanket
   sed: replace only `indahl-both`, `name: both`, `# Both`, `/both`, and the folder paths, then read the file in full.
4. README: add "Renamed <date> from indahl-both to indahl-two-readings. Same skill." Credit lines stay as they are.
5. Builders: 'both' -> 'two-readings' in PARTS of build_plugins.py and build_bundle.py, ORDER and the starter prompts in
   build_openai.py, the marketplace.json entry (name, source, description from plugin.json). rm -rf plugins/both and openai/indahl-both*.
6. Site: /connect and /plugins are generated from marketplace.json. /how is hand-written in build_site.py (_HOWS) and names indahl-both: edit it by hand. Add one line on /plugins: "indahl-both is now indahl-two-readings", so existing installs (`indahl-both@heuremen` stops resolving) know where it went.
7. Ship via ledger/ship.sh (builds, re-pins, mirrors to Heuremen-LLC/claude-plugins). Check plugins/two-readings answers 200 on GitHub
   and plugins/both is gone. grep -ri "indahl-both" over claude-plugins, openai and the site build: zero hits outside the README rename line, the /plugins redirect line and the archive tarball. List every hit.
8. Portal: Wayfinder withdraws indahl-both; Bones fills indahl-two-readings to step 4; his ticks, his submit, his publish request.
9. Bundle (indahl) and indahl-full pick up the new part name on the build; the bundle's directory listing needs its publish re-requested.

## Not changing
The four-outcome vocabulary, the skill body, any other part.

Refereed by Sage 13 Nov 2026 (MOVES, applied): /how is a hand edit, the zero-grep exempts and lists, and existing installs get a redirect line.
