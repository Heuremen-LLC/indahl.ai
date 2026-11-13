# Row - Princeton University (The Wall (OY); file title: Recount Matrix: Learning Research)
Built 25 Oct 2026. Columns per PLAN_OY_INDEX.md addenda 1-3. Quotes verbatim; no adjectives, no scores, no ranks.

## Search procedure (same for every school; logged)
Window 2023 to Oct 2026, English. Sources: Princeton's own .edu pages first; news only as pointers.
- Access note: princeton.edu hosts return HTTP 403 to direct fetch (curl and WebFetch, 25 Oct). Pages were read through
  (a) Wayback Machine snapshots (timestamp given per page) and (b) the r.jina.ai text reader of the live page (marked "live, 25 Oct").
  Chrome extension not connected (not used).
- (1) provost / faculty / committee / task-force reports: odoc.princeton.edu Official Dean's Communications (2023 memo, 2025 teaching memo);
  McGraw "University Report and Resources" list (working-group report link). Web search: "Princeton generative AI working group report".
- (2) teaching-centre guidance: mcgraw.princeton.edu/generative-ai hub and its subpages (setting-policy, ethical-and-other-risks,
  impact-learning, ai-resilient-activities-and-assignments, embracing-ai-classroom, scholarly-integrity-and-detecting-use-ai,
  considerations-using-gai-...); ai.princeton.edu/education; RRR 2.4.6 (rrr.princeton.edu).
- (3) institution-run surveys with n: web searches "site:princeton.edu survey students generative AI", "Princeton entering student survey
  generative AI", McGraw ethics page survey link.
- (4) evaluation of own policy/tools/pilots with outcome: web searches "Princeton AI pilot evaluation", "McGraw AI feedback pilot";
  McGraw "Embracing AI" pilot paragraph; faculty blog (login-gated).
- (5) detector stance: ODoC 2023 memo; McGraw detection page (live) and archived hub section.
- (6) faculty empirical studies with released data: web searches (Princeton + LLM + students + experiment / dataset); Crossref API;
  collaborate.princeton.edu research portal; arXiv API title search. Also checked SWEEP_ivies.md (Princeton: 3 A, 0 B) and
  SWEEP_202610_osf.md / CARDS.md (no Princeton entries).
- Excluded as pointers only: Daily Princetonian Frosh Survey articles (student newspaper; https://www.dailyprincetonian.com/article/2025/10/princeton-data-2029-frosh-survey-blog-ai-use-fields),
  PAW articles (https://paw.princeton.edu/article/princeton-memo-directs-faculty-acceptable-use-chatgpt-and-other-ai ;
  https://paw.princeton.edu/article/generative-ai-advances-princeton-tries-keep-policies-updated).

## S0 self-evaluation: USAGE-OR-ATTITUDE ONLY
- Receipt 1 (usage figure from institution's own forms, no n): https://odoc.princeton.edu/about/official-deans-communications/2025/teaching-memo-dean-gordin-fall-2025
  (Wayback 20260202): "according to our entering student forms, the proportion of students who stated that they used GenAI products in the
  past year “rarely or never” was 28%. Last year the equivalent number was 53%."
- Receipt 2 (usage survey, n not stated, survey body UNREAD): https://mcgraw.princeton.edu/ethical-and-other-risks (live, 25 Oct):
  "A survey of Princeton students from spring 2026 shows that there is a wide variety in how often, and for what purpose, students use
  generative AI tools."
- Pilot mentioned, no outcome found: https://mcgraw.princeton.edu/embracing-ai-classroom (live): "Some faculty are engaging AI to provide
  students feedback on assignments. ... These pilots—one of which is described on our faculty blog—are being conducted thoughtfully and
  carefully to protect student data". Blog is login-gated (UNREAD).
- Stated intent, no measurement named: ODoC 2023 memo: "We will continue to assess the development of generative AI and will generate more
  comprehensive guidance as the year progresses." (assessment of the technology, not of the policy).
- Course-level item kept in S7, not S0: Khan et al. SIGCSE TS 2026 (CubBot, randomized assessment, 134 students) is a faculty/student study
  of a course tool; results UNREAD, so it does not set S0 here.

## S1 public AI-in-learning documents
| Date | Type | Title | URL | Read via |
|---|---|---|---|---|
| 2023-08-30 | Dean's memo (policy + working-group recommendations) | Generative AI in Teaching and Learning Fall 2023, Faculty and Student Memo (signed "Deans Dolan, Stanton, and Swanson") | https://odoc.princeton.edu/about/official-deans-communications/2023/generative-ai-teaching-and-learning-fall-2023-faculty-and | Wayback 20260311 |
| 2023-09-15 (filename) | Committee report | Generative AI Working Group Report (Office of the Dean of the College) | https://princetonu.sharepoint.com/sites/mcgraw/gen-ai/Shared%20Documents/GenAI-working-group-report-9-15-23.pdf | UNREAD (SharePoint, login) |
| 2025-08-20 | Dean's teaching memo (AI section) | Teaching Memo from Dean Gordin Fall 2025 | https://odoc.princeton.edu/about/official-deans-communications/2025/teaching-memo-dean-gordin-fall-2025 | Wayback 20260202 |
| current (RRR edition live 25 Oct) | Policy (academic regulations 2.4.6 / 2.4.7) | Rights, Rules, Responsibilities 2.4 Academic Regulations | https://rrr.princeton.edu/students-and-university/24-academic-regulations | live, 25 Oct |
| undated (live 2026; Feb 2026 earlier version archived) | Teaching-centre guidance hub | AI and Our Classrooms (formerly "Generative AI and Our Classrooms") | https://mcgraw.princeton.edu/generative-ai | live + Wayback 20260207 |
| undated (live) | Guidance | Setting a Policy | https://mcgraw.princeton.edu/setting-policy | live |
| undated (live; cites spring 2026 survey) | Guidance | Ethical and Other Risks | https://mcgraw.princeton.edu/ethical-and-other-risks | live |
| undated (live; cites 2026 sources) | Guidance (evidence page) | Impact on Learning | https://mcgraw.princeton.edu/impact-learning | live |
| undated (live) | Guidance | AI-Resilient Activities and Assignments | https://mcgraw.princeton.edu/ai-resilient-activities-and-assignments | live |
| undated (live) | Guidance | Embracing AI in the Classroom | https://mcgraw.princeton.edu/embracing-ai-classroom | live |
| undated (live; cites 2026-06 and 2026-08 sources) | Guidance (detector stance) | Scholarly Integrity and Detecting the Use of AI | https://mcgraw.princeton.edu/scholarly-integrity-and-detecting-use-ai | live |
| undated (archived 2025-11-07) | Guidance for students | Considerations for Using GAI for Engagement, Learning, Studying and Exam Prep | https://mcgraw.princeton.edu/considerations-using-gai-engagement-learning-studying-and-exam-prep | Wayback 20251107 |
| undated (archived 2025-11-15) | University AI site, education page | AI at Princeton: Education | https://ai.princeton.edu/education | Wayback 20251115 (live = CAS login) |

## S2 evidence cited (documents read)
- Peer-reviewed studies cited: 12 distinct (9 on live McGraw pages, 3 more on the Feb 2026 archived hub):
  live: npj Science of Learning 2016 meta-analysis (https://www.nature.com/articles/npjscilearn201613, considerations page);
  Trends in Cognitive Sciences 2016 (https://doi.org/10.1016/j.tics.2016.07.002); Frontiers in AI 2022 (https://www.frontiersin.org/articles/10.3389/frai.2022.908261/full);
  ScienceDirect S2666920X26000494 (bias meta-study); ScienceDirect S2666920X26000342 (impact page); Scientific Reports 2025, Kestin et al.
  (https://www.nature.com/articles/s41598-025-97652-6, impact + embracing pages); IEEE 11573616 (University of Florida detectors);
  Springer chapter 978-3-031-98420-4_7 (autism misclassification); Patterns S2666389923001307 (non-native writers).
  archived hub only: J. Responsible Technology 2023 (https://doi.org/10.1016/j.jrt.2023.100060); ProQuest scholarly journal article on ICT
  use/digital skills (ezproxy link); Teaching CS50 with AI (SIGCSE 2024).
- Preprints cited: arXiv 2608.11256 (Notre Dame, Pangram); arXiv 2304.02819; arXiv 1906.02243; SSRN 4475995.
- Own surveys: entering student forms (28% vs 53%; n NOT STATED, response rate NOT STATED); spring 2026 student survey (n NOT STATED on page;
  linked as a Canva design, UNREAD).
- Other reports: Stanford SCALE "Evidence Base on AI in K-12" report; UTS cognitive-offloading report (2026); MIT AI and education report;
  UChicago BFI insight; Harvard Kennedy School literature review (Google Doc); U.S. Department of Education report (archived hub reading list);
  news/blog items (USA Today, Ars Technica, NYT, The Atlantic, MIT News, Inside Higher Ed, Brookings, Stanford HAI news, Time).
- ODoC 2023 and 2025 memos: no study cited. 2023 memo: working group "met to sort through the literature" (no list given).

## S3 data released: NONE FOUND
- Searched: Gordin memo (figure only, no table or instrument); McGraw ethics page (survey linked to Canva design, UNREAD); web search for
  institutional-research publication of entering-student AI items (none on .edu found). No microdata, aggregates file, or instrument located.

## S4 recommendations naming an evidence item: 6 of 30 (by proximity: a cited study/report/data point in the same paragraph)
Counted in: ODoC 2023 memo (3), Gordin 2025 memo AI section (3), McGraw hub intro (2), setting-policy (2), ethics page (4),
impact page (2), AI-resilient page (12 headings), detection page (2), considerations page (1). Total n = 31 listed; 1 dropped as duplicate
(syllabus-policy rec repeated hub/setting-policy) -> n = 30.
Naming evidence (k = 6):
1. Gordin 2025, reevaluate assignments: "this is the moment to reevaluate what you do and how you do it" (follows entering-student 28%/53% figure).
2. Ethics page, talk about learning interference: "We suggest that faculty talk to their students about how artificial intelligence might
   interfere with their learning" (TICS 2016 + Frontiers 2022 in paragraph).
3. Ethics page, environmental discussion: "We encourage you to engage your students in a discussion of environmental concerns" (MIT News article).
4. Impact page: "preserve the cognitive friction or desirable difficulty required for learning" (Kestin Sci Rep; UTS report).
5. Impact page: "design our courses and assignments with great intention" (MIT report link).
6. Detection page: "we advise against relying on AI detection tools" (UChicago BFI, Notre Dame arXiv, UF IEEE, Springer, Patterns).
Plus considerations page "recommend that any decisions about the use of AI ... be guided by an understanding of how humans learn" names a
framework "derived from a robust meta-analysis" in the next paragraph - counted NO (different paragraph; strict proximity). Borderline, flagged.
Not naming evidence (24): incl. ODoC 2023 "We don't recommend that faculty use these tools" (detectors; no source in memo), syllabus-policy recs,
oral/bluebook, all 12 AI-resilient headings (faculty examples, no study), data-privacy review rec (blog link only - counted NO), ethics talk rec.

## S5 testable claims (stated as fact)
1. "A recent study shows that students learn significantly more in less time when using an AI tutor, compared with doing in-class active
   learning." - https://mcgraw.princeton.edu/embracing-ai-classroom ; cited: Kestin et al., Sci Rep 2025. (Same study recounted in the Harvard
   row, harvard_kestin/.)
2. "unstructured or unmediated AI use improves short-term performance, but not durable learning." - https://mcgraw.princeton.edu/impact-learning ;
   cited: UTS report (2026) PDF.
3. "Offloading may improve a student’s short-term performance (i.e., getting good grades on an assignment) but diminish their long-term
   learning and cognition." - https://mcgraw.princeton.edu/ethical-and-other-risks ; cited: Frontiers in AI 2022.
4. "We believe that detection and surveillance tools are not an effective means to identify or deter the use of generative AI. They’re not
   reliable, and they appear to be biased." - ODoC 2023 memo ; uncited in memo.
5. "the proportion of students who stated that they used GenAI products in the past year “rarely or never” was 28%. Last year the equivalent
   number was 53%." - Gordin 2025 memo ; source: "our entering student forms" (n not stated; no release).
Pricing (ABOVE/BELOW/CONSISTENT/CANNOT_TELL): not done in this row; (5) CANNOT_TELL until n/denominators are released.

## S6 AI-detector stance
- ODoC 2023 (Wayback 20260311): "We believe that detection and surveillance tools are not an effective means to identify or deter the use of
  generative AI. They’re not reliable, and they appear to be biased. We don’t recommend that faculty use these tools."
- McGraw (live, 25 Oct) https://mcgraw.princeton.edu/scholarly-integrity-and-detecting-use-ai : "For several reasons, we advise against relying
  on AI detection tools to determine if students have violated your AI policy." Also: "Pangram is often considered the most accurate of the AI
  detection tools."
- McGraw hub, Feb 2026 archive: "we do not recommend you use such software to attempt to determine if student work is AI-generated."

## S7 own-faculty studies with released data
- Khan, Mahinpei, Hedayati, Dean, Fong. "Characterizing the Relationship Between Generative AI, Student Behavior, and Learning Outcomes in
  Upper-Level CS Education: A Case Study in an Undergraduate Machine Learning Course." SIGCSE TS 2026 V.2, pp. 1673-1674 (2-page abstract),
  https://doi.org/10.1145/3770761.3777156 ; portal: https://collaborate.princeton.edu/en/publications/characterizing-the-relationship-between-generative-ai-student-beh/
  Abstract: "an undergraduate machine learning course with 134 students ... a randomized, controlled assessment comparing performance with
  and without CubBot access."
  Data link: NONE FOUND (abstract and portal list none; ACM full text UNREAD - CAPTCHA).
  Funding (verbatim from Crossref funder metadata, not the paper text): "Princeton University's Office of Undergraduate Research Senior Thesis
  Research Funding Program" (award 147398); "Princeton University's Friedland Independent Work/Senior Thesis Fund"; "Princeton University’s SEAS
  Innovation Grant". Not government-grant funded per this metadata -> not CARD ONLY.
- No other Princeton-authored empirical AI-and-learning study with released data found in the searches listed above.

## UNREAD (7)
1. Spring 2026 student survey (Canva design link) - https://www.canva.com/design/DAHFDrRa-0g/MZwxlVr3Xa-uNft_V2mmpg/edit
2. Generative AI Working Group Report 9-15-23 - https://princetonu.sharepoint.com/sites/mcgraw/gen-ai/Shared%20Documents/GenAI-working-group-report-9-15-23.pdf (login)
3. GenAI memo for all faculty and undergrad students (ODoC related document) - https://odoc.princeton.edu/document/856 (403, no snapshot)
4. McGraw learning framework chart - https://mcgraw.princeton.edu/document/4296 (403, no snapshot)
5. Learning from Teaching faculty blog (AI feedback pilot) - https://commons.princeton.edu/learning-from-teaching/ (CAS login)
6. President's Opening Exercises 2026 (quoted on hub) - https://president.princeton.edu/blogs/opening-exercises-2026-what-you-learn-along-way (403)
7. Khan et al. SIGCSE 2026 full text - https://dl.acm.org/doi/10.1145/3770761.3777156 (CAPTCHA)
Also: live ai.princeton.edu/education returns CAS login (read via Wayback 20251115 only); McGraw hub "Resources and Readings" accordions on the
live page did not render in the reader (read via Wayback 20260207).

## Bones check (25 Oct): Khan et al., SIGCSE TS 2026, doi 10.1145/3770761.3777156
- Abstract (collaborate.princeton.edu) describes "a randomized, controlled assessment comparing performance with and without CubBot access"
  (COS 324, 134 students) but reports no result; ACM full text 403 to us; no funding line on the page. -> pilot stays HELD (results UNREAD).
- Bones retry (25 Oct ~12:35): OpenAlex marks the paper open access (hybrid) but the ACM PDF is blocked to us (reader returns 467 bytes); arXiv API: no CubBot preprint. Pilot stays HELD, results UNREAD.
