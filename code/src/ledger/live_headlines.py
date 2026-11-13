#!/usr/bin/env python3
"""live_headlines.py: the ledger rule for headline numbers that move on every read (10 Nov 2026, cold read row 12, Wayfinder: "it depends on
the headline and how big the change is; WATER is good for every twelve hours").

Each live desk headline has ONE ledger row of kind 'live_headline'. The row names the feed and the JSON field the headline comes from, the
desk's refresh cadence in hours, and the material-change rule. check_ledger.py reads every such row against the live feed: the field must exist
and the feed's stamp must be fresher than cadence x 1.5. The value is not compared there, because it moves on every read.

A new ledger VALUE row (kind 'live_value') is written only on a material change:
  interval  the outcome label flips (ABOVE / BELOW / CONSISTENT / CANNOT_TELL), or the headline number moves outside the interval the
            previous value row printed. Moves inside it stay live on the page without a new row.
  set       the plan's stated rule, read on a set of fields: a value row when any of them changes (and on an outcome flip, if named).
  flip      the plan states no width and no rule for this number: a flip of outcome only. A desk with no outcome writes no value rows.
The first run writes one baseline value row per desk that can ever write one. The previous value row of a desk is marked superseded, never deleted.

  live_headlines.py seed           add the live_headline rows that are missing (needs ledger/CHECKS.md with a complete last entry)
  live_headlines.py run            write value rows on material changes (tick-bus rider, or by hand). --dry prints and writes nothing
  live_headlines.py check          what check_ledger.py runs: field present, stamp fresh
  live_headlines.py selftest       planted feeds against the change rule
Python 3.9 (the tick bus's own python), standard library only."""
import os, sys, json, re, time, hashlib, urllib.request, datetime as D
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.expanduser('~/bones-forge')
sys.path.insert(0, HERE)
SNAP = os.path.join(HERE, 'live_values'); LOCK = os.path.join(HERE, '.live_headlines.lock'); CHECKS = 'ledger/CHECKS.md'
SITE = 'https://indahl.ai'
TICK_H = 0.0917   # median wall time of one tick-bus tick since 3 Nov 2026 (watch/ticks.log), 5.5 minutes

# Paths are lists of keys. An int is a list index, '*' takes every value of a dict or list, and a dict picks the first list item whose fields match.
P = lambda *k: list(k)
DESKS = {
 'airq': dict(name='AIRQ', field=P('comparison', 'Map reading (atm channels, raw)', 'share'), n=P('comparison', 'Map reading (atm channels, raw)', 'n'), of=P('comparison', 'Map reading (atm channels, raw)', 'of'),
   show='pct', stamp=P('live', 'updated'), cadence_h=1.0, kind='interval',
   outcome=P('comparison', 'Map reading (atm channels, raw)', 'outcome'), lo=P('comparison', 'Map reading (atm channels, raw)', 'share_lo'), hi=P('comparison', 'Map reading (atm channels, raw)', 'share_hi'),
   cadence_why='The airq_live_tick.py rider runs every 10 ticks (median 0.93 h since 3 Nov) and keeps the live block of the feed, stamped live.updated, and PLAN.md says each hour. The headline share itself comes from the window read, run by hand once per window (feed fields window and updated).',
   rule_why='PLAN.md line 17 states a 95 percent Wilson interval on monitors with the outcome rule beside it.'),
 'hosts': dict(name='HOSTS', field=P('problems_now'), show='count', stamp=P('updated'), cadence_h=0.25, kind='flip', outcome=P('headline', 'outcome'),
   cadence_why='The hosts_tick.py rider runs every 2 ticks (median 0.19 h) and PLAN.md says about 12 minutes. Rounded up to the quarter hour.',
   rule_why='PLAN.md line 12 says the count is a display with no outcome, and it states no width. So the rule is a flip of outcome only, read on the desk\'s own 24-hour flag test (feed headline.outcome). Moves of the count write no row.'),
 'trials': dict(name='TRIALS', field=P('all', 'share_no_results'), n=P('all', 'no_results'), of=P('all', 'n'), show='pct1', stamp=P('read'), cadence_h=5.0, kind='interval',
   outcome=P('all', 'outcome'), lo=P('all', 'lo'), hi=P('all', 'hi'),
   cadence_why='The trials_tick.py rider runs every 48 ticks (median 4.45 h) and PLAN.md says the whole set is re-read about every 5 hours.',
   rule_why='PLAN.md line 22 states a 95 percent Wilson interval and lines 23 to 24 the outcome rule.'),
 'hpt': dict(name='HPT', field=P('comparison', '2 The file it links resolves to data', 'share'), n=P('comparison', '2 The file it links resolves to data', 'n'), of=P('comparison', '2 The file it links resolves to data', 'of'),
   show='n_of', stamp=P('updated'), cadence_h=168.0, kind='interval',
   outcome=P('comparison', '2 The file it links resolves to data', 'outcome'), lo=P('comparison', '2 The file it links resolves to data', 'share_lo'), hi=P('comparison', '2 The file it links resolves to data', 'share_hi'),
   cadence_why='The hpt_tick.py rider runs every 1,740 ticks (about 160 h) and PLAN.md says about 7 days.',
   rule_why='PLAN.md line 15 states the outcome rule on a 95 percent Wilson interval over AGREE plus DISAGREE.'),
 'support': dict(name='SUPPORT', field=P('all', 'share'), n=P('all', 'unreleased'), of=P('all', 'tested'), show='pct', stamp=P('updated'), cadence_h=4.5, kind='interval',
   outcome=P('all', 'outcome'), lo=P('all', 'share_lo'), hi=P('all', 'share_hi'),
   cadence_why='The support_tick.py rider runs every 48 ticks (median 4.45 h). PLAN.md line 8 says every 7 days, and the rider re-reads faster than that.',
   rule_why='PLAN.md line 13 states the outcome rule, read on the bootstrap interval over products that PLAN.md line 27 names for the cycle-level outcome.'),
 'fedsep': dict(name='FEDSEP', field=P('pooled', 'Next year, September projection', 'share'), n=P('pooled', 'Next year, September projection', 'outside'), of=P('pooled', 'Next year, September projection', 'triples'),
   show='n_of', stamp=P('updated'), cadence_h=3.5, kind='interval',
   outcome=P('pooled', 'Next year, September projection', 'outcome'), lo=P('pooled', 'Next year, September projection', 'share_lo'), hi=P('pooled', 'Next year, September projection', 'share_hi'),
   cadence_why='The fedsep_tick.py rider runs every 36 ticks (median 3.34 h) and PLAN.md line 43 says about 3.5 hours.',
   rule_why='PLAN.md line 12 states a 95 percent bootstrap interval over years and line 13 the outcome rule against the 30 percent the Fed\'s 70 percent range leaves outside.'),
 'airline': dict(name='AIRLINE', field=P('headline', 'n'), n=P('headline', 'n'), of=P('headline', 'of'), show='n_of', stamp=P('updated'), cadence_h=560.0, kind='set', keys=[P('headline', 'above')],
   cadence_why='The airline_summary.py rider runs every 6,000 ticks (about 556 h, rounded up to 560 h). The BTS read behind the count is made by hand when BTS posts new months, each with a plan addendum (PLAN.md line 33).',
   rule_why='The count of airlines is not a share and has no width. The plan\'s stated rule is per airline (PLAN.md line 13, ABOVE when the lower end of the route bootstrap interval is above +1 minute). A value row is written when the list of airlines read ABOVE changes, which is the only way the count moves.'),
 'ailuminate': dict(name='AILUMINATE', field=P('table', '*', 'overall'), show='range', stamp=P('updated'), cadence_h=2.5, kind='set', keys=[P('table', '*', 'overall')], outcome=P('headline', 'outcome'),
   cadence_why='The ailuminate_tick.py rider runs every 24 ticks (median 2.22 h) and PLAN.md line 36 says about 2.3 hours. Rounded up to the half hour.',
   rule_why='The range has no width. The plan\'s stated rule is test B (PLAN.md line 15): a system is CHANGED when any of its values differs from the first value stored. A value row is written when any published overall score changes, or when test A flips.'),
 'weights': dict(name='WEIGHTS', field=P('ever', 'share'), n=P('ever', 'n'), of=P('ever', 'of'), show='n_of', stamp=P('updated'), cadence_h=3.5, kind='interval',
   outcome=P('headline', 'outcome'), lo=P('ever', 'share_lo'), hi=P('ever', 'share_hi'),
   cadence_why='The weights_tick.py rider runs every 36 ticks (median 3.34 h) and PLAN.md line 30 says about 3 hours. Rounded up to the half hour.',
   rule_why='The feed prints a 95 percent Wilson interval on the changed-on-any-pass share. Its outcome is the plan\'s test on the latest pair (PLAN.md line 13), since the any-pass share carries none.'),
 'campus': dict(name='CAMPUS', field=P('state_now', 'Opens (HTTP 200)'), n=P('state_now', 'Opens (HTTP 200)'), of=P('sources'), show='n_of', stamp=P('updated'), cadence_h=7.0, kind='set', keys=[P('state_now', 'Not found (404, 410)')],
   cadence_why='The campus_tick.py rider runs every 72 ticks (median 6.69 h) and PLAN.md line 38 says about 7.0 hours.',
   rule_why='The count has no width and no outcome. The plan\'s stated rule is GONE: a source that returned 200 and then 404 or 410, never on one failure (PLAN.md line 17). A value row is written when the count of sources not found changes. Blocked reads and errors that come and go stay live on the page.'),
 'secrecords': dict(name='SECRECORDS', field=P('comparison', 'HSTS preload header', 'share'), n=P('comparison', 'HSTS preload header', 'n'), of=P('comparison', 'HSTS preload header', 'of'), show='pct', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('comparison', 'HSTS preload header', 'outcome'), lo=P('comparison', 'HSTS preload header', 'share_lo'), hi=P('comparison', 'HSTS preload header', 'share_hi'),
   cadence_why='The secrecords_tick.py rider runs every 62 ticks (median 5.75 h) and the PLAN.md cadence addendum says about 6.0 hours. The stamp is the start of a pass of about 1.4 h.',
   rule_why='PLAN.md line 14 states a 95 percent Wilson interval and line 15 the outcome rule.'),
 'hfsize': dict(name='HFSIZE', field=P('comparison', 'share'), n=P('comparison', 'n'), of=P('comparison', 'of'), show='n_of', stamp=P('updated'), cadence_h=6.5, kind='interval',
   outcome=P('comparison', 'outcome'), lo=P('comparison', 'share_lo'), hi=P('comparison', 'share_hi'),
   cadence_why='The hfsize_tick.py rider runs every 64 ticks (median 5.92 h) and the PLAN.md cadence addendum says about 6.2 hours. Rounded up to the half hour.',
   rule_why='PLAN.md line 15 states a 95 percent Wilson interval and line 16 the outcome rule.'),
 'pkglicense': dict(name='PKGLICENSE', field=P('disagree', 'share'), n=P('disagree', 'n'), of=P('disagree', 'of'), show='n_of', stamp=P('updated'), cadence_h=7.0, kind='interval',
   outcome=P('disagree', 'outcome'), lo=P('disagree', 'share_lo'), hi=P('disagree', 'share_hi'),
   cadence_why='The pkglicense_tick.py rider runs every 68 ticks (median 6.29 h) and the PLAN.md cadence addendum says about 6.6 hours. Each project is re-read once its last read is 30 days old (pkglicense_tick.py line 75).',
   rule_why='PLAN.md line 14 states a 95 percent Wilson interval and line 15 the outcome rule.'),
 'pkginstall': dict(name='PKGINSTALL', field=P('comparison', 'share'), n=P('comparison', 'n'), of=P('comparison', 'of'), show='of_minus_n', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('comparison', 'outcome'), lo=P('comparison', 'share_lo'), hi=P('comparison', 'share_hi'),
   cadence_why='The pkginstall_tick.py rider runs every 60 ticks (median 5.56 h) and the PLAN.md cadence addendum says about 5.8 hours.',
   rule_why='PLAN.md line 13 states a 95 percent Wilson interval on the share that does not resolve and line 14 the outcome rule. The headline prints the commands that do resolve, the same reading from the other side.'),
 'revise': dict(name='REVISE', field=P('counts', 'Most recent, after the annual benchmark, against first', 'share'), n=P('counts', 'Most recent, after the annual benchmark, against first', 'exceed'),
   of=P('counts', 'Most recent, after the annual benchmark, against first', 'months'), show='n_of', stamp=P('updated'), cadence_h=3.5, kind='interval',
   outcome=P('counts', 'Most recent, after the annual benchmark, against first', 'outcome'), lo=P('counts', 'Most recent, after the annual benchmark, against first', 'share_lo'),
   hi=P('counts', 'Most recent, after the annual benchmark, against first', 'share_hi'),
   cadence_why='The revise_tick.py rider runs every 36 ticks (median 3.34 h) and the PLAN.md cadence addendum says about 3.5 hours. The counts move only when BLS posts a release.',
   rule_why='PLAN.md line 13 states a 95 percent Wilson interval over months and line 14 the outcome rule.'),
 'change': dict(name='CHANGE', field=P('lifespan', 'Google, names with preview', 'under180'), n=P('lifespan', 'Google, names with preview', 'under180'), of=P('lifespan', 'Google, names with preview', 'n'),
   show='n_of', stamp=P('updated'), cadence_h=2.5, kind='set', keys=[P('lifespan', 'Google, names with preview', 'under180'), P('lifespan', 'Google, names with preview', 'n')], outcome=None,   # 10 Nov 2026 (newsletter audit): the lifespan table is descriptive in the plan, so this headline carries no outcome
   cadence_why='The change_tick.py rider runs every 24 ticks (median 2.22 h) and PLAN.md line 10 says every 24 ticks. Rounded up to the half hour.',
   rule_why='The lifespan count has no width. The plan\'s stated rule is per dated row: NEW, MOVED_LATER, MOVED_EARLIER, REMOVED or DATE_ADDED (PLAN.md line 11). A value row is written when the count under six months or the count of dated preview models changes, which is when such a row enters or leaves. PLAN.md Addendum 1 (line 29) calls the lifespan table descriptive with no outcome, so the headline carries none. Until 10 Nov 2026 it carried the held-or-moved test\'s outcome, which is not this number.'),
 'cadence': dict(name='CADENCE', field=P('most_overdue', 0, 'age_days'), show='years', stamp=P('updated'), cadence_h=0.25, kind='set', keys=[P('most_overdue', 0, 'title'), P('most_overdue', 0, 'portal')],
   cadence_why='The cadence_tick.py rider runs every 2 ticks (median 0.19 h) and rewrites the feed each run. One portal is re-read when its last read is 24 h old (cadence_tick.py line 28). Rounded up to the quarter hour.',
   rule_why='The headline is the series read furthest past its stated interval. It is BELOW by construction under the plan\'s rule (PLAN.md line 14, BELOW when the age is more than twice the stated interval) and has no width of its own. A value row is written when another series takes the top place. Its age grows by a day each day without a new row.'),
 'linkrot': dict(name='LINKROT', field=P('all', 'rot_share'), n=P('all', 'gone'), of=P('all', 'links'), show='pct1', stamp=P('updated'), cadence_h=0.75, kind='interval',
   outcome=P('all', 'outcome'), lo=P('all', 'lo'), hi=P('all', 'hi'),
   cadence_why='The linkrot_tick.py rider runs every 6 ticks (median 0.56 h). Each link is re-read once its last read is 7 days old (linkrot_tick.py line 50). Rounded up to the quarter hour.',
   rule_why='PLAN.md line 14 states a 95 percent Wilson interval and line 15 the outcome rule.'),
 'launch': dict(name='LAUNCH', field=P('flown_watched'), show='count', stamp=P('updated'), cadence_h=0.75, kind='flip', outcome=P('cells', {'lead': '7 days'}, 'outcome'),
   cadence_why='The launch_tick.py rider runs every 6 ticks (median 0.56 h). Rounded up to the quarter hour.',
   rule_why='The plan states no rule and no width for the count of watched launches that have flown. So the rule is a flip of outcome only, read on the plan\'s own test at the 7-day lead (PLAN.md lines 14 to 20).'),
 'tape': dict(name='TAPE', field=P('head', 't'), show='age', stamp=P('head', 't'), cadence_h=0.75, kind='flip', outcome=None,
   cadence_why='The tape_tick.py rider runs every 6 ticks (median 0.56 h) and PLAN.md line 4 says every 6 ticks. Rounded up to the quarter hour.',
   rule_why='The headline is the age of the newest chained entry, a clock. The plan states no rule, no width and no outcome for it, so the rule is a flip of outcome only, and with no outcome this headline writes no value rows. The freshness check is what reads it.'),
 'water': dict(name='WATER', field=P('headline_lead6', 'mead', 'band', 'share'), n=P('headline_lead6', 'mead', 'band', 'inside'), of=P('headline_lead6', 'mead', 'band', 'n'), show='n_of', stamp=P('updated'), cadence_h=12.0, kind='interval',
   outcome=P('headline_lead6', 'mead', 'band', 'outcome'), lo=P('headline_lead6', 'mead', 'band', 'lo'), hi=P('headline_lead6', 'mead', 'band', 'hi'),
   cadence_why='Wayfinder\'s word on 10 Nov 2026: WATER is good for every twelve hours. The water_tick.py rider runs every 5 ticks (about half an hour). The 24-Month Study is monthly.',
   rule_why='PLAN.md states a 95 percent Wilson interval on water years and the outcome rule against the 80 percent Reclamation states. The value rows water.band6.mead and water.band6.powell already hold the shipped reading.'),
 'cone': dict(name='CONE', field=P('cells', {'cell': 'Atlantic, whole path'}, 'share'), n=P('cells', {'cell': 'Atlantic, whole path'}, 'inside'), of=P('cells', {'cell': 'Atlantic, whole path'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('cells', {'cell': 'Atlantic, whole path'}, 'outcome'), lo=P('cells', {'cell': 'Atlantic, whole path'}, 'lo'), hi=P('cells', {'cell': 'Atlantic, whole path'}, 'hi'),
   cadence_why='The cone_tick.py rider runs every 60 ticks (median 0.0917 h a tick, about 5.5 h) and refreshes the current-season NHC files at most every 6 hours (cone_tick.py CURRENT_HOURS). Rounded up to 6 h. The headline cell moves only when NHC posts a new HURDAT2 file.',
   rule_why='PLAN.md (Rules, Cells, Intervals) states a storm-level block bootstrap 95 percent interval over scored whole-path forecasts and the outcome rule against NHC\'s stated 60 to 70 percent. The value rows cone.cell.al.path and cone.cell.ep.path hold the shipped reading.'),
 'quake': dict(name='QUAKE', field=P('headline_cell', 'share'), n=P('headline_cell', 'inside'), of=P('headline_cell', 'scored'), show='n_of', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('headline_cell', 'outcome'), lo=P('headline_cell', 'lo'), hi=P('headline_cell', 'hi'),
   cadence_why='The quake_tick.py rider runs every 60 ticks (median 0.0917 h a tick, about 5.5 h). Rounded up to 6 h. The count moves when a forecast window has been closed for 7 days and the catalog is read again.',
   rule_why='PLAN.md (Rules, Range cells) states the union of a 95 percent Wilson interval and a sequence-block bootstrap and the outcome rule against the stated 95 percent. The value rows quake.cover.m3 and the window and magnitude rows hold the shipped reading.'),
 'census': dict(name='CENSUS', field=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'share'), n=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'inside'), of=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=26.0, kind='interval',
   outcome=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'outcome'), lo=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'lo'), hi=P('cells', {'series': 'SALES', 'geo': 'US', 'step': 'S1'}, 'hi'),
   cadence_why='The census_tick.py rider (census_tick.py --pull --publish) runs every 264 ticks (median 0.0917 h a tick, about 24 h) and puts census_live in the site KV. Rounded up to 26 h. The headline cell moves only when ALFRED records a new vintage or a new width copy is made.',
   rule_why='PLAN.md (Rules) states a 95 percent Wilson interval over scored rows and the outcome rule against 90 percent. The value rows census.cell.sales.us.s1 and the other cell rows hold the shipped reading.'),
 'flu': dict(name='FLU', field=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'share'), n=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'inside'), of=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=12.0, kind='interval',
   outcome=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'outcome'), lo=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'lo'), hi=P('cells', {'cell': 'all horizons', 'level': '95', 'side': 'final'}, 'hi'),
   cadence_why='The flu_tick.py rider runs every 66 ticks (median 0.0917 h a tick, about 6 h) and pulls the hub at most every 6 hours. Doubled to 12 h so one late tick does not read stale. The count moves when the hub posts a new ensemble or a new release of the target data, about weekly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over target weeks and the outcome rule against the stated 95 percent. The value rows flu.cell.all95 and flu.cell.h0_95 to flu.cell.h3_95 hold the shipped reading.'),
 'credit': dict(name='CREDIT', field=P('ruler1', {'year': 2025}, 'timely'), show='pct1', stamp=P('updated'), cadence_h=192.0, kind='interval',
   outcome=P('ruler1', {'year': 2025}, 'outcome'), lo=P('ruler1', {'year': 2025}, 'lo'), hi=P('ruler1', {'year': 2025}, 'hi'),
   cadence_why='The credit_tick.py rider runs every 1,800 ticks (median 0.0917 h a tick, about 7 days) and downloads the complaint file when it is older than 160 h. Rounded up to 8 days. The 2025 cell moves only when complaints received in 2025 are added or change in the file.',
   rule_why='PLAN.md (Rules, Headline) fixes ruler one for 2025: the database timely share with a company-month block bootstrap 95 percent interval against the band 99.55 to 99.65 percent that the CFPB printed 99.6 percent allows. The value row credit.timely.2025 holds the shipped reading.'),
 'tornado': dict(name='TORNADO', field=P('cells', {'cell': 'United States', 'preliminary': False}, 'bands', {'band': '10 to 15'}, 'freq'), show='pct1', stamp=P('updated'), cadence_h=24.0, kind='interval',
   outcome=P('cells', {'cell': 'United States', 'preliminary': False}, 'bands', {'band': '10 to 15'}, 'outcome'), lo=P('cells', {'cell': 'United States', 'preliminary': False}, 'bands', {'band': '10 to 15'}, 'lo'), hi=P('cells', {'cell': 'United States', 'preliminary': False}, 'bands', {'band': '10 to 15'}, 'hi'),
   cadence_why='The tornado_tick.py rider runs every 222 ticks (median 0.0917 h a tick, about 20 h) and refetches the current year outlook file and the current fiscal year warnings when they are 20 h old. Rounded up to 24 h. The closed-year headline cell moves only when SPC posts a new database year.',
   rule_why='PLAN.md (Rules, Headline) fixes the United States closed-years 10 to 15 percent band, a day-level block bootstrap 95 percent interval and the band outcome rule. The value row tornado.us.band10_15 holds the shipped reading.'),
 'steo': dict(name='STEO', field=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'share'), n=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'inside'), of=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=48.0, kind='interval',
   outcome=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'outcome'), lo=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'lo'), hi=P('cells', {'series': 'WTI', 'cell': 'all leads'}, 'hi'),
   cadence_why='The steo_tick.py rider runs every 264 ticks (about a day) and reads EIA monthly spot prices at most once a day. Doubled to 48 h. The count moves when EIA posts a new month, about monthly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over outcome months and the outcome rule against the stated 95 percent. The value rows steo.cell.wti.all and steo.cell.hh.all hold the shipped reading.'),
 'seasonal': dict(name='SEASONAL', field=P('cells', {'cell': 'temperature, leaning'}, 'observed'), n=P('cells', {'cell': 'temperature, leaning'}, 'hits'), of=P('cells', {'cell': 'temperature, leaning'}, 'rows'), show='pct', stamp=P('updated'), cadence_h=48.0, kind='interval',
   outcome=P('cells', {'cell': 'temperature, leaning'}, 'outcome'), lo=P('cells', {'cell': 'temperature, leaning'}, 'lo'), hi=P('cells', {'cell': 'temperature, leaning'}, 'hi'),
   cadence_why='The seasonal_tick.py rider runs every 264 ticks (about a day) and reads the CPC files at most once a day. Doubled to 48 h. The share moves when CPC adds a verified season, monthly.',
   rule_why='PLAN.md (Rules) states a moving-block bootstrap 95 percent interval over seasons and the outcome rule against the mean stated chance. The value rows seasonal.lean.temp and seasonal.lean.prec hold the shipped reading.'),
 'neo': dict(name='NEO', field=P('cells', {'cell': 'all leads'}, 'share'), n=P('cells', {'cell': 'all leads'}, 'inside'), of=P('cells', {'cell': 'all leads'}, 'scored'), show='n_of', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('cells', {'cell': 'all leads'}, 'outcome'), lo=P('cells', {'cell': 'all leads'}, 'lo'), hi=P('cells', {'cell': 'all leads'}, 'hi'),
   cadence_why='The neo_tick.py rider runs every 60 ticks (median 0.0917 h a tick, about 5.5 h) and stores one dated JPL copy at most every 6 hours (neo_tick.py SNAP_HOURS). Rounded up to 6 h. The count moves when an approach passes and JPL has a later solution for it.',
   rule_why='PLAN.md (Rules, Cells) states a 95 percent Wilson interval over scored headline rows, an object counted once, and the outcome rule against our 99.7 percent reading of 3-sigma. The value rows neo.cell.all, neo.cell.lead0_7, neo.cell.lead8_30 and neo.cell.lead30 hold the shipped reading.'),
 'solar': dict(name='SOLAR', field=P('headline', 'bss'), n=P('headline', 'consistent'), of=P('headline', 'bins'), show='n_of', stamp=P('updated'), cadence_h=6.0, kind='interval',
   outcome=P('headline', 'outcome'), lo=P('headline', 'lo'), hi=P('headline', 'hi'),
   cadence_why='The solar_tick.py rider runs every 60 ticks (about 5.5 h) and stores dated copies of the SWPC products at most every 6 hours (solar_tick.py SNAP_HOURS). Rounded up to 6 h. A new day is scored once it has been over for 3 days.',
   rule_why='PLAN.md (Headline row, Ruler two) fixes the headline as M-class flares on day one: the count of bins with 30 or more days that read cannot tell because their interval holds the mean stated chance (no bin reads consistent under Faults and Guards 2.0, PLAN_ADDENDUM_std2.md), and the Brier skill against climatology with a 27-day block bootstrap interval read against the band of minus 0.05 to plus 0.05. The value rows solar.m1.bins and solar.m1.skill hold the shipped reading.'),
}
# the static text on each desk page that the row records (the page's first question heading); WATER keeps its own surface key
H2 = {'airq': 'Do the sensors meet the targets the EPA wrote down?', 'hosts': 'Who serves the same model, and how steadily?', 'trials': 'Results due against results posted',
      'hpt': 'Is the price file where the rule says it is?', 'support': 'Is a cycle that is stated as supported still being released?', 'fedsep': 'Do the Fed\'s stated ranges describe what happened?',
      'airline': 'Are schedules getting longer while flights are not?', 'ailuminate': 'Do the published results stay what they say?', 'weights': 'Does a model name keep the same weights?',
      'campus': 'Do the pages schools published stay where they were?', 'secrecords': 'Do a domain\'s security records do what they say?', 'hfsize': 'Does the size in a model\'s name match the weights?',
      'pkglicense': 'Is the license a package states the license of its repository?', 'pkginstall': 'Does the install command a project gives work today?', 'revise': 'How far does a first estimate move?',
      'change': 'When a vendor says something ends on a date, does the date hold?', 'cadence': 'Stated Update Cadence Against Delivered', 'linkrot': 'Papers state where their code is. Does the link still lead there?',
      'launch': 'Stated launch time against the time it flew', 'tape': 'A record of what was published, in the order it was published', 'water': 'When Reclamation projects a lake level, where does the lake end up?', 'neo': 'When JPL states how close an object will pass, where does the latest solution put it?', 'seasonal': 'When the seasonal outlook states a chance, how often does it happen?', 'steo': 'When EIA states a price interval, how often does the price land inside it?', 'tornado': 'When the Storm Prediction Center draws a tornado chance, how often does a tornado come?', 'credit': 'When the CFPB states how companies answer complaints, what does its own database show?', 'quake': 'When the USGS states the odds of aftershocks, what follows?', 'census': 'When the Census Bureau states how uncertain a first print is, does the later value stay inside?', 'flu': 'When the CDC flu forecast states an interval, how often does the reported count land inside it?', 'cone': 'When the National Hurricane Center draws a cone, how often does the storm stay inside it?', 'solar': 'When SWPC states a chance of a solar flare or a geomagnetic storm, how often does it happen?'}
OUTS = ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')


def feed_url(slug): return '%s/%s/live.json' % (SITE, slug)


def get(url):
    u = url + ('&' if '?' in url else '?') + 'x=%d' % time.time()
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'heuremen-ledger/0.1 (+https://indahl.ai)'}), timeout=30).read())


_MISS = object()
def dig(o, path):
    """Follow a path. Returns _MISS when any step is absent. '*' maps over the rest and returns a list."""
    for i, k in enumerate(path):
        if k == '*':
            vals = list(o.values()) if isinstance(o, dict) else (o if isinstance(o, list) else None)
            if vals is None: return _MISS
            out = [dig(v, path[i + 1:]) for v in vals]
            return _MISS if not out or any(x is _MISS for x in out) else out
        if isinstance(k, dict):
            if not isinstance(o, list): return _MISS
            o = next((x for x in o if isinstance(x, dict) and all(x.get(a) == b for a, b in k.items())), _MISS)
            if o is _MISS: return _MISS
            continue
        if isinstance(o, dict) and k in o: o = o[k]
        elif isinstance(o, list) and isinstance(k, int) and -len(o) <= k < len(o): o = o[k]
        else: return _MISS
    return o


_MON = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
def stamp_epoch(v, now=None):
    """Feed stamps come in four shapes (cold read row 31): '10 Nov 11:42', '2026-11-10 11:32', '2026-11-10 02:56 UTC', '2026-11-10T11:21:18Z'. All UTC."""
    if not isinstance(v, str): return None
    now = now or time.time()
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?', v)
    if m: return D.datetime(*[int(x or 0) for x in m.groups()], tzinfo=D.timezone.utc).timestamp()
    m = re.match(r'(\d{1,2}) ([A-Za-z]{3}) (\d{2}):(\d{2})', v)
    if m and m.group(2).lower() in _MON:
        y = D.datetime.fromtimestamp(now, D.timezone.utc).year
        t = D.datetime(y, _MON.index(m.group(2).lower()) + 1, int(m.group(1)), int(m.group(3)), int(m.group(4)), tzinfo=D.timezone.utc)
        if t.timestamp() > now + 3600: t = t.replace(year=y - 1)
        return t.timestamp()
    return None


def fields_of(spec):
    out = [('field', spec['field']), ('stamp', spec['stamp'])]
    for k in ('n', 'of', 'outcome', 'lo', 'hi'):
        if spec.get(k): out.append((k, spec[k]))
    for i, k in enumerate(spec.get('keys') or []): out.append(('key%d' % i, k))
    return out


def _f(n): return '{:,}'.format(int(n))
def display(spec, d, now=None):
    v = dig(d, spec['field']); s = spec['show']
    if s == 'pct': return '%.0f%%' % (100 * v)
    if s == 'pct1': return '%.1f%%' % (100 * v)
    if s == 'n_of': return '%s of %s' % (_f(dig(d, spec['n'])), _f(dig(d, spec['of'])))
    if s == 'of_minus_n': return '%s of %s' % (_f(dig(d, spec['of']) - dig(d, spec['n'])), _f(dig(d, spec['of'])))
    if s == 'count': return _f(v)
    if s == 'range': return '%g to %g' % (min(v), max(v))
    if s == 'years': return '%.1f years (%s days)' % (v / 365.25, _f(v))
    if s == 'age':
        a = max(0, (now or time.time()) - (stamp_epoch(v) or 0)); return '%d min' % round(a / 60) if a < 5400 else '%.1f h' % (a / 3600)
    return str(v)


def reading(spec, d, now=None):
    """What a value row records for one feed: the number, its interval and outcome where the desk prints them, and the rule's key fields."""
    g = lambda k: (None if not spec.get(k) else (lambda x: None if x is _MISS else x)(dig(d, spec[k])))
    v = dig(d, spec['field'])
    return dict(value=None if v is _MISS else v, display=display(spec, d, now), outcome=g('outcome'), lo=g('lo'), hi=g('hi'),
                keys=[(lambda x: None if x is _MISS else x)(dig(d, k)) for k in (spec.get('keys') or [])], stamp=dig(d, spec['stamp']))


def material(spec, prev, cur):
    """Is cur a material change against the previous value row's reading? Returns the reason, or None."""
    if prev is None: return 'baseline: first value row under the live-headline rule'
    po, co = prev.get('outcome'), cur.get('outcome')
    if spec.get('outcome') and po in OUTS and co in OUTS and po != co: return 'outcome flipped %s -> %s' % (po, co)
    k = spec['kind']
    if k == 'interval':
        lo, hi, v = prev.get('lo'), prev.get('hi'), cur.get('value')
        if isinstance(v, (int, float)) and lo is not None and hi is not None and not (float(lo) - 1e-9 <= v <= float(hi) + 1e-9):
            return 'value %s moved outside the previous interval [%s, %s]' % (v, lo, hi)
    if k == 'set' and prev.get('keys') != cur.get('keys'): return 'a field the plan\'s rule reads changed: %s -> %s' % (json.dumps(prev.get('keys'))[:120], json.dumps(cur.get('keys'))[:120])
    return None


def rule_text(spec):
    if spec['kind'] == 'interval':
        r = 'A new value row is written only when the outcome flips or the headline number moves outside the interval the previous value row printed. Moves inside it stay live on the page.'
    elif spec['kind'] == 'set':
        r = 'A new value row is written only under the plan\'s stated rule, read on the fields listed in the row' + (', or when the outcome flips.' if spec.get('outcome') else '.')
    else:
        r = 'A new value row is written only when the outcome flips.' if spec.get('outcome') else 'No value rows are written for this headline.'
    return r + ' ' + spec['rule_why']


# ---------------------------------------------------------------------------------------------------------------- seed
def seed():
    import ledger as L
    ck = L.checks_ref(CHECKS); rows = L.load(); added = []
    for slug, s in DESKS.items():
        rid = 'live.%s.headline' % slug
        if rid in rows: continue
        surf = 'water' if slug == 'water' else 'desk_' + slug
        L.surface_path(surf)
        live = dict(feed=feed_url(slug), field=s['field'], stamp=s['stamp'], cadence_h=s['cadence_h'], stale_after_h=round(1.5 * s['cadence_h'], 3),
                    fields=dict(fields_of(s)), rule=s['kind'], show=s['show'], cadence_why=s['cadence_why'], rule_text=rule_text(s))
        rows[rid] = dict(checks=ck, id=rid, kind='live_headline',
                         claim='%s headline: the number comes from %s, field %s. Refresh cadence %g h, read stale after %g h. %s'
                               % (s['name'], feed_url(slug), json.dumps(s['field'], ensure_ascii=False), s['cadence_h'], 1.5 * s['cadence_h'], rule_text(s)),
                         value='live', lo=None, hi=None, unit='', outcome='RECORD', source=dict(file='watch/headlines.py', grep="def %s():" % slug),
                         surfaces=[dict(surface=surf, text=H2[slug])], status='live', live=live,
                         history=[dict(at=L.now(), change='added', evidence=CHECKS, why='live-headline rule, cold read row 12, Wayfinder 10 Nov 2026')])
        added.append(rid)
    L.save(rows); print('seed: added', len(added), 'live_headline rows:', ', '.join(added) or 'none')


# ---------------------------------------------------------------------------------------------------------------- check (for check_ledger.py)
def check_rows(rows, now=None):
    now = now or time.time(); drift = []; cache = {}
    for r in sorted(rows.values(), key=lambda r: r['id']):
        if r.get('kind') != 'live_headline' or r.get('status') != 'live': continue
        lv = r['live']; url = lv['feed']
        if url not in cache:
            try: cache[url] = get(url)
            except Exception as e: cache[url] = e
        d = cache[url]
        if isinstance(d, Exception): drift.append(('LIVEFEED', r['id'], url.replace(SITE, ''), '%s: %s' % (type(d).__name__, str(d)[:60]))); continue
        miss = [nm for nm, p in lv['fields'].items() if dig(d, p) is _MISS]
        if miss: drift.append(('LIVEFIELD', r['id'], url.replace(SITE, ''), 'absent on the live feed: ' + ', '.join('%s %s' % (m, json.dumps(lv['fields'][m], ensure_ascii=False)) for m in miss))); continue
        t = stamp_epoch(dig(d, lv['stamp']), now)
        if t is None: drift.append(('LIVESTAMP', r['id'], url.replace(SITE, ''), 'stamp %r does not read as a time' % (dig(d, lv['stamp']),))); continue
        age = (now - t) / 3600; lim = 1.5 * float(lv['cadence_h'])
        if age > lim: drift.append(('LIVESTALE', r['id'], url.replace(SITE, ''), 'stamp %s is %.2f h old, cadence %g h x 1.5 = %g h' % (dig(d, lv['stamp']), age, lv['cadence_h'], lim)))
    return drift


def ages(rows, now=None):
    now = now or time.time(); out = []
    for r in sorted(rows.values(), key=lambda r: r['id']):
        if r.get('kind') != 'live_headline' or r.get('status') != 'live': continue
        try: d = get(r['live']['feed']); t = stamp_epoch(dig(d, r['live']['stamp']), now); out.append((r['id'], round((now - t) / 3600, 2), 1.5 * r['live']['cadence_h']))
        except Exception as e: out.append((r['id'], None, type(e).__name__))
    return out


# ---------------------------------------------------------------------------------------------------------------- run (the writer)
def run(dry=False, now=None, force=None):
    """force: {slug: why}. 10 Nov 2026 (newsletter audit): a desk whose rule changed writes a new value row under the new rule even when the
    number moved inside the previous interval, so the ledger never keeps a reading made under a rule the desk no longer runs."""
    force = force or {}
    import ledger as L, fcntl
    now = now or time.time(); lk = open(LOCK, 'w'); fcntl.flock(lk, fcntl.LOCK_EX)
    rows = L.load(); hl = {}
    try: hl = json.load(open(os.path.join(ROOT, 'watch', 'headlines.json')))['pages']
    except Exception: pass
    wrote = []
    for slug, s in DESKS.items():
        hrow = rows.get('live.%s.headline' % slug)
        if not hrow or hrow.get('status') != 'live': continue
        try: d = get(feed_url(slug))
        except Exception as e: print('live_headlines: %s feed not read (%s), nothing written' % (slug, type(e).__name__)); continue
        if any(dig(d, p) is _MISS for _, p in fields_of(s)): print('live_headlines: %s field absent, nothing written' % slug); continue
        if s['kind'] == 'flip' and not s.get('outcome'): continue   # no outcome and no rule: this headline writes no value rows, the freshness check reads it
        cur = reading(s, d, now)
        prevs = [r for r in rows.values() if r.get('kind') == 'live_value' and r.get('live_of') == hrow['id'] and r.get('status') == 'live']
        prev = max(prevs, key=lambda r: r['history'][0]['at']) if prevs else None
        why = material(s, prev and prev.get('reading'), cur) or (('rule changed: ' + force[slug]) if slug in force else None)
        if not why: continue
        ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(now)); rid = 'live.%s.v%s' % (slug, ts)
        head = dict(id=rid, desk=slug, feed=feed_url(slug), at=ts, why=why, **cur)
        line1 = json.dumps(head, ensure_ascii=False, sort_keys=True)
        snap = os.path.join(SNAP, slug, ts + '.json'); rel = os.path.relpath(snap, ROOT)
        h = hl.get(slug) or {}; pub = ('%s %s' % (h.get('big', ''), h.get('line', ''))).strip()
        iv = (' [%s, %s]' % (cur['lo'], cur['hi'])) if cur.get('lo') is not None else ''
        claim = '%s headline at the feed stamp %s: %s%s%s. %s.%s' % (s['name'], cur['stamp'], cur['display'], (' (value %s%s)' % (cur['value'], iv)) if s['show'] not in ('range', 'age') else '',
                                                                 (', ' + cur['outcome']) if cur.get('outcome') else '', why[0].upper() + why[1:], (' Headline as published: ' + pub) if pub else '')
        print(('DRY ' if dry else '') + 'live_headlines: %s %s (%s)' % (rid, cur['display'], why))
        if dry: continue
        os.makedirs(os.path.dirname(snap), exist_ok=True)
        open(snap, 'w').write(line1 + '\n' + json.dumps(d, ensure_ascii=False) + '\n')
        oc = cur['outcome'] if cur.get('outcome') in OUTS else ('COUNT' if s['show'] in ('n_of', 'count') else 'LEVEL')
        rows[rid] = dict(checks=hrow['checks'], id=rid, kind='live_value', live_of=hrow['id'], claim=claim, value=str(cur['value']) if not isinstance(cur['value'], list) else cur['display'],
                         lo=None if cur.get('lo') is None else str(cur['lo']), hi=None if cur.get('hi') is None else str(cur['hi']), unit=s['show'], outcome=oc,
                         source=dict(file=rel, grep=line1), surfaces=[], status='live', reading=cur,
                         history=[dict(at=L.now(), change='added', evidence=rel, why=why)])
        if prev:
            prev['status'] = 'superseded'; prev['history'].append(dict(at=L.now(), change='superseded by ' + rid, why=why, evidence=rel))
        wrote.append(rid)
    if wrote and not dry: L.save(rows)
    if wrote and not dry:   # 10 Nov 2026 (findable pass): the desk's change feed posts the new entry now, not at the next site build
        try:
            import changes_feed; changes_feed.push(sorted({w.split('.')[1] for w in wrote}))
        except Exception as e: print('live_headlines: change feed not pushed (%s)' % type(e).__name__)
    print('live_headlines: %d value row%s written' % (len(wrote), '' if len(wrote) == 1 else 's'))
    return wrote


# ---------------------------------------------------------------------------------------------------------------- selftest
def selftest():
    iv = dict(kind='interval', outcome=['o'], field=['v'], lo=['lo'], hi=['hi'], show='pct', stamp=['t'])
    p = dict(value=0.20, lo=0.15, hi=0.26, outcome='ABOVE', keys=[])
    assert material(iv, None, p).startswith('baseline')
    assert material(iv, p, dict(p, value=0.25)) is None                       # inside the previous interval: stays live, no row
    assert 'outside' in material(iv, p, dict(p, value=0.27))                   # outside: a row
    assert 'outside' in material(iv, p, dict(p, value=0.14))
    assert 'flipped' in material(iv, p, dict(p, value=0.21, outcome='CANNOT_TELL'))   # a flip inside the interval: a row
    st = dict(kind='set', keys=[['k']], outcome=None, field=['v'], show='count', stamp=['t'])
    q = dict(value=5, keys=[['A', 'B']], outcome=None, lo=None, hi=None)
    assert material(st, q, dict(q, value=6)) is None                           # the count moves, the rule's field does not: no row
    assert material(st, q, dict(q, keys=[['A', 'C']])) is not None
    fl = dict(kind='flip', outcome=None, field=['v'], show='age', stamp=['t'])
    assert material(fl, dict(value=1, outcome=None), dict(value=2, outcome=None)) is None   # no outcome: never a row after the baseline
    d = {'a': {'b c': {'share': 0.5}}, 'cells': [{'lead': '1 day', 'o': 'X'}, {'lead': '7 days', 'o': 'Y'}], 't': {'x': {'s': 1}, 'y': {'s': 3}}}
    assert dig(d, ['a', 'b c', 'share']) == 0.5 and dig(d, ['cells', {'lead': '7 days'}, 'o']) == 'Y' and dig(d, ['t', '*', 's']) == [1, 3] and dig(d, ['a', 'nope']) is _MISS
    n = D.datetime(2026, 11, 10, 12, 0, tzinfo=D.timezone.utc).timestamp()
    for s, h in (('10 Nov 11:42', 0.3), ('2026-11-10 11:32', 0.4667), ('2026-11-10 02:56 UTC', 9.0667), ('2026-11-10T11:21:18Z', 0.645), ('10 Nov 11:32 UTC', 0.4667), ('31 Dec 23:00', 7525.0)):
        assert abs((n - stamp_epoch(s, n)) / 3600 - h) < 0.01, (s, (n - stamp_epoch(s, n)) / 3600)
    print('live_headlines selftest: change rule, paths and the stamp shapes read as planted')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['seed']: seed()
    elif a[:1] == ['run']: run(dry='--dry' in a, force=dict(x.split('=', 1) for x in a if '=' in x and not x.startswith('--')))   # run [--dry] slug=why ...
    elif a[:1] == ['check']:
        import ledger as L
        dr = check_rows(L.load()); print('live headlines: %d drift' % len(dr)); [print('  %-9s %-26s %-22s %s' % x) for x in dr]
        if '--ages' in a: [print('  %-26s age %s h, limit %s h' % x) for x in ages(L.load())]
        sys.exit(1 if dr else 0)
    elif a[:1] == ['selftest']: selftest()
    else: print(__doc__)
