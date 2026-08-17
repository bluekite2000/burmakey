"""
Ingest the fetched Lao corpus: clean PDF artifacts, tokenize, count,
verify it is what it claims to be, answer the tone question with TOKENS,
and pretrain the engine.
"""
import re, json, collections, unicodedata
from laonlp.tokenize import word_tokenize
from typist import lex, FREQ
from tones import analyse as tone_of, HIGH, MID, LOW

RAW = (open("corpus/udhr_lo.txt").read() + "\n" +
       open("corpus/headlines_lo.txt").read())

# ---------------- cleaning (PDF text-layer artifacts) ----------------------
COMB = "ັິີຶືຸູົຼ່້໊໋໌ໍ"
t = RAW
t = t.replace("แ", "ແ")                     # Thai แ -> Lao ແ
t = re.sub(f" +([{COMB}])", r"\1", t)                  # space before combining mark
t = re.sub(r"([ກ-ຮໜໝ]) າ", "\\1ຳ", t)                  # detached ຳ
t = re.sub(r"ືື", "ື", t); t = re.sub(r"ິິ", "ິ", t)     # doubled above-vowels
t = re.sub(r"ີິ", "ີ", t); t = re.sub(r"ົົ", "ົ", t)
t = re.sub(r"ືິ", "ື", t); t = re.sub(r"ຶື", "ຶ", t)
t = re.sub(r"[0-9A-Za-z,;:.\-()\[\]'\"%/]+", " ", t)   # digits & latin out

# ---------------- verify it is Lao running text ----------------------------
lao_chars = sum(1 for c in t if "຀" <= c <= "໿")
total_chars = sum(1 for c in t if not c.isspace())
print("=" * 66)
print("CORPUS VERIFICATION")
print("=" * 66)
print(f"sources    : UDHR official Lao translation (OHCHR) + RFA/VOA Lao headlines")
print(f"licensing  : UDHR freely reproducible; headlines = titles (facts)")
print(f"Lao-script : {100*lao_chars/max(total_chars,1):.1f}% of non-space chars")

toks = []
for line in t.split("\n"):
    line = line.strip()
    if not line: continue
    words = [w for w in word_tokenize(line) if any("຀" <= c <= "໿" for c in w)]
    toks.append(words)

flat = [w for ws in toks for w in ws]
in_lex = [w for w in flat if w in lex]
print(f"tokens     : {len(flat):,}   distinct {len(set(flat)):,}")
print(f"in lexicon : {len(in_lex):,} ({100*len(in_lex)/len(flat):.1f}%) "
      f"— rest are compounds/damaged/OOV")

# ---------------- token-frequency tone answer ------------------------------
from tones import analyse
from laonlp.tokenize.syllable import syllable_tokenize
tone_tok = collections.Counter()
for w in flat:
    for syl in syllable_tokenize(w):
        if not any(c in HIGH | MID | LOW for c in syl): continue
        tn, _ = analyse(syl)
        if tn: tone_tok[{"lowrising":"rising"}.get(tn, tn)] += 1
tot = sum(tone_tok.values())
print("\nTONE FREQUENCY BY TOKEN (real running text — answers §9.3 properly)")
for tn, n in tone_tok.most_common():
    print(f"   {tn:<10} {100*n/tot:5.1f}%")

# ---------------- compare with the assumed model ---------------------------
uni = collections.Counter(in_lex)
top_corpus = [w for w, _ in uni.most_common(20)]
top_assumed = sorted(lex, key=lambda w: -FREQ[w])[:20]
overlap = len(set(top_corpus) & set(top_assumed))
print(f"\ntop-20 corpus words vs my assumed frequency model: {overlap}/20 overlap")
print("corpus top 10:", " ".join(top_corpus[:10]))

# ---------------- pretrain + test on held-out dialogue ---------------------
big = collections.Counter()
for ws in toks:
    kept = [w for w in ws if w in lex]
    for a, b in zip(kept, kept[1:]):
        big[(a, b)] += 1
print(f"\nbigram pairs learned: {len(big):,} (seen >=2: "
      f"{sum(1 for v in big.values() if v>=2):,})")
json.dump({"uni": dict(uni), "big": {f"{a}\t{b}": c for (a, b), c in big.items()}},
          open("pretrained.json", "w"), ensure_ascii=False)

import optimise3 as O3
from typist import karaoke
enc3 = O3.make_encoder(json.load(open("cfg3.json")))
stream = [w for r in json.load(open("convo.json"))["rows"] for w, _ in r["words"]]
kk_spell = {w: karaoke(lex[w]["syl"]) for w in lex}
by_prefix = collections.defaultdict(list)
for w, s in kk_spell.items():
    by_prefix[""].append(w)
    for i in range(1, len(s)+1): by_prefix[s[:i]].append(w)
for p in by_prefix:
    by_prefix[p] = sorted(by_prefix[p], key=lambda w: -FREQ[w])[:60]

def run(pretrain, shortlist=5):
    recency = collections.Counter(); bigr = collections.defaultdict(collections.Counter)
    if pretrain:
        for w, c in uni.items(): recency[w] += c * 0.3
        for (a, b), c in big.items(): bigr[a][b] += c * 0.5
    prev = None; taps = zero = 0
    def score(w):
        return FREQ[w] + 10*recency[w] + (100*bigr[prev][w] if prev else 0)
    for w in stream:
        s = kk_spell[w]; found = None
        for k in range(0, len(s)+1):
            pool = set(by_prefix[s[:k]]) | {x for x in recency if kk_spell[x].startswith(s[:k])}
            cs = sorted(pool, key=score, reverse=True)[:shortlist]
            if w in cs: found = k; break
        k = len(s) if found is None else found
        taps += k + 1
        if found == 0: zero += 1
        recency[w] += 1
        if prev is not None: bigr[prev][w] += 1
        prev = w
    return taps/len(stream), 100*zero/len(stream)

cold_t, cold_z = run(False)
pre_t, pre_z = run(True)
print("\nENGINE TEST — two-friends dialogue (held out), shortlist 5")
print(f"   cold start        : {cold_t:.2f} taps/word   {cold_z:.1f}% zero-key")
print(f"   corpus-pretrained : {pre_t:.2f} taps/word   {pre_z:.1f}% zero-key")
print(f"   difference        : {pre_t-cold_t:+.2f} taps/word")
