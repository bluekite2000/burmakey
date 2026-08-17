"""
Draft 3: search with THREE objectives, not two.

Draft 2 was fast and accurate and looked like line noise, because the
optimiser was only ever scored on keystrokes and ambiguity. This adds the
missing axis: how close a spelling stays to what Lao people already type.

FAMILIARITY = 1 - (edit distance from the karaoke spelling / word length),
frequency-weighted. If someone already writes `maew` for cat, then `maew`
scores 1.0, `maewq` scores high, and `myhw` scores badly.

All three metrics are frequency-weighted — measured over words in proportion
to how often they are actually typed, not once each.
"""
import json, collections, functools
from typist import FREQ, lex, karaoke

TONES = ["high", "mid", "rising", "highfall", "low", "lowfall"]

_ONS = ["x","k","kh","ng","j","s","ny","d","t","th","n","b","p","ph","f",
        "m","y","l","w","h","kw","khw"]
ONSET = {
  # keep every familiar digraph; write the zero onset
  "digraph": {o: o for o in _ONS},
  # every multi-letter onset collapses to one key
  "single": {**{o: o for o in _ONS},
             **{"x":"z","kh":"q","ng":"g","j":"c","ny":"j","th":"x",
                "ph":"v","khw":"qw"}},
  # keep kh/th/ph (universally recognised); compress only ng and ny
  "mixed":  {**{o: o for o in _ONS}, **{"ng":"g","ny":"j"}},
}
VOWEL = {
  "digraph": {"i":"i","e":"e","E":"ae","M":"eu","V":"oe","a":"a","u":"u",
              "o":"o","O":"oa","iM":"ia","MM":"uea","uM":"ua"},
  "compact": {"i":"i","e":"e","E":"y","M":"r","V":"oe","a":"a","u":"u",
              "o":"o","O":"oa","iM":"ia","MM":"ra","uM":"ua"},
}
FINAL = {"":"", "p":"p","t":"t","k":"k","m":"m","n":"n","ng":"ng","w":"w","y":"y"}
FINAL_G = {**FINAL, "ng":"g"}

POOL = {"digraph": ["r","v","q","z","c"],
        "single":  ["h","l","s","f","d"],
        "mixed":   ["r","v","q","z","c"]}


def make_encoder(cfg):
    on = ONSET[cfg["onset"]]
    vo = VOWEL[cfg["vowel"]]
    fi = FINAL_G if cfg["onset"] in ("single", "mixed") else FINAL
    marked = [t for t in TONES if t != cfg["unmarked"]]
    TL = dict(zip(marked, POOL[cfg["onset"]]))
    TL[cfg["unmarked"]] = ""
    zero_written = cfg["zero"] == "write"

    def enc(sylls):
        out = []
        for s in sylls:
            o = on[s["on"]]
            if s["on"] == "x" and not zero_written:
                o = ""
            v = vo[s["v"]]
            if s["len"] == "L":
                v = v[0] + v if cfg["length"] == "double" else v + "h"
            elif cfg["length"] == "markshort":
                v = v + "h"
            f = fi[s["fin"]]
            t = TL[s["t"]]
            out.append(o + t + v + f if cfg["tonepos"] == "early" else o + v + f + t)
        return "".join(out)
    return enc


def edit(a, b):
    if a == b: return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]


WORDS = list(lex)
KK = {w: karaoke(lex[w]["syl"]) for w in WORDS}
WSUM = sum(FREQ[w] for w in WORDS)


def evaluate(cfg, shortlist=3):
    enc = make_encoder(cfg)
    spell = {w: enc(lex[w]["syl"]) for w in WORDS}
    pref = collections.defaultdict(list)
    for w, s in spell.items():
        for i in range(1, len(s) + 1):
            pref[s[:i]].append(w)
    for p in pref:
        if len(pref[p]) > shortlist:
            pref[p] = sorted(pref[p], key=lambda w: -FREQ[w])[:shortlist]
    groups = collections.defaultdict(int)
    for s in spell.values():
        groups[s] += 1

    taps = amb = fam = 0.0
    for w in WORDS:
        s, f = spell[w], FREQ[w]
        k = next((i for i in range(1, len(s)+1) if w in pref[s[:i]]), len(s))
        taps += f * (k + 1)
        if groups[s] > 1:
            amb += f
        kk = KK[w]
        fam += f * (1 - edit(s, kk) / max(len(s), len(kk), 1))
    return {"taps": taps/WSUM, "amb": 100*amb/WSUM, "fam": 100*fam/WSUM}


if __name__ == "__main__":
    grid = [{"onset":o,"vowel":v,"length":l,"unmarked":"high",
             "tonepos":tp,"zero":z}
            for o in ["digraph","single","mixed"]
            for v in ["digraph","compact"]
            for l in ["double","mark","markshort"]
            for tp in ["late","early"]
            for z in ["write","omit"]]

    print(f"evaluating {len(grid)} configurations, frequency-weighted…\n")
    kk_taps = sum(FREQ[w]*(len(KK[w])+1) for w in WORDS)/WSUM
    kkg = collections.Counter(KK.values())
    kk_amb = 100*sum(FREQ[w] for w in WORDS if kkg[KK[w]] > 1)/WSUM
    print(f"{'karaoke Lao (typed out)':34} taps={kk_taps:.2f}  "
          f"ambiguous={kk_amb:.1f}%  familiarity=100.0%\n")

    res = []
    for cfg in grid:
        r = evaluate(cfg); r["cfg"] = cfg; res.append(r)

    front = [r for r in res if not any(
        o["taps"] <= r["taps"] and o["amb"] <= r["amb"] and o["fam"] >= r["fam"]
        and (o["taps"] < r["taps"] or o["amb"] < r["amb"] or o["fam"] > r["fam"])
        for o in res)]
    front.sort(key=lambda r: -r["fam"])
    print("PARETO SURFACE (taps / ambiguity / familiarity)")
    print(f"{'taps':>6}{'amb%':>7}{'famil%':>8}   configuration")
    for r in front:
        c = r["cfg"]
        print(f"{r['taps']:>6.2f}{r['amb']:>7.1f}{r['fam']:>8.1f}   "
              f"onset={c['onset']:<8} vowel={c['vowel']:<8} "
              f"len={c['length']:<9} tone={c['tonepos']:<6} zero={c['zero']}")

    # draft 3: most familiar option that stays within 5% of the best taps
    best_taps = min(r["taps"] for r in res)
    ok = [r for r in res if r["taps"] <= best_taps * 1.05 and r["amb"] <= 30]
    d3 = max(ok, key=lambda r: r["fam"])
    print(f"\nDRAFT 3 = most familiar spelling within 5% of the fastest")
    print(f"   {d3['cfg']}")
    print(f"   taps={d3['taps']:.2f}  ambiguous={d3['amb']:.1f}%  "
          f"familiarity={d3['fam']:.1f}%")
    json.dump(d3["cfg"], open("cfg3.json","w"))
