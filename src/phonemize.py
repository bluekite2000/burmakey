"""Extract a PHONEME-level lexicon once, so spelling becomes a free variable."""
import re, csv, json, unicodedata
import laonlp
from laonlp.tokenize.syllable import syllable_tokenize
from tones import analyse as tone_of
from lao2al import C, TONE_MARKS, ONSET, FINAL, SONORANT, PATTERNS, onset_al

VOW = {  # AL vowel grapheme -> (quality, length)
    "i":("i","S"),"ii":("i","L"),"e":("e","S"),"ee":("e","L"),
    "ae":("E","S"),"aae":("E","L"),"eu":("M","S"),"eeu":("M","L"),
    "oe":("V","S"),"ooe":("V","L"),"a":("a","S"),"aa":("a","L"),
    "u":("u","S"),"uu":("u","L"),"o":("o","S"),"oo":("o","L"),
    "oa":("O","S"),"ooa":("O","L"),"ia":("iM","S"),"iia":("iM","L"),
    "uea":("MM","S"),"uuea":("MM","L"),"ua":("uM","S"),"uua":("uM","L"),
}
TONE_CANON = {"lowrising":"rising"}   # 7 labels -> 6 tones


def syl_phonemes(syl):
    s = unicodedata.normalize("NFC", syl)
    tone, _ = tone_of(s)
    if tone is None:
        return None
    tone = TONE_CANON.get(tone, tone)
    bare = "".join(ch for ch in s if ch not in TONE_MARKS)
    for rx, vowel, forced in PATTERNS:
        m = rx.match(bare)
        if not m:
            continue
        o = onset_al(m.group("o"))
        if o is None:
            return None
        f = forced
        if f is None:
            g = m.groupdict().get("f")
            f = FINAL.get(g, "") if g else ""
        q, ln = VOW[vowel]
        return {"on": o, "v": q, "len": ln, "fin": f, "t": tone}
    return None


def word_phonemes(w):
    out = []
    for syl in syllable_tokenize(w):
        if not any(ch in C for ch in syl):
            continue
        p = syl_phonemes(syl)
        if p is None:
            return None
        out.append(p)
    return out or None


if __name__ == "__main__":
    root = laonlp.__path__[0]
    words = [w.strip() for w in open(root + "/corpus/lo_spellcheck_dict.txt",
             encoding="utf-8") if w.strip() and not w.startswith("#")]
    gloss = {}
    for r in csv.DictReader(open(root + "/corpus/lao-eng-dictionary.csv")):
        lw, en = r.get("LaoWord","").strip(), (r.get("English") or "").strip()
        if lw and en and lw not in gloss:
            gloss[lw] = en[:44]

    lex = []
    for w in words:
        p = word_phonemes(w)
        if p:
            lex.append({"lao": w, "syl": p, "g": gloss.get(w, "")})
    json.dump(lex, open("phonlex.json","w"), ensure_ascii=False)
    print(f"phonemised {len(lex):,} / {len(words):,} words "
          f"({100*len(lex)/len(words):.1f}%)")

    import collections
    on = collections.Counter(s["on"] for e in lex for s in e["syl"])
    ln = collections.Counter(s["len"] for e in lex for s in e["syl"])
    fin= collections.Counter(s["fin"] for e in lex for s in e["syl"])
    print("\nonset frequency (top 12):",
          ", ".join(f"{k or 'ZERO'}={v:,}" for k,v in on.most_common(12)))
    print(f"\nvowel length: long={ln['L']:,} ({100*ln['L']/sum(ln.values()):.1f}%) "
          f"short={ln['S']:,} ({100*ln['S']/sum(ln.values()):.1f}%)")
    print(f"no final coda: {fin['']:,} ({100*fin['']/sum(fin.values()):.1f}%)")
    multi = sum(1 for k,v in on.items() if len(k)>1 for _ in range(v))
    tot = sum(on.values())
    print(f"\nsyllables whose onset is a MULTI-letter grapheme: "
          f"{sum(v for k,v in on.items() if len(k)>1):,} / {tot:,} "
          f"({100*sum(v for k,v in on.items() if len(k)>1)/tot:.1f}%)")
