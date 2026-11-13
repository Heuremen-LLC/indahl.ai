# Helper brief: NJ public statements (RANK desk, indahl.ai, Heuremen LLC)

Collect PUBLIC statements only. Do not judge or characterise. Quote exactly, link, date. No adjectives, no causes, no personal data beyond published officials' titles. Never state anything from memory: every item must come from a page you fetched this session.

Tools: WebSearch, WebFetch, and curl with `-A "HeuremenRANK/0.1 (+https://indahl.ai/oy)"`. Do NOT use Chrome/browser/playwright tools. Do not spoof user agents or get around bot checks.
If a page refuses (403, challenge, login), append ONE row to /Users/heuremen/bones-forge/research/MANUAL_READS.md (use `>>` append only):
| RANK | <school and document> | <exact URL> | challenge / login / refused | <what to look for> | ~/bones-forge/rank_index/raw/manual/<file> |
and move on.

## A. RANK CLAIMS
Any public statement by the school, its district or college (official homepage, official news/press release, board of education minutes or agenda, official social posts linked from the official site) about its US News & World Report rank. Exact quote under 30 words. Record publisher, URL, date on page, list and edition named (if any), and scope: state / national / neither. Prefer 2026-2027 HS edition and 2027 K-8/college editions, but record older ones too, labelled with their date. Also news-site search hits are useful only to FIND an official page; cite only the official publisher's page. Useful searches: `site:<district domain> "U.S. News"`, `"<school>" "U.S. News" ranked`, district news pages, BOE minutes PDFs.

## B. INSTRUCTIONAL TIME (K-12 only)
Published bell schedule and school calendar for 2023-24, 2024-25, 2025-26 where public: regular day start/end, stated instructional minutes, number of school days, early-dismissal patterns. Quote exactly with URL and date. Only what the documents state. Calendars are often PDFs: download with curl and extract text with `pdftotext -layout` (or python pypdf with `python3 -I`). Count of days: only if the document states it (e.g. "180 days" or a monthly day count printed on the calendar); do not count yourself unless you label it `"derived": "counted from calendar by helper"`.

## Saving pages
Save a copy of every page you quote under /Users/heuremen/bones-forge/rank_index/public/nj_claims/pages/<slug>/ (one folder per page, slug like `mcvsd_hths_news_2025` ), e.g. `curl -sL -A "HeuremenRANK/0.1 (+https://indahl.ai/oy)" -o pages/<slug>/page.html <url>` (or .pdf). If only WebFetch worked, save the fetched text you quote to pages/<slug>/webfetch.txt with the URL on line 1.

## Output
Write two JSON arrays to /Users/heuremen/bones-forge/rank_index/public/nj_claims/parts/<GROUP>_claims.json and <GROUP>_schedules.json.
Claims item:
{"school": "...", "kind": "rank_claim", "publisher": "...", "quote": "exact words", "url": "...", "date_on_page": "YYYY-MM-DD or as printed or null", "date_read": "2026-11-10", "list_named": "e.g. Best High Schools / Best Elementary Schools / National Universities / null", "edition_named": "e.g. 2026-2027 / 2025 / null", "scope": "state|national|neither", "saved_copy": "pages/<slug>/...", "note": "optional, factual only"}
Schedule item:
{"school": "...", "kind": "bell_schedule|calendar|instructional_minutes|early_dismissal", "school_year": "2024-25", "publisher": "...", "quote": "exact words", "url": "...", "date_on_page": "...", "date_read": "2026-11-10", "fields": {"start": "7:45", "end": "2:30", "instructional_minutes": null, "school_days": null, "early_dismissal": "..."}, "saved_copy": "pages/<slug>/..."}
Also write <GROUP>_gaps.txt listing per school what you looked for and did not find, and which URLs went to MANUAL_READS.

Budget: about 30 minutes. Breadth over depth: one good item per school per kind beats five for one school. Final message: short list of what you wrote and gaps.
