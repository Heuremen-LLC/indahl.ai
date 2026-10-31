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
  // 31 Oct 2026 (his "anything that we label live should look live and not static"): on a desk's own page, a strip under the headline.
  // Reading now: a moving bar with the count and the item being read (desks that report progress, /progress/<desk>.json).
  // Between reads: a clock counting up from the last read, and a bar filling toward the next scheduled read (the desk's rider schedule).
  var SLUG = (location.pathname.split('/')[1] || ''), ACT = null, PROG = null;
  function dur(ms) { var s = Math.max(0, Math.floor(ms / 1000)), h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
    return ((h ? h + ' h ' : '') + (h || m ? m + ' min ' : '') + (h ? '' : x + ' s')).trim(); }
  function fmt(n) { return Number(n).toLocaleString('en-US'); }
  function stripEl() {
    var main = document.querySelector('main.wrap'); if (!main) return null; var s = document.getElementById('livestrip');
    if (!s) { s = document.createElement('div'); s.id = 'livestrip'; s.setAttribute('aria-live', 'off');
      s.innerHTML = '<span class="lsp-dot"></span><span class="lsp-txt"></span><span class="lsp-bar"><span class="lsp-fill"></span></span>';
      var hl = main.querySelector('.hl, #hl-slot'); if (hl && hl.parentNode) hl.parentNode.insertBefore(s, hl.nextSibling); else main.insertBefore(s, main.firstChild); }
    return s;
  }
  function paint() {
    if (!ACT || !SLUG) return; var mode = (ACT.live || {})[SLUG], read = (ACT.read || {})[SLUG], every = (ACT.every_min || {})[SLUG];
    if (!mode && !read) { var o = document.getElementById('livestrip'); if (o) o.parentNode.removeChild(o); return; }
    var s = stripEl(); if (!s) return; var txt = s.querySelector('.lsp-txt'), fill = s.querySelector('.lsp-fill'), now = Date.now();
    var running = PROG && PROG.running && PROG.total && (now - Date.parse(PROG.t)) < 180000;
    if (running) {
      s.className = 'livestrip lsp-reading'; fill.style.width = (100 * PROG.done / PROG.total).toFixed(1) + '%';
      txt.textContent = 'Reading now' + (PROG.label ? ', ' + PROG.label : '') + ': ' + fmt(PROG.done) + ' of ' + fmt(PROG.total) + (PROG.what ? ', ' + PROG.what : '');
    } else if (mode === 'reading') {
      s.className = 'livestrip lsp-reading lsp-indet'; fill.style.width = ''; txt.textContent = 'Reading now';
    } else if (read) {
      var el = now - Date.parse(read), cyc = every ? every * 60000 : 0; s.className = 'livestrip lsp-wait';
      fill.style.width = cyc ? Math.min(100, 100 * el / cyc).toFixed(2) + '%' : '0%';
      txt.textContent = 'Last read ' + dur(el) + ' ago.' + (cyc ? (el < cyc ? ' Next scheduled read in about ' + dur(cyc - el).replace(/ \d+ s$/, '') + '.' : ' Next scheduled read is due.') + ' Reads about every ' + dur(cyc).replace(/ \d+ s$/, '').trim() + '.' : '');
    }
  }
  function prog() { if (!SLUG) return; fetch('/progress/' + SLUG + '.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (p) { PROG = p && p.desk ? p : null; paint(); }).catch(function () {}); }
  function act() { fetch('/activity.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) { ACT = d; paint(); }).catch(function () {}); }
  run(); setInterval(run, 60000); setInterval(tick, 30000);
  if (SLUG && !/\.|^$/.test(SLUG)) { act(); prog(); setInterval(act, 60000); setInterval(prog, 5000); setInterval(paint, 1000); }
})();
