"""Head to head: the competitors, BurmaKey v1, and BurmaKey v2.

Two input scenarios, because which one you use decides the answer:

  canonical  the user types the single spelling the v1 lexicon expects. This is
             what the original study assumed, and it flatters v1.
  realistic  the user types one of the spellings myG2P actually attests for the
             word, sampled by how often it is attested. Real Burglish varies;
             this is the case the study never tested.

Competitor cost is the measured constant from the real apps: character entry,
no word prediction, no per-word commit tap (see measure_bagan.py).
"""
import collections, random, re, sys, json
import burmese2 as B
import engine_v2 as E

SEED = 20260818
KEYMAP = 'bagan_keymap_full.json'


def v1_norms(t):
    """The variant rules the shipped keyboard actually has."""
    a = t.replace('ph', 'hp')
    a = re.sub(r'ay', 'ei', a); a = re.sub(r'ai', 'ei', a)
    a = re.sub(r'ung\b', 'un', a); a = a.replace('aung', 'aun')
    a = a.replace('ee', 'i').replace('oo', 'u'); a = a.replace('aw', 'o')
    b = re.sub(r'([kpmbhtnsgl])y(?=[aeiou])', r'\1j', a)
    b = re.sub(r'ny', 'nj', b)
    return [t, a, b] if a != b else [t, a]


class EngineV1:
    """The engine as it ships: one canonical spelling per word, eight rules."""
    def __init__(self, lex, freq, shortlist=5):
        self.lex, self.freq, self.shortlist = lex, freq, shortlist
        self.by_prefix = collections.defaultdict(list)
        for w, code in lex.items():
            for i in range(1, len(code) + 1):
                self.by_prefix[code[:i]].append(w)
        for p in self.by_prefix:
            self.by_prefix[p] = sorted(self.by_prefix[p],
                                       key=lambda w: -freq.get(w, 0))[:50]
        self.reset()

    def reset(self):
        self.recency = collections.Counter()
        self.bigram = collections.defaultdict(collections.Counter)
        self.prev = None

    def prime(self, sents, weight=0.2):
        for s in sents:
            kept = [w for w in s if w in self.lex]
            for a, b in zip(kept, kept[1:]):
                self.bigram[a][b] += weight

    def score(self, w):
        v = self.freq.get(w, 0) + 10 * self.recency[w]
        if self.prev is not None:
            v += 100 * self.bigram[self.prev][w]
        return v

    def type_word(self, target, spelling):
        for k in range(0, len(spelling) + 1):
            pool = []
            for variant in v1_norms(spelling[:k]):
                pool.extend(self.by_prefix.get(variant, ()))
            if not pool:
                continue
            ranked = sorted(set(pool), key=self.score, reverse=True)
            if target in ranked[:self.shortlist]:
                return k + 1, True
        return len(spelling) + 1, False

    def learn(self, w):
        self.recency[w] += 1
        if self.prev is not None:
            self.bigram[self.prev][w] += 1
        self.prev = w


def competitor_taps(word, cost):
    return sum(cost.get(ch, 1) for ch in word)


def main():
    rng = random.Random(SEED)
    print("building v2 index (all attested spellings) ...", flush=True)
    syl = E.syllable_variants()
    forms = {}
    for w in B.LEX:
        f = E.word_forms(w, B.sylbreak, syl)
        if f:
            forms[w] = f
    tags, tagprob = E.pos_map()
    print(f"  {len(forms):,} words, {sum(len(f) for f in forms.values()):,} spellings "
          f"({sum(len(f) for f in forms.values())/len(forms):.1f} per word)")

    try:
        km = json.load(open(KEYMAP))['keymap']
        cost = {}
        for k, v in km.items():
            k = k.replace('​', '')
            if k and (k not in cost or v[2] < cost[k]):
                cost[k] = v[2]
    except FileNotFoundError:
        cost = {}

    lex = {w: B.LEX[w] for w in forms}
    v1 = EngineV1(lex, B.FREQ)
    v2 = E.EngineV2(forms, B.FREQ, tags, tagprob)
    v2np = E.EngineV2(forms, B.FREQ, tags, tagprob, use_pos=False)  # ablation
    v1.prime(B.TRAIN); v2.prime(B.TRAIN, lex); v2np.prime(B.TRAIN, lex)

    test = [s for s in B.TEST if any(w in forms for w in s)]
    results = {}
    for scenario in ('canonical', 'realistic'):
        v1.reset(); v2.reset(); v2np.reset()
        v1.prime(B.TRAIN); v2.prime(B.TRAIN, lex); v2np.prime(B.TRAIN, lex)
        acc = {k: dict(taps=0, words=0, miss=0) for k in ('v1', 'v2', 'v2np')}
        comp_taps = comp_words = 0
        rs = random.Random(SEED)
        for s in test:
            for w in s:
                if w not in forms:
                    v1.prev = v2.prev = None
                    continue
                if scenario == 'canonical':
                    spelling = B.LEX[w]
                else:
                    pool = list(forms[w].items())
                    tot = sum(p for _, p in pool) or 1.0
                    r = rs.random() * tot
                    spelling = pool[-1][0]
                    for cand, p in pool:
                        r -= p
                        if r <= 0:
                            spelling = cand
                            break
                for name, eng in (('v1', v1), ('v2', v2), ('v2np', v2np)):
                    t, ok = eng.type_word(w, spelling)
                    acc[name]['taps'] += t
                    acc[name]['words'] += 1
                    acc[name]['miss'] += (not ok)
                    eng.learn(w)
                if cost:
                    comp_taps += competitor_taps(w, cost)
                    comp_words += 1
        results[scenario] = dict(acc)
        results[scenario]['competitor'] = (comp_taps / comp_words) if comp_words else None

    print(f"\nscored {results['canonical']['v1']['words']:,} words per scenario\n")
    print("=" * 72)
    print("TAPS PER WORD, and how often the word could not be offered at all")
    print("=" * 72)
    print(f"{'':34}{'taps/word':>12}{'unreachable':>14}")
    for scenario in ('canonical', 'realistic'):
        r = results[scenario]
        print(f"\n  {scenario} input" +
              ("   (what the study assumed)" if scenario == 'canonical'
               else "   (what people actually type)"))
        if r['competitor']:
            print(f"    {'Bagan / TTKeyboard':<30}{r['competitor']:>12.2f}{'—':>14}")
        for name, label in (('v1', 'BurmaKey v1 (shipped)'),
                            ('v2np', 'BurmaKey v2, variants only'),
                            ('v2', 'BurmaKey v2, variants + POS')):
            a = r[name]
            print(f"    {label:<30}{a['taps']/a['words']:>12.2f}"
                  f"{100*a['miss']/a['words']:>13.1f}%")
    json.dump(results, open('h2h_v2_results.json', 'w'), indent=1)
    print("\nwrote h2h_v2_results.json")


if __name__ == '__main__':
    main()
