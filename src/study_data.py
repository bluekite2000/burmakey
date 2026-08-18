"""Measure what myG2P and myPOS contain, and what the current pipeline uses.

Every figure quoted in docs/next-engine.md comes from this script. Run it after
cloning the two corpora (see README) — it takes about a minute and touches
nothing else.
"""
import collections, re, sys

G2P = '/tmp/myg2p/ver2/myg2p.ver2.0.txt'
POS = '/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt'
CLEAN = re.compile(r"[.:'\-$]")


def rows():
    out = []
    for line in open(G2P, encoding='utf8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 5 and '...' not in p[1]:
            out.append(p)
    return out


def syllable_map(rs):
    """syllable -> Counter of every attested romanization."""
    m = collections.defaultdict(collections.Counter)
    for r in rs:
        syls, roms = r[2].split(), r[3].split()
        if len(syls) != len(roms):
            continue
        for s, rom in zip(syls, roms):
            rom = CLEAN.sub('', rom)
            if re.fullmatch(r'[a-z]+', rom):
                m[s][rom] += 1
    return m


def part1(rs, syl):
    print("=" * 68)
    print("1. WHAT THE ROMANIZER DISCARDS")
    print("=" * 68)
    multi = {s: c for s, c in syl.items() if len(c) > 1}
    tot = sum(sum(c.values()) for c in syl.values())
    lost = sum(sum(c.values()) - c.most_common(1)[0][1] for c in syl.values())
    print(f"  syllables mapped        {len(syl):,}")
    print(f"  with >1 romanization    {len(multi):,} ({100*len(multi)/len(syl):.0f}%)")
    print(f"  attestations discarded  {lost:,}/{tot:,} ({100*lost/tot:.1f}%)")
    print("\n  syllable  kept            discarded")
    for s, c in sorted(multi.items(), key=lambda kv: -sum(kv[1].values()))[:6]:
        keep, *drop = [f"{r}({n})" for r, n in c.most_common()]
        print(f"  {s:<9} {keep:<15} {' '.join(drop[:4])}")


def part2(syl):
    """How many real spellings can the shipped normaliser accept?"""
    import burmese2 as B

    def normBase(t):
        t = t.replace('ph', 'hp')
        t = re.sub(r'ay', 'ei', t); t = re.sub(r'ai', 'ei', t)
        t = re.sub(r'ung\b', 'un', t); t = t.replace('aung', 'aun')
        t = t.replace('ee', 'i').replace('oo', 'u'); t = t.replace('aw', 'o')
        return t

    def norms(t):
        a = normBase(t)
        b = re.sub(r'([kpmbhtnsgl])y(?=[aeiou])', r'\1j', a)
        return {t, a, re.sub(r'ny', 'nj', b)}

    def forms(w, cap=24):
        outs = ['']
        for s in B.sylbreak(w):
            rs = syl.get(s)
            if not rs:
                return None
            outs = [o + r for o in outs for r, _ in rs.most_common()][:cap]
        return set(outs)

    print("\n" + "=" * 68)
    print("2. WHAT THE SHIPPED VARIANT RULES ACCEPT")
    print("=" * 68)
    hit = miss = 0
    rejected = collections.Counter()
    words = 0
    total_forms = 0
    for w in list(B.LEX)[:4000]:
        f = forms(w)
        if not f:
            continue
        words += 1
        total_forms += len(f)
        for spelling in f:
            if B.LEX[w] in norms(spelling) or spelling == B.LEX[w]:
                hit += 1
            else:
                miss += 1
                rejected[spelling] += 1
    tot = hit + miss
    print(f"  attested spellings per word  {total_forms/words:.2f}")
    print(f"  accepted by the rules        {hit:,}/{tot:,} ({100*hit/tot:.1f}%)")
    print(f"  REJECTED outright            {miss:,}/{tot:,} ({100*miss/tot:.1f}%)")
    print("  examples the keyboard cannot accept: " +
          " ".join(s for s, _ in rejected.most_common(6)))


def part3(rs):
    print("\n" + "=" * 68)
    print("3. THE UNUSED IPA COLUMN")
    print("=" * 68)
    aligned = [r for r in rs if len(r[2].split()) == len(r[4].split())]
    ph = collections.Counter()
    for r in aligned:
        for s in r[4].split():
            ph.update(s)
    tones = ''.join(sorted(c for c in ph if c in '̰̤́̀ʔ'))
    print(f"  rows with IPA aligned to syllables  {len(aligned):,}/{len(rs):,}")
    print(f"  distinct IPA characters             {len(ph)}")
    print(f"  tone / phonation marks present      {tones!r}")


def part4():
    print("\n" + "=" * 68)
    print("4. THE UNUSED POS TAGS, AND BIGRAM SPARSITY")
    print("=" * 68)
    sents = []
    for l in open(POS, encoding='utf8'):
        s = [t.rsplit('/', 1) for t in l.split() if '/' in t]
        s = [(w, t) for w, t in s if w and t != 'punc']
        if len(s) >= 3:
            sents.append(s)
    tr, te = sents[2000:], sents[:2000]
    wb, tb = collections.Counter(), collections.Counter()
    for s in tr:
        for a, b in zip(s, s[1:]):
            wb[(a[0], b[0])] += 1
            tb[(a[1], b[1])] += 1
    seen = unseen = tseen = 0
    for s in te:
        for a, b in zip(s, s[1:]):
            seen += (a[0], b[0]) in wb
            unseen += (a[0], b[0]) not in wb
            tseen += (a[1], b[1]) in tb
    tot = seen + unseen
    print(f"  test bigrams              {tot:,}")
    print(f"  word bigram seen          {100*seen/tot:.1f}%")
    print(f"  word bigram UNSEEN        {100*unseen/tot:.1f}%   <- bigram term silent here")
    print(f"  POS  bigram seen          {100*tseen/tot:.1f}%")
    print(f"  types: word {len(wb):,} vs POS {len(tb):,}")


if __name__ == '__main__':
    rs = rows()
    syl = syllable_map(rs)
    print(f"myG2P rows {len(rs):,} | syllables {len(syl):,}\n")
    part1(rs, syl)
    if '--quick' not in sys.argv:
        part2(syl)
    part3(rs)
    part4()
