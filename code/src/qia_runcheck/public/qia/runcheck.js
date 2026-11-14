// QIA "Check a run": which published IBM calibration record was in force at the start of a run, what IBM stamped during it, the flags in that
// record for your qubits, and what changed between records. It reads only our static files under /qia/records/. Nothing you type leaves the page.
// The checks and the wording follow qia_check.py of the QIA Research Package (https://indahl.ai/qia). Every time shown is UTC.
(function (root) {
  'use strict';
  var FIELDS = ['T1', 'T2', 'readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1', 'init_error'], ERRS = FIELDS.slice(2, 5), TIMES = ['T1', 'T2'];
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
    if (v !== v) return 'nan';
    if (v === Infinity) return 'inf';
    if (v === -Infinity) return '-inf';
    if (v === 0) return Object.is(v, -0) ? '-0' : '0';
    var neg = v < 0, a = Math.abs(v), g = digitsOf(a), rr = roundDigits(g.d, g.x, P), k = rr.k, x = rr.x, s;
    if (x < -4 || x >= P) {
      var m = k.charAt(0) + '.' + k.slice(1); m = m.replace(/0+$/, '').replace(/\.$/, '');
      var e = Math.abs(x); s = m + 'e' + (x < 0 ? '-' : '+') + (e < 10 ? '0' : '') + e;
    } else {
      s = fixedStr(k, x, Math.max(P - 1 - x, 0)); if (s.indexOf('.') > -1) s = s.replace(/0+$/, '').replace(/\.$/, '');
    }
    return (neg ? '-' : '') + s;
  }
  // ---- Python value model: the shards carry ints, floats, strings, null, bool, and {r, t} for what JSON would blur (0.0, nan, huge ints) ----
  function toVal(c) {
    if (c && typeof c === 'object') { var x = NaN; if (c.t === 'f') x = c.r === 'nan' ? NaN : c.r === 'inf' ? Infinity : c.r === '-inf' ? -Infinity : Number(c.r); else if (c.t === 'i') x = Number(c.r); return { pv: 1, t: c.t, r: c.r, x: x }; }
    return c;
  }
  function pyFloatRepr(x) {   // Python repr(float)
    if (x !== x) return 'nan'; if (x === Infinity) return 'inf'; if (x === -Infinity) return '-inf';
    if (x === 0) return Object.is(x, -0) ? '-0.0' : '0.0';
    var m = /^(-?)(\d)(?:\.(\d+))?e([+-]\d+)$/.exec(x.toExponential()), dg = m[2] + (m[3] || ''), ex = parseInt(m[4], 10), r;
    if (ex >= -4 && ex < 16) {
      if (ex >= 0) { while (dg.length < ex + 1) dg += '0'; r = dg.slice(0, ex + 1) + '.' + (dg.slice(ex + 1) || '0'); }
      else r = '0.' + new Array(-ex).join('0') + dg;
    } else { var a = Math.abs(ex); r = dg.charAt(0) + (dg.length > 1 ? '.' + dg.slice(1) : '') + 'e' + (ex < 0 ? '-' : '+') + (a < 10 ? '0' : '') + a; }
    return m[1] + r;
  }
  function pyStrRepr(t) {
    var q = (t.indexOf("'") > -1 && t.indexOf('"') < 0) ? '"' : "'", o = q;
    for (var i = 0; i < t.length; i++) {
      var c = t.charAt(i), n = t.charCodeAt(i);
      if (c === '\\') o += '\\\\'; else if (c === q) o += '\\' + q; else if (c === '\n') o += '\\n'; else if (c === '\r') o += '\\r'; else if (c === '\t') o += '\\t';
      else if (n < 32 || (n >= 127 && n < 161)) o += '\\x' + (n < 16 ? '0' : '') + n.toString(16); else o += c;
    }
    return o + q;
  }
  function pyRepr(v) {
    if (v == null) return 'None'; if (v === true) return 'True'; if (v === false) return 'False';
    if (typeof v === 'string') return pyStrRepr(v);
    if (typeof v === 'number') return Number.isInteger(v) ? String(v) : pyFloatRepr(v);
    return v.r;
  }
  var FLOATRE = /^[+-]?(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[eE][+-]?\d+(?:_\d+)*)?$/;
  function num(v) {   // as num() of qia_check.py: float or null
    var x;
    if (v == null || typeof v === 'boolean') return null;
    if (typeof v === 'number') x = v;
    else if (typeof v === 'string') { var t = v.trim(); if (!FLOATRE.test(t)) return null; x = Number(t.replace(/_/g, '')); }
    else if (v.pv) x = v.t === 'o' ? NaN : v.x; else return null;
    return (x !== x || x === Infinity || x === -Infinity) ? null : x;
  }
  function fmt(v) {   // fmt() of qia_check.py
    if (v == null) return '';
    if (typeof v === 'number') return fmtG(v, 4);
    if (typeof v === 'boolean') return v ? 'True' : 'False';
    if (typeof v === 'string') return v;
    return v.t === 'o' ? v.r : fmtG(v.x, 4);
  }

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
  var QW = /^(\d{4})-?(\d\d)-?(\d\d)(?:(.)(\d\d)(?::?(\d\d)(?::?(\d\d)(?:[.,](\d+))?)?)?(?:([+-])(\d\d)(?::?(\d\d)(?::?(\d\d)(?:\.(\d+))?)?)?)?)?$/;
  function qWhen(s) {   // when() of qia_check.py: { us, naive } with us = microseconds since the epoch (UTC), or null when it raises
    var t = String(s).trim().replace(/Z/g, '+00:00'), leap = false, lm = /^(.*T\d\d:\d\d:)60(\.\d+)?(.*)$/.exec(t);
    if (lm) { t = lm[1] + '59' + (lm[2] || '') + lm[3]; leap = true; }
    var m = QW.exec(t); if (!m) return null;
    var y = +m[1], mo = +m[2], da = +m[3], h = +(m[5] || 0), mi = +(m[6] || 0), se = +(m[7] || 0), us = m[8] ? +((m[8] + '000000').slice(0, 6)) : 0;
    if (y < 1 || mo < 1 || mo > 12 || h > 23 || mi > 59 || se > 59) return null;
    var c = new Date(0); c.setUTCFullYear(y, mo - 1, da); if (c.getUTCMonth() !== mo - 1 || c.getUTCDate() !== da) return null;
    c.setUTCHours(h, mi, se, 0);
    var naive = !m[9], off = 0;
    if (m[9]) { var oh = +m[10], om = +(m[11] || 0), os = +(m[12] || 0); if (oh > 23 || om > 59 || os > 59) return null; off = (oh * 3600 + om * 60 + os) * (m[9] === '-' ? -1 : 1); }
    return { us: (c.getTime() / 1000 - off + (leap ? 1 : 0)) * 1e6 + us, naive: naive };
  }
  function minuteUs(us) { return minute(Math.floor(us / 1000)); }
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function minute(ms) { var d = new Date(ms); return d.getUTCFullYear() + '-' + p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate()) + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()); }
  function second(ms) { return minute(ms) + ':' + p2(new Date(ms).getUTCSeconds()); }

  // ---- the checks, as in check_record of qia_check.py (rules R01 to R12) ----
  var UNIT_US = { '': 1.0, 'us': 1.0, '\u00b5s': 1.0, '\u03bcs': 1.0, 'ns': 1e-3, 'ms': 1e3, 's': 1e6 }, DAY = 86400.0, TOL = 1e-9;
  function hasUnit(u) { return Object.prototype.hasOwnProperty.call(UNIT_US, u); }
  function strT(t) { return t == null ? 'None' : String(t); }
  // refMs: the run time (ms), or null. refName: how the detail names it.
  function checkRecord(rec, qubits, refMs, refName) {
    var S = rec.stamp * 1000, ref = refMs == null ? null : refMs * 1000, rows = [], rn = refName || 'the run';
    qubits.forEach(function (q) {
      function U(f, why) { rows.push({ qubit: q, check: 'UNKNOWN', field: f, detail: why, outcome: 'UNKNOWN' }); }
      var e = rec.Q[q] || {}, keys = Object.keys(e), val = {}, date = {}, dord = [];
      if (!keys.length) { U('(all)', 'no figures: no T1, T2 or error figure for this qubit in the record'); return; }
      TIMES.forEach(function (f) { if (!(f in e)) U(f, 'absent from the record'); });
      keys.forEach(function (f) {
        var entries = e[f], seen = {}, nd = 0;
        entries.forEach(function (x) { var n = num(x.v), k = (n != null ? pyFloatRepr(n) : pyRepr(x.v)) + '\u0000' + strT(x.t) + '\u0000' + String(x.u || ''); if (!seen[k]) { seen[k] = 1; nd++; } });
        if (nd > 1) { U(f, entries.length + ' conflicting entries in one record; none used'); return; }
        var v = entries[0].v, t = entries[0].t, u = entries[0].u;
        if (t != null && t !== '') {
          var w = qWhen(t);
          if (!w) U(f, 'date ' + pyRepr(t) + ' cannot be read');
          else if (w.naive) U(f, 'date ' + t + ' has no zone, so its age cannot be known; not read');
          else { date[f] = w.us; dord.push(f); }
        } else U(f, 'no measurement date, so its age cannot be checked');
        var x = num(v);
        if (TIMES.indexOf(f) > -1) {
          if (u == null) return U(f, 'no unit given');
          if (!hasUnit(u)) return U(f, 'unknown unit ' + pyRepr(u));
          if (x == null || x <= 0) return U(f, 'value ' + pyRepr(v) + ' is not a usable time');
          val[f] = x * UNIT_US[u];
        } else {
          if (!(u === '' || u == null || u === '%')) return U(f, 'unknown unit ' + pyRepr(u) + ' for an error rate');
          if (x == null) return U(f, 'value ' + pyRepr(v) + ' cannot be read');
          if (u === '%') x = x / 100;
          if (x < 0) return U(f, 'value ' + pyRepr(v) + ' is negative, not a usable error rate');
          val[f] = x;
        }
      });
      dord.forEach(function (f) {
        var d = date[f], as = (S - d) / 1e6, ar = ref != null ? (ref - d) / 1e6 : null;
        if (as > DAY || (ar != null && ar > DAY)) rows.push({ qubit: q, check: 'STALE', field: f, detail: 'measured ' + minuteUs(d) + ' UTC: ' + fmtFixed(as / 3600, 1) + ' h before the stamp' + (ar != null ? ', ' + fmtFixed(ar / 3600, 1) + ' h before ' + rn : '') });
      });
      ERRS.concat(['init_error']).forEach(function (f) {
        if (f in val && val[f] === 0) rows.push({ qubit: q, check: 'ZERO', field: f, detail: 'published value 0' });
        else if (f in val && val[f] !== 0 && Math.abs(val[f]) < 1e-6) rows.push({ qubit: q, check: 'TINY', field: f, detail: 'published value ' + pyFloatRepr(val[f]) + ': below 1e-6, which no count of up to 1,000,000 shots can give' });
      });
      dord.forEach(function (f) {
        var d = date[f]; if ((d - S) / 1e6 > 0) rows.push({ qubit: q, check: 'FUTURE', field: f, detail: 'measured ' + minuteUs(d) + ' UTC, ' + fmtFixed((d - S) / 1e6 / 3600, 1) + ' h AFTER the record stamp' });
      });
      if ('T1' in val && 'T2' in val) {
        var r = val.T2 / val.T1;
        if (r > 2.0 * (1 + TOL)) rows.push({ qubit: q, check: 'T2>2T1', field: 'T2/T1', detail: 'ratio ' + fmtFixed(r, 3) + ' (T1 ' + fmtG(val.T1, 4) + ' us, T2 ' + fmtG(val.T2, 4) + ' us)', outcome: r > 2.5 * (1 + TOL) ? 'ABOVE' : 'CANNOT_TELL' });
      }
      if ('T1' in date && 'T2' in date) {
        var gap = Math.abs(date.T1 - date.T2) / 1e6 / 3600;
        if (gap > 24) rows.push({ qubit: q, check: 'PAIR', field: 'T1/T2 dates', detail: fmtFixed(gap, 1) + ' h apart' });
      }
    });
    var real = rows.filter(function (r) { return r.check !== 'UNKNOWN'; }), unk = rows.filter(function (r) { return r.check === 'UNKNOWN'; });
    rows = real.concat(unk);   // real flags above UNKNOWN rows, as the package sorts them
    rows.forEach(function (r) { r.category = (r.check === 'T2>2T1' || r.check === 'PAIR' || r.field === 'T1' || r.field === 'T2') ? 'T1 and T2' : 'Error figures'; });
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

  // ---- shard rows -> records (the same shape qia_check.load gives: every entry of every field, in the record's own order) ----
  function toRecord(item, shard) {
    var Q = {}, dates = shard.dates, units = shard.units || [], orders = shard.orders;
    function ent(v, d, u) { return { v: toVal(v), t: d === -1 ? null : dates[d], u: u === -1 ? null : units[u] }; }
    item.q.forEach(function (row, i) {
      var order = orders[row[0]], e = {}, p = 1, k, f;
      for (k = 0; k < order.length; k++) { f = FIELDS[+order.charAt(k)]; e[f] = [ent(row[p], row[p + 1], row[p + 2])]; p += 3; }
      if (row.length > p) row[p].forEach(function (x) { e[FIELDS[x[0]]].push(ent(x[1], x[2], x[3])); });
      Q[i] = e;
    });
    return { stamp: parseWhen(item.s), iso: item.s, file: item.f, Q: Q };
  }

  // ---- the analysis, as in the "after" report of qia_check.py. recs: all records of the processor, oldest first (stamp, then file name). ----
  function figsKey(rec) {   // a record's figures, independent of file bytes: two records conflict only if these differ
    return Object.keys(rec.Q).map(Number).sort(function (a, b) { return a - b; }).map(function (q) {
      var e = rec.Q[q]; return q + ':' + Object.keys(e).sort().map(function (f) { return f + '=' + e[f].map(function (x) { var n = num(x.v); return (n != null ? 'n' + pyFloatRepr(n) : 'r' + pyRepr(x.v)) + '|' + strT(x.t) + '|' + String(x.u || ''); }).join(','); }).join(';');
    }).join('\n');
  }
  function analyze(recs, startMs, endMs, qspec) {
    var last = null, during = [];
    recs.forEach(function (r) { if (r.stamp <= startMs) { if (last == null || r.stamp > last) last = r.stamp; } else if (r.stamp <= endMs) during.push(r); });
    var inForce = last == null ? [] : recs.filter(function (r) { return r.stamp === last; });
    var under = inForce[0] || null, out = { under: under, inForce: inForce, conflict: false, during: during, flags: [], changes: [], missing: [], qubits: [] };
    if (!under) return out;
    var pq = pickQubits(qspec, under.Q), qs = pq.qs; out.missing = pq.miss; out.qubits = qs;
    out.flags = checkRecord(under, qs, startMs, 'the run time');
    function key(x) { return x ? [num(x.v) != null ? num(x.v) : pyRepr(x.v), strT(x.t), String(x.u || '')] : null; }
    function same(a, b) { return (!a && !b) || (a && b && a[0] === b[0] && a[1] === b[1] && a[2] === b[2]); }
    function cat(f) { return f === 'T1' || f === 'T2' ? 'T1 and T2' : 'Error figures'; }
    function withUnit(x) { return fmt(x && x.v) + (x && x.u ? ' ' + x.u : ''); }
    function first(Q, q, f) { return ((Q[q] || {})[f] || [])[0]; }
    function diff(Qa, Qb, label, stamp) {
      qs.forEach(function (q) {
        FIELDS.forEach(function (f) {
          var v1 = first(Qa, q, f), v2 = first(Qb, q, f);
          if (!(v1 || v2) || same(key(v1), key(v2))) return;
          var n1 = v1 && num(v1.v), n2 = v2 && num(v2.v);
          var known = !!(v1 && v2) && TIMES.indexOf(f) > -1 && hasUnit(v1.u || '') && hasUnit(v2.u || '') && n1 != null && n2 != null;
          var a = known ? n1 * UNIT_US[v1.u || ''] : 0, b = known ? n2 * UNIT_US[v2.u || ''] : 0;
          var unitOnly = known && strT(v1.t) === strT(v2.t) && (v1.u || '') !== (v2.u || '') && Math.abs(a - b) <= 1e-9 * Math.max(Math.abs(a), Math.abs(b));
          out.changes.push({ record: label + (unitOnly ? ' (unit only, same value)' : ''), stamp: stamp, qubit: q, field: f, before: withUnit(v1), after: withUnit(v2),
            date_before: v1 ? v1.t : '', date_after: v2 ? v2.t : '', category: cat(f) });
        });
      });
    }
    var conflict = inForce.length > 1 && inForce.map(figsKey).filter(function (k, i, a) { return a.indexOf(k) === i; }).length > 1;
    out.conflict = conflict;
    if (conflict) inForce.slice(1).forEach(function (rb, i) {   // same-stamp records at the start, compared with each other
      var ra = inForce[i];
      qs.forEach(function (q) {
        FIELDS.forEach(function (f) {
          var v1 = first(ra.Q, q, f), v2 = first(rb.Q, q, f);
          if ((v1 || v2) && !same(key(v1), key(v2))) out.changes.push({ record: 'CONFLICT ' + ra.file + ' vs ' + rb.file, stamp: rb.stamp, qubit: q, field: f, before: withUnit(v1), after: withUnit(v2), date_before: v1 ? v1.t : '', date_after: v2 ? v2.t : '', category: cat(f) });
        });
      });
    });
    if (during.length) {
      (conflict ? inForce : [under]).forEach(function (br) { diff(br.Q, during[0].Q, minute(during[0].stamp) + (conflict ? ' (from ' + br.file + ')' : ''), during[0].stamp); });
      during.slice(1).forEach(function (r2, i) { diff(during[i].Q, r2.Q, minute(r2.stamp) + ' (from ' + during[i].file + ')', r2.stamp); });
    }
    return out;
  }

  // ---- load what a run needs: the manifest, then only the day files that hold the record in force and the records during the run ----
  function load(getJson, backend, startMs, endMs, qspec) {
    return getJson('/qia/records/' + backend + '/manifest.json').then(function (man) {
      var list = man.records.map(function (r) { return { stamp: parseWhen(r[0]), iso: r[0], file: r[1], day: r[2] }; }), need = [], under = null;
      list.forEach(function (r) { if (r.stamp <= startMs && (under == null || r.stamp > under)) under = r.stamp; });
      list.forEach(function (r) { if ((under != null && r.stamp === under) || (r.stamp > startMs && r.stamp <= endMs)) need.push(r); });
      var days = {}; need.forEach(function (r) { days[r.day] = 1; });
      return Promise.all(Object.keys(days).sort().map(function (d) { return getJson('/qia/records/' + backend + '/' + d + '.json').then(function (j) { return [d, j]; }); })).then(function (shards) {
        var byFile = {};
        shards.forEach(function (s) { s[1].records.forEach(function (it) { byFile[it.f] = toRecord(it, s[1]); }); });
        var recs = need.map(function (r) { return byFile[r.file]; }).filter(Boolean);
        var res = analyze(recs, startMs, endMs, qspec);
        res.manifest = { first: list.length ? list[0].iso : null, newest: list.length ? list[list.length - 1].iso : null, built: man.built };
        return res;
      });
    });
  }

  var api = { qWhen: qWhen, num: num, pyFloatRepr: pyFloatRepr, analyze: analyze, load: load, checkRecord: checkRecord, parseWhen: parseWhen, parseQubits: parseQubits, fmtG: fmtG, fmtFixed: fmtFixed, toRecord: toRecord, minute: minute, FIELDS: FIELDS };
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
    out.appendChild(el('p', 'bench-note', 'What this page checks: the record in force at the start, for the qubits in that record. Records stamped during the run are listed and their changes shown, but their own flags are not checked here. The qia-check package checks each of them (qia-check after).'));   // 13 Nov 2026, Sage: the limit sits beside the result
    out.appendChild(el('h4', null, 'The record in force at the start'));
    out.appendChild(el('p', null, 'The latest record in our mirror stamped at or before the start was stamped ' + second(r.under.stamp) + ' UTC, ' + fmtFixed(age, 1) + ' hours before the start. File: ' + r.under.file + '. If IBM recalibrated after it and before the run, the record in force is not in our mirror.'));
    if (r.inForce.length > 1) out.appendChild(el('p', 'bench-note', 'Our mirror holds ' + r.inForce.length + ' files with that stamp. ' + (r.conflict ? 'Their figures differ, so which one was in force is not known. The flags below are for the first file.' : 'Their figures are the same.')));
    if (m.newest && Date.parse(m.newest) < e) out.appendChild(el('p', 'bench-note', 'Our newest record for ' + b + ' is stamped ' + utcShow(m.newest) + ' UTC, earlier than the end of the run, so later records may exist that are not here yet.'));
    if (r.missing.length) out.appendChild(el('p', 'bench-note', 'Not in this record, so not checked: qubits ' + r.missing.join(', ') + '.'));
    out.appendChild(el('h4', null, 'Flags in that record, for ' + (q.all ? 'every qubit' : 'your qubits')));
    if (!r.flags.length) out.appendChild(el('p', null, 'Nothing flagged in the figures this check reads.'));
    else {
      var nu = r.flags.filter(function (x) { return x.check === 'UNKNOWN'; }).length;
      if (nu) out.appendChild(el('p', 'bench-note', nu + ' UNKNOWN row' + (nu === 1 ? '' : 's') + ': something could not be read. UNKNOWN is not a pass.'));
      out.appendChild(table('Flags in the record in force at the start', [['Qubit', 'qubit', 1], ['Check', 'check'], ['Figure', 'field'], ['Detail', 'detail'], ['Outcome', 'outcome']],
        r.flags.map(function (x) { return { qubit: x.qubit, check: x.check, field: x.field, detail: String(x.detail).replace(/; /g, ', '), outcome: x.outcome }; })));
    }
    out.appendChild(el('h4', null, 'Records IBM stamped during the run'));
    if (!r.during.length) out.appendChild(el('p', null, (m.newest && Date.parse(m.newest) < e) ? 'None in our mirror so far. Our records stop before the end of the run, so a later record may still appear.' : 'None. No record in our mirror was stamped between the start and the end of the run.'));
    else {
      var ul = el('ul'); r.during.forEach(function (x) { ul.appendChild(el('li', null, second(x.stamp) + ' UTC, ' + x.file)); }); out.appendChild(ul);
      if (!r.changes.length) out.appendChild(el('p', null, 'The T1, T2 and error figures on these qubits did not change in those records.'));
      else {
        out.appendChild(el('p', null, 'T1, T2 or error figures on these qubits changed during the run. Each record is set against the one before it.'));
        out.appendChild(table('Figures that changed during the run', [['Record, UTC', 'record'], ['Qubit', 'qubit', 1], ['Figure', 'fl'], ['Before', 'before', 1], ['After', 'after', 1], ['Measured before, UTC', 'db'], ['Measured after, UTC', 'da']],
          r.changes.map(function (c) { return { record: c.record, qubit: c.qubit, fl: c.field + (UNIT[c.field] || ''), before: c.before, after: c.after, db: utcShow(c.date_before), da: utcShow(c.date_after) }; })));
      }
    }
    out.appendChild(el('p', 'bench-note', 'These checks read IBM’s published figures only and make no claim about your results. Compare your results against the record in force.'));
  }
})(typeof window !== 'undefined' ? window : globalThis);
