"""extract_oy.py: reads the published OY pages (the HTML the site serves) and returns their tables as plain records.
Standard library only. Every text value is the page text with tags removed and character references decoded. Every link is the address as published.
Used by build_package.py. It is not part of the pack."""
import re, html, os, json
SITE = os.path.expanduser('~/bones-forge/indahl-ai/')

def T(s):
    s = re.sub(r'<a class="fb nosig"[^>]*>Follow</a>', '', s)   # 11 Nov: the Follow link entities.py puts beside a name is not page text
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def tables(page):
    return re.findall(r'<table class="mtx">(.*?)</table>', page, re.S)

def trs(tbl):
    body = tbl.split('</thead>', 1)[1]
    return [re.findall(r'<td[^>]*>(.*?)</td>', r, re.S) for r in re.findall(r'<tr>(.*?)</tr>', body, re.S)]

def heads(tbl):
    return [T(x) for x in re.findall(r'<th[^>]*>(.*?)</th>', tbl.split('</thead>', 1)[0], re.S)]

A = re.compile(r'<a href="([^"]*)">([^<]*)</a>(?:\s*<span class="srckind">\(([^)]*)\)</span>)?')

def first(page_re, page, flags=re.S):
    m = re.search(page_re, page, flags); assert m, page_re; return m

def text_blocks(page):
    big = T(first(r'<div class="hl-big">(.*?)</div>', page).group(1))
    line = T(first(r'<p class="hl-line">(.*?)</p>', page).group(1))
    how = T(first(r'<h2>How these rows were read</h2><p>(.*?)</p>', page).group(1))
    chat = T(first(r'<h2 id="findings">(.*?)</h2>', page).group(1))
    note = T(first(r'<h2 id="the-list">The list</h2>\s*<p class="meta">(.*?)</p>', page).group(1))
    bacc = T(first(r'<h2 id="private-baccalaureate-colleges">Private baccalaureate colleges</h2><p>(.*?)</p>', page).group(1))
    return {'headline_number': big, 'headline_text': line, 'how_these_rows_were_read': how, 'chatbot_table_heading': chat, 'list_note': note, 'private_baccalaureate_text': bacc}

def chatbot(tbl):
    out = []
    assert heads(tbl) == ['Institution', 'Document', 'Text', 'Source']
    for c in trs(tbl):
        m = A.fullmatch(c[3].strip()); assert m and m.group(2) == 'source', c[3]
        out.append({'institution': T(c[0]), 'document': T(c[1]), 'text': T(c[2]), 'source_url': html.unescape(m.group(1))})
    return out

def findings(tbl):
    assert heads(tbl) == ['Finding', 'Rows', 'Which']
    out = []
    for c in trs(tbl):
        which, det = (c[2].split('<details>', 1) + [''])[:2]
        found = {}
        if det:
            for li in re.findall(r'<li>(.*?)</li>', det, re.S):
                m = re.fullmatch(r'<b>(.*?)</b>: (.*)', li, re.S); assert m, li
                links = A.findall(m.group(2)); assert len(links) <= 1, li
                txt = T(m.group(2)); url = ''
                if links:
                    url = html.unescape(links[0][0]); assert links[0][1] == 'pilot source' and txt.endswith(' (pilot source)'), li
                    txt = txt[:-len(' (pilot source)')]
                nm = T(m.group(1)); assert nm not in found, nm
                found[nm] = (txt, url)
        items, pos = [], 0
        for m in A.finditer(which):
            items.append({'name': html.unescape(m.group(2)), 'url': html.unescape(m.group(1)), 'kind': m.group(3) or ''})
        rest = A.sub('\x00', which)
        plain = [T(x) for x in re.split(r'\x00', rest) if re.sub(r'[,\s]', '', x)]
        note = ''
        if items:
            for p in plain: items.append({'name': p, 'url': '', 'kind': ''})   # a row without a link, such as our own
        else:
            assert len(plain) == 1; note = plain[0]
        names = [i['name'] for i in items]
        assert set(found) <= set(names), (set(found) - set(names))
        for i in items: i['what_we_found'], i['what_we_found_source_url'] = found.get(i['name'], ('', ''))
        rows = T(c[1]); m = re.fullmatch(r'(\d+)(?: to (\d+))?(?: of (\d+))?', rows); assert m, rows   # 10 Nov 2026: a count the record cannot settle is printed as a range, a to b of n
        out.append({'finding': T(c[0]), 'rows': rows, 'count': int(m.group(1)), 'count_high': int(m.group(2)) if m.group(2) else None, 'of': int(m.group(3)) if m.group(3) else None, 'note': note, 'institutions': items})
    return out

def lst(tbl):
    assert heads(tbl) == ['Institution', 'First document cited', 'Measures its own AI policy', 'Released its own AI data', 'Pilot results read']   # 10 Nov 2026: was Public AI policy or guidance
    out = []
    for c in trs(tbl):
        m = A.fullmatch(c[0].strip()); inst = {'institution': T(c[0]), 'institution_url': '', 'institution_url_kind': ''}
        if m: inst = {'institution': html.unescape(m.group(2)), 'institution_url': html.unescape(m.group(1)), 'institution_url_kind': m.group(3) or ''}
        else: assert '<' not in c[0], c[0]
        m = A.fullmatch(c[1].strip()); pol = {'first_document_cited': T(c[1]), 'first_document_url': ''}
        if m: pol = {'first_document_cited': html.unescape(m.group(2)), 'first_document_url': html.unescape(m.group(1))}
        pil = T(c[4]); purl = ''
        m = re.search(r'\(<a href="([^"]*)">pilot source</a>\)\s*$', c[4].strip())
        if m: purl = html.unescape(m.group(1)); pil = T(c[4].strip()[:m.start()])
        if pil == '–': pil = ''
        out.append(dict(inst, **pol, measures_own_policy=T(c[2]), released_own_data=T(c[3]), pilot_results=pil, pilot_source_url=purl))
    return out

def dash(s):
    s = T(s); return None if s == '—' else s

def school_row(c):
    m = A.fullmatch(c[0].strip()); assert m and m.group(1).startswith('/oy/school/'), c[0]
    return {'unitid': m.group(1).rsplit('/', 1)[1], 'school': html.unescape(m.group(2)), 'state': T(c[1]), 'site': T(c[2]),
            'sentences': None if dash(c[3]) is None else int(T(c[3])), 'course_titles': None if dash(c[4]) is None else int(T(c[4])), 'read_in_full': dash(c[5]) or ''}

def schools_table(tbl):
    assert heads(tbl) in (['School', 'State', 'Site', 'Sentences', 'Course titles', 'Read in full'], ['School', 'State', 'Site', 'Sentences', 'Course titles', 'Read by us'])   # 11 Nov: the page heading is now 'Read by us'
    return [school_row(c) for c in trs(tbl)]

def school_page(page, unitid):
    """the sections of one school page, as published"""
    sec = first(r'<section class="legal">(.*?)</section>', page).group(1)
    meta = first(r'^<p class="meta">(.*?)</p>', sec).group(1)
    m = re.fullmatch(r'(.*?) &middot; (\w\w) &middot; <a href="/oy">All schools</a>', meta); assert m, meta
    carnegie, state = html.unescape(m.group(1)), m.group(2)
    h1 = T(first(r'<h1>(.*?)</h1>', page).group(1))
    school_p = first(r'<h2>School</h2><p>(.*?)</p>', sec).group(1)
    site_m = first(r'Site: <a href="([^"]*)">', school_p); fed = first(r'Federal ID <a href="([^"]*)">(\d+)</a>', school_p)
    assert fed.group(2) == unitid
    site_text = T(first(r'<h2>Site</h2><p>(.*?)</p>', sec).group(1))
    rif = re.search(r'<h2>Read (?:in full|in a browser)</h2><p>Page type: <b>(.*?)</b> (.*?) Read (\d+ \w+ \d{4})\.(?:</p>| [^<]*</p>)', sec, re.S)
    def listing(title, lbl):
        m = re.search(r'<h2>' + title + r'</h2>(.*?)(?=<h2>|<p class="meta">Pages read by script)', sec, re.S); assert m, title
        blk = m.group(1); items = []
        for li in re.findall(r'<li>(.*?)</li>', blk, re.S):
            a = re.fullmatch(r'(.*) <a href="([^"]*)">Source</a>', li, re.S); assert a, li
            items.append({'text': T(a.group(1)), 'url': html.unescape(a.group(2))})
        paras = [T(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', blk, re.S)]
        return paras, items
    sp, sitems = listing('Sentences on the school&rsquo;s own pages', 'sentences'); cp, citems = listing('Course titles in the public catalog', 'courses')
    read_on = first(r'<p class="meta">Pages read by script on (.*?)\. The data and the scripts are public', sec).group(1)
    return {'unitid': unitid, 'page_url': 'https://indahl.ai/oy/school/' + unitid, 'name': h1, 'carnegie': carnegie, 'state': state, 'school_paragraph': T(school_p),
            'site_url': html.unescape(site_m.group(1)), 'ncesid_url': html.unescape(fed.group(1)), 'site_read': site_text,
            'read_in_full_label': T(rif.group(1)).rstrip('.') if rif else '', 'read_in_full_note': T(rif.group(2)) if rif else '', 'read_in_full_date': rif.group(3) if rif else '',
            'sentences_note': ' '.join(sp), 'sentences': sitems, 'course_titles_note': ' '.join(cp), 'course_titles': citems, 'read_on': html.unescape(read_on)}
