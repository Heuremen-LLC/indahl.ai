# NJ public statements: rank claims and instructional time

Read 2026-11-10 by the RANK desk (Heuremen LLC). Fetched with WebFetch and curl (UA "HeuremenRANK/0.1 (+https://indahl.ai/oy)"). No browser tools, no bot-check workarounds.

## Files
- `claims.json`: rank statements by schools, districts and colleges about U.S. News & World Report ranks. Exact quote, publisher, URL, date on page, list and edition as named, scope (state / national / neither).
- `schedules.json`: bell schedules and calendars for the K-12 schools. Quotes are verbatim excerpts; "..." joins excerpts from the same document. Derived values (sums of printed monthly day counts, OCR) are labelled in `fields` or `note`.
- `pages/<slug>/`: saved copy of every quoted page or PDF. `quote_check` in each row = every quoted segment found in the saved copy (all rows "verbatim" on 2026-11-10, by tools/verify.py).
- `parts/`: per-helper raw outputs and gap notes (g1 to g7). `tools/merge.py`, `tools/verify.py` rebuild and recheck.

## Publishers cited
- Monmouth County Vocational School District: mcvsd.org, bths.mcvsd.org (Google Sheet bell schedule linked from the site)
- Middlesex County Magnet Schools: eams.mcmsnj.net, district calendar PDFs on resources.finalsite.net
- Union County Vocational-Technical Schools: ucvts district calendar PDFs (ucvtsorg.finalsite.com), the 2025-26 one image-only and read by OCR (pages/ucvts_cal_a681/ocr.txt)
- Jersey City Public Schools: ihs.jcboe.org, mhs.jcboe.org, ps16.jcboe.org, ii.jcboe.org
- Paterson Public Schools: paterson.k12.nj.us press release, ps28.paterson.k12.nj.us, 2025-26 calendar PDF
- Union City Board of Education: ucboe.us news, 2025-26 calendar PDF
- School District of the Chathams: chatham-nj.org Milton Avenue live feed
- Glen Rock Public Schools: glenrocknj.org
- Millburn Township Public Schools: millburn.org (district line only)
- Livingston Public Schools: livingston.org/about-our-schools
- HoLa: press release text as hosted on insidernj.com (school site unreachable)
- Colleges: stevens.edu, news.njit.edu, njit.edu, rutgers.edu, newark.rutgers.edu, paw.princeton.edu (Princeton Alumni Weekly), montclair.edu, monmouth.edu, drew.edu, shu.edu, sites.rowan.edu, today.rowan.edu

## Not read (rows in ~/bones-forge/research/MANUAL_READS.md)
TCNJ 2027 and 2026 releases (403); Princeton Charter School (HTTP 500); Rumson schools site (no connection); HoLa site (no connection); Markham Place 2025-26 guidebook PDF; High Technology HS schedules page (image only, linked doc login).

## Limits
The session's shared web-search budget ran out early, so board of education minutes were not searched for any school, and several schools were checked only through their homepage and news pages.
