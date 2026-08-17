"""
Long-run simulation: a multi-hour conversation spanning ~25 topics,
common chat plus rare vocabulary, measured on all four systems.
"""
import json, re, random, collections, statistics
import optimise3 as O3
from typist import lex, FREQ, karaoke

random.seed(42)
enc3 = O3.make_encoder(json.load(open("cfg3.json")))

# ---------------- topic vocabulary, broad span ----------------------------
TOPICS = {
 "greetings":  ["hello","good","name","friend","meet","thank","sorry"],
 "food":       ["eat","rice","food","delicious","hungry","noodle","fish","chicken","fruit","sweet","spicy","drink","cook"],
 "family":     ["mother","father","sister","brother","child","grandmother","aunt","uncle","wife","husband"],
 "work":       ["work","money","busy","boss","tired","office","salary","meeting"],
 "school":     ["study","book","teacher","school","learn","read","write","exam","student"],
 "weather":    ["rain","hot","cold","sun","wind","cloud","storm","season","flood"],
 "feelings":   ["happy","sad","love","like","angry","afraid","miss","beautiful","funny","worry","lonely"],
 "travel":     ["go","come","car","bus","road","village","city","far","near","travel","boat","airplane","ticket"],
 "shopping":   ["buy","sell","price","expensive","cheap","clothes","shop","market"],
 "time":       ["today","tomorrow","yesterday","now","evening","night","hour","year","month","week","morning"],
 "health":     ["sick","doctor","medicine","hospital","pain","head","stomach","fever","healthy","die"],
 "body":       ["hand","eye","ear","mouth","foot","hair","heart","blood","skin","bone"],
 "house":      ["house","door","window","roof","kitchen","bed","table","chair","garden"],
 "nature":     ["tree","river","mountain","forest","flower","bird","dog","cat","snake","elephant","buffalo"],
 "farming":    ["field","plant","harvest","grow","seed","farmer","buffalo","garden"],
 "religion":   ["monk","temple","merit","pray","festival","spirit","buddha","ceremony"],
 "numbers":    ["one","two","three","four","five","ten","hundred","thousand","many","few","half"],
 "colors":     ["red","white","black","green","blue","yellow","color"],
 "tech":       ["telephone","photograph","electric","machine","radio","television","computer"],
 "government": ["country","law","police","soldier","government","leader","tax","border","war","peace"],
 "sports":     ["play","ball","run","swim","win","lose","strong","fast"],
 "music":      ["sing","song","dance","music","drum","festival"],
 "emotion2":   ["speak","say","tell","ask","answer","listen","hear","see","look","think","know","understand","remember","forget"],
 "actions":    ["walk","sit","stand","sleep","wake","wash","open","close","give","take","hold","throw","cut","build"],
 "qualities":  ["big","small","new","old","good","bad","long","short","heavy","light","clean","dirty","full","empty"],
}

def topic_words(keys):
    hits = {}
    for w, e in lex.items():
        g = e["g"].lower()
        for k in keys:
            if re.search(r"\b" + re.escape(k), g):
                if w not in hits or FREQ[w] > FREQ[hits[w][0]]:
                    hits[w] = (w, k)
    return sorted(hits, key=lambda w: -FREQ[w])[:28]

TOPIC_VOCAB = {t: topic_words(ks) for t, ks in TOPICS.items()}
CORE = sorted(lex, key=lambda w: -FREQ[w])[:60]

# ---------------- conversation generator ----------------------------------
def gen_convo(n_msgs=600):
    msgs, order = [], list(TOPICS)
    random.shuffle(order)
    ti, in_topic = 0, 0
    for m in range(n_msgs):
        if in_topic >= random.randint(10, 22):
            ti = (ti + 1) % len(order); in_topic = 0
        in_topic += 1
        tv = TOPIC_VOCAB[order[ti]]
        n = random.randint(3, 8)
        words = []
        for _ in range(n):
            if random.random() < 0.55:
                words.append(random.choice(CORE))
            elif random.random() < 0.8:
                words.append(random.choice(tv[:12]))     # common topic words
            else:
                words.append(random.choice(tv))          # incl. rare tail
        msgs.append(words)
    return msgs

msgs = gen_convo()
stream = [w for ws in msgs for w in ws]
print(f"generated {len(msgs)} messages, {len(stream):,} words, "
      f"{len(set(stream)):,} distinct, {len(TOPICS)} topics")

# ---------------- engines --------------------------------------------------
kk_spell = {w: karaoke(lex[w]["syl"]) for w in lex}
d3_spell = {w: enc3(lex[w]["syl"]) for w in lex}
SHORT = 3

def run(input_spell, learning=True):
    # beam-limited candidates, like a real engine: static top-50 by frequency
    # per prefix, plus any learned (recent/bigram) words matching the prefix
    by_prefix = collections.defaultdict(list)
    for w, s in input_spell.items():
        by_prefix[""].append(w)
        for i in range(1, len(s)+1):
            by_prefix[s[:i]].append(w)
    for p in by_prefix:
        by_prefix[p] = sorted(by_prefix[p], key=lambda w: -FREQ[w])[:50]
    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    prev = None
    def score(w):
        s = FREQ[w]
        if learning:
            s += 10*recency[w] + (100*bigram[prev][w] if prev else 0)
        return s
    per = []
    zero = bar = full = 0
    for w in stream:
        s = input_spell[w]
        found = pick1 = None
        learned = [x for x in recency if input_spell[x].startswith] if False else None
        for k in range(0, len(s)+1):
            pool = by_prefix[s[:k]]
            if learning and recency:
                pfx = s[:k]
                extra = [x for x in recency if input_spell[x].startswith(pfx)]
                pool = set(pool) | set(extra)
            cs = sorted(pool, key=score, reverse=True)[:SHORT]
            if w in cs:
                found, pick1 = k, cs[0] == w
                break
        if found is None:
            k, pick1 = len(s), True; full += 1
        else:
            k = found
        per.append(k + 1)
        if found == 0: zero += 1
        if not pick1: bar += 1
        if learning:
            recency[w] += 1
            if prev is not None: bigram[prev][w] += 1
        prev = w
    n = len(stream)
    return dict(per=per, taps=sum(per), tpw=sum(per)/n,
                zero=100*zero/n, bar=100*bar/n, full=100*full/n)

def typed_out(spell):
    per = [len(spell[w]) + 1 for w in stream]
    return dict(per=per, taps=sum(per), tpw=sum(per)/len(stream),
                zero=0.0, bar=0.0, full=100.0)

kg = collections.Counter(kk_spell.values())
dg = collections.Counter(d3_spell.values())
amb_kk = 100*sum(1 for w in stream if kg[kk_spell[w]] > 1)/len(stream)
amb_d3 = 100*sum(1 for w in stream if dg[d3_spell[w]] > 1)/len(stream)

R = {
 "karaoke typed out (today)":       (typed_out(kk_spell), amb_kk),
 "karaoke + learning engine":       (run(kk_spell), amb_kk),
 "draft 3 typed + learning":        (run(d3_spell), amb_d3),
 "DRAFT 4 (karaoke in, clear out)": (run(kk_spell), amb_d3),
}
print()
print(f"{'':34}{'taps':>8}{'t/word':>8}{'0-key':>8}{'bar-pick':>9}{'full':>7}{'amb out':>8}")
for n, (r, a) in R.items():
    print(f"{n:34}{r['taps']:>8,}{r['tpw']:>8.2f}{r['zero']:>7.1f}%"
          f"{r['bar']:>8.1f}%{r['full']:>6.1f}%{a:>7.0f}%")

base = R["karaoke typed out (today)"][0]
d4 = R["DRAFT 4 (karaoke in, clear out)"][0]
print(f"\nDRAFT 4 vs today: {d4['taps']-base['taps']:+,} taps "
      f"({100*(d4['taps']-base['taps'])/base['taps']:+.1f}%), "
      f"ambiguity {amb_kk:.0f}% -> {amb_d3:.0f}%")

# ---------------- warm-up curve -------------------------------------------
print("\nLEARNING CURVE (draft 4 taps/word by conversation stage)")
per = d4["per"]; base_per = base["per"]
q = len(per)//5
for i in range(5):
    seg = per[i*q:(i+1)*q]; bseg = base_per[i*q:(i+1)*q]
    print(f"   words {i*q:>5,}-{(i+1)*q:>5,}:  draft 4 {statistics.mean(seg):.2f}"
          f"   today {statistics.mean(bseg):.2f}"
          f"   saving {100*(1-statistics.mean(seg)/statistics.mean(bseg)):.0f}%")

# ---------------- by rarity band -------------------------------------------
rank = {w: i for i, w in enumerate(sorted(lex, key=lambda w: -FREQ[w]))}
bands = [("common (top 200)", 0, 200), ("mid (200-2000)", 200, 2000),
         ("rare (2000+)", 2000, 10**9)]
print("\nBY WORD RARITY (draft 4 vs today, taps/word)")
for name, lo, hi in bands:
    idx = [i for i, w in enumerate(stream) if lo <= rank[w] < hi]
    if not idx: continue
    print(f"   {name:18} n={len(idx):>5,}  draft4 "
          f"{statistics.mean([per[i] for i in idx]):.2f}  today "
          f"{statistics.mean([base_per[i] for i in idx]):.2f}")
