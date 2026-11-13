# Row - Baylor University (Waco TX) (agent desk row, 25 Oct 2026; Bones recount pending before THE register)
Not an Ivy: no SWEEP_ivies.md section. Fetch notes: most *.web.baylor.edu HTML pages (atl, its, provost, honorcode, facultysenate
HTML, ir) return a Cloudflare 403 challenge to curl; they were read through WebFetch (summariser). Quotes marked [WebFetch] came
through the summariser, not raw source: recheck verbatim at recount. libguides.baylor.edu pages, business.baylor.edu/ai and all PDF/DOCX
files (Faculty Senate minutes, Honor Code) were fetched with curl and read as raw text (HTML stripped; PDF text via pypdf; DOCX XML):
those quotes are verbatim from source. Faculty Senate minutes are the Senate's own summaries of what speakers said.

## Search log (same procedure every school; window 2023 to Oct 2026, English, baylor.edu primary)
- WebSearch: ONE query attempted ("Baylor University generative AI teaching learning guidance provost task force", baylor.edu only):
  refused, session search budget used up. ZERO search results used. A SEARCH PASS IS OWED for items (1)-(6), especially (3), (4), (6).
- www.baylor.edu/sitemap.xml: 404. Site search not usable (JS). Link-following from hubs instead:
  ATL home https://atl.web.baylor.edu/ -> AI Resources -> SET page + SET archive -> Teaching with AI Symposium -> 10:10:10 AI Microlearning;
  ITS GenAI hub https://its.web.baylor.edu/ai -> Instructor Guide to Generative AI (all tabs: home, tools, teaching, copyright, resources)
  -> Student Guide to Generative AI (home, howgenaiworks, bestpractices, academicintegrityandcitations) -> OAI "Suggestions for Dealing
  with AI-Produced Assignments" -> Honor Code PDF (rev. 7 Jul 2025) -> Baylor Business AI page -> Baylor Responsible AI (rai.research);
  Provost home -> Provost news list -> Provost Newsletters Jul 2023 and Dec 2025 -> Generative AI Working Group page provost.web.baylor.edu/ai;
  Faculty Senate home -> Motions/Resolutions list (34 titles, none on AI) -> Meeting Minutes current: ALL 18 minutes files Sep 2024 - May 2026
  downloaded and grepped for AI|artificial intelligence|ChatGPT|generative (14 files with hits, all hits read);
  Institutional Research home -> Administered Surveys (10 surveys listed; none on AI).
- Faculty studies (6): OpenAlex API (institution I157394403, from 2023-01-01, title_and_abstract search: "ChatGPT students",
  "generative AI learning", "artificial intelligence education students", "large language model students"; 31 hits listed, 4 candidates
  opened at metadata level) + OpenAlex author-name filter for ATL staff (Herridge, Richmann, Alstot, Carini, Kulesza).
- (1) committee/task-force report: NONE FOUND as a published report. Found: Generative AI Working Group page (members, charge, no report);
  Senate minutes record a Provost "AI Committee" (formed summer 2024), an "AI Task Force", and a Senate ad hoc "AI, Emerging Technologies,
  and Academic Integrity" committee (created 20 Jan 2026; oral report May 2026 in minutes).
  (2) teaching-centre guidance: found (ATL AI Resources; Libraries Instructor/Student Guides; ITS GenAI guidelines).
  (3) institution-run surveys with n: 2 found, n not stated for either (ATL undergraduate survey, SET 27 Feb 2024; faculty AI survey
  closed 6 Feb 2026, results not located).
  (4) evaluation with an outcome measure: NONE FOUND (see S0).
  (5) detector stance: found (S6).
  (6) faculty studies with released data: NONE FOUND (S7); search owed.

## UNREAD
1. https://baylor.app.box.com/s/brx9fvvh28up5njvuitpki0n1a3fy2sg (Recommended Syllabus Statements; Box, JS; ITS page says "Box login required").
2. SET 27 Feb 2024 "Artificial Intelligence: What Do Students Really Think?" recording (video only; survey n would be here):
   https://mediaspace.baylor.edu/media/SET+Spring+2024%E2%80%94Artificial+IntelligenceA+What+Do+Students+Really+ThinkF/1_8vveox8m
3. Faculty AI survey (closed 6 Feb 2026) results - not located on provost, ir, atl or facultysenate pages.
4. https://atl.web.baylor.edu/set-archive - WebFetch read chars 0-100000 of 109367; last 9,367 chars not read.
5. Symposium slides (Google Docs): Gurung https://docs.google.com/document/d/1RL4Pq847VePdpMyPS5rTNiV_hSmJQeN1inZFQ7oLGfI/edit ;
   Cavazos https://docs.google.com/document/d/1Wk1AE4rgmmldqtBWQ8-DoqpPhnxhkgN-TGgqMuBudj8/edit ; Clayton
   https://docs.google.com/document/d/1mSWYn8-fAa4T_CGNfPH40JNv3salUTRxEQL8qbdc8BQ/edit (presenters' affiliations not checked).
6. https://aisel.aisnet.org/context/cais/article/4876/viewcontent/auto_convert.pdf (Alstot et al. PDF) - 403 to curl; landing page read only.
7. https://link.springer.com/article/10.1007/s13278-026-01619-y - 303 to login at WebFetch, curl blocked.
8. Wood et al. 2023 accounting paper full text (https://pure.eur.nl/en/publications/4b4e63da-d144-4e62-9d69-6785ac220eb6) - not opened;
   abstract via OpenAlex only.
9. https://libguides.baylor.edu/students-chatGPT - 404 (target of the guide's "Baylor has disabled Turnitin's AI detector" link).
10. LibAnswers AI FAQs https://libanswers.baylor.edu/search/?t=0&adv=1&topics=AI - results load by JS; not read.
11. https://baylor.ai/?page_id=8 and https://rai.research.baylor.edu/center-responsible-ai-and-governance - not opened.
12. Provost news: https://provost.web.baylor.edu/news/story/2025/integration-graduate-school-and-gpe-carini-appointed-vice-provost-ai-and - not opened.
13. Generative AI Literacy Course (Canvas) https://baylor.instructure.com/enroll/APM47F - not opened.
14. https://sites.google.com/view/scaling-the-ai-mountain-alstot/home (SET 19 Mar 2026 materials) - not opened.

## Cells
- S0: USAGE-OR-ATTITUDE ONLY.
  (a) ATL survey of undergraduates, SET 27 Feb 2024, https://atl.web.baylor.edu/set-archive [WebFetch]: "This session reports on a recent
      survey of Baylor undergraduates"; participants learn "under what conditions students view AI use as cheating". n not stated on page.
  (b) Faculty AI survey, Faculty Senate minutes Feb 2026
      https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2026-08/faculty_senate_february_2026_meeting_minutes.docx :
      "The faculty survey on AI closed on Friday, February 6, and we are looking at those results." (drafting noted Oct 2025 minutes:
      "Currently drafting a faculty survey"). Results not located.
  (c) Attendance count only, Provost Newsletter Dec 2025 https://provost.web.baylor.edu/news/story/2025/provost-newsletter-december-2025
      [WebFetch]: "with 149 total attendees/participants over the two-week event."
  Outcome-type statement with no data source, n or comparison given (not counted as MEASURED): Senate minutes Oct 2025, Provost/EC
  meeting 6 Oct 2025, https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2025-11/Minutes%20October%202025.pdf p.3:
  "Data supports that high AI use students are not as academically successful as other students."
- S1:
  1. 11 Dec 2023 (Provost Update; modified 5 Jan 2024), Office of Academic Integrity guidance "Suggestions for Dealing with Artificial
     Intelligence (AI)-Produced Assignments" - https://honorcode.web.baylor.edu/academic-integrity-office/faculty-resources/suggestions-dealing-artificial-intelligence-ai-produced
  2. Undated, ITS/University "GenAI" hub with guidelines (9 numbered) - https://its.web.baylor.edu/ai
  3. Last updated 8 Oct 2026, Libraries guidance "Instructor Guide to Generative AI" (James, Filgo) - https://libguides.baylor.edu/instructorsguidetogenai
     (tabs /teaching, /copyright, /resources, /tools, /prompting)
  4. Last updated 8 Oct 2026, Libraries guidance "Student Guide to Generative AI" - https://libguides.baylor.edu/studentsguidetogenai
  5. Undated, ATL resource page "AI Resources" - https://atl.web.baylor.edu/resources/ai-resources
  6. Undated, Provost committee page "Baylor Generative AI Working Group" (charge + 16 names; page says "composed of 18 members") -
     https://provost.web.baylor.edu/ai
  7. 10 Jul 2023 Provost Newsletter (AI section) - https://provost.web.baylor.edu/news/story/2023/provost-newsletter-july-2023 ;
     8 Dec 2025 Provost Newsletter (AI section) - https://provost.web.baylor.edu/news/story/2025/provost-newsletter-december-2025
  8. Faculty Senate minutes with AI items, Sep 2024 - May 2026 (14 files), e.g. Sep 2024 (Provost AI Committee charge)
     https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2024-10/Minutes%20September%202024.pdf ; Jan 2026 (ad hoc
     committee created) https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2026-08/january_faculty_senate_minutes_1-20-26.pdf ;
     May 2026 (ad hoc committee report) https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2026-09/senate_may_2026_minutes_0.docx
  9. Events: ATL Teaching with AI Symposium (2 Oct 2026) https://atl.web.baylor.edu/special-events/teaching-ai-symposium ; 10:10:10 AI
     Microlearning (13-24 Apr 2026) https://atl.web.baylor.edu/special-events/101010-ai-microlearning
  10. Undated, Hankamer School of Business "AI Partnership" page - https://business.baylor.edu/ai/ (FAQ answer is placeholder text
      "Lorem ipsum dolor sit amet, consectetur adipisicing elit.")
  Honor Code (rev. 7 Jul 2025) https://risk.web.baylor.edu/sites/g/files/ecbvkj1966/files/2025-07/Honor%20Code.pdf : no AI text
  (grep AI|artificial|generative: 0 hits); clause used for AI is "Offering for course credit as one's own work, in whole or in part, the
  work of another."
- S2:
  Doc 3 (Instructor Guide; Teaching + Academic Integrity tabs, counted): peer-reviewed 2 (Long & Magerko 2020 CHI; Lo 2023 J. Academic
  Librarianship 49(4) 102720); preprint 1 (Liang et al. 2023, https://arxiv.org/abs/2304.02819v2); SSRN working papers 2 (Mollick &
  Mollick 2023 x2); other institution 1 (King's College London 2024 PAIR guidance); own policy documents 3 (Honor Code; OAI students page;
  OAI suggestions page). Own survey: none. Resources tab = reading list (not counted per claim; includes Perkins et al. 2024 AIAS, JUTLP).
  Doc 1 (OAI, Dec 2023) [WebFetch]: no studies or data cited; links to articles, newsletters, videos.
  Doc 2 (ITS hub): none cited (links to guides and external resources).
  Doc 4 (Student Guide; home + 3 tabs read): detector section cites no study; example citations are illustrations.
  Doc 8 (Senate minutes): speakers' figures with no source named, e.g. Oct 2025 p.3 "Presented Data that over 75% of companies have an AI
  requirement and over 86% of entry level business processes will be eliminated by 2030." Own surveys: 2 named, n and response rate not stated.
- S3: NONE. No microdata, aggregates, instrument or codebook found for the Feb 2024 undergraduate survey or the Feb 2026 faculty survey.
- S4: Doc 3 (Instructor Guide, Teaching + Academic Integrity tabs): 5 of 12 recommendations name a source item (detectors "don't rely on
  them" -> Liang et al. 2023; CLEAR prompting -> Lo 2023; PAIR -> KCL 2024; seven roles -> Mollick & Mollick 2023 SSRN; prompt appendix ->
  Mollick & Mollick 2023 SSRN); 7 name none (pedagogy-not-plagiarism shift; scaffolding; consult liaison librarian; choose one of three
  syllabus templates; output-evaluation checklist; invest in assignment design; clarify expectations in syllabus). Of the 5, peer-reviewed: 1 (Lo 2023).
  Doc 2 (ITS 9 guidelines): 0 of 9. Doc 1 (OAI suggestions): 0 named [WebFetch: "The page cites no studies or data."].
- S5 (stated-as-fact claims about AI and learning; up to 5):
  1. "Data supports that high AI use students are not as academically successful as other students." - Senate minutes Oct 2025 p.3
     (Vice Provost Carini at Provost/EC meeting 6 Oct 2025) - uncited (data not identified).
  2. "Students – 96% - of them use AI." - Senate minutes Feb 2026 (Carini) - uncited.
  3. "Students feel more distance from us when they are using AI." - Senate minutes Feb 2026 (Carini) - uncited.
  4. "breaking the work into stages with reflection built in reinforces original thinking and reduces the perceived need to reach for an AI
     shortcut." - https://libguides.baylor.edu/instructorsguidetogenai/teaching - uncited.
  5. "In many teaching situations, generative artificial intelligence can enhance learning." - SET Fall 2024 "AI-Conscious Teaching"
     description, https://atl.web.baylor.edu/set-archive [WebFetch] - uncited.
  Also on record (not counted): "Using AI to think for you — even when permitted — undercuts the learning the assignment is designed to
  produce." (https://libguides.baylor.edu/studentsguidetogenai/academicintegrityandcitations, uncited); "They are particularly prone to
  flagging writing by non-native English speakers as AI-generated — a bias documented by Liang et al. (2023)" (Instructor Guide /copyright, cited);
  May 2026 minutes, Dr. Argueta (Honor Council): "academic dishonesty is growing exponentially" (uncited).
- S6:
  OAI, Dec 2023 [WebFetch]: "allow the AI detection feature within Turnitin.com to expire at the end of December 2023." and "Too much
  uncertainty exists, much of it related to accuracy, for the University to retain the feature at this time."
  Instructor Guide https://libguides.baylor.edu/instructorsguidetogenai/copyright : "The short version: don't rely on them. AI detectors
  remain unreliable" ... "Baylor has disabled Turnitin's AI detector for this reason".
  Student Guide /academicintegrityandcitations: "Baylor allowed its Turnitin AI detection feature to expire at the end of 2023 due to accuracy
  concerns" ... "No AI detection score alone constitutes proof of a violation."
  Senate minutes Nov 2025 p.9 https://facultysenate.web.baylor.edu/sites/g/files/ecbvkj1731/files/2025-12/Minutes%20November%202025.pdf :
  "administration who indicated that AI detectors are not generally sufficient evidence to support or prove a claim of cheating."
  Senate minutes May 2026 (ad hoc AI committee): "No anti-cheating software is perfect."
- S7: NONE FOUND with released data. Candidates logged (OpenAlex, Baylor-affiliated author):
  1. Wood et al. (326 authors; Baylor: Lauren Farish, Jason E. MacGregor), "The ChatGPT Artificial Intelligence Chatbot: How Well Does It
     Answer Accounting Assessment Questions?", Issues in Accounting Education 2023, https://doi.org/10.2308/issues-2023-013 - empirical
     (abstract: "we compare ChatGPT and student performance for 28,085 questions"); measures AI performance, not student learning;
     data link and funding line UNREAD (UNREAD 8).
  2. Alstot (Baylor), Goldberg, Sobo, Hauze (San Diego State), "A Sociomaterial View of AI Diffusion in Higher Education...", CAIS v58
     (2026, in press), https://aisel.aisnet.org/cais/vol58/iss1/113 - survey n = 12,166 + 16 interviews [WebFetch]; sampled institution
     not stated on landing page; data availability and funding not shown; PDF UNREAD (UNREAD 6).
  3. Spitsberg, Kettler, McKamie (Baylor), "Large language model AI-guided creative writing co-creation in secondary schools", Theory Into
     Practice 2025, https://doi.org/10.1080/00405841.2025.2528551 - abstract: "Our proposed adapted model of creative writing intervention"
     (model, no study data in abstract); K-12, university-authored.
  4. "Exploring public discourse on artificial intelligence for teaching and learning: a social-computational mixed-methods analysis",
     Social Network Analysis and Mining 2026, https://doi.org/10.1007/s13278-026-01619-y - Baylor author per OpenAlex (Min Liu),
     affiliation unconfirmed; page UNREAD (UNREAD 7).
  Funding lines: none read (OpenAlex grants field empty for all 4; not a substitute for the paper's own line). Search owed.
- Search pass (Bones, 25 Oct ~12:55), "Baylor University students AI use academic success data faculty senate 2025": no source for the Senate-minutes
  line "Data supports that high AI use students are not as academically successful"; found only the 2024 committee (Lariat) and the ATL
  undergraduate-survey session listing (mediaspace, no figures). Line stays uncited, S0 unchanged.
