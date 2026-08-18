"""Regenerate the typing-race demo's right side with the v4 engine.

The demo replays hardcoded per-keystroke frames generated in the v1 era. The
left (script keyboard) side is unchanged — that behaviour was measured on the
real app. The right side is re-simulated: same 24 messages, but candidates and
picks come from the v4 hybrid index, exactly what the live keyboard runs.
"""
import json, sys
import burmese2 as B, engine_v2 as E
from h2h_v3 import rule_forms

SCRATCH='/private/tmp/claude-501/-Users-huudat/3c669fe4-3307-4e49-992b-373f48472204/scratchpad/race_D.json'
D=json.load(open(SCRATCH,encoding='utf8'))

# v4 index + a rom for display (canonical spelling per word)
syl=E.syllable_variants()
forms={}
for w in set(B.LEX)|{w for s in B.TRAIN for w in s}:
    f=rule_forms(w) or {}
    for sp,wt in (E.word_forms(w,B.sylbreak,syl) if w in B.LEX else {}).items():
        f[sp]=max(f.get(sp,0.0),wt)
    if f: forms[w]=f
tags,tp=E.pos_map()
eng=E.EngineV2(forms,B.FREQ,tags,tp,use_pos=False)
eng.prime(B.TRAIN,forms)
rom={w:(B.LEX.get(w) or max(forms[w],key=forms[w].get)) for w in forms}

def top5(prefix):
    pool=eng.by_prefix.get(prefix)
    if not pool and len(prefix)>=3: pool=eng._fuzzy_pool(prefix)
    if not pool: return []
    seen=set(); out=[]
    for w,_ in sorted(pool.items(),key=lambda kv:-eng.score(kv[0],kv[1])):
        if w in seen: continue
        seen.add(w); out.append([w,rom.get(w,"")])
        if len(out)==5: break
    return out

def zero5():
    ids={}
    if eng.prev is not None:
        for w,c in eng.bigram.get(eng.prev,{}).items(): ids[w]=100*c
    for w,c in eng.recency.items(): ids[w]=max(ids.get(w,0),10*c)
    out=sorted(ids,key=lambda w:-(ids[w]+B.FREQ.get(w,0)))[:5]
    return [[w,rom.get(w,"")] for w in out]

new_msgs=[]; taps_R=0
for msg in D["msgs"]:
    words=[e["out"] for e in msg["R"] if e["t"]=="commit"]
    ev=[{"t":"bar","bar":zero5()}]
    for w in words:
        if w not in forms:                     # not indexable: typed out raw
            for ch in (B.LEX.get(w) or w):
                ev.append({"t":"key","c":ch,"bar":[]}); taps_R+=1
            ev.append({"t":"commit","out":w,"rom":B.LEX.get(w,""),"pick":-1}); taps_R+=1
            eng.prev=None; continue
        sp=B.LEX.get(w) or max(forms[w],key=forms[w].get)
        done=False
        for k in range(0,len(sp)+1):
            bar=top5(sp[:k]) if k else zero5()
            if k: ev.append({"t":"key","c":sp[k-1],"bar":bar}); taps_R+=1
            names=[x[0] for x in bar]
            if w in names:
                ev.append({"t":"commit","out":w,"rom":sp,"pick":names.index(w)})
                taps_R+=1; done=True; break
        if not done:
            ev.append({"t":"commit","out":w,"rom":sp,"pick":-1}); taps_R+=1
        eng.learn(w)
    new_msgs.append({"L":msg["L"],"R":ev})

taps_L=sum(1 for m in D["msgs"] for e in m["L"] if e["t"]=="key")
out={"msgs":new_msgs,"tot":{"L":D["tot"]["L"],"R":taps_R},"keys":D["keys"]}
json.dump(out,open("race_D_v4.json","w",encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(f"regenerated: L taps {D['tot']['L']} (unchanged) | R taps {D['tot']['R']} -> {taps_R}")
