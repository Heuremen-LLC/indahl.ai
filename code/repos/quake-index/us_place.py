"""us_place.py: display only (added 10 Nov 2026 at the outside referee, R2). Is an event in the United States or its territories, read from the
ComCat place or title text. Rule: the text names a US state or territory, or ends in ', CA' (ComCat's short form for California), or is one of
the named exceptions below. Everything else is elsewhere. The Mariana Islands region and the Hubbard Glacier event (Alaska and Yukon border) are
counted as US. Never used for an outcome."""
import re
STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
          'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
          'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
          'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
          'Guam', 'Northern Mariana Islands', 'Puerto Rico', 'U.S. Virgin Islands', 'American Samoa']
EXTRA = ('Ridgecrest Earthquake Sequence', 'Hubbard Glacier', 'Mariana Islands region', 'the Mariana Islands')
def is_us(place, title=''):
    t = '%s | %s' % (place or '', title or '')
    if any(re.search(r'\b%s\b' % re.escape(s), t) for s in STATES): return True
    if re.search(r', CA\b', t): return True
    return any(x in t for x in EXTRA)
