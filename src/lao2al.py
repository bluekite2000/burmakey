"""Lao script -> Aksoon Laatin. Builds the lexicon the keyboard predicts from."""
import re, csv, json, collections, unicodedata
import laonlp
from laonlp.tokenize.syllable import syllable_tokenize
from tones import analyse as tone_of

C = "ກຂຄງຈສຊຍດຕຖທນບປຜຝພຟມຢຣລວຫອຮໜໝ"
TONE_MARKS = "່້໊໋"

ONSET = {
    "ກ":"k","ຂ":"kh","ຄ":"kh","ງ":"ng","ຈ":"j","ສ":"s","ຊ":"s","ຍ":"ny",
    "ດ":"d","ຕ":"t","ຖ":"th","ທ":"th","ນ":"n","ບ":"b","ປ":"p","ຜ":"ph",
    "ຝ":"f","ພ":"ph","ຟ":"f","ມ":"m","ຢ":"y","ຣ":"l","ລ":"l","ວ":"w",
    "ຫ":"h","ອ":"x","ຮ":"h","ໜ":"n","ໝ":"m",
}
FINAL = {"ກ":"k","ງ":"ng","ດ":"t","ນ":"n","ບ":"p","ມ":"m","ວ":"w","ຍ":"y"}
SONORANT = set("ງຍນມລວ")

TONE_LETTER = {  # phonological tone -> Aksoon Laatin final letter
    "high":"", "mid":"z", "rising":"q", "lowrising":"q",
    "highfall":"c", "low":"r", "lowfall":"v",
}

# ordered: most specific first.  o = onset, f = final
P = [
    (r"^ເ(?P<o>[C]+?)ົາ$",            "a",   "w"),
    (r"^ເ(?P<o>[C]+?)ຶອ(?P<f>[F])?$", "uea", None),
    (r"^ເ(?P<o>[C]+?)ືອ(?P<f>[F])?$", "uuea",None),
    (r"^ເ(?P<o>[C]+?)ັຍ(?P<f>[F])?$", "ia",  None),
    (r"^ເ(?P<o>[C]+?)ຍ(?P<f>[F])?$",  "iia", None),
    (r"^ເ(?P<o>[C]+?)າະ$",            "oa",  None),
    (r"^ເ(?P<o>[C]+?)ິ(?P<f>[F])?$",  "oe",  None),
    (r"^ເ(?P<o>[C]+?)ີ(?P<f>[F])?$",  "ooe", None),
    (r"^ເ(?P<o>[C]+?)ະ$",             "e",   None),
    (r"^ເ(?P<o>[C]+?)ັ(?P<f>[F])$",   "e",   None),
    (r"^ເ(?P<o>[C]+?)(?P<f>[F])?$",   "ee",  None),
    (r"^ແ(?P<o>[C]+?)ະ$",             "ae",  None),
    (r"^ແ(?P<o>[C]+?)ັ(?P<f>[F])$",   "ae",  None),
    (r"^ແ(?P<o>[C]+?)(?P<f>[F])?$",   "aae", None),
    (r"^ໂ(?P<o>[C]+?)ະ$",             "o",   None),
    (r"^ໂ(?P<o>[C]+?)(?P<f>[F])?$",   "oo",  None),
    (r"^ໃ(?P<o>[C]+?)$",              "a",   "y"),
    (r"^ໄ(?P<o>[C]+?)$",              "a",   "y"),
    (r"^(?P<o>[C]+?)ຳ$",              "a",   "m"),
    (r"^(?P<o>[C]+?)ົວ(?P<f>[F])?$",  "ua",  None),
    (r"^(?P<o>[C]+?)ວ(?P<f>[F])$",    "uua", None),
    (r"^(?P<o>[C]+?)ຽ(?P<f>[F])?$",   "iia", None),
    (r"^(?P<o>[C]+?)ໍ$",              "ooa", None),
    (r"^(?P<o>[C]+?)ອ(?P<f>[F])?$",   "ooa", None),
    (r"^(?P<o>[C]+?)ະ$",              "a",   None),
    (r"^(?P<o>[C]+?)ັ(?P<f>[F])$",    "a",   None),
    (r"^(?P<o>[C]+?)າ(?P<f>[F])?$",   "aa",  None),
    (r"^(?P<o>[C]+?)ິ(?P<f>[F])?$",   "i",   None),
    (r"^(?P<o>[C]+?)ີ(?P<f>[F])?$",   "ii",  None),
    (r"^(?P<o>[C]+?)ຶ(?P<f>[F])?$",   "eu",  None),
    (r"^(?P<o>[C]+?)ື(?P<f>[F])?$",   "eeu", None),
    (r"^(?P<o>[C]+?)ຸ(?P<f>[F])?$",   "u",   None),
    (r"^(?P<o>[C]+?)ູ(?P<f>[F])?$",   "uu",  None),
    (r"^(?P<o>[C]+?)ົ(?P<f>[F])$",    "o",   None),
    (r"^(?P<o>[C]+?)(?P<f>[F])$",     "o",   None),
]
FSET = "ກງດນບມວຍ"
PATTERNS = [(re.compile(p.replace("[C]", f"[{C}]").replace("[F]", f"[{FSET}]")), v, f)
            for p, v, f in P]


def fix_ho(m, bare):
    """ຫ + sonorant is one onset, not onset ຫ + sonorant coda, when the
    syllable still has another consonant to serve as the real coda."""
    return m

def onset_al(s):
    """Lao onset string -> Aksoon Laatin onset."""
    if len(s) >= 2 and s[0] == "ຫ" and s[1] in SONORANT:
        return ONSET.get(s[1], "")
    if len(s) >= 2 and s[-1] == "ວ" and s[0] in "ກຂຄ":
        return ONSET[s[0]] + "w"
    return ONSET.get(s[0], None)


def syl_to_al(syl):
    s = unicodedata.normalize("NFC", syl)
    tone, _ = tone_of(s)
    bare = "".join(ch for ch in s if ch not in TONE_MARKS)
    for rx, vowel, forced_final in PATTERNS:
        m = rx.match(bare)
        if not m:
            continue
        o = onset_al(m.group("o"))
        if o is None:
            return None
        f = forced_final
        if f is None:
            g = m.groupdict().get("f")
            f = FINAL.get(g, "") if g else ""
        if tone is None:
            return None
        return o + vowel + f + TONE_LETTER.get(tone, "")
    return None


def word_to_al(w):
    parts = []
    for syl in syllable_tokenize(w):
        if not any(ch in C for ch in syl):
            continue
        a = syl_to_al(syl)
        if a is None:
            return None
        parts.append(a)
    return "".join(parts) if parts else None


if __name__ == "__main__":
    root = laonlp.__path__[0]
    words = [w.strip() for w in open(root + "/corpus/lo_spellcheck_dict.txt",
             encoding="utf-8") if w.strip() and not w.startswith("#")]

    gloss = {}
    for r in csv.DictReader(open(root + "/corpus/lao-eng-dictionary.csv")):
        lw, en = r.get("LaoWord", "").strip(), (r.get("English") or "").strip()
        if lw and en and lw not in gloss:
            gloss[lw] = en[:60]

    lex, failed = {}, 0
    for w in words:
        al = word_to_al(w)
        if al:
            lex.setdefault(al, []).append(w)
        else:
            failed += 1

    print(f"words in list      : {len(words):,}")
    print(f"converted          : {len(words)-failed:,} "
          f"({100*(len(words)-failed)/len(words):.1f}%)")
    print(f"failed             : {failed:,}")
    print(f"distinct AL spellings: {len(lex):,}")
    homo = sum(1 for v in lex.values() if len(v) > 1)
    print(f"AL spellings mapping to >1 Lao word: {homo:,} "
          f"({100*homo/len(lex):.1f}%)  <- these need the ranker")
    print()
    print("samples (Aksoon Laatin -> Lao -> English):")
    shown = 0
    for al, ws in lex.items():
        if ws[0] in gloss and 4 <= len(al) <= 11 and shown < 14:
            print(f"   {al:<13} {ws[0]:<12} {gloss[ws[0]]}")
            shown += 1

    out = {al: [[w, gloss.get(w, "")] for w in ws] for al, ws in lex.items()}
    json.dump(out, open("lexicon.json", "w"), ensure_ascii=False)
    print(f"\nwrote lexicon.json ({len(out):,} entries)")
