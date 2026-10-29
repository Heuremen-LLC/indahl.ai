// VAULT: everything happens in this browser. The file is hashed here, sealed here and opened here. Only a SHA-256 hash is ever sent, and only when you press the receipt button.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var BASE = location.origin + '/tape/drand';
  var MAX = 60 * 1024 * 1024;
  function hex(buf) { return Array.prototype.map.call(new Uint8Array(buf), function (b) { return b.toString(16).padStart(2, '0'); }).join(''); }
  function sha256(buf) { return crypto.subtle.digest('SHA-256', buf).then(hex); }
  function read(file) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(r.result); }; r.onerror = function () { rej(r.error); }; r.readAsArrayBuffer(file); }); }
  function readText(file) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(r.result); }; r.onerror = function () { rej(r.error); }; r.readAsText(file); }); }
  function utc(ms) { return new Date(ms).toISOString().replace('.000Z', 'Z').replace('T', ' '); }
  function save(name, data, type) { var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([data], { type: type || 'application/octet-stream' })); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 4000); }
  function say(id, txt) { $(id).textContent = txt; }
  function receipt(r) { return 'Hash ' + r.h + '. Received ' + r.received_utc + ' UTC. ' + (r.entry ? 'On the tape as entry ' + r.entry + '.' : 'It joins the tape within the hour.') + ' To check it later, paste the hash into Check a receipt.'; }
  function commit(h, out) {
    say(out, 'Sending the hash.');
    return fetch('/tape/commit', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ h: h }) }).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'failed'); return j; }); }).then(function (j) { say(out, receipt(j)); }).catch(function (e) { say(out, 'No receipt: ' + e.message + '.'); });
  }
  // 1 receipt
  var curHash = '';
  $('v-file').addEventListener('change', function () { var f = this.files[0]; $('v-commit').disabled = true; if (!f) return; say('v-hash', 'Hashing.'); read(f).then(sha256).then(function (h) { curHash = h; say('v-hash', h); $('v-commit').disabled = false; }); });
  $('v-commit').addEventListener('click', function () { if (curHash) commit(curHash, 'v-receipt'); });
  function lookup(h) { h = (h || '').trim().toLowerCase(); if (!/^[0-9a-f]{64}$/.test(h)) { say('v-found', 'A hash is 64 characters, 0 to 9 and a to f.'); return; } fetch('/tape/receipt/' + h, { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) { say('v-found', j.status === 'not found' ? 'No receipt for that hash.' : receipt(j)); }); }
  $('v-check').addEventListener('click', function () { lookup($('v-lookup').value); });
  var q = /[?&]h=([0-9a-fA-F]{64})/.exec(location.search); if (q) { $('v-lookup').value = q[1]; lookup(q[1]); }
  // 2 seal
  var now = new Date(Date.now() + 120000); now.setSeconds(0, 0);
  function local(d) { var p = function (n) { return String(n).padStart(2, '0'); }; return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + 'T' + p(d.getHours()) + ':' + p(d.getMinutes()); }
  $('s-when').min = local(now); var yr = new Date(); yr.setFullYear(yr.getFullYear() + 1); yr.setSeconds(0, 0); $('s-when').value = local(yr);
  $('s-go').addEventListener('click', function () {
    var f = $('s-file').files[0], when = new Date($('s-when').value).getTime();
    if (!f) { say('s-out', 'Pick a file first.'); return; }
    if (!(when > Date.now() + 60000)) { say('s-out', 'Pick a time at least a minute from now.'); return; }
    if (f.size > MAX) { say('s-out', 'That file is over 60 MB. Seal a smaller one.'); return; }
    if (!window.VAULT_TL) { say('s-out', 'The sealing code did not load.'); return; }
    var round = window.VAULT_TL.roundAt(when); say('s-out', 'Sealing.'); $('s-go').disabled = true;
    read(f).then(function (buf) {
      var head = new TextEncoder().encode(JSON.stringify({ name: f.name, type: f.type || 'application/octet-stream', size: f.size })), pay = new Uint8Array(4 + head.length + buf.byteLength);
      new DataView(pay.buffer).setUint32(0, head.length); pay.set(head, 4); pay.set(new Uint8Array(buf), 4 + head.length);
      return window.VAULT_TL.encrypt(pay, round, BASE);
    }).then(function (ct) {
      var opens = window.VAULT_TL.roundTime(round), name = (f.name.replace(/\.[^.]*$/, '') || 'file') + '.sealed.txt';
      save(name, ct, 'text/plain');
      return sha256(new TextEncoder().encode(ct)).then(function (h) { say('s-out', 'Sealed. The file ' + name + ' was saved to your downloads. Nobody can open it before ' + utc(opens) + ' UTC (drand round ' + round + '). After that anyone holding it can. Its hash is ' + h + '.'); $('s-hash').value = h; $('s-commit').disabled = false; });
    }).catch(function (e) { say('s-out', 'Could not seal: ' + e.message); }).then(function () { $('s-go').disabled = false; });
  });
  $('s-commit').addEventListener('click', function () { if ($('s-hash').value) commit($('s-hash').value, 's-receipt'); });
  // 3 open
  $('o-go').addEventListener('click', function () {
    var f = $('o-file').files[0]; if (!f) { say('o-out', 'Pick a sealed file first.'); return; }
    say('o-out', 'Opening.'); $('o-go').disabled = true;
    readText(f).then(function (t) { return window.VAULT_TL.decrypt(t, BASE); }).then(function (pay) {
      var n = new DataView(pay.buffer, pay.byteOffset).getUint32(0), meta = JSON.parse(new TextDecoder().decode(pay.slice(4, 4 + n))), body = pay.slice(4 + n);
      save(meta.name || 'opened-file', body, meta.type); say('o-out', 'Opened. ' + (meta.name || 'The file') + ' was saved to your downloads.');
    }).catch(function (e) { var m = String(e && e.message || e); say('o-out', /too early|not yet|future|round/i.test(m) ? 'Not yet. This file cannot be opened until its release time. (' + m + ')' : 'Could not open it: ' + m); }).then(function () { $('o-go').disabled = false; });
  });
})();
