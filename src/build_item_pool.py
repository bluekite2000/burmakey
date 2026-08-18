"""Build the guided-test item sets: 3 fixed anchors + a rotated pool.

Anchors stay identical across all testers, preserving clean between-user
comparison on the same text. The pool is chosen greedily for SYLLABLE
coverage, so each additional tester exercises vocabulary the previous ones
did not — which is what feeds the rules-G2P exception list and broadens the
variant-weight evidence.
"""
import json, re, random
import burmese2 as B
import g2p_rules as G

# candidate sentences: chat-length, fully typable by the v4-era engine
cands = []
for s in B.TEST:
    toks = [w for w in s if not re.fullmatch(r"[၀-၉0-9။၊.,!?]+", w)]
    if 3 <= len(toks) <= 7 and all(w in B.LEX for w in toks):
        cands.append(toks)
random.Random(5).shuffle(cands)

# anchors: the same first three every tester has typed so far
anchors = cands[:3]

# pool: greedy max-coverage of unseen syllables
seen = set()
for t in anchors:
    for w in t:
        seen.update(G.segment(w))
pool, rest = [], cands[3:]
while len(pool) < 60 and rest:
    best, gain = None, -1
    for t in rest[:800]:
        g = len({s for w in t for s in G.segment(w)} - seen)
        if g > gain:
            best, gain = t, g
    pool.append(best)
    for w in best:
        seen.update(G.segment(w))
    rest.remove(best)

fmt = lambda toks: {"my": "".join(toks), "burglish": " ".join(B.LEX[w] for w in toks)}
out = {
    "anchors": [fmt(t) for t in anchors],
    "pool": [fmt(t) for t in pool],
    # stress + free stay as before
}
json.dump(out, open("exercise_pool.json", "w"), ensure_ascii=False, indent=1)
allsyl = len(seen)
fixed = {s for t in cands[:10] for w in t for s in G.segment(w)}
print(f"anchors: {len(anchors)} | pool: {len(pool)} sentences")
print(f"syllable coverage: old fixed set {len(fixed)} -> anchors+pool {allsyl}")
