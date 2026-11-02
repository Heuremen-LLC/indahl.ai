# Sources

Heuremen LLC · https://indahl.ai/oy

Each entry gives the source as the OY pages state it, with the dates found in the pages. The descriptions follow https://indahl.ai/oy and its school pages.

## The list and the findings (json/oy_list.json, json/oy_findings.json, json/oy_chatbot_citations.json)

- Documents published by the institutions themselves, and studies about them, each linked from its row. The page states: for each institution we looked for what it has published about AI in teaching and learning, read its own public pages and checked scholarly indexes for studies by its faculty. For most rows a general web search was not run.
- The list is as of {AS_OF}. The page states: Read 25 October 2026.
- Where the page marks a link as a journal article, a preprint, a registry entry, a repository copy, a faculty blog post or conference slides, the column `kind` or `institution_url_kind` says so.
- The chatbot citations quote a passage from each named document, with the address of the document.
- The documents belong to the institutions and authors that published them. The terms of each document are its owner's.
- The words in the columns `public_policy_or_guidance`, `measures_own_policy`, `released_own_data`, `pilot_results` and in the findings, notes and `what_we_found` text are ours.

## Private baccalaureate colleges (json/oy_schools.json)

- The school's own public pages, read by script on {READ_ON_DATE} (UTC, when each read finished). Sentences that name AI and also contain a digit and a word such as study, survey, pilot, section or percent. Course titles in the public catalog that name AI, machine learning, data science, technology and society, digital humanities, philosophy of mind or related topics. Each item carries the address of the page it was found on.
- The schools are the private nonprofit baccalaureate colleges of the federal directory. The directory puts them in two Carnegie 2021 classes, Arts and Sciences focus and Diverse fields.
- Federal ID and class: the federal IPEDS directory of the National Center for Education Statistics, U.S. Department of Education, https://nces.ed.gov/collegenavigator/ . The page states: Class from the 2021 Carnegie classification in the federal IPEDS directory. The pages state no separate terms for the class.
- Schools whose pages we also read in full are marked in `read_in_full_label`, and the note beside the label is ours. They were read on 28 October 2026.
- Scripts: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/oy

## Not in this pack

The pages for children, and the CAMPUS page that watches the cited documents for change. The CAMPUS page is a live feed and not a table of OY rows.
