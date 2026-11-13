#!/usr/bin/env python3
"""fetch_statements.py: caches the OPEC press statement pages and their required-production table images (public, no login) under data/raw/stmt. Never re-fetches a cached file.
The tables are images, read by eye into make_targets.py. To add a month, add the statement slug and image id to STM."""
import os, subprocess
H = os.path.dirname(os.path.abspath(__file__)); D = H + '/data/raw/stmt'; os.makedirs(D, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh) Safari/605'
STM = {'28-05-dec-2024': '1738743572', '244557-03-april-2025': '1743675427', '563-03-may-2025': '1746270556', '569-05-july-2025': '1751707386', '1518572-03-august-2025': '1754220274',
       '1574579-02-november-2025': '1762099998', '583-30-november-2025': '1764516384', '587-4-january-2026': '1767526985', '589-1-february-2026': '1769954571', '593-1-march-2026': '1772363311',
       '597-5-april-2026': '1775398028', '1835609-5-july-2026': '1783246215', '2033620-1-november-2026': '1793534438', '1783605-7-june-2026': None}
for slug, img in STM.items():
    for url, out in [('https://www.opec.org/pr-detail/%s.html' % slug, '%s/%s.html' % (D, slug))] + ([('https://www.opec.org/assets/imagedb/pic/%s.png' % img, '%s/%s.png' % (D, img))] if img else []):
        if not os.path.exists(out):
            subprocess.run(['curl', '-sSL', '-m', '60', '-A', UA, '-o', out, url]); print('fetched', url)
