// Heuremen LLC app shell (and, since 10 Nov 2026, the notifications a reader turns on with "Notify me on this device": notify.js, push_send.py). Everything is network first, so an update shows on the next load, and kept for offline reading. Live data, forms and sign-in are never cached.
var V = 'hlc-v4', SHELL = ['/', '/style.css', '/icons/icon-192.png'];
var SKIP = /^\/(contact|inquire|inquiry|api|auth|callback|respond|nda|alerts|signup|webhooks|push|newsletter\/unsubscribe)(\/|$|\?)|\/live\.json$|\/live\.js$|\.json$|\.xml$|\.ics$/;
self.addEventListener('install', function (e) { e.waitUntil(caches.open(V).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); })); });
self.addEventListener('activate', function (e) { e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== V && k !== 'hlc-push'; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); })); });
self.addEventListener('fetch', function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin || SKIP.test(u.pathname)) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then(function (res) { var cp = res.clone(); if (res.ok) caches.open(V).then(function (c) { c.put(r, cp); }); return res; }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('/'); }); }));
    return;
  }
  e.respondWith(fetch(r).then(function (res) { if (res.ok) { var cp = res.clone(); caches.open(V).then(function (c) { c.put(r, cp); }); } return res; }).catch(function () { return caches.match(r); }));
});
// 10 Nov 2026: a notification for an outcome change (push_send.py sends {title, body, url, tag}, encrypted for this browser). A click opens the desk.
self.addEventListener('push', function (e) {
  var d = {}; try { d = e.data ? e.data.json() : {}; } catch (x) { d = { body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || 'indahl.ai', { body: d.body || '', icon: '/icons/icon-192.png', badge: '/icons/icon-192.png', tag: d.tag || undefined, data: { url: d.url || '/' } }));
});
self.addEventListener('notificationclick', function (e) {
  e.notification.close(); var u = (e.notification.data && e.notification.data.url) || '/';
  try { if (new URL(u, location.origin).origin !== location.origin) u = '/'; } catch (x) { u = '/'; }
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (cs) {
    for (var i = 0; i < cs.length; i++) if (cs[i].url === new URL(u, location.origin).href && 'focus' in cs[i]) return cs[i].focus();
    return self.clients.openWindow(u);
  }));
});
// 10 Nov 2026: the browser replaced the push subscription. Subscribe again with our key and move the record (found by the token the page keeps
// in the hlc-push cache) to the new subscription, so the desks picked stay on without a press of the button.
self.addEventListener('pushsubscriptionchange', function (e) {
  e.waitUntil(caches.open('hlc-push').then(function (c) { return c.match('/push/token'); }).then(function (m) { return m ? m.text() : ''; }).then(function (t) {
    if (!/^[0-9a-f]{40}$/.test(t)) return;
    var b64 = function (s) { var r = atob((s + '='.repeat((4 - s.length % 4) % 4)).replace(/-/g, '+').replace(/_/g, '/')), a = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) a[i] = r.charCodeAt(i); return a; };
    var get = e.newSubscription ? Promise.resolve(e.newSubscription) : fetch('/push/key').then(function (r) { return r.json(); }).then(function (k) { return self.registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64(k.key) }); });
    return get.then(function (s) { return fetch('/push/resubscribe', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ t: t, sub: s.toJSON() }) }); });
  }).catch(function () {}));
});
