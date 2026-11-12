// STAN training, live (12 Nov 2026). Reads /iris/lab/stan.json, which stan/scripts/live_status.py writes (numbers and fixed words only).
// Refreshes every 60 s.
(function () {
  var box = document.getElementById('stan-live'); if (!box) return;
  var STAGES = ['teachers', 'crosstalk', 'silver', 'training', 'paired test'];
  var STAGE_TEXT = {
    'teachers': 'Three teacher models are labelling claims, each on its own.',
    'crosstalk': 'The teachers are labelling again after seeing each other’s labels.',
    'silver': 'Agreements between the teachers are being turned into training examples.',
    'training': 'STAN is training.',
    'paired test': 'STAN is trained and is being tested on the answer key.',
    'kept': 'The paired test is read. STAN was kept.',
    'not kept': 'The paired test is read. STAN was not kept.'
  };
  var NAMES = { base: 'Untrained base (Qwen3-1.7B)', llama: 'Llama 3.1 8B', mistral: 'Mistral 7B', gemma: 'Gemma 3 4B' };
  function h(tag, txt, cls) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function pct(x) { return x == null ? '-' : Math.round(x * 100) + '%'; }
  function p3(x) { return x == null ? '-' : x.toFixed(3); }
  function iv(w) { return w && w.length === 2 ? '[' + p3(w[0]) + ', ' + p3(w[1]) + ']' : '-'; }
  function nm(k) { return NAMES[k] || k; }
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
  var DESK = { sagar: 'SAGAR, gravitational-wave papers', brands: 'BRANDS, papers by authors at named companies', quant: 'Quant desk' };
  var MACH = { arm: 'Armature GPU', mac: 'Mac seat' };
  function drawLive(d) {
    box.appendChild(h('h3', 'STAN A, full text'));
    var A = d.stan_a;
    if (A) box.appendChild(h('p', 'The teacher route is ' + A.stage + '. ' + A.cells_passed + ' of ' + A.cells + ' teacher-code cells passed the keep line written before the run.'));
    var E = d.stan_e;
    if (E) {
      box.appendChild(h('h3', 'STAN-E, errata drafted by local models'));
      box.appendChild(h('p', 'Each model is graded against findings that two independent readers confirmed. Confirmed papers so far: ' + E.verified_positive_papers + '. A hit is a confirmed finding the model also drafted.', 'meta'));
      if (E.runs && E.runs.length) box.appendChild(table(['Run', 'Papers seen', 'Papers flagged', 'Confirmed papers seen', 'Hits', 'Recall, 95% interval', 'Unreadable replies'],
        E.runs.map(function (r) { return [r.model, r.papers_seen, r.papers_flagged, r.verified_positive_papers_seen, r.hits, iv(r.recall_wilson95), r.parse_fail]; })));
      if (E.running_now && E.running_now.length) box.appendChild(h('p', 'Running now: ' + E.running_now.map(function (j) { return j.model + ' on the ' + MACH[j.machine]; }).join(', ') + '.'));
    }
    var P2 = d.pipelines;
    if (P2) {
      box.appendChild(h('h3', 'Where the confirmed findings come from'));
      Object.keys(P2).forEach(function (k) { var x = P2[k]; box.appendChild(h('p', (DESK[k] || k) + ': ' + x.findings_confirmed + ' findings confirmed, ' + x.batches_merged + ' batches merged, ' + x.queue_left + ' papers still queued.')); });
    }
    box.appendChild(h('p', 'Feed written ' + utc(d.updated) + ' (' + ago(d.updated) + '). Updated again every minute.', 'meta'));
  }
  function draw(d) {
    box.textContent = '';
    if (!d || !d.stage) { box.appendChild(h('p', 'The live feed has not been written yet.')); return; }
    drawLive(d);
    box.appendChild(h('h3', 'The closed abstract lane'));
    box.appendChild(h('p', 'The record of the first STAN run, on titles and abstracts, stays below. Its last stage was: ' + d.stage + '.', 'meta'));
    var si = STAGES.indexOf(d.stage); if (si < 0) si = STAGES.length;
    box.appendChild(h('h3', 'Where the run is'));
    box.appendChild(h('p', STAGE_TEXT[d.stage] || ''));
    box.appendChild(table(['Stage', 'State'], STAGES.map(function (s, i) { return [s, i < si ? 'done' : (i === si ? 'now' : 'not yet')]; })));
    var T = d.teachers || {};
    if (T.names && T.names.length) {
      box.appendChild(h('h3', 'Teachers'));
      box.appendChild(table(['Teacher', 'First round, claims labelled', 'Second round, claims labelled'],
        T.names.map(function (n) { var l = (T.labelled || {})[n] || {}; return [nm(n), (l.round1 || {}).labelled, (l.round2 || {}).labelled]; })));
      if (T.slices && T.slices.length) {
        box.appendChild(h('p', 'By slice of the claim pool, first round then second round, for each teacher.', 'meta'));
        box.appendChild(table(['Slice', 'Claims'].concat(T.names.map(nm)),
          T.slices.map(function (s) { return [s.slice, s.items].concat(T.names.map(function (n) { return (s.labelled_round1 || {})[n] + ' / ' + (s.labelled_round2 || {})[n]; })); })));
      }
    }
    var S = d.silver || {};
    if (S.silver_pairs != null) {
      box.appendChild(h('h3', 'Training examples from agreement'));
      box.appendChild(table(['Reading', 'Value'], [
        ['Claim and code pairs where all three teachers agreed with a quote', S.silver_pairs],
        ['Training rows built so far', S.train_rows], ['Validation rows', S.valid_rows],
        ['Pairs where two of three agreed, held for review', S.review_queue_two_of_three],
        ['Claims not yet labelled by all three', S.items_not_yet_labelled_by_all_three]]));
    }
    var B = d.baseline_gold_dev;
    if (B) {
      box.appendChild(h('h3', 'Baseline on the development half of the answer key'));
      box.appendChild(h('p', 'Agreement counts a cannot tell answer as agreeing with every recount that did not flag the code, so it mostly measures how often a model abstains, not skill. Our referee caught this on 12 November. Read it beside the share of calls each model commits to, in the headline above.'));
      var order = ['base', 'llama', 'mistral', 'gemma'].filter(function (k) { return B[k]; }).concat(Object.keys(B).filter(function (k) { return ['base', 'llama', 'mistral', 'gemma'].indexOf(k) < 0; }));
      box.appendChild(table(['Model', 'Agree', 'Of', 'Agreement', '95% interval', 'Always guess the most common answer'],
        order.map(function (k) { var q = (B[k] || {}).pooled || {}; return [nm(k), q.agree, q.n, p3(q.rate), iv(q.wilson95), p3(B[k].majority_class_rate)]; })));
    }
    var C = d.bench_gold_dev;
    if (C && Object.keys(C).length) {
      box.appendChild(h('h3', 'Scoreboard: other small models on the same claims'));
      box.appendChild(table(['Model', 'Claims labelled', 'Agreement', '95% interval'],
        Object.keys(C).map(function (k) { var q = C[k].pooled || {}; return [k, C[k].labelled + ' of ' + C[k].n_items, p3(q.rate), iv(q.wilson95)]; })));
    }
    var R = d.training;
    if (R) {
      box.appendChild(h('h3', 'Training'));
      box.appendChild(table(['Reading', 'Value'], [['Base model', R.base + ' (' + R.license + ')'], ['Training rows', R.train_rows], ['Steps', R.iters], ['Seconds', R.seconds], ['LoRA rank', R.rank]]));
    }
    var P = d.paired_test;
    if (P) {
      var pp = (P.paired_stan_minus_base || {}).pooled || {};
      box.appendChild(h('h3', 'Paired test'));
      box.appendChild(table(['Reading', 'Value'], [
        ['Claims in the test half', P.n_items], ['Base agreement', p3(((P.base || {}).pooled || {}).rate)], ['STAN agreement', p3(((P.stan || {}).pooled || {}).rate)],
        ['STAN minus base, mean over seven codes', p3(pp.mean)], ['95% paired bootstrap interval', pp.ci95 ? '[' + p3(pp.ci95[0]) + ', ' + p3(pp.ci95[1]) + ']' : '-'],
        ["Band reading", P.band_reading], ['Kept', P.kept ? 'yes' : 'no']].concat(P.base_conversion && P.base_conversion.base ? [['Base answers turned into CANNOT_TELL by the quote rule (no word-for-word quote)', P.base_conversion.base.ct_by_quote_rule + ' of ' + P.base_conversion.base.calls], ['STAN answers that chose CANNOT_TELL itself', P.base_conversion.stan.ct_chosen_by_model + ' of ' + P.base_conversion.stan.calls]] : [])));
      if (P.base_conversion) box.appendChild(h('p', 'The base model never chose CANNOT_TELL. Our quote rule made most of its answers CANNOT_TELL. STAN chose it every time, so the two columns do not measure the same act.'));
    }
    var L = d.plan;
    if (L) {
      box.appendChild(h('h3', 'The plan, written first'));
      box.appendChild(table(['File', 'sha256', 'OpenTimestamps'], [['PLAN.md', L.sha256, L.stamp], ['PLAN_ADDENDUM_1.md', L.addendum_1_sha256, L.addendum_1_stamp]]));
    }
  }
  function load() {
    fetch('/iris/lab/stan.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(function () { box.textContent = 'The live feed is not reachable right now.'; });
  }
  load(); setInterval(load, 60000);
})();
