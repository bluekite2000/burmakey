"""Two friends texting. Simulate the whole conversation on both keyboards."""
import json, collections, statistics
import optimise3 as O3
from typist import lex, FREQ, karaoke

CFG3 = json.load(open("cfg3.json"))
enc3 = O3.make_encoder(CFG3)

def find(*meanings):
    best = None
    for w, e in lex.items():
        g = e["g"].lower().strip()
        for m in meanings:
            if g == m or g.startswith(m + " ") or g == m + "s":
                if best is None or FREQ[w] > FREQ[best]: best = w
    if best: return best
    for w, e in lex.items():
        g = e["g"].lower()
        if any(m in g for m in meanings):
            if best is None or FREQ[w] > FREQ[best]: best = w
    return best

MEAN = {
 "i":["I","me"],"you":["you"],"go":["go"],"come":["come"],"eat":["eat"],
 "rice":["rice"],"water":["water"],"food":["food"],"delicious":["delicious","tasty"],
 "hungry":["hungry"],"market":["market"],"buy":["buy"],"sell":["sell"],
 "expensive":["expensive"],"cheap":["cheap"],"money":["money"],"work":["work"],
 "tired":["tired"],"busy":["busy"],"school":["school"],"study":["study"],
 "teacher":["teacher"],"book":["book"],"write":["write"],"read":["read"],
 "rain":["rain"],"hot":["hot"],"cold":["cold"],"happy":["happy","glad"],
 "love":["love"],"like":["like"],"miss":["miss"],"beautiful":["beautiful","pretty"],
 "friend":["friend"],"mother":["mother"],"sister":["older sister"],
 "house":["house","home"],"car":["car"],"city":["capital city","city"],
 "village":["village"],"far":["far"],"near":["near"],"today":["today"],
 "tomorrow":["tomorrow"],"night":["night"],"time":["time"],"day":["day"],
 "good":["good"],"new":["new"],"big":["big"],"know":["know"],"see":["see"],
 "say":["say"],"want":["want"],"can":["can"],"not":["not"],"and":["and"],
 "very":["very"],"many":["many"],"clothes":["clothes"],"phone":["telephone","phone"],
 "photo":["photograph","picture"],"fish":["fish"],"chicken":["chicken"],
 "fruit":["fruit"],"spicy":["hot spicy","spicy"],"she":["she","her"],
}
V = {k: find(*ms) for k, ms in MEAN.items()}
V = {k: v for k, v in V.items() if v}
print(f"vocabulary resolved: {len(V)}/{len(MEAN)}")

def S(*keys): return [V[k] for k in keys if k in V]

CONVO = [
 ("A","greeting",S("good","day","friend")),("B","greeting",S("good","day","you","good","not")),
 ("A","greeting",S("i","good","very")),("B","food",S("you","eat","rice","not")),
 ("A","food",S("not","i","hungry","very")),("B","food",S("i","know","food","delicious")),
 ("A","food",S("want","go","eat","fish","and","chicken")),("B","food",S("food","spicy","not")),
 ("A","food",S("spicy","i","like","very")),("B","plan",S("tomorrow","you","can","come","not")),
 ("A","plan",S("can","i","come","night")),("B","market",S("i","want","go","market","buy","clothes")),
 ("A","market",S("clothes","expensive","not")),("B","market",S("expensive","very","money","not","many")),
 ("A","market",S("buy","fruit","cheap")),("B","weather",S("today","hot","very")),
 ("A","weather",S("rain","come","night")),("B","weather",S("i","not","like","rain")),
 ("A","work",S("you","work","today","not")),("B","work",S("work","i","tired","very","busy")),
 ("A","work",S("time","not","many")),("B","school",S("sister","i","go","school")),
 ("A","school",S("teacher","good","not")),("B","school",S("teacher","good","she","study","book")),
 ("A","school",S("i","want","read","book","new")),("B","family",S("mother","you","good","not")),
 ("A","family",S("mother","i","good","she","house")),("B","family",S("i","miss","mother","very")),
 ("A","travel",S("you","go","city","not")),("B","travel",S("city","far","very","i","go","car")),
 ("A","travel",S("village","near","house","i")),("B","feeling",S("i","happy","see","you")),
 ("A","feeling",S("i","love","friend","i")),("B","feeling",S("you","beautiful","very")),
 ("A","feeling",S("you","say","good")),("B","phone",S("i","see","photo","you")),
 ("A","phone",S("photo","new","not")),("B","phone",S("new","beautiful","very")),
 ("A","close",S("time","go","work")),("B","close",S("good","see","you","tomorrow")),
]

def build(encoder):
    spell = {w: encoder(lex[w]["syl"]) for w in lex}
    pref = collections.defaultdict(list)
    for w, s in spell.items():
        for i in range(1, len(s)+1): pref[s[:i]].append(w)
    for p in pref: pref[p] = sorted(pref[p], key=lambda w: -FREQ[w])[:3]
    return spell, pref, collections.Counter(spell.values())

def type_msg(words, spell, pref, groups, predictive=True):
    keys = taps = ambig = 0; detail = []
    for w in words:
        s = spell[w]
        k = next((i for i in range(1,len(s)+1) if w in pref[s[:i]]), len(s)) if predictive else len(s)
        keys += k; taps += k + 1
        if groups[s] > 1: ambig += 1
        detail.append([s, s[:k], groups[s]])
    return keys, taps, ambig, detail

SYS = {"karaoke": karaoke, "draft3": enc3}
built = {n: build(e) for n, e in SYS.items()}
tot = {n: [0,0,0,0] for n in SYS}
rows = []
for who, topic, words in CONVO:
    if not words: continue
    r = {"who":who,"topic":topic,"words":words}
    for n in SYS:
        sp, pr, gr = built[n]
        k,t,a,d = type_msg(words, sp, pr, gr, predictive=(n!="karaoke"))
        r[n] = {"keys":k,"taps":t,"amb":a,"detail":d}
        tot[n][0]+=k; tot[n][1]+=t; tot[n][2]+=a; tot[n][3]+=len(words)
    rows.append(r)

print("="*74)
print("CONVERSATION — 2 friends, 40 messages, 10 topics")
print("="*74)
print(f"messages {len(rows)}   words typed {tot['karaoke'][3]}   "
      f"distinct {len({w for r in rows for w in r['words']})}")
print()
print(f"{'':36}{'keystrokes':>12}{'taps':>8}{'ambiguous':>16}")
for n,l in [("karaoke","karaoke Lao (today, no predictor)"),("draft3","Aksoon Laatin draft 3")]:
    k,t,a,w = tot[n]
    print(f"{l:36}{k:>12,}{t:>8,}{a:>11,} ({100*a/w:.0f}%)")
dk = tot["karaoke"][1]-tot["draft3"][1]
print(f"\ndraft 3 saves {dk:,} taps ({100*dk/tot['karaoke'][1]:.1f}%) "
      f"and {tot['karaoke'][2]-tot['draft3'][2]:,} fewer ambiguous words")
json.dump({"rows":[{**r,"words":[[w,lex[w]["g"]] for w in r["words"]]} for r in rows],
           "tot":tot}, open("convo.json","w"), ensure_ascii=False)
print("wrote convo.json")
