// LIVE tags: a small mark beside a desk or division link while that desk is being read, evaluated or trained, or finished a few minutes ago.
// "live" = being read now or just read; "eval" = a model evaluation is running (hours); "train" = a training run is going.
(function () {
  var HREF = { model: '/hermes/model' }, TAGGED = [], WORD = { reading: 'live', 'just read': 'live', evaluating: 'eval', training: 'train' };
  var TITLE = { live: 'Being read now', eval: 'A model evaluation is running now', train: 'A training run is going now' };
  function href(slug) { return HREF[slug] || '/' + slug; }
  function mark(a, word) {
    if (a.querySelector('.livetag')) return; var t = document.createElement('span'); t.className = 'livetag lt-' + word; t.title = TITLE[word]; t.setAttribute('aria-label', word); t.textContent = word; a.appendChild(t); TAGGED.push(t);
  }
  function clear() { TAGGED.forEach(function (t) { if (t.parentNode) t.parentNode.removeChild(t); }); TAGGED = []; }
  function run() {
    fetch('/activity.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      clear(); if (!d || (d.updated && (Date.now() - Date.parse(d.updated)) > 45 * 60 * 1000)) return;
      var live = d.live || {}, divs = d.divisions || {};
      Object.keys(live).forEach(function (slug) {
        var w = WORD[live[slug]] || 'live'; document.querySelectorAll('a[href="' + href(slug) + '"]').forEach(function (a) { if (!(slug in divs)) mark(a, w); else if (a.closest('.hdesks, .ddpanel, .desklist, .hmore')) mark(a, w); });
      });
      Object.keys(divs).forEach(function (dv) { document.querySelectorAll('a[href="/' + dv + '"]').forEach(function (a) { mark(a, divs[dv]); }); });
    }).catch(function () {});
  }
  run(); setInterval(run, 60000);
})();
