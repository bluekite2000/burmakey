"""
Search the spelling space for configurations that are BOTH shorter to type
and less ambiguous than the hand-designed Aksoon Laatin.

Key structural idea being tested: a Lao syllable is onset-vowel-final-tone,
and those slots are positionally distinct. So the SAME letter can mean an
onset at the start and a tone at the end without collision, because Lao
allows only 8 coda consonants and everything else is stranded. That frees
enough letters to give every aspirated onset a single character.
"""
import json, itertools, statistics, collections

LEX = json.load(open("phonlex.json"))

# ---------------------------------------------------------------- encodings
# keys are the onset graphemes as stored in phonlex.json
_ONS = ["x","k","kh","ng","j","s","ny","d","t","th","n","b","p","ph","f",
        "m","y","l","w","h","kw","khw"]
ONSET_DIGRAPH = {o: o for o in _ONS}
# single-letter: every aspirate and palatal gets its own key
ONSET_SINGLE = dict(ONSET_DIGRAPH)
ONSET_SINGLE.update({"x":"z","kh":"q","ng":"g","j":"c","ny":"j",
                     "th":"x","ph":"v","khw":"qw"})

VOWEL_DIGRAPH = {"i":"i","e":"e","E":"ae","M":"eu","V":"oe","a":"a",
    "u":"u","o":"o","O":"oa","iM":"ia","MM":"uea","uM":"ua"}
VOWEL_COMPACT = {"i":"i","e":"e","E":"y","M":"r","V":"oe","a":"a",
    "u":"u","o":"o","O":"oa","iM":"ia","MM":"ra","uM":"ua"}

FINAL_DIGRAPH = {"":"", "p":"p","t":"t","k":"k","m":"m","n":"n",
                 "ng":"ng","w":"w","y":"y"}
FINAL_SINGLE  = {"":"", "p":"p","t":"t","k":"k","m":"m","n":"n",
                 "ng":"g","w":"w","y":"y"}

TONES = ["high","mid","rising","highfall","low","lowfall"]
# tone letters drawn from letters never used as a CODA -> no collision
TONE_POOL_DIGRAPH = ["r","v","q","z","c"]
TONE_POOL_SINGLE  = ["h","l","s","f","d"]   # free in coda position


def make_encoder(cfg):
    on = ONSET_SINGLE if cfg["onset"] == "single" else ONSET_DIGRAPH
    vo = VOWEL_COMPACT if cfg["vowel"] == "compact" else VOWEL_DIGRAPH
    fi = FINAL_SINGLE if cfg["onset"] == "single" else FINAL_DIGRAPH
    pool = TONE_POOL_SINGLE if cfg["onset"] == "single" else TONE_POOL_DIGRAPH
    marked = [t for t in TONES if t != cfg["unmarked"]]
    tone_letter = dict(zip(marked, pool))
    tone_letter[cfg["unmarked"]] = ""

    def enc_syl(s):
        o = on[s["on"]]
        v = vo[s["v"]]
        if s["len"] == "L":
            if cfg["length"] == "double":
                v = v[0] + v
            else:                       # 'mark' = a dedicated length letter
                v = v + cfg["lenmark"]
        elif cfg["length"] == "markshort":
            v = v + cfg["lenmark"]
        f = fi[s["fin"]]
        t = tone_letter[s["t"]]
        return (o + t + v + f) if cfg["tonepos"] == "early" else (o + v + f + t)

    return lambda syls: "".join(enc_syl(s) for s in syls)


def evaluate(cfg):
    enc = make_encoder(cfg)
    spell = collections.defaultdict(list)
    for e in LEX:
        spell[enc(e["syl"])].append(e["lao"])
    words = sorted(spell)
    counts = collections.Counter()
    for w in words:
        for i in range(1, len(w) + 1):
            counts[w[:i]] += 1
    keys = []
    for w in words:
        k = next((i for i in range(1, len(w)+1) if counts[w[:i]] == 1), len(w))
        keys.append(k)
    amb_words = sum(len(v) for v in spell.values() if len(v) > 1)
    total = sum(len(v) for v in spell.values())
    return {
        "keys": statistics.mean(keys),
        "len": statistics.mean(map(len, words)),
        "amb": 100 * amb_words / total,
        "n": len(words),
    }


BASE = {"onset":"digraph","vowel":"digraph","length":"double",
        "lenmark":"h","unmarked":"mid","tonepos":"late"}

grid = []
for onset in ["digraph","single"]:
    for vowel in ["digraph","compact"]:
        for length in ["double","mark","markshort"]:
            for unmarked in TONES:
                for tonepos in ["late","early"]:
                    grid.append({"onset":onset,"vowel":vowel,"length":length,
                                 "lenmark":"h","unmarked":unmarked,
                                 "tonepos":tonepos})

print(f"evaluating {len(grid)} spelling configurations over {len(LEX):,} words…\n")
base = evaluate(BASE)
print(f"{'BASELINE (draft 1)':46} keys={base['keys']:.2f}  "
      f"len={base['len']:.2f}  ambiguous={base['amb']:.1f}%")
print(f"{'karaoke Lao (from earlier run)':46} keys=5.69  len=6.93  ambiguous=31.4%\n")

res = []
for cfg in grid:
    r = evaluate(cfg)
    r["cfg"] = cfg
    res.append(r)

# Pareto front on (keys, amb)
front = [r for r in res if not any(
    o["keys"] <= r["keys"] and o["amb"] <= r["amb"] and
    (o["keys"] < r["keys"] or o["amb"] < r["amb"]) for o in res)]
front.sort(key=lambda r: r["keys"])

print("PARETO FRONT — no other configuration beats these on both axes")
print(f"{'keys':>6}{'len':>7}{'amb%':>7}   configuration")
for r in front:
    c = r["cfg"]
    print(f"{r['keys']:>6.2f}{r['len']:>7.2f}{r['amb']:>7.1f}   "
          f"onset={c['onset']:<8} vowel={c['vowel']:<8} len={c['length']:<9} "
          f"unmarked={c['unmarked']:<9} tone={c['tonepos']}")

best = min(res, key=lambda r: r["keys"] + 0.12 * r["amb"])
print(f"\nBEST BALANCED (min keys + 0.12*ambiguity):")
print(f"   {best['cfg']}")
print(f"   keys={best['keys']:.2f}  len={best['len']:.2f}  amb={best['amb']:.1f}%")
print(f"   vs draft 1: {best['keys']-base['keys']:+.2f} keys, "
      f"{best['amb']-base['amb']:+.1f}pp ambiguity")
print(f"   vs karaoke: {best['keys']-5.69:+.2f} keys, {best['amb']-31.4:+.1f}pp ambiguity")
json.dump(best["cfg"], open("best_cfg.json","w"))
