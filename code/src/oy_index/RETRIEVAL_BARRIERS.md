# Where machine retrieval fails: sites that block or hide public pages from automated readers

Internal file for OY and the research notes (28 Oct 2026). Training is a separate question and is not covered here. This file is about plain retrieval: a person, or a person's assistant, asks for a page that is public and gets a wall, a challenge, an empty shell or a login.

## Why it matters
An assistant that cannot open a page does not always say so. It may return a snippet, a cached summary, a different page or nothing, and the person asking has no way to see the difference. For every study we index, the page that holds the evidence is the one that has to open. A site that hides it from automated readers removes that study from any search that runs through an assistant, and nobody sees the gap. We treat that gap as data: an unread page is logged as UNREAD with the code it returned. It is never folded into nothing found.

## What we do about it
- One fetch attempt per page. If it returns a wall we log the address, the title and the date, and move on. We do not rotate agents, solve challenges or route around a block.
- A blocked page is reported as not reached. The person who can open it in a browser pastes the text and we check it the same day.
- Every claim we publish quotes the page it came from, so a page we could not read can only enter by someone reading it.

## OY: reach of the school domains we crawled
134 school domains tested for a plain first fetch. 89 returned a readable page. 45 did not.

Status codes returned by the domains not reached: 403 x 21, 202 x 14, 000 x 7, 307 x 2, 200 x 1.
29 of them returned fewer than 2,000 bytes, which is an error stub or a challenge page, not a site.

| domain | code | bytes returned |
|---|---|---|
| aju.edu | 403 | 103 |
| alc.edu | 403 | 5430 |
| arizonachristian.edu | 403 | 4544 |
| bacone.edu | 000 | 0 |
| bennett.edu | 202 | 169 |
| bethanywv.edu | 202 | 169 |
| blc.edu | 403 | 5430 |
| brescia.edu | 403 | 5455 |
| bua.edu | 202 | 169 |
| colby.edu | 000 | 0 |
| ec.edu | 000 | 0 |
| ew.edu | 202 | 169 |
| georgetowncollege.edu | 403 | 4557 |
| goshen.edu | 403 | 5458 |
| gracechristian.edu | 202 | 169 |
| haverford.edu | 403 | 5461 |
| hiram.edu | 403 | 5453 |
| hlg.edu | 202 | 1107 |
| hputx.edu | 307 | 1387 |
| juniata.edu | 403 | 361 |
| livingstone.edu | 202 | 169 |
| mayaguez.pucpr.edu | 200 | 208 |
| mmm.edu | 000 | 0 |
| mtaloy.edu | 202 | 169 |
| new.trinity.edu | 000 | 0 |
| oakhills.edu | 202 | 169 |
| obu.edu | 403 | 5430 |
| ottawa.edu | 307 | 1359 |
| pcj.edu | 403 | 5481 |
| peace.edu | 202 | 169 |
| philander.edu | 000 | 0 |
| puc.edu | 403 | 5451 |
| randolphcollege.edu | 403 | 103 |
| reinhardt.edu | 403 | 5500 |
| ripon.edu | 403 | 5432 |
| rustcollege.edu | 202 | 169 |
| sa.edu | 000 | 0 |
| simpsonu.edu | 403 | 103 |
| socalsem.edu | 202 | 169 |
| susqu.edu | 403 | 5457 |
| uolivet.edu | 202 | 169 |
| washjeff.edu | 403 | 919 |
| wheaton.edu | 403 | 5455 |
| wilberforce.edu | 202 | 169 |
| williams.edu | 403 | 5456 |

## Vendor and benchmark pages (SAD lanes), 28 Oct
Pages that returned a wall on one attempt. Full list with addresses is in BLOCKED_URLS.md.
- Intel newsroom (403 Access Denied)
- Cisco white papers on cisco.com (403 Access Denied)
- HPE community posts (403, Just a moment challenge)
- Supermicro press releases (403 Access Denied)
- Azure post via a mirror (202 challenge)
- Dell Info Hub posts (bot check)

Open pages on the same subjects (Lambda, Nebius, CoreWeave, Red Hat, AMD, Crusoe) read without trouble. The walls sit on the vendors with the most to say.

## Notes for the site
- The first step of the work is getting the data into one place. For most indexed studies that means a person finding the link, opening it and reading it.
- The count of pages that needed a person is recorded where the outcome is recorded: UNREAD in OY, NOT REACHED in SAD.
- Add a row here each time a wall stops a lane. Pastes from Wayfinder get marked received.
