# OY: school pages

The data and scripts behind https://indahl.ai/oy/school/ pages.

- `smallpass/small_pass*.py` read each school's own public site: the sitemap and common paths, at most 25 pages about AI per school, and keep sentences that name AI and also contain a digit and a study word. `course_pass*.py` read public catalogs for course titles.
- `smallpass/ROSTER.csv` and `ROSTER22.csv` are the schools, from the federal IPEDS directory (2024), Carnegie 2021 classes 21 and 22.
- `build_schools.py` turns the reads into `schools.json`, one record per school. It filters out rows that are not what the page says they are (page code, menus, other meanings of an AI word, course descriptions, repeats, older catalogs) and counts every removal by reason, per school.
- `smallpass/site_links.py` checks which form of each school's address answers.

The reads ran on 28 October 2026 (UTC). They are script reads, not assessments of any school. Run with `python3 -I`.

Heuremen LLC
