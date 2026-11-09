// Sage V training, live (9 Nov 2026). Reads /iris/lab/live.json, which sage_v/live_export.py writes on the tick:
// stages, seat names, timestamps and numbers only. Refreshes every 30 s.
(function () {
  var box = document.getElementById('sagev-live'); if (!box) return;
  var LABEL = {
    grounded: 'Claims whose quote is in the passage cited (share)',
    accuracy: 'Claims grounded and judged right (share)',
    confident_wrong: 'Claims stated at 0.8 or more and not right (share)',
    fabricated: 'Claims whose quote is in no passage shown (share)',
    answered: 'Prompts answered with at least one claim (share)',
    right_per_prompt: 'Right claims per prompt',
    cw_per_prompt: 'Confident and wrong claims per prompt',
    net_per_prompt: 'Right minus confident and wrong, per prompt'
  };
  function h(tag, txt, cls) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function f3(x) { return x == null ? '-' : (x > 0 ? '+' : '') + x.toFixed(3); }
  function p3(x) { return x == null ? '-' : x.toFixed(3); }
  function utc(iso) { return iso ? iso.replace('T', ' ').replace(/:\d\dZ$/, ' UTC') : '-'; }
  function ago(iso) {
    if (!iso) return ''; var m = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    if (m < 1) return 'just now'; if (m < 60) return m + ' min ago'; var hh = Math.floor(m / 60); return hh + ' h ' + (m % 60) + ' min ago';
  }
  function table(head, rows) {
    var t = h('table', null, 'hl-tab'), th = h('thead'), tr = h('tr'); head.forEach(function (c) { tr.appendChild(h('th', c)); }); th.appendChild(tr); t.appendChild(th);
    var tb = h('tbody'); rows.forEach(function (r) { var x = h('tr'); r.forEach(function (c) { x.appendChild(h('td', c)); }); tb.appendChild(x); }); t.appendChild(tb);
    var w = h('div', null, 'tablewrap'); w.appendChild(t); return w;
  }
  function stageText(s) {
    if (s.stage && s.stage !== 'idle') return s.stage + (s.heartbeat ? ' (heartbeat ' + ago(s.heartbeat) + ')' : '');
    return 'not training now';
  }
  function draw(d) {
    box.textContent = '';
    if (!d || !d.seats) { box.appendChild(h('p', 'The live feed has not been written yet.')); return; }
    var top = h('p', null, 'meta');
    top.textContent = (d.cycle != null ? 'Council cycle ' + Number(d.cycle).toLocaleString('en-US') + '. ' : '') + 'Feed written ' + utc(d.updated) + ' (' + ago(d.updated) + '). This page reads it again every 30 seconds.';
    box.appendChild(top);
    box.appendChild(h('h3', 'Each seat now'));
    box.appendChild(table(['Seat', 'Stage now', 'Status', 'Serving the current adapter since'],
      d.seats.map(function (s) { return [s.seat, stageText(s), s.status, s.serving_since ? utc(s.serving_since) : '-']; })));
    box.appendChild(h('p', 'Stages run in order: harvest (new training rows), SFT (supervised training), DPO (preference training), then the paired eval. Released means the paired eval ruled out harm. Serving, not released means the adapter answers in the council but has not passed that test.', 'meta'));
    box.appendChild(h('h3', 'Recent paired evals'));
    if (!(d.paired || []).length) box.appendChild(h('p', 'No paired eval in the feed yet.'));
    (d.paired || []).slice(0, 6).forEach(function (r) {
      box.appendChild(h('p', r.seat + ', read ' + utc(r.ts) + '. ' + (r.n != null ? r.n + ' held-out prompts, base model and adapter on the same prompts.' : ''), 'sv-ph'));
      var rows = (d.metric_order || Object.keys(LABEL)).filter(function (k) { return r[k]; }).map(function (k) { var v = r[k]; return [LABEL[k] || k, p3(v[0]), p3(v[1]), f3(v[2]) + ' to ' + f3(v[3])]; });
      box.appendChild(table(['Reading', 'Base', 'Adapter', 'Adapter minus base, 95% interval'], rows));
    });
    box.appendChild(h('p', 'Intervals are 95% paired bootstrap intervals over prompts. A second model judges whether a grounded claim is right, and code checks every quote.', 'meta'));
    box.appendChild(h('h3', 'Recent events'));
    box.appendChild(table(['Time', 'Seat', 'Event'], (d.events || []).slice(0, 25).map(function (e) {
      return [utc(e.ts), e.seat, e.event + (e.training_rows != null ? ' (' + Number(e.training_rows).toLocaleString('en-US') + ' training rows)' : '')];
    })));
  }
  function load() { fetch('/iris/lab/live.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () { box.textContent = 'The live feed could not be read just now.'; }); }
  load(); setInterval(load, 30000);
})();
