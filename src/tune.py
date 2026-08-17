"""Tune the two free engine parameters the earlier sims guessed at:
shortlist size and learning weights. Also price the attention cost of
bar-picking, which tap counts ignore."""
import json, random, collections, statistics
import optimise3 as O3
from typist import lex, FREQ, karaoke
import re

random.seed(42)
enc3 = O3.make_encoder(json.load(open("cfg3.json")))
kk_spell = {w: karaoke(lex[w]["syl"]) for w in lex}

# same long stream as sim_long (regenerate identically)
exec(open("sim_long.py").read().split("# ---------------- engines")[0]
     .split('TOPIC_VOCAB =')[0].replace('print(f"generated','pass #',1)
     if False else "")
# simpler: rebuild stream via the generator section of sim_long
import importlib.util
src = open("sim_long.py").read()
gen_src = src[:src.index("# ---------------- engines")]
ns = {}
exec(compile(gen_src, "gen", "exec"), ns)
stream = ns["stream"]
print(f"stream: {len(stream):,} words")

by_prefix = collections.defaultdict(list)
for w, s in kk_spell.items():
    by_prefix[""].append(w)
    for i in range(1, len(s)+1):
        by_prefix[s[:i]].append(w)
for p in by_prefix:
    by_prefix[p] = sorted(by_prefix[p], key=lambda w: -FREQ[w])[:60]

def run(shortlist, w_rec, w_big):
    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    prev = None
    taps = bar = 0
    def score(w):
        return FREQ[w] + w_rec*recency[w] + (w_big*bigram[prev][w] if prev else 0)
    for w in stream:
        s = kk_spell[w]
        found = pick1 = None
        for k in range(0, len(s)+1):
            pool = by_prefix[s[:k]]
            if recency:
                pfx = s[:k]
                pool = set(pool) | {x for x in recency if kk_spell[x].startswith(pfx)}
            cs = sorted(pool, key=score, reverse=True)[:shortlist]
            if w in cs:
                found, pick1 = k, cs[0] == w
                break
        k = len(s) if found is None else found
        taps += k + 1
        if not pick1: bar += 1
        recency[w] += 1
        if prev is not None: bigram[prev][w] += 1
        prev = w
    n = len(stream)
    return taps/n, 100*bar/n

print(f"\n{'config':38}{'taps/word':>10}{'bar-pick':>10}{'attn cost*':>11}")
print("-"*70)
base_today = statistics.mean(len(kk_spell[w])+1 for w in stream)
print(f"{'today (typed out, no engine)':38}{base_today:>10.2f}{'0%':>10}{base_today:>11.2f}")
results = {}
for name, sl, wr, wb in [
    ("current engine (shortlist 3)",       3, 10, 100),
    ("shortlist 5",                        5, 10, 100),
    ("shortlist 5 + heavier learning",     5, 50, 300),
    ("shortlist 3 + heavier learning",     3, 50, 300),
]:
    t, b = run(sl, wr, wb)
    # attention cost: a bar-pick costs ~0.5 taps-equivalent of scanning
    attn = t + 0.005*b
    results[name] = (t, b, attn)
    print(f"{name:38}{t:>10.2f}{b:>9.1f}%{attn:>11.2f}")
print("\n* attention cost = taps/word + 0.5 tap-equivalents per bar-pick")
best = min(results.items(), key=lambda kv: kv[1][2])
print(f"best: {best[0]}  ({100*(1-best[1][0]/base_today):.0f}% fewer taps than today)")
