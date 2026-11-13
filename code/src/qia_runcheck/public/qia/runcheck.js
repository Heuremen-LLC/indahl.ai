// QIA "Check a run": which published IBM calibration record was in force at the start of a run, what IBM stamped during it, the flags in that
// record for your qubits, and what changed between records. It reads only our static files under /qia/records/. Nothing you type leaves the page.
// The checks and the wording follow qia_check.py of the QIA Research Package (https://indahl.ai/qia). Every time shown is UTC.
(function (root) {
  'use strict';
  var FIELDS = ['T1', 'T2', 'readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1'], ERRS = FIELDS.slice(2);
  var UNIT = { T1: ' (µs)', T2: ' (µs)' };

  // ---- number formatting that matches Python's f'{v:.4g}' and f'{v:.3f}' (exact decimal value, ties to even) ----
  function digitsOf(v) {   // v > 0 -> { d: 101 significant digits of the exact value, x: decimal exponent of the first digit }
    var s = v.toExponential(100), m = /^(\d)\.(\d+)e([+-]\d+)$/.exec(s);
    return { d: m[1] + m[2], x: parseInt(m[3], 10) };
  }
  function roundDigits(d, x, n) {   // keep n significant digits, ties to even; n may be 0 or below
    if (n < 0) return { k: '', x: x };
    var kept = d.slice(0, n), rest = d.slice(n), up = false;
    if (rest.charAt(0) > '5') up = true;
    else if (rest.charAt(0) === '5') up = /[1-9]/.test(rest.slice(1)) ? true : (n > 0 && (kept.charCodeAt(n - 1) - 48) % 2 === 1);
    if (!up) return { k: kept, x: x };
    if (n === 0) return { k: '1', x: x + 1 };
    var a = kept.split(''), i = n - 1;
    while (i >= 0) { if (a[i] === '9') { a[i] = '0'; i--; } else { a[i] = String(+a[i] + 1); break; } }
    if (i < 0) return { k: '1' + a.join('').slice(0, n - 1), x: x + 1 };
    return { k: a.join(''), x: x };
  }
  function place(k, x, p) { var i = x - p; return (i >= 0 && i < k.length) ? k.charAt(i) : '0'; }
  function fixedStr(k, x, f) {
    var ip = '', fp = '', p;
    for (p = Math.max(x, 0); p >= 0; p--) ip += place(k, x, p);
    for (p = -1; p >= -f; p--) fp += place(k, x, p);
    return ip + (f > 0 ? '.' + fp : '');
  }
  function fmtFixed(v, f) {
    var neg = v < 0, a = Math.abs(v), r;
    if (a === 0) r = fixedStr('', 0, f);
    else { var g = digitsOf(a), rr = roundDigits(g.d, g.x, g.x + 1 + f); r = fixedStr(rr.k, rr.x, f); }
    return (neg ? '-' : '') + r;
  }
  function fmtG(v, P) {   // Python format(v, '.<P>g')
    if (v === 0) return '0';
    var neg = v < 0, a = Math.abs(v), g = digitsOf(a), rr = roundDigits(g.d, g.x, P), k = rr.k, x = rr.x, s;
    if (x < -4 || x >= P) {
      var m = k.charAt(0) + '.' + k.slice(1); m = m.replace(/0+$/, '').replace(/\.$/, '');
      var e = Math.abs(x); s = m + 'e' + (x < 0 ? '-' : '+') + (e < 10 ? '0' : '') + e;
    } else {
      s = fixedStr(k, x, Math.max(P - 1 - x, 0)); if (s.indexOf('.') > -1) s = s.replace(/0+$/, '').replace(/\.$/, '');
    }
    return (neg ? '-' : '') + s;
  }
  function fmt(v) { return v == null ? '' : (typeof v === 'number' ? fmtG(v, 4) : String(v)); }

  // ---- times ----
  var ISO = /^(\d{4})-(\d\d)-(\d\d)[T ](\d\d):(\d\d)(?::(\d\d)(\.\d+)?)?\s*(Z|[+-]\d\d(?::?\d\d)?)?$/i;
  function parseWhen(s) {   // -> ms since epoch (UTC), or NaN. No zone given means UTC.
    var m = ISO.exec(String(s).trim()); if (!m) return NaN;
    var t = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)), c = new Date(t);
    if (c.getUTCMonth() !== +m[2] - 1 || c.getUTCDate() !== +m[3] || +m[4] > 23 || +m[5] > 59 || +(m[6] || 0) > 59) return NaN;
    if (m[7]) t += Math.round(parseFloat(m[7]) * 1000);
    if (m[8] && m[8].toUpperCase() !== 'Z') { var o = /^([+-])(\d\d):?(\d\d)?$/.exec(m[8]); t -= (o[1] === '-' ? -1 : 1) * (+o[2] * 60 + +(o[3] || 0)) * 60000; }
    return t;
  }
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function minute(ms) { var d = new Date(ms); return d.getUTCFullYear() + '-' + p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate()) + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()); }
  function second(ms) { return minute(ms) + ':' + p2(new Date(ms).getUTCSeconds()); }

  // ---- the four checks, as in check_record of qia_check.py ----
  function checkRecord(rec, qubits) {
    var S = rec.stamp, rows = [];
    qubits.forEach(function (q) {
      var e = rec.Q[q] || {}, t1 = e.T1, t2 = e.T2;
      ['T1', 'T2'].forEach(function (f) {
        if (e[f] && e[f][1]) { var w = parseWhen(e[f][1]); if ((S - w) / 1000 > 86400) rows.push({ qubit: q, check: 'STALE', field: f, detail: 'measured ' + minute(w) + ' UTC, ' + fmtFixed((S - w) / 1000 / 3600, 1) + ' h before the stamp' }); }
      });
      ERRS.forEach(function (f) { if (e[f] && e[f][0] === 0) rows.push({ qubit: q, check: 'ZERO', field: f, detail: 'published value exactly 0' }); });
      if (t1 && t2 && t1[0] && t2[0] != null && t1[0] > 0) {
        var r = t2[0] / t1[0];
        if (r > 2.0) rows.push({ qubit: q, check: 'T2>2T1', field: 'T2/T1', detail: 'ratio ' + fmtFixed(r, 3) + ' (T1 ' + fmtG(t1[0], 4) + ', T2 ' + fmtG(t2[0], 4) + ')', outcome: r > 2.5 ? 'ABOVE' : 'CANNOT_TELL' });
        if (t1[1] && t2[1]) {
          var gap = Math.abs(parseWhen(t1[1]) - parseWhen(t2[1])) / 1000 / 3600;
          if (gap > 24) rows.push({ qubit: q, check: 'PAIR', field: 'T1/T2 dates', detail: fmtFixed(gap, 1) + ' h apart' });
        }
      }
    });
    return rows;
  }

  // ---- qubit list: "0,1,5" (also "0-5"). Empty means every qubit in the record. ----
  function parseQubits(s) {
    s = String(s || '').trim(); if (!s) return { all: true, list: [] };
    var out = [], parts = s.split(/[,\s]+/).filter(Boolean), i, m;
    for (i = 0; i < parts.length; i++) {
      if ((m = /^(\d+)$/.exec(parts[i]))) out.push(+m[1]);
      else if ((m = /^(\d+)-(\d+)$/.exec(parts[i])) && +m[2] >= +m[1] && +m[2] - +m[1] < 1000) { for (var q = +m[1]; q <= +m[2]; q++) out.push(q); }
      else return { error: 'Qubits are numbers separated by commas, for example 0,1,5, or a range such as 0-5.' };
    }
    return { all: false, list: out };
  }
  function pickQubits(spec, Q) {
    var keys = Object.keys(Q).map(Number).sort(function (a, b) { return a - b; });
    if (spec.all) return { qs: keys, miss: [] };
    return { qs: spec.list.filter(function (q) { return Q[q]; }), miss: spec.list.filter(function (q) { return !Q[q]; }) };
  }

  // ---- shard rows -> records (the same shape qia_check.load gives) ----
  function toRecord(item, dates) {
    var Q = {};
    item.q.forEach(function (row, i) {
      var e = {};
      FIELDS.forEach(function (f, j) { var v = row[2 * j], d = row[2 * j + 1]; if (d !== -2) e[f] = [v, d === -1 ? null : dates[d]]; });
      Q[i] = e;
    });
    return { stamp: parseWhen(item.s), iso: item.s, file: item.f, Q: Q };
  }

  // ---- the analysis, as in the "after" report of qia_check.py. recs: all records of the processor, oldest first. ----
  function analyze(recs, startMs, endMs, qspec) {
    var under = null, during = [];
    recs.forEach(function (r) { if (r.stamp <= startMs) under = r; else if (r.stamp <= endMs) during.push(r); });
    var out = { under: under, during: during, flags: [], changes: [], missing: [], qubits: [] };
    if (!under) return out;
    var pq = pickQubits(qspec, under.Q), qs = pq.qs; out.missing = pq.miss; out.qubits = qs;
    out.flags = checkRecord(under, qs);
    var prev = under;
    during.forEach(function (r2) {
      qs.forEach(function (q) {
        FIELDS.forEach(function (f) {
          var v1 = (prev.Q[q] || {})[f], v2 = (r2.Q[q] || {})[f];
          if (v1 || v2) {
            var a = v1 ? [v1[0], v1[1]] : [null, null], b = v2 ? [v2[0], v2[1]] : [null, null];
            if (a[0] !== b[0] || a[1] !== b[1]) out.changes.push({ record: minute(r2.stamp), stamp: r2.stamp, qubit: q, field: f, before: fmt(v1 && v1[0]), after: fmt(v2 && v2[0]), date_before: v1 ? (v1[1] || '') : '', date_after: v2 ? (v2[1] || '') : '' });
          }
        });
      });
      prev = r2;
    });
    return out;
  }

  // ---- load what a run needs: the manifest, then only the day files that hold the record in force and the records during the run ----
  function load(getJson, backend, startMs, endMs, qspec) {
    return getJson('/qia/records/' + backend + '/manifest.json').then(function (man) {
      var list = man.records.map(function (r) { return { stamp: parseWhen(r[0]), iso: r[0], file: r[1], day: r[2] }; }), need = [], under = null;
      list.forEach(function (r) { if (r.stamp <= startMs) under = r; });
      if (under) need.push(under); list.forEach(function (r) { if (r.stamp > startMs && r.stamp <= endMs) need.push(r); });
      var days = {}; need.forEach(function (r) { days[r.day] = 1; });
      return Promise.all(Object.keys(days).sort().map(function (d) { return getJson('/qia/records/' + backend + '/' + d + '.json').then(function (j) { return [d, j]; }); })).then(function (shards) {
        var byStamp = {};
        shards.forEach(function (s) { s[1].records.forEach(function (it) { byStamp[it.s] = toRecord(it, s[1].dates); }); });
        var recs = need.map(function (r) { return byStamp[r.iso]; }).filter(Boolean);
        var res = analyze(recs, startMs, endMs, qspec);
        res.manifest = { first: list.length ? list[0].iso : null, newest: list.length ? list[list.length - 1].iso : null, built: man.built, samestamp: (man.not_read_same_stamp || []).length };
        return res;
      });
    });
  }

  var api = { analyze: analyze, load: load, checkRecord: checkRecord, parseWhen: parseWhen, parseQubits: parseQubits, fmtG: fmtG, fmtFixed: fmtFixed, toRecord: toRecord, minute: minute, FIELDS: FIELDS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.QIARunCheck = api;
  if (typeof document === 'undefined') return;

  // ---- the page ----
  var box = document.getElementById('runcheck-live'); if (!box) return;
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function field(id, label, input, hint) {
    var w = el('div', 'rc-field'), l = el('label', null, label); l.setAttribute('for', id); input.id = id; w.appendChild(l); w.appendChild(input);
    if (hint) { var h = el('span', 'meta', hint); h.id = id + '-hint'; input.setAttribute('aria-describedby', h.id); w.appendChild(h); }
    return w;
  }
  function table(caption, cols, rows) {
    var t = el('table', 'mtx'), c = el('caption', null, caption), hd = el('tr'), b = el('tbody');
    t.appendChild(c); cols.forEach(function (x) { var h = el('th', null, x[0]); h.setAttribute('scope', 'col'); hd.appendChild(h); }); var th = el('thead'); th.appendChild(hd); t.appendChild(th);
    rows.forEach(function (r) { var tr = el('tr'); cols.forEach(function (x) { tr.appendChild(el('td', x[2] ? 'n' : null, r[x[1]] == null ? '' : r[x[1]])); }); b.appendChild(tr); });
    t.appendChild(b); return t;
  }
  function utcShow(s) { if (!s) return ''; var t = parseWhen(s); return isNaN(t) ? String(s) : second(t); }
  var cache = {};
  function getJson(u) { if (!cache[u]) cache[u] = fetch(u).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); }); return cache[u]; }

  var form = el('form', 'pk-ctl rc-form'); form.setAttribute('novalidate', ''); form.setAttribute('aria-label', 'Check a run');
  var sel = el('select'), st = el('input'), en = el('input'), qs = el('input'), go = el('button', 'btn ghost', 'Check this run');
  st.type = 'text'; en.type = 'text'; qs.type = 'text'; st.placeholder = '2026-11-01 12:00'; en.placeholder = '2026-11-01 12:40'; qs.placeholder = 'all, or e.g. 0,1,5'; go.type = 'submit';
  st.setAttribute('autocomplete', 'off'); en.setAttribute('autocomplete', 'off'); qs.setAttribute('autocomplete', 'off');
  form.appendChild(field('rc-proc', 'Processor', sel)); form.appendChild(field('rc-start', 'Run start, UTC', st, 'Year-month-day hour:minute'));
  form.appendChild(field('rc-end', 'Run end, UTC', en, 'Same form')); form.appendChild(field('rc-q', 'Your qubits', qs, 'Leave empty for all')); form.appendChild(go);
  var out = el('div'); out.setAttribute('aria-live', 'polite'); box.textContent = ''; box.appendChild(form); box.appendChild(out);
  var proc = {};
  getJson('/qia/records/index.json').then(function (ix) {
    ix.processors.forEach(function (p) { proc[p.backend] = p; var o = el('option', null, p.backend); o.value = p.backend; sel.appendChild(o); });
  }).catch(function () { out.textContent = 'The list of processors could not be read just now.'; });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault(); out.textContent = '';
    var s = parseWhen(st.value), e = parseWhen(en.value), q = parseQubits(qs.value);
    function say(m) { out.appendChild(el('p', 'bench-note', m)); }
    if (isNaN(s) || isNaN(e)) return say('Give the start and the end as UTC times like 2026-11-01 12:00. A time with Z or an offset, for example 2026-11-01T12:00:00-05:00, is converted to UTC.');
    if (e < s) return say('The end is earlier than the start.');
    if (q.error) return say(q.error);
    if (!sel.value) return say('Pick a processor.');
    out.appendChild(el('p', 'bench-note', 'Reading the records.'));
    load(getJson, sel.value, s, e, q).then(function (r) { render(r, sel.value, s, e, q); }).catch(function () { out.textContent = ''; say('The records could not be read just now.'); });
  });

  function render(r, b, s, e, q) {
    out.textContent = ''; var m = r.manifest;
    out.appendChild(el('h4', null, 'Run window, UTC: ' + minute(s) + ' to ' + minute(e) + ' on ' + b));
    if (!r.under) {
      out.appendChild(el('p', null, 'No record in our mirror is stamped at or before the run start, so the record in force at the start is not here. Our mirror of ' + b + ' begins at ' + utcShow(m.first) + ' UTC.'));
      return;
    }
    var age = (s - r.under.stamp) / 3600000;
    out.appendChild(el('h4', null, 'The record in force at the start'));
    out.appendChild(el('p', null, 'The latest record in our mirror stamped at or before the start was stamped ' + second(r.under.stamp) + ' UTC, ' + fmtFixed(age, 1) + ' hours before the start. File: ' + r.under.file + '. If IBM recalibrated after it and before the run, the record in force is not in our mirror.'));
    if (m.newest && Date.parse(m.newest) < e) out.appendChild(el('p', 'bench-note', 'Our newest record for ' + b + ' is stamped ' + utcShow(m.newest) + ' UTC, earlier than the end of the run, so later records may exist that are not here yet.'));
    if (r.missing.length) out.appendChild(el('p', 'bench-note', 'Not in this record, so not checked: qubits ' + r.missing.join(', ') + '.'));
    out.appendChild(el('h4', null, 'Flags in that record, for ' + (q.all ? 'every qubit' : 'your qubits')));
    if (!r.flags.length) out.appendChild(el('p', null, 'Nothing flagged.'));
    else out.appendChild(table('Flags in the record in force at the start', [['Qubit', 'qubit', 1], ['Check', 'check'], ['Figure', 'field'], ['Detail', 'detail'], ['Outcome', 'outcome']], r.flags));
    out.appendChild(el('h4', null, 'Records IBM stamped during the run'));
    if (!r.during.length) out.appendChild(el('p', null, (m.newest && Date.parse(m.newest) < e) ? 'None in our mirror so far. Our records stop before the end of the run, so a later record may still appear.' : 'None. No record in our mirror was stamped between the start and the end of the run.'));
    else {
      var ul = el('ul'); r.during.forEach(function (x) { ul.appendChild(el('li', null, second(x.stamp) + ' UTC, ' + x.file)); }); out.appendChild(ul);
      if (!r.changes.length) out.appendChild(el('p', null, 'The T1, T2 and readout-error figures on these qubits did not change in those records.'));
      else {
        out.appendChild(el('p', null, 'T1, T2 or readout-error figures on these qubits changed during the run. Each record is set against the one before it.'));
        out.appendChild(table('Figures that changed during the run', [['Record, UTC', 'record'], ['Qubit', 'qubit', 1], ['Figure', 'fl'], ['Before', 'before', 1], ['After', 'after', 1], ['Measured before, UTC', 'db'], ['Measured after, UTC', 'da']],
          r.changes.map(function (c) { return { record: c.record, qubit: c.qubit, fl: c.field + (UNIT[c.field] || ''), before: c.before, after: c.after, db: utcShow(c.date_before), da: utcShow(c.date_after) }; })));
      }
    }
    out.appendChild(el('p', 'bench-note', 'These checks read IBM’s published figures only and make no claim about your results. Compare your results against the record in force.'));
  }
})(typeof window !== 'undefined' ? window : globalThis);
