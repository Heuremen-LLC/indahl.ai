#!/usr/bin/env python3
"""alert_hooks.py (10 Nov 2026): what a sender adds with one line, without changing its own code paths.

  webhooks_send.py:  post, deliver = alert_hooks.webhooks(post, deliver)
    - every signed delivery (one that carries x-indahl-timestamp) also gets x-indahl-signature-ed25519 and x-indahl-key-id: the Ed25519
      signature of "<timestamp>.<body>" under the published key (sign.py). If signing fails the delivery still goes, without that header,
      and the canary (canary.py) reports it.
    - every accepted delivery records its events on the public alert receipts with the channel kind webhook (alert_receipts.record).
The guard needs no line here: webhooks_send.py and push_send.py read change rows through notify_events.change_rows, which applies it."""
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)


def webhooks(post, deliver):
    import sign, alert_receipts as AR

    def post2(u, body, headers):
        if 'x-indahl-timestamp' in headers:
            try: headers = dict(headers, **sign.webhook_headers(headers['x-indahl-timestamp'], body))
            except Exception: pass
        return post(u, body, headers)

    def deliver2(rec, evs, done=None):
        ok, why = deliver(rec, evs, done)
        if ok and not AR.DRY:
            for ev in evs:
                try: AR.record(ev, 'webhook')
                except Exception: pass
        return ok, why
    return post2, deliver2


def email_sent(events):
    """for alerts_send.py (not wired yet, its owner is changing it): call after send_one() returns ok for a subscriber, with the change events
    in that email (notify_events.event() dicts, or the 'update' events with uid/desk/at). Records the channel kind email on each receipt."""
    import alert_receipts as AR
    for ev in events:
        try: AR.record(ev, 'email')
        except Exception: pass


def guarded(change_rows):
    """for alerts_send.py: keep only rows whose number is published (alert_receipts.guard), each refusal logged with a Bones alert"""
    import alert_receipts as AR
    rows = AR.raw_rows()
    keep = [c for c in change_rows if AR.guard(c['id'], rows=rows)[0]]
    if len(keep) == len(change_rows): AR.guard_clear()
    return keep
