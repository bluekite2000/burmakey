"""
Burmese romanized-input study on real corpus data:
- myG2P v2 (24,802 words with tone-marked romanization)  [CC BY-NC-SA 4.0]
- myPOS v3 (43,196 real segmented sentences)              [CC BY-NC-SA 4.0]

Core design choice: skip inventing an orthography.
Input = toneless "Burglish" (what people already type), output = Burmese
script (unambiguous by construction), engine disambiguates.
"""
import re, json, random, collections, statistics

# ---------------- lexicon from myG2P -----------------------------------
LEX = {}          # word -> canonical toneless burglish
TONED = {}        # word -> tone-marked roman (for analysis)
for line in open('/tmp/myg2p/ver2/myg2p.ver2.0.txt', encoding='utf8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 4: continue
    w, roman = p[1], p[3]
    if '...' in w or '(' in roman: continue
    toned = roman.replace(' ', '')
    burg = re.sub(r"[.:'\-$]", "", toned)      # strip tone/reduction marks
    if not burg or not re.fullmatch(r"[a-z]+", burg): continue
    if w not in LEX:
        LEX[w] = burg
        TONED[w] = toned
print(f"lexicon: {len(LEX):,} Burmese words with toneless Burglish spellings")

# ---------------- corpus: real sentences, real frequencies --------------
sents = []
for line in open('/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt',
                 encoding='utf8'):
    toks = [t.rsplit('/', 1)[0] for t in line.split()]
    toks = [t for t in toks if t and not re.fullmatch(r"[၀-၉0-9။၊.,!?]+", t)]
    if len(toks) >= 3:
        sents.append(toks)
random.seed(7); random.shuffle(sents)
TRAIN, TEST = sents[2000:], sents[:2000]
print(f"corpus: {len(sents):,} sentences -> train {len(TRAIN):,} / test {len(TEST):,}")

train_toks = [w for s in TRAIN for w in s]
FREQ = collections.Counter(train_toks)
cov = sum(1 for w in (x for s in TEST for x in s) if w in LEX)
tot = sum(len(s) for s in TEST)
print(f"test tokens {tot:,}, lexicon coverage {100*cov/tot:.1f}%")

# ---------------- collision measurement (the disease) -------------------
burg_groups = collections.defaultdict(list)
for w, b in LEX.items(): burg_groups[b].append(w)
type_amb = sum(len(v) for v in burg_groups.values() if len(v) > 1)
print(f"\nBURGLISH AMBIGUITY (toneless, like real chat):")
print(f"  by dictionary type : {100*type_amb/len(LEX):.1f}% of words share a spelling")
tt = ta = 0
for s in TEST:
    for w in s:
        if w in LEX:
            tt += 1
            if len(burg_groups[LEX[w]]) > 1: ta += 1
print(f"  by token (real text): {100*ta/tt:.1f}% of running words ambiguous")
worst = sorted(burg_groups.items(), key=lambda kv: -len(kv[1]))[:5]
for b, ws in worst:
    print(f"    '{b}' -> {len(ws)} words: {' '.join(ws[:6])}")

# ---------------- typing simulations ------------------------------------
by_prefix = collections.defaultdict(list)
freq_rank = {w: FREQ.get(w, 0) for w in LEX}
for w, b in LEX.items():
    for i in range(1, len(b)+1):
        by_prefix[b[:i]].append(w)
for p in by_prefix:
    by_prefix[p] = sorted(by_prefix[p], key=lambda w: -freq_rank[w])[:50]

def simulate(shortlist=5, pretrain_bigrams=False, learning=True):
    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    if pretrain_bigrams:
        for s in TRAIN:
            kept = [w for w in s if w in LEX]
            for a, b in zip(kept, kept[1:]):
                bigram[a][b] += 0.2                     # corpus prior, damped
    taps = n = zero = bar = full = 0
    for s in TEST:
        prev = None
        for w in s:
            if w not in LEX:
                prev = None; continue
            n += 1
            sp = LEX[w]
            def score(x):
                v = freq_rank[x] + 10*recency[x]
                if prev is not None: v += 100*bigram[prev][x]
                return v
            found = pick1 = None
            for k in range(0, len(sp)+1):
                pool = by_prefix[sp[:k]]
                if learning and recency:
                    pool = set(pool) | {x for x in recency if LEX[x].startswith(sp[:k])}
                cs = sorted(pool, key=score, reverse=True)[:shortlist]
                if w in cs:
                    found, pick1 = k, cs[0] == w
                    break
            k = len(sp) if found is None else found
            taps += k + 1
            if found == 0: zero += 1
            if found is None: full += 1
            elif not pick1: bar += 1
            if learning:
                recency[w] += 1
                if prev is not None: bigram[prev][w] += 1
            prev = w
    return dict(tpw=taps/n, n=n, zero=100*zero/n, bar=100*bar/n, full=100*full/n)

# baselines
script_chars = burg_chars = bn = 0
for s in TEST:
    for w in s:
        if w in LEX:
            bn += 1
            script_chars += len(w) + 1        # one key per codepoint + space
            burg_chars += len(LEX[w]) + 1
print(f"\nBASELINES (taps/word over {bn:,} real test tokens)")
print(f"  Burmese script, typed key-per-character : {script_chars/bn:.2f}")
print(f"  Burglish typed out (today's chat)       : {burg_chars/bn:.2f}  "
      f"[{100*ta/tt:.0f}% ambiguous]")

r_cold = simulate(pretrain_bigrams=False)
print(f"\nDRAFT-4 ENGINE (Burglish in -> Burmese script out)")
print(f"  cold start        : {r_cold['tpw']:.2f} taps/word  "
      f"zero-key {r_cold['zero']:.1f}%  bar-pick {r_cold['bar']:.1f}%  "
      f"full {r_cold['full']:.1f}%")
r_pre = simulate(pretrain_bigrams=True)
print(f"  corpus-pretrained : {r_pre['tpw']:.2f} taps/word  "
      f"zero-key {r_pre['zero']:.1f}%")
best = min(r_cold, r_pre, key=lambda r: r['tpw']) if isinstance(r_cold,dict) else None
b = r_pre if r_pre['tpw'] < r_cold['tpw'] else r_cold
print(f"\nvs script typing : {b['tpw']-script_chars/bn:+.2f} "
      f"({100*(b['tpw']-script_chars/bn)/(script_chars/bn):+.1f}%)")
print(f"vs Burglish chat : {b['tpw']-burg_chars/bn:+.2f} "
      f"({100*(b['tpw']-burg_chars/bn)/(burg_chars/bn):+.1f}%), "
      f"ambiguity {100*ta/tt:.0f}% -> 0% (script output)")
json.dump({"lex":len(LEX),"test_tokens":bn,
           "script_tpw":script_chars/bn,"burg_tpw":burg_chars/bn,
           "cold":r_cold,"pretrained":r_pre,
           "token_amb":100*ta/tt}, open("burmese_results.json","w"))
