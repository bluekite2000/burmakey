"""
Iteration 2: syllable-level romanizer -> near-full corpus coverage.

myG2P aligns syllable splits with per-syllable romanizations; mining those
alignments yields a syllable->roman dictionary that romanizes ANY Burmese
word, not just the 24k dictionary entries.
"""
import re, json, random, collections

# ---- 1. mine syllable -> roman from myG2P alignments -------------------
syl_roman = collections.defaultdict(collections.Counter)
for line in open('/tmp/myg2p/ver2/myg2p.ver2.0.txt', encoding='utf8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 4 or '...' in p[1]: continue
    syls, roms = p[2].split(), p[3].split()
    if len(syls) != len(roms): continue
    for s, r in zip(syls, roms):
        r = re.sub(r"[.:'\-$]", "", r)
        if re.fullmatch(r"[a-z]+", r):
            syl_roman[s][r] += 1
SYL = {s: c.most_common(1)[0][0] for s, c in syl_roman.items()}
print(f"syllable->roman map: {len(SYL):,} syllables")

# ---- 2. syllable breaker (sylbreak logic) -------------------------------
BREAK = re.compile(r"(?<!္)([က-အဣ-ဪဿ၎])(?!်)")
def sylbreak(w):
    return [s for s in BREAK.sub(r" \1", w).split() if s]

# validate against myG2P's own splits
ok = tot = 0
for line in open('/tmp/myg2p/ver2/myg2p.ver2.0.txt', encoding='utf8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 3 or '...' in p[1]: continue
    tot += 1
    if sylbreak(p[1]) == p[2].split(): ok += 1
print(f"sylbreak accuracy vs myG2P ground truth: {100*ok/tot:.1f}%")

def romanize(w):
    out = []
    for s in sylbreak(w):
        r = SYL.get(s)
        if r is None: return None
        out.append(r)
    return "".join(out) if out else None

# ---- 3. corpus, full-vocabulary lexicon ---------------------------------
sents = []
for line in open('/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt',
                 encoding='utf8'):
    toks = [t.rsplit('/', 1)[0] for t in line.split()]
    toks = [t for t in toks if t and not re.fullmatch(r"[၀-၉0-9။၊.,!?]+", t)]
    if len(toks) >= 3: sents.append(toks)
random.seed(7); random.shuffle(sents)
TRAIN, TEST = sents[2000:], sents[:2000]

vocab = collections.Counter(w for s in TRAIN for w in s)
vocab.update(w for s in TEST for w in s)
LEX = {}
for w in vocab:
    r = romanize(w)
    if r: LEX[w] = r
FREQ = collections.Counter(w for s in TRAIN for w in s)
test_toks = [w for s in TEST for w in s]
cov = sum(1 for w in test_toks if w in LEX)
print(f"vocab {len(vocab):,} -> romanized {len(LEX):,}; "
      f"test-token coverage {100*cov/len(test_toks):.1f}%  (was 21.1%)")

# ---- 4. ambiguity, token-weighted ---------------------------------------
groups = collections.defaultdict(list)
for w, b in LEX.items(): groups[b].append(w)
ta = sum(1 for w in test_toks if w in LEX and len(groups[LEX[w]]) > 1)
print(f"Burglish token ambiguity on real text: {100*ta/cov:.1f}%")

# ---- 5. simulations ------------------------------------------------------
by_prefix = collections.defaultdict(list)
for w, b in LEX.items():
    for i in range(1, len(b)+1): by_prefix[b[:i]].append(w)
for p in by_prefix:
    by_prefix[p] = sorted(by_prefix[p], key=lambda w: -FREQ[w])[:50]

def simulate(shortlist=5, pretrain=False):
    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    learned_pref = collections.defaultdict(set)   # prefix -> learned words
    if pretrain:
        for s in TRAIN:
            kept = [w for w in s if w in LEX]
            for a, b in zip(kept, kept[1:]): bigram[a][b] += 0.2
    taps = n = zero = bar = full = 0
    for s in TEST:
        prev = None
        for w in s:
            if w not in LEX: prev = None; continue
            n += 1; sp = LEX[w]
            def score(x):
                v = FREQ[x] + 10*recency[x]
                if prev is not None: v += 100*bigram[prev][x]
                return v
            found = pick1 = None
            for k in range(0, len(sp)+1):
                pool = by_prefix[sp[:k]]
                lp = learned_pref.get(sp[:k])
                if lp: pool = set(pool) | lp
                cs = sorted(pool, key=score, reverse=True)[:shortlist]
                if w in cs: found, pick1 = k, cs[0] == w; break
            k = len(sp) if found is None else found
            taps += k + 1
            if found == 0: zero += 1
            if found is None: full += 1
            elif not pick1: bar += 1
            if w not in recency:
                b = LEX[w]
                learned_pref[""].add(w)
                for i in range(1, len(b)+1): learned_pref[b[:i]].add(w)
            recency[w] += 1
            if prev is not None: bigram[prev][w] += 1
            prev = w
    return dict(tpw=taps/n, n=n, zero=100*zero/n, bar=100*bar/n, full=100*full/n)

script = sum(len(w)+1 for w in test_toks if w in LEX)/cov
burg   = sum(len(LEX[w])+1 for w in test_toks if w in LEX)/cov
print(f"\nBASELINES over {cov:,} real tokens: script {script:.2f}  burglish {burg:.2f}")
for name, kw in [("cold shortlist5", {}), ("pretrained shortlist5", {"pretrain":True}),
                 ("pretrained shortlist3", {"pretrain":True,"shortlist":3})]:
    r = simulate(**kw)
    print(f"  {name:22}: {r['tpw']:.2f} taps/word  zero-key {r['zero']:.1f}%  "
          f"bar {r['bar']:.1f}%  full {r['full']:.1f}%")
    if name == "pretrained shortlist5": best = r
print(f"\nBEST vs script typing : {100*(best['tpw']-script)/script:+.1f}%")
print(f"BEST vs Burglish chat : {100*(best['tpw']-burg)/burg:+.1f}%  "
      f"+ ambiguity {100*ta/cov:.0f}% -> 0%")
json.dump({"syls":len(SYL),"lex":len(LEX),"cov":100*cov/len(test_toks),
  "amb":100*ta/cov,"script":script,"burg":burg,"best":best},
  open("burmese2_results.json","w"))
