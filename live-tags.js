// LIVE tags: a small mark beside a desk or division link.
// "live" = being read now or read in the last few minutes; "eval" = a model evaluation is running (hours); "train" = a training run is going.
// 31 Oct 2026: a desk whose feed is current on its schedule but was not read just now says when it was last read ("read 3 h ago"),
// counted from the feed's own stamp and updated every minute, instead of a bare "live".
(function () {
  var HREF = { model: '/hermes/model' }, TAGGED = [], WORD = { reading: 'live', 'just read': 'live', 'on schedule': 'read', evaluating: 'eval', training: 'train' };
  var TITLE = { live: 'Being read now', eval: 'A model evaluation is running now', train: 'A training run is going now' };
  var MODE_TITLE = { reading: 'Being read now', 'just read': 'Read in the last few minutes' };
  var READ = {};
  function href(slug) { return HREF[slug] || '/' + slug; }
  function ago(iso) {
    var m = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    if (m < 1) return 'read just now'; if (m < 60) return 'read ' + m + ' min ago';
    var h = Math.floor(m / 60); if (h < 48) return 'read ' + h + ' h ago'; return 'read ' + Math.floor(h / 24) + ' days ago';
  }
  function mark(a, word, mode, slug) {
    if (a.querySelector('.livetag')) return; var t = document.createElement('span'); t.className = 'livetag lt-' + word;
    if (word === 'read' && READ[slug]) { t.setAttribute('data-read', READ[slug]); t.textContent = ago(READ[slug]); t.title = 'Last read ' + new Date(READ[slug]).toUTCString().replace(' GMT', ' UTC'); }
    else { if (word === 'read') { word = 'live'; t.className = 'livetag lt-live'; } t.textContent = word; t.title = MODE_TITLE[mode] || TITLE[word]; }
    t.setAttribute('aria-label', t.textContent); a.appendChild(t); TAGGED.push(t);
  }
  function clear() { TAGGED.forEach(function (t) { if (t.parentNode) t.parentNode.removeChild(t); }); TAGGED = []; }
  function tick() { TAGGED.forEach(function (t) { var r = t.getAttribute('data-read'); if (r) { t.textContent = ago(r); t.setAttribute('aria-label', t.textContent); } }); }
  function run() {
    fetch('/activity.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      clear(); if (!d || (d.updated && (Date.now() - Date.parse(d.updated)) > 45 * 60 * 1000)) return;
      var live = d.live || {}, divs = d.divisions || {}; READ = d.read || {};
      Object.keys(live).forEach(function (slug) {
        var m = live[slug], w = WORD[m] || 'live'; document.querySelectorAll('a[href="' + href(slug) + '"]').forEach(function (a) { if (!(slug in divs)) mark(a, w, m, slug); else if (a.closest('.hdesks, .ddpanel, .desklist, .hmore')) mark(a, w, m, slug); });
      });
      Object.keys(divs).forEach(function (dv) { document.querySelectorAll('a[href="/' + dv + '"]').forEach(function (a) { mark(a, divs[dv]); }); });
    }).catch(function () {});
  }
  run(); setInterval(run, 60000); setInterval(tick, 30000);
})();
