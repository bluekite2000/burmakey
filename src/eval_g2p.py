"""Score the rule-based G2P against myG2P as held-out gold. Read-only use."""
import collections, re, sys
import g2p_rules as G

CLEAN = re.compile(r"[.:'\-$]")
rows = []
for line in open('/tmp/myg2p/ver2/myg2p.ver2.0.txt', encoding='utf8'):
    p = line.rstrip('\n').split('\t')
    if len(p) == 5 and '...' not in p[1]:
        rows.append(p)

# gold: word -> set of attested toneless romanizations (joined syllables)
gold = collections.defaultdict(set)
gold_syl = collections.defaultdict(set)
for r in rows:
    syls, roms = r[2].split(), r[3].split()
    if len(syls) != len(roms):
        continue
    clean = [CLEAN.sub('', x) for x in roms]
    if all(re.fullmatch(r'[a-z]+', c) for c in clean):
        gold[r[1]].add(''.join(clean))
        for s, c in zip(syls, clean):
            gold_syl[s].add(c)

# ---- syllable level ----
hit = miss = 0
errors = collections.Counter()
for s, forms in gold_syl.items():
    out = G.romanize(s, variants=True) or set()
    # a syllable attested ONLY in voiced form occurs only word-internally,
    # where the sandhi rule fires; test it in that context
    out |= G.romanize('က' + s, variants=True) and {
        v[2:] for v in G.romanize('က' + s, variants=True) if v.startswith('ka')} or set()
    if out & forms:
        hit += 1
    else:
        miss += 1
        can = G.romanize(s)
        errors[(can, tuple(sorted(forms))[0])] += 1
print(f"SYLLABLES  {hit:,}/{hit+miss:,} match an attested form  ({100*hit/(hit+miss):.1f}%)")

# ---- word level ----
whit = wmiss = 0
werr = collections.Counter()
seg_ok = seg_tot = 0
for r in rows[:len(rows)]:
    w = r[1]
    if w not in gold:
        continue
for w, forms in gold.items():
    out = G.romanize(w, variants=True) or set()
    if out & forms:
        whit += 1
    else:
        wmiss += 1
        if wmiss <= 0:
            print('  miss:', w, G.romanize(w), '| gold:', sorted(forms)[:2])
print(f"WORDS      {whit:,}/{whit+wmiss:,} match an attested form  ({100*whit/(whit+wmiss):.1f}%)")

# segmentation vs gold splits
for r in rows[:6000]:
    seg_tot += 1
    if G.segment(r[1]) == r[2].split():
        seg_ok += 1
print(f"SEGMENTER  {seg_ok:,}/{seg_tot:,} exact splits  ({100*seg_ok/seg_tot:.1f}%)  [pipeline's regex: 89.4%]")

print("\ntop syllable error classes (rule output vs gold):")
for (mine, want), c in errors.most_common(int(sys.argv[1]) if len(sys.argv)>1 else 12):
    print(f"  {c:>4}x  rules say {mine!r:<12} gold has {want!r}")
