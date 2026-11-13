"""Recount Matrix: Language Models (indahl.ai/iris), same form as OY: publication on top, findings, then the lists. Facts only.
Writes iris_body.html (build_site.py reads it for /iris) and staged/language-matrix.html. Every number is a ledger row (pub2.*), surface iris_matrix."""
import os, re, sys, html
B = os.path.expanduser('~/bones-forge/'); sys.path.insert(0, B + 'indahl-ai'); import build_site as bs
E = html.escape; AS_OF = '25 October 2026'
bib = open(B + 'iris_index/pub2/paper/refs.bib').read()
def ref(key):
    m = re.search(r'@\w+\{' + key + r',(.*?)\n\}', bib, re.S); t = m.group(1)
    g = lambda f: (re.search(f + r'=\{(.*?)\},?\n', t, re.S) or [None, ''])[1].strip()
    return g('title'), g('author'), g('eprint')
BOOK = [('r2610_30512', 'Rebuilds (17,000 calls; every cell of the paper&rsquo;s Table 1).'),
 ('r2610_25964', 'Rebuilds (9,000 questions).'),
 ('r2610_31256', 'EM rebuilds on all 22 files; F1 to the printed digit on 18, four differ by 0.01&ndash;0.02 (cause not found).'),
 ('r2610_31135', 'Rebuilds (229,700 records).'),
 ('r2610_25159', 'Rebuilds.'), ('r2610_15732', 'Rebuilds.'),
 ('r2610_18610', 'Rebuilds, including the no-controls figures they report (69.1 vs 70.9).'),
 ('r2610_21468', 'Rebuilds.'),
 ('r2610_17203', 'Author agreement (69.6%) rebuilds; judge scores only under a favourite-answer rule defined after the data (74.5 exactly; 74.3 against 74.0 printed).'),
 ('r2610_25626', 'Rebuilds from per-run files (answer keys not released).'), ('r2610_24999', 'Rebuilds.')]
FINDINGS = [('Studies indexed with released files', '11'), ('Rebuilt to the printed digit', '9'), ('Within 0.02 F1', '1'),
 ('Only under a rule defined after the data', '1'),
 ('Outcome change, reported serving backend changed against unchanged (one run pair)', '+9.8 points [+2.1, +17.6]'),
 ('Score change, same model and seed on a different GPU and host', '76 of 8,000 question-position cells (0.95%)'),
 ('Verdict flip when the two answers swap position, no repeat floor, one run per judge: GPT-4.1, Claude Sonnet 4.5, Gemini 2.5 Flash', '31.0%, 31.3%, 30.9%')]
MODELS = [('gemma3:4b', '0.026 [0.000, 0.052]', '0.755 [0.696, 0.815]', '0.145 [0.100, 0.200]'),
 ('phi4-mini', '0.103 [0.052, 0.164]', '0.495 [0.424, 0.565]', '0.075 [0.040, 0.115]'),
 ('mistral:7b', 'cannot tell (rule-dependent)', 'rule-dependent, not checked', '0.217 [0.162, 0.278]'),
 ('llama3.1:8b', 'cannot tell (rule-dependent)', 'rule-dependent, not checked', '0.150 [0.105, 0.200]'),
 ('qwen3:4b', '0.388 [0.302, 0.474]', '0.049 [0.022, 0.082]', 'not scored (no answer field)')]

import json as _json
R2 = _json.load(open(B + 'iris_index/matrix/matrix_v2_results_v2.json'))
ORDER2 = ['phi4-mini', 'mistral_7b', 'falcon3_3b', 'smollm2_1.7b', 'llama3.1_8b', 'gemma3_4b', 'olmo2_7b', 'granite3.3_2b', 'deepseek-r1_1.5b', 'qwen3_4b']
NAME2 = {'phi4-mini': 'phi4-mini', 'mistral_7b': 'mistral:7b', 'falcon3_3b': 'falcon3:3b', 'smollm2_1.7b': 'smollm2:1.7b', 'llama3.1_8b': 'llama3.1:8b',
         'gemma3_4b': 'gemma3:4b', 'olmo2_7b': 'olmo2:7b', 'granite3.3_2b': 'granite3.3:2b', 'deepseek-r1_1.5b': 'deepseek-r1:1.5b', 'qwen3_4b': 'qwen3:4b'}
pc_ = lambda v: f'{100*v[0]:.1f}% [{100*v[1]:.1f}, {100*v[2]:.1f}]'
pt_ = lambda v: f'{100*v[0]:+.1f} points [{100*v[1]:+.1f}, {100*v[2]:+.1f}]'
def _cell(v, key, fmt):
    o = v['outcomes'].get(key, 'ABOVE')
    if o.startswith('CANNOT_TELL'):
        why = 'replies cut off' if 'truncated' in o else 'failed the first-option check'
        return f'<span class="by">cannot tell ({why})</span>'
    return fmt(v[key])
def wilson_(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return max(0, c - h), min(1, c + h)
CT_ = lambda why: f'<span class="by">cannot tell ({why})</span>'
def _repeat(v):   # 30 Oct 2026 (D-6): the exact-repeat check is a count with a Wilson interval, not a bootstrap of an all-zero sample
    n = v['copy_disagree'][3]; k = round(v['copy_disagree'][0] * n); lo, hi = wilson_(k, n)
    return f'{100*k/n:.1f}% [{100*lo:.1f}, {100*hi:.1f}]<span class="by"> {k} of {n}</span>'
def _fmt_B(v):   # 30 Oct 2026 (D-5): the reworded-prompt rate rests on the items readable in the original, its repeat and the reworded format; more than 10% dropped is cannot tell
    n = v['mcq4_B_flip_minus_floor'][3]
    if (200 - n) / 200 > 0.10: return CT_(f'{n} of 200 items readable in the reworded format')
    return pc_(v['mcq4_B_flip_minus_floor']) + f'<span class="by"> {n} of 200 items</span>'
HEAD2 = []
for m in ORDER2:
    v = R2[m]; trunc = 'truncated' in ' '.join(v['outcomes'].values())
    score = CT_('replies cut off') if trunc else f'{100*v["acc_A"][0]:.1f}%'
    ro = v['outcomes']['mcq4_rev_flip_minus_floor']
    chg = CT_('replies cut off') if trunc else (CT_('failed the first-option check') if ro.startswith('CANNOT') else pt_(v['mcq4_rev_acc_change']))
    HEAD2.append((f'<a href="/iris/runs/model-{m.replace("_", "-")}.zip">{NAME2[m]}</a>', score, chg, _cell(v, 'mcq4_rev_flip_minus_floor', pc_), CT_('replies cut off') if trunc else _fmt_B(v),
                  CT_('replies cut off') if trunc else _repeat(v)))
HEAD_INTRO = ('<p>A published evaluation reports one score per model. We ran ten open-weight models on 200 four-option questions from the Jev-ToM release of public theory-of-mind benchmarks and changed one thing at a time. '
              'The models ran in Ollama on our own Mac server at temperature 0 with a fixed seed (20261025), a 4,096-token context and a 500-token reply limit. The prompt asks for a JSON answer and the server&rsquo;s JSON mode was not used.</p>')
HEAD_NOTE = ('<p class="by">Score on the original order is the share of correct answers among the replies we could read. Score change is the reversed-order score minus the original. '
             'Answers that changed counts the items whose answer differs between two runs, minus the same count for an exact repeat of the original. The exact repeat column is a determinism check and not a noise floor, because the run is greedy with a fixed seed. '
             'For the reworded prompt the story, question and options are printed without labels and the reply is asked for as a letter only, so the format changes along with the wording. '
             'Under each of those rates is the number of the 200 items on which the original reply, its exact repeat and the reworded reply could all be read. '
             'Cannot tell means the cell is not read. Order cells are not read when the replies hit our length limit, or when the model did not reliably pick the option listed first when told to (at least 80% of 40 check items, in both orders), because then an order effect cannot be separated from guessing. '
             'Reworded cells are not read when more than 10% of the 200 items could not be read. '
             'Intervals are 95%, percentile bootstrap over items with 2,000 draws, except the exact repeat column, which uses the Wilson method. All raw replies are in the data below.</p>')
PERSONA_NOTE = ('<p class="by">Five of the ten models are shown and the other five are in the data. Over-attribution and false &ldquo;none&rdquo; come from NepPlural, 300 comments of which 116 have no persona and 184 have one. '
                'A reply counts as &ldquo;none&rdquo; when it sets the no-persona flag, a rule we stated after we had seen the replies. The gemma3:4b rate may be driven by our prompt or format, and we report it as measured. '
                'Among the five not shown, falcon3:3b has a higher false &ldquo;none&rdquo; rate than any model above, and smollm2:1.7b and olmo2:7b have higher over-attribution rates than any model above. '
                'The last column is a different task, two-option Jev-ToM items, where an order effect cannot be separated from a preference for one letter. For gemma3:4b, mistral:7b and phi4-mini the flips landed on one preferred letter. It is not the same measure as the four-option table above.</p>')

def table(head, rows, cls='mtx'):
    return (f'<div class="scroll"><table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')

# IRIS Key (25 Oct, his word: an index of what moves a language-model score besides the model, with the models and the articles it touches)
KEY = [
 ('L1', 'Option order', 'The answer changes when only the order of the options changes.',
  'falcon3:3b 42.5%, mistral:7b 27.3%, phi4-mini 27.8%, smollm2:1.7b 50.0% of answers change with the options reversed, net of the exact repeat (our setup, four-option questions). GPT-4.1, Claude Sonnet 4.5 and Gemini 2.5 Flash flip the verdict on 31.0%, 31.3% and 30.9% of prompts when the two answers swap position. That is a different measure, taken from an earlier experiment in the judge calls released with arXiv 2610.30512, run once per judge with no repeat floor (<a href="/iris/runs/frontier.zip">our recount</a>). The pinned October GPT-4.1 runs are the only ones with a repeat floor. Their flip is 12.5 points [8.0, 16.7] above it.',
  ['2610.30512']),
 ('L2', 'Prompt wording', 'The answer changes when only the wording or format of the prompt changes.',
  'With the answer format changed (the story, question and options without labels, and a reply of the letter only): gemma3:4b 11.3%, llama3.1:8b 12.0%, mistral:7b 13.1% and olmo2:7b 20.8% of answers change, net of the exact repeat (our setup, four-option questions). For falcon3:3b, smollm2:1.7b, granite3.3:2b and phi4-mini more than 10% of the 200 items could not be read in the new format, so those cells are cannot tell.',
  ['2610.30512']),
 ('L3', 'Repeat spread', 'The same setup run again, with another seed, or on another GPU or host gives different answers.',
  'Our setup, on our Mac server: an exact repeat gave a different answer on none of the 173 to 200 readable items for seven of the eight models read and on 1 of 195 for falcon3:3b. This is a determinism check, not a noise floor. Mamba-2.8B with the same seed on a different GPU and host: 76 of 8,000 question-position cells (0.95%) change, A40 against A10G (from the files released with arXiv 2610.31135).',
  ['2610.30512', '2610.31135', '2610.25626']),
 ('L4', 'Length limit', 'Replies are cut off by the length setting before an answer is given.',
  'deepseek-r1:1.5b 108 of 200 and qwen3:4b 191 of 200 replies hit our length limit, so their cells are not read.', []),
 ('L5', 'Serving backend', 'Outcomes differ between reruns of the same model name, and differ more on prompts where the provider&rsquo;s reported serving backend changed between the runs.',
  'GPT-4.1 as judge: the outcome changed on 27.3% of prompts where the reported serving backend changed between two runs and 17.5% where it did not, +9.8 points [+2.1, +17.6], one run pair. This splits prompts by a reported fingerprint and does not name a cause. Prompts with a changed backend sat somewhat nearer the decision boundary, and within margin bands (defined after the data) the gap is +8.0 points [+0.7, +15.3] (from the files released with arXiv 2610.30512).',
  ['2610.30512']),
 ('L6', 'Answer reading rule', 'The score depends on the rule used to read the answer out of the reply.',
  'F1 moves 6.13 points [4.43, 7.83] on the adversarial split, 5.37 on popular and 3.15 on random depending on which yes or no tokens are read. This is one model, LLaVA-1.5-7B at 4-bit precision, so we cannot say how much of any reported gain a matched evaluation would keep (from the files released with arXiv 2610.25964). On arXiv 2610.17203, our planned rule scores a judge by the share of its 16 picks per item. Under it the GPT-5.6-Sol judge scores 72.9 against 74.5 printed. The printed 74.5 rebuilds exactly only under a rule found after the data, which scores the judge by its more-picked answer.', ['2610.25964', '2610.17203']),
 ('L7', 'Model as reference', 'A model&rsquo;s output is the reference or the judge the results are scored against.',
  'The GPT labeller\'s gold labels, once reviewed, give 0.960 accuracy and put it ahead of every trained classifier by 0.115 to 0.145. The gold was built by reviewing that labeller\'s output, so the lead cannot be separated from anchoring (arXiv 2610.25159). Paired on items decisive for both, the Gemini 3.1 Pro judge agrees with the reader majority 0.657 [0.486, 0.800] of the time on G1 against G2, consistent with chance, and 0.839 [0.710, 0.968] on G1 against G0, above chance (arXiv 2610.21468).', ['2610.25159', '2610.21468', '2610.17203']),
 ('L8', 'Batching', 'Several items go into one call, and the answers differ from one item per call.',
  'Labelling 4 or 8 records per call agrees with single-record labels 0.02 to 0.03 less than two single-record runs agree with each other (from the files released with arXiv 2610.24999).', ['2610.24999', '2610.15732']),
 ('L9', 'Answer options offered', 'Adding or removing a &ldquo;none&rdquo; or abstain option changes the score.',
  'Allowing a &ldquo;none&rdquo; answer raises macro-F1 by +0.21 for GPT, +0.27 for Gemini and +0.20 for Claude (from the files released with arXiv 2610.15732). Our setup, with a none option offered: gemma3:4b gives a false &ldquo;none&rdquo; on 0.755 [0.696, 0.815] of persona items. We counted a reply as none by a rule stated after we had seen the replies, and our prompt or format may drive this rate.', ['2610.15732']),
]
ART_CODES = {}
for c_, *_x, arts in KEY:
    for a_ in arts: ART_CODES.setdefault(a_, []).append(c_)
codes_html = lambda ep: ' '.join(f'<a class="code" href="/iris/key#{c}">{c}</a>' for c in ART_CODES.get(ep, [])) or '&mdash;'


SHOW = {  # study -> (also in their released files, what it shows about the model, printed numbers rebuild)
 '2610.30512': ('17,000 judge calls from repeat runs, each with the reported serving backend', 'The same pinned GPT-4.1 judge changed outcomes on 27.3% of prompts where the reported serving backend changed and 17.5% where it did not (+9.8 points [+2.1, +17.6]). This splits prompts by a reported fingerprint and does not name a cause. Prompts with a changed backend sat somewhat nearer the decision boundary, and within margin bands (defined after the data) the gap is +8.0 points [+0.7, +15.3]. In an earlier experiment, run once per judge with no repeat floor, GPT-4.1, Claude Sonnet 4.5 and Gemini 2.5 Flash flip about 3 verdicts in 10 when the two answers swap position.', 'Printed numbers rebuild'),
 '2610.25964': ('Per-question token outputs for 9,000 questions', 'LLaVA-1.5-7B at 4-bit precision scores differently depending on which yes or no tokens are read: F1 moves 6.13 points [4.43, 7.83] on the adversarial split, 5.37 on popular and 3.15 on random. The authors say the shift exceeds the adversarial gain reported by five of the six papers they surveyed. Against our interval four of those six gains lie below the lower bound, one inside and one above, and the six carry no widths. The paper says the comparison stays unresolved until readout and precision are matched.', 'Printed numbers rebuild'),
 '2610.31256': ('Per-item predictions for every model run', 'Every model gains from 5-shot prompting on the same items: +7.01 [+5.06, +9.10] to +17.74 [+12.92, +22.82] points.', 'EM rebuilds. F1 on 18 of 22, the other 4 within 0.02'),
 '2610.31135': ('Every record with its run id and the GPU used', 'Same model and seed: 8,000 of 8,000 question-position cells identical on the same host. On a different GPU and host, 76 of 8,000 cells (0.95%) change, A40 against A10G. The primacy gap moves by +0.0019 [-0.0050, +0.0088], consistent with zero.', 'Printed numbers rebuild'),
 '2610.25159': ('The GPT labeller&rsquo;s silver labels and the per-item predictions on the gold set', 'The GPT labeller the gold labels were reviewed from scores 0.960 accuracy on that gold, ahead of every trained classifier by 0.115 to 0.145. The gold was built by reviewing this labeller&rsquo;s output, so the lead cannot be separated from anchoring. The labeller is not in the paper&rsquo;s results table.', 'Printed numbers rebuild'),
 '2610.15732': ('Per-comment outputs for the forced and abstain runs', 'Allowing a &ldquo;none&rdquo; answer raises macro-F1 by +0.21 for GPT, +0.27 for Gemini and +0.20 for Claude. With it allowed, Gemini is ahead of GPT by +0.052 [+0.011, +0.096] and of Claude by +0.077 [+0.036, +0.119].', 'Printed numbers rebuild'),
 '2610.18610': ('Per-question predictions for every model', 'The first-place lead holds: +1.59 [+0.25, +2.89] points over GPT-3.5 and +2.36 [+0.98, +3.75] over GPT-5.6-Luna.', 'Printed numbers rebuild'),
 '2610.21468': ('Item-level judge verdicts, reader decisions and reader retests', 'The Gemini 3.1 Pro judge agrees with the reader majority 0.657 [0.486, 0.800] of the time on G1 against G2, consistent with chance. On G1 against G0 it agrees 0.839 [0.710, 0.968] of the time, above chance. Both are paired on items decisive for both, 35 and 31 items. Readers agree with themselves 0.930.', 'Printed numbers rebuild'),
 '2610.17203': ('Every judge pick and the author labels', 'Under our planned scoring rule, which scores a judge by the share of its 16 picks per item, the GPT-5.6-Sol judge scores 72.9 against 74.5 printed. The printed 74.5 rebuilds exactly only under a rule found after the data, which scores the judge by its more-picked answer.', 'Judge scores rebuild only under a rule found after the data (74.5 exactly)'),
 '2610.25626': ('Per-run accuracies for three seeds per setting', 'With seeds as the unit, MapSteal&rsquo;s lead over the best other method resolves in 2 of 18 settings, uncorrected for 18 tests, is consistent with zero in 15 and is behind in 1. The comparison is a Welch interval on three seeds against three, and the two lower bounds are +0.03 and +0.06 points. The authors&rsquo; 12 of 18 is a correct count of means.', 'Printed numbers rebuild. Answer keys not released'),
 '2610.24999': ('Labels from single-record and batched runs (4 and 8 records per call)', 'Labelling 4 or 8 records per call agrees with single-record labels 0.02 to 0.03 less than two single-record runs agree with each other.', 'Printed numbers rebuild'),
}

book_rows = []
for k, t in BOOK:
    title, author, ep = ref(k); first = author.split(' and ')[0].split(',')[0].strip(); etal = ' et al.' if ' and ' in author else ''
    al, sh, rb = SHOW[ep]
    book_rows.append((f'{E(title)}<br><span class="by">{rb} &middot; <a href="https://arxiv.org/abs/{ep}">arXiv {ep}</a> &middot; <a href="/iris/runs/study-{ep}.zip">our data</a></span>', al, sh, codes_html(ep)))
PUB = 'https://heuremen.org/a-pinned-model-is-not-a-stable-tool.pdf'
body = f'''
<section><h2 id="headline">For the models that passed our option-order check, reversing the order of the options changes 27% to 50% of the answers. Their score change reads cannot tell: every interval contains zero and reaches 8 to 11 points on one side.</h2>{HEAD_INTRO}{table(["Model", "Score on the original order", "Score change, options reversed", "Answers that changed, options reversed", "Answers that changed, answer format changed", "Answers that changed, exact repeat (determinism check)"], HEAD2, "mtx wide")}{HEAD_NOTE}
<h2>Among the models shown, given a none option, gemma3:4b misses three in four real personas and qwen3:4b tags two in five comments that have none.</h2>{table(["Model", "Over-attribution (no-persona items)", "False &ldquo;none&rdquo; (persona items)", "Two-option flips under option reversal, including letter fallback"], MODELS)}{PERSONA_NOTE}</section>
<section><h2>What the Papers’ Own Released Data Shows About the Models</h2>{table(["Study", "Also in their released files", "What it shows about the model", "IRIS codes"], book_rows)}</section>
'''
EXTRA = open(B + 'oy_index/matrix_page/oy_body.html').read().split('</style>')[0] + '.mtx .by{font-weight:400;color:var(--mid);font-size:14px}</style>'
out = B + 'iris_index/matrix_page/'
open(out + 'iris_body.html', 'w').write(EXTRA + '\n' + body)
KEYBODY = ('<p class="crumb"><a href="/iris">IRIS</a> &middot; <a href="/iris/list">The List</a></p><section><h2>IRIS codes: what moves a language-model result besides the model</h2><p class="by">Intervals are 95%, by percentile bootstrap over items unless the row says otherwise.</p>'
    + table(['Code', 'Name', 'What happens', 'Measured', 'Indexed studies where it touches the data'],
            [(f'<span id="{c}">{c}</span>', n, d, m or '&mdash;', ', '.join(f'<a href="https://arxiv.org/abs/{a}">arXiv {a}</a>' for a in arts) or '&mdash;') for c, n, d, m, arts in KEY]) + '</section>')
open(out + 'iris_key_body.html', 'w').write(KEYBODY)
os.makedirs(out + 'staged', exist_ok=True)
doc = bs.page('/iris', 'Recount Matrix: Language Models | IRIS | Indahl', 'Recount Matrix: Language Models. Published language-model evaluations recounted from their own released files, with a source for every row.',
              EXTRA + body, bs.hero('IRIS', 'Recount Matrix: Language Models', '')).replace('href="/style.css"', 'href="style.css"')
open(out + 'staged/language-matrix.html', 'w').write(doc); open(out + 'staged/style.css', 'w').write(bs.CSS)
print('ok', len(book_rows), 'papers')
