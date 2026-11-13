"""Findings sections for the OY matrix page. Facts, numbers and sources only (his rule 25 Oct: no commentary). Every number here has a
ledger row (ledger/ledger.jsonl ids oy.*); LEDGER below is the list add_ledger.py reads."""
import html
E = html.escape
A = lambda u, t='source': f'<a href="{E(u)}">{t}</a>'
EXTRA_TALLY = [  # rows appended to the top findings table (label, value)
 ('Released microdata from an institution-run survey or evaluation of AI use or outcomes (of 114 read)', '0'),
 ('Released summary tables or an instrument only (of 114 read)', '38'),
 ('Released nothing (of 114 read)', '76'),
 ('Pilots run or funded by the institution, results read', '10'),
]
CHATBOT = [  # institution, document, quote, url
 ('Mississippi State University', 'Provost&rsquo;s Generative AI Working Group report, November 2023, p. 15',
  '&ldquo;Creating transparent instructional designs significantly boosts learning outcomes, especially for first-generation students &hellip; (ChatGPT, 2023)&rdquo;',
  'https://www.provost.msstate.edu/sites/www.provost.msstate.edu/files/2023-11/AI%20Working%20Group%20Report.pdf'),
 ('Montana State University', 'Center for Faculty Excellence, &ldquo;Information about Generative AI&rdquo;',
  '&ldquo;It&rsquo;s important to note that the information I provided is based on my training data available up until September 2021 &hellip; Source: OpenAI. (2023). ChatGPT (Jun 14 version) [Large language model].&rdquo;',
  'https://www.montana.edu/facultyexcellence/teaching-advising/courseclassdesign/genai/'),
 ('Tulane University', 'Newcomb-Tulane College Academic Integrity Annual Report 2024&ndash;2025',
  '&ldquo;According to ChatGPT, the number of college students who are asking it to write papers or answer exam questions for them &lsquo;increases each day&rsquo; (ChatGPT, July 5, 2025).&rdquo;',
  'https://tulane.box.com/shared/static/ttkrxglfx1cq5zj5b2qz9h64zx7c7ezg'),
 ('University of Illinois Chicago', 'Center for the Advancement of Teaching Excellence, &ldquo;AI writing tools&rdquo;',
  '&ldquo;Students can practice using new vocabulary words in context by creating their own sentences or paragraphs (OpenAI, 2023a).&rdquo;',
  'https://teaching.uic.edu/ai-writing-tools/'),
 ('University of Nevada, Las Vegas', 'ChatGPT policy page',
  '&ldquo;we asked the following question directly to ChatGPT: How might students use ChatGPT? According to ChatGPT the example below highlights potential applications from the student perspective&rdquo;',
  'https://www.unlv.edu/policies/chatgpt'),
 ('Washington University in St. Louis', 'Center for Teaching and Learning handout, &ldquo;Establishing the Role of AI in Your Classes&rdquo;',
  '&ldquo;This table will help clarify the roles of AI and humans in your class &hellip;&rdquo; (OpenAI, 2023)',
  'https://ctl.wustl.edu/wp-content/uploads/2023/08/Establishing-the-Role-of-AI-in-Your-Classes-Handout.pdf'),
 ('Wesleyan University', 'Library guide &ldquo;ChatGPT&rdquo;',
  '&ldquo;According to Claude an LLM (Large Language Model) &lsquo;is a type of artificial intelligence trained to understand and generate human language&hellip;&rsquo;&rdquo;',
  'https://libguides.wesleyan.edu/chatgpt'),
 ('West Virginia University', 'Teaching and Learning Commons AI page (archived 23 May 2024)',
  '&ldquo;Is artificial intelligence a good thing? Well, according to ChatGPT: &hellip;&rdquo;',
  'https://web.archive.org/web/20240523153624/https://tlcommons.wvu.edu/ai'),
]
RECOUNTS = [  # study, what rebuilt / what the files show, url
 ('Bastani et al., PNAS 2025 (University of Pennsylvania)', 'Table 1 rebuilds exactly. The exam effect, &minus;0.054 (&minus;17%), is significant under clustered standard errors (p &asymp; 0.02) and not under a wild cluster bootstrap (p &asymp; 0.11, 13 GPT-Base classrooms).', 'https://doi.org/10.1073/pnas.2422633122'),
 ('Cornell University, Spring 2025 generative AI surveys', 'An item count of 2,029 against 1,988 respondents. Group labels total 2,539 on a base the files do not identify.', 'https://academicinnovation.cornell.edu/gen-ai/generative-ai-impact-on-learning-spring-2025-surveys/'),
 ('Kestin et al. 2025 (Harvard University)', 'Post-test +0.65 [+0.40, +0.91] within the 122 students with both lessons. The interval is a 95% percentile bootstrap over students, 5,000 resamples, in points on the post-test score. Topic and week are confounded. 72 of 194 &ldquo;eligible&rdquo; students have one lesson row. The printed &ldquo;M&rdquo; values are medians.', 'https://github.com/HarvardAItutor/Study-Data-v4'),
 ('Lin, EdArXiv 2026 (mj4bu)', 'GPT-4o re-grader (gpt-4o-2024-08-06, temperature 0, three calls per answer, majority label) on Python function designs: after a synonym swap, 47 of 100 passing answers fail, against 7% for unchanged copies. Every printed figure rebuilds.', 'https://osf.io/preprints/edarxiv/mj4bu'),
 ('MIT committee report 2026', 'No peer-reviewed learning-outcome study is cited. 20 of 33 recommendations name no evidence, counting an evidence item as named when the report cites it in the same subsection. The headline 25% is a student-newspaper survey.', 'https://sites.mit.edu/ai-use/ai-committee-final-report-aug-13/'),
 ('Oppenheimer et al., IJAIED 2025 (Carnegie Mellon University)', 'Grades rebuild. 89% at the scale ceiling. The printed t(177) = 4.25 carries the p of a paired test, t(26) = 2.97, p = .006.', 'https://doi.org/10.1007/s40593-025-00521-6'),
 ('Pardos &amp; Bhandari, PLOS ONE 2024 (UC Berkeley)', 'Means rebuild exactly. &ldquo;Equivalent&rdquo; holds only at margins of about 13.4 points or wider. The ChatGPT group starts 10&ndash;12 points lower.', 'https://doi.org/10.1371/journal.pone.0304013'),
 ('UMD Virtual Study Assistant trial, Oct 2026', 'The paper reports final grades lower by 0.37 SD in the exact-match sample and by 0.27 to 0.37 SD across samples. Our division of its Table 3 by the control SD gives &minus;0.32 without controls and &minus;0.37 with controls in the exact-match sample. The OSF pre-registration lists 41 instructors and 3,387 consenting students. The paper analyses 30 and 2,379.', 'https://edworkingpapers.com/sites/default/files/ai26-1598.pdf'),
 ('UMN, UNC, UCI expert consensus report 2026', 'Of the 65 learning processes, 42 reached consensus on enhancement, vulnerability or both, as the report states. Applying the report&rsquo;s own evidence rule to its 65 per-process tables, 0 of 65 reach consensus on evidence. That total is our count from the tables.', 'https://www.cehd.umn.edu/AI-expert-consensus-report-2026'),
 ('University of Chicago, use of Jabarian &amp; Imas 2025', 'The study rebuilds. For the Pangram detector, 0 of 1,992 human texts flagged at the paper&rsquo;s 0.5 cut and, by our count, 1 of 1,992 at the vendor&rsquo;s &ldquo;Possibly AI&rdquo; label. The corpus holds no student writing.', 'https://github.com/brianjabarian/DetectionAI'),
]
OWN_NUMBERS = [  # institution, finding, url
 ('George Washington University', 'Faculty Senate resolution SR 24/8. The text prints &ldquo;a 476.2% increase in the &lsquo;cheating&rsquo; category&rdquo; and its own table prints 472.6%. The table prints 84.64% of reports as cheating, and 209 of 256 is 81.64%. The table has no AI category.', 'https://facultysenate.gwu.edu/sites/g/files/zaxdzs6626/files/2024-08/5-24-8_final_adopted.a.pdf'),
 ('St. John Fisher University', 'Abstract: blanket prohibition &ldquo;dropped sharply from 57% in the fall of 2023 to 23% in the fall of 2025.&rdquo; Its tables: any prohibition 57% to 59%. 25 of the 34 points fall at a change from one-choice to multi-choice forms.', 'https://joidat.scholasticahq.com/article/160147-from-caution-to-adoption-tracking-implementation-of-a-university-wide-ai-syllabi-policy'),
 ('University of Pennsylvania', 'Faculty Senate committee report on AI and student learning: no study cited, including Bastani et al., PNAS 2025, by Penn authors.', 'https://almanac.upenn.edu/uploads/media/061626-senate_supplement.pdf'),
]
THAT_SCHOOL = [  # institution, finding, url
 ('Clarkson University', 'ChatGPT as a writing coach in the first-year seminar: pre and post surveys, n = 64 and 53. Writing self-efficacy &ldquo;did not improve.&rdquo;', 'https://www.sciencedirect.com/science/article/abs/pii/S8755461525000106'),
 ('Denison University', 'Student survey series: 53% used AI for coursework in fall 2024, 78% in spring 2025, nearly 80% in October 2025. 55% agree AI in coursework &ldquo;undermines the value of a college education.&rdquo;', 'https://onetwentyseven.blog/2025/12/12/lots-of-students-use-ai-fewer-think-its-good-for-their-education/'),
 ('Elon University', 'Paired sections, &ldquo;must cite&rdquo; and &ldquo;no AI&rdquo; policies: 15 of 47 respondents in &ldquo;no AI&rdquo; sections and 36 of 72 in &ldquo;must cite&rdquo; sections report using AI on a coding assignment.', 'https://causeweb.org/cause/sites/default/files/ecots/ecots22/materials/Elon_eCOTS2026_AISyllabus_slides.pdf'),
 ('St. John Fisher University', '3,300+ syllabi coded over five semesters under its own AI syllabus policy: syllabi with no AI policy stated, 19.5% to 2.7%.', 'https://joidat.scholasticahq.com/article/160147-from-caution-to-adoption-tracking-implementation-of-a-university-wide-ai-syllabi-policy'),
]
def table(head, rows):
    th = ''.join(f'<th>{h}</th>' for h in head)
    return f'<div class="scroll"><table class="mtx"><thead><tr>{th}</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>'
def sections():
    return (f'<section><h2>Chatbot cited as a source</h2>{table(["Institution", "Document", "Text", "Source"], [(i, d, q, A(u)) for i, d, q, u in CHATBOT])}</section>'
            f'<section><h2>Recounted from released files</h2>{table(["Study", "From its files", "Source"], [(s, t, A(u)) for s, t, u in RECOUNTS])}</section>'
            f'<section><h2>Own documents, own numbers</h2>{table(["Institution", "Finding", "Source"], [(i, t, A(u)) for i, t, u in OWN_NUMBERS])}</section>'
            f'<section><h2>Studies by the school&rsquo;s own faculty or staff</h2>{table(["Institution", "Finding", "Source"], [(i, t, A(u)) for i, t, u in THAT_SCHOOL])}</section>')
