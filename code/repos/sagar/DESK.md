# Astrophysics desk (temporary authorization, Wayfinder 12 Nov 2026)

Name: SAGAR (Wayfinder chose it 12 Nov; Sage signed 12 Nov 20:38), Standards Audit of Gravitational and Astrophysical Research (Wayfinder, 12 Nov). Bones: yes. No astronomy
project uses it. 'Sagar' means ocean, and it nods to Sgr, Sagittarius. Snag: Sagar is a common personal name, so name searches hit
authors, so index by DOI and arXiv id, never by name.

Ask: closer to QIA. Index public astrophysics studies against our standards (Faults and Guards), and see where our recounts and
calibrations add to their knowledge base. Window: from September 2015, when Advanced LIGO's first observing run began (GW150914
was recorded 14 Sep 2015), rolling forward to today.

## Earlier name candidates (Wayfinder's)
- ARA, Astrophysics Research Audit. Collides with the Askaryan Radio Array (ARA), a South Pole neutrino experiment that publishes
  under that name, in this field. Bones: no.
- STARS, Science and Technical Audit of Research and Systems. Collides softly with Smithsonian STARS (Scientists Taking Astronomy to
  Rural Schools, an education program, not research). Bones: usable, the least-bad of the two. Also considered and ruled out: SAGR (Galactic excludes extragalactic GW work), SGR (soft gamma repeaters), SAGA (satellite-galaxy survey), AURA, PARSEC, SEXTANT, PARALLAX (a measurement word inside the papers).

## Well depth
Counts in WELL.md (arXiv API, astro-ph, submitted 1 Sep 2015 to 12 Nov 2026).

## Open for Sage
- Do the seven codes transfer as written? F1 names IBM's stated figures, F7 is a classical comparison. An astro reading of each code
  is needed before any indexing (for example F1 = calibration or injections from the same pipeline, F7 = a simpler model that fits as well).
- Which slice first: gravitational-wave papers on public GWOSC strain are the closest analogue to QIA (public data, recomputable).

## Status 12 Nov evening
NASA ADS is live (Wayfinder's token, kept in a session file, never committed). Slice 1 has 1,042 papers: 1,003 outside and 39 LVK
control. Rules are frozen in RULES.md. Work order is newest first, because recent authors are likeliest to answer. No email is sent
without Wayfinder's word on each send.

## Contact first (Wayfinder, 12 Nov evening)
Only studies whose authors we can reach get indexed. Order: (1) find a working contact per paper, newest first; (2) index the
reachable ones; (3) the email shows the authors their study's page on the site, so they may look around while they're there. Contacts come from ADS (320 of 1,003 outside papers) and then from the first two pages of the arXiv PDF
(contacts/pdf_emails.py). Domains get an MX check before any address counts as reachable. Contacts live in contacts/ (gitignored,
mode 700) and feed the rolodex. Nothing is sent without Wayfinder's word on each send.

## Page format (target, not built yet)
SAGAR study pages mirror QIA's: one six-cell row per study (work and institution as published, study link, their printed value, the
recounted or measured value, the code, how it was checked), feeding build_site.py the way iris_list_body.html feeds /iris/list.
Pages carry the QIA footer: "A classification for indexing, not an assessment", plus correction and removal forms. Only rows in
index/verified.jsonl go on a page, and only after a referee pass. The emails link the study page.
