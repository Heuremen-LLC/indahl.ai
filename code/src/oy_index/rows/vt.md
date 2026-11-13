# Row - Virginia Polytechnic Institute and State University (Virginia Tech) (agent row, 25 Oct 2026; not yet recounted by Bones)
Not an Ivy: no SWEEP_ivies.md section. Window 2023 to Oct 2026, English, vt.edu primary pages; news.vt.edu as pointers only.
Method note: session WebSearch budget exhausted (1 search attempted, refused, 0 results). Pages found by fetching vt.edu hub pages
(ai.vt.edu, provost.vt.edu, tlos.vt.edu, teaching.vt.edu, honorsystem.vt.edu, it.vt.edu, facultysenate.vt.edu, governance.vt.edu) with curl
and following their links; PDFs text-extracted locally. Site search: VTechWorks (VT's own repository) DSpace search API queried
("generative AI students learning", "ChatGPT students", "rolai", "generative AI course students survey", "ChatGPT engineering education",
"large language model students course"). search.vt.edu returns a JS shell (no results in static HTML). ai.vt.edu/sitemap.xml and
tlos.vt.edu/sitemap.xml 404; news.vt.edu/sitemap.xml no response. Coverage = link-reachable pages + VTechWorks; A SEARCH PASS IS STILL OWED.

## Search log (same procedure as every row)
- (1) provost/senate/committee/task-force reports: ai.vt.edu/about/governance.html -> "Responsible and Ethical AI Framework for Virginia Tech" (AI Working
  Group Final Report, 48 pp., read in full); AI Principles PDF + one-pager (read); IT Governance AI Working Committee page + charter PDF (read);
  AI Futures Working Group page (strategicaffairs) + news 20 Aug 2026 (read). Faculty senate home (www.facultysenate.vt.edu) read: links only to BOV
  constituency reports and a login SharePoint; governance.vt.edu Resolution Tracker: list is script-loaded, no resolution text in static HTML.
- (2) teaching-centre guidance: ai.vt.edu/index/teaching.html, /index/learning.html, /training.html, /tools/hokieai.html (read); TLOS "Considering
  Generative AI at Virginia Tech" (read), "Using Generative AI in Assessments" (read), Graduate School statement (read), TLOS AI resources index (read);
  CETL teaching.vt.edu/hub/ai-resources.html (read); OUAI honorsystem.vt.edu/resources/syllabus.html (read); "Introduction to AI Literacy
  Guidelines" Oct 2025 PDF (read); Summer 2024 FLC site aiteaching.vt.domains (home page read only).
- (3) institution-run surveys with n: framework report (spring 2025 faculty survey n = 118; ChatGPT Edu pilot surveys); Kim et al. 2025 (TLOS-funded
  survey, 982 students / 76 faculty, PDF read: methods, funding, data lines); Fall 2024 student AI literacy survey (Tableau dashboard, UNREAD).
- (4) evaluation of own policy/tools/pilots: framework Appendix C (ChatGPT Edu pilot) read; Section 7.1 (Copilot pilot, Rolai) read; TLOS ChatGPT Edu
  pilot page read; TLOS 2024-25 Annual Report PDF read (AI/pilot passages); Copilot study notice 404.
- (5) detector stance: grep of every fetched page/PDF for "detect", "Turnitin", "detector"; TLOS page and OUAI syllabus page carry stances.
  Honor Code definitions page: no AI text.
- (6) faculty empirical studies with released data: VTechWorks API (queries above); candidate PDFs opened: Kim et al. 2025, DevCoach (Wang, Trimble,
  Brown 2025), Generative Co-Learners (Wang et al. 2025); metadata only: Kaufman 2026, Jelson & Lee 2024, SPHERE (Tang et al. 2025).
  CS1-LLM (Vadaparty et al. 2026, hdl 10919/142747) is in VTechWorks but its listed authors carry no VT affiliation in the record: not counted.
- Pointers only (news): news.vt.edu/articles/2026/08/virginia-tech-sets-course-for-human-centered-ai-leadership.html ;
  news.vt.edu/articles/2026/08/hokieai-access.html ; news.vt.edu/articles/2026/10/division-of-it-2026-annual-report.html (not read).

## Cells
- S0 self-evaluation: USAGE-OR-ATTITUDE ONLY (outcome measurement of learning: PLANNED ONLY).
  Pilot (employees and graduate assistants, not a learning outcome): "The pilot did not track pre/post performance benchmarks, monetize time savings, or
  measure organizational outcomes tied to usage." (https://ai.vt.edu/content/dam/ai_vt_edu/Responsible-and-Ethical-AI-Framework-for-Virginia-Tech-(v1.0-Sep-2025).pdf p45, App. C.6.2)
  Pilot results printed are self-report: "Productivity Increase: 94% of respondents reported increased productivity" (same PDF p44; 425 participants; respondent n not printed).
  Planned (student-facing tutoring tool): "Rolai, an AI-tutoring add-on now under evaluation in selected Canvas courses through Fall 2025, will be folded into
  the same assessment pipeline once outcome data are available." (same PDF p19). No Rolai outcome found on reachable pages.
  Planned: "The AI Working Group's annual assessment should evaluate not just technical effectiveness but also impacts on academic integrity, pedagogical
  values, and environmental sustainability." (same PDF p26). Planned metrics list (p25): "the rates of participation in AI literacy training programs, and overall user satisfaction".
  Attitude survey: Kim et al. 2025 (below, S7) "surveyed 982 students and 76 faculty" (perceptions; TLOS-funded).
- S1 documents:
  1. July 2025 (cover) / "v1.0-Sep-2025" (file name), committee report, "Responsible and Ethical Artificial Intelligence Framework for Virginia Tech - Virginia
     Tech AI Working Group Final Report" (sponsors: Provost, EVP/COO): https://ai.vt.edu/content/dam/ai_vt_edu/Responsible-and-Ethical-AI-Framework-for-Virginia-Tech-(v1.0-Sep-2025).pdf
  2. Principles (guidance; "They are not ratified university policy."), page last updated 23 Sep 2026: https://ai.vt.edu/guidance/principles.html ;
     PDFs https://ai.vt.edu/content/dam/ai_vt_edu/Virginia-Tech-Responsible-and-Ethical-AI-Principles.pdf
  3. Undated, guidance "Using AI for Teaching": https://ai.vt.edu/index/teaching.html ; undated, guidance "Using AI for Learning" (students): https://ai.vt.edu/index/learning.html
  4. Last updated 17 Aug 2026, TLOS guidance "Considering Generative AI at Virginia Tech": https://tlos.vt.edu/resources/generative-ai.html (same page also at provost.vt.edu/tlos-considering-generative-ai-at-vt.html)
  5. Undated, TLOS guidance "Using Generative AI in Assessments": https://tlos.vt.edu/resources/using-generative-ai-in-assessments.html
  6. Undated, statement, Graduate School Dean + TLOS: https://tlos.vt.edu/resources/generative-ai/graduate-school-statement.html
  7. "2025-26", OUAI syllabus requirements incl. three AI policy templates: https://honorsystem.vt.edu/resources/syllabus.html
  8. Oct 2025, guidance "Introduction to AI Literacy Guidelines": https://tlos.vt.edu/content/dam/tlos_vt_edu/assets/pdf/Introduction-to-AI-Literacy-Guidelines-Oct2025.v1.pdf
  9. Undated, CETL resource page "AI Resources": https://teaching.vt.edu/hub/ai-resources.html
  10. Committee charter (undated), IT Governance AI Working Committee: https://it.vt.edu/content/dam/it_vt_edu/governance/IT-Governance-AI-Working-Committee-Charter.pdf
  11. Aug 2026, vision statement, AI Futures Working Group: https://strategicaffairs.vt.edu/AI_Futures.html (reached via ai.vt.edu/about/ai-futures-working-group.html)
  12. Pilot page, last updated 16 Jun 2026: https://tlos.vt.edu/training-tools/chatgpt-edu-pilot.html
  (Research-only, outside teaching scope: "Considerations for the Responsible and Ethical Use of AI in Research", drafted 25 Nov 2025, revised 14 Oct 2026,
  https://www.research.vt.edu/research-support/forms-guidance/sirc/considerations-responsible-ethical-use-ai.html - not used below.)
- S2 evidence cited:
  Framework report: peer-reviewed studies cited 0. Own surveys: "a spring 2025 faculty survey (n = 118)" (p6; response rate not stated; detailed data
  "see supplementary document", not located); ChatGPT Edu pilot "pre- and post-deployment surveys" (p43; 425 participants; respondent n and response rate not
  printed); Copilot pilot via external vendor Cloudforce, "A cohort of 177 faculty and staff" (p19). Instrument: DEC readiness assessment, "Formal reliability or
  validity studies have not yet been released." (p6). Other reports: global figures uncited, e.g. "By 2024, AI adoption reached 72-78% globally" (p36, no source).
  AI Literacy Guidelines: 2 sources, both Digital Education Council (2024 student survey; 2025 framework); 0 peer-reviewed.
  TLOS "Considering Generative AI": 0 studies named; "several studies have demonstrated" (uncited); resources listed are books, newsletters, blogs; own survey
  linked: "VT Fall 2024 student AI literacy survey" (Tableau; n UNREAD).
  CETL AI Resources: 1 peer-reviewed study (Kim et al., Innovative Higher Education 2025, own faculty, n = 982 students / 76 faculty; response rate not stated).
  ai.vt.edu teaching/learning pages, Graduate School statement, OUAI syllabus page, TLOS assessments page: none cited.
- S3 data released: PARTIAL - aggregates printed in the framework report (pilot percentages, p44-46); one survey instrument printed (Kim et al. 2025:
  "The specific survey items are listed in the Appendix of this article"); no microdata ("Data cannot be shared openly to protect the privacy of human subjects.",
  Kim et al.). Fall 2024 student survey dashboard UNREAD (aggregate level unknown). Faculty survey n = 118: no data or instrument found.
- S4 recommendations naming an evidence item: 2 of 59 (both name internal VT items; 0 name a peer-reviewed study or a learning outcome). Hand count by agent; Bones recount pending.
  Framework five strategic recommendations (p1-2): 2 of 5 ("Revise Five Critical Policies" -> "as detailed in Appendix B.3" policy review; "Pilot Investment" ->
  "ChatGPT Edu (see Appendix C for complete results) and Microsoft 365 Copilot (see Section 7.1 for pilot outcomes)"); Framework C.8.1 deployment
  recommendations: 0 of 6; TLOS "Considering Generative AI" numbered recommendations: 0 of 6 (no.4 refers to "several studies", none named);
  ai.vt.edu Teaching page: 0 of 16 (each tagged with a Principle, no evidence); ai.vt.edu Learning page: 0 of 13; Graduate School statement guidelines: 0 of 5;
  OUAI "Developing an AI Policy" considerations: 0 of 8.
- S5 testable claims (stated as fact):
  1. "AI can help you work, but it cannot help you learn something you never practiced." (https://ai.vt.edu/index/learning.html) - uncited.
  2. "several studies have demonstrated that they can generate both “false positives” and “false negatives” when attempting to detect AI-created content,
     especially when applied to the work of non-native English speakers." (https://tlos.vt.edu/resources/generative-ai.html) - uncited (no study named).
  3. "When students understand the pedagogical reasons behind course policies, they will be more likely to accept specific guidelines." (same TLOS page) - uncited.
  4. "Employers are becoming skilled at detecting AI-generated cover letters." (https://ai.vt.edu/index/learning.html) - uncited.
  5. "Consider these current realities at Virginia Tech: In the classroom, surveys show that over 80% of students regularly use AI tools like ChatGPT for
     coursework" (AI Literacy Guidelines PDF p1) - cited: "(Digital Education Council, 2024)" (Global AI Student Survey 2024; not a VT survey per its listed title).
- S6 AI-detector stance:
  TLOS: "Virginia Tech has not licensed or endorsed any specific platforms for detecting generative AI, and TLOS recommends caution when using these tools."
  and "the Office for Undergraduate Academic Integrity does not accept AI detection reports as a form of evidence for Honor Code cases." (https://tlos.vt.edu/resources/generative-ai.html, updated 17 Aug 2026)
  OUAI: "The OUAI requires human analysis of any work being reported as AI plagiarism, although AI detector evidence may be included in a report." (https://honorsystem.vt.edu/resources/syllabus.html, "2025-26")
  Framework: "the unreliability of AI detection tools creates enforcement dilemmas" (framework PDF p26) - uncited.
  (The two quotes on OUAI handling of detector reports are printed on two VT pages as above; no reconciliation found.)
- S7 own-faculty studies with released data: NONE FOUND with released learning data.
  1. Kim, Klopfer, Grohs, Eldardiry, Weichert, Cox, Pike, "Examining Faculty and Student Perceptions of Generative AI in University Courses", Innovative Higher
     Education 2025, https://doi.org/10.1007/s10755-024-09774-w (VTechWorks https://hdl.handle.net/10919/124367). Funding verbatim: "This research was supported by
     Technology-Enhanced Learning and Online Strategies (TLOS) at Virginia Tech." Data: "Data cannot be shared openly to protect the privacy of human subjects."
     Instrument: items in article appendix. Outcome type: perceptions (no learning measure).
  2. Wang, Trimble, Brown, "DevCoach ...", FSE Companion '25, https://doi.org/10.1145/3696630.3727255 (user study n = 20). Data link: none; instruments released
     (https://github.com/wangt7/DevCoach/tree/main/UserStudyMaterials : "Post Survey.pdf", "Quiz1.pdf", "Quiz2.pdf"). Funding line: none found in extracted text.
  3. Wang, Wu, Liu, Brown, Chen, "Generative Co-Learners ...", https://doi.org/10.1145/3701198 (n = 12). Data link: none found. Acknowledgments verbatim:
     "Thanks to all participants for their involvement in the user study." (no funding line).
  4. Kaufman 2026, "Designing for Honest AI Use: What Happens When Students Must Disclose?" (lightning talk, abstract only, https://hdl.handle.net/10919/143745): practice report, no data.
  Not opened (metadata only): Jelson & Lee 2024 (hdl 10919/121529; abstract describes a planned study), Tang et al. SPHERE 2025 (hdl 10919/137115; n = 20, instructors).

## Notes (facts only, for the recount)
- ChatGPT Edu pilot participant count printed three ways: "425 full-time employees and graduate assistants" (framework p43); "provided access to 480 employees and
  graduate students" (TLOS 2024-25 Annual Report, https://tlos.vt.edu/assets/pdf/2024-25-TLOS-Annual-Report.pdf); "up to 500 full-time university employees and
  graduate assistants selected for the pilot" (TLOS pilot page, a cap).
- Framework dated "July 2025" on its cover; file name "v1.0-Sep-2025"; governance page: "published September 2025".
- Framework "Pilot results" are employee productivity self-reports; no student learning outcome appears in Appendix C.

## UNREAD
- https://public.tableau.com/app/profile/ellie.kohler/viz/AIAssessmentSurvey/AILiteracySurvey (Fall 2024 student AI literacy survey, via tinyurl.com/ailitdashboard; script-rendered, no text)
- Framework "supplementary document “Implementation Guides and Background Research.”" (holds faculty survey n = 118 detail; no URL found)
- https://news.vt.edu/notices/2025/05/it-copilot-study-report-next-steps.html (404; cited by framework for Copilot pilot results)
- https://governance.vt.edu/ResolutionTracker/Completed and /UnderReview (resolution list script-loaded; AI-related resolutions not checked)
- https://virginiatech.sharepoint.com/sites/VTFacultySenate/ (login)
- https://search.vt.edu/search?q=rolai (script-rendered; Rolai pilot outcome page not found)
- https://tlos.vt.edu/content/dam/tlos_vt_edu/assets/pdf/AI-Literacy-Guidelines-Presentation-Oct2025.v1.pdf (downloaded, not read)
- https://event.fourwaves.com/aiteaching/abstracts/26de5aa4-4767-40de-8531-30e52d20e8a0 (TLOS AI teaching event abstracts; not opened)
- https://aiteaching.vt.domains/ subpages (Summer 2024 FLC; home page only)
- https://4help.vt.edu/sp?id=kb_article&sysparm_article=KB0015426 (ChatGPT Edu KB; not opened)
