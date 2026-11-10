# Tested

Heuremen LLC · https://indahl.ai/oy

On 2026-11-10 the zip was unzipped into an empty folder and every CSV was opened with pandas 2.3.3 on Python 3.9 at default settings. The list, findings and text were compared with the OY page as built for release that day, and the school pages and their files are unchanged from the test of 2026-11-01, when all 389 live school pages were fetched and read with lxml 6.1 and Beautiful Soup 4. Every count and number below matched.

- Headline: 10 of 148 listed colleges and universities with a published, measured grade or learning outcome of their own AI policy, guidance, tool or pilot under the rule written before any school was read, and 3 to 4 of 148 under the rule set after the first 41 schools were read, 148 rows in `oy_list.csv` and 8 chatbot citations in `oy_chatbot_citations.csv`
- Table of findings: 16 findings with the Rows text as printed, and the 311 institutions or studies named under them with their links and their what we found text
- Chatbot cited as a source: 8 of 148, with institution, document, text and source address of each row
- Measured its own policy, guidance or a centrally provided tool: 6 of 148
- Outcome reported without counts: 3 of 148
- Plans to measure its own policy: 47 of 148
- Surveys of use or attitudes, no measure of its own policy: 71 of 148
- None found: 17 of 148, one of them our own row
- Not reached, because the pages refused our reader or need a login: 4 of 148
- Released nothing: 76 of 114, and summary tables or an instrument only: 38 of 114, with 114 read and 34 not read
- Pilots run or funded by the institution, results read: 10 of 148, and the list shows 12 pilot cells, of which 2 say the results were not read
- The list: institution, institution link, first document cited and its link, measures, released data, pilot text and pilot link of all 148 rows equal the page table
- Private baccalaureate colleges: 389 rows with school, state, site text, sentences, course titles and read in full equal to the page table, and 41 schools marked read in full
- School pages: all 389 live pages have the same name and federal ID as the CSV, and every sentence and course title with its address equals `oy_school_sentences.csv` (61 rows) and `oy_school_course_titles.csv` (291 rows)
- Sentences found are 62 and sentences shown are 61, because one school page says it shows 1 of 2. Course titles found and shown are both 291

Where the page shows a dash, the CSV cell is blank. At default settings pandas reads a blank cell as missing. No cell in any file is text that pandas reads as missing, such as NA or None.

The file `verify.py` compares every CSV cell with the JSON, and recomputes the counts the files state about each other, such as the institutions under each finding and the sentences and course titles of every school.

Not tested: Excel or LibreOffice. The outside links in the rows were compared with the page and were not opened again, so a document that has moved since is not detected here.
