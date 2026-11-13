# Row - University of Georgia (UGA) (agent row, 25 Oct 2026; not yet recounted by Bones)
Not an Ivy: no SWEEP_ivies.md section. Window 2023 to Oct 2026, English, uga.edu primary pages; news.uga.edu used as pointers and for dates.
Method note: session WebSearch budget ran out after 2 searches (queries: "University of Georgia generative AI teaching learning provost task force report";
"site:uga.edu generative AI guidance teaching CTL"; a 3rd, "UGA AI detection Turnitin...", returned results; a 4th on surveys was refused). Everything else was found by
fetching uga.edu hub pages with curl, following their own links, WordPress sitemaps (instruction, ctl, aihub), the sites' own search (ctl.uga.edu/?s=, news.uga.edu
WP search endpoint) and the UGA Policy Library's own Kuali catalog search. PDFs text-extracted locally. A search pass is still owed (surveys, faculty studies, OSF/Zenodo/ERIC).

## Search log (same procedure as every row)
- (1) provost/senate/committee/task-force reports: provost.uga.edu home (no AI report linked); aihub.uga.edu (Leadership Council on AI page, Policy & Guidance, Memos & Updates);
  policy.uga.edu Kuali search "artificial intelligence" -> Policy 01.07.005 (read in full via the catalog API). Acceptable Use guidance PDF (read in full).
  33rd Academic Affairs Faculty Symposium (March 2023) news read; its "final summative symposium report" not found on instruction.uga.edu (Teaching Academy pages + sitemaps).
  University Council (univcouncil.uga.edu, council.uga.edu): no connection (curl 000). No task-force report found.
- (2) teaching-centre guidance: ctl.uga.edu Generative AI & Teaching hub + 4 subpages (Introduction; Academic Honesty; Policies for T&L; PAIRR Feedback Guide PDF) read;
  CTL Turnitin page (AI section) read; aihub.uga.edu/resources-tools/teach-with-ai/ (FAQ) read; Office of Instruction memos Fall 2023 (PDF), Spring 2024 (PDF), Fall 2026 (Mailchimp) read.
- (3) institution-run surveys with n: Your UGA Experience Survey (SERU) page read (lists genAI items; no results posted); CTL event page announcing a Spring 2025 community survey (read;
  results page not found); OIR site search "SERU" (no report link). No survey with n found.
- (4) evaluation of own policy/tools/pilots: Student Premium AI License Pilot page + 3 Sep 2026 expansion post read; GAIT Faculty Fellows page + 5 Jun 2026 news read;
  Innovation in AI Teaching Award page read; AI @ UGA strategy page read; Policy 01.07.005 sections 11-15 (review) read. No outcome evaluation found.
- (5) detector stance: CTL Academic Honesty page, CTL Turnitin page, 2023/2024/2026 instruction memos, AI Hub FAQ read.
- (6) faculty studies with released data: news.uga.edu WP search (terms: AI survey; generative AI survey; ChatGPT study; artificial intelligence students learning; ChatGPT students;
  AI tutor; AI classroom study; generative AI teaching; 2023-on), Crossref metadata for the one study found. No OSF/Zenodo/ERIC pass run.
- Pointers only (news): https://news.uga.edu/faculty-discuss-ways-to-harness-ai-potential/ (19 May 2023) ; https://news.uga.edu/gait-fellows-explore-the-use-of-ai-in-the-classroom/ (5 Jun 2026) ;
  https://news.uga.edu/uga-expands-ai-resources-for-campus-community/ (29 Sep 2026) ; https://news.uga.edu/10-million-grant-to-fund-national-genai-center-at-uga/ (10 Oct 2024).

## Cells
- S0 self-evaluation: USAGE-OR-ATTITUDE ONLY (one survey, results not located) + PLANNED ONLY (pilot feedback surveys, policy review). No outcome measure found.
  Survey: https://ctl.uga.edu/event/responsible-use-of-ai-for-teaching-learning-uga-community-perspectives/ "In Spring 2025 we deployed a survey to the UGA community, investigating perspectives on the use of AI for teaching and learning." (event 22 Oct 2025; n and results not on page)
  Pilot: https://aihub.uga.edu/resources-tools/students/student-premium-ai-license-pilot-program/ "Pilot participants will help UGA understand student demand, effective use cases and support needs for premium AI tools." ; "Complete a brief feedback survey at the end of each semester (spring 2026, fall 2026 and spring 2027)."
  Pilot (news): https://aihub.uga.edu/uga-expands-student-pilot-program-for-premium-ai-tools/ "help inform the university’s continued evaluation of how these technologies can best support teaching, learning and student success."
  Policy review: https://policy.uga.edu/policies#/programs/H1xNko5fMl "Office of Institutional Research: Provides data and analysis to support evidence-based updates" (01.07.005 s.12); "this policy shall be reviewed periodically, defined as at a minimum, annually." (s.11)
  Fellows: https://ctl.uga.edu/programs/past-programs/generative-ai-and-teaching-fellows/ "a cohort of faculty to explore, share, develop, implement, and assess innovative applications of generative AI" (no assessment results found).
- S1 documents:
  1. 3 Aug 2023, instruction memo (Provost + VP Instruction), "ChatGPT and Similar Tools" section: https://instruction.uga.edu/wp-content/uploads/FallTerm2023InstructionMemoAug3.pdf
  2. Spring 2024, instruction memo, "GENERATIVE AI" section: https://instruction.uga.edu/wp-content/uploads/Spring-2024-Instruction-Memo.pdf
  3. Approved 5 Mar 2025 (rev. eff. 7 Aug 2026), guidance "UGA Guidance on Acceptable Use of AI" (Leadership Council on AI 21 Feb 2025; Provost): https://aihub.uga.edu/wp-content/uploads/2026/08/ai-acceptable-use-guidelines-rev-080626.pdf
  4. Initial approval 1 Jul 2026, last revised 12 Aug 2026, policy 01.07.005 "Policy on the Use of Artificial Intelligence (AI) in Academic and Operational Contexts" (s.6 "AI Use in Instruction"): https://policy.uga.edu/policies#/programs/H1xNko5fMl (text read via https://uga.kuali.co/api/v1/catalog/program/64402e2e07c328001cd0ecd1/H1xNko5fMl)
  5. 29 Jul 2026, Fall 2026 instruction memo (AI policy, AI literacy, Turnitin sections): https://mailchi.mp/634805669f33/fall-2026-instruction-memo
  6. Last updated Oct 2025, CTL guidance "Introduction to Generative AI & Teaching": https://ctl.uga.edu/teaching-resources/generative-ai-teaching/introduction-to-generative-ai-and-teaching/
  7. Undated (as of Apr 2025 data), CTL guidance "Academic Honesty & Generative AI": https://ctl.uga.edu/teaching-resources/generative-ai-teaching/academic-honesty-and-generative-ai/
  8. CC-BY-NC-SA 2026, CTL guidance "Generative AI Policies for Teaching & Learning" (Vanderveen & Poproski): https://ctl.uga.edu/teaching-resources/generative-ai-teaching/generative-ai-policies-for-teaching-and-learning/
  9. 2026 (page published 28 Jan 2026), CTL guide "PAIRR Feedback Guide" PDF (Hartung & Poproski): https://ctl.uga.edu/wp-content/uploads/PAIRR-Feedback-Guide.pdf
  10. Undated (2026), AI Hub guidance/FAQ "Teach with AI": https://aihub.uga.edu/resources-tools/teach-with-ai/
  11. Undated (2025-26), strategy page "Building the AI-Infused University: UGA’s Strategic Path Forward": https://aihub.uga.edu/about/ai-uga/
  12. Undated, CTL Turnitin page (AI Writing Detection section): https://ctl.uga.edu/teaching-resources/digital-learning-tools/turnitin/
  Not counted: USG Board of Regents policy 06.28 (linked by UGA; government system policy, out of scope per addendum 3).
- S2 evidence cited: peer-reviewed journal articles cited: 0 across documents 1-12. Other items cited: CTL Policies page (doc 8) lists 2 references:
  https://ctl.uga.edu/teaching-resources/generative-ai-teaching/generative-ai-policies-for-teaching-and-learning/ "Davis, M. (2024). Supporting inclusion in academic integrity in the age of GenAI. In Using Generative AI effectively in higher education" (book chapter) ; "Perkins, M., Roe, J., & Furze, L. (2024, December 12). The AI Assessment scale revisited" (arXiv preprint).
  Doc 7 and doc 5 link a vendor blog (turnitin.com, false-positive rate) and a news item (hai.stanford.edu "ai-detectors-biased-against-non-native-english-writers") behind "studies show".
  Doc 10 links an opinion column (insidehighered.com, Savini, 16 Jul 2025). Doc 9 attributes PAIRR to a program page (writing.ucdavis.edu/pairr), no study cited.
  Own surveys: Spring 2025 CTL community survey (n, response rate not found); SERU (genAI items listed, administered odd years, no results posted). Docs 3, 4: 0 studies; cite laws/standards only.
- S3 data released: NONE FOUND (no microdata, aggregates or instrument). SERU page describes item topics only: https://instruction.uga.edu/units/assessment/your-uga-experience-survey/ "Emerging technologies: Frequency, ethics, and appropriateness of generative AI tool usage in academic coursework"
- S4 recommendations naming an evidence item: 9 of 54 (agent hand count; Bones recount pending). 0 of 54 name a peer-reviewed journal study.
  Doc 6 CTL Intro: 0 of 7 (Learn; Explore; Reflect; Set and communicate stance; document use; fair access; accuracy support).
  Doc 8 CTL Policies: 2 of 8 (AI Assessment Scale -> Perkins et al. arXiv; traffic-light chart -> Davis 2024 chapter; 0: 3 "Basics" features, start from learning goals, declaration statements, student reflection).
  Doc 7 CTL Honesty: 1 of 5 ("use ... with caution" -> Turnitin blog + Stanford HAI news; 0: discuss expectations, use only Turnitin, review sentence-level data/compare past writing, report).
  Doc 10 AI Hub FAQ: 5 of 15 (5 AI-resilient design strategies -> Savini Inside Higher Ed opinion; 0: communicate policy, misuse response, integration, accessibility, 4 disclosure points, grading, disability support).
  Doc 9 PAIRR: 0 of 5 steps (program page only). Doc 1 memo 2023: 0 of 4. Doc 2 memo 2024: 0 of 3. Doc 5 memo 2026: 1 of 7 (Turnitin caution -> Turnitin blog + HAI news).
  Doc 4 policy s.6 mandates (not counted as recommendations): 0 evidence citations.
- S5 testable claims (stated as fact):
  1. https://ctl.uga.edu/wp-content/uploads/PAIRR-Feedback-Guide.pdf "Enhances Formative Assessment by providing multi-faceted feedback (peer and GAI), deepening engagement with revision, and improving writing quality." - uncited (framework attributed to UC Davis program page).
  2. https://ctl.uga.edu/teaching-resources/generative-ai-teaching/academic-honesty-and-generative-ai/ "Turnitin reports a sentence-level false positive rate of 4%, but studies show that this false positive rate is higher for students who speak English as a second language, as well as for text that was modified by a grammar modulator." - cited: Turnitin blog (vendor), Stanford HAI news; grammar-modulator part uncited.
  3. https://ctl.uga.edu/teaching-resources/generative-ai-teaching/academic-honesty-and-generative-ai/ "Turnitin’s AI Writing Detector was trained on output from GPT-3.5." - uncited.
  4. https://aihub.uga.edu/resources-tools/teach-with-ai/ "AI-resilient assessment design keeps student learning visible and central whether AI is prohibited, permitted, or intentionally incorporated." - cited: Savini, Inside Higher Ed opinion (2025).
  5. https://aihub.uga.edu/wp-content/uploads/2026/08/ai-acceptable-use-guidelines-rev-080626.pdf "AI can be used to support educational activities, such as providing personalized learning experiences, offering tutoring assistance, and enhancing accessibility for students with disabilities." - uncited.
  Date check (for pricing): https://ctl.uga.edu/teaching-resources/digital-learning-tools/turnitin/ "Turnitin introduced their AI Writing Detection feature in July 2024." vs https://instruction.uga.edu/wp-content/uploads/FallTerm2023InstructionMemoAug3.pdf "UGA’s Similarity Reports includes an AI writing indicator score, which is independent from the similarity score." (memo dated Aug 2023).
- S6 AI-detector stance: one approved detector, used with caution, not definitive.
  https://ctl.uga.edu/teaching-resources/generative-ai-teaching/academic-honesty-and-generative-ai/ "Turnitin’s AI Writing Detector is the only AI Writing Detector approved for use at UGA." ; "It is important that Turnitin scores not be used as a definitive measure of misconduct."
  https://mailchi.mp/634805669f33/fall-2026-instruction-memo "Turnitin writing indicator scores should never be considered definitive evidence of academic misconduct."
  https://instruction.uga.edu/wp-content/uploads/FallTerm2023InstructionMemoAug3.pdf "Do not rely solely on AI detector tools to identify whether an assignment was created using generative AI."
- S7 own-faculty studies with released data:
  1. Wu, Saraf, Lee, Latif, Liu, Zhai, "Unveiling Scoring Processes: Dissecting the Differences Between LLMs and Human Graders in Automatic Scoring", Technology, Knowledge and Learning, 21 Mar 2025,
     https://doi.org/10.1007/s10758-025-09836-8 -> CARD ONLY (Crossref funder: "National Science Foundation", awards 2101104, 213884, 2223768). Funding line verbatim and data link UNREAD (Springer page returned 3 kB challenge).
  2. GENIUS Center (Zhai, lead): https://news.uga.edu/10-million-grant-to-fund-national-genai-center-at-uga/ "five-year, $10 million grant from the Institute of Education Sciences" -> CARD ONLY.
  3. ArchPal (Harding, GAIT 2025-26): https://news.uga.edu/gait-fellows-explore-the-use-of-ai-in-the-classroom/ "Piloted in spring 2026 across humanities, social science and science courses" - no study or data release found.
  No UGA faculty study on AI and learning with released data found on reachable pages (search pass owed).

## UNREAD
1-3. https://outlookuga.sharepoint.com/:b:/s/ProvostCommunications/IQAbyBDRqZ97T65a-Y-hO1uXAbn4ui_8aia0YtP4nJAEcf0?e=fnKjiC (and the 2 sibling ProvostCommunications links on aihub.uga.edu/news-updates/memos-updates/; Microsoft login required) - includes "Call for Proposals for New AI Course Innovation Grants" and "Appointment of UGA AI Executive Steering Committee" memos
4. https://outlookuga-my.sharepoint.com/:b:/g/personal/kmarsin_uga_edu/IQDvR4144ZUoTIWvujSXn1VBAXHTfXZTGhn9j31XpS4rK-I?e=Ds1kJP (linked from Fall 2026 memo; not opened)
5. https://app.powerbi.com/links/KEQgPnvqUi (linked from Fall 2026 memo; not opened)
6. https://link.springer.com/article/10.1007/s10758-025-09836-8 (client challenge)
7. https://univcouncil.uga.edu/ and https://council.uga.edu/ (no connection)
8. 2023 Academic Affairs Faculty Symposium "final summative symposium report" (named in news 19 May 2023; no URL found)
9. Spring 2025 CTL community AI survey results (presented 22 Oct 2025; no URL found)
10. https://aihub.uga.edu/resources-tools/students/when-to-use-ai/ (served a LibGuide page; not read in full)
11. https://uga.view.usg.edu/d2l/le/discovery/view/course/3616588 ("Navigating AI Literacy for Instructors" eLC course; login)
12. https://research.uga.edu/integrity/ai/ (research AI guidance; not fetched)
13. https://docs.google.com/spreadsheets/d/1lM6g4yveQMyWeUbEwBM6FZVxEWCLfvWDh1aWUErWWbQ/edit (external syllabus-policy repository; not opened)
