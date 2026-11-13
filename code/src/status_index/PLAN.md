# UPTIME: status pages against independent probes (28 Oct 2026, his word)
Written and committed before any probe round was read against any status page.

## What is stated
Each vendor's own status page publishes an overall indicator (none, minor, major, critical) and incident records through the standard Statuspage JSON (`/api/v2/summary.json`, `/api/v2/incidents.json`). "None" is the vendor stating that all systems are operational.

## What is delivered
One plain HTTPS GET per vendor per round to a public page or endpoint the vendor serves (list in vendors.json, saved with its date), from each of our probe seats: the Mac and the Pi on the house network, and a GitHub runner network. A request is a failure if it times out at 10 seconds, cannot connect, or returns status 500 or higher. A 4xx counts as reachable. Rounds ride HST ticks, never a timer, one request per vendor per seat per round, with our own user agent that names this site. A vendor whose endpoint returns a bot wall (403 on every round) is dropped and listed.

## Events
A disagreement round is one where the vendor's indicator reads none and at least two seats fail the vendor's endpoint in the same round. A confirmation round is one where the indicator reads minor, major or critical and at least two seats fail. A quiet round is none with all seats up. Rounds where only one seat fails are counted as seat blips and shown.

## Floor (measured, not assumed)
Control targets with no status page that are as reliable as anything reachable: example.com and 1.1.1.1 over HTTPS. The control miss rate, two or more seats failing, is the instrument floor and is published beside every vendor.

## Outcomes per vendor
BELOW: disagreement rounds exceed the floor by more than two square roots of the expected count (the vendor was less reachable than its page stated). CONSISTENT: they do not. CANNOT_TELL: fewer than 300 rounds held. ABOVE is not assigned, because a reachable service is the stated case. Incidents the vendor records are shown with their start and end beside our rounds in the same window.

## Not claimed
One endpoint is not a whole service. A disagreement is a disagreement between the page and the endpoint we asked, on those seats, in that round. No ranking. Each vendor gets a vendor-response path.

## Addendum 1 (29 Oct, from the internal audit, before any vendor read BELOW)
1. Seats. A disagreement needed two of three seats to fail, but the Mac and the Pi sit on the same house network, so one home-network fault counted as two seats and as a vendor disagreement. The Mac and the Pi are now one seat. A disagreement needs the home seat and the GitHub runner seat to fail in the same round with the page saying none.
2. Floor. The control floor is 0 misses in 170 rounds. That is not a zero rate. The floor used for the expected count is the upper end of the Wilson 95 percent interval of the control rate (0.022 at 170 rounds), so the first disagreement round cannot make a vendor BELOW on its own.
3. Episodes. Consecutive disagreement rounds are one episode, and BELOW now needs at least two episodes as well as the count over the expected count plus two square roots.
4. Stated and not fixed. The control floor comes from example.com and 1.1.1.1, the most reliable targets, while vendors are probed at their own endpoints, so the floor may be lower than the floor of a vendor-type endpoint. A timeout at our seat or a failed connect is scored as a vendor failure with no terminating reason recorded. CONSISTENT at 300 rounds does not say how small an outage rate 300 rounds could have seen.
