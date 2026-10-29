# ARXIVDRIFT: the version we read against the version that stands now. Plan, written before any version is compared.

## What this is
QIA and IRIS index published studies and record the arXiv version read (it is in each link, for example abs/2509.20558v2). Authors revise. This table shows, for every indexed arXiv study, whether a later version exists and whether the revision changed what we read: the numbers in the abstract, the title, or the paper's standing.
It is descriptive. No claim is tested, so no ABOVE or BELOW is assigned. Shares carry Wilson 95% intervals.

## Population
Every study in the published lists https://indahl.ai/qia/list.json and https://indahl.ai/iris/list.json whose link is arxiv.org/abs/ID followed by a version. Unit: one study. Read version: the version in the link.

## Read (fixed now)
arXiv API (public), user agent naming this site, one request per 3 seconds. Latest metadata by id_list in batches of 50. For a study whose latest version is above the read version, the read version's own title and abstract by id_list with the explicit version, in batches of 10.
Classes:
- UNCHANGED: latest version equals the read version.
- REVISED_SAME: later version exists; title, abstract numbers and abstract text equal.
- REVISED_TEXT: later version exists; numbers equal; title or abstract wording differs.
- REVISED_NUMBERS: later version exists; the multiset of numeric tokens in the abstract differs (numbers added or removed are listed).
- WITHDRAWN: the latest abstract or comment states the paper is withdrawn.
- NOTHING_RETURNED: the API returned no entry for the id.
Numeric tokens: integers and decimals with an optional percent sign, found by the pattern in the code, ignoring the tokens inside the arXiv identifier. Text comparison ignores case, spacing and punctuation.
Reported: counts per class overall and by month indexed; the share of studies with any change (REVISED_NUMBERS, REVISED_TEXT or WITHDRAWN) with its interval; the list of REVISED_NUMBERS and WITHDRAWN studies with the numbers each version states.
Re-read every 7 days. A version number that rises later is a new reading, and the history of classes per study is kept.

## Known-good
Before each pass: 1706.03762 read at v1 must come back REVISED_NUMBERS (the abstract's headline BLEU figure changed between versions), and 1512.03385 read at v1 must come back UNCHANGED (a single-version paper). If either reads wrong the pass is not published and the page says the instrument failed its gate. Both assumptions are checked once by hand before the first full pass and any correction is logged as a dated addendum.

## Not claimed
That a revision is better or worse. That an unchanged abstract means an unchanged paper (only abstract, title and standing are compared). Why an author revised.
## What changes on QIA and IRIS
Nothing is edited automatically. A study that reads REVISED_NUMBERS gets a recount by hand before any of our rows change, and the recount is a dated note.

## Addendum 1 (29 Oct, after the first round, before anything was published)
The first round flagged 2604.24289 as WITHDRAWN because its arXiv comment says "Section 6 ... is withdrawn". The comment withdraws a section, and the paper stands; also that comment was already part of the version we read (v2). The detector matched the word anywhere in the comment, which is looser than the plan's class (the paper is withdrawn). The detector now requires the abstract to begin with, or the comment to begin with, a statement that the paper itself is withdrawn (this paper or article or submission, withdrawn). All studies are read again with the corrected detector. The hand check of 2511.10921 (v1: 27 benchmark circuits, 24.94 to 52.00 per cent fidelity improvement; v2: 24 circuits, 24.94 to 80.48 per cent) confirms REVISED_NUMBERS there.
