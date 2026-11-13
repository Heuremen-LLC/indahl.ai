# Row - University of Utah (agent desk row, 25 Oct 2026; Bones recount pending before THE register)
Not an Ivy: no SWEEP_ivies.md section. [v] = quote read from page source fetched with curl (HTML stripped to text by a local
extractor; recheck byte-exact at recount); [p] = PDF text extracted with pypdf from the downloaded file; [oa] = abstract text
rebuilt from the OpenAlex record (word order from the inverted index); [f] = WebFetch summary (paraphrase, NOT a quote; recount).

## Search log (same procedure every school; window 2023 to Oct 2026, English, utah.edu primary)
- WebSearch: 1 query run ("University of Utah generative AI teaching guidance task force report"; pointers: attheu fall-2023
  guidelines, provost ChatGPT message, CTE fall-2023 PDF). Next 2 queries refused: session web-search budget used up.
  SEARCH PASS STILL OWED: institution-run student/faculty AI surveys, Turnitin AI-indicator setting, Academic Senate AI items
  beyond the 3 summaries read, faculty empirical studies (S7) with data links, UBot/Academic Recovery results.
- @theU site search and WordPress search endpoint: Cloudflare 403. Sitemaps: ai.utah.edu/sitemap.xml 404, cte.utah.edu/sitemap.xml
  404, innovationlab.utah.edu/sitemap.xml 404. Pages found by fetching hubs and following links: ai.utah.edu (home, guidelines,
  teach, faq, at-a-glance, about, student guide + 4 subpages, news list, 25 blog posts), cte.utah.edu (home, AI Tools for Education),
  attheu.utah.edu tag/ai pages 1-3 + tag/artificial-intelligence (link list) and 9 articles, innovationlab.utah.edu (our-work,
  UGuide, UBot, Academic Recovery, TEF-Talk), rai.utah.edu (home, teaching-and-learning, annual report page + 2025 PDF, teaching
  awards), regulations.utah.edu Policy 6-410, it.utah.edu 2023/09 AI guidelines post, 3 Academic Senate summaries (Feb 2, Aug 24,
  Sept 28 2026). Bibliographic lookup: OpenAlex works API (institution I223532165, from 2023-01-01, 5 title/abstract queries,
  61 works listed) for S7 candidates.
- (1) committee/task-force report on AI in T&L: NONE FOUND (no provost/senate/task-force report; Sept 2026 AI Use Guidelines
  from the Office of AI is the institutional guidance; Senate summaries read carry AI degree programs only).
  (2) teaching-centre guidance: found (CTE). (3) institution-run survey with n: NONE FOUND at institution level (see S2).
  (4) evaluation of own policy/tools/pilots with outcome: NONE FOUND (see S0). (5) detector stance: found. (6) faculty studies
  with released data: NONE FOUND (candidates in S7, full texts UNREAD).

## UNREAD
- https://cte.utah.edu/instructor-education/ai-fall23-instructional-update/fall-2023-instructional-guidelines-on-generative-ai.pdf (404; same-titled @theU article read).
- https://academic-affairs.utah.edu/ (403 to curl; provost hub not searched).
- https://attheu.utah.edu/?s=... and /wp-json/wp/v2/posts?search=... (Cloudflare 403).
- https://zenodo.org/records/22804230 PDF "Stduents-AI-Use-Fall2025-Rohde-Mao.pdf" (zenodo 403 to curl; file URL 404 to the fetch tool; record page seen only as a fetch summary [f]).
- https://doi.org/10.1016/j.compedu.2025.105314 ; https://doi.org/10.1016/j.compedu.2026.105725 ; https://doi.org/10.1080/15391523.2025.2511313 (closed access; data statements and funding lines not read).
- https://peer.asee.org/60175 (Firth & Wagner, "Integrating an AI-Driven Socratic Tutor into Process Control Education", ASEE 2026; 403).
- https://stage.tlt.utah.edu/ubot/ (members only; not opened) and CTE "AI Course on Canvas" (login; not opened).
- AI Forum slide decks May 28 2025 and Aug 5 2025 (linked from ai.utah.edu posts; not opened). Sept 16 2026 deck read [p].
- https://rai.utah.edu/wp-content/uploads/2024/12/One-U-RAI-Annual-Report-2023–2024.pdf (not opened; 2025 report read [p]).

## Cells
- S0: USAGE-OR-ATTITUDE ONLY (no institution-run outcome measure with n and comparison found); PLANNED ONLY lines logged.
  - UBot (Office of Undergraduate Studies AI tutor, Academic Recovery Project): "UBot was successfully deployed to MATH 1050-003:
    College Algebra in Spring 2024 with overwhelming student support." [v] https://innovationlab.utah.edu/our-work/ubot.php (no n,
    no outcome stated).
  - UGuide pilot: "UGuide is currently being piloted with over 700 students in the Quest program ... Early feedback has been
    overwhelmingly positive" [v] https://ai.utah.edu/blog/posts/2025/ai-community-of-practice-ai-transforms-student-success.php
    (respondent n not stated).
  - Physics & Astronomy department report (Fall 2025 courses): "This quality improvement project has a limited scope by design,
    and this report is not intended to provide generalized conclusions about how AI tools affect student learning." [oa]
    https://doi.org/10.5281/zenodo.22804230
  - Math course (two classes, UBot vs no UBot): "Anecdotally, students who participate appear to have a better grasp of their
    mistakes and the underlying material." [v] https://ai.utah.edu/blog/posts/2026/individualized-math-learning.php
  - PLANNED ONLY: TEF-Talk (AI course-feedback dashboard pilot, launched Fall 2023): "Forthcoming once sessions and analysis are
    complete." [v] https://innovationlab.utah.edu/our-work/teaching-excellence.php ; Academic Recovery Project (hosts UBot): "Once
    impacts are studied, the program will be refined, replicated, and scaled" [v] https://innovationlab.utah.edu/our-work/academic-recovery.php ;
    AI Use Guidelines: "This guidance will be reviewed at least annually" [p] (review, no outcome measure named).
  - Instructor-level, not institutional: grading guidelines ask each instructor to "Conduct a small-scale comparison between human
    grading and AI-assisted grading using a representative sample of assignments." [p] (logged; not an institutional evaluation).
- S1 (public AI-in-learning documents):
  1. 2023-01-28, interim guidance (Provost message), https://attheu.utah.edu/facultystaff/chatgpt-message-from-provost-mitzi-montoya/
     (companion same date: https://attheu.utah.edu/facultystaff/chatgpt-message-to-faculty/). "Please note that this is interim guidance" [v]
  2. 2023-08-02, teaching-centre guidance, "Fall 2023 Instructional Guidelines on generative AI" (CTE director),
     https://attheu.utah.edu/facultystaff/fall-2023-instructional-guidelines-on-generative-ai/
  3. CTE "AI Tools for Education" page (refreshed per AI Office post 2025-07-18; page reads "Last updated January 2026."; footer
     6/2/26), guidance, https://cte.utah.edu/instructor-education/ai-for-teaching.php
  4. CTE "Student Guide to AI Generative Tools" PDF (21 pp; references "Retrieved August 28, 2024"), guidance,
     https://cte.utah.edu/instructor-education/ai-website-content/gen_ai_2024.pdf
  5. 2026-09, policy-level guidance, "Artificial Intelligence Use Guidelines" v1.0 (Office of AI; Section 9 "AI in Teaching and
     Learning"), https://ai.utah.edu/guidelines/9.2026.ai.guidelines.pdf
  6. Undated (listed on guidelines page, footer 9/14/26), "Guidelines for Responsible Use of AI in Grading" (6 pp),
     https://ai.utah.edu/guidelines/guidelines_for_responsible_use_of_ai_in_grading.pdf ; plus "AI-Assisted Grading Syllabus
     Statement" (3 pp), https://ai.utah.edu/guidelines/ai_assisted_grading_syllabus_statement.pdf
  7. Undated, student guidance web guide incl. 5-level acceptable-use scale, https://ai.utah.edu/ai-student-guide/ (+ /acceptable-use.php,
     /guiding-principles.php, /watch-out-for.php, /questions.php); AI Office FAQ https://ai.utah.edu/faq.php
  8. Undated, department statement (Writing and Rhetoric Studies, linked by CTE as sample),
     https://cte.utah.edu/instructor-education/ai-website-content/chatgpt-sample-statment-.pdf
  9. 2026-09-16, department report (Physics & Astronomy, Rohde & Mao), https://doi.org/10.5281/zenodo.22804230 (PDF UNREAD).
  Policy 6-410 (Academic Integrity; "Revision 0", effective August 15, 2023): no AI text found [v] https://regulations.utah.edu/academics/6-410.php
- S2 (evidence cited):
  - CTE page (doc 3): 6 author-year in-text citations, no reference list on the page, peer-review status not checked: "(Das,
    Mutsuddi, & Ray, 2024; Yadav, 2024)", "(Muhie & Woldie, 2019)", "(Asatryan, 2023)", "(Maphalala & Ajani, 2025; Ojha, 2024)" [v].
    Other reports: Cengage 2024 employability survey quoted ("73% of employers use GenAI while more than half (55%) of graduates said
    their program did not prepare them" [v]), WEF Future of Jobs 2025 (link). Other institutions'/blog pages: MIT Sloan "AI detectors
    don't work", MIT Sloan AI-grading post, Society for the Teaching of Psychology article, UCL page, Hechinger, news/podcasts.
  - AI Use Guidelines (doc 5), grading guidelines (doc 6): 0 citations; grading doc acknowledgment "draws in part on earlier
    AI-assisted grading guidelines developed by Himanshu Mishra" [p].
  - Student Guide PDF (doc 4): 4 references (U library guide, CTE site, studentguidetoai.org, OpenAI ChatGPT) [p]; 0 studies.
  - Provost/2023 CTE docs (1, 2): 0 studies; 2023 article points to "EWeek ... chart of the Top 10 AI Detection Tools" [v].
  - Own surveys: none found at institution level. Faculty-presenter session survey (English Language Institute, TESOL Ecuador):
    "Survey data from their session showed moderate concern (average score: 2.72 on a 5-point scale)" [v]
    https://ai.utah.edu/blog/posts/2025/will-ai-replace-the-english-teacher.php (n and response rate not stated; respondents not U students).
- S3: none found (no microdata, instrument or codebook for any institution-run AI pilot or survey). Zenodo record for doc 9 lists
  one PDF file and no data statement [f] (recount).
- S4: CTE page (doc 3), counted by hand: 1 of 41 by proximity (Why AI Matters "Educators must ... lead its integration" follows
  "(Maphalala & Ajani, 2025; Ojha, 2024)"); Quick Tips 0/5 (tip 5 links MIT Sloan page = not counted, same rule as uiowa CRLT blog);
  syllabus + Copilot recommendations 0/2; Course Policies 0/7; Preparing Students 0/4; Designing Assignments 0/6; Grading 0/11
  ("to learn more" links MIT post + STP article = not counted); In-class 0/5. AI Use Guidelines Section 9-9.2: 0 of 16.
  Grading guidelines: 0 citations (n not enumerated). Hand recount pending.
- S5 (stated as fact):
  1. "AI-detection tools have repeatedly proven to be unreliable and inaccurate, often yielding false alarms flagging student work."
     - https://cte.utah.edu/instructor-education/ai-for-teaching.php [v] - linked: MIT Sloan EdTech page (not a study).
  2. "AI technologies power adaptive learning systems that tailor instruction to individual student needs, increasing engagement and
     promoting deeper learning (Das, Mutsuddi, & Ray, 2024; Yadav, 2024)." - same page [v] - cited author-year, no reference list.
  3. "accessing ALTER-Math tends to increase students' learning gains, defined as post-quiz score minus pre-quiz score, by 1.56
     times, Li said." - https://attheu.utah.edu/research/ai-paves-the-way-for-kids-to-learn-math-by-teaching-it/ (2025-03-20) [v] -
     source: faculty statement; "Researchers have quizzed 6,000 of those students" [v]; no paper cited. (K-12, Florida; not U students.)
  4. "a randomized controlled trial that accessed the initially efficacy of the app compared to role plays; which found significant
     improvements pre/post at a rate no different than traditional lecture and role plays" - https://ai.utah.edu/blog/posts/2025/ai-community-of-practice-leveraging-ai-and-vr.php [v] - uncited (no trial link).
  5. "Improved Writing: Students demonstrate stronger writing skills, producing clearer, more structured assignments." -
     https://ai.utah.edu/blog/posts/2025/ai-elevates-learning-nursing-education.php [v] - uncited.
  Not listed (cap 5): "UBot has quickly proven its value" (CTE page, uncited); "Generative AI struggles with nuanced, context-rich
  problems." (CTE page, uncited); Turnitin "It doesn't work for ChatGPT." (@theU 2023-01-26, uncited).
- S6: "AI-detection tools should not be treated as conclusive evidence of academic misconduct. Academic integrity determinations
  should be based on the totality of available evidence ... Instructors should not upload student work to unapproved third-party AI
  detection services." [p] https://ai.utah.edu/guidelines/9.2026.ai.guidelines.pdf (Sept 2026). CTE: "Ditch Detection Tools ...
  They are not on the list of UIT-approved AI tools and could expose FERPA-secured data to significant security risks." [v]
  FAQ: "Microsoft Copilot includes detection features, but the university does not endorse any specific tool due to reliability
  concerns." [v] https://ai.utah.edu/faq.php . 2023 record: "in spring 2023 semester, MBECTE recommended that faculty not rely on
  Turnitin's Originality score ... Faculty are encouraged to explore independent AI detection tools, such as ZeroGPT, or Writer." [v]
  https://attheu.utah.edu/facultystaff/fall-2023-instructional-guidelines-on-generative-ai/ . Current Turnitin AI-indicator setting:
  not found (search owed). No study cited for any detector line (CTE links MIT Sloan page).
- S7: no own-faculty empirical study on AI and learning with released data found (search pass owed). Candidates logged:
  - Rohde, C., Mao, Y.-Y. "How Do Students Use AI Tools in Undergraduate Physics Computing Courses? A Case Study." Zenodo report,
    2026-09-16, https://doi.org/10.5281/zenodo.22804230 . Data link: none found (record lists one PDF [f]). Funding: none listed [f]. PDF UNREAD.
  - ALTER-Math / teachable-agent line (Chenglu Li, Bailing Lyu, Hai Li; Educational Psychology): Computers & Education 2025
    https://doi.org/10.1016/j.compedu.2025.105314 ; JRTE 2025 https://doi.org/10.1080/15391523.2025.2511313 ; Computers & Education
    2026 https://doi.org/10.1016/j.compedu.2026.105725 (all closed, UNREAD; data link not found; funding line not obtained). Project
    funding verbatim (news): "The team is supported by $10 million in funding from leading education philanthropists and
    organizations through the Learning Engineering Virtual Institute." [v] (@theU 2025-03-20). Data claim verbatim: "created three
    robust datasets with tens of thousands of entries, and published two open-source codebases" [v] (no link given).
  - Zhang-Kopf, Li, Gülfidan, Li, Guo, Learning and Individual Differences 2026, https://doi.org/10.1016/j.lindif.2026.103009 :
    "Data analysis from 192 students in the experimental group and 205 students in the business-as-usual instruction group" [oa].
    OpenAlex funders: National Science Foundation, NewSchools Venture Fund, University of Utah -> CARD ONLY (funding line verbatim
    not read).
  - Firth, S., Wagner, D. "Integrating an AI-Driven Socratic Tutor into Process Control Education." ASEE 2026,
    https://doi.org/10.18260/1-2--60175 (UNREAD, 403; data and funding not obtained).
  - VMI (Virtual Motivational Interviewing, Population Health Sciences / social work): RCT mentioned in an AI Office post (S5 #4);
    no paper, data link or funding line found.
- Bones (25 Oct): CTE PDF gen_ai_2024.pdf lists "OpenAI. (2023). ChatGPT (GPT-4) [Large language model]." in its references; no in-text use found in the 21.6k-char text
  (checked for "OpenAI, 2023", "ChatGPT, 2023", "(GPT-4"). Reference entry only -> not counted in P3-17.
