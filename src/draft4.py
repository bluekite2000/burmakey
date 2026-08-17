"""
Draft 4: same spelling as draft 3 — the speed now comes from the ENGINE.

Three additions, all standard in modern keyboards, none present in my
earlier simulations:
  1. zero-keystroke suggestions: the bar is populated BEFORE you type,
     so a predicted word costs 1 tap total
  2. recency: words you've used in this conversation rank higher
  3. bigram: words that followed your previous word rank higher

The engine starts COLD (no pretraining on the test conversation) and
learns online as the conversation proceeds — exactly what a personal
keyboard does. Both keyboards get the identical engine.
"""
import json, collections
import optimise3 as O3
from typist import lex, FREQ, karaoke

enc3 = O3.make_encoder(json.load(open("cfg3.json")))
convo = json.load(open("convo.json"))
stream = [w for r in convo["rows"] for w, _ in r["words"]]

SHORTLIST = 3

def simulate(encoder, engine="smart"):
    spell = {w: encoder(lex[w]["syl"]) for w in lex}
    by_prefix = collections.defaultdict(list)
    for w, s in spell.items():
        by_prefix[""].append(w)
        for i in range(1, len(s) + 1):
            by_prefix[s[:i]].append(w)

    recency = collections.Counter()
    bigram  = collections.defaultdict(collections.Counter)
    prev = None
    groups = collections.Counter(spell.values())

    def score(w):
        s = FREQ[w]
        if engine == "smart":
            s += 10 * recency[w]
            if prev is not None:
                s += 100 * bigram[prev][w]
        return s

    taps = keys = zero = amb = 0
    for w in stream:
        s = spell[w]
        found = None
        for k in range(0, len(s) + 1):
            cands = sorted(by_prefix[s[:k]], key=score, reverse=True)[:SHORTLIST]
            if w in cands:
                found = k
                break
        k = len(s) if found is None else found
        taps += k + 1
        keys += k
        if found == 0: zero += 1
        if groups[s] > 1: amb += 1
        if engine == "smart":
            recency[w] += 1
            if prev is not None: bigram[prev][w] += 1
        prev = w
    n = len(stream)
    return {"taps": taps, "tpw": taps / n, "zero": 100 * zero / n,
            "amb": 100 * amb / n}

print("=" * 70)
print(f"SAME 40-MESSAGE CONVERSATION ({len(stream)} words), engine upgraded")
print("=" * 70)
rows = [
 ("karaoke, typed out (today)",      karaoke, "dumb-notype"),
 ("karaoke + frequency predictor",   karaoke, "freq"),
 ("karaoke + LEARNING engine",       karaoke, "smart"),
 ("draft 3 + frequency predictor",   enc3,    "freq"),
 ("DRAFT 4 = draft 3 + LEARNING",    enc3,    "smart"),
]
print(f"{'':34}{'taps':>7}{'taps/word':>11}{'0-key hits':>12}{'ambig':>8}")
out = {}
for name, enc, eng in rows:
    if eng == "dumb-notype":
        spell = {w: enc(lex[w]["syl"]) for w in lex}
        g = collections.Counter(spell.values())
        taps = sum(len(spell[w]) + 1 for w in stream)
        r = {"taps": taps, "tpw": taps/len(stream), "zero": 0.0,
             "amb": 100*sum(1 for w in stream if g[spell[w]]>1)/len(stream)}
    else:
        r = simulate(enc, "smart" if eng == "smart" else "freq")
    out[name] = r
    print(f"{name:34}{r['taps']:>7,}{r['tpw']:>11.2f}{r['zero']:>11.1f}%"
          f"{r['amb']:>7.0f}%")

base = out["karaoke, typed out (today)"]
d4   = out["DRAFT 4 = draft 3 + LEARNING"]
kk_s = out["karaoke + LEARNING engine"]
print(f"\ndraft 4 vs today's reality : {d4['taps']-base['taps']:+,} taps "
      f"({100*(d4['taps']-base['taps'])/base['taps']:+.1f}%)")
print(f"draft 4 vs karaoke w/ SAME engine: {d4['taps']-kk_s['taps']:+,} taps "
      f"({100*(d4['taps']-kk_s['taps'])/kk_s['taps']:+.1f}%)")
