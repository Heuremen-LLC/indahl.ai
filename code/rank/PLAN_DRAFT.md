# RANK: US News rankings against the public record. DRAFT, NOT SEALED. No comparison has been made.

Status 10 Nov 2026: blocked before any US News figure was read. Every route to usnews.com from this machine was refused:
- direct fetch (WebFetch): timed out (60 s), list page and methodology article
- curl with a browser user agent: refused by the permission system as bot-check circumvention (not retried)
- Playwright browser: refused, same reason
- Internet Archive copies of the list pages: refused by the permission system as walled content read from a copy
- Chrome extension (owner's own browser): not connected
Nothing from US News is held in this folder.

Needed to proceed (owner's call): connect the Claude Chrome extension so lists are read in the owner's own session, or allow a US News source in the permission settings.

Public-record side, reachability checked 10 Nov 2026 (HeuremenRANK user agent):
- NCES CCD via Urban Institute Education Data API: 200
- NCES CCD school search: 200
- IPEDS use-the-data: 200
- ABA required disclosures: 200
- College Scorecard API: 403 without a key (api.data.gov key or DEMO_KEY needed)
- National Blue Ribbon Schools award-winner page: 403 to our user agent
- NJ School Performance Reports (rc.doe.state.nj.us): no answer in 25 s

Plan outline to seal once the US News side can be read (indicators and weights are quoted from US News's own methodology pages at seal time, not from memory):
- Lists: Best High Schools, Best Middle Schools, Best Elementary Schools, Best Colleges (National Universities, National Liberal Arts Colleges, Regional if easy), Best Graduate Schools (Business, Law, Medicine, Engineering, Education). Current edition, top 10 each, ties kept.
- Per figure: MATCH (same year, equal after rounding to the precision US News prints), MISMATCH, CANNOT_TELL (year differs, figure not public, definition differs). Year of each side printed.
- Rank recompute only where every indicator and weight is stated and public. Otherwise CANNOT_TELL, method not fully stated or inputs not public.
- Documented data-correction cases: primary sources only (US News's own notices, the school's own statement, court or regulator filings).
