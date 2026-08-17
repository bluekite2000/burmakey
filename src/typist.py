"""
Simulate a Lao person typing a message, on the old keyboard and the new one.

Differs from every earlier measurement here in one crucial way: real people
type common words over and over. A dictionary treats 'and' and 'palaeontology'
as equally likely. This weights by frequency.

FREQUENCY MODEL (stated, because it is an assumption, not data):
  tier 1  the 117-word Lao stopword list        -- the commonest words
  tier 2  words the POS tagger memorised         -- mid frequency
  tier 3  everything else, ordered short-first   -- Zipf's law of abbreviation
  weight = 1 / rank^0.95   (Zipf)
A real running-text corpus would replace this wholesale. It is the largest
remaining source of error in these numbers.
"""
import json, random, statistics, collections
import laonlp
from optimise import make_encoder, LEX

random.seed(7)
root = laonlp.__path__[0]

stop = [w.strip() for w in open(root + "/corpus/stopwords_lao.txt", encoding="utf-8")
        if w.strip() and not w.startswith("#")]
tagdict = list(json.load(open(root + "/corpus/ptagger_SeqLabeling_corpus.json"))["tagdict"])

lex = {e["lao"]: e for e in LEX}
rank, r = {}, 1
for w in stop:
    if w in lex and w not in rank: rank[w] = r; r += 1
for w in tagdict:
    if w in lex and w not in rank: rank[w] = r; r += 1
rest = sorted((w for w in lex if w not in rank),
              key=lambda w: (len(lex[w]["syl"]), len(w)))
for w in rest:
    rank[w] = r; r += 1

FREQ = {w: 1.0 / (k ** 0.95) for w, k in rank.items()}
print(f"vocabulary {len(FREQ):,}   tier1 {sum(1 for w in stop if w in lex)}"
      f"   tier2 {sum(1 for w in tagdict if w in lex and w not in stop):,}")

CFG_NEW = json.load(open("best_cfg.json"))
CFG_OLD = {"onset":"digraph","vowel":"digraph","length":"double",
           "lenmark":"h","unmarked":"mid","tonepos":"late"}


def karaoke(sylls):
    ON = {"x":"","kh":"kh","ng":"ng","ny":"ny","th":"th","ph":"ph","j":"j",
          "khw":"khw","kw":"kw"}
    V = {"i":"i","e":"e","E":"ae","M":"eu","V":"oe","a":"a","u":"u","o":"o",
         "O":"o","iM":"ia","MM":"uea","uM":"ua"}
    return "".join(ON.get(s["on"], s["on"]) + V[s["v"]] + s["fin"] for s in sylls)


def build(encoder):
    spell = {}
    by_prefix = collections.defaultdict(list)
    for w, e in lex.items():
        s = encoder(e["syl"])
        spell[w] = s
    for w, s in spell.items():
        for i in range(1, len(s) + 1):
            by_prefix[s[:i]].append(w)
    for p in by_prefix:
        by_prefix[p].sort(key=lambda w: -FREQ[w])
    return spell, by_prefix


def type_word(target, spell, by_prefix, shortlist=3):
    """Type until the target appears in the visible candidate list, then tap."""
    s = spell[target]
    for i in range(1, len(s) + 1):
        cands = by_prefix[s[:i]][:shortlist]
        if target in cands:
            return i + 1, cands[0] == target, i
    return len(s) + 1, True, len(s)


SYSTEMS = {
    "karaoke Lao (today)":      karaoke,
    "Aksoon Laatin draft 1":    make_encoder(CFG_OLD),
    "Aksoon Laatin draft 2":    make_encoder(CFG_NEW),
}

pop = list(FREQ)
wts = [FREQ[w] for w in pop]
stream = random.choices(pop, weights=wts, k=4000)

print(f"\nsimulating a {len(stream):,}-word message stream "
      f"(words drawn by frequency)\n")
print(f"{'':26}{'taps/word':>11}{'keys/word':>11}{'top pick wrong':>16}")
results = {}
for name, enc in SYSTEMS.items():
    spell, pref = build(enc)
    taps, wrong, keys = [], 0, []
    for w in stream:
        t, top_ok, k = type_word(w, spell, pref)
        taps.append(t); keys.append(k)
        if not top_ok: wrong += 1
    results[name] = (statistics.mean(taps), statistics.mean(keys),
                     100 * wrong / len(stream))
    print(f"{name:26}{results[name][0]:>11.2f}{results[name][1]:>11.2f}"
          f"{results[name][2]:>15.1f}%")

kk = results["karaoke Lao (today)"]
d2 = results["Aksoon Laatin draft 2"]
print(f"\ndraft 2 vs karaoke: {d2[0]-kk[0]:+.2f} taps/word "
      f"({100*(d2[0]-kk[0])/kk[0]:+.1f}%),  "
      f"wrong top pick {kk[2]:.1f}% -> {d2[2]:.1f}%")

print("\n" + "=" * 66)
print("A REAL MESSAGE, KEY BY KEY")
print("=" * 66)
msg = [w for w in random.choices(pop, weights=wts, k=60)
       if len(lex[w]["syl"]) <= 2 and lex[w]["g"]][:6]
for name in ["karaoke Lao (today)", "Aksoon Laatin draft 2"]:
    spell, pref = build(SYSTEMS[name])
    tot = 0
    print(f"\n{name}")
    for w in msg:
        t, ok, k = type_word(w, spell, pref)
        tot += t
        seen = spell[w][:k]
        print(f"   {lex[w]['g'][:26]:<27} type {seen:<9} ({k} keys) "
              f"+tap  {'' if ok else '  <- had to pick from list'}")
    print(f"   {'TOTAL':<27} {tot} taps for {len(msg)} words")
