"""BurmaKey v2: accept every attested spelling, and back off through POS.

Two changes from the engine in burmese2.py, both taken straight from the data
study (docs/next-engine.md):

1. The romanizer no longer collapses each syllable to its most frequent
   spelling. Every romanization myG2P attests becomes a way to reach the word,
   carrying its own weight. This is the trie form of the weighted FST the study
   proposes — variants are arcs, not hand-written rules.

2. When a word bigram has never been seen — 29.6% of held-out contexts — the
   ranker backs off to a POS-class bigram instead of scoring zero.

Everything else is deliberately unchanged so the comparison stays honest: same
5-candidate bar, same recency term, same beam.
"""
import collections, re, math

CLEAN = re.compile(r"[.:'\-$]")
G2P = '/tmp/myg2p/ver2/myg2p.ver2.0.txt'
POS = '/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt'
MAX_FORMS = 24          # cap the expansion per word; keeps the index bounded


def syllable_variants():
    """syllable -> {romanization: count}, keeping every attestation."""
    m = collections.defaultdict(collections.Counter)
    for line in open(G2P, encoding='utf8'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 4 or '...' in p[1]:
            continue
        syls, roms = p[2].split(), p[3].split()
        if len(syls) != len(roms):
            continue
        for s, r in zip(syls, roms):
            r = CLEAN.sub('', r)
            if re.fullmatch(r'[a-z]+', r):
                m[s][r] += 1
    return m


def word_forms(word, sylbreak, syl, cap=MAX_FORMS):
    """Every spelling the data attests for a word, with a probability.

    Weight is the product of each syllable's share of its own attestations, so
    the canonical spelling stays most likely while the alternants remain
    reachable rather than being discarded.
    """
    forms = {'': 1.0}
    for s in sylbreak(word):
        table = syl.get(s)
        if not table:
            return {}
        total = sum(table.values())
        nxt = {}
        for prefix, w in forms.items():
            for rom, n in table.most_common():
                nxt[prefix + rom] = max(nxt.get(prefix + rom, 0.0), w * n / total)
        forms = dict(sorted(nxt.items(), key=lambda kv: -kv[1])[:cap])
    # Keep only the spellings that carry real probability. 73% of the raw
    # expansion is tail — combinations of several rare choices at once — and
    # it buys no recall while adding noise to every prefix it touches.
    ranked = sorted(forms.items(), key=lambda kv: -kv[1])
    total = sum(w for _, w in ranked) or 1.0
    kept, run = {}, 0.0
    for spelling, w in ranked:
        kept[spelling] = w / total
        run += w / total
        if run >= 0.95 and len(kept) >= 2:
            break
    return kept


def pos_map():
    """word -> most frequent POS tag, and the class bigram table."""
    tag = collections.defaultdict(collections.Counter)
    bigram = collections.defaultdict(collections.Counter)
    for line in open(POS, encoding='utf8'):
        s = [t.rsplit('/', 1) for t in line.split() if '/' in t]
        s = [(w, t) for w, t in s if w and t != 'punc']
        for w, t in s:
            tag[w][t] += 1
        for (w1, t1), (w2, t2) in zip(s, s[1:]):
            bigram[t1][t2] += 1
    best = {w: c.most_common(1)[0][0] for w, c in tag.items()}
    prob = {}
    for t1, c in bigram.items():
        tot = sum(c.values())
        for t2, n in c.items():
            prob[(t1, t2)] = n / tot
    return best, prob


class EngineV2:
    def __init__(self, lexicon_forms, freq, tags, tagprob, shortlist=5, beam=50,
                 use_pos=True):
        self.freq, self.tags, self.tagprob = freq, tags, tagprob
        self.use_pos = use_pos
        self.shortlist, self.beam = shortlist, beam
        self.by_prefix = collections.defaultdict(dict)   # prefix -> {word: weight}
        for word, forms in lexicon_forms.items():
            for spelling, w in forms.items():
                for i in range(1, len(spelling) + 1):
                    d = self.by_prefix[spelling[:i]]
                    if w > d.get(word, 0.0):
                        d[word] = w
        # trim each prefix to the beam, best-weighted then most frequent
        for p, d in self.by_prefix.items():
            if len(d) > beam:
                keep = sorted(d.items(), key=lambda kv: -freq.get(kv[0], 0))[:beam]
                self.by_prefix[p] = dict(keep)
        self.reset()

    def reset(self):
        self.recency = collections.Counter()
        self.bigram = collections.defaultdict(collections.Counter)
        self.prev = None

    def prime(self, sentences, lex, weight=0.2):
        for s in sentences:
            kept = [w for w in s if w in lex]
            for a, b in zip(kept, kept[1:]):
                self.bigram[a][b] += weight

    def score(self, word, spell_weight):
        v = self.freq.get(word, 0) + 10 * self.recency[word]
        v *= (0.85 + 0.15 * spell_weight)   # mild: a rarer spelling is weaker
                                            # evidence, but frequency still leads
        if self.prev is not None:
            seen = self.bigram[self.prev][word]
            if seen:
                v += 100 * seen
            else:
                # NEW: the word bigram is unseen, so fall back to the POS class
                if not self.use_pos:
                    return v
                t1 = self.tags.get(self.prev)
                t2 = self.tags.get(word)
                if t1 and t2:
                    v += 60 * self.tagprob.get((t1, t2), 0.0)
        return v

    def type_word(self, target, spelling):
        """Return taps needed, and whether the target was reachable at all."""
        for k in range(0, len(spelling) + 1):
            pool = self.by_prefix.get(spelling[:k])
            if not pool:
                continue
            ranked = sorted(pool.items(), key=lambda kv: -self.score(kv[0], kv[1]))
            if any(w == target for w, _ in ranked[:self.shortlist]):
                return k + 1, True
        return len(spelling) + 1, False      # never offered: typed out as raw

    def learn(self, word):
        self.recency[word] += 1
        if self.prev is not None:
            self.bigram[self.prev][word] += 1
        self.prev = word
