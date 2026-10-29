# HOSTS: one open-weight model, many hosts. What the hosts state, and what we keep. Plan, committed before the first read.

## The question
An open-weight model can be served by a dozen companies. OpenRouter, an aggregator, publishes for each model the list of hosts that serve it, with each host's stated quantization (the numeric precision of the weights), prices, context limits, and uptime figures for the last 5 minutes, 30 minutes and 1 day. We read all of it every 12 minutes, keep every read, and show the pattern: where hosts differ for the same model, when they go down, and whether the one-day uptime the aggregator states matches what its own 5-minute figures add up to. We run no inference and spend nothing. We never rank hosts.

## Data
The public OpenRouter API, no key: the models list (openrouter.ai/api/v1/models) and, for each model with a Hugging Face id, openrouter.ai/api/v1/models/ID/endpoints. The latency and throughput fields in the response are empty without a key and are kept as returned. One request every 0.4 seconds, the user agent heuremen-hosts/0.1 (+https://indahl.ai/hosts).

## Read (fixed now)
Every poll (every 2 ticks of the tick bus, about 12 minutes): the models list, then the endpoint list of every model that has a Hugging Face id. Stored per endpoint and poll, as returned: model id, host name, tag, quantization, status, uptime for 5 minutes, 30 minutes and 1 day, maximum completion tokens, context length, prompt and completion prices. A model or host that disappears is kept as absent in that poll. A poll that fails is stored as NOTHING_RETURNED, never as zero hosts. Stored polls are kept 14 days.

## Display (no outcome)
Counts of models, hosts and endpoints now; endpoints with a status other than 0 or a 5-minute uptime below 100 now, with their 30-minute and 1-day figures; and per quantization label the share of endpoints with a 5-minute uptime of 100 in the last 24 hours of our polls. Everything is a list or a count. No ranking, no best or worst.

## Test (fixed now): the stated one-day uptime against our own record
For every endpoint with at least 100 polls in a 24-hour span ending at a poll, compare the one-day uptime stated at that poll with the mean of the 5-minute uptime figures from our polls in the 24 hours up to it. AGREE when they differ by 2 percentage points or less, DISAGREE otherwise, NOT_COMPARABLE when fewer than 100 polls, or when an endpoint was absent in more than 10 percent of the polls. The unit is the endpoint, taking the latest qualifying poll, and the headline is the share DISAGREE with a Wilson 95 percent interval. ABOVE if the lower end is above 0.05. CONSISTENT if the upper end is below 0.15. Otherwise CANNOT_TELL. Until 24 hours of polls exist the outcome is NOTHING_RETURNED.

## Known-good, run before every poll
The endpoint parser on a planted response (uptime values, null latency, a missing field) returns each field and returns None for a missing one without failing. The agreement function returns AGREE at a difference of exactly 2.0 and DISAGREE at 2.01, NOT_COMPARABLE at 99 polls. A live check: the models list is non-empty and the first open-weight model returns at least one endpoint.

## Hand check
Ten DISAGREE endpoints, chosen by seed 7, are opened by hand against the stored polls: the stated figure, the 288 or so 5-minute figures in the window and their mean are recomputed with a separate routine.

## Not claimed
That a host's figures are wrong. The aggregator may define uptime from requests and not from time, so a difference between its 1-day figure and the mean of its 5-minute figures need not be an error, and the page says so. That any host serves the model it names. Anything about the quality or speed of a host.
