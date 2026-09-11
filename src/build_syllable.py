"""roman->Burmese syllable table for OOV composition.

Rhymes come from g2p_rules (the self-authored orthographic G2P, no corpus).
Onsets use user-facing Burglish spellings. Input is normalised (Burglish->MLC)
before matching. Everything is derived from the rules; no dictionary/myG2P ships.
"""
import re, g2p_rules as G
ASAT = '်'

# rhyme roman  <- (vowel-signs, final)  via romanising အ + rhyme
RHYMES = {}
for (vs, fin) in G.RHYME:
    rr = G._syllable('အ' + vs + (fin + ASAT if fin else ''))
    if rr:
        RHYMES[(vs, fin)] = rr
# user stop/extra finals the MLC romaniser spells differently
for k,(vs,fin) in {'at':('','တ'),'it':('ိ','တ'),'ut':('ု','တ'),'ok':('ု','က'),
                   'aik':('ို','က'),'auk':('ော','က'),'ik':('ိ','စ'),
                   'et':('','က'),'ap':('','ပ'),'ip':('ိ','ပ'),'up':('ု','ပ')}.items():
    RHYMES[(vs,fin)] = k.strip()

# user-facing onset spelling -> Burmese onset (consonant [+ medial])
ONSET = {
 '':'အ',
 'k':'က','kh':'ခ','g':'ဂ','ng':'င','s':'စ','hs':'ဆ','z':'ဇ','ny':'ည',
 't':'တ','ht':'ထ','d':'ဒ','n':'န','p':'ပ','hp':'ဖ','ph':'ဖ','b':'ဗ',
 'm':'မ','y':'ယ','r':'ရ','l':'လ','w':'ဝ','th':'သ','dh':'သ','h':'ဟ',
 # medial y (palatal)
 'ky':'ကျ','ch':'ချ','gy':'ဂျ','py':'ပျ','phy':'ဖျ','by':'ဗျ',
 'my':'မျ','hmy':'မှျ','ly':'လျ','sh':'ရှ',
 # medial w
 'kw':'ကွ','khw':'ခွ','gw':'ဂွ','sw':'စွ','hsw':'ဆွ','zw':'ဇွ','tw':'တွ',
 'htw':'ထွ','dw':'ဒွ','nw':'နွ','pw':'ပွ','hpw':'ဖွ','bw':'ဗွ','mw':'မွ',
 'lw':'လွ','ww':'ဝွ','thw':'သွ','hw':'ဟွ','shw':'ရွှ','ywa':'ယွ',
 # aspirated sonorants
 'hn':'နှ','hm':'မှ','hl':'လှ','hng':'ငှ','hny':'ညှ','hnw':'နွှ',
 'kya':'ကျ',
}

table = {}
for uon, bon in ONSET.items():
    for (vs, fin), rr in RHYMES.items():
        syl = bon + vs + (fin + ASAT if fin else '')
        key = uon + rr
        if key:
            prev = table.get(key)
            def rank(x): return (x.count('ံ'), len(x))
            if prev is None or rank(syl) < rank(prev):
                table[key] = syl

lines = sorted(f"{r}|{b}" for r, b in table.items())
open('syllable.txt', 'w', encoding='utf8').write("\n".join(lines) + "\n")
print(f"{len(lines)} entries, {sum(len(l) for l in lines)/1024:.1f} KB")

# --- normalisation: Burglish -> the MLC-ish roman the table is keyed on ---
SUBS = [
 ('aung','aun'),('oung','oun'),('aing','ain'),('eing','ein'),('uing','uin'),
 ('oaing','ain'),('aik','ai'),
 ('uu','u'),('ee','i'),('oo','u'),
 ('ay','ei'),('ai','ei'),
 ('aw','o'),
]
def norm(s):
    s = s.lower()
    for a,b in SUBS:
        s = s.replace(a,b)
    return s

keys = sorted(table, key=len, reverse=True)
def compose(s):
    s = norm(s); out=[]; i=0
    while i < len(s):
        for k in keys:
            if k and s.startswith(k, i):
                out.append(table[k]); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return ''.join(out)

for w in ["aung","mimi","thura","kaung","naymaung","zawgyi","lwin","hnin",
          "kyaw","seinlei","mgmg","suumon","htunhtun","chit","mingala","phyu"]:
    print(f"  {w:12s} -> {compose(w)}")
