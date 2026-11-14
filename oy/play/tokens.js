// OY: how a language model reads. A real byte-pair tokenizer, trained right here on public-domain nursery rhymes;
// YO, who read the same bytes but has one token; and the guess-the-next-piece game models are trained on. (23 Oct 2026)
const CORPUS = `twinkle twinkle little star how i wonder what you are up above the world so high like a diamond in the sky
twinkle twinkle little star how i wonder what you are
row row row your boat gently down the stream merrily merrily merrily merrily life is but a dream
hickory dickory dock the mouse ran up the clock the clock struck one the mouse ran down hickory dickory dock
mary had a little lamb its fleece was white as snow and everywhere that mary went the lamb was sure to go
humpty dumpty sat on a wall humpty dumpty had a great fall
hey diddle diddle the cat and the fiddle the cow jumped over the moon the little dog laughed to see such sport and the dish ran away with the spoon`;
const $ = id => document.getElementById(id);
const words = {}; for (const w of CORPUS.split(/\s+/)) words[w] = (words[w] || 0) + 1;
// train merges once: every word starts as single letters, with a mark for the space in front of it
const MERGES = []; let vocab = Object.entries(words).map(([w, n]) => ({ sym: ['␣', ...w], n }));
for (let step = 0; step < 150; step++) {
  const pairs = {};
  for (const { sym, n } of vocab) for (let i = 0; i < sym.length - 1; i++) { const k = sym[i] + '\u0000' + sym[i + 1]; pairs[k] = (pairs[k] || 0) + n; }
  let best = null, bn = 1; for (const [k, n] of Object.entries(pairs)) if (n > bn) { best = k; bn = n; }
  if (!best) break; const [a, b] = best.split('\u0000'); MERGES.push([a, b]);
  vocab = vocab.map(({ sym, n }) => { const o = []; for (let i = 0; i < sym.length; i++) { if (i < sym.length - 1 && sym[i] === a && sym[i + 1] === b) { o.push(a + b); i++; } else o.push(sym[i]); } return { sym: o, n }; });
}
function tokenize(text, m) {
  const out = [];
  for (const w of text.toLowerCase().split(/\s+/).filter(Boolean)) {
    let sym = ['␣', ...w];
    for (let j = 0; j < m; j++) { const [a, b] = MERGES[j]; const o = []; for (let i = 0; i < sym.length; i++) { if (i < sym.length - 1 && sym[i] === a && sym[i + 1] === b) { o.push(a + b); i++; } else o.push(sym[i]); } sym = o; }
    out.push(...sym);
  }
  return out;
}
const hue = t => { let h = 0; for (const c of t) h = (h * 31 + c.charCodeAt(0)) % 360; return h; };
function chips(el, toks, yo) {
  el.textContent = '';
  for (const t of toks) { const s = document.createElement('span'); s.className = 'tok'; s.textContent = yo ? 'I' : t.replace('␣', '·');
    s.style.background = yo ? 'hsl(45,80%,80%)' : `hsl(${hue(t)},70%,85%)`; el.appendChild(s); }
}
function render() {
  const m = +$('tok-steps').value, text = $('tok-in').value, toks = tokenize(text, m);
  chips($('tok-out'), toks, false); chips($('yo-out'), toks, true);
  $('tok-count').textContent = `${m} lessons learned · ${toks.length} pieces` + (m ? ` · newest piece: "${(MERGES[m - 1][0] + MERGES[m - 1][1]).replace('␣', '·')}"` : ' · every letter is its own piece');
  $('yo-count').textContent = `${toks.length} pieces, all of them: I`;
  guessTable(m);
}
// guess the next piece: count which piece follows which, in the rhymes
function guessTable(m) {
  const seq = tokenize(CORPUS, m), next = {};
  for (let i = 0; i < seq.length - 1; i++) { const a = seq[i], b = seq[i + 1]; (next[a] = next[a] || {})[b] = (next[a][b] || 0) + 1; }
  const toks = tokenize($('tok-in').value, m), last = toks[toks.length - 1], row = next[last] || {};
  const tot = Object.values(row).reduce((x, y) => x + y, 0), top = Object.entries(row).sort((x, y) => y[1] - x[1]).slice(0, 3);
  $('guess-out').textContent = !last ? 'Type something first.' : !tot ? `After "${last.replace('␣', '·')}" the rhymes never had anything next. No guess: I can't tell.`
    : `After "${last.replace('␣', '·')}", the next piece was: ` + top.map(([t, n]) => `"${t.replace('␣', '·')}" ${Math.round(100 * n / tot)}%`).join(', ');
  window.__next = next;
}
$('guess-go').addEventListener('click', () => {
  const m = +$('tok-steps').value; let toks = tokenize($('tok-in').value, m);
  for (let i = 0; i < 6; i++) { const row = (window.__next || {})[toks[toks.length - 1]]; if (!row) break;
    const best = Object.entries(row).sort((x, y) => y[1] - x[1])[0][0]; toks.push(best); }
  $('tok-in').value = toks.join('').replace(/␣/g, ' ').trim(); render();
});
$('tok-steps').max = MERGES.length; $('tok-steps').addEventListener('input', render); $('tok-in').addEventListener('input', render); render();
