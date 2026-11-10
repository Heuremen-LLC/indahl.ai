"""dsa_html.py: renders section_dsa.html for SOCIAL section 1 from the rows dsa_tick.py computes. Plain HTML, no scripts,
classes from indahl.ai/style.css (mtx, scroll, by, runbox, bench-note, meta, data, o-ABOVE and the other outcome classes)."""
import html, math

E = lambda s: html.escape('' if s is None else str(s), quote=True)
ORDER = ['Facebook', 'Instagram', 'Facebook and Instagram', 'TikTok', 'YouTube', 'X', 'LinkedIn', 'Snapchat', 'Pinterest', 'WhatsApp Channels', 'Amazon Store', 'AliExpress', 'Temu', 'Shein',
         'Zalando', 'Booking.com', 'Apple App Store', 'Google Maps', 'Google Play', 'Google Shopping', 'Pornhub', 'XVideos', 'XNXX', 'Stripchat', 'Wikipedia']
PER = ['2025H2', '2026H1']
PLAB = {'2025H2': 'Jul to Dec 2025', '2026H1': 'Jan to Jun 2026'}
ADS_ORDER = ['YouTube (ads)', 'Google Maps (ads)', 'Google Play (ads)']

def n(x): return '{:,}'.format(x) if isinstance(x, int) else ('' if x is None else str(x))
def word(o): return {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', 'NOTHING_RETURNED': 'nothing returned'}.get(o, o or '')
def fr(x):
    if x is None: return 'none'
    if x == 'unbounded' or (isinstance(x, float) and math.isinf(x)): return 'no upper edge'
    x = float(x)
    if x == 0: return '0'
    if abs(x - 0.9) < 0.005 or abs(x - 1.1) < 0.005: return '%.5g' % x   # Addendum 6.10: more figures near an edge (five, so 1.0997 does not print as 1.100)
    if x >= 100: return '{:,.0f}'.format(x)
    if x >= 10: return '%.1f' % x
    if 0.5 <= x < 2: return '%.3f' % x
    if x >= 0.1: return '%.2f' % x
    d = int(-math.floor(math.log10(x))) + 1   # two significant figures as a plain decimal
    return ('%.' + str(d) + 'f') % x
def oc_cell(r):
    o = r.get('outcome'); extra = ''
    if r.get('outcome_rule'): extra = '<span class="by"> defined after the data, plan rule reads %s</span>' % E(word(r['outcome_rule']))
    elif r.get('outcome_without_column_bound'): extra = '<span class="by"> row defined after the data, cannot tell from the column-sum bound alone, without it reads %s</span>' % E(word(r['outcome_without_column_bound']))
    elif r.get('defined_after_data'): extra = '<span class="by"> row defined after the data</span>'
    elif r.get('addendum5') or r.get('addendum6_5'): extra = '<span class="by"> band from the restriction columns, defined after the data</span>'
    return '<td class="o-%s">%s%s</td>' % (E(o), E(word(o)), extra)
def ratio_cell(r):
    if r.get('stated') is None:
        why = (r.get('reason') or '').replace('No stated figure: ', '').rstrip('.')
        d = (r.get('delivered') or {}).get('D_app')
        return '<td>no stated figure<span class="by"> %s%s</span></td>' % (E(why), ('. Database %s' % n(d)) if d is not None else '')
    d = r['delivered']; rr = r.get('ratio')
    head = 'zero stated' if r['stated'] == 0 else '%s [%s, %s]' % (fr(rr), fr(r.get('ratio_lo')), fr(r.get('ratio_hi')))
    return '<td>%s<span class="by"> report %s, database %s</span></td>' % (E(head), n(r['stated']), n(d['D_app']))

def render(rows, auto_period, sources, summ):
    by = {(r['platform'], r['period'], r['measure']): r for r in rows}
    o = []
    o.append('<section id="social-dsa">')
    o.append('<h2>Two filings, one platform</h2>')
    o.append('<p>Each very large online platform in the EU states its content moderation counts twice. Its transparency report gives totals for each half-year in a template the European Commission fixed. Its statements of reasons go one by one into the Commission’s DSA Transparency Database. We read the report’s figures against the count of the same platform’s statements for the same half-year, and print where the two agree as well as where they differ. YouTube, Google Maps and Google Play report their ads moderation in separate files, so their main rows leave out statements flagged as ads, and their ads are read on rows of their own.</p>')
    o.append('<p>Two of the four checks committed with the plan failed. Under the plan as committed every row would read cannot tell. We located both failures before reading the comparisons and replaced the checks in dated addenda. The readings below use those addenda, and every rule set after the data is labelled on its row.</p>')
    import datetime as _D
    nd = summ.get('newest_created_day') or ''
    try: rd = (_D.datetime.strptime(summ.get('updated_utc', ''), '%Y-%m-%d %H:%M') - _D.timedelta(hours=10)).date().isoformat()   # HST
    except Exception: rd = ''
    fmt = lambda x: _D.date.fromisoformat(x).strftime('%-d %B %Y') if x else ''
    o.append('<p class="meta">Database aggregates read %s (HST), with statements submitted up to %s. Reports are read in the latest version each platform publishes.</p>' % (E(fmt(rd)), E(fmt(nd))))
    o.append('<p class="data">Data: <a href="/social/dsa.json">rows</a> &middot; <a href="/social/dsa_summary.json">summary</a> &middot; <a href="/social/dsa_automation_monthly.json">automation fields by month</a></p>')
    # main table
    o.append('<h3>All measures and their automation</h3>')
    o.append('<p>Report states: the platform’s transparency report, sheet 8, scope Total number. Database holds: statements of reasons in the DSA Transparency Database for the same platform, counted by the date each decision applies from. Each cell shows the database count divided by the report’s figure. The bracket is the range the scope differences we can size allow. It is not a sampling interval.</p>')
    o.append('<div class="scroll"><table class="mtx wide"><thead><tr><th>Platform</th><th>Half-year</th><th>All measures, database over report [scope band]</th><th>Outcome</th><th>Solely automated</th><th>Outcome</th><th>Not automated</th><th>Outcome</th></tr></thead><tbody>')
    for p in ORDER:
        for per in PER:
            t = by.get((p, per, 'total'))
            if not t: continue
            if t['outcome'] == 'NOTHING_RETURNED':
                o.append('<tr><td>%s</td><td>%s</td><td colspan="6">%s<span class="by"> nothing returned</span></td></tr>' % (E(p), PLAB[per], E(t.get('reason'))))
                continue
            cells = ''.join(ratio_cell(by[(p, per, m)]) + oc_cell(by[(p, per, m)]) for m in ('total', 'solely', 'not'))
            o.append('<tr><td>%s</td><td>%s</td>%s</tr>' % (E(p), PLAB[per], cells))
    o.append('</tbody></table></div>')
    ph = [r for r in rows if r.get('platform_notes') and r['measure'] in ('total', 'solely', 'not', 'share', 'own', 'own_tc', 'own_illegal', 'own_auto', 'notice', 'notice_tf')]
    if ph:
        seen_q = {}
        for r in ph:
            for pn in r['platform_notes']: seen_q.setdefault((r['platform'], pn['quote']), []).append('%s %s' % (PLAB[r['period']], r['measure_label'].lower()))
        o.append('<p class="bench-note">Where a row rests on a platform\u2019s own note on a field, the note is quoted here, from the report:</p><ul class="bench-note">')
        for (p, q), where in seen_q.items():
            o.append('<li>%s, %s: \u201c%s\u201d</li>' % (E(p), E(', '.join(sorted(set(where)))), E(q)))
        o.append('</ul>')
    o.append('<p class="bench-note">For YouTube, Google Maps and Google Play these rows count only statements not flagged as ads, against the main report files. Facebook and Instagram each say some actions are reported for both services combined, so their own rows read cannot tell. The combined row reads both services together and also reads cannot tell. Both reports build their totals as sums of restriction columns, so the combined lower edge is the larger of the two services\u2019 largest columns, and that leaves every combined band too wide to read.</p>')
    o.append('<p class="bench-note">Solely automated is read against statements marked fully automated, and not automated against statements marked not automated. The database also has a partially automated category with no field in the report, so those statements are added to the upper edge of both bands. Stated zero: consistent if the database holds none, above if it holds at least 100 statements across the whole band.</p>')
    # own initiative and notices
    o.append('<details class="runbox"><summary>Own initiative and notices, every row</summary>')
    o.append('<p>Report states: sheets 5 and 6, row TOTAL, column “Number of measures taken at the provider’s own initiative”, and sheet 4, row TOTAL, actions taken on notices. Database holds: statements marked own voluntary initiative, or marked as an Article 16 or trusted flagger notice. Statements marked other type of notification are added to the upper edge of the own-initiative bands. The two filings label notice sources differently, so on notice rows the database band runs from zero to every statement the platform filed, and the report’s own count of notified items sets the stated upper edge. That leaves an outcome only where every statement the platform filed is still fewer than its notice actions. These notice rules were set after the data.</p>')
    o.append('<div class="scroll"><table class="mtx"><thead><tr><th>Platform</th><th>Half-year</th><th>Measure</th><th>Database over report [scope band]</th><th>Outcome</th></tr></thead><tbody>')
    for p in ORDER:
        for per in PER:
            for m in ('own', 'own_tc', 'own_illegal', 'own_auto', 'notice', 'notice_tf'):
                r = by.get((p, per, m))
                if not r or r['outcome'] == 'NOTHING_RETURNED': continue
                o.append('<tr><td>%s</td><td>%s</td><td>%s</td>%s%s</tr>' % (E(p), PLAB[per], E(r['measure_label']), ratio_cell(r), oc_cell(r)))
    o.append('</tbody></table></div></details>')
    # second reading B: share
    o.append('<h3>The platform’s own automation share against its filings</h3>')
    o.append('<p>Report share: solely automated measures over solely plus not automated measures, sheet 8. Database share: statements marked fully automated over all statements, with the upper edge counting partially automated statements as automated. The difference is in percentage points, database minus report, signed. The bracket is the range from the two date bases, the partially automated category, orders and spam measures the database does not require, and, where a report builds its total from column sums, the lower edge those sums allow. Agreement means within 5 points either way.</p>')
    o.append('<div class="scroll"><table class="mtx"><thead><tr><th>Platform</th><th>Half-year</th><th>Report share</th><th>Database share [band]</th><th>Difference, points [band]</th><th>Outcome</th></tr></thead><tbody>')
    for p in ORDER:
        for per in PER:
            r = by.get((p, per, 'share'))
            if not r: continue
            if r.get('stated_share') is None:
                o.append('<tr><td>%s</td><td>%s</td><td colspan="3">%s</td>%s</tr>' % (E(p), PLAB[per], E(r.get('reason')), oc_cell(r))); continue
            o.append('<tr><td>%s</td><td>%s</td><td>%.1f%%</td><td>%.1f%% [%.1f%%, %.1f%%]</td><td>%+.1f [%+.1f, %+.1f]</td>%s</tr>' % (E(p), PLAB[per], r['stated_share'] * 100, r['delivered_share'] * 100, r['delivered_share_lo'] * 100, r['delivered_share_hi'] * 100, r['diff_points'], r['diff_lo_points'], r['diff_hi_points'], oc_cell(r)))
    o.append('</tbody></table></div>')
    # second reading A
    o.append('<h3>The two automation fields inside the database</h3>')
    o.append('<p>Each statement carries two automation fields: whether the decision was fully, partially or not automated, and whether the content was detected by automated means. The shares below are for statements submitted from January to June 2026, with ads statements on rows of their own for YouTube, Google Maps and Google Play. No platform states a figure for these, so no outcome is given. Shares by month are in the data file.</p>')
    o.append('<div class="scroll"><table class="mtx"><thead><tr><th>Platform</th><th>Statements</th><th>Fully automated decision</th><th>Partially automated</th><th>Not automated</th><th>Automated detection</th><th>Fully automated decision, no automated detection</th></tr></thead><tbody>')
    ap = {(a['platform'], a['period']): a for a in auto_period}
    for p in [x for q in ORDER for x in ([q, q + ' (ads)'] if q + ' (ads)' in ADS_ORDER else [q])]:
        a = ap.get((p, '2026H1'))
        if not a: continue
        o.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%.1f%%</td><td class="n">%.1f%%</td><td class="n">%.1f%%</td><td class="n">%.1f%%</td><td class="n">%.1f%%</td></tr>' % (E(p), n(a['statements']), a['fully'] * 100, a['partially'] * 100, a['not'] * 100, a['detection_yes'] * 100, a['fully_no_detection'] * 100))
    o.append('</tbody></table></div>')
    # ads rows (Addendum 6.1)
    o.append('<h3>Ads moderation, read against the ads report files</h3>')
    o.append('<p>Report states: the separate ads files of the YouTube, Google Maps and Google Play reports, sheet 8 scope Total number and sheet 6 row TOTAL. Database holds: statements of the same service flagged as ads. These rows were set after the data.</p>')
    o.append('<div class="scroll"><table class="mtx"><thead><tr><th>Service</th><th>Half-year</th><th>Measure</th><th>Database over report [scope band]</th><th>Outcome</th></tr></thead><tbody>')
    for p in ADS_ORDER:
        for per in PER:
            for m in ('total', 'solely', 'not', 'own_tc'):
                r = by.get((p, per, m))
                if not r: continue
                o.append('<tr><td>%s</td><td>%s</td><td>%s</td>%s%s</tr>' % (E(p), PLAB[per], E(r['measure_label']), ratio_cell(r), oc_cell(r)))
            r = by.get((p, per, 'share'))
            if r and r.get('stated_share') is not None:
                o.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>report %.1f%%, database %.1f%% [%.1f%%, %.1f%%], difference %+.1f points [%+.1f, %+.1f]</td>%s</tr>' % (E(p), PLAB[per], E(r['measure_label']), r['stated_share'] * 100, r['delivered_share'] * 100, r['delivered_share_lo'] * 100, r['delivered_share_hi'] * 100, r['diff_points'], r['diff_lo_points'], r['diff_hi_points'], oc_cell(r)))
    o.append('</tbody></table></div>')
    # label-split rows (Addendum 6.7)
    labs = [r for r in rows if r.get('measure') == 'label_split']
    if labs:
        o.append('<h3>Splits the two filings label differently</h3>')
        o.append('<p>On these splits one half reads above and the other below, for the same platform and half-year. The two filings put the same decisions on different sides of the split, so neither half is read on its own. This reading was set after the data and carries no outcome.</p>')
        o.append('<div class="scroll"><table class="mtx"><thead><tr><th>Platform</th><th>Half-year</th><th>Split</th><th>First half, database over report</th><th>Second half, database over report</th></tr></thead><tbody>')
        for r in sorted(labs, key=lambda x: (ORDER.index(x['platform']) if x['platform'] in ORDER else 99, x['period'], x['split'])):
            cells = []
            for mm in r['members']:
                head = fr(mm['ratio']) if mm.get('ratio') is not None else 'zero stated'
                cells.append('<td>%s: %s<span class="by"> report %s, database %s, read %s</span></td>' % (E(mm['measure_label']), E(head), n(mm['stated']), n(mm['D_app']), E(word(mm['reading_before']))))
            o.append('<tr><td>%s</td><td>%s</td><td>%s</td>%s</tr>' % (E(r['platform']), PLAB[r['period']], 'automation' if r['split'] == 'automation' else 'ground', ''.join(cells)))
        o.append('</tbody></table></div>')
    # how we read it
    o.append('<h3>How we read it</h3>')
    o.append('<p>The stated figure is the one the platform printed in its report, quoted from the file with its name and date in the data. The delivered figure is the number of statements the same platform filed, counted from the Commission’s monthly aggregates of the database. We count statements by the date each decision applies from, including statements filed late up to the newest aggregate, and again by the date each statement was submitted. The band runs between the two counts. It also carries the partially automated category, statements that name only Iceland, Liechtenstein or Norway, and the measures the law does not require in the database: orders from authorities and spam. Above means the database holds more than the report states, beyond the whole band and by more than a tenth. Below means it holds less, by the same test. Either must clear its edge by at least 100 statements. Consistent means the whole band lies within a tenth of the stated figure. Cannot tell means none of these. Some differences neither source sizes, so no reading names a cause. A below reading can come from statements the law does not require where the recipient’s contact details are unknown or for deceptive high-volume commercial content that a report does not label as spam (DSA Article 17(2)), from a filing that counts one decision per item, per account or per restriction type, from a report that counts content filtered at upload, and from statements filed after the newest aggregate. An above reading can come from how each filing decides which decisions concern the EU, and from one decision filed as more than one statement, since the aggregates cannot detect re-filings.</p>')
    o.append('<p>The plan and its rules were committed before the first count of the database by platform. Changes made after the first counts are dated addenda to the plan. Rows that use a rule defined after the data say so. These cover the separate ads files, the notice rows, notes in which a platform says a field counts something the database does not hold, bounds taken from a report’s own restriction columns, splits the two filings label differently, and a minimum of 100 statements for an above or below reading. On six days in February and May 2026 the Commission’s simple aggregate counts statements twice. We read the complete aggregate, which matches the Commission’s published daily totals within 0.05% on every day but three at the turn of September and October 2026. The bands carry those three days, and two days in November 2026 with no published file. That allowance is wide on purpose, and it is the reason many trusted flagger and own-initiative illegal-content rows read cannot tell.</p>')
    # sources
    o.append('<h3>Sources</h3><ul>')
    o.append('<li><a href="https://transparency.dsa.ec.europa.eu/explore-data/download">DSA Transparency Database</a>, European Commission, monthly aggregates (complete version), CC BY 4.0. <a href="https://dsa.pages.code.europa.eu/transparency-database/dsa-tdb/data_sources.html">Aggregate files</a> and <a href="https://transparency.dsa.ec.europa.eu/page/api-documentation">field definitions</a>.</li>')
    o.append('<li><a href="https://digital-strategy.ec.europa.eu/en/library/implementing-regulation-laying-down-templates-concerning-transparency-reporting-obligations">Implementing Regulation (EU) 2024/2835</a>, the report template and its instructions. <a href="https://digital-strategy.ec.europa.eu/en/policies/dsa-brings-transparency">The Commission’s list of platform reports</a>. <a href="https://eur-lex.europa.eu/eli/reg/2022/2065/oj">Regulation (EU) 2022/2065</a>, Articles 17 and 24.</li>')
    seen = set()
    for p in ORDER:
        recs = [s for s in sources if s['service'] == p and s.get('status') == 'read']
        if not recs: continue
        links = []
        for s in sorted(recs, key=lambda x: x.get('period') or ''):
            url = s.get('page_url') or s.get('source_url')
            if url and 'fbcdn.net' in (s.get('source_url') or '') and s.get('page_url'): url = s['page_url']
            label = '%s report, publication date %s' % (PLAB.get(s.get('period'), s.get('period')), (('given as ' + s['published_display']) if s.get('published_display') else (s.get('published') or s.get('published_verbatim') or 'not given')))
            links.append('<a href="%s">%s</a>' % (E(url), E(label)) if url else E(label))
        o.append('<li>%s: %s.</li>' % (E(p), ' and '.join(links)))
    o.append('</ul>')
    o.append('<p class="meta">Named here and want to answer a row? <a href="/respond?u=social-dsa">Respond</a></p>')
    o.append('</section>')
    return '\n'.join(o) + '\n'
