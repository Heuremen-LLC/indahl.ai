# CHANGE parser fixtures

The parser gate in change_tick.py reads four saved pages: the deprecation pages of Anthropic, OpenAI, Google and Cloudflare as fetched on 29 Oct 2026. Those pages belong to their publishers, so the saved copies are kept in our own record and are not published here. EXPECTED.json is ours. It holds the row count and the first three row names the parser read from each saved page when the plan was written.

To run the gate yourself, fetch each page from the address in change_tick.py and save it as fixtures/<Name>.html. The live pages change over time, so the counts in EXPECTED.json hold for the 29 Oct copies only.
