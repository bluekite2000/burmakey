"""Render the lexicon under the winning configuration (draft 2)."""
import json, collections, re
from optimise import make_encoder, evaluate
cfg = json.load(open("best_cfg.json"))
LEX = json.load(open("phonlex.json"))
enc = make_encoder(cfg)

TONE="hlsfd"
def karaoke(sylls):
    """what a karaoke writer produces: no tone, no length, no zero onset"""
    ON={"x":"","kh":"kh","ng":"ng","ny":"ny","th":"th","ph":"ph","j":"j",
        "khw":"khw","kw":"kw"}
    V={"i":"i","e":"e","E":"ae","M":"eu","V":"oe","a":"a","u":"u","o":"o",
       "O":"o","iM":"ia","MM":"uea","uM":"ua"}
    return "".join(ON.get(s["on"],s["on"])+V[s["v"]]+s["fin"] for s in sylls)

rows=[]
for e in LEX:
    rows.append({"a":enc(e["syl"]),"l":e["lao"],"g":e["g"],"k":karaoke(e["syl"])})
rows=[r for r in rows if r["g"]]
rows.sort(key=lambda r:(len(r["a"]),r["a"]))
rows=rows[:5200]
json.dump(rows,open("demo_lex.json","w"),ensure_ascii=False,separators=(",",":"))
print("demo entries:",len(rows))
print("\nsample  draft2 / karaoke / Lao / English")
for r in rows[400:412]:
    print(f"   {r['a']:<10} {r['k']:<10} {r['l']:<11} {r['g'][:34]}")
