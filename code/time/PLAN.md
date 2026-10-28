# TIME: stated against delivered for public clocks (28 Oct 2026, his word)
Written and committed before any server is queried.

## Reference and seats
The reference is the Pi, a stratum 1 clock disciplined by GPS PPS (chrony; its own offset and RMS are logged with every run). Second seat: the Mac, to show what a plain machine sees. Read-only: ordinary NTP client queries, version 4, at most one query per server every 2 seconds, nothing transmitted on any radio, GPS receive only.

## Measurement
Per server, rounds of 8 queries. Per query: offset and round-trip delay from the four NTP timestamps, plus what the server states in its own reply: stratum, reference id, root delay, root dispersion, leap indicator. The kept sample per round is the minimum-delay query. Its uncertainty is half its round-trip delay (the unknown asymmetry of the path), added in quadrature with the reference's own logged uncertainty. A server that returns nothing is NOTHING_RETURNED and is counted, never dropped.

## Statements and outcome rules (fixed here)
T1 The server's own stated error bound. A server's reply states root delay and root dispersion, so it claims the true time lies within root dispersion plus half the root delay of its own reference. Rule: with offset o, half-delay h, claimed bound E: CONSISTENT if |o| + h <= E, ABOVE if |o| - h > E (the server is further from true time than it states), CANNOT_TELL otherwise.
T2 A provider's published accuracy figure, where the provider's own page gives a number. Same rule with E taken from the page, the page text quoted verbatim and dated. Where the path uncertainty h exceeds E the outcome is CANNOT_TELL and says so; no claim smaller than the path can resolve is called met.
T3 Stratum and reference class stated by the provider against stratum and reference id in the reply: CONSISTENT if equal, ABOVE or BELOW by the stratum difference otherwise.
T4 Leap handling stated by the provider (smear or step) is recorded as stated. No leap second falls in the window, so the outcome is CANNOT_TELL until one does.
Four outcomes everywhere. No ranking of providers. Rounds repeated on the Pi's tick, never on a timer.

## What is published
Per server: median and interquartile of the kept offsets, median delay, stated and measured fields, the outcome per statement, the raw sample file and the collector script. The reference's own quality line is shown next to every table.
