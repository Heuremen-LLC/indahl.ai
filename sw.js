// Heuremen LLC app shell. Everything is network first, so an update shows on the next load, and kept for offline reading. Live data, forms and sign-in are never cached.
var V = 'hlc-v2', SHELL = ['/', '/style.css', '/icons/icon-192.png'];
var SKIP = /^\/(contact|inquire|inquiry|api|auth|callback|respond|nda)(\/|$|\?)|\/live\.json$|\/live\.js$|\.json$/;
self.addEventListener('install', function (e) { e.waitUntil(caches.open(V).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); })); });
self.addEventListener('activate', function (e) { e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== V; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); })); });
self.addEventListener('fetch', function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin || SKIP.test(u.pathname)) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then(function (res) { var cp = res.clone(); if (res.ok) caches.open(V).then(function (c) { c.put(r, cp); }); return res; }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('/'); }); }));
    return;
  }
  e.respondWith(fetch(r).then(function (res) { if (res.ok) { var cp = res.clone(); caches.open(V).then(function (c) { c.put(r, cp); }); } return res; }).catch(function () { return caches.match(r); }));
});
