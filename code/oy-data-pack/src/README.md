# OY Data Pack

Heuremen LLC · https://indahl.ai/oy

The data behind the OY page at https://indahl.ai/oy and its school pages at https://indahl.ai/oy/school/, as files you can open in a spreadsheet or Python. OY lists what colleges and universities have published about AI in teaching and learning and about measuring their own AI policies, with a source link for every row. The OY pages publish these tables as web pages and not as data files. The files here are the tables of the pages as published on 2026-11-01, read out of the pages without changes to their text, as JSON and as CSV with one row per record. The list is as of {AS_OF}. The school pages were read on {READ_ON_DATE}. Pages that a school has moved or rewritten since can differ from what we quote.

## What is in each file

Chatbot citations (`json/oy_chatbot_citations.json`, `csv/oy_chatbot_citations.csv`): {N_CHATBOT} rows. Each has the institution, the document, the quoted text and `source_url`, the address of the document.

Findings (`json/oy_findings.json`): the table of findings of the page, with {N_FINDINGS} findings. `csv/oy_findings.csv` has one row per finding with the finding, the `rows` text as printed, such as 8 of 148, the `count`, the denominator `of` and a `note` when the finding has no institutions to list. `csv/oy_finding_institutions.csv` has one row per institution or study named under a finding: `name`, `url`, `kind` when the page marks the link as a journal article, a preprint or another kind of document, and `what_we_found` with `what_we_found_source_url` where the page gives them. A blank `url` is a row without a link, such as our own row.

The list (`json/oy_list.json`, `csv/oy_list.csv`): {N_LIST} rows, one of them our own. The columns are `institution` and `institution_url` (the document the page links from the name), `institution_url_kind`, `public_policy_or_guidance` with `public_policy_url`, `measures_own_policy`, `released_own_data`, `pilot_results` and `pilot_source_url`. A blank means the page shows no link or a dash.

Private baccalaureate colleges (`json/oy_schools.json`): {N_SCHOOLS} schools, one page each. `csv/oy_schools.csv` has one row per school with the federal ID in `unitid`, the Carnegie class, the school page address, the address of the school's site, the text about what the script read, `sentences_total` and `course_titles_total` as the table prints them, `read_in_full_label` for the schools whose pages we also read in full, and the notes printed on the school page. A blank in a total means the page shows a dash. The columns `sentences_json` and `course_titles_json` hold the lists of the school page as text. The same lists come as `csv/oy_school_sentences.csv` ({N_SENT} rows) and `csv/oy_school_course_titles.csv` ({N_COURSE} rows), one row per item with its `url`. A sentence ends in an ellipsis where the script cut it, as the page shows. The page shows at most the number it says in its note, and `sentences_total` gives the number found.

Page text (`json/oy_text.json`, `csv/oy_text_meta.csv`): the headline, the explanation of how the rows were read and the other text of the page that describes the tables, as key and value rows.

## Sources and dates

SOURCES.md lists the sources and their terms. NOTICE.txt carries the attribution lines. Every sentence, course title and quoted text has the address of its page in the row. The list rows carry the address of the document each cell comes from. The other cells are our own classification and carry no address of their own.

## How to open the files

Spreadsheet: open any file in `csv/`. The files are UTF-8 with a byte order mark so Excel reads names correctly. Empty text and missing values are both shown as blank cells.

Python, standard library only:

```
import json, csv
rows = json.load(open("json/oy_list.json", encoding="utf-8"))["rows"]
schools = list(csv.DictReader(open("csv/oy_schools.csv", encoding="utf-8-sig")))
```

Check the pack with `python verify.py`. It recounts the rows of every file, compares every CSV cell with the JSON, and recomputes the counts the files state about each other, such as the number of institutions under each finding and the sentences and course titles of every school.

## What is here

- `json/`: the tables of the OY pages as JSON
- `csv/`: one CSV for each table, plus the text file as key and value rows
- `SOURCES.md`: sources, links, terms and dates
- `TESTED.md`: what the files were opened with and what was compared
- `NOTICE.txt`: attribution and terms
- `LICENSE.txt`: terms by file
- `verify.py`: recounts and compares the files
- `START_HERE.html`: this guide as a page
- `CITATION.cff`

## Links

- OY: https://indahl.ai/oy
- Code and scripts: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/oy
- Correction or removal form: https://indahl.ai/correction
- Federal IPEDS directory, College Navigator: https://nces.ed.gov/collegenavigator/

## Notes on the data

The list is a classification for indexing. It is not an assessment of any school or its people. None found means we looked in the places the page names on that date and found nothing. That does not show that none exists. We chose the institutions ourselves, in batches, so the rows are not a random sample.

The sentences and course titles on the school pages were found by script and were not read in full, except for the schools marked in `read_in_full_label`. Many sentences are not about teaching and learning. The page of each school says how many rows our filters removed.

Not in this pack are the pages of OY that are not data tables, which are the pages for children, and the CAMPUS page, which watches the change of the cited documents over time.

## Terms

Each part of this pack keeps the terms of its source, and LICENSE.txt gives them by file. The sentences, titles and quotations belong to the schools and authors of the pages named in each row. The federal ID and class come from the federal IPEDS directory. To correct or remove a row, use https://indahl.ai/correction. It is open to anyone, and we acknowledge every request within three business days.

Heuremen LLC permits anyone to use, copy and change its own parts with attribution to Heuremen LLC and https://indahl.ai/oy. For its own text (the README, SOURCES.md, NOTICE.txt, LICENSE.txt, TESTED.md, START_HERE.html and the labels, counts and notes it wrote in the tables, which LICENSE.txt lists by column) that permission does not include use as AI training data. Its reservation against text and data mining and AI training covers that text only and does not apply to the quoted sentences, titles and quotations.
