# YO Read FRESH TEST, Addendum 9: a same-work paper in primary (Sage, 5 Nov 2026), written BEFORE any output is read

No eval_fresh file, out_ log or OUTPUTS_YO_FRESH content has been opened.
1. Sage asked for a hand read of every primary and sensitivity paper whose trained match has author overlap >= 0.5 at any title score,
   because every known twin had kept its title. List: contam/yf_same_author.py and .out (29 fresh papers). Calls: contam/HAND_READ.text.
2. Found: doi:10.5281/zenodo.18154889 (in primary AND sensitivity) is the SAME WORK as trained doi:10.5281/zenodo.18155193 (TRAIN split):
   a Turkish version with the same abstract and numbers. Title score 0.00 and full-text share 0.022 (language), so every automated check
   missed it, including the metadata check that found 8 of 8 known twins.
   doi:10.5281/zenodo.19437054 (primary and sensitivity) is BORDERLINE: a later edition of the same LCL-832 research programme as two
   trained records, with a separate record and different numbers.
   The other 27 are siblings or different people (SIBLING calls for 4 read in text; 23 from titles and author lists only).
3. Primary is stamped and is not changed. It stays the headline, and the page says it contains one same-work paper and one borderline one.
4. Two more sensitivities, reported regardless of how they read: "samework" = primary minus zenodo.18154889 (87 papers);
   "samework_border" = primary minus zenodo.18154889 and zenodo.19437054 (86 papers). Run by yf_minus_a9.py, the same code as
   yf_minus.py with only its list changed (refuses unless yf_score.py is the Addendum 3 scorer). Planted test: yf_minus_a9_tests.out.
5. In the full set (secondary) two more are same work or likely same work: zenodo.20779478 ~ 20779575 (same work; training saw only the
   trained record's landing page) and zenodo.18204497 ~ 18646355 (likely same work, rewritten).
6. Disclosed: A7, A8 and A9 were stamped after the output stamp (block 974615, 03:00:14Z). Their "before" is before reading the outputs,
   and that the outputs are unread is witnessed only by us.

Files (sha256):
   3425afb6588a55d0bb5b2a4541965e54ba84d3ca53da1e672c02c29dba4bd4c3  contam/yf_same_author.py
   bcbe6b14fdcbef1a3307c877966e63afd6a338692ec63a355b99f3915d16a431  contam/yf_same_author.out
   c8ee439918a036a04311f40f20ce434a2ff1c04bc3be672a1a55ba581b3117f1  contam/HAND_READ.text
   67d70ad35c48baad1322035ba568fbe9829842b5af4385647dac6c3c6e5e8233  yf_minus_a9.py
   859f1ea65a1e39dcab8bb9793e615a664ff95c6fb7f9a6dac3f40578d9401c27  yf_minus_a9_tests.out
