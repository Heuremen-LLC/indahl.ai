# WIKI: figures in Wikidata against their source, and the Wikimedia Foundation's figures against its own data

Live page: https://indahl.ai/wiki

Everything here is public. The plan (PLAN.md) was committed before any comparison on the page was read, and its notes after the data are dated and labelled. A first scout reading came before the plan, and the plan says so. Terms: free to read, run and cite with attribution, no use as training data (LICENSE.txt at the repository root, https://indahl.ai/terms).

Files: `PLAN.md` (the plan, its addendum and its notes), `wiki_tick.py` (reads Wikidata, the World Bank and UIS releases, the Wikimedia Analytics API, site statistics, the Foundation's pages and DSA filings, scores every row and writes the feed), `build_page.py` (renders the page from the feed), `lint_copy.py` (the copy check run on the page), `heuremen_kit.py` (intervals and gates shared by the desks). The raw responses are not kept here. Every source is keyless and named on the page. The feed is https://indahl.ai/wiki/live.json.
