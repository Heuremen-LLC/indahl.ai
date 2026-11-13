# Right of reply, live. Plan, written before the first reply is posted.

## What exists
The response door (/respond) takes one https link to a PDF per unit code (for example time-all, qia-ibm), stores the unit, link, host and time, and says nothing is posted until we have read the file and recounted anything it disputes.

## What this adds (fixed now)
1. replies.json: the public record of posted replies. One entry per reply: unit, link, host, received time, posted time, and our recount line (what the reply disputes, what we recounted, the outcome before and after, or "recounted, nothing changed", or "cannot recount from the file").
2. A block on each corner page that lists the posted replies whose unit starts with that corner's code. The block does not appear when there are none.
3. A review tool for us (reply_review.py): lists pending replies, fetches the PDF into a scratch folder for reading, and posts an entry only when a recount line is supplied. A reply is never posted without that line.
## Rules
Posted as received, dated, with the host it came from, and no edits to its text. The reply link is a link, we do not host the file. Nothing in a reply changes a row by itself. A row changes only through a dated addendum after a recount, and the entry points to that addendum. A reply that is not a PDF, is abusive, or names a private person is not posted and the sender is not told why beyond the received message. Posting is a decision by Heuremen LLC, recorded in replies.json with the date.
## Not claimed
That a reply is correct. That a missing reply means agreement.
