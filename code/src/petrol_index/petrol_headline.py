"""petrol_headline.py: the PETROL headline (big number and line) from summary_petrol.json. Used by build_page.py and written to petrol_headline.json for watch/headlines.py (a petrol() rider in the style of census()). Standard library only."""
MON = ['January','February','March','April','May','June','July','August','September','October','November','December']
def mname(m): return '%s %s' % (MON[int(m[5:7]) - 1], m[:4])
def headline(S):
    h = S['part1']['headline']; c = h['counts']; w2 = S['part2']['headline']; e = w2['counts']; sc = sum(e.values())
    big = '%d below' % c['BELOW']
    line = ('OPEC+ states a required production level for each country and OPEC publishes what secondary sources say each produced. For %s the delivered figure sat above the required level by more than OPEC\'s own revision width for %d countries, below it for %d and inside it for %d, and %d could not be read. '
            'EIA\'s weekly estimate of US crude production, averaged by month, sat above EIA\'s monthly figure by more than the 2015 to 2019 spread in %d of %d months since 2020, below it in %d and inside it in %d.'
            % (mname(h['month']), c['ABOVE'], c['BELOW'], c['CONSISTENT'], c['CANNOT_TELL'], e['ABOVE'], sc, e['BELOW'], e['CONSISTENT']))
    line += ' Beside the OPEC+ month: %s Beside the EIA months: %s' % (S['part1']['headline']['req13']['line'], S['part2']['headline']['req13']['line'])
    return big, line
