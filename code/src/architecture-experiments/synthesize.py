#!/usr/bin/env python3
"""Step 3: synthesis. Loads the original 6-prompt confidence_signals.jsonl plus
the 25-prompt batch2 raw outputs from all three architectures (transformer,
diffusion/LLaDA, rwkv), merges them into one 31-prompt dataset, and computes
real agreement/disagreement metrics between architectures -- not vibes,
actual counts and correlations. Pure stdlib, no numpy/torch dependency, so it
runs under plain system python3.

Writes:
  confidence_signals_full.jsonl  -- the merged 31-prompt dataset
  synthesis_metrics.json         -- all computed numbers, for the findings doc
"""
import json, re, math, pathlib, statistics as st

FORGE = pathlib.Path.home() / 'bones-forge' / 'architecture-experiments'

# ---------------------------------------------------------------- text utils
STOPWORDS = set("""a an the is are was were be been being to of in on at for with as by from that this it its
it's and or but if then so than too very can could would should will shall may might must not no nor
i you he she we they them his her their our your my me him us do does did done have has had having
about into over under again further here there when where why how all any both each few more most other
some such only own same""".split())

def normalize_words(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [w for w in text.split() if w and w not in STOPWORDS and len(w) > 1]

def jaccard(a_text, b_text):
    a, b = set(normalize_words(a_text)), set(normalize_words(b_text))
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

HEDGE_PHRASES = [
    "it depends", "on one hand", "on the other hand", "arguably", "subjective",
    "no single", "not a simple", "some argue", "some people", "some would",
    "there is no", "cannot say for certain", "i cannot know",
    "i don't know", "i do not know", "i'm not sure", "i am not sure",
    "as an ai", "i don't have", "i do not have", "uncertain", "debatable",
    "depends on", "it's complicated", "it is complicated", "there's no easy",
    "no easy answer", "matter of perspective", "matter of opinion", "varies",
    "case by case", "context matters", "hard to say", "difficult to say",
    "there is no single", "not necessarily", "in some cases", "in other cases",
]

def hedge_count(text):
    t = (text or "").lower()
    return sum(t.count(p) for p in HEDGE_PHRASES)

def hedge_rate_per_100w(text):
    words = normalize_words(text)
    n = max(1, len(words))
    return 100.0 * hedge_count(text) / n

# ground truth keyword checks for prompts where correctness is objectively verifiable
FACTUAL_KEYWORDS = {
    "What is the boiling point of water at sea level in degrees Celsius?": ["100"],
    "Who wrote the novel Moby-Dick?": ["melville"],
    "What is the chemical symbol for gold?": [" au", "au ", "au.", "au,", "'au'", '"au"'],
    "In what year did World War II end?": ["1945"],
    "What is the capital of Australia?": ["canberra"],
    "How many continents are there on Earth?": ["seven", " 7 ", " 7,", " 7.", " 7\n"],
    "What is the speed of light in a vacuum, in meters per second (approximately)?": [
        "299,792,458", "299792458", "299,792", "3 x 10", "3×10", "3.0 x 10", "300,000,000", "300 million", "3e8",
    ],
}

def factual_correct(prompt, text):
    keys = FACTUAL_KEYWORDS.get(prompt)
    if not keys:
        return None
    low = " " + (text or "").lower() + " "
    return any(k.lower() in low for k in keys)

def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None, len(pairs)
    xs2, ys2 = zip(*pairs)
    n = len(xs2)
    mx, my = st.mean(xs2), st.mean(ys2)
    num = sum((x - mx) * (y - my) for x, y in zip(xs2, ys2))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs2))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys2))
    if denx == 0 or deny == 0:
        return None, n
    return num / (denx * deny), n

# ---------------------------------------------------------------- loading
def load_original():
    entries = []
    with open(FORGE / 'confidence_signals.jsonl') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

def load_batch2():
    t = json.load(open(FORGE / 'transformer_signals_raw_batch2.json'))['results']
    l = json.load(open(FORGE / 'llada_signals_raw_batch2.json'))['results']
    r = json.load(open(FORGE / 'rwkv_signals_raw_batch2.json'))['results']
    by_t = {x['prompt']: x for x in t}
    by_l = {x['prompt']: x for x in l}
    by_r = {x['prompt']: x for x in r}
    entries = []
    for prompt, tt in by_t.items():
        ll = by_l.get(prompt)
        rr = by_r.get(prompt)
        entries.append({
            "prompt": prompt,
            "category": tt["category"],
            "transformer": tt,
            "diffusion": ll,
            "rwkv": rr,
        })
    return entries

def main():
    original = load_original()
    batch2 = load_batch2()
    all_entries = original + batch2

    full_path = FORGE / 'confidence_signals_full.jsonl'
    with open(full_path, 'w') as f:
        for e in all_entries:
            f.write(json.dumps(e) + "\n")
    print(f"Wrote {full_path}  ({len(all_entries)} prompts: {len(original)} original + {len(batch2)} batch2)")

    # ---------------- per-entry metrics
    rows = []
    for e in all_entries:
        t_text = e['transformer'].get('output_text', '')
        d_text = e['diffusion'].get('output_text', '') if e.get('diffusion') else ''
        r_text = e['rwkv'].get('output_text', '') if e.get('rwkv') else ''
        row = {
            "prompt": e['prompt'],
            "category": e['category'],
            "jaccard_t_d": jaccard(t_text, d_text),
            "jaccard_t_r": jaccard(t_text, r_text),
            "jaccard_d_r": jaccard(d_text, r_text),
            "hedge_t": hedge_rate_per_100w(t_text),
            "hedge_d": hedge_rate_per_100w(d_text),
            "hedge_r": hedge_rate_per_100w(r_text),
            "transformer_perplexity": e['transformer'].get('perplexity'),
            "transformer_mean_entropy": e['transformer'].get('mean_entropy_nats'),
            "diffusion_mean_confidence": e['diffusion'].get('mean_confidence_overall') if e.get('diffusion') else None,
            "rwkv_wkv_delta_variance": e['rwkv'].get('wkv_state_delta_variance') if e.get('rwkv') else None,
            "factual_correct_t": factual_correct(e['prompt'], t_text),
            "factual_correct_d": factual_correct(e['prompt'], d_text),
            "factual_correct_r": factual_correct(e['prompt'], r_text),
        }
        rows.append(row)

    # ---------------- RWKV coherence filter (confound flag, not exclusion of data --
    # just a separately-reported subset since RWKV-Raven-1.5B is ~5-9x smaller than
    # the other two models)
    rwkv_incoherent = [r for r in rows if r['jaccard_t_r'] < 0.05 and r['jaccard_d_r'] < 0.05]

    # ---------------- category grouping: closed/verifiable vs open-ended
    CLOSED = {"factual", "technical"}
    OPEN = {"ambiguous", "ethical", "self-referential"}
    closed_rows = [r for r in rows if r['category'] in CLOSED]
    open_rows = [r for r in rows if r['category'] in OPEN]

    def summ(vals):
        vals = [v for v in vals if v is not None]
        if not vals:
            return {"n": 0, "mean": None, "stdev": None}
        return {"n": len(vals), "mean": st.mean(vals), "stdev": st.pstdev(vals) if len(vals) > 1 else 0.0}

    metrics = {}
    metrics["n_total"] = len(rows)
    metrics["n_original"] = len(original)
    metrics["n_batch2"] = len(batch2)
    metrics["categories"] = sorted(set(r['category'] for r in rows))

    # per-category agreement (transformer vs diffusion -- the two capable models)
    by_cat = {}
    for cat in metrics["categories"]:
        cat_rows = [r for r in rows if r['category'] == cat]
        by_cat[cat] = {
            "n": len(cat_rows),
            "jaccard_t_d": summ([r['jaccard_t_d'] for r in cat_rows]),
            "jaccard_t_r": summ([r['jaccard_t_r'] for r in cat_rows]),
            "jaccard_d_r": summ([r['jaccard_d_r'] for r in cat_rows]),
            "hedge_t": summ([r['hedge_t'] for r in cat_rows]),
            "hedge_d": summ([r['hedge_d'] for r in cat_rows]),
            "hedge_r": summ([r['hedge_r'] for r in cat_rows]),
            "transformer_perplexity": summ([r['transformer_perplexity'] for r in cat_rows]),
            "transformer_mean_entropy": summ([r['transformer_mean_entropy'] for r in cat_rows]),
            "diffusion_mean_confidence": summ([r['diffusion_mean_confidence'] for r in cat_rows]),
            "rwkv_wkv_delta_variance": summ([r['rwkv_wkv_delta_variance'] for r in cat_rows]),
        }
    metrics["by_category"] = by_cat

    metrics["closed_vs_open"] = {
        "closed_categories": sorted(CLOSED),
        "open_categories": sorted(OPEN),
        "closed_jaccard_t_d": summ([r['jaccard_t_d'] for r in closed_rows]),
        "open_jaccard_t_d": summ([r['jaccard_t_d'] for r in open_rows]),
        "closed_hedge_t": summ([r['hedge_t'] for r in closed_rows]),
        "open_hedge_t": summ([r['hedge_t'] for r in open_rows]),
        "closed_hedge_d": summ([r['hedge_d'] for r in closed_rows]),
        "open_hedge_d": summ([r['hedge_d'] for r in open_rows]),
        "closed_hedge_r": summ([r['hedge_r'] for r in closed_rows]),
        "open_hedge_r": summ([r['hedge_r'] for r in open_rows]),
        "closed_transformer_perplexity": summ([r['transformer_perplexity'] for r in closed_rows]),
        "open_transformer_perplexity": summ([r['transformer_perplexity'] for r in open_rows]),
        "closed_diffusion_mean_confidence": summ([r['diffusion_mean_confidence'] for r in closed_rows]),
        "open_diffusion_mean_confidence": summ([r['diffusion_mean_confidence'] for r in open_rows]),
    }

    # correlations across all 31 prompts: does an architecture's OWN uncertainty
    # signal predict cross-architecture disagreement (1 - jaccard_t_d)?
    disagreement_t_d = [1 - r['jaccard_t_d'] for r in rows]
    r_ppl, n1 = pearson([r['transformer_perplexity'] for r in rows], disagreement_t_d)
    r_ent, n2 = pearson([r['transformer_mean_entropy'] for r in rows], disagreement_t_d)
    r_dconf, n3 = pearson([r['diffusion_mean_confidence'] for r in rows], disagreement_t_d)
    r_rwkv_var, n4 = pearson([r['rwkv_wkv_delta_variance'] for r in rows], [1 - r['jaccard_d_r'] for r in rows])
    metrics["correlations"] = {
        "transformer_perplexity_vs_disagreement_t_d": {"r": r_ppl, "n": n1},
        "transformer_entropy_vs_disagreement_t_d": {"r": r_ent, "n": n2},
        "diffusion_confidence_vs_disagreement_t_d": {"r": r_dconf, "n": n3},
        "rwkv_state_delta_var_vs_disagreement_d_r": {"r": r_rwkv_var, "n": n4},
    }

    # calibration: on the 7 objectively-verifiable factual prompts, does each
    # architecture's own uncertainty signal predict its own correctness?
    factual_rows = [r for r in rows if r['factual_correct_t'] is not None]
    correct_t = [r for r in factual_rows if r['factual_correct_t']]
    wrong_t = [r for r in factual_rows if not r['factual_correct_t']]
    correct_d = [r for r in factual_rows if r['factual_correct_d']]
    wrong_d = [r for r in factual_rows if not r['factual_correct_d']]
    correct_r = [r for r in factual_rows if r['factual_correct_r']]
    wrong_r = [r for r in factual_rows if not r['factual_correct_r']]
    metrics["factual_calibration"] = {
        "n_factual_verifiable_prompts": len(factual_rows),
        "transformer_accuracy": len(correct_t) / len(factual_rows) if factual_rows else None,
        "transformer_perplexity_when_correct": summ([r['transformer_perplexity'] for r in correct_t]),
        "transformer_perplexity_when_wrong": summ([r['transformer_perplexity'] for r in wrong_t]),
        "diffusion_accuracy": len(correct_d) / len(factual_rows) if factual_rows else None,
        "diffusion_confidence_when_correct": summ([r['diffusion_mean_confidence'] for r in correct_d]),
        "diffusion_confidence_when_wrong": summ([r['diffusion_mean_confidence'] for r in wrong_d]),
        "rwkv_accuracy": len(correct_r) / len(factual_rows) if factual_rows else None,
    }

    metrics["rwkv_incoherence"] = {
        "n_incoherent_of_total": f"{len(rwkv_incoherent)}/{len(rows)}",
        "incoherent_prompts": [r['prompt'] for r in rwkv_incoherent],
        "note": "incoherent = jaccard(rwkv,transformer) < 0.05 AND jaccard(rwkv,diffusion) < 0.05 -- essentially no shared content words with either capable model. RWKV-Raven-1.5B is ~5-9x smaller than the other two models (1.5B vs 8B/14B), so this is flagged as a capability confound, not attributed to the recurrent architecture itself.",
    }

    metrics["all_rows"] = rows

    out_path = FORGE / 'synthesis_metrics.json'
    out_path.write_text(json.dumps(metrics, indent=2, default=str))
    print(f"Wrote {out_path}")

    # console summary
    print("\n=== closed (factual+technical) vs open (ambiguous+ethical+self-referential) ===")
    cvo = metrics["closed_vs_open"]
    print(f"transformer-diffusion Jaccard agreement: closed mean={cvo['closed_jaccard_t_d']['mean']:.4f} (n={cvo['closed_jaccard_t_d']['n']}) "
          f"vs open mean={cvo['open_jaccard_t_d']['mean']:.4f} (n={cvo['open_jaccard_t_d']['n']})")
    print(f"transformer perplexity: closed mean={cvo['closed_transformer_perplexity']['mean']:.4f} vs open mean={cvo['open_transformer_perplexity']['mean']:.4f}")
    print(f"diffusion mean_confidence: closed mean={cvo['closed_diffusion_mean_confidence']['mean']:.4f} vs open mean={cvo['open_diffusion_mean_confidence']['mean']:.4f}")
    print(f"hedge rate/100w -- transformer: closed={cvo['closed_hedge_t']['mean']:.3f} open={cvo['open_hedge_t']['mean']:.3f}")
    print(f"hedge rate/100w -- diffusion:   closed={cvo['closed_hedge_d']['mean']:.3f} open={cvo['open_hedge_d']['mean']:.3f}")
    print(f"hedge rate/100w -- rwkv:        closed={cvo['closed_hedge_r']['mean']:.3f} open={cvo['open_hedge_r']['mean']:.3f}")
    print("\n=== correlations (n=%d prompts) ===" % len(rows))
    for k, v in metrics["correlations"].items():
        print(f"  {k}: r={v['r']}, n={v['n']}")
    print("\n=== factual calibration (n=%d verifiable prompts) ===" % metrics["factual_calibration"]["n_factual_verifiable_prompts"])
    fc = metrics["factual_calibration"]
    print(f"  transformer accuracy={fc['transformer_accuracy']}, ppl correct={fc['transformer_perplexity_when_correct']}, ppl wrong={fc['transformer_perplexity_when_wrong']}")
    print(f"  diffusion accuracy={fc['diffusion_accuracy']}, conf correct={fc['diffusion_confidence_when_correct']}, conf wrong={fc['diffusion_confidence_when_wrong']}")
    print(f"  rwkv accuracy={fc['rwkv_accuracy']}")
    print(f"\n=== RWKV incoherence: {metrics['rwkv_incoherence']['n_incoherent_of_total']} ===")

if __name__ == '__main__':
    main()
