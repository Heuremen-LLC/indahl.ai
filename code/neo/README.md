# NEO: JPL close-approach distances stated from an earlier orbit solution, against the latest solution

Live page: https://indahl.ai/neo

Everything here is public. The plan (PLAN.md) was committed before any stated distance was set beside a later one. Readings added after the data are labelled in the feed (after_data_note) and decide nothing. Terms: free to read, run and cite with attribution, no use as training data (LICENSE.txt at the repository root, https://indahl.ai/terms).

Files: `PLAN.md` (the plan), `neo_tick.py` (reads the JPL Close-Approach Data API, the SBDB API, the Sentry lists and the Internet Archive copies of the Close-Approach service, scores every row and writes the feed), `neo_headline.py` (the headline line, used by the page and the live headline), `build_page.py` (renders the page from the feed), `lint_copy.py` (the copy check run on the page), `heuremen_kit.py` (intervals and gates shared by the desks). The raw responses are not kept here. Every source is keyless and named on the page. The feed is https://indahl.ai/neo/live.json.
