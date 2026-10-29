# PKGLICENSE: the license a package states against the license of its repository. Plan, written before any package is compared.

## Claim read
A PyPI package states its license in its metadata (license expression, a License classifier, or the license field). The repository it points to carries a license file. Stated: the package is under license X. Record: the repository's license file says Y.

## Population
The 1,000 projects with the most downloads in the last 30 days, from the public list https://hugovk.github.io/top-pypi-packages/ (the list date is stored with the read). Unit: one project.

## Read (fixed now)
PyPI JSON API (https://pypi.org/pypi/PROJECT/json), one request per 0.5 seconds, user agent naming this site. The repository is the first github.com owner/repo found, in order, in the project URLs keyed Source, Repository, Code, Homepage and then the home page field.
The repository's license is the one GitHub detects from its license file (GraphQL licenseInfo, 100 repositories per query, through the gh sign-in), by SPDX id.
Stated license, in order: the license expression; else the first License classifier; else the license field when it is 100 characters or fewer. Both sides are mapped to a family: MIT, Apache-2.0, BSD (BSD-2-Clause, BSD-3-Clause, 0BSD, BSD), ISC, GPL-2.0, GPL-3.0, GPL (version not given), LGPL, AGPL, MPL-2.0, PSF, Unlicense, CC0, and OTHER for anything else, a custom license, or NOASSERTION.
Classes: AGREE (same family; GPL with no version agrees with GPL-2.0 or GPL-3.0), DISAGREE (both sides in a named family and the families differ), NOT_COMPARABLE (no stated license, no GitHub repository, repository not found, or either side OTHER).
Reported: counts by class; the share DISAGREE among AGREE plus DISAGREE with its Wilson 95% interval; the list of DISAGREE projects with both strings as given.
Outcome against the claim that the stated license is the repository's license (zero disagreement): ABOVE if the lower end of the share is above 0.10. CONSISTENT if the upper end is below 0.05. Otherwise CANNOT_TELL. Fewer than 30 comparable projects: CANNOT_TELL. Thresholds fixed here.
Re-read every 30 days.

## Hand check (fixed now)
Every DISAGREE row is opened by hand once (the metadata and the repository's license file) before it is shown. A row where the mapping, not the project, was wrong is corrected in the mapping by a dated addendum and the whole read is run again. Nothing is shown until that is done.

## Known-good
The mapping is run on planted pairs before every read (MIT with MIT, Apache Software License classifier with Apache-2.0, BSD-3-Clause with BSD-2-Clause as the same family, GPLv3 classifier with GPL-3.0, MIT with Apache-2.0 as DISAGREE, a custom license as NOT_COMPARABLE). Live: requests must read AGREE (Apache-2.0 both sides) and numpy must read AGREE (BSD family both sides). Any wrong answer stops the pass.

## Not claimed
Which side is right. That a repository's license file governs files in a package built from a different source. That a vendored component's license is the package's license.

## Addendum 1 (29 Oct, after the first gate run, before any project was compared)
The first live gate failed on numpy. The plan named numpy as a control that must read AGREE, but its metadata lists several licenses (BSD-3-Clause, 0BSD, MIT, Zlib, CC0-1.0) and GitHub reports NOASSERTION for its repository, so under the rules numpy correctly reads NOT_COMPARABLE. The control was wrongly chosen, the rules are unchanged. The live controls are now requests (Apache-2.0 on both sides) and flask (BSD-3-Clause on both sides), both read by hand on 29 Oct 2026 before this addendum was committed.

## Addendum 2 (29 Oct, after the first read and the hand check, before anything was shown)
The first read: 1,000 projects, 692 AGREE, 7 DISAGREE, 301 NOT_COMPARABLE (186 repository license not detected, 100 no GitHub repository in the metadata, 15 no stated license). Disagreement share 7 of 699 compared, 1.0 per cent, Wilson 0.5 to 2.1 per cent, CONSISTENT. The hand check opened both sides of every DISAGREE row. Result, with no change to the mapping or any rule:
- pathspec: the repository holds two license files (MIT and MPL-2.0) and GitHub reports MIT; the package states MPL-2.0.
- requests-oauthlib and redshift-connector: the PyPI license field matches the repository (ISC; Apache License 2.0) and the License classifier contradicts it (BSD License). The plan's order uses the classifier when there is no expression, so these read DISAGREE; the metadata disagrees with itself.
- opencv-python and opencv-python-headless: the repository license is MIT (the packaging scripts); the wheels bundle OpenCV, which is Apache-2.0, and the package states Apache.
- pydeck and pandas-gbq: the package lives in a subfolder of a larger repository (deck.gl; google-cloud-python), whose root license differs from the package's.
Each reason is shown beside its row.
