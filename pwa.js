// Registers the app shell. Nothing is sent anywhere: the worker only keeps public pages on the visitor's own device.
if ('serviceWorker' in navigator) window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {}); });
// 31 Oct 2026: app badge. The number on the installed app's icon = desks read since this device last opened NOW. Kept in this browser only.
(function () {
  if (!('setAppBadge' in navigator)) return;
  var K = 'hlc_now_seen', seen = 0;
  try { seen = +(localStorage.getItem(K) || 0); } catch (e) {}
  if (location.pathname.replace(/\/+$/, '') === '/now') { try { localStorage.setItem(K, String(Date.now())); } catch (e) {} if (navigator.clearAppBadge) navigator.clearAppBadge().catch(function () {}); return; }
  function upd() {
    fetch('/activity.json', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var n = Object.values((d && d.read) || {}).filter(function (t) { return Date.parse(t) > seen; }).length;
      (n ? navigator.setAppBadge(n) : navigator.clearAppBadge()).catch(function () {});
    }).catch(function () {});
  }
  if (seen) { upd(); setInterval(upd, 300000); }
})();
