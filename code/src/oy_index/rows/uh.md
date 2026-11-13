# Row - University of Houston (agent desk row, 25 Oct 2026; Bones recount pending before THE register)
Not an Ivy: no SWEEP_ivies.md section. Quotes marked [v] were checked byte-for-byte (whitespace-normalised) against the page HTML fetched
with curl on 25 Oct 2026; [p] = taken from PDF text extraction (pypdf); [m] = Crossref metadata field, not the paper's own text.

## Search log (same procedure every school; window 2023 to Oct 2026, English, uh.edu primary)
- WebSearch: FAILED on first two queries (session web-search budget exhausted). SEARCH PASS STILL OWED for all six items.
- Substitute procedure: downloaded https://www.uh.edu/sitemap.xml (32,934 URLs) and filtered URLs for ai / artificial / generative /
  chatgpt / turnitin / detect / honesty / teaching / survey / faculty-senate; then fetched hub pages and followed their links:
  uh.edu/ai/ (hub, education, faculty, resources, policy, colleges, research, ai-tools, faq, chatgpt); fdis/ (Turnitin, TIP grant pages,
  recipients 2024-2026); ai/research/tip-ai.php; eit/ai-event/ (2024, 2025, 2026 virtual); class/oet/ai/ ("More information coming soon!");
  infotech/aisolutions/ (AI Impact Initiative, Copilot, use-cases teaching + learning, four AI Sparks stories); provost academic-honesty
  pages (faculty + student) and the policy PDF; faculty-council/ (home, minutes 11-19-25, 01-21-26, 03-25-26, 05-13-26, 09-16-26;
  2026 Faculty Handbook PDF); uhsystem.edu AI guidance page and SAM 07.A.13; news stories 2024-08-20, 2026-03-11, 2026-03-17;
  faculty pages uh.edu/nouhadrizk/ (initiatives, EDM-lab publications) and aminalipour.com (publications); Crossref API by title for
  four Alipour-group papers; export.arxiv.org abs page for the arXiv ID cited in the FAQ. Site's own search not used (no plain-HTML
  endpoint found).
- (1) provost/senate/committee/task-force report on AI in teaching: NONE FOUND (no AI task-force report on uh.edu; Faculty Council minutes
  2025-26 carry only Q&A lines on AI, e.g. 09-16-26 [p]: "Concern was raised that UH's AI infrastructure is underdeveloped. Response: Many
  faculty are already working with AI tools."). (2) teaching-centre guidance: found (ai@UH FAQ + ChatGPT page; FDIS courses on Canvas).
  (3) institution-run survey with n: NONE FOUND. (4) evaluation of own policy/tools/pilots with outcome: NONE FOUND (see S0).
  (5) detector stance: found (FDIS Turnitin page; FAQ). (6) faculty studies with data: see S7.

## UNREAD (UNREAD = 10)
1. https://publications.uh.edu/content.php?catoid=56&navoid=21270 (official Academic Honesty Policy in the catalog; curl 202 empty body,
   fetch tool certificate error). The provost-hosted policy PDF (footer "UC/GPSC FALL 2015" [p]) has no AI text.
2. https://canvas.uh.edu/courses/17897/pages/sample-ai-syllabus-statements (FAQ's sample syllabus statements; returns Canvas login shell).
3. https://canvas.uh.edu/courses/36376 ("AI Basics for Instructors", Canvas).
4. https://uofh.sharepoint.com/sites/AIFoundations (AI Foundations course, SharePoint login).
5. https://docs.google.com/document/u/0/d/1RMVwzjc1o0Mi8Blw_-JUTcXv02b2WRH86vw7mi16W3U/mobilebasic (linked from the student honesty page as
   "Sample Syllabi Policies for AI Generative Tools"; author not known; not opened).
6. https://doi.org/10.1145/3769994.3770027 (Hak et al., Koli Calling 2025; data/funding unread).
7. Ali, Ahmed, Alipour, Terashima-Marin, Journal of Computers in Education 2025 (DOI not resolved; Crossref lookup rate-limited).
8. EIT 2025 session "J. Kovach, A. Chatterjee - Piloting On-Demand AI Tutoring Using 'Tailored Tutor' in Applied Thermodynamics"
   https://www.uh.edu/eit/ai-event/2025/ - recording/paper not located (possible S0/S7 candidate).
9. TIP grant 2024 project "Implementation & Data Analysis of AI Role Play Software in MARK 3337"
   https://www.uh.edu/fdis/grants/tip-grant/recipients_2024.php - no results page located.
10. 2026 EIT conference program PDF (linked from https://www.uh.edu/eit/ai-event/2026/virtual.php), not opened.

## Cells
- S0: PLANNED ONLY. UIT AI Impact Initiative objective [v] https://www.uh.edu/infotech/aisolutions/ai-impact/ : "Measure and communicate how
  AI is improving teaching, learning, research, and operational processes". No measured result for teaching/learning found; the page's
  measured items are operations ("Learn how Internal Audit uses AI to reduce compliance review time by 93%." [v]). Project-level plans:
  TIP grant proposals must include "Assessment plan" and "Assessment of success" [v]
  https://www.uh.edu/fdis/grants/tip-grant/selection-and-submission.php ; Fall 2026 call: "preference will be given to proposals
  implementing artificial intelligence (AI) in their courses" [v] https://www.uh.edu/fdis/grants/tip-grant/ . ChatGPT Edu: "ChatGPT Edu
  is currently in trial phase at the University of Houston." [v] https://www.uh.edu/ai/ai-tools/chatgpt.php - no trial evaluation found.
  Copilot "Piloting" (ai/resources) - no results found.
- S1:
  1. Undated (live Oct 2026), ai@UH FAQ for faculty - https://www.uh.edu/ai/ai-tools/faq.php (guidance)
  2. Undated, ai@UH "ChatGPT For Education" faculty page - https://www.uh.edu/ai/ai-tools/chatgpt.php (guidance)
  3. Undated, ai@UH Resources (student certification courses, instructor courses) - https://www.uh.edu/ai/resources/ (guidance/training)
  4. Undated, UH System "Usage of Artificial Intelligence (AI) at UHS" - https://uhsystem.edu/offices/information-security/resources/artificial-intelligence/index.php
     (security/privacy guidance; "UHS is developing an official AI policy." [v]; academic use deferred: "Please check with the provost’s
     office at your System university regarding specific use cases of AI tools in your curriculum." [v])
  5. Issued 10/07/2026, UH System SAM 07.A.13 "Artificial Intelligence Acceptable Use" - https://uhsystem.edu/resources/compliance-ethics/uhs-policies/sams/07-information-technology/07a13/ (policy)
  6. Undated, FDIS Turnitin page - https://www.uh.edu/fdis/technology/turnitin/ (tool page; detector)
  7. Undated, UIT AI Tools Hub use cases (teaching, learning) - https://www.uh.edu/infotech/aisolutions/ai-tools-hub/use-cases/usecases-teaching.php ,
     .../usecases-learning.php (prompt libraries)
  8. 17 Mar 2026, news release, Gemini for Education / NotebookLM - https://www.uh.edu/news-events/stories/2026/march/03172026-google-ai-partnership.php
  9. 2024-2026, EIT Presents conference pages (2024, 2025, 2026) - https://www.uh.edu/eit/ai-event/ (event programs)
  10. Undated, Faculty Council home page summary of SAM 07.A.13 - https://www.uh.edu/faculty-council/ ("The University of Houston System
      recently adopted SAM 07.A.13" [v])
  11. 2026 Faculty Handbook (one AI mention, intro) - https://www.uh.edu/faculty-council/resources-and-publications/faculty-handbook/_files/2026-faculty-handbook.pdf
- S2: peer-reviewed studies cited: 1 (Lee et al. 2025, CHI, linked as "CHI Conference" in doc 1). Preprints cited: 1 (arXiv 2506.08872,
  linked as "Cornell Research"; the arXiv record title is "Your Brain on ChatGPT: Accumulation of Cognitive Debt when Using an AI
  Assistant for Essay Writing Task", first author Kosmyna). Both in one sentence [v]: "For more on potential concerns with AI use in
  writing-heavy courses, see:". Own surveys: none. Other reports: doc 4 lists as "Additional resources" OWASP Top 10 for LLM Applications,
  NIST AI 600-1, UNESCO "AI and Education: Guide for policy-makers", WHO LMM guidance (listed, not cited for any claim). Docs 2, 3, 5-11:
  none.
- S3: NONE (no microdata, aggregates, instrument or codebook in any document).
- S4: 1 of 41 (hand recount pending). Doc 1 FAQ: 1/12 (the syllabus-expectations answer is followed by the two links above; other 11
  directives name nothing). Doc 5 SAM: 0/17 (numbered provisions 4.1-4.17). Doc 4: 0/6 (general-guideline headings; agent and
  hosting bullets not counted, not learning). Doc 2: 0/5 ("Responsible and Appropriate Use" bullets + closing sentence). Doc 8: 0/1
  ("UH encourages instructors to clearly articulate AI expectations in their syllabi" [v]). Docs 3, 6, 7, 9-11 not counted (no
  directives on learning).
- S5 (stated as fact; all uncited):
  1. "recognizes the use of Artificial Intelligence (“AI”) Systems can be an effective tool for innovation and increasing student and
     employee productivity" - doc 5 SAM 07.A.13 [v] - uncited.
  2. "This approach ensures academic rigor and helps prevent the inaccuracies often associated with non-enterprise AI platforms." - doc 8
     (NotebookLM) [v] - uncited.
  3. "The success of this open pedagogy using GenAI-based CIA activities is outstanding." - faculty initiative page
     https://www.uh.edu/nouhadrizk/initiatives/open-pedagogy-using-chatgpt-interactive-activities/ [v] - uncited (no n).
  4. "Students testimonials reflect the CIA’s huge impact on enhancing their authentic and meaningful learning" - same page [v] -
     testimonials, no n, no count.
  5. "we still have more than 30% of students receive DFW grade in the fundamental programming and data science courses" - same page [v]
     - uncited numeric baseline (no course list, term or denominator).
- S6: FDIS [v] https://www.uh.edu/fdis/technology/turnitin/ : "It also has an AI-detection tool to determine if student’s submission has
  AI-generated content." FAQ [v] https://www.uh.edu/ai/ai-tools/faq.php : "Focus on transparency and responsible use rather than detection
  alone". SAM 07.A.13 [v]: "Unless otherwise specified by the instructor, it is a violation of the Academic Integrity provision of the
  student code of conduct to use Generative AI to create all or part of an assignment." No accuracy figure or detector-use rule found.
  Catalog honesty policy UNREAD (item 1).
- S7: no own-faculty empirical study on AI and learning with released data found. Candidates logged:
  - Amoozadeh, ..., Alipour, "Student-AI Interaction: A Case Study of CS1 students", Koli Calling 2024, https://doi.org/10.1145/3699538.3699567 ;
    funder [m]: "NSF (National Science Foundation)" award 2225373 -> CARD ONLY.
  - Amoozadeh, ..., Alipour, "Trust in Generative AI among Students: An exploratory study", SIGCSE TS 2024,
    https://doi.org/10.1145/3626252.3630842 ; funder [m]: "National Science Foundation" award 2225373 -> CARD ONLY.
  - Alfageeh, ..., Alipour, "From Prompts to Propositions: A Logic-Based Lens on Student-LLM Interactions", Koli Calling 2025,
    https://doi.org/10.1145/3769994.3770004 ; funder [m]: "National Science Foundation" award 2225373; "Research Council of Finland" award
    356114 -> CARD ONLY.
  - Hak, Johnson, Amoozadeh, Alipour, Chattopadhyay, "Observing Without Doing: Pseudo-Apprenticeship Patterns in Student LLM Use", Koli
    Calling 2025, https://doi.org/10.1145/3769994.3770027 ; Crossref funder: none listed; data link: none found; UNREAD.
  - Ali, Ahmed, Alipour, Terashima-Marin, "Adoption of AI-coding assistants in programming education...", J. Computers in Education 2025 -
    UNREAD. Alipour site [v-text]: "My research is sponsored by NSF and IARPA ."
  - Out of scope (creativity, not learning), logged: Lee (UH) & Chung (Rice), "An empirical investigation of the impact of ChatGPT on
    creativity", Nature Human Behaviour 2024 (news 2024-08-20); Hou et al., Information Systems Research (news 2026-03-11). Data/funding
    not checked.
  - Rizk EDM-lab publications page (https://www.uh.edu/nouhadrizk/about/educational-data-mining-lab/publications/): no generative-AI
    learning study listed (latest education items 2021).
