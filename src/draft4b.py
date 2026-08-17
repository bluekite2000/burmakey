"""
Draft 4 final: INPUT = toneless karaoke letters (fast, familiar).
              ENGINE = learning predictor picks the intended word.
              OUTPUT = draft 3 spelling (or Lao script) — unambiguous.

You type like you already do; the keyboard writes the clear form.
Also measures the new failure mode this creates: how often the top
suggestion is a WRONG homophone (user must glance at the bar), and how
often the intended word isn't findable by prefix at all.
"""
import json, collections
import optimise3 as O3
from typist import lex, FREQ, karaoke

enc3 = O3.make_encoder(json.load(open("cfg3.json")))
stream = [w for r in json.load(open("convo.json"))["rows"] for w, _ in r["words"]]
SHORTLIST = 3

def run(input_enc, output_enc, learning=True):
    ispell = {w: input_enc(lex[w]["syl"]) for w in lex}
    ospell = {w: output_enc(lex[w]["syl"]) for w in lex}
    by_prefix = collections.defaultdict(list)
    for w, s in ispell.items():
        by_prefix[""].append(w)
        for i in range(1, len(s) + 1):
            by_prefix[s[:i]].append(w)
    ogroups = collections.Counter(ospell.values())

    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    prev = None
    taps = zero = amb_out = bar_pick = fullword = 0

    def score(w):
        s = FREQ[w]
        if learning:
            s += 10 * recency[w] + (100 * bigram[prev][w] if prev else 0)
        return s

    for w in stream:
        s = ispell[w]
        found = pick1 = None
        for k in range(0, len(s) + 1):
            cands = sorted(by_prefix[s[:k]], key=score, reverse=True)[:SHORTLIST]
            if w in cands:
                found, pick1 = k, (cands[0] == w)
                break
        if found is None:
            k, pick1 = len(s), True
            fullword += 1
        else:
            k = found
        taps += k + 1
        if found == 0: zero += 1
        if not pick1: bar_pick += 1
        if ogroups[ospell[w]] > 1: amb_out += 1
        recency[w] += 1
        if prev is not None: bigram[prev][w] += 1
        prev = w
    n = len(stream)
    return dict(taps=taps, tpw=taps/n, zero=100*zero/n, amb=100*amb_out/n,
                barpick=100*bar_pick/n, full=100*fullword/n)

print("=" * 74)
print("DRAFT 4: type karaoke, engine disambiguates, output is unambiguous")
print("=" * 74)
rows = [
  ("karaoke typed out (today)",          None),
  ("draft 3 input, learning engine",     (enc3,    enc3)),
  ("DRAFT 4: karaoke in -> draft 3 out", (karaoke, enc3)),
]
print(f"{'':38}{'taps':>6}{'t/word':>8}{'0-key':>8}{'bar-pick':>9}{'amb out':>9}")
out = {}
for name, cfg in rows:
    if cfg is None:
        spell = {w: karaoke(lex[w]["syl"]) for w in lex}
        g = collections.Counter(spell.values())
        t = sum(len(spell[w]) + 1 for w in stream)
        r = dict(taps=t, tpw=t/len(stream), zero=0, barpick=0,
                 amb=100*sum(1 for w in stream if g[spell[w]]>1)/len(stream))
    else:
        r = run(*cfg)
    out[name] = r
    print(f"{name:38}{r['taps']:>6,}{r['tpw']:>8.2f}{r['zero']:>7.1f}%"
          f"{r['barpick']:>8.1f}%{r['amb']:>8.0f}%")

base, d4 = out["karaoke typed out (today)"], out["DRAFT 4: karaoke in -> draft 3 out"]
print(f"\nDRAFT 4 vs today : {d4['taps']-base['taps']:+,} taps "
      f"({100*(d4['taps']-base['taps'])/base['taps']:+.1f}%)  "
      f"ambiguity {base['amb']:.0f}% -> {d4['amb']:.0f}%")
print(f"cost of the trick: wrong top suggestion (must glance at bar) on "
      f"{d4['barpick']:.1f}% of words")
