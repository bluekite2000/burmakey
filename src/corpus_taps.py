"""Taps per word over the WHOLE corpus, every topic, for both systems.

Why this replaces a multi-hour emulator run: Bagan has no word prediction —
measured directly on the running app — so its cost is a deterministic function
of the text. One tap per base-layer glyph, one long-press for a second-layer
glyph, two taps for anything on the shifted or symbol page, and no per-word
commit tap (Burmese script is written without spaces between words). Given the
measured keymap, that is arithmetic, and arithmetic covers all 43k sentences
rather than the few hundred an overnight run could grind through.

The emulator established the things arithmetic cannot: that no candidates are
offered, which glyph sits on which layer, and that one tap really does yield
one codepoint (verified character-for-character, see measure_bagan.py).

BurmaKey is scored on the SAME sentences through the same ranker as the study.

Usage: python3 corpus_taps.py [keymap.json]
"""
import sys, json, os, re, collections

import burmese2 as B
import h2h_mobile as H

KEYMAP = sys.argv[1] if len(sys.argv) > 1 else "bagan_keymap_full.json"
TOPICS = "longrun_topics.json"
CORPUS = '/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt'
MAXLEN = 12


ZWSP = "\u200b"


def load_keymap(path):
    """Glyph -> taps needed to produce it.

    Bagan emits ZWSP+mark when a combining vowel is tapped standalone, so the
    probe recorded keys like "\u200bေ". Strip it: what matters is that one tap
    on that key produces the mark.
    """
    d = json.load(open(path))["keymap"]
    out = {}
    for k, v in d.items():
        k = k.replace(ZWSP, "")
        if not k:
            continue
        if k not in out or v[2] < out[k]:
            out[k] = v[2]
    return out


def sentences():
    out = []
    for line in open(CORPUS, encoding='utf8'):
        toks = [t.rsplit('/', 1)[0] for t in line.split() if '/' in t]
        # myPOS marks compounds with '|' and leaves some latin/punct artifacts;
        # they are annotation, not text a person would type
        toks = [t for t in toks
                if t and not re.fullmatch(r"[၀-၉0-9။၊.,!?]+", t)
                and not re.search(r"[|/A-Za-z]", t)]
        if 3 <= len(toks) <= MAXLEN:
            out.append(toks)
    return out


def main():
    cost = load_keymap(KEYMAP)
    sents = sentences()
    print(f"keymap: {len(cost)} glyphs  |  corpus: {len(sents):,} sentences")

    # ---- coverage -----------------------------------------------------
    freq = collections.Counter(ch for s in sents for w in s for ch in w)
    tot = sum(freq.values())
    cov = sum(c for ch, c in freq.items() if ch in cost)
    miss = [(ch, c) for ch, c in freq.most_common() if ch not in cost]
    print(f"glyph coverage: {100*cov/tot:.2f}%  "
          f"({len(miss)} unmapped glyph types, {100*(tot-cov)/tot:.2f}% of instances)")
    if miss[:6]:
        print("  top unmapped:", " ".join(f"{ch}({100*c/tot:.2f}%)" for ch, c in miss[:6]))

    typable = [s for s in sents if all(ch in cost for w in s for ch in w)]
    print(f"fully typable sentences: {len(typable):,} "
          f"({100*len(typable)/len(sents):.1f}%)\n")

    # ---- Bagan: deterministic -----------------------------------------
    def bagan_taps(word):
        return sum(cost[ch] for ch in word)

    # ---- BurmaKey: the study's ranker on the same sentences ------------
    burg = dict(B.LEX)
    idx = H.build_prefix_index(burg)
    traces = H.run_engine(typable, burg, idx)
    bk_taps = sum(len(t[0]) + 1 for t in traces)
    bk_words = len(traces)

    scored = [(w, bagan_taps(w)) for s in typable for w in s if w in burg]
    bg_taps = sum(t for _, t in scored)
    bg_words = len(scored)

    print("=" * 66)
    print("TAPS PER WORD over the whole corpus (words both systems can type)")
    print("=" * 66)
    print(f"  Bagan / TTKeyboard, character entry : {bg_taps/bg_words:.2f}"
          f"   ({bg_words:,} words)")
    print(f"  BurmaKey, Burglish + ranker         : {bk_taps/bk_words:.2f}"
          f"   ({bk_words:,} words)")
    print(f"  difference                          : "
          f"{100*(bk_taps/bk_words - bg_taps/bg_words)/(bg_taps/bg_words):+.1f}%")

    glyphs = [ch for w, _ in scored for ch in w]
    multi = sum(1 for ch in glyphs if cost.get(ch, 1) > 1)
    print(f"  glyphs needing 2 taps (shift page)  : "
          f"{100*multi/len(glyphs):.2f}% of glyphs")
    print(f"  mean codepoints per word            : "
          f"{len(glyphs)/bg_words:.2f}")

    # ---- per topic -------------------------------------------------
    # cluster THIS sentence set, so the breakdown matches what was scored
    import longrun
    print("\nclustering for the per-topic breakdown ...", flush=True)
    assign, _ = longrun.kmeans_topics([(t, t) for t in typable], k=10, iters=8)
    per = collections.defaultdict(lambda: [0, 0, 0])
    ti = 0
    for si, s2 in enumerate(typable):
        for w in s2:
            if w not in burg:
                continue
            per[assign[si]][0] += bagan_taps(w)
            per[assign[si]][1] += 1
    for t, tr in zip([assign[i] for i, s2 in enumerate(typable)
                      for w in s2 if w in burg], traces):
        per[t][2] += len(tr[0]) + 1
    print("\n topic   words   Bagan t/w   BurmaKey t/w   diff")
    for t in sorted(per, key=lambda t: -per[t][1]):
        bt, n, kt = per[t]
        print(f"  {t:>4}  {n:>7,}  {bt/n:>10.2f}  {kt/n:>13.2f}  "
              f"{100*(kt/n-bt/n)/(bt/n):>+6.1f}%")
    spread = [per[t][0]/per[t][1] for t in per]
    print(f"\n  per-topic Bagan taps/word ranges {min(spread):.2f}-{max(spread):.2f}")

    json.dump({"bagan_tpw": bg_taps/bg_words, "burmakey_tpw": bk_taps/bk_words,
               "bagan_words": bg_words, "coverage": 100*cov/tot,
               "typable_sentences": len(typable)},
              open("corpus_taps_results.json", "w"))
    print("\nwrote corpus_taps_results.json")


if __name__ == "__main__":
    main()
