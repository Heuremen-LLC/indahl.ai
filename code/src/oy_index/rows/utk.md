# Row - University of Tennessee, Knoxville (agent desk row, 25 Oct 2026; Bones recount pending before THE register)
Not an Ivy: no SWEEP_ivies.md section. Quotes marked [v] were read from page source fetched with curl (HTML stripped to text by a
local extractor; recheck byte-exact at recount); [p] = PDF text extracted with pypdf from the downloaded file (page given);
[w] = read through the WebFetch tool (summarised reader; short quotes only; recheck byte-exact at recount).
Public UT System Board policy BT0035 is included as a document that governs the campus (system-wide policy of the university's own
board); no government document is entered.

## Search log (same procedure every school; window 2023 to Oct 2026, English, utk.edu primary)
- WebSearch: 2 queries run ("University of Tennessee Knoxville generative AI task force report teaching learning site:utk.edu";
  "UTK survey students faculty generative AI respondents results"); then the session's shared web-search budget ran out (next 2
  queries refused: Turnitin AI detection at UTK; UTK student/faculty AI survey). SEARCH PASS STILL OWED: institution-run student or
  faculty AI surveys (OIRA, Student Government, OIT), GenAI Faculty Fellows outcomes, Canvas AI-tools pilot results, the 2026 AI
  consultant report, Turnitin AI-indicator status, faculty empirical studies (S7) beyond the OpenAlex pass below. No archive or
  third-party reader services used.
- Arxiv 2304.14415 ("Generative AI Perceptions", n = 243 + 813) surfaced in search; authors per arXiv API (Amani, White, Balart,
  Arora, Shryock, Brumbelow, Watson) are not UTK; not entered.
- Hub pages fetched and links followed: provost.utk.edu (provost-initiatives/ai-information; 2026/03/02 coming-soon-ut-ai-hub [w];
  page-sitemap.xml [w]: no other AI page listed); teaching.utk.edu (generative-artificial-intelligence, teaching-with-gen-ai-utk,
  genai-i-have-my-doubts, try-something-out, update-revise-and-redesign-gen-ai, critical-literacies-framework, genai-in-your-class,
  student-centered-approach-plagiarism, ai-me [w], 2025/09/18 sept-ai-faculty-innovator [w], 2026/01/23 tli-advice-for-faculty [w],
  concurrent-session-iii [w]); page dates from teaching.utk.edu/wp-json/wp/v2/pages; oit.utk.edu/ai (home; teaching-and-learning-
  with-ai + 4 subpages; instructional/assessment-academic-integrity; teachingtools/turnitin-similarity; news: Claude watermarking,
  new-ai-features-within-canvas [w]; hpsc AI symposium abstracts 22 Sep 2023; annual report 2025-26 strategic initiatives);
  writingcenter.utk.edu/ai-tools-and-writing-assignments-instructor-resources (full); policy.tennessee.edu BT0035 (full);
  senate.utk.edu (home [w], senatemeetings [w]; 14 PDFs downloaded and searched for AI/artificial/generative/ChatGPT/detect:
  FS minutes 09.16.2024, 11.18.2024, 02.03.2025, 03.03.2025, 04.07.2025, 05.05.2025, 09.22.2025, 10.20.2025, 11.17.2025, 03.02.2026;
  FS agendas 04.06.2026, 05.04.2026, 09.21.2026; FS Achievements 2026); studentlife.utk.edu/studentconduct (home + academic-integrity
  [w]); libguides.utk.edu/Generative-AI (home, ai-ut [w]); cecs.utk.edu/futurenav-pilot; www.utk.edu/news search "generative AI" [w].
- Site search used: WordPress search API (/wp-json/wp/v2/search) on oit, teaching, provost, senate, cecs for "AI detection",
  "turnitin", "survey AI", "generative AI" (news, studentconduct, writingcenter returned non-JSON); then Cloudflare began refusing
  curl on utk.edu wp-json (provost media library search not completed; logged as owed).
- Faculty studies: OpenAlex API, institution I75027704, from 2023-01-01, title_and_abstract search "ChatGPT students" (13),
  "generative AI learning" (30, top 25 listed), "generative AI course" (6), "large language model students" (9). Two arXiv candidates
  read in full (PDF); others listed by title only (OpenAlex per-work lookups then failed).
- (1) committee/task-force report: committees listed (Jan 2023 steering + 4 faculty committees; Jan 2024 student committee); NO
  report document found (2023 provost AI pages 404). (2) teaching-centre guidance: FOUND (TLI, OIT, Writing Center). (3)
  institution-run survey with n: NONE FOUND. (4) evaluation of own policy/tools/pilots with outcome: see S0. (5) detector stance:
  FOUND. (6) faculty empirical studies with released data: NONE FOUND (two with data "on reasonable request" / no statement).

- Receipt check (25 Oct): 16 [v] quotes matched against the cached fetched pages (all PASS). check_receipts.py live run: 10 pairs FAIL
  (pairs were page titles/URL fragments, and utk.edu Cloudflare was refusing curl at the time); rerun at recount.

## UNREAD
- https://provost.utk.edu/emergence-of-ai-tools-in-higher-education/ (HTTP 404; cited by 2023 listening-session deck in search result).
- https://provost.utk.edu/emergence-of-ai-tools-in-higher-education/suggested-syllabus-statements/ (HTTP 404; linked from Writing Center page).
- https://provost.utk.edu/wp-content/uploads/sites/10/2023/04/ChatGPT-Taskforce-Listening-Session-3-FINAL-3.9.2023.pdf (HTTP 404; search result).
- https://cecs.utk.edu/aiut-igniting-the-future-of-learning/ (HTTP 404; linked from provost AI page).
- https://libguides.utk.edu/Generative-AI/research-news (HTTP 404; search result).
- https://liveutk.sharepoint.com/sites/TeachWithGenaiatUTK (UT login; campus GenAI teaching hub).
- https://liveutk.sharepoint.com/sites/provost/SitePages/Generative-artificial-intelligence-(GenAI)-faculty-fellowship-program.aspx (UT login).
- https://liveutk.sharepoint.com/sites/tli/SitePages/Critical-Technology-Resilient-Literacies-(CTRL)-Framework.aspx and .../General%20Recommendations%20for%20Teaching%20with%20GenAI.aspx (UT login).
- https://liveutk.sharepoint.com/sites/faculty-senate/ (UT login).
- AI consultant assessment report, "a report is expected by mid-March" (FS minutes 03.02.2026 [p p.4]); no URL found.
- Faculty Senate: Executive Council agendas/minutes 2024-2026 (not opened); FS minutes 10.21.2024 (.docx), FS agendas other than the 3 listed (not opened).
- https://writingcenter.utk.edu/ai-tools-and-writing-information-for-students/ (not opened).
- https://oit.utk.edu/ai/ai-matrix/ ; https://oit.utk.edu/ai/frequently-asked-questions-about-ai/ ; https://oit.utk.edu/news/generative-ai/ (not opened).
- https://teaching.utk.edu/debating-gen-ai-ethics/ , /environmental-impact-of-gen-ai/ , /was-gen-ai-designed-ethically/ , /starter-questions-to-what-extent-will-genai-benefit-or-harm-our-society-and-culture/ (not opened).
- Student Code of Conduct PDF (linked from studentlife.utk.edu/studentconduct/; not opened) and catalog Honor Statement https://catalog.utk.edu/content.php?catoid=43&navoid=8257#hono_stat (catalog search returned empty).
- OpenAlex candidates not opened: doi 10.18260/1-2--44826 ; 10.18260/1-2--44819 ; 10.1016/j.jslw.2024.101130 ; 10.46328/ijtes.648 ; 10.1016/j.compcom.2024.102896 ; 10.1111/bjet.70038.
UNREAD count: 16.

## Cells
- S0: PLANNED ONLY (no institution-run outcome evaluation found; faculty course-level pre/post studies flagged for Bones to rule).
  - Canvas AI tools (Smart Search, Note Tool, Khanmigo): "To ensure these tools meet instructional needs, they will be tested by faculty
    before full implementation. Dan Harder's office is coordinating a pilot program for these features" [p p.8-9]
    http://senate.utk.edu/wp-content/uploads/sites/16/2025/01/FacultySenate_Minutes_11.18.2024.pdf ; same minutes: "A timeline has not
    been established yet." [p]. OIT announcement 19 Sep 2025 reports no pilot results [w] https://oit.utk.edu/news/new-ai-features-within-canvas/
  - AI needs assessment: "A consultant completed an assessment, and a report is expected by mid-March." [p p.4]
    http://senate.utk.edu/wp-content/uploads/sites/16/2026/04/FacultySenate_Minutes_03.02.2026_approved.pdf (report not found; needs
    assessment, not an outcome measure).
  - CECS Futurenav pilot (ETS career platform, CECS 101): "As a pilot, we will assess how students use the tool, learn from that experience,
    and share the results." [v] https://cecs.utk.edu/futurenav-pilot/ (usage, not a learning outcome; results not found).
  - UT System BT0035 oversight: "The Office of Institutional Compliance shall prepare reports regarding the implementation and ongoing
    compliance with this policy as may be requested by the Audit and Compliance Committee." [v]
    https://policy.tennessee.edu/policy/bt0035-policy-on-artificial-intelligence/ (compliance reporting, no outcome measure).
  - Flagged (faculty research on own courses, not an institutional evaluation): Zahra, He, Bowers, Wang, arXiv 2609.38029 (29 Sep 2026):
    "ChatGPT was used as a thinking partner in an undergraduate research methods and statistics course during Spring 2025 (N = 14)" and
    "Pre-post tests showed gains on every AASCDM dimension and on eight of nine MAILS dimensions, while WGCTA percentiles did not
    change." [p p.2] https://arxiv.org/abs/2609.38029 . Zahra, Wang, Harper, He, arXiv 2609.37880: "A total of 26 enrolled across the two
    courses, and 20 consented to research use" [p]; "AI literacy increased, concentrating in understanding AI, whereas critical thinking,
    awareness, and knowledge did not change." [p p.2] https://arxiv.org/abs/2609.37880
- S1:
  1. Jan 2023 (committees) / Jan 2024 (student committee), undated page, provost initiative page with committee rosters "AI in Higher
     Education" - https://provost.utk.edu/provost-initiatives/ai-information/ ("These committees were established in January 2023 to
     provide guidance to the Vice Provost regarding the integration of AI technologies across campus." [v]). No committee report found.
  2. 15 Mar 2023, modified 16 Apr 2026, Writing Center guidance "AI Tools and Writing Assignments: Instructor Resources" -
     https://writingcenter.utk.edu/ai-tools-and-writing-assignments-instructor-resources/ (dates from page JSON-LD).
  3. 22 Sep 2023, OIT symposium "AI in Higher Ed: Transforming the Teaching and Learning Experience" (abstracts) -
     https://oit.utk.edu/hpsc/abstracts-ai-in-higher-education-symposium/
  4. 28 Feb 2025, UT System Board policy "BT0035 - Policy on Artificial Intelligence" -
     https://policy.tennessee.edu/policy/bt0035-policy-on-artificial-intelligence/ ("Effective Date: 02/28/2025" [v]).
  5. Undated (current), OIT guidance hub "Artificial Intelligence" + "Teaching and Learning with AI" (4 subpages) - https://oit.utk.edu/ai/ ;
     https://oit.utk.edu/ai/teaching-and-learning-with-ai/
  6. 4 Nov 2024 (modified 10 Nov 2025), TLI hub "Generative Artificial Intelligence" - https://teaching.utk.edu/generative-artificial-intelligence/
  7. 13 Aug 2025 (modified 17 Aug 2026), TLI guidance "Teaching with Generative Artificial Intelligence" - https://teaching.utk.edu/teaching-with-gen-ai-utk/
  8. 18 Aug 2025 (modified 17 Aug 2026), TLI framework "Critical Technology Resilient Literacies (CTRL) Framework" - https://teaching.utk.edu/critical-literacies-framework/
  9. Jul 2026, TLI guidance set: "GenAI: I have my doubts" (6 Jul, mod. 17 Aug 2026), "I just want to try something out" (7 Jul), "I'm ready to
     update, revise, and redesign" (10 Jul), "What does GenAI do in your class?" (8 Jul) - https://teaching.utk.edu/genai-i-have-my-doubts/ ;
     https://teaching.utk.edu/try-something-out/ ; https://teaching.utk.edu/update-revise-and-redesign-gen-ai/ ; https://teaching.utk.edu/genai-in-your-class/
  10. Faculty Senate minutes with AI items: 18 Nov 2024 (Canvas AI tools, approved minutes 03 Feb 2025), 17 Nov 2025, 02 Mar 2026; spring 2026
     roundtables "AI In the Classroom (Student Success + Faculty Senate)" [p] (agenda 04.06.2026).
  11. Undated (2026), provost announcement "Coming soon: UT AI Hub" - https://provost.utk.edu/2026/03/02/coming-soon-ut-ai-hub/ [w]
- S2 (counted by hand from page text; recount pending):
  - TLI "Teaching with Generative Artificial Intelligence" (doc 7): 10 author-year in-text citations, no reference list and no links on the
    page (raw HTML checked): Mowreader 2024; Cardona et al. 2023; Byrd et al. 2023; Hutson et al. 2024; Gebru & Torres 2024; Metz 2024;
    Doshi & Hauser 2024; Darvishi et al. 2024; Crawford et al. 2024; framework sources Gupta et al. 2024, Selber 2004, Kellner & Share 2005.
    Peer-review status not determinable from the page (identification owed at recount). Own surveys: none.
  - TLI "try something out" (doc 9): "we have evidence that it may shortchange them on their learning (Darvishi et al., 2024) and may have
    long term emotional consequences (Crawford et al., 2024)." [v] (author-year only).
  - Writing Center (doc 2): preprints linked 2 - Sadasivan et al. 2023 (https://doi.org/10.48550/arXiv.2303.11156), Liang et al. 2023
    (https://doi.org/10.48550/arXiv.2304.02819); peer-reviewed linked 1 - Fyfe, "How to cheat on your final paper" (https://doi.org/10.1007/s00146-022-01397-z);
    Eodice et al. 2017 (Google Drive PDF); other reports: MLA-CCCC Joint Task Force Working Paper; Dobrin, Talking about Generative AI;
    Harvard AI Pedagogy Project; opinion/other: Mollick post, John Nash LinkedIn post, Warner (Inside Higher Ed, 19 Jul 2023), Krause blog,
    Cornell and Vanderbilt teaching-centre pages. Own surveys: none.
  - OIT teaching pages (doc 5): no citations to studies; resources list Bowen & Watson (book) and "101 Creative Ideas on Using AI in
    Education" (https://zenodo.org/records/8072950). Own surveys: none.
  - BT0035 (doc 4): legal sources only ("Pursuant to Tennessee Public Chapter 550 (2024)" [v]); no studies, no data.
  - Faculty Senate minutes: "Reports continue to come in from faculty and students regarding AI" [p p.2] (FS minutes 11.17.2025; no n, no instrument).
- S3: NONE FOUND (no microdata, aggregates, instrument or codebook released by the institution; no institution-run AI survey found).
- S4 (hand count, recount pending; a "see/resource" line is not counted as a recommendation):
  - Writing Center instructor page (doc 2): 4 of 25 name an evidence item. All-faculty list 1 of 6 ("Don't rely on AI detectors ...
    Sadasivan et al. (2023)"); allowing-faculty list 3 of 19 (foreground value of writing: MLA-CCCC working paper p.4; meaningful
    writing: "Eodice et al., 2017"; detectors: "Sadasivan et al. (2023) ... Liang et al., (2023)"). Not counted as evidence: John Nash
    LinkedIn post (model), Warner column (opinion), Provost syllabus statements (policy).
  - TLI "Teaching with GenAI" (doc 7): 1 of 4 ("You should assume that GenAI software can do anything you might assign your students.
    That means we all need to update how we teach (Cardona et al., 2023; Byrd et al., 2023)" [v]); none: engage + critical thinking;
    "We need AL-aware teaching practices" [v, spelling as printed]; "We need critical literacy" [v].
  - TLI "I have my doubts" prohibition section (doc 9): 0 of 5 (role-based framing; AI assessment scale "Furze et al. (2026)" = a scale/model;
    assignment icons; course culture; detection tools with caution - no citation).
  - TLI "try something out" (doc 9): 1 of 6 (bridge-to-people perspective cites Darvishi et al. 2024; Crawford et al. 2024).
  - OIT "Guidance on AI Adoption" (doc 5): 0 of 10 (engage as it evolves; journey; safe environment; assistive tool; baby steps; neurodiversity;
    building trust; process over product; collaborative environment; AI Acknowledgment Worksheet) - no citations on page.
  - BT0035 (doc 4): 0 of 4 operative requirements (communicate permitted uses; students adhere; unpermitted use = misconduct; detector rule).
- S5 (stated as fact):
  1. "AI output text is known to include made-up information that sounds very plausible." - Writing Center [v]
     https://writingcenter.utk.edu/ai-tools-and-writing-assignments-instructor-resources/ - uncited.
  2. "Studies and anecdotal reports suggest that most students will use AI to help them get started on projects, develop or expand parts
     of projects (e.g., find additional supporting resources), and improve an existing draft." - Writing Center [v] - uncited (no study named).
  3. "In general, detection tools have shown only limited utility, as they frequently generate false negatives ... and false positives
     (misidentifying student work, especially when edited with Grammarly, as whole-cloth AI creations)." - TLI [v]
     https://teaching.utk.edu/genai-i-have-my-doubts/ - uncited.
  4. "Artificial intelligence in teaching and learning offers transformative tools such as personalized learning experiences, automated
     grading systems, and intelligent tutoring, significantly enhancing educational outcomes." - OIT [v]
     https://oit.utk.edu/ai/teaching-and-learning-with-ai/ - uncited.
  5. "GenAI can't connect people with other people, we have evidence that it may shortchange them on their learning (Darvishi et al., 2024)"
     - TLI [v] https://teaching.utk.edu/try-something-out/ - cited author-year (Darvishi et al., 2024), no reference list on page.
- S6:
  - Campus (Writing Center, Aug 2023 note): "At this time, we do not recommend relying on AI detectors to make academic integrity decisions." [v];
    "Don't rely on AI detectors to draw conclusions about AI use or make academic integrity decisions." [v]
    https://writingcenter.utk.edu/ai-tools-and-writing-assignments-instructor-resources/ (cites Sadasivan et al. 2023; Liang et al. 2023).
  - Campus (TLI, Jul-Aug 2026): "Use Detection Tools with Caution: In general, detection tools have shown only limited utility" [v]; "A
    detection tool can suggest an area of concern, but it's up to you and your students to clarify expectations and set up ways for students
    to "show their work."" [v] https://teaching.utk.edu/genai-i-have-my-doubts/
  - UT System (BT0035, 28 Feb 2025): "under no circumstances shall the results of AI detection tools be the single measure for determining
    the academic performance of or misconduct by a Student." [v] https://policy.tennessee.edu/policy/bt0035-policy-on-artificial-intelligence/
  - Turnitin: OIT pages describe Similarity only; no AI-indicator status found [v] https://oit.utk.edu/teachingtools/turnitin-similarity/
    (search owed).
- S7: no own-faculty empirical study on AI and learning with released data found (search pass owed). Candidates logged:
  - Zahra, F. T.; He, J.; Bowers, D. M.; Wang, W. "Critical Thinking with Generative AI: A Constraint-First Design Pilot of a Thinking-Partner
    Intervention." arXiv 2609.38029 (2026), https://arxiv.org/abs/2609.38029 ; data: "The de-identified interaction log corpus and analysis
    code that support the findings of this study are available from the corresponding author on reasonable request" [p] (not released);
    funding line: none found in text.
  - Zahra, F. T.; Wang, W.; Harper, F.; He, J. "Fluency Without Evidence: Constraint-First Design and the Limits of Self-Report in AI-Assisted
    Learning." arXiv 2609.37880 (2026), https://arxiv.org/abs/2609.37880 ; data statement: none found; funding line: none found.
  - Listed by OpenAlex (UTK affiliation), not opened: "Full Paper: Exploring the Impact of ChatGPT on a First-Year Engineering Design Course"
    (ASEE 2024, doi 10.18260/1-2--44826); "Engineering Education after ChatGPT" (ASEE 2024, doi 10.18260/1-2--44819); "Graduate students'
    use of ChatGPT for academic text revision" (JSLW 2024, doi 10.1016/j.jslw.2024.101130); "Multimodal composing with generative AI"
    (Computers and Composition 2024, doi 10.1016/j.compcom.2024.102896); "Unveiling interaction patterns between students and generative AI
    teachable agent" (BJET 2026, doi 10.1111/bjet.70038); "Reflections on the Merit and Perils of AI in Higher Education" (IJTES 2025,
    doi 10.46328/ijtes.648). Data links and funding lines not obtained.
  - OIT symposium 2023 abstract: "This presentation will discuss an AI in Education project funded by the National Science Foundation." [v]
    (presenter Antonenko; affiliation not stated as UTK) -> CARD ONLY if entered (government grant).

## Bones check (25 Oct): Zahra et al., arXiv 2609.38029 (abstract via arXiv API)
- Design-Based Research pilot, one course, Spring 2025, N = 14, pre/post only (no comparison arm) -> not a counted pilot under the S0 rule.
  Abstract: gains on every AASCDM dimension and eight of nine MAILS (self-reported AI literacy) dimensions, "while WGCTA percentiles did not
  change" (standardized critical thinking). Data statement in the row (interaction log corpus) - verify at recount.
