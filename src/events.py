"""Generate the keystroke-by-keystroke event stream for the video replay."""
import json, collections
import optimise3 as O3
from typist import lex, FREQ, karaoke

enc3 = O3.make_encoder(json.load(open("cfg3.json")))
rows = json.load(open("convo.json"))["rows"]

kk_spell = {w: karaoke(lex[w]["syl"]) for w in lex}
d3_spell = {w: enc3(lex[w]["syl"]) for w in lex}
kk_groups = collections.Counter(kk_spell.values())

by_prefix = collections.defaultdict(list)
for w, s in kk_spell.items():
    by_prefix[""].append(w)
    for i in range(1, len(s) + 1):
        by_prefix[s[:i]].append(w)

recency = collections.Counter()
bigram = collections.defaultdict(collections.Counter)
prev = None
SHORT = 3

def score(w):
    s = FREQ[w]
    s += 10 * recency[w]
    if prev is not None:
        s += 100 * bigram[prev][w]
    return s

def cands_at(prefix):
    return sorted(by_prefix[prefix], key=score, reverse=True)[:SHORT]

def cand_view(cs):
    return [[w, lex[w]["g"][:22], d3_spell[w]] for w in cs]

msgs = []
tot = {"L": 0, "R": 0}
for r in rows:
    words = r["words"]
    left_steps, right_steps = [], []
    for w, g in words:
        ks = kk_spell[w]
        # LEFT: type every letter, then space
        for ch in ks:
            left_steps.append({"t": "key", "c": ch})
        left_steps.append({"t": "commit", "out": ks, "amb": kk_groups[ks]})
        tot["L"] += len(ks) + 1
        # RIGHT: learning engine
        found = pick = None
        for k in range(0, len(ks) + 1):
            cs = cands_at(ks[:k])
            if k > 0:
                right_steps.append({"t": "key", "c": ks[k-1], "bar": cand_view(cs)})
            else:
                right_steps.append({"t": "bar", "bar": cand_view(cs)})
            if w in cs:
                found, pick = k, cs.index(w)
                break
        if found is None:
            pick = 0
        right_steps.append({"t": "commit", "out": w, "rom": d3_spell[w],
                            "pick": pick, "g": g[:22]})
        tot["R"] += (found if found is not None else len(ks)) + 1
        recency[w] += 1
        if prev is not None:
            bigram[prev][w] += 1
        prev = w
    msgs.append({"who": r["who"], "L": left_steps, "R": right_steps,
                 "gloss": " · ".join(g.split()[0] if g else "?" for _, g in words)})

json.dump({"msgs": msgs, "tot": tot}, open("events.json", "w"),
          ensure_ascii=False, separators=(",", ":"))
import os
print(f"messages {len(msgs)}  left taps {tot['L']}  right taps {tot['R']}  "
      f"file {os.path.getsize('events.json'):,} bytes")
