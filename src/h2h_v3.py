"""v3: the engine with a lexicon built ENTIRELY from the rule-based G2P.

No myG2P at runtime, no myG2P-derived index. The dictionary is used in this
script only to (a) sample "realistic" input spellings — which for v3 is a
genuinely held-out test, since v3 never saw them — and (b) benchmark.

myPOS still supplies word frequencies; that dependency is unchanged and noted.
"""
import collections, random, re, json
import burmese2 as B
import engine_v2 as E
import g2p_rules as G
from h2h_v2 import EngineV1, v1_norms

SEED = 20260818
KEYMAP = 'bagan_keymap_full.json'


def rule_forms(word):
    """word -> {spelling: weight}, canonical first, sandhi variants after."""
    canon = G.romanize(word)
    if canon is None or not re.fullmatch(r'[a-z]+', canon):
        return {}
    forms = {canon: 1.0}
    for v in (G.romanize(word, variants=True) or ()):
        if re.fullmatch(r'[a-z]+', v):
            forms.setdefault(v, 0.6)
    return forms


def main():
    rng = random.Random(SEED)
    print("building indices ...", flush=True)
    syl = E.syllable_variants()
    v2_forms, v3_forms = {}, {}
    vocab = set(B.LEX) | {w for s in B.TEST for w in s} | \
            {w for s in B.TRAIN for w in s}
    for w in vocab:
        f2 = E.word_forms(w, B.sylbreak, syl) if w in B.LEX else {}
        if f2:
            v2_forms[w] = f2
        f3 = rule_forms(w)
        if f3:
            v3_forms[w] = f3
    tags, tagprob = E.pos_map()
    print(f"  v2 (dictionary): {len(v2_forms):,} words")
    print(f"  v3 (rules only): {len(v3_forms):,} words, "
          f"{sum(len(f) for f in v3_forms.values())/len(v3_forms):.1f} spellings/word")

    km = json.load(open(KEYMAP))['keymap']
    cost = {}
    for k, v in km.items():
        k = k.replace('​', '')
        if k and (k not in cost or v[2] < cost[k]):
            cost[k] = v[2]

    lex1 = {w: B.LEX[w] for w in v2_forms}
    engines = {
        'v1': EngineV1(lex1, B.FREQ),
        'v2': E.EngineV2(v2_forms, B.FREQ, tags, tagprob, use_pos=False),
        'v3': E.EngineV2(v3_forms, B.FREQ, tags, tagprob, use_pos=False),
    }

    test = B.TEST
    results = {}
    for scenario in ('canonical', 'realistic'):
        for e in engines.values():
            e.reset()
        engines['v1'].prime(B.TRAIN)
        engines['v2'].prime(B.TRAIN, v2_forms)
        engines['v3'].prime(B.TRAIN, v3_forms)
        acc = {k: dict(taps=0, words=0, miss=0) for k in engines}
        comp_taps = comp_words = 0
        rs = random.Random(SEED)
        for s in test:
            for w in s:
                # score only words every system can attempt, for a fair frame
                if w not in B.LEX or w not in v3_forms:
                    for e in engines.values():
                        e.prev = None
                    continue
                if scenario == 'canonical':
                    spelling = B.LEX[w]
                else:
                    pool = list((v2_forms.get(w) or {B.LEX[w]: 1.0}).items())
                    tot = sum(p for _, p in pool) or 1.0
                    r = rs.random() * tot
                    spelling = pool[-1][0]
                    for cand, p in pool:
                        r -= p
                        if r <= 0:
                            spelling = cand
                            break
                for name, eng in engines.items():
                    t, ok = eng.type_word(w, spelling)
                    acc[name]['taps'] += t
                    acc[name]['words'] += 1
                    acc[name]['miss'] += (not ok)
                    eng.learn(w)
                comp_taps += sum(cost.get(ch, 1) for ch in w)
                comp_words += 1
        results[scenario] = {k: dict(v) for k, v in acc.items()}
        results[scenario]['competitor'] = comp_taps / comp_words

    n = results['canonical']['v1']['words']
    print(f"\nscored {n:,} words per scenario\n")
    print("=" * 74)
    print("TAPS PER WORD / WORD UNREACHABLE   (unreachable -> sent as raw Latin)")
    print("=" * 74)
    LAB = {'v1': 'v1  dictionary, 8 rules      ',
           'v2': 'v2  dictionary, all variants ',
           'v3': 'v3  RULES ONLY, no dictionary'}
    for sc in ('canonical', 'realistic'):
        r = results[sc]
        print(f"\n  {sc} input")
        print(f"    {'Bagan / TTKeyboard':<31}{r['competitor']:>7.2f}      —")
        for k in ('v1', 'v2', 'v3'):
            a = r[k]
            print(f"    {LAB[k]:<31}{a['taps']/a['words']:>7.2f}"
                  f"{100*a['miss']/a['words']:>9.1f}%")
    json.dump(results, open('h2h_v3_results.json', 'w'), indent=1)
    print("\nwrote h2h_v3_results.json")


if __name__ == '__main__':
    main()
