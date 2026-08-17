"""
Follow-up: where does the 2.9% boundary ambiguity actually come from,
and does writing the zero onset fix it?
"""
import random
from collections import defaultdict
import verify as V

random.seed(11)
syls = list(V.legal_syllables())
sample = random.sample(syls, 700)
pairs = [(a, b) for a in sample[:350] for b in sample[350:]]
random.shuffle(pairs)
pairs = pairs[:60000]


def classify(parses):
    """Given >1 parse of a 2-syllable string, name the cause."""
    causes = set()
    for p in parses:
        if p[1][0] == "":
            causes.add("zero-onset")
    for p in parses:
        if p[0][2] in {"p", "t", "k"} and p[1][0] == "h":
            causes.add("aspiration digraph (final C + h)")
        if p[0][2] == "n" and p[1][0] == "y":
            causes.add("ny digraph (final n + y)")
        if p[0][2] == "n" and p[1][0] == "g":
            causes.add("ng digraph")
    return causes or {"other"}


print("=" * 62)
print("Where the ambiguity comes from")
print("=" * 62)
cause_count = defaultdict(int)
amb_total = 0
for a, b in pairs:
    txt = V.render(a) + V.render(b)
    parses = [p for p in V.parse_word(txt, 2) if len(p) == 2]
    if len(parses) > 1:
        amb_total += 1
        for c in classify(parses):
            cause_count[c] += 1

print(f"ambiguous strings: {amb_total:,} of {len(pairs):,} ({100*amb_total/len(pairs):.1f}%)")
for c, n in sorted(cause_count.items(), key=lambda kv: -kv[1]):
    print(f"   {c:34s} implicated in {n:5,}  ({100*n/amb_total:.1f}% of ambiguous)")


# ---- intervention: write the zero onset with the reserved letter x -------
print()
print("=" * 62)
print("Intervention: write zero onset as 'x' (currently unassigned)")
print("=" * 62)

V.ONSETS["x"] = "?"
del V.ONSETS[""]
V.ONSET_KEYS = sorted(V.ONSETS, key=len, reverse=True)

syls2 = [("x" if o == "" else o, v, f, t) for (o, v, f, t) in syls]
by_str = defaultdict(list)
for s in syls2:
    by_str[V.render(s)].append(s)
mono_coll = sum(1 for k, v in by_str.items() if len(v) > 1)
print(f"monosyllable collisions after change : {mono_coll}")

sample2 = [("x" if o == "" else o, v, f, t) for (o, v, f, t) in sample]
pairs2 = [(a, b) for a in sample2[:350] for b in sample2[350:]]
random.seed(11)
random.shuffle(pairs2)
pairs2 = pairs2[:60000]

amb2 = 0
left = defaultdict(int)
ex = []
for a, b in pairs2:
    txt = V.render(a) + V.render(b)
    parses = [p for p in V.parse_word(txt, 2) if len(p) == 2]
    if len(parses) > 1:
        amb2 += 1
        for c in classify(parses):
            left[c] += 1
        if len(ex) < 5:
            ex.append((txt, parses))

print(f"two-syllable ambiguity after change  : {amb2:,} of {len(pairs2):,} "
      f"({100*amb2/len(pairs2):.2f}%)")
print(f"  was 2.9% -> reduction of {100*(1 - amb2/max(amb_total,1)):.0f}%")
print()
print("remaining causes:")
for c, n in sorted(left.items(), key=lambda kv: -kv[1]):
    print(f"   {c:34s} {n:5,}")
print()
for txt, parses in ex:
    print(f"   {txt!r}")
    for p in parses[:2]:
        print(f"        {p}")
