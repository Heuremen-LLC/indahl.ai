# Addendum 3 to PLAN_YO_FRESH.md (4 Nov 2026, Sage VERDICT 23:15Z on Addendum 2: MOVES). Stamped before any adapter answers a fresh item.
Addenda 1 and 2 stand except where this changes them.
1. What is measured. yr_data.truth sets DATES = NO only when an F4 note contains "run dates not printed", and LINK = NO only on "no data link printed"
   or "no data or code url|link|repositor". The List's F4 notes record what a paper leaves out and never record dates or links as found. In the 88
   primary papers, 44 DATES YES and 42 LINK YES come from silence (the note says nothing about them). So this round measures AGREEMENT WITH THE LIST
   READER'S F4 NOTES AS PARSED BY yr_data.truth, ON UNSEEN PAPERS. It is not a test of what each paper prints. truth() is NOT changed, so the round
   stays comparable with the first 148-paper test, which was scored the same way.
2. PRIMARY = the 88 (Addendum 2), truth() unchanged. SENSITIVITY = 84: the 88 minus four labels known before any model answer to be wrong or tainted:
   elte.2025.051 (DATES note "no date printed for the two quantum processor runs", parsed YES), zenodo.18049904 ("no url, doi or repository for data or
   code printed", parsed LINK YES), zenodo.17883260 ("data doi printed as a placeholder, no data url", parsed LINK YES) and ssrn.7358502 (same-author
   near-twin of a used paper). math14132314 and zenodo.19078829 are arguable LINK labels and stay in both sets. Sensitivity YES: DATES 43/84,
   LINK 67/84, REQUEST 12/84.
3. A field's verdict reads as shown only if it holds on BOTH sets (yf_combine.py). If the two sets disagree, the field prints "depends on 4 labels"
   and nothing stronger. The 288 remain a secondary reading with no verdict.
4. Page wording: "matches the reader's notes", never "reads papers", for this round and for the existing 148-paper results. A test of what papers
   print needs a labelling pass where the reader writes dates and links down as found. That is a future plan with its own stamp.
5. Every file the result depends on, with its sha256 (paths relative to yo/read/). The driver refuses to run if any of them has changed
   (STAMPED_FILES_ADDENDUM3.sha256 holds the same lines):
   51de1626dca19d79a2ef2cef9d26643da32d9781ed17a8edcf2169c688728482  fresh/data/list_snapshot_20261104.json
   ec3b9595c420c6e81d37cbd983f796f2d3b00cce7907bd75a9e766ced59dcb5e  fresh/primary_ids.txt
   b64df5183330172d17084a3f080e56d5bcadd53680055c41c6ffea94f79610be  fresh/sensitivity_ids.txt
   17eb1f3c2df9b83ce2d44fca16e2138f912205fa64afb4a2648acecf2c0d5373  fresh/data/test_items_primary.jsonl
   329291f4ede5618207da960f7efbd46d8db29f2c29d41979bb8490431c7126bb  fresh/data/test_items_sensitivity.jsonl
   e1087ae0c23dfb46daa13e3cbfe8c18c73499efa56a9f2817827fb4fb9b5e92c  fresh/data/test_items_fresh.jsonl
   f7d7a5e6ea120c45dc1691855a4807c449986784966dc3eaae11004b7afb2fa1  yr_data.py
   c085f5df854ffd42df55cd8da1945d576e7bb2d9873c7ecc403f943d433eba2a  yr_known_good.py
   280043a19fd0d5a5a32e8ccf665dec58ecd0aa4af7bad493f13e7d1f0525a067  fresh/yf_build.py
   ae9fa83e373a285603e65cdaa959c858989b37fba76ae2dc0dacbf259a737b67  fresh/yf_primary.py
   5f320c5d8c5e1be42a5245e0ff3f468431764756fbc5bbdddd12fa75b8666539  fresh/yf_sensitivity.py
   9e4729b0c4fd3edf99beeef72f0badd51ddb921522523cb7a26691529bad71d8  fresh/yf_eval.py
   26194d1af29b1ab18b9d573d1213846e258b4c683b3d5a790dcf87c5a0ebad2d  fresh/yf_score.py
   42daa5f4f936d8acb31448c716c1d00f63e25945ea22358eca59e3262ab79dc9  fresh/yf_combine.py
   a4516895ea9db47c15d4f3efa61b8c9f793a1ec132ca26464c63d0c139df7ad0  fresh/yf_gate.py
   30fca903b7c1e78f2755458418fcd95ec264ec6bd7d4ddf22cbea6c1ffc6aa53  fresh/yf_drive.sh
   3a33c1945cd3795e3e9ce1c68c7c5c5abe05333f5a42961696e701500ed4977f  ../yo2_data.py
6. Receipts saved before this stamp: yf_score_tests.out now also covers the sensitivity set, the combine step, and a planted split, which prints
   "depends on 4 labels". KNOWN_GOOD.text and PRIMARY_SET.text are unchanged.
7. The gate (yf_gate.py) requires verified Bitcoin block attestations on the plan and on Addenda 1, 2 and 3 before the first adapter loads.
