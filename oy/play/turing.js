// OY: a Turing machine that adds one. A tape of symbols, a head that reads one square at a time, and a short rule table.
// Base 2 uses two symbols; base 3 uses three. Same machine idea: Turing's machines work with any set of symbols. (23 Oct 2026)
const $ = id => document.getElementById(id);
let tape = [], head = 0, state = 'add', base = 2, steps = 0, timer = null;
function load() { base = +$('tm-base').value; const n = Math.max(0, Math.min(999, parseInt($('tm-num').value) || 0));
  tape = ['_', ...n.toString(base).split(''), '_']; head = tape.length - 2; state = 'add'; steps = 0; draw(`Start: ${n} written in base ${base}. The head starts on the last digit.`); }
function step() {
  if (state === 'halt') return false;
  const s = tape[head]; steps++;
  if (s === '_') { tape[head] = '1'; state = 'halt'; if (head === 0) tape.unshift('_'), head++; draw('Blank square: write 1. Halt.'); return false; }
  const v = parseInt(s, base);
  if (v < base - 1) { tape[head] = (v + 1).toString(base); state = 'halt'; draw(`Read ${s}: write ${v + 1}. Halt.`); return false; }
  tape[head] = '0'; head--; draw(`Read ${s}: it's the biggest digit, so write 0 and carry one square left.`); return true;
}
function draw(msg) {
  $('tm-tape').textContent = ''; tape.forEach((s, i) => { const c = document.createElement('span'); c.className = 'cell' + (i === head ? ' head' : ''); c.textContent = s === '_' ? '' : s; $('tm-tape').appendChild(c); });
  const digits = tape.join('').replace(/_/g, ''); $('tm-msg').textContent = msg;
  $('tm-state').textContent = `State: ${state === 'halt' ? 'HALT' : 'adding one'} · step ${steps}` + (state === 'halt' ? ` · tape now says ${digits} = ${parseInt(digits, base)}` : '');
}
$('tm-load').addEventListener('click', () => { clearInterval(timer); load(); });
$('tm-step').addEventListener('click', () => step());
$('tm-run').addEventListener('click', () => { clearInterval(timer); timer = setInterval(() => { if (!step()) clearInterval(timer); }, 700); });
$('tm-base').addEventListener('change', () => { clearInterval(timer); load(); });
load();
