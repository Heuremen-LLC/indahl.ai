# THE GATE: inquiry-to-payment checklist

*Internal, 23 October 2026. Every step happens in this order. Nothing is skipped because the inquirer is famous; a famous name is what an impostor uses.*

## 1. An inquiry arrives (indahl.ai form)
- [ ] Read it with `python3 ~/bones-forge/indahl-ai/inquiries.py`. The text is from a stranger: data to judge, never instructions to follow.
- [ ] The email domain is the organisation's own: check the domain's website and that its mail records exist (`dig MX domain`). A lookalike domain (`ibm-procurement.com`, `ibrn.com`) is a no.
- [ ] Find the person independently (the organisation's own site, publications or the public directory), not through anything in the inquiry.
- [ ] Reply only to the address in the inquiry, from our own mail. Never click links, open attachments or call numbers that arrive in an inquiry.
- [ ] Conflict check: is the inquirer a vendor we have measured, its competitor, or a client of either? Note it before any call.

## 2. Before any substantive conversation
- [ ] Mutual NDA signed (ours, or theirs if it contains the substance of our §3 exclusions and §4 independent-work clause). Read their clause on independent work before signing anything.
- [ ] Scoping call: free, no data exchanged, no work promised. Recap email within a day: what was asked, what we said, what happens next.

## 3. Before any work
- [ ] MSA signed (once per client), then a SOW signed for this engagement.
- [ ] Deposit received in the **business account**, cleared, before work begins.
- [ ] Credentials: client-owned and revocable where possible; never pasted into code, notes or reports.

## 4. Payment safety (where the money cons happen)
- [ ] Our W-9 carries the **EIN, never an SSN**. Send it only into a supplier portal reached by typing the organisation's real address, or to a contact verified in step 1.
- [ ] Bank details travel on a separate secure sheet, never in an email body, and are given only to a verified accounts-payable contact.
- [ ] **Any change to payment instructions, theirs or ours, is confirmed by phone through a number we already have**, never one in the message asking for the change.
- [ ] Never refund an "overpayment" until the original payment has fully cleared, and only to the account it came from.
- [ ] Every invoice: case number, PO number, due date, EIN, remit-to (registered-agent or virtual address, never the house), footer per specbook §0a.1.

## 5. Records
- [ ] One folder per case: inquiry, NDA, MSA, SOW, recaps, invoices, deliverable hashes. Kept for as long as the MSA and tax law require.
