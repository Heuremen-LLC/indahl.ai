# UPTIME: status pages against independent probes (28 Oct 2026, his word)
Written and committed before any probe round was read against any status page.

## What is stated
Each vendor's own status page publishes an overall indicator (none, minor, major, critical) and incident records through the standard Statuspage JSON (`/api/v2/summary.json`, `/api/v2/incidents.json`). "None" is the vendor stating that all systems are operational.

## What is delivered
One plain HTTPS GET per vendor per round to a public page or endpoint the vendor serves (list in vendors.json, saved with its date), from each of our probe seats: the Mac and the Pi on the house network, and a GitHub runner network. A request is a failure if it times out at 10 seconds, cannot connect, or returns status 500 or higher. A 4xx counts as reachable. Rounds ride Nova's ticks, never a timer, one request per vendor per seat per round, with our own user agent that names this site. A vendor whose endpoint returns a bot wall (403 on every round) is dropped and listed.

## Events
A disagreement round is one where the vendor's indicator reads none and at least two seats fail the vendor's endpoint in the same round. A confirmation round is one where the indicator reads minor, major or critical and at least two seats fail. A quiet round is none with all seats up. Rounds where only one seat fails are counted as seat blips and shown.

## Floor (measured, not assumed)
Control targets with no status page that are as reliable as anything reachable: example.com and 1.1.1.1 over HTTPS. The control miss rate, two or more seats failing, is the instrument floor and is published beside every vendor.

## Outcomes per vendor
BELOW: disagreement rounds exceed the floor by more than two square roots of the expected count (the vendor was less reachable than its page stated). CONSISTENT: they do not. CANNOT_TELL: fewer than 300 rounds held. ABOVE is not assigned, because a reachable service is the stated case. Incidents the vendor records are shown with their start and end beside our rounds in the same window.

## Not claimed
One endpoint is not a whole service. A disagreement is a disagreement between the page and the endpoint we asked, on those seats, in that round. No ranking. Each vendor gets a vendor-response path.
