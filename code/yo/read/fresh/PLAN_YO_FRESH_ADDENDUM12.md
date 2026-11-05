# YO Read FRESH TEST, Addendum 12 (Sage, 5 Nov 2026), written BEFORE any output is read

No eval_fresh file, out_ log or OUTPUTS_YO_FRESH content has been opened.
1. Sage (VERDICT 05:48:20Z): some trained DOIs were trained on another record's text, so matches against the DOI's own metadata may look
   at the wrong label. contam/yf_textrecord.py: of 540 trained papers, 36 text files are not named for their own DOI; 26 are the same record
   under another file name (zenodo_X.txt); 10 are another record: 4 published versions of arXiv papers, 1 adjacent Zenodo record
   (21987398 read via 21987397), and 5 known same-work pairs where training read the FRESH twin's own text (19303627 via 18671523,
   20108939 via 20108875, 22644883 via 22072152, 22809021 via 22736832, 22849729 via 19633727); those 5 fresh papers are outside primary
   and sensitivity.
2. The full-text check already compared against the files training read. contam/yf_textrecord_meta.py reruns the author/title match for
   the 10, against the record actually read: 1 hit in primary/sensitivity, zenodo.18880113 (Green, VQ-MODEL) ~ the read record 18671523
   (PermaMind), already called SIBLING in contam/HAND_READ_5.text from that same text. Nothing new; no list changes.
3. Custody wording (Sage, same verdict): "every sentence in the training files is fixed by Bitcoin block 974519, and read1's training files
   (with labels) are vouched for by its stamped adapter, reproduced bit-for-bit" (read/retrain_read1/RESULT.md, yo 02fb799).
4. Disclosed again: A7 to A12 postdate the output stamp (block 974615); that the outputs are unread is self-witnessed.

Files (sha256):
   c074fe3fda474be09ec8466e36573e3294ee1eb0bcbd4b0ab352a36c09e0e767  contam/yf_textrecord.py
   ed31c50af7577f500a591b031c76f47854e0fb739527b74a47999ca3dd42a2eb  contam/yf_textrecord.out
   f779b37473ddf3aa7de499e2dce730c88ab1b4c801e5516595ee2d09d2db3b34  contam/yf_textrecord_meta.py
   e7d4ba5ad373fc1e087cc9e74b7f3f96532cb94e0aad1b3d54ac900b982b909a  contam/yf_textrecord_meta.out
