"""Emit the v4 hybrid lexicon in the web keyboard's spelling|word format.

Same line format the page already parses (kou|ကို), just more lines: every
rule-generated and attested spelling above a weight floor. Lines are ordered
by word frequency then spelling weight, because the page's prior is 1/(rank).
"""
import re, json
import burmese2 as B, engine_v2 as E
from h2h_v3 import rule_forms

syl = E.syllable_variants()
vocab = set(B.LEX) | {w for s in B.TRAIN for w in s} | {w for s in B.TEST for w in s}
entries = []            # (freq, weight, spelling, word)
words = 0
for w in vocab:
    f = rule_forms(w) or {}
    for sp, wt in (E.word_forms(w, B.sylbreak, syl) if w in B.LEX else {}).items():
        f[sp] = max(f.get(sp, 0.0), wt)
    if not f:
        continue
    freq = B.FREQ.get(w, 0)
    # rare words outside the dictionary are mostly corpus noise a demo user
    # will never type; the size they cost is real, the recall is not
    if w not in B.LEX and freq < 2:
        continue
    words += 1
    keep = sorted(((wt, sp) for sp, wt in f.items() if wt >= 0.25),
                  reverse=True)[:4]
    if not keep:
        keep = [(1.0, max(f, key=f.get))]
    for wt, sp in keep:
        entries.append((freq, wt, sp, w))
entries.sort(key=lambda e: (-e[0], -e[1]))
lines = [f"{sp}|{w}" for _, _, sp, w in entries]
open('weblex_v4.txt', 'w', encoding='utf8').write("\n".join(lines))
print(f"{words:,} words, {len(lines):,} spelling lines, "
      f"{sum(len(l) for l in lines)/1024:.0f} KB raw")
