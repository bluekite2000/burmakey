"""
Long-horizon learning dynamics: what the engine does after day one.

Every earlier number in this project comes from a SINGLE pass over held-out
text with fresh state. That cannot answer the questions that decide whether
the on-device learning design actually survives contact with weeks of use:

  Q1  Does learning keep paying, saturate, or start to hurt?
  Q2  What happens when a user changes topic — does the learned prior get in
      the way, and for how long?
  Q3  How much does performance vary BETWEEN users? (We have a mean and no
      distribution.)
  Q4  Does the per-user state stay inside a sane on-device budget, or does the
      bigram table grow without bound?
  Q5  The shipped engine scores recency as an UNBOUNDED count (+10 per use).
      Over thousands of words, does that need a decay or a cap?

This is deliberately NOT a competitor benchmark. Simulated chatters cannot
manufacture information about human behaviour — they can only resample the
corpus statistics we already have. What they CAN do is exercise the engine's
own state over a horizon the single-pass test never reaches. Every result here
is a statement about the engine's mechanics, not about people.

Design
  topics    derived by k-means over content-word tf-idf (myPOS has no document
            or topic metadata; adjacent lines are unrelated), cached to disk
  split     the bigram prior is pretrained on one half of the corpus; every
            user's message stream is drawn from a DISJOINT held-out half, and
            sampled WITHOUT REPLACEMENT within a user, so nothing is scored
            twice for the same user and no user ever types text the prior saw
  users     each has a primary topic and keeps it, so vocabularies genuinely
            differ between users (that spread is Q3)
  variants  the same streams replayed under four engine rules:
              frozen = shipped prior, on-device learning OFF (the control
                       that says what learning is actually worth)
              raw    = what ships today (score += 10 * lifetime count)
              decay  = exponential forgetting, half-life HALFLIFE words
              cap    = lifetime count clipped at RECENCY_CAP
  priming   Q2 is a separate within-topic experiment, NOT a cohort split. An
            earlier cohort design compared users who switched topic against
            users who did not, but those are different people typing
            different text, so it measured topic difficulty rather than
            switching. Instead all three arms type the IDENTICAL evaluation
            text and differ only in the history the engine carries in:
            cold / primed-on-same-topic / primed-on-different-topic.

Nothing here is evidence about people. It is evidence about the engine.

Usage:  python3 longrun.py [--quick] [--users N] [--days N] [--msgs N]
Reads the same myG2P/myPOS clones as burmese2.py (see README).
"""
import sys, json, math, random, collections, os, time

import burmese2 as B   # lexicon + romanizer + corpus, no report side effects

# ---------------------------------------------------------------- config
USERS      = 24
DAYS       = 20
MSGS       = 30        # messages per user per day
TOPICS     = 10
MAXLEN     = 12        # chat-ish message length ceiling, in words
SHORTLIST  = 5
HALFLIFE   = 200.0     # words, for the "decay" variant
RECENCY_CAP = 5        # for the "cap" variant
SEED       = 20260817
CACHE      = "longrun_topics.json"


# ============================================================ topics
def content_sentences():
    """Sentences as (all_tokens, content_tokens) using myPOS's own tags."""
    out = []
    path = '/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt'
    for line in open(path, encoding='utf8'):
        toks, content = [], []
        for t in line.split():
            if '/' not in t:
                continue
            w, tag = t.rsplit('/', 1)
            if not w or tag == 'punc':
                continue
            toks.append(w)
            if tag in ('n', 'v', 'adj'):
                content.append(w)
        if 3 <= len(toks) <= MAXLEN and len(content) >= 2:
            out.append((toks, content))
    return out


def kmeans_topics(sents, k=TOPICS, iters=12, seed=SEED):
    """Tiny sparse k-means over tf-idf of content words. Vocabulary-disjoint
    clusters are what the experiment needs; semantic tidiness is not."""
    df = collections.Counter()
    for _, c in sents:
        df.update(set(c))
    n = len(sents)
    idf = {w: math.log(n / (1 + c)) for w, c in df.items() if c >= 5}

    vecs = []
    for _, c in sents:
        v = collections.defaultdict(float)
        for w in c:
            if w in idf:
                v[w] += idf[w]
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({w: x / norm for w, x in v.items()})

    rng = random.Random(seed)
    cents = [dict(vecs[i]) for i in rng.sample(range(len(vecs)), k)]
    assign = [0] * len(vecs)
    for it in range(iters):
        moved = 0
        for i, v in enumerate(vecs):
            best, bs = 0, -1.0
            for ci, c in enumerate(cents):
                if len(v) > len(c):
                    s = sum(x * v.get(w, 0.0) for w, x in c.items())
                else:
                    s = sum(x * c.get(w, 0.0) for w, x in v.items())
                if s > bs:
                    bs, best = s, ci
            if assign[i] != best:
                moved += 1
                assign[i] = best
        acc = [collections.defaultdict(float) for _ in range(k)]
        cnt = [0] * k
        for i, v in enumerate(vecs):
            a = acc[assign[i]]
            cnt[assign[i]] += 1
            for w, x in v.items():
                a[w] += x
        for ci in range(k):
            if not cnt[ci]:
                cents[ci] = dict(vecs[rng.randrange(len(vecs))])
                continue
            c = {w: x / cnt[ci] for w, x in acc[ci].items()}
            c = dict(sorted(c.items(), key=lambda kv: -kv[1])[:400])  # keep sparse
            norm = math.sqrt(sum(x * x for x in c.values())) or 1.0
            cents[ci] = {w: x / norm for w, x in c.items()}
        if moved < len(vecs) * 0.005:
            break
    return assign, it + 1


# ============================================================ engine
class Engine:
    """burmese2's ranker, with per-user persistent state and a pluggable
    recency rule. Scoring is identical to the shipped engine when
    variant == 'raw'."""

    def __init__(self, prior_bigram, variant="raw"):
        # variant "frozen" = the shipped prior with on-device learning switched
        # OFF. It is the control that says what learning is actually worth.
        self.variant = variant
        self.learn = variant != "frozen"
        self.recency = collections.Counter()
        self.bigram = collections.defaultdict(collections.Counter)
        for a, bs in prior_bigram.items():          # copy, never share
            self.bigram[a] = collections.Counter(bs)
        self.learned_pref = collections.defaultdict(set)
        self.prev = None
        self.seen_words = 0

    def _rec(self, x):
        v = self.recency.get(x, 0.0)
        if v == 0.0:
            return 0.0
        if self.variant == "cap":
            return min(v, RECENCY_CAP)
        return v          # 'raw' and 'decay' both store the value directly;
                          # 'decay' applies forgetting at write time

    def type_word(self, w, code):
        """Returns (keys_pressed, candidate_slot or None)."""
        rec, big, prev = self._rec, self.bigram, self.prev

        def score(x):
            v = B.FREQ[x] + 10 * rec(x)
            if prev is not None:
                v += 100 * big[prev][x]
            return v

        found = slot = None
        for kk in range(0, len(code) + 1):
            pool = B.by_prefix[code[:kk]]
            lp = self.learned_pref.get(code[:kk])
            if lp:
                pool = set(pool) | lp
            cs = sorted(pool, key=score, reverse=True)[:SHORTLIST]
            if w in cs:
                found, slot = kk, cs.index(w)
                break

        if not self.learn:
            self.prev = w
            self.seen_words += 1
            return (len(code) + 1, None) if found is None else (found + 1, slot)

        if self.variant == "decay":
            # forget before recording, so the newest use always weighs 1.0
            f = 0.5 ** (1.0 / HALFLIFE)
            for x in list(self.recency):
                v = self.recency[x] * f
                if v < 0.01:
                    del self.recency[x]
                else:
                    self.recency[x] = v

        if w not in self.recency:
            self.learned_pref[""].add(w)
            for i in range(1, len(code) + 1):
                self.learned_pref[code[:i]].add(w)
        self.recency[w] += 1
        if self.prev is not None:
            self.bigram[self.prev][w] += 1
        self.prev = w
        self.seen_words += 1

        if found is None:
            return len(code) + 1, None
        return found + 1, slot

    def end_message(self):
        self.prev = None

    def state_size(self, prior_pairs=0, prior_heads=0):
        """State ABOVE the shipped prior — the part that actually grows on the
        device. The prior is a fixed shipped asset, not per-user growth."""
        pairs = sum(len(v) for v in self.bigram.values())
        return {"recency_entries": len(self.recency),
                "user_bigram_heads": len(self.bigram) - prior_heads,
                "user_bigram_pairs": pairs - prior_pairs,
                "learned_prefixes": len(self.learned_pref),
                "approx_kb": round((len(self.recency) * 24
                                    + (pairs - prior_pairs) * 32
                                    + len(self.learned_pref) * 20) / 1024.0, 1)}


# ============================================================ priming
def priming_experiment(sents, pools, usable, prior_bigram, rng,
                       warm_msgs=300, eval_msgs=150, chunks=5):
    """Q2, done without a confound.

    The cohort version of this question compared users who switched topic
    against users who did not — but those are different people typing
    different text, so the difference measured topic difficulty, not
    switching. Here every arm types the IDENTICAL evaluation text; only the
    history the engine carries into it differs:

        cold          fresh engine (shipped prior only)
        primed-right  warmed on `warm_msgs` of the SAME topic
        primed-wrong  warmed on `warm_msgs` of a DIFFERENT topic

    primed-wrong worse than cold  =>  the learned state actively hurts after
    a topic change. Chunked results show how long that lasts.
    """
    out = []
    for a_i in range(len(usable)):
        ta = usable[a_i]
        tb = usable[(a_i + 1) % len(usable)]
        pa, pb = pools[ta], pools[tb]
        if len(pb) < warm_msgs + eval_msgs or len(pa) < warm_msgs:
            continue
        warm_b = pb[:warm_msgs]
        eval_b = pb[warm_msgs:warm_msgs + eval_msgs]   # disjoint from warm_b
        warm_a = pa[:warm_msgs]

        def run(warm):
            eng = Engine(prior_bigram, variant="raw")
            for si in warm:
                for w in sents[si][0]:
                    if w in B.LEX:
                        eng.type_word(w, B.LEX[w])
                    else:
                        eng.prev = None
                eng.end_message()
            per_chunk, taps, n = [], 0, 0
            size = max(1, len(eval_b) // chunks)
            ct, cn = 0, 0
            for j, si in enumerate(eval_b):
                for w in sents[si][0]:
                    if w not in B.LEX:
                        eng.prev = None
                        continue
                    k, _ = eng.type_word(w, B.LEX[w])
                    taps += k; n += 1; ct += k; cn += 1
                eng.end_message()
                if (j + 1) % size == 0 and cn:
                    per_chunk.append(ct / cn); ct = cn = 0
            return (taps / n if n else float("nan")), per_chunk

        cold, cold_c = run([])
        right, right_c = run(warm_b)
        wrong, wrong_c = run(warm_a)
        out.append({"topic_a": ta, "topic_b": tb, "cold": cold,
                    "primed_right": right, "primed_wrong": wrong,
                    "cold_chunks": cold_c, "wrong_chunks": wrong_c,
                    "right_chunks": right_c})
    return out


# ============================================================ experiment
def main(argv):
    global USERS, DAYS, MSGS
    if "--quick" in argv:
        USERS, DAYS, MSGS = 6, 6, 12
    for flag, name in (("--users", "USERS"), ("--days", "DAYS"), ("--msgs", "MSGS")):
        if flag in argv:
            globals()[name] = int(argv[argv.index(flag) + 1])

    t0 = time.time()
    rng = random.Random(SEED)

    sents = content_sentences()
    print(f"corpus: {len(sents):,} chat-length sentences (<= {MAXLEN} words)")

    # ---- topics (cached) --------------------------------------------
    if os.path.exists(CACHE):
        blob = json.load(open(CACHE))
        if blob.get("n") == len(sents) and blob.get("k") == TOPICS:
            assign = blob["assign"]
            print(f"topics: loaded {TOPICS} cached clusters")
        else:
            assign = None
    else:
        assign = None
    if assign is None:
        print(f"topics: clustering {len(sents):,} sentences into {TOPICS} ...")
        assign, iters = kmeans_topics(sents)
        json.dump({"n": len(sents), "k": TOPICS, "assign": assign}, open(CACHE, "w"))
        print(f"topics: converged in {iters} iterations, cached")

    by_topic = collections.defaultdict(list)
    for i, a in enumerate(assign):
        by_topic[a].append(i)
    sizes = sorted((len(v) for v in by_topic.values()), reverse=True)
    print(f"topic sizes: {sizes}")

    # ---- split: prior half vs stream half (disjoint) ----------------
    idx = list(range(len(sents)))
    rng.shuffle(idx)
    half = len(idx) // 2
    prior_idx, stream_idx = set(idx[:half]), set(idx[half:])

    prior_bigram = collections.defaultdict(collections.Counter)
    for i in prior_idx:
        kept = [w for w in sents[i][0] if w in B.LEX]
        for a, b in zip(kept, kept[1:]):
            prior_bigram[a][b] += 0.2
    prior_heads = len(prior_bigram)
    prior_pairs = sum(len(v) for v in prior_bigram.values())
    print(f"prior pretrained on {len(prior_idx):,} sentences; "
          f"{len(stream_idx):,} held out for user streams")
    print(f"shipped prior: {prior_heads:,} heads / {prior_pairs:,} pairs "
          f"(fixed asset, excluded from per-user growth below)")

    # per-topic pools drawn only from the held-out half
    pools = {t: [i for i in v if i in stream_idx] for t, v in by_topic.items()}
    for t in pools:
        rng.shuffle(pools[t])
    usable = [t for t in pools if len(pools[t]) >= 200]
    print(f"usable topics: {len(usable)} "
          f"(pool sizes {[len(pools[t]) for t in usable]})")

    # ---- build per-user streams, disjoint, no repeats within a user --
    need = DAYS * MSGS
    cursor = collections.Counter()
    users = []
    for u in range(USERS):
        users.append({"id": u, "primary": usable[u % len(usable)]})

    def take(topic, n):
        p = pools[topic]
        c = cursor[topic]
        got = p[c:c + n]
        cursor[topic] = c + len(got)
        if len(got) < n:                          # wrap; recorded in the report
            cursor[topic] = n - len(got)
            got = got + p[:n - len(got)]
        return got

    reuse = False
    for uu in users:
        stream = []
        for d in range(1, DAYS + 1):
            stream.append(take(uu["primary"], MSGS))
        uu["stream"] = stream
    for t in usable:
        if cursor[t] > len(pools[t]):
            reuse = True
    print(f"streams built: {USERS} users x {DAYS} days x {MSGS} msgs"
          f"{'  (WARNING: pool wrapped, some sentences reused across users)' if reuse else ''}")

    # ---- run the three variants over identical streams ---------------
    variants = ["frozen", "raw", "decay", "cap"]
    results = {v: {"daily": collections.defaultdict(list), "per_user": [],
                   "state": collections.defaultdict(list)} for v in variants}
    results["words"] = collections.defaultdict(list)

    for v in variants:
        for uu in users:
            eng = Engine(prior_bigram, variant=v)
            per_day = []
            for d, batch in enumerate(uu["stream"], 1):
                taps = n = zero = top1 = bar = full = 0
                for si in batch:
                    toks = sents[si][0]
                    for w in toks:
                        if w not in B.LEX:
                            eng.prev = None
                            continue
                        k, slot = eng.type_word(w, B.LEX[w])
                        taps += k
                        n += 1
                        if slot is None:
                            full += 1
                        else:
                            if k == 1:
                                zero += 1
                            if slot == 0:
                                top1 += 1
                            else:
                                bar += 1
                    eng.end_message()
                if n == 0:
                    continue
                rec = dict(tpw=taps / n, zero=100 * zero / n, top1=100 * top1 / n,
                           bar=100 * bar / n, full=100 * full / n, n=n)
                per_day.append(rec)
                results[v]["daily"][d].append(rec["tpw"])
                if v == "raw":
                    results["words"][d].append(n)
                if uu["id"] == 0:
                    results[v]["state"][d] = eng.state_size(
                        prior_pairs, prior_heads)
            if per_day:
                results[v]["per_user"].append({
                    "id": uu["id"],
                    "day1": per_day[0]["tpw"],
                    "last": per_day[-1]["tpw"],
                    "mean": sum(p["tpw"] for p in per_day) / len(per_day)})
        print(f"  variant {v:5} done  ({time.time()-t0:.0f}s elapsed)")

    prime = priming_experiment(sents, pools, usable, prior_bigram, rng,
                               warm_msgs=DAYS * MSGS // 2,
                               eval_msgs=max(40, DAYS * MSGS // 4))
    print(f"  priming experiment done  ({time.time()-t0:.0f}s elapsed)")

    # ---- report -------------------------------------------------------
    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    print("\n" + "=" * 72)
    print("Q1  WHAT IS LEARNING WORTH, DAY BY DAY?")
    print("    'frozen' = shipped prior, learning OFF. The gap is the answer;")
    print("    a widening gap means learning compounds, a flat one means it")
    print("    saturates after the first day.")
    print("=" * 72)
    print("day  " + "".join(f"{v:>9}" for v in variants) + "     gain%   words")
    for d in range(1, DAYS + 1):
        fz = mean(results["frozen"]["daily"][d])
        rw = mean(results["raw"]["daily"][d])
        wl = sum(results["words"][d]) / max(1, len(results["words"][d]))
        print(f"{d:>3}  " + "".join(
            f"{mean(results[v]['daily'][d]):>9.3f}" for v in variants)
            + f"{100*(fz-rw)/fz:>10.1f}{wl:>8.0f}")
    fz1, rw1 = mean(results["frozen"]["daily"][1]), mean(results["raw"]["daily"][1])
    fzL = mean(results["frozen"]["daily"][DAYS])
    rwL = mean(results["raw"]["daily"][DAYS])
    print(f"\n  day 1   learning saves {100*(fz1-rw1)/fz1:.1f}%")
    print(f"  day {DAYS:<3} learning saves {100*(fzL-rwL)/fzL:.1f}%"
          f"   -> {'COMPOUNDS' if (fzL-rwL)/fzL > (fz1-rw1)/fz1 * 1.15 else 'SATURATES'}")

    print("\n" + "=" * 72)
    print("Q2  DOES A LEARNED PRIOR HURT AFTER A TOPIC CHANGE?")
    print("    Identical evaluation text in all three arms; only the engine's")
    print("    history differs. (taps/word, mean over topic pairs)")
    print("=" * 72)
    if prime:
        cold = mean([r["cold"] for r in prime])
        right = mean([r["primed_right"] for r in prime])
        wrong = mean([r["primed_wrong"] for r in prime])
        print(f"  cold (no history)          {cold:.3f}")
        print(f"  primed on the SAME topic   {right:.3f}   ({100*(right-cold)/cold:+.1f}% vs cold)")
        print(f"  primed on a DIFFERENT topic{wrong:>7.3f}   ({100*(wrong-cold)/cold:+.1f}% vs cold)")
        verdict = ("the stale prior HURTS" if wrong > cold * 1.005
                   else "the stale prior is harmless")
        print(f"\n  verdict: {verdict}")
        print("\n  recovery, by fifth of the evaluation stream:")
        print("  chunk        cold   primed-wrong   primed-right")
        nc = min(len(r["cold_chunks"]) for r in prime)
        for c in range(nc):
            print(f"  {c+1:>5}  {mean([r['cold_chunks'][c] for r in prime]):>10.3f}"
                  f"{mean([r['wrong_chunks'][c] for r in prime]):>15.3f}"
                  f"{mean([r['right_chunks'][c] for r in prime]):>15.3f}")
        print(f"\n  ({len(prime)} topic pairs)")
    else:
        print("  skipped: topic pools too small at this scale")

    print("\n" + "=" * 72)
    print("Q3  BETWEEN-USER SPREAD (variant raw, mean taps/word per user)")
    print("=" * 72)
    ms = sorted(u["mean"] for u in results["raw"]["per_user"])
    if ms:
        print(f"  n={len(ms)}  min {ms[0]:.3f}  p25 {ms[len(ms)//4]:.3f}  "
              f"median {ms[len(ms)//2]:.3f}  p75 {ms[3*len(ms)//4]:.3f}  "
              f"max {ms[-1]:.3f}")
        print(f"  spread max-min = {ms[-1]-ms[0]:.3f} taps/word "
              f"({100*(ms[-1]-ms[0])/ms[len(ms)//2]:.0f}% of median)")

    print("\n" + "=" * 72)
    print("Q4  ON-DEVICE STATE GROWTH (user 0, variant raw)")
    print("=" * 72)
    print("    (state ABOVE the shipped prior — what actually grows per user)")
    print("day  recency  user_heads  user_pairs  prefixes   approx_KB")
    for d in sorted(results["raw"]["state"]):
        st = results["raw"]["state"][d]
        print(f"{d:>3}{st['recency_entries']:>9}{st['user_bigram_heads']:>12}"
              f"{st['user_bigram_pairs']:>12}{st['learned_prefixes']:>10}"
              f"{st['approx_kb']:>12.1f}")
    ds = sorted(results["raw"]["state"])
    if len(ds) >= 2:
        a, b = results["raw"]["state"][ds[0]], results["raw"]["state"][ds[-1]]
        span = ds[-1] - ds[0]
        if span:
            print(f"\n  growth {a['approx_kb']:.1f} -> {b['approx_kb']:.1f} KB over "
                  f"{span} days = {(b['approx_kb']-a['approx_kb'])/span:.2f} KB/day"
                  f"  (~{(b['approx_kb']-a['approx_kb'])/span*365:.0f} KB/year)")

    print("\n" + "=" * 72)
    print("Q5  RECENCY RULE: does the unbounded count need decay or a cap?")
    print("=" * 72)
    for v in variants:
        d1 = mean(results[v]["daily"][1])
        dl = mean(results[v]["daily"][DAYS])
        allm = mean([x for d in results[v]["daily"] for x in results[v]["daily"][d]])
        print(f"  {v:6} day1 {d1:.3f}  day{DAYS} {dl:.3f}  overall {allm:.3f}  "
              f"({100*(dl-d1)/d1:+.1f}% day1->day{DAYS})")

    out = {
        "config": {"users": USERS, "days": DAYS, "msgs": MSGS,
                   "topics": TOPICS,
                   "maxlen": MAXLEN, "halflife": HALFLIFE,
                   "recency_cap": RECENCY_CAP, "seed": SEED,
                   "pool_wrapped": reuse},
        "daily": {v: {str(d): mean(results[v]["daily"][d])
                      for d in range(1, DAYS + 1)} for v in variants},
        "priming": prime,
        "per_user": results["raw"]["per_user"],
        "state": {str(d): results["raw"]["state"][d]
                  for d in sorted(results["raw"]["state"])},
    }
    json.dump(out, open("longrun_results.json", "w"), indent=1)
    print(f"\nwrote longrun_results.json  ({time.time()-t0:.0f}s total)")


if __name__ == "__main__":
    main(sys.argv[1:])
