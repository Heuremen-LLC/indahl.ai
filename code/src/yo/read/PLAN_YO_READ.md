# YO Read -- plan (committed before any YO Read item was built, any seed trained or any reply read; times from git). Wayfinder and Bones.
Wayfinder, 2 Nov: "we still have a stripped down model to train, where else can we point it?" ... "go for it!"
Why: the QIA List's F4 lines ("run dates not printed", "no data link printed", data "on request") come from reading each paper in full.
Two of them were wrong on 1 and 2 Nov (a GitHub link held on a Zenodo record, counts held in a record bundle). A small reader that answers
the three F4 questions from the sentences that could carry the answer would put a second reading beside ours before a notice goes out.
YO does not decide any code: it answers YES or NO on sentences code picked, and every disagreement goes back to a full reread.

## Data
Papers: every study in qia_leads/sweep_20261101/out and qia_leads/backfill_20261101/out whose text file is on disk and whose List entry
(qia_leads/matrix_page/list.json, matched by arXiv id or DOI) reads "Full text". The List as published is the truth.
Questions, one item per paper per question (answer YES or NO):
 - DATES: does the text print a date or date range of the hardware runs? Truth NO iff the entry's F4 lines include "run dates not printed".
 - LINK: does the text print a URL, DOI or repository for the study's own data or code? Truth NO iff an F4 line reads "no data link
   printed" or "no data or code URL / link / repository".
 - REQUEST: does the text say data or code are available on request? Truth YES iff an F4 line contains "request".
Candidates, picked by code (yr_data.py) from the text with the reference list cut (last References or Bibliography heading in the second
half of the text): sentences matching the question's pattern (DATES: a month name, an ISO date or a year 2016 to 2026; LINK: http, www,
doi, github, gitlab, zenodo, figshare, osf.io, repository, availability, supplementa; REQUEST: request, availab, contact), stronger
matches first (DATES: month or ISO date before year only; LINK: a URL before words only), then text order, at most 20, each cut to 240
characters around the match. A paper with no candidate for a question still gets the item ("no sentence matched"). The same candidates
go to every arm. The count of items whose candidates were capped at 20 is reported by question.
Split by paper, fixed now: TEST = first hex digit of sha256(normalised id) in 0,1,2; VALID = digit 3; TRAIN = the rest. TEST is not read
before the comparison.
## Training
Base Qwen/Qwen3-1.7B, a new LoRA (not continued from YO v7), mlx-lm, mask_prompt, max_seq_length 2048 (every prompt checked under 1,900
tokens before writing), LoRA on 16 layers, batch 4, learning rate 1e-4, 800 iterations, validation every 200. Seeds 61, 62, 63
(adapters read1, read2, read3), one after another, one GPU job at a time on the Mac.
## Arms and readings
Arms: each seed; REGEX (fixed now: DATES YES iff a candidate has a month name with a year or an ISO date; LINK YES iff a candidate has a
github, gitlab, zenodo, figshare or osf.io address, or an availability sentence with a URL; REQUEST YES iff a candidate matches
"(up)on (reasonable) request"); MAJORITY (the TRAIN majority answer per question); BASE (Qwen3-1.7B, no adapter, same prompt).
Reply parse, fixed now: the first YES or NO word in the reply; anything else is unread and scored wrong, counted by arm.
RD, RL, RQ = share of TEST papers answered right, per question. Each seed minus REGEX, paired bootstrap over TEST papers, 2,000 resamples,
seed 41, 95 %, margin 0.02, four outcomes. Also printed: false YES and false NO per arm, and the flips against REGEX in each direction.
RULE (written before any item is built): a seed passes if RD or RL is ABOVE REGEX and none of RD, RL, RQ is BELOW REGEX. YO Read goes to
work as a second reading before QIA notices only if ALL THREE seeds pass, seed 61 first. Otherwise it is reported as tried. No seed is
chosen by its scores. Every reading is published.
## KNOWN-GOOD
The scorer on the truth gives 1.000 on TEST for every question, and the driver refuses to train if not. Replies are read in full (parse
check on every reply plus 10 per question per seed) before the comparison is written.
