# YO Read FRESH TEST, Addendum 10 (Sage, 5 Nov 2026), written BEFORE any output is read

No eval_fresh file, out_ log or OUTPUTS_YO_FRESH content has been opened.
1. Wording ruled by Sage (VERDICT 05:42:58Z): "fresh" is not printed. The page says "screened for same work": primary contains one known
   same-work version (zenodo.18154889, a Turkish translation of trained 18155193) and one borderline later edition of a trained programme
   (zenodo.19437054, LCL-833: "same programme, later edition"). Primary stays the headline; the samework sensitivities sit beside it at
   equal size and placement.
2. The sensitivity set (84) gets the same two runs: "samework" (83 papers) and "samework_border" (82), by yf_minus_a10.py TAG sensitivity
   (yf_minus.py code generalised to a SET argument; refuses unless yf_score.py is the Addendum 3 scorer). It also runs the two primary
   lists. Planted test: yf_minus_a10_tests.out.
3. Translation pass (contam/yf_lang.py, yf_lang.out, yf_translate_match.py, yf_translate_match.out): the detector catches the known Turkish
   paper; it is the only non-English fresh paper in primary and sensitivity. Non-English trained papers, titles translated by the model in
   session (no translation service), match no fresh paper (best title 0.18, no shared surname) beyond the known full-set Sanchez pair.
   Nothing new, so no further minus-run is added.
4. Abstract reads (contam/HAND_READ_ABSTRACTS.text: Brahmbhatt x9 and Sanchez x3, against hard specifics; contam/HAND_READ_4.text: the other
   12, fresh abstract + trained title): all siblings, different work or different people. Each file states what its calls rest on.
5. Disclosed again: this addendum, like A7 to A9, postdates the output stamp (block 974615). That the outputs are unread is self-witnessed.

Files (sha256):
   a519569f50240f25d5ef7777a97d7f4d2bc008a87147a774269f3d209b3818ac  yf_minus_a10.py
   37e20470f9391f9ef3ee098e48aa457f58d288c12248f5deb506123c2961b2aa  yf_minus_a10_tests.out
   fb191815a1f9f82529d809fdd8df63076327d323d3946f7160cb7af21db91aec  contam/yf_lang.py
   e20b97db9c855b95c827facafe5d60fb2ecd5711bf49e425a0f91b1b84bd4aa2  contam/yf_lang.out
   6c6d36931f2d14a061226eb1ae9cfdb79fae78acb78af583c9ec8e1b3a89e782  contam/yf_translate_match.py
   b12238672d67a1cc877e2477f80c1fb9b46a871fb0d7fb3addcbd92b8787db80  contam/yf_translate_match.out
   e02815ec45f2808062c85df8eb66cabe8e4c463ecafa762fa4959dc60df4fc63  contam/HAND_READ_ABSTRACTS.text
   ad8f83cb74255221ea0a1877b31216acbe639c82084470265b8de4f8f05f15ba  contam/HAND_READ_4.text
