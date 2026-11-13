# Row - American University (agent row, 25 Oct 2026; not yet recounted by Bones)
Not an Ivy: no SWEEP_ivies.md section. Window 2023 to Oct 2026, English, american.edu / edspace.american.edu / kogod.american.edu /
subjectguides.library.american.edu primary pages; news as pointers only.
Access notes: www.american.edu and search.american.edu return a Cloudflare challenge (HTTP 403) to plain HTTP; those pages were read in a
headless browser (Playwright: page load, then same-origin fetch + DOM textContent, verbatim text, no summarizer). edspace.american.edu/cfe/
front-end returned HTTP 504; CFE page text was read from the site's own WordPress REST API (/cfe/wp-json/wp/v2/pages?slug=...), content.rendered,
tag-stripped. kogod.american.edu, edspace /ctrl/ and subjectguides pages read via plain HTTP fetch + tag strip. PDFs/DOCX text-extracted locally
(pypdf / zip XML), no code from the site run. wwwqa.american.edu (a QA mirror; robots.txt "QA - BLOCK ALL") was probed only and not used for any cell.

## Search log (same procedure as every row)
- Session web search: 2 queries ran ("American University generative AI teaching learning task force report provost site:american.edu" -> 0 AU
  hits; "American University CTRL generative AI guidance faculty syllabus Turnitin AI detection" -> pointers to edspace CFE AI page, OAI Fall
  2024 PDF, Cohn Aug 2025 handout). Third query refused: session web-search budget used up. SEARCH PASS STILL OWED (web) for items 1-6.
- Site's own search used instead: search.american.edu Funnelback (collection american~sp-meta, JSON endpoint) via the browser, 30 queries:
  generative AI survey; artificial intelligence task force; AI working group report; AI teaching learning; ChatGPT students study; AI detection
  Turnitin; AI pilot evaluation; AI literacy; faculty survey artificial intelligence; AI Institute; AI faculty fellows; AI research study students
  learning; Kogod AI; AI report provost; AI student survey results; ChatGPT experiment students learning outcomes; randomized AI students; AI
  disclosure form; academic integrity annual report; academic integrity cases AI; Perplexity pilot; AI tutor study; large language model students
  writing study; AI course evaluation outcomes; AI fellows report; generative AI students grades; AI in teaching survey faculty results; Committee
  on Information Services AI; AI policy evaluation; Sine Institute toplines. Plus CFE WordPress REST search (pages+posts, "AI", "artificial",
  "generative": 96 pages listed, AI-relevant ones read).
- (1) provost/faculty-senate/committee/task-force reports: no provost or faculty-senate task-force REPORT on AI in teaching found. Found and read:
  OIT "University Guidance on the Responsible Use of Artificial Intelligence (AI)" + "Responsible Use of AI Principles" + Working Group membership
  PDF ("Responsible Use of AI Working Group Membership (2024-2025)", co-chairs OIT and Computer Science); Provost/Dean of Faculty semester
  "Faculty Resources and Guidance" memos Jan 2024, Aug 2024, Jan 2025, Aug 2025, Jan 2026, Aug 2026 (AI paragraph in each); CFE launch
  announcement 2 Jul 2025 (Deputy Provost); Faculty Senate home page (summary of 9 Sep 2026 meeting: "Updates to the Academic Integrity Code and
  to the document retention policy are underway."). Faculty Senate minutes PDFs 2024-2026 not opened (UNREAD).
- (2) teaching-centre guidance: CFE (successor to CTRL from summer 2025) "Artificial Intelligence Resources" page, Syllabus Guide AI section,
  May Workshops page (Faculty Institute on AI in Teaching & Research), SoTL Faculty Fellows page; CTRL-hosted OAI PDF "AI & Academic Integrity:
  OAI's Fall Guidance 2024" (49 pp, read in full); Elizabeth Cohn "Using Generative AI for Assignments: A Handout for Faculty" (Aug 2025, DOCX on
  edspace afworkshops, read in full); OAI FAQ page; Kogod "Building Trust..." (AI Disclosure Form); Library "Artificial Intelligence and
  Libraries" guide + 5 subpages.
- (3) institution-run surveys with n: Kogod "AI at Kogod: A Three-Year Student Research Report" (4 Aug 2026; 609 responses / 483 analysed, 2024-26,
  read in full). Sine Institute poll (Oct 2025; n=1,214 young Americans 18-34 nationally, not an AU-student survey; press release read, toplines PDF
  UNREAD). CFE announcement mentions "faculty surveys, focus groups" shaping the centre (no AI results, no n). OAI May workshop session on
  "the violations we've seen" (description only; no counts published found).
- (4) evaluation of own policy/tools/pilots with an outcome measure: none found. Read: Kogod podcast transcripts (Sep 2025, Jun 2026), IAAI launch
  (Apr 2025), "AI at Kogod: What They Are Saying" (May 2025), ETS-AU Futurenav Compass pilot release (28 Apr 2026; career tool, no outcome data),
  CAS "Sarah" virtual TA (7 Feb 2024; student quotes only), Library AI Initiatives / working groups (library workflows, not learning).
- (5) detector stance: OIT guidance, CFE AI Resources, OAI Fall 2024 PDF pp18 and 37-39, Cohn handout, magazine Q&A (Steele, Nov 2023).
  Academic Integrity Code PDF (11 pp, last revised 1 Aug 2023, PDF created 13 Mar 2024): 0 hits for "artificial", "generative", "AI", "detect".
- (6) faculty empirical studies with released data: site search (queries above) + CAS AI page + CARSH 2026-27 cohort page + Baker/Steele pages.
  No AU-affiliated empirical study of AI and learning with a data link found. NOT RUN (owed): web search, AU Digital Research Archive, OSF/
  Dataverse/ICPSR "American University" + generative AI, Google Scholar/ERIC author checks (Steele, Cohn, Favero, Alaghmand, Virtu, Lee).

## Cells
- S0 self-evaluation: USAGE-OR-ATTITUDE ONLY.
  (a) Kogod student survey, self-report, 3 cross-sections, no outcome measure, no comparison arm: "609 responses were collected over the three
      years, but a sample size of 483 over the three years was used for most of the data in this report" ... "All data is self-reported."
      Agreement item (1-5): "AI has improved my understanding of course material." 3.75 / 4.41 / 4.19 (2024/2025/2026).
      (https://kogod.american.edu/news/ai-at-kogod-a-three-year-student-research-report)
  Planned-only text:
  (b) Kogod, Angela Virtu (Jun 2026 podcast transcript): "The next major project is AI assessment. We've integrated AI into all our classes, but now
      we need to answer important questions: Is it helping students? Is it hurting students? Can we quantify its impact?"
      (https://kogod.american.edu/news/how-kogods-ai-first-business-school-model-drove-40-enrollment-growth-in-three-years)
  (c) CARSH 2026-27 student cohort project (Alaghmand, Chemistry): "The Effect of AI on General Chemistry Education: Evaluating Improvement of
      Student Learning Outcomes" ... "In this research, we gather more data, get more precise results, and make valid conclusions."
      (https://www.american.edu/cas/carsh/cohort.cfm)
  (d) OIT: "This guidance will be updated over time to reflect changes in the regulatory environment, industry standards, and technology."
      OAI 2024 PDF p38: "We will continue to monitor detection tools".
- S1 documents:
  1. 9 Jan 2024 / 19 Aug 2024 / 8 Jan 2025 / 19 Aug 2025 / 7 Jan 2026 / 21 Aug 2026, Provost "Faculty Resources and Guidance" memos (guidance,
     AI paragraph): https://www.american.edu/provost/communications/january-9-2024.cfm (and august-19-2024, january-8-2025, august-19-2025,
     january-7-2026, august-21-2026 .cfm)
  2. Aug 2024 (PDF created 2024-08-09), OAI "AI & Academic Integrity: OAI's Fall Guidance 2024" (guidance slides, 49 pp):
     https://edspace.american.edu/ctrl/wp-content/uploads/sites/23/2024/08/AI-Academic-Integrity-OAIs-Fall-Guidance-2024.pdf
  3. Undated page; working group "(2024-2025)"; membership PDF created 2026-02-25. OIT "University Guidance on the Responsible Use of Artificial
     Intelligence (AI)" (university guidance): https://www.american.edu/oit/security/responsible-use-of-ai.cfm ; Principles:
     https://www.american.edu/oit/security/responsible-use-of-ai-principles.cfm ; members:
     https://www.american.edu/oit/security/upload/Responsible-Use-of-AI-Working-Group-Members.pdf
  4. Created 2026-02-18, modified 2026-06-01 (WP API), CFE "Artificial Intelligence Resources" (teaching-centre guidance):
     https://edspace.american.edu/cfe/ai-resources/
  5. Modified 2026-08-31 (WP API), CFE Syllabus Guide AI section (guidance): https://edspace.american.edu/cfe/syllabus-guide/
  6. Aug 2025, Cohn "Using Generative AI for Assignments: A Handout for Faculty" (faculty handout, August workshops):
     https://edspace.american.edu/afworkshops/wp-content/uploads/sites/1300/2025/08/AI-handout-Aug-2025-E-Cohn.docx
  7. 27 Aug 2025, Kogod "Building Trust in Higher Education in the Age of Artificial Intelligence" (AI Disclosure Form; school practice):
     https://kogod.american.edu/news/building-trust-in-higher-education-in-the-age-of-artificial-intelligence
  8. 4 Aug 2026, Kogod "AI at Kogod: A Three-Year Student Research Report" (survey report):
     https://kogod.american.edu/news/ai-at-kogod-a-three-year-student-research-report
  9. Undated (page has session list incl. "Lessons Learned from AY23-24"), CFE May Workshops / Faculty Institute on AI (workshop descriptions):
     https://edspace.american.edu/cfe/may-faculty-workshops/
  10. Undated, OAI FAQ (AI paragraph): https://www.american.edu/academics/integrity/faq.cfm
  11. Updated 7 May 2026, Library "Artificial Intelligence and Libraries" guide (working groups Fall 2023 / early 2024; exploratory report
      "completed in May 2024"): https://subjectguides.library.american.edu/lib-ai
  12. 28 Oct 2025, Sine Institute poll release (survey of national sample, not AU students):
      https://www.american.edu/media/news/sine-institute-survey-ai-higher-education-civic-discourse.cfm
  Context (statements, not guidance): IAAI launch 3 Apr 2025 (https://kogod.american.edu/news/kogod-school-of-business-launches-institute-for-applied-artificial-intelligence);
  Kogod podcast transcripts 15 Sep 2025 and 24 Jun 2026 (URLs in S0/S5).
- S2 evidence cited (agent hand count; Bones recount pending):
  - Own surveys: Kogod 2024-26: 609 responses total, 483 analysed; per-year n not printed; response rate not stated (denominator not given;
    "Professors from a range of Kogod core and elective courses posted a link to the survey"). Sine poll: n=1,214 (Generation Lab panel; not AU
    students; response rate not on release page).
  - OIT Guidance + Principles: peer-reviewed 0; other reports 0; no citations.
  - Provost memos: 0 citations.
  - OAI Fall 2024 PDF: peer-reviewed 0. Other: Bertram Gallant (UC San Diego, 2023) guide, credited "Adapted from" on 14 slides; Lance Eaton
    syllabus repository (8 example slides); Leon Furze AI Assessment Scale blog post; Vox video; Ezra Klein Show podcast; book "Teaching with AI".
  - CFE AI Resources: peer-reviewed 0; points to Library FAQs, OAI SharePoint, library toolkits.
  - Cohn handout: studies named with a citation: 1 (Allison & DeRewal 2023; peer-review status not checked); other: Watkins template, Furze et al.
    AI Assessment Scale, WAC Clearinghouse TextGenEd, Harvard MetaLab, Ditch That Textbook, Bertram Gallant, Conrad (critical-ai), Facebook post
    (Cail), CTRL Beat (Favero); own research referred to, not linked ("My research indicates").
  - Kogod "Building Trust": other reports 2 (unnamed source for "31% to 63% in 2024"; "Digital Education Council's 2024 Global AI Student Survey").
  - Kogod three-year report: own survey only.
- S3 data released: AGGREGATES ONLY. Kogod report: percentage tables and item means by year; no counts per cell, no per-year n, no
  microdata, no instrument file (item wordings quoted in the page only). Sine poll: toplines PDF linked (UNREAD, 404); "For full crosstabs,
  please contact the Sine Institute". Microdata: none found.
  Hand check (agent) of Kogod "Which AI language models have you used..." table: Overall column vs year columns -
  MetaAI Overall 5.3% while year values are 1.5/3.6/2.6/2.8/0.0%; Grok Overall 1.9% while year values are 3.0/3.6/5.3/5.6/10.3%;
  Other Overall 2.6% while year values are 1.5/0.0/0.0/0.0/0.0%. An overall share cannot lie outside the range of its subgroup shares;
  these 3 rows do not reconcile as printed. Weekly-usage deltas check: (4.3-17.1)/17.1 = -74.9%, (29.0-6.2)/6.2 = +367.7%, match.
  "Studying for exams" 2024 value printed 1.4% (2025 59.2%, 2026 66.2%) - recorded as printed.
- S4 recommendations naming an evidence item: 1 of 22 (agent count; Bones recount pending).
  OIT Guidelines for Teaching: 0 of 7 (syllabi state policies; recognize literacy needs; be transparent; not solely rely on AI to grade;
  respect student IP; access equity; data/privacy awareness). OAI "5 Things" headings: 0 of 5 (whole deck credited "Adapted from" a UCSD
  guide; no study). CFE "measures can help to prevent AI policy violations": 0 of 7. Provost Aug 2026 AI paragraph: 0 of 2.
  Kogod AI Disclosure Form: 1 of 1 by proximity (introduced after "nearly half of students in the Digital Education Council's 2024 Global AI
  Student Survey say they need clearer guidance"). Cohn handout recommendations not counted (individual faculty handout).
- S5 testable claims (stated as fact):
  1. "Over the past year, I've seen student deliverables improve significantly when they use AI properly." (Casey Evans, Kogod, 15 Sep 2025,
     https://kogod.american.edu/news/how-ai-is-changing-the-way-we-teach-business-education) - uncited.
  2. "It's revolutionized how we teach and how students learn." (David Marchick, 24 Jun 2026, Kogod 40% page URL in S0) - uncited.
  3. "My research indicates that students often use GenAI instead of doing the reading." (Cohn handout, Aug 2025) - cites own research, no link.
  4. "Even the most effective tools still produce false positives" (OAI Fall 2024 PDF p38) - uncited.
  5. "AI detection tools can easily lead to false accusations of plagiarism, especially for weaker writers or students whose first language is not
     English." (Steele, Nov 2023, https://www.american.edu/magazine/article/q-a-ai-in-the-classroom.cfm) - uncited.
  Other statements recorded, not priced: "Now about 90% of our faculty use AI in the classroom." (Marchick, Jun 2026, uncited); "Undergraduate
  enrollment is up 40% over three years." (same); "This policy was effective in that I could evaluate whether students understood the course
  material based on what they submitted." (Cohn, own course, no data); "Kogod's work includes offering more than 40 AI-integrated courses"
  (Apr 2025) vs "They have about 58 courses that have been transformed" (podcast host, Sep 2025).
- S6 AI-detector stance:
  "As of this date, the University does not subscribe to any AI detection tools. Additionally, the Office of Academic Integrity does not accept
  documentation from these tools as proof of a violation" (https://www.american.edu/oit/security/responsible-use-of-ai.cfm).
  "The difficulty of proving AI misuse without a reasonable doubt cannot be overstated. It is why AU's agreement with Turnitin's plagiarism
  software, which can be enabled in Canvas, does not include AI verification tools." (https://edspace.american.edu/cfe/ai-resources/)
  "We don't use detection tools in OAI investigations; detection scores are not used as evidence in cases" ... "OAI has consulted with experts on
  our campus about the value of detection tools" (OAI Fall 2024 PDF p38). Detector record cited on these pages: none linked; the campus expert
  consultation: NONE FOUND as a document. Cohn handout: "AI detectors are very unreliable, AI detectors should not be used."
- S7 own-faculty studies with released data:
  1. "AI at Kogod: A Three-Year Student Research Report" (student author Christina Eid with Caron Martinez, Henry Ho, Gwanhoo Lee; 2024-2026),
     URL in S1.8; data: aggregates on page, no data link. Funding line: none stated on page.
  2. CARSH project "The Effect of AI on General Chemistry Education: Evaluating Improvement of Student Learning Outcomes" (Alaghmand, 2026-27) -
     planned, no results or data. Funding verbatim: "2026-27 Student Cohort Projects and Faculty Mentors Hedayat & Google Student AI Research Award"
     (not government).
  3. Cohn "My research" on reading and GenAI - not linked; data NONE FOUND.
  4. Steele, Computers & Education: Artificial Intelligence paper (quoted on Baker page) - UNREAD; data and funding unchecked.
  No AU-affiliated empirical study of AI and learning with a released dataset found (see search log item 6; web pass owed).

## UNREAD
- https://www.american.edu/sine-institute/upload/10-27-25-Sine-Survey-Toplines.pdf (HTTP 404 on fetch)
- OAI SharePoint slide deck "A Red-Light Green-Light Upgrade Using AI Dispositions..." and OAI handout (AU login), links on CFE AI page
- https://american0.sharepoint.com/sites/AcademicIntegrity/ (OAI Academic Integrity SharePoint; AU login)
- AU Library AI working group reports (Exploratory, May 2024; Experimentation) - summarized on subjectguides pages, report files not located
- Steele, Computers & Education: Artificial Intelligence paper (cited on https://www.american.edu/baker/graduate/articles/faculty-experts-on-ai-in-the-classroom.cfm)
- CTRL Beat Spring 2024, Favero "Blending Human Knowledge With Generative AI" (named in Cohn handout; URL not extracted)
- https://www.american.edu/facultysenate/upload/faculty-senate-minutes-april-1-26.pdf and https://www.american.edu/facultysenate/upload/faculty-senate-minutes-2-4-26.pdf (search hits; not opened)
- https://www.american.edu/about/strategic-plan/upload/phase-1-working-group-submissions.pdf (search hit; not opened)
- https://www.american.edu/student-affairs/upload/dsa-annual-report-2024-2025.pdf (search hit; not opened)
- https://subjectguides.library.american.edu/AI_Toolkit (library instruction toolkit; not opened)
- Kogod AI Disclosure Form document (linked from Building Trust article; not opened)
- https://edspace.american.edu/cfe/ai-resources/ front-end (HTTP 504; content read via WP REST API instead)
