# Tested

Heuremen LLC · https://indahl.ai/oy

On 2026-11-01 the zip was unzipped into an empty folder and every CSV was opened with pandas 3.1.0 on Python 3.14 at default settings. The live OY page and all 389 live school pages were fetched the same day and read with lxml 6.1 and Beautiful Soup 4. Every count and number below was compared with the live pages and matched.

- Headline: 0 of 148 listed colleges and universities with a published, measured learning outcome of their own AI policy, 148 rows in `oy_list.csv` and 8 chatbot citations in `oy_chatbot_citations.csv`
- Table of findings: 14 findings with the Rows text as printed, and the 297 institutions or studies named under them with their links and their what we found text
- Chatbot cited as a source: 8 of 148, with institution, document, text and source address of each row
- Measured its own policy or tool: 3 of 148
- Outcome reported without counts: 3 of 148
- Plans to measure: 47 of 148
- Usage or attitude surveys only: 74 of 148
- None found: 21 of 148, one of them our own row
- Released nothing: 76 of 114, and summary tables or an instrument only: 38 of 114, with 114 read and 34 not read
- Pilots run or funded by the institution, results read: 10 of 148, and the list shows 12 pilot cells, of which 2 say the results were not read
- The list: institution, institution link, policy link, measures, released data, pilot text and pilot link of all 148 rows equal the page table
- Private baccalaureate colleges: 389 rows with school, state, site text, sentences, course titles and read in full equal to the page table, and 41 schools marked read in full
- School pages: all 389 live pages have the same name and federal ID as the CSV, and every sentence and course title with its address equals `oy_school_sentences.csv` (61 rows) and `oy_school_course_titles.csv` (291 rows)
- Sentences found are 62 and sentences shown are 61, because one school page says it shows 1 of 2. Course titles found and shown are both 291

Where the page shows a dash, the CSV cell is blank. At default settings pandas reads a blank cell as missing. No cell in any file is text that pandas reads as missing, such as NA or None.

The file `verify.py` compares every CSV cell with the JSON, and recomputes the counts the files state about each other, such as the institutions under each finding and the sentences and course titles of every school.

Not tested: Excel or LibreOffice. The outside links in the rows were compared with the page and were not opened again, so a document that has moved since is not detected here.
