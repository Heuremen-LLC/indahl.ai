// OY: real quantum coins. Bits measured on 7 April 2026 (8 qubits in superposition, then measured; ibm_kingston,
// ibm_marrakesh, ibm_fez; 4096 bytes each, quantum_bytes.js). The bytes were saved sorted by value, so the original
// order is lost: we hand the bits out in a shuffled order (an odd stride through all 32768). Every bit is a real measurement.
const $ = id => document.getElementById(id);
const STRIDE = 20261, N = 32768, chips = {};
for (const name of ['kingston', 'marrakesh', 'fez']) { const s = atob(window.QUANTUM_BYTES[name]), b = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); chips[name] = { b, i: Math.floor(Math.random() * N) }; }
let chip = 'kingston';
function bit() { const c = chips[chip], pos = (c.i++ * STRIDE) % N; return (c.b[pos >> 3] >> (pos & 7)) & 1; }
const tally = { H: 0, T: 0 };
function flip(n) {
  let last; for (let k = 0; k < n; k++) { last = bit() ? 'H' : 'T'; tally[last]++; }
  $('coin').textContent = last; $('coin').className = 'coin flip';
  void $('coin').offsetWidth; $('coin').className = 'coin ' + (last === 'H' ? 'heads' : 'tails');
  const tot = tally.H + tally.T; $('coin-tally').textContent = `${tally.H} heads · ${tally.T} tails · ${tot} flips · ${(100 * tally.H / tot).toFixed(1)}% heads`;
}
for (const b of document.querySelectorAll('[data-chip]')) b.addEventListener('click', () => { chip = b.dataset.chip; document.querySelectorAll('[data-chip]').forEach(x => x.classList.toggle('on', x === b)); $('coin-from').textContent = 'ibm_' + chip; });
$('coin').addEventListener('click', () => flip(1)); $('flip-10').addEventListener('click', () => flip(10)); $('flip-100').addEventListener('click', () => flip(100));
$('flip-reset').addEventListener('click', () => { tally.H = tally.T = 0; $('coin-tally').textContent = ''; $('coin').textContent = '?'; $('coin').className = 'coin'; });
// the bet: ten coins sealed before you call
let sealed = [], at = 0, hits = 0;
function newBatch() { sealed = Array.from({ length: 10 }, () => bit() ? 'H' : 'T'); at = 0; hits = 0; showBet('Ten coins are sealed. Call the first one.'); }
function showBet(msg) { $('bet-row').textContent = sealed.map((c, i) => i < at ? c : '•').join(' '); $('bet-msg').textContent = msg + (at ? `  ${hits} of ${at} right.` : ''); }
function call(c) { if (!sealed.length || at >= 10) { newBatch(); return; } const was = sealed[at++]; if (was === c) hits++;
  showBet(at < 10 ? `It was ${was === 'H' ? 'heads' : 'tails'}.` : `Done. About 5 of 10 is what anyone gets.`); }
$('bet-new').addEventListener('click', newBatch); $('bet-h').addEventListener('click', () => call('H')); $('bet-t').addEventListener('click', () => call('T'));
