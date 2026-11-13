import os, re
B = os.path.expanduser('~/bones-forge')
def sub(path, old, new, count=1):
    s = open(path).read(); assert s.count(old) == count, (path, old[:60], s.count(old)); open(path, 'w').write(s.replace(old, new))
bs = B + '/indahl-ai/build_site.py'
sub(bs, "'/census/coverage': '/census'}", "'/census/coverage': '/census', '/census/fidelity': '/census'}")
sub(bs, "'census','census/revisions'}", "'census','census/revisions','census/fidelity'}")
sub(bs, "    if path == '/census/coverage' and globals().get('_COVSLOT')", "    if path == '/census/fidelity' and globals().get('_FIDSLOT'): return _FIDSLOT   # 11 Nov 2026: CENSUS FIDELITY is a one-time desk, its headline is built with the page (fidelity_index/build_page.py)\n    if path == '/census/coverage' and globals().get('_COVSLOT')")
block = '''# 11 Nov 2026: CENSUS FIDELITY, the third desk under CENSUS, at /census/fidelity. State divorce and marriage counts reported to the CDC (NCHS) set beside the ACS
# estimates with the 90 percent margin Census states, women's estimate scored, men's beside it. One-time desk: no tick rider for the readings (a snapshot rider keeps dated NCHS copies),
# no feed, no data pack. Plan: fidelity_index/PLAN.md, sealed (1b571f2) before the first comparison, outside referee fidelity_referee/REFEREE.md (FIX THEN SHIP, fixes applied
# in fidelity_index/build_page.py, recorded in fidelity_index/CHECKS.md). The body is fidelity_index/fidelity.html, rendered by build_page.py. Ledger rows fid.* (surface desk_fidelity).
_fd = open(os.path.join(HERE, '..', 'fidelity_index', 'fidelity.html'), encoding='utf-8').read()
_fd_main = _fd[_fd.index('<main class="wrap">') + len('<main class="wrap">'):_fd.index('</main>')].strip('\\n')
assert _fd_main.startswith('<section id="hl-slot"'), 'FIDELITY: the headline block is not where build_page.py puts it'
_FIDSLOT = _fd_main[:_fd_main.index('</section>') + len('</section>')]
_FIDBODY = _fd_main[len(_FIDSLOT):].strip('\\n')
assert '<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>' in _FIDBODY, 'FIDELITY: the division line is not where build_page.py puts it'
assert 'This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.' in _FIDBODY, 'FIDELITY: the required Census API line is missing'
_FIDBODY = _FIDBODY.replace('<table class="bench">', '<table class="mtx">').replace('<div class="tw">', '<div class="tablewrap">')
PAGES['/census/fidelity'] = page('/census/fidelity', 'CENSUS | State Counts Against the ACS | Heuremen LLC', 'CENSUS: state divorce and marriage counts reported to the CDC, set beside the Census American Community Survey estimates and the 90 percent margin Census states, women and men both shown.', _FIDBODY, hero_slim('CENSUS &middot; State Counts Against the ACS'))
_FEED.append(('/census/fidelity', 'CENSUS: State Counts Against the ACS', 'State divorce and marriage counts reported to the CDC, set beside the Census American Community Survey estimates and their stated margin.'))
'''
sub(bs, "_CENSUSDIV = ('<section", block + "_CENSUSDIV = ('<section")
sub(bs, "  '<p class=\"meta\">Sources: U.S. Census Bureau, Economic Indicators Time Series API and explanatory notes.", "  '<p>The third desk sets the state counts of marriages and divorces reported to the CDC beside the Census Bureau\\'s American Community Survey estimates. Its page is <a href=\"/census/fidelity\">CENSUS Fidelity</a>. It was run once and does not refresh.</p>'\n  '<p class=\"meta\">Sources: U.S. Census Bureau, Economic Indicators Time Series API and explanatory notes.")
sub(bs, "('/census/coverage', 'COVERAGE', 'The 2020 Census state counts against the Census Bureau\\'s own survey')", "('/census/coverage', 'COVERAGE', 'The 2020 Census state counts against the Census Bureau\\'s own survey'), ('/census/fidelity', 'FIDELITY', 'State marriage and divorce counts from the CDC against the Census survey estimates')")
sub(B + '/ledger/ledger.py', "    'desk_censuscov':", "    'desk_fidelity': 'indahl-ai/census/fidelity.html',   # 11 Nov 2026: the CENSUS FIDELITY desk (division CENSUS); page body from fidelity_index/fidelity.html (one-time desk, no feed)\n    'desk_censuscov':")
sub(B + '/ledger/receipts.py', "'census_index': 'census',", "'census_index': 'census', 'fidelity_index': 'fidelity', 'census_coverage': 'census-coverage',")
pp = B + '/ledger/push_public.sh'
sub(pp, "'census': ('census_index', A),", "'census': ('census_index', A), 'fidelity': ('fidelity_index', A), 'census-coverage': ('census_coverage', A),")
sub(pp, "print('  public desks: %d file(s) re-synced from the working folders' % n)", "for f in ('gate2_rate_misses.csv', 'gate2_swap_check.json'):   # 11 Nov: FIDELITY publishes the gate 2 miss list and the swap test beside its code\n    sp, dd = os.path.join(B, 'fidelity_index', 'data', f), os.path.join(C, 'fidelity', 'data')\n    if os.path.isfile(sp) and os.path.isdir(os.path.dirname(dd)):\n        os.makedirs(dd, exist_ok=True); dp = os.path.join(dd, f)\n        if not (os.path.exists(dp) and filecmp.cmp(sp, dp, shallow=False)): shutil.copy2(sp, dp); n += 1\nprint('  public desks: %d file(s) re-synced from the working folders' % n)")
print('patched')
