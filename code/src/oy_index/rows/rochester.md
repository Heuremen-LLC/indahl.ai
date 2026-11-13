## Row - University of Rochester (built 25 Oct 2026; not an Ivy, no SWEEP_ivies.md section; SCHOOL_LIST batch 14)
Quotes are verbatim from page text pulled with curl and tags stripped (HTML), from the sites' own WordPress JSON (`/wp-json/wp/v2/posts`, content field), or from pypdf text extraction (AS&E PDF). Paraphrase-only fetch output was not used for quotes. News items are pointers and are not counted.

### Search log (same procedure as every row)
Window 2023 to Oct 2026, English, rochester.edu primary documents first; news only as pointers.
- SEARCH PASS STILL OWED: the session web-search tool was exhausted on the first query ("University of Rochester generative AI teaching guidance task force report provost" - not run). All finding below was by fetching rochester.edu hub pages and following links, plus the sites' own search (newscenter and provost WordPress search API), plus Crossref metadata API (query.affiliation "University of Rochester"). rochester.edu/sitemap.xml and /college/sitemap.xml return 404. OpenAlex API: daily budget exhausted (not used).
- Hub pages read: https://www.rochester.edu/ai/ ; https://www.rochester.edu/provost/gen-ai-education/ ; https://www.rochester.edu/college/teaching/index.html (+10 subpages: teaching-guidance x4, workshops, communities, innovation grants, ed-tech tools, online resources, teaching-guidelines) ; https://www.rochester.edu/college/honesty/ (+ about/reports, instructors/prevention, violations, resources, ai-misuse, clear-ai-policies, students/faq, tips, policy/index, policy/quiz3) ; https://writing.rochester.edu/undergraduate/gen-ai.html ; https://www.rochester.edu/college/learningcenter/ ; https://tech.rochester.edu/services/artificial-intelligence-ai/ ; https://www.rochester.edu/university-research/ai-research-committee/ .
- (1) Provost/senate/committee reports: provost GenAI in Education guidelines (AI Council education subcommittee) read in full; provost news search "AI", "generative" -> 2025-03-03 data-security memo, 2026-06-24 Gresens appointment, 2026-08-25 Cetin appointment, 2026-09-18 initiatives update - all read. No faculty-senate AI report located (faculty senate pages not located from hubs).
- (2) Teaching-centre guidance: College Teaching Center pages grepped for AI/artificial/generative/ChatGPT/detect: only a "Generative Artificial Intelligence Teaching Group" (communities page) and a link to the provost guidelines (teaching-guidelines page). Academic Honesty site: AS&E Instructors' Guide PDF (Feb 2023), "Addressing AI Misuse", "Developing Clear Course GenAI Policies", Quiz 3. WSAP "Writing and Gen AI" page (presentation embedded; not read, see UNREAD).
- (3) Institution-run surveys with n: newscenter search "AI survey", "ChatGPT survey"-type queries ("generative AI survey", "AI survey", "AI literacy", "AI council") - no institution-run student/faculty AI survey found. Student newspaper (campustimes.org) search API returned non-list (not searched).
- (4) Evaluation of own policy/tools/pilots: newscenter search "AI pilot", "AI tutor", "Copilot", "Gemini", "Claude" - none for teaching. Provost memo names chat.rochester.edu; no usage or outcome report located. Crossref affiliation queries ("generative AI students learning", "medical education generative AI", "AI tutor course students", "nursing students artificial intelligence", "undergraduate course ChatGPT learning outcomes", "survey students artificial intelligence use", "academic integrity artificial intelligence", "writing course generative AI", "teacher education artificial intelligence") -> one School of Nursing course study (S0/S7).
- (5) Detector stance: provost guidelines; honesty "Addressing AI Misuse"; AS&E Feb 2023 PDF read in full; newscenter search "AI detection" (no teaching hit).
- (6) Faculty empirical studies with released data: Crossref queries above; newscenter "large language model students", "ChatGPT students".

### S0 self-evaluation: MEASURED (one faculty course study, School of Nursing; n not read - full text paywalled)
- Receipt: Dzikowicz, DiPaulo, Serwetnyk, Marconi, Carey (all "School of Nursing, University of Rochester"), Nurse Educator 2026-05-14, doi 10.1097/NNE.0000000000002178, abstract via Crossref: "GoodNurse was then integrated into a 4-credit ECG course; AI usage, satisfaction, and grades were analyzed." ; "In the course, 43% of students used GoodNurse, achieving higher grades (95.1 ± 2.5%) than nonusers (88.8 ± 5.9%; P =.0048)".
- Comparison = users vs nonusers within one course (usage self-selected per abstract wording "43% of students used"); total n UNREAD.
- Institution level (provost guidelines, implementation recommendations): PLANNED ONLY. Receipt https://www.rochester.edu/provost/gen-ai-education/ : "Initiate targeted pilot programs to explore creative uses of GenAI in teaching, learning, and assessment." ; "These pilot programs can test new ideas, address challenges, and inform best practices for broader adoption across the university."
- https://www.rochester.edu/provost/gresens-named-to-new-academic-honesty-post/ (2026-06-24): "addressing emerging challenges, such as the ethical use of artificial intelligence in teaching and research and leveraging data-informed approaches to guide policy development and institutional practices."
- No outcome measure, n or comparison found for the provost guidelines, chat.rochester.edu, or the Teaching Center GenAI group.

### S1 public AI-in-learning documents
| Date | Type | Title | URL |
|---|---|---|---|
| 2023-02 (PDF header "February 2023"; metadata 2023-02-23) | guidance (AS&E Honesty Liaisons; Board on Academic Honesty; Teaching Center; WSAP) | AS&E Instructors' Guide to Using ChatGPT/AI in the Classroom | https://www.rochester.edu/college/honesty/assets/pdf/chatgpt-ai-guidance-for-instructors.pdf |
| 2024-12-02, revised 2025-03-07 and 2025-05-16 (page text); page modified 2025-09-25 | university guidelines (AI Council education subcommittee, Office of the Provost) | Generative AI Use in Education | https://www.rochester.edu/provost/gen-ai-education/ |
| 2025-03-03 | provost memo | Responsible Use of AI Tools and Institutional Data Security | https://www.rochester.edu/provost/responsible-use-of-ai-tools-and-institutional-data-security/ |
| undated (cites ICAI presentation of 2026-06-25) | guidance (Academic Honesty, SAS/Hajim) | Addressing AI Misuse | https://www.rochester.edu/college/honesty/instructors/ai-misuse.html |
| undated (cites College Board May 2025 brief) | guidance (Academic Honesty) | Developing Clear Course GenAI Policies | https://www.rochester.edu/college/honesty/instructors/clear-ai-policies.html |
| undated | student quiz (Academic Honesty) | Quiz #3 Online Learning Tools | https://www.rochester.edu/college/honesty/policy/quiz3.html |
| undated | teaching-centre program listing | Teaching Communities (Generative Artificial Intelligence Teaching Group) | https://www.rochester.edu/college/teaching/programs-services/communities.html |
| 2026-08-25 | appointment announcement | Mujdat Cetin Named Inaugural Associate Vice President and Vice Provost for Artificial Intelligence | https://www.rochester.edu/provost/mujdat-cetin-named-inaugural-associate-vice-president-and-vice-provost-for-artificial-intelligence/ |
- Policy text (not AI-specific document): SAS/Hajim/Simon Academic Honesty Policy lists "Usage of material generated by AI tools (Grammarly, ChatGPT, DALL-E, translation software, or similar) that is not allowed by the instructor" (https://www.rochester.edu/college/honesty/policy/index.html).

### S2 evidence cited
- Provost guidelines: 11 numbered references. Peer-reviewed 0. Own surveys 0. Government/multilateral 3 ([1] National AI Research Resource Task Force 2023; [7] NIST AI 600-1; [8] UNESCO). Survey/industry reports 3 ([3] CHLOE 9 report 2024, Quality Matters; [5] Anthology paper; [6] Inside Higher Ed PDF). OER 1 ([4] AI Hacks for Educators, UCF). Own policies 3 ([9]-[11]). Descriptive note 1 ([2]).
- Addressing AI Misuse: peer-reviewed 1 (Bassett et al., "Heads we win, tails you lose: AI detectors in education", J Higher Education Policy and Management 2026, doi 10.1080/1360080X.2026.2622146; linked as "Heads I Win, Tales You Lose"). Other institutions' guidance 11 (named list). Conference presentation 1 (ICAI 2026-06-25). Own surveys 0.
- Developing Clear Course GenAI Policies: other report 1 (College Board AI research brief, high-school students). Other institutions' policies 3 (Syracuse, CMU, Harvard). Peer-reviewed 0.
- AS&E Feb 2023 guide: peer-reviewed 0; other institutions 2 (Georgetown CNDLS page; UCSD Academic Integrity Office message); one published rubric named (Ash and Clayton [2004]); own surveys 0.
- Quiz 3, Teaching Center listing, provost memo, Cetin announcement: none.

### S3 data released: NONE (AI-specific)
- No microdata, aggregates or instrument for any AI-in-learning document.
- Related, not AI-specific: Academic Honesty "Reports and Statistics" publishes aggregate case counts by term F21-S26 (https://www.rochester.edu/college/honesty/about/reports.html); infraction categories listed are "Fabrication and Falsification", "Giving Unauthorized Aid", "Plagiarism", "Receiving, Using, or Having Access to Unauthorized Aid", "Unauthorized Recording...", "Misconduct in Group Projects" - no AI category.

### S4 recommendations naming an evidence item: 1 of 40
- Provost guidelines: 0 of 23 (12 instructor guidelines, 6 student guidelines, 5 implementation recommendations). The student honesty guideline cites [9][10][11] (own policies, not evidence). E.g. "Approach GenAI Detection Tools Cautiously" carries no citation.
- Addressing AI Misuse: 0 of 6 headed steps (Anticipate problems; Attempt to verify learning; Inform the Board; Prepare for the conversation; Talk with the Student; Report your findings). Note 3 (detector, not a headed step) names the Bassett et al. article.
- Developing Clear Course GenAI Policies: 1 of 1 ("it is imperative that faculty set clear expectations for AI use", premise footnoted to the College Board brief).
- AS&E Feb 2023 guide: 0 of 10 name a study (5 "Be ..." expectations + 5 teaching options); 1 names another institution (UCSD); 1 names a rubric (Ash and Clayton 2004).

### S5 testable claims (stated as fact)
1. "GenAI detection tools are unreliable, biased, easily defeated, and unable to provide definitive evidence of academic honesty policy violations." - provost guidelines - uncited.
2. "students are by definition learners for whom verifying the accuracy of AI outputs is more challenging and time-consuming than it is for experts." - provost guidelines - uncited.
3. "clearly communicating expectations and direct conversations with students are more effective for dealing with issues of AI misuse in class than relying on AI detectors." - Addressing AI Misuse - uncited (page says practices "gathered from guidance found at" 11 institutions and an ICAI presentation).
4. "Although there are better and worse AI detectors, their probative value, in general, is quite low. ... AI-humanizers can outwit the detectors." - Addressing AI Misuse - cited: Bassett et al. 2026, doi 10.1080/1360080X.2026.2622146.
5. "Out-of-class assignments are the most susceptible to unauthorized AI use" - Addressing AI Misuse - uncited.

### S6 AI-detector stance
- Provost guidelines (https://www.rochester.edu/provost/gen-ai-education/): "If instructors use GenAI detection tools in a course, they should disclose to students when and how the software will be used. Instructors should avoid using GenAI detection software as the sole basis for an academic honesty policy violation"
- Addressing AI Misuse (https://www.rochester.edu/college/honesty/instructors/ai-misuse.html): "The University of Rochester does not endorse or recommend any AI Detector software." ; "do not submit personally identifiable information to an AI-detector, as this may constitute a FERPA violation."

### S7 own-faculty studies with released data: NONE FOUND
- Dzikowicz et al. 2026, "Generative AI for ECG Interpretation Education: Impact on Nursing, Student Performance, and AI Model Accuracy", Nurse Educator, https://doi.org/10.1097/NNE.0000000000002178 . Data link: not located (full text paywalled at ovid.com). Funding line: UNREAD (Crossref lists no funder).
- Gegg-Harrison & Quarterman 2024, "AI Detection's High False Positive Rates and the Psychological and Material Impacts on Students", book chapter in Academic Integrity in the Age of Artificial Intelligence (IGI Global), https://doi.org/10.4018/979-8-3693-0240-8.ch011 . Abstract: "A small corpus study is presented demonstrating much higher than advertised rates of false positives across a range of popular "AI detection" tools." Data link: not located. Funding line: none in Crossref.
- Gegg-Harrison 2026, "Writing About and With (or Without) AI (WRTG/ENGL/DMS 290B)", chapter in Teaching AI (EdTech Books), https://doi.org/10.59668/2869.30077 - course description chapter; page renders by script (UNREAD).
- CARD ONLY: Ramji, Fenning, Lipomi 2026, "Teaching with an AI Tutor: An Undergraduate Case Study in Nanoengineering", Chemistry of Materials, doi 10.1021/acs.chemmater.6c00883 (Lipomi lists UC San Diego and University of Rochester); Crossref funder: "Materials Research Science and Engineering Center, University of California, San Diego" award "DMR-2011924" (NSF award) -> government grant.
- Not counted (not a learning study): 10.1097/ALN.0000000000005181 (LLM performance on an anesthesiology CE exam, UR School of Medicine).
- News pointer only: https://www.rochester.edu/newscenter/how-to-use-ai-in-teaching-and-learning-707122/ (2026-06-10, Warner School faculty on K-12 classroom AI use; no study or data named).

### UNREAD (6)
- https://journals.lww.com/10.1097/NNE.0000000000002178 (full text paywalled; total n, data availability, funding not read)
- https://edtechbooks.org/teaching_ai/WRTG_ENGL_DMS_290B (renders by script; no text returned)
- https://writing.rochester.edu/undergraduate/gen-ai.html (WSAP presentation embedded; only intro text read)
- https://rochester.app.box.com/s/4axjoc5nszk4lnkdyiz698hj6iwh198m (WSAP "honesty with online learning tools" PPT, Box; not opened)
- https://tech.rochester.edu/services/artificial-intelligence-ai/ (tool list renders by script; tool names not read)
- https://docs.google.com/document/d/1RMVwzjc1o0Mi8Blw_-JUTcXv02b2WRH86vw7mi16W3U/edit (external "Syllabi Policies for AI Generative Tools", linked from provost page; not opened)
- NOT LOCATED: faculty senate AI documents; any usage/outcome report for chat.rochester.edu; Teaching Center GenAI group outputs; Simon, URMC/SMD, Nursing, Eastman, Warner school-level AI teaching policies (not probed). Web-search pass owed for all six items.
- Bones (25 Oct ~13:35): GoodNurse abstract read (OpenAlex; PubMed 42139039): "In the course, 43% of students used GoodNurse, achieving higher
  grades (95.1 ± 2.5%) than nonusers (88.8 ± 5.9%; P = .0048)". Course n not in the abstract. Backed out from the printed means, SDs, 43% and
  P (t-tests, Welch and pooled): P = .0048 fits a course of about 20-24 students (refereed range). INFERRED, not printed; test not stated in the abstract (a rank test would change the fit); full text still UNREAD.
  Users chose to use the tool (no assignment), so the gap carries selection. Pilot stays HELD.
