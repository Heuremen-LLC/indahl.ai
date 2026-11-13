# LINKROT, second question: is there code behind a live link? Plan, written before any repository is queried.

## Claim read
The paper says code is available at a GitHub link. The first LINKROT question asks whether the link resolves (PLAN.md). This one asks, for GitHub links that resolve, whether the repository holds code.

## Data
GitHub GraphQL API through the gh command-line sign-in already on this machine, 50 repositories per query, read-only. For each live GitHub owner/repo link from the LINKROT list: isEmpty, isArchived, isFork, pushedAt, diskUsage, the commit count on the default branch, and the license name. Links that moved to a different repository name are read under the new name. A repository that the API cannot find reads NOT_FOUND and is not counted here (the first question already counts it).

## Rule (fixed now)
EMPTY: isEmpty is true, or the default branch has no commits.
STUB: not empty and the default branch has 3 or fewer commits. Reported apart and not counted as a miss.
ARCHIVED: isArchived is true. Reported apart, descriptive only (an archived repository still holds the code).
STALE: last push over 365 days before the read. Reported apart, descriptive only.
Miss share = EMPTY / (all repositories read), per submission-year cohort and overall, Wilson 95% interval.
Outcome against the claim that code is there: ABOVE if the lower end is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 repositories in a cohort: CANNOT_TELL. Same thresholds as PLAN.md.
## Known-good
Before each pass: torvalds/linux must read not empty with many commits, and a repository known empty by construction must read EMPTY. The empty control is the sandbox repository we create for this under Heuremen-LLC (no commits, left empty on purpose). If either control reads wrong the pass is CANNOT_TELL.
## Cadence
Each repository is read once and again every 30 days. GraphQL cost is one point per 100 aliases, far under the hourly limit.
## Not claimed
That the code matches the paper, runs, or is complete. Only whether anything is there.

## Addendum 1 (29 Oct, after the first pass, before the column was shown)
The pass already holds each repository's detected license (GitHub licenseInfo). A descriptive column is added: repositories that hold code or a stub and have no license detected (licenseInfo empty), as a count and a share of repositories read with a Wilson 95% interval, overall and by submission year of the paper. It is counted apart. It is not a miss, does not enter the empty-repository outcome, and carries no outcome of its own. A repository whose license GitHub reports as NOASSERTION (custom or mixed) is counted in neither this column nor a named license. It was defined after the first pass, and the page says so.
