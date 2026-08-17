"""Simulated CHAT-register Burmese corpus (myPOS is news register).
Same method as the Lao study: messages assembled from high-frequency
conversational vocabulary; word order approximate, which understates
bigram gains. Tests the register the keyboard actually targets."""
import pickle, random, collections, statistics
D = pickle.load(open("mm_data.pkl","rb"))
LEX, FREQ, TRAIN = D["LEX"], D["FREQ"], D["TRAIN"]
random.seed(11)

# conversational core: top words are naturally chat particles/pronouns/verbs
CORE = [w for w, _ in FREQ.most_common(300) if w in LEX]
MID  = [w for w, _ in FREQ.most_common(3000)[300:] if w in LEX]
msgs = []
for _ in range(600):
    n = random.randint(3, 8)
    msgs.append([random.choice(CORE) if random.random() < 0.7
                 else random.choice(MID) for _ in range(n)])
stream = [w for m in msgs for w in m]
print(f"simulated chat: {len(msgs)} messages, {len(stream):,} words, "
      f"{len(set(stream)):,} distinct")

groups = collections.defaultdict(list)
for w, b in LEX.items(): groups[b].append(w)
amb = sum(1 for w in stream if len(groups[LEX[w]]) > 1)
print(f"Burglish ambiguity in chat register: {100*amb/len(stream):.1f}%")

by_prefix = collections.defaultdict(list)
for w, s in LEX.items():
    for i in range(1, len(s)+1): by_prefix[s[:i]].append(w)
for p in by_prefix:
    by_prefix[p] = sorted(by_prefix[p], key=lambda w: -FREQ[w])[:50]
BIG = collections.defaultdict(collections.Counter)
for s in TRAIN:
    kept = [w for w in s if w in LEX]
    for a, b in zip(kept, kept[1:]): BIG[a][b] += 0.2

recency = collections.Counter(); lbig = collections.defaultdict(collections.Counter)
lpref = collections.defaultdict(set)
taps = zero = 0
prev = None
for m in msgs:
    prev = None
    for w in m:
        sp = LEX[w]
        def score(x):
            v = FREQ[x] + 10*recency[x]
            if prev is not None: v += 100*(BIG[prev][x] + lbig[prev][x])
            return v
        found = None
        for k in range(0, len(sp)+1):
            pool = by_prefix[sp[:k]]
            lp = lpref.get(sp[:k])
            if lp: pool = set(pool) | lp
            cs = sorted(pool, key=score, reverse=True)[:5]
            if w in cs: found = k; break
        k = len(sp) if found is None else found
        taps += k + 1
        if found == 0: zero += 1
        if w not in recency:
            for i in range(0, len(sp)+1): lpref[sp[:i]].add(w)
        recency[w] += 1
        if prev is not None: lbig[prev][w] += 1
        prev = w

n = len(stream)
burg = statistics.mean(len(LEX[w])+1 for w in stream)
script = statistics.mean(len(w)+1 for w in stream)
print(f"\nscript typed out : {script:.2f} taps/word")
print(f"Burglish typed   : {burg:.2f} taps/word  [{100*amb/n:.0f}% ambiguous]")
print(f"DRAFT 4 engine   : {taps/n:.2f} taps/word  zero-key {100*zero/n:.1f}%")
print(f"vs script  {100*(taps/n-script)/script:+.1f}%   "
      f"vs Burglish {100*(taps/n-burg)/burg:+.1f}%")
