# SOCIAL: platform reports against the filings

Live page: https://indahl.ai/social

Everything here is public. Terms: free to read, run and cite with attribution, no use as training data (LICENSE.txt at the repository root, https://indahl.ai/terms).

Files: `build_social.py` (places each cleared section file on the page as it is and reads every number outside the sections from that section's summary), `check_social.py` (checks every number on the page against the section summaries and data files, the headline rule and the copy rules). Each section has its own folder with its plan and tick: `code/social-dsa`, `code/adspend`, `code/social-tiktok` and `code/social-bluesky`. The page summary is https://indahl.ai/social/summary.json.
