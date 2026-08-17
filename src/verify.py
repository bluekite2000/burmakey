"""
Aksoon Laatin verifier.

Tests the claims made in the orthography proposal:
  1. Every distinct Lao syllable renders to a distinct Latin string (injectivity).
  2. Every rendered string parses back to exactly one syllable (round-trip).
  3. How often two-syllable sequences are ambiguous (the §6 claim that tone
     letters act as syllable delimiters).

No corpus needed. This enumerates the phonological space directly.
"""
import random
from itertools import product
from collections import defaultdict

# ---------------------------------------------------------------- inventory

ONSETS = {
    "": "?",  "k": "k", "kh": "kh", "ng": "ng", "j": "tc", "s": "s",
    "ny": "N", "d": "d", "t": "t", "th": "th", "n": "n", "b": "b",
    "p": "p", "ph": "ph", "f": "f", "m": "m", "y": "j", "l": "l",
    "w": "w", "h": "h", "kw": "kw", "khw": "khw",
}

# grapheme -> (quality, length)
VOWELS = {
    "i": ("i", "S"),    "ii": ("i", "L"),
    "e": ("e", "S"),    "ee": ("e", "L"),
    "ae": ("E", "S"),   "aae": ("E", "L"),
    "eu": ("M", "S"),   "eeu": ("M", "L"),
    "oe": ("V", "S"),   "ooe": ("V", "L"),
    "a": ("a", "S"),    "aa": ("a", "L"),
    "u": ("u", "S"),    "uu": ("u", "L"),
    "o": ("o", "S"),    "oo": ("o", "L"),
    "oa": ("O", "S"),   "ooa": ("O", "L"),
    "ia": ("iM", "S"),  "iia": ("iM", "L"),
    "uea": ("MM", "S"), "uuea": ("MM", "L"),
    "ua": ("uM", "S"),  "uua": ("uM", "L"),
}

FINALS = ["", "p", "t", "k", "m", "n", "ng", "w", "y"]
STOPS = {"p", "t", "k"}

# tone -> letter.  mid is unwritten.
TONES = {"mid": "", "low": "r", "lowfall": "v", "rise": "q", "high": "z", "highfall": "c"}
CHECKED_TONES = ["mid", "high", "lowfall", "highfall"]   # 4 on checked syllables

TONE_LETTERS = {v for v in TONES.values() if v}


def is_checked(vgrapheme, final):
    """Stops close a checked syllable; so does a short vowel with no coda
    (phonetic glottal stop)."""
    if final in STOPS:
        return True
    if final == "" and VOWELS[vgrapheme][1] == "S":
        return True
    return False


def legal_syllables(apply_phonotactics=True):
    for onset, vg, final in product(ONSETS, VOWELS, FINALS):
        quality = VOWELS[vg][0]
        if apply_phonotactics:
            # no /w/ coda after round vowels, no /j/ coda after front vowels
            if final == "w" and quality in {"u", "o", "O", "uM"}:
                continue
            if final == "y" and quality in {"i", "e", "E", "iM"}:
                continue
        tones = CHECKED_TONES if is_checked(vg, final) else list(TONES)
        for tone in tones:
            yield (onset, vg, final, tone)


def render(syl):
    onset, vg, final, tone = syl
    return onset + vg + final + TONES[tone]


# ---------------------------------------------------------------- parser

ONSET_KEYS = sorted(ONSETS, key=len, reverse=True)
VOWEL_KEYS = sorted(VOWELS, key=len, reverse=True)
FINAL_KEYS = sorted([f for f in FINALS if f], key=len, reverse=True)


def parse_all(s):
    """Return every syllable analysis of the whole string s. Exhaustive,
    not greedy -- we want to find ambiguity, not paper over it."""
    out = []
    for o in ONSET_KEYS:
        if o and not s.startswith(o):
            continue
        rest1 = s[len(o):]
        for v in VOWEL_KEYS:
            if not rest1.startswith(v):
                continue
            rest2 = rest1[len(v):]
            for f in [""] + FINAL_KEYS:
                if f and not rest2.startswith(f):
                    continue
                rest3 = rest2[len(f):]
                if rest3 == "":
                    tone = "mid"
                elif rest3 in TONE_LETTERS:
                    tone = next(k for k, x in TONES.items() if x == rest3)
                else:
                    continue
                cand = (o, v, f, tone)
                allowed = CHECKED_TONES if is_checked(v, f) else list(TONES)
                if tone in allowed:
                    out.append(cand)
    return out


def parse_word(s, max_syls=2):
    """Every way of splitting s into <= max_syls syllables."""
    if max_syls == 0:
        return [[]] if s == "" else []
    if s == "":
        return [[]]
    results = []
    for i in range(1, len(s) + 1):
        head, tail = s[:i], s[i:]
        heads = parse_all(head)
        if not heads:
            continue
        for tails in parse_word(tail, max_syls - 1):
            for h in heads:
                results.append([h] + tails)
    return results


# ---------------------------------------------------------------- tests

print("=" * 62)
print("TEST 1 — injectivity of the monosyllable rendering")
print("=" * 62)

syls = list(legal_syllables())
buckets = defaultdict(list)
for s in syls:
    buckets[render(s)].append(s)

collisions = {k: v for k, v in buckets.items() if len(v) > 1}
print(f"legal syllables enumerated : {len(syls):,}")
print(f"distinct Latin strings     : {len(buckets):,}")
print(f"COLLISIONS                 : {len(collisions)}")
for k, v in list(collisions.items())[:12]:
    print(f"   {k!r} <- {v}")

print()
print("=" * 62)
print("TEST 2 — round-trip: string parses back to exactly one syllable")
print("=" * 62)

bad_count, multi_count = 0, 0
examples = []
for s in syls:
    txt = render(s)
    got = parse_all(txt)
    if s not in got:
        bad_count += 1
        if len(examples) < 8:
            examples.append(("LOST", txt, s, got))
    if len(got) > 1:
        multi_count += 1
        if len(examples) < 8:
            examples.append(("AMBIG", txt, s, got))

print(f"syllables tested           : {len(syls):,}")
print(f"failed to round-trip       : {bad_count}")
print(f"parsed >1 way              : {multi_count}")
for tag, txt, s, got in examples:
    print(f"   [{tag}] {txt!r} expected {s} got {got}")

print()
print("=" * 62)
print("TEST 3 — two-syllable boundary ambiguity (the §6 claim)")
print("=" * 62)

random.seed(11)
sample = random.sample(syls, 700)
pairs = [(a, b) for a in sample[:350] for b in sample[350:]]
random.shuffle(pairs)
pairs = pairs[:60000]

amb = 0
amb_examples = []
amb_by_tone = defaultdict(int)
tot_by_tone = defaultdict(int)

for a, b in pairs:
    txt = render(a) + render(b)
    parses = [p for p in parse_word(txt, 2) if len(p) == 2]
    tot_by_tone[a[3]] += 1
    if len(parses) > 1:
        amb += 1
        amb_by_tone[a[3]] += 1
        if len(amb_examples) < 6:
            amb_examples.append((txt, parses))

print(f"two-syllable words tested  : {len(pairs):,}")
print(f"ambiguous (>1 parse)       : {amb:,}  ({100*amb/len(pairs):.1f}%)")
print()
print("ambiguity rate by tone of the FIRST syllable:")
for t in TONES:
    n = tot_by_tone[t]
    if n:
        print(f"   {t:9s} (letter {TONES[t] or '-'}) : {100*amb_by_tone[t]/n:5.1f}%   n={n}")

print()
for txt, parses in amb_examples:
    print(f"   {txt!r}")
    for p in parses[:3]:
        print(f"        {p}")
