// Follow any named thing: search over /e/index.json, grouped by kind. Ticks a box in the form on this page. No tracking, nothing sent.
(function () {
  var q = document.getElementById('ent-q'), out = document.getElementById('ent-res'), picked = document.getElementById('ent-picked'); if (!q || !out || !picked) return;
  var data = null, K = {};
  function load(cb) { if (data) return cb(); fetch('/e/index.json').then(function (r) { return r.json(); }).then(function (d) { data = d.e; K = d.kinds; cb(); }).catch(function () { out.textContent = 'The list could not be loaded.'; }); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function add(id, name, kind) {
    if (picked.querySelector('input[value="' + id.replace(/"/g, '') + '"]')) { picked.querySelector('input[value="' + id.replace(/"/g, '') + '"]').checked = true; return; }
    var l = document.createElement('label'); l.innerHTML = '<input type="checkbox" name="en" checked> Rows about ' + esc(name) + ' <span class="meta">' + esc(kind) + '</span>';
    l.firstChild.value = id; picked.appendChild(l); picked.hidden = false;
  }
  window.hlcFollow = function (id) { load(function () { for (var i = 0; i < data.length; i++) if (data[i][0] === id) { add(id, data[i][2], (K[data[i][1]] || '').replace(/s$/, '')); return; } }); };
  q.addEventListener('input', function () {
    var t = q.value.trim().toLowerCase(); if (t.length < 2) { out.innerHTML = ''; return; }
    load(function () {
      var g = {}, n = 0;
      for (var i = 0; i < data.length && n < 60; i++) { var e = data[i], hay = (e[2] + ' ' + e[3].join(' ')).toLowerCase(); if (hay.indexOf(t) >= 0) { (g[e[1]] = g[e[1]] || []).push(e); n++; } }
      var h = '';
      Object.keys(K).forEach(function (k) { if (!g[k]) return; h += '<p class="su-dh">' + esc(K[k]) + '</p><ul class="su-list">' + g[k].map(function (e) { return '<li><button type="button" class="linkbtn" data-id="' + esc(e[0]) + '" data-n="' + esc(e[2]) + '" data-k="' + esc(K[k]) + '">Follow</button> <a href="' + esc(e[4]) + '">' + esc(e[2]) + '</a>' + (e[3].length ? ' <span class="meta">' + esc(e[3].join(', ')) + '</span>' : '') + '</li>'; }).join('') + '</ul>'; });
      out.innerHTML = h || '<p class="meta">Nothing by that name is on a desk yet.</p>';
    });
  });
  out.addEventListener('click', function (ev) { var b = ev.target.closest ? ev.target.closest('button[data-id]') : null; if (!b) return; add(b.getAttribute('data-id'), b.getAttribute('data-n'), b.getAttribute('data-k').replace(/s$/, '')); b.textContent = 'Ticked'; });
  var m = /[?&]e=([^&]+)/.exec(location.search); if (m) window.hlcFollow(decodeURIComponent(m[1]));
})();
