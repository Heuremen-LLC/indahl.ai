// NOW: everything moving on indahl.ai, from the live feeds, refreshed every few seconds. The app opens here.
(function () {
  var root = document.getElementById('now'); if (!root) return;
  var NS = 'http://www.w3.org/2000/svg', ACT = null, PROG = {}, YO = null, YOR = null, Q = null, LISTS = [], CLOCK = null;
  function h(tag, txt, cls) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function fmt(n) { return Number(n).toLocaleString('en-US'); }
  function dur(ms) { var s = Math.max(0, Math.floor(ms / 1000)), hh = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
    return ((hh ? hh + ' h ' : '') + (hh || m ? m + ' min ' : '') + (hh ? '' : x + ' s')).trim(); }
  function bar(frac, cls) { var b = h('span', null, 'nw-bar ' + (cls || '')), f = h('span', null, 'nw-fill'); f.style.width = Math.max(0, Math.min(100, 100 * frac)).toFixed(1) + '%'; b.appendChild(f); return b; }
  function J(u) { return fetch(u, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); }
  function sec(title) { var s = h('section', null, 'nw-sec'); s.appendChild(h('h2', title)); return s; }
  function row(link, label, text, b, cls) { var r = h('div', null, 'nw-row ' + (cls || '')), a = h('a', label); a.href = link; r.appendChild(a); r.appendChild(h('span', text, 'nw-txt')); if (b) r.appendChild(b); return r; }
  function paint() {
    root.textContent = ''; var now = Date.now();
    var top = h('p', 'Now: ' + new Date(now).toUTCString().replace('GMT', 'UTC') + '. Every line below is read from a live feed and moves on its own.', 'nw-clock'); root.appendChild(top);
    var live = (ACT && ACT.live) || {}, read = (ACT && ACT.read) || {}, every = (ACT && ACT.every_min) || {};
    var reading = Object.keys(live).filter(function (k) { return live[k] === 'reading' || live[k] === 'just read' || (PROG[k] && PROG[k].running && now - Date.parse(PROG[k].t) < 180000); });
    var s1 = sec('Reading now');
    if (!reading.length) s1.appendChild(h('p', 'No desk is mid-read this minute. The next scheduled reads are below.', 'nw-txt'));
    reading.forEach(function (k) {
      var p = PROG[k], run = p && p.running && now - Date.parse(p.t) < 180000;
      s1.appendChild(row('/' + k, k.toUpperCase(), run ? (p.label ? p.label + ': ' : '') + fmt(p.done) + ' of ' + fmt(p.total) + (p.what ? ', ' + p.what : '') : (live[k] === 'reading' ? 'reading now' : 'read in the last few minutes'), bar(run ? p.done / p.total : 1, run ? 'nw-run' : 'nw-ind')));
    });
    root.appendChild(s1);
    if (YO && YO.state) {
      var st = YO.state === 'training', s2 = sec(st ? 'Training now' : 'Training');   // 9 Nov 2026 (site pass L17): 'now' only while a run is going
      var t = YO.state === 'done' ? 'YO finished training. Its test reading is on the lab page.' : YO.state === 'trained' ? 'YO finished training. Its test reading is being checked.' : st ? 'YO, step ' + fmt(YO.step) + ' of ' + fmt(YO.steps) + (YO.train && YO.train.length ? ', training loss ' + YO.train[YO.train.length - 1][1].toFixed(3) : '') : 'YO is getting ready to train.';
      s2.appendChild(row('/iris/lab', 'YO', t, bar((YO.step || 0) / (YO.steps || 1), st ? 'nw-run' : ''))); root.appendChild(s2);
    }
    if (YOR && YOR.n) {
      var s3 = sec('YO reads IBM records'); (YOR.latest || []).slice(0, 3).forEach(function (r) { s3.appendChild(row('/qia#yo', r.backend, r.stamp + ', agreement with the code ' + r.score.toFixed(2))); }); root.appendChild(s3);
    }
    if (CLOCK && CLOCK.rows) {
      // 9 Nov 2026 (site pass M16): the block says which fire it shows. The feed is rewritten after each fire by clock_feed.py (newest fire per chip)
      var s4 = sec('Darkwave clock' + (CLOCK.fire ? ', fire of ' + CLOCK.fire : '')); CLOCK.rows.slice(-2).forEach(function (r) { s4.appendChild(row('/darkwave', r.chip, r.text)); });
      if (CLOCK.note) s4.appendChild(h('p', CLOCK.note, 'nw-note')); root.appendChild(s4);
    }
    var pr = Q && Q.processors; if (typeof pr === 'string') { try { pr = JSON.parse(pr.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false')); } catch (e) { pr = null; } }
    if (pr && pr.length) {
      var s5 = sec('IBM processors'); pr.forEach(function (p) { s5.appendChild(row('/qia', p.backend, (p.pending == null ? 'queue not read' : fmt(p.pending) + (+p.pending === 1 ? ' job waiting' : ' jobs waiting')))); });
      if (Q.updated) s5.appendChild(h('p', 'Read ' + Q.updated + '.', 'nw-note')); root.appendChild(s5);
    }
    if (LISTS.length) {
      var s6 = sec('Newest on the Lists'); LISTS.slice(0, 5).forEach(function (x) { s6.appendChild(row(x.href, x.div, x.indexed + ', ' + x.study)); }); root.appendChild(s6);
    }
    var s7 = sec('Every desk'), ks = Object.keys(read).sort(function (a, b) { return Date.parse(read[b]) - Date.parse(read[a]); });
    ks.forEach(function (k) { var r = row('/' + k, k.toUpperCase(), '', bar(0, 'nw-wait')); r.setAttribute('data-read', read[k]); r.setAttribute('data-cyc', (every[k] || 0) * 60000); s7.appendChild(r); });
    root.appendChild(s7); tick();
  }
  function tick() {   // clocks and bars move every second without rebuilding the page, so links stay clickable
    var now = Date.now(), c = root.querySelector('.nw-clock'); if (c) c.firstChild.nodeValue = 'Now: ' + new Date(now).toUTCString().replace('GMT', 'UTC') + '. Every line below is read from a live feed and moves on its own.';
    root.querySelectorAll('[data-read]').forEach(function (r) { var el = now - Date.parse(r.getAttribute('data-read')), cyc = +r.getAttribute('data-cyc');
      r.querySelector('.nw-txt').textContent = 'read ' + dur(el) + ' ago' + (cyc ? (el < cyc ? ', next in about ' + dur(cyc - el).replace(/ \d+ s$/, '') : ', next read due') : '');
      r.querySelector('.nw-fill').style.width = (cyc ? Math.min(100, 100 * el / cyc) : 0).toFixed(2) + '%'; });
  }
  function loadAct() { J('/activity.json').then(function (d) { ACT = d; var ks = Object.keys((d && d.live) || {});
    Promise.all(ks.map(function (k) { return J('/progress/' + k + '.json').then(function (p) { if (p && p.desk) PROG[k] = p; }); })).then(paint); }); }
  function loadSlow() {
    J('/iris/yo.json').then(function (d) { YO = d; }); J('/qia/yo.json').then(function (d) { YOR = d; }); J('/qia/queue.json').then(function (d) { Q = d; });
    J('/darkwave/clock.json').then(function (d) { CLOCK = d; });
    Promise.all([J('/qia/list.json'), J('/iris/list.json')]).then(function (ls) {
      var out = []; [['QIA', ls[0], '/qia/list#'], ['IRIS', ls[1], '/iris/list']].forEach(function (L) { ((L[1] && L[1].studies) || []).forEach(function (s) { out.push({ div: L[0], study: s.study, indexed: s.indexed || '', href: L[0] === 'QIA' && s.anchor ? L[2] + s.anchor : (L[0] === 'QIA' ? '/qia/list' : L[2]) }); }); });
      out.sort(function (a, b) { return a.indexed < b.indexed ? 1 : a.indexed > b.indexed ? -1 : 0; }); LISTS = out; paint(); });
  }
  loadAct(); loadSlow(); setInterval(loadAct, 15000); setInterval(loadSlow, 60000); setInterval(tick, 1000);
})();
