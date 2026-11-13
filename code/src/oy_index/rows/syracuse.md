# Row - Syracuse University (agent desk row, 25 Oct 2026; Bones recount pending before THE register)
Not an Ivy: no SWEEP_ivies.md section. Quotes checked against page text pulled with curl (HTML stripped); WordPress sites (news.syr.edu,
teachingexcellence.syr.edu) read through each site's own wp-json API (dates = API date/modified); CTLE annual-report PDFs via pypdf.

## Search log (same procedure every school; window 2023 to Oct 2026, English, syr.edu / syracuse.edu primary)
- WebSearch: 1 query tried ("Syracuse University generative AI teaching learning guidance provost task force report") - refused, session
  web-search budget used up. 0 queries ran. SEARCH PASS STILL OWED for all six items, especially (3) surveys with n and (6) faculty studies.
  OpenAlex API also refused (daily budget) - faculty-study sweep by affiliation NOT run.
- Hubs walked: www.syracuse.edu/sitemap.xml (grepped ai/artificial/generative/chatgpt/provost/teach); www.syracuse.edu/academics/ai/;
  www.syracuse.edu/stories/ai-in-education/; ai.syracuse.edu (ITS AI hub: llms.txt index, home, academics, students, responsible-ai,
  ai-guidelines, academic-integrity, ai-tools, claude, agentic-os, support, privacy, stories index + 5 stories); its.syr.edu/artificialintelligence/,
  its.syr.edu/aiforstudents/; teachingexcellence.syr.edu (CTLE + Academic Integrity Office; wp-json search "AI", 60 hits listed, 20 opened incl.
  8 "Beyond AIO Policy" newsletters; 2 annual-report PDFs); policies.syr.edu Academic Integrity Policy; su-jsm.atlassian.net Online Learning
  Services KB "Detecting AI Created Content"; senate.syracuse.edu (home, links; wp-json search "artificial" returned []); effectiveness.syr.edu
  (home, survey-resources: no AI hits); news.syr.edu (wp-json search, 19 queries, ~400 hits listed, 16 posts opened).
  Hosts that did not resolve: ctle.syr.edu, provost.syr.edu, senate.syr.edu (redirect host senate.syracuse.edu used). class.syr.edu renders by script.
- (1) committee/task-force reports on AI in teaching: NONE FOUND (no provost/senate AI task-force report located; CTLE-CLASS "Informal Faculty
  Working Group" credited on a CTLE page; Data Governance Committee reviews the ITS AI guidelines). (2) teaching-centre guidance: found (CTLE).
  (3) institution-run surveys with n: NONE FOUND with AI results (usage counts only, see S0). (4) evaluation of own policy/tools/pilots with
  outcome measure: NONE FOUND. (5) detector stance: found. (6) faculty studies with released data: NONE FOUND in pages walked (search owed).

## UNREAD (not opened, script-rendered, login, video, or fetched but not read)
1. CTLE "Peer-to-Peer Faculty Advice" pages, 4 (Aug 2023; content is video iframes):
   https://teachingexcellence.syr.edu/resources/generative-ai/peer-to-peer-faculty-advice-on-artificial-intelligenceai/what-factors-should-we-consider-in-deciding-when-to-use-and-when-to-curtail-ai-use-in-fall-courses/ (+3 sibling pages, same parent)
2. CLASS "Syllabus Recommendations" (renders by script): https://class.syr.edu/academic-integrity/syllabus-recommendations/
3. CTLE/CLASS "What We Know About ChatGPT and Options for Responding" (Confluence): https://su-jsm.atlassian.net/wiki/pages/viewpage.action?pageId=154894572
4. Vendor AI Policy: https://ai.syracuse.edu/vendor-ai-policy.html
5. AI Data and Privacy (fetched, not read): https://ai.syracuse.edu/privacy.html
6. "Supporting Student Well-Being in an AI-Driven World" page (linked from ai.syracuse.edu/students.html; not opened)
7. Libraries AI research guide (fetched, not read): https://researchguides.library.syr.edu/AI
8. News pointer, librarian AI-literacy grant (funder not checked): https://news.syr.edu/2026/09/23/professor-wins-grant-to-train-academic-librarians-nationwide-on-ai-literacy/
9. News pointer, NSF-funded AI research: https://news.syr.edu/2026/10/14/nsf-funds-professors-research-to-tackle-ais-blind-spots/
10. CTLE workshop slides (Google Slides x3, Drive file x1) linked from https://teachingexcellence.syr.edu/resources/generative-ai/
11. ITS Information Security Framework (SU login) linked from https://ai.syracuse.edu/responsible-ai.html
12. University Senate committee pages (not walked): https://senate.syracuse.edu/committees/academic/ and /committees/curriculuminstruction/
13. ITS stories fetched, not read: https://ai.syracuse.edu/stories/ibl-google-cloud.html , https://ai.syracuse.edu/stories/claude-code-cowork.html , https://ai.syracuse.edu/agentic-os.html
UNREAD count: 13

## Cells
- S0: PLANNED ONLY (ITS Responsible AI Guidelines; outcome = compliance/incidents, not learning). Quote: "5.4. Performance: The effectiveness of the
  guidelines will be evaluated based on compliance rates, reported incidents, and the outcomes of enforcement actions." https://ai.syracuse.edu/ai-guidelines.html
  Detector plan (KB): "If a reliable tool for AI detection becomes available, ITS will evaluate the tool and consider recommending it to the Syracuse
  University academic community." https://su-jsm.atlassian.net/wiki/spaces/blackboard01/pages/154381741/Detecting+AI+Created+Content
  USAGE-OR-ATTITUDE items (no outcome measure, no comparison, no data file):
  - Clementine class-search assistant: "In its first 37 days — March 25 to April 30, 2026 — 2,038 students asked Clementine 8,217 questions across
    2,401 conversations." https://ai.syracuse.edu/stories/clementine.html
  - Claude Enterprise: "By the end of the semester, more than 10,000 users had opted in, with 80% to 90% staying active week to week. Between October
    and April, student usage surged 394%, outpacing peer institutions." https://ai.syracuse.edu/stories/claude-to-campus.html (peer comparison: no source named)
  - Academics page stat: "80 % Weekly active average usage rate of AI tools among licensed users across campus." https://ai.syracuse.edu/academics.html
  - CTLE 2025-26 annual report (all CTLE programs, not AI-specific; n not stated): "89% of CTLE workshop and event participants who completed a
    post-program survey plan to implement changes to their teaching practices." https://teachingexcellence.syr.edu/wp-content/uploads/2026/06/25-26-Annual-CTLE-Report.pdf (p2)
  - A&S badge (no n, no instrument): "We asked A&S undergraduates what they were looking for regarding AI and their education, and overwhelmingly we
    heard that they wanted something to help them use these tools thoughtfully" https://news.syr.edu/2026/09/14/digital-badge-helps-students-use-ai-responsibly/
  Classroom tool, no measure: law "AI coach" - "the evidence and contract coaches have proven very accurate (Graves directly tests them regularly
  himself, in addition to frequent student feedback)" https://news.syr.edu/2026/04/24/law-professor-builds-ai-coach-to-support-students-around-the-clock/
  Institutional context (fact, no judgment): campus-wide Claude Enterprise licence via Anthropic partnership from Sept 2025 (news.syr.edu 2025-09-22).
- S1 (date, type, URL):
  1. 2023-01-12 provost memo to faculty, "ChatGPT" section (news post): https://news.syr.edu/2023/01/12/important-reminders-for-faculty-2/
  2. 2023-03-02 (modified 2024-04-23) CTLE guidance "From Defining AI to Ensuring Equitable Access: Six Points to Consider in Teaching This Fall":
     https://teachingexcellence.syr.edu/resources/artificial-intelligence/teaching-and-learning-in-the-age-of-artificial-intelligence/
  3. 2023-08-09 CTLE Peer-to-Peer Faculty Advice videos (UNREAD #1).
  4. 2024-10-08 (modified 2026-10-16) CTLE resource page "AI (Artificial Intelligence)": https://teachingexcellence.syr.edu/resources/generative-ai/
  5. Fall 2025 ("Where We Stand — Fall 2025"; page "Updated Oct 07") ITS/Online Learning Services KB guidance "Detecting AI Created Content" (URL in S0).
  6. Academic Integrity Policy, AI section (policy; revisions listed "2008, 2011, 2017, 2021, and 2025"):
     https://policies.syr.edu/policies/academic-rules-student-responsibilities-and-services/academic-integrity-policy/
  7. 2025-07-29 (modified 2026-10-12) CTLE/AIO "Syllabus Requirements" with three mandatory AI statements: https://teachingexcellence.syr.edu/syllabus-requirements/
  8. Undated (© 2026) ITS "Responsible AI Guidelines" (data/tool policy; reviewed by Data Governance Committee) (URL in S0); companion pages
     https://ai.syracuse.edu/academic-integrity.html , https://ai.syracuse.edu/students.html , https://its.syr.edu/aiforstudents/
  9. 2025-09 to 2026-10 AIO newsletter "Beyond AIO Policy" (AI items Nov 2025, Mar 2026, Sep 2026, Oct 2026):
     https://teachingexcellence.syr.edu/academic-integrity/beyond-aio-policy/september-2026/
  10. ITS stories: Claude to campus (Sept 2025), Clementine (spring 2026), AI at Work (https://ai.syracuse.edu/stories/ai-at-work.html).
  11. News: 2025-09-22 Claude announcement; 2025-10-23 Chancellor Senate remarks on AI adoption; 2026-07-08 AI academic portfolio; 2026-09-10 Meredith
      Fellow Yung Q&A (https://news.syr.edu/2026/09/10/teaching-and-learning-intentionally-in-the-age-of-ai/); 2026-09-14 A&S AI Literacy badge.
  12. CTLE annual reports 2024-25 and 2025-26 (list AI workshops; PDFs on teachingexcellence.syr.edu home page).
- S2 (evidence cited):
  - Doc 5 KB: bibliography 24 entries (hand count). Peer-reviewed 2 (Elkhatat, Elsaid & Almeer 2023, IJEI 19:17; Weber-Wulff et al. 2023, IJEI 19:26).
    Preprint 1 (Saha & Feizi 2025, arXiv:2502.15666). Vendor/company posts 2 (Turnitin CPO blog; OpenAI classifier post). Other universities' pages 4.
    Own SU pages 2. News/magazine 12. Google Doc 1.
  - Doc 4 CTLE AI page: 87 links (79 off-campus), a resource list. Journal articles 2 by venue (Teaching of Psychology 2024, doi 10.1177/00986283241275664;
    "Assessment in the age of artificial intelligence", Computers and Education: Artificial Intelligence 2022 - DOI matched by Bones from the ScienceDirect
    PII via Crossref, verify). Preprint 1 (EdArXiv mrz8h). 6 chapters of one OER volume (Utah State). Books 5. Rest: guides, blogs, news.
  - Doc 1 provost memo: 0 studies; 2 news articles linked (Fast Company, Inside Higher Ed).
  - Doc 2 CTLE Six Points: 0 studies; Turnitin help page quoted.
  - Doc 6 policy: 0 studies; definition "adapted from Briggs, C. & Briggs, R. (2024), The AI Conundrum , MIT Press" (book).
  - Docs 7, 8, 9: 0 studies.
  - Own surveys: none with AI results found (see S0 usage items).
- S3: NONE (no microdata, aggregate file or instrument found for any AI survey, tool or pilot; usage counts appear in prose only).
- S4: 1 of 36 (hand count; unit = one directive sentence/rule; "evidence item" = a named study or data).
  Doc 1 memo 0/3 (careful with detectors - links a news article; make expectations clear in syllabus/assignments; read the IHE article).
  Doc 2 Six Points 0/5 (prepare students; define terms; transparency/conversations; keep access/paywalls in mind; view peer-to-peer advice).
  Doc 5 KB 1/7 - the 1: "For all of the reasons given above, university ITS does not currently license, support, or recommend any tool for AI writing
  detection." (preceding paragraphs cite Weber-Wulff et al. 2023, Elkhatat et al. 2023); 0 for: no detection-only cases; formulate a course AI
  statement; discuss openly; conversations as path to authentic assessment (cites Chronicle newsletter + Indiana page); refer to CLASS resources;
  spend time adapting assessments.
  Doc 6 policy 0/3 (no detection-only reports; report must state course AI rules; in-app features not unauthorized).
  Doc 7 syllabus 0/6 (copy required language; choose one AI statement; no detection-only cases; consider assignments before choosing; "If possible,
  provide opportunities for students to explore and practice with AI"; faculty may not write their own statement).
  Doc 8 Guidelines 0/12 (sections 1, 1.1, 1.2, 2, 2.1, 3, 4, 5, 5.1-5.4; data/tool rules).
  Not counted: doc 4 (resource list), docs 9-12 (newsletters/news/stories).
- S5 (stated as fact; up to 5):
  1. "To date, there are no tools that can reliably detect writing that is AI-generated (Weber-Wulff et al. 2023)." - doc 5 - cited.
  2. "The detector’s false negative rate was close to 40-50% in tests where AI-generated text was reworded by a human or by a separate AI paraphrasing
     tool (Weber-Wulff et al. 2023)." - doc 5 - cited (source check owed: the page attributes the figure to Turnitin's detector).
  3. "Non-native English speakers are flagged by AI detection tools at a disproportionate rate (Myers 2023)." - doc 5 - cited (Stanford HAI news item).
  4. "Using AI can save time and foster learning." - doc 2 - uncited.
  5. "All generative-AI tools are prohibited in this course because their use inhibits achievement of the course learning objectives." - doc 7
     (mandatory template, Option 1) - uncited.
- S6 (detector stance):
  - ITS/OLS KB: "ITS and Online Learning Services do not currently support or recommend any tool for the detection of AI-generated writing." and
    "Given the concerns about its effectiveness, ITS elected to not license the AI content detection tool." (URL in S0)
  - Policy: "An academic integrity incident report suspecting a student of inappropriate Generative-AI use cannot be submitted to the AIO with only AI
    detection results as proof of violation" (doc 6 URL).
  - Syllabus Requirements: "Artificial Intelligence cases may not be submitted to the Academic Integrity Office with AI-detection results as the only
    evidence of an Academic Integrity Violation." https://teachingexcellence.syr.edu/syllabus-requirements/
  - Provost memo 2023: "Faculty should be careful in using these tools as their reliability remains largely unproven." (doc 1 URL)
  - CTLE Six Points: "Detection tools are proliferating. None is foolproof." (doc 2 URL)
- S7 (own-faculty studies on AI and learning with released data): NONE FOUND with released data (search owed). Candidates seen, no data:
  - Crowston (iSchool) pilot study, intro Python course + 40 developer interviews; no results found. Funding line: "Kevin Crowston has received a $50,000
    grant from the Alfred P. Sloan Foundation to launch a pilot study". Same page: "have put together a three-year proposal for the National Science
    Foundation" (if NSF-funded later: CARD ONLY). https://news.syr.edu/2025/12/24/ischool-professor-awarded-50k-to-study-ais-impact-on-coding-skills/
  - Yung (ECS), Meredith Faculty Fellowship 2025-26, "classroom experimentation" - no study or data found (Q&A URL in S1 item 11).
  - Jing Lei (School of Education): news Q&As only; no study with data located.
Open items: search pass owed (all six items); faculty-study sweep (OpenAlex/SURFACE) owed; source check S5 item 2; CTLE video pages; senate committee
pages; Clementine/Claude usage figures have no released file.
