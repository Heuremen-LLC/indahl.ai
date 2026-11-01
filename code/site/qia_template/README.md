# Quantum Idle Audit bill template

Edit only the data file, then render:

    python3 render_bill.py QIA-2026-001.json      # writes QIA-2026-001.html and .pdf

- `QIA-2026-001.json`: case number, date, chips, and three lists of rows: `deviations`
  (n, figure, chip, ibm_states, delivered, deviation, how), `record_notes` (n, record, chip, shows),
  `effects` (n, effect, ibm_states, delivered, how), plus the `method` line. Rows are numbered 1..N in order.
- `head.html`: letterhead and base style. `render_bill.py`: layout, page fitting, house-style checks.
- The renderer refuses to build on: straight apostrophes, dash ranges (write "a to b"), states as bare
  digits (write |0⟩ |1⟩), hashes, money figures, AI or framework words, row numbers out of order.
- It fits the pages itself: the third section starts on a new page, and the footer is never alone on a page.
- A new case: copy the JSON to the new case number and replace the rows.
Deploy: copy the PDF to cloudflare-workers/heuremen-door/public/quantum-idle-audit.pdf and to this repo's
quantum-idle-audit.pdf, then `npx -y wrangler@4 deploy` in the worker folder.
