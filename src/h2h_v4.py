"""v4, the hybrid: rules as the backbone, attested data as corrections.

Construction:
  - start from v3's rule-generated spellings for EVERY word the rules can
    romanize (coverage, OOV generalisation, licence-clean backbone)
  - where licensed dictionary data exists for a word, layer its attested
    spellings on top with their weights (the correction layer)

The correction layer is exactly the part one must be licensed for; swap in a
different source — e.g. the keyboard's own consented typing stream — and the
architecture is unchanged.

Scored against v1, v2, v3 and the measured competitor cost, same 19,898
held-out words, both input scenarios. Also a THIRD scenario, oov: words the
dictionary does not contain at all, where only a rules backbone can play.
"""
import collections, random, re, json
import burmese2 as B
import engine_v2 as E
import g2p_rules as G
from h2h_v2 import EngineV1
from h2h_v3 import rule_forms

SEED = 20260818
KEYMAP = 'bagan_keymap_full.json'


def main():
    print("building indices ...", flush=True)
    syl = E.syllable_variants()
    vocab = set(B.LEX) | {w for s in B.TEST for w in s} | \
            {w for s in B.TRAIN for w in s}
    v2_forms, v3_forms, v4_forms = {}, {}, {}
    for w in vocab:
        f2 = E.word_forms(w, B.sylbreak, syl) if w in B.LEX else {}
        f3 = rule_forms(w)
        if f2:
            v2_forms[w] = f2
        if f3:
            v3_forms[w] = f3
        # hybrid: rules everywhere, attested weights where they exist
        if f2 or f3:
            merged = dict(f3)                       # backbone
            for sp, wt in (f2 or {}).items():       # corrections dominate
                merged[sp] = max(merged.get(sp, 0.0), wt)
            v4_forms[w] = merged
    tags, tagprob = E.pos_map()
    print(f"  v2 {len(v2_forms):,} | v3 {len(v3_forms):,} | v4 {len(v4_forms):,} words "
          f"({sum(len(f) for f in v4_forms.values())/len(v4_forms):.1f} spellings/word)")

    km = json.load(open(KEYMAP))['keymap']
    cost = {}
    for k, v in km.items():
        k = k.replace('​', '')
        if k and (k not in cost or v[2] < cost[k]):
            cost[k] = v[2]

    lex1 = {w: B.LEX[w] for w in v2_forms}
    mk = lambda forms: E.EngineV2(forms, B.FREQ, tags, tagprob, use_pos=False)
    engines = {'v1': EngineV1(lex1, B.FREQ), 'v2': mk(v2_forms),
               'v3': mk(v3_forms), 'v4': mk(v4_forms)}
    prime = {'v1': lambda e: e.prime(B.TRAIN),
             'v2': lambda e: e.prime(B.TRAIN, v2_forms),
             'v3': lambda e: e.prime(B.TRAIN, v3_forms),
             'v4': lambda e: e.prime(B.TRAIN, v4_forms)}

    results = {}
    for scenario in ('canonical', 'realistic', 'oov'):
        for k, e in engines.items():
            e.reset(); prime[k](e)
        acc = {k: dict(taps=0, words=0, miss=0) for k in engines}
        comp_taps = comp_words = 0
        rs = random.Random(SEED)
        for s in B.TEST:
            for w in s:
                if scenario == 'oov':
                    # words the dictionary lacks but the rules can romanize:
                    # only spelling available is the rules' own
                    if w in B.LEX or w not in v3_forms:
                        for e in engines.values():
                            e.prev = None
                        continue
                    spelling = max(v3_forms[w], key=v3_forms[w].get)
                else:
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
        results[scenario]['competitor'] = comp_taps / max(1, comp_words)

    LAB = {'v1': 'v1  dictionary + 8 rules     ',
           'v2': 'v2  dictionary, all variants ',
           'v3': 'v3  rules only               ',
           'v4': 'v4  HYBRID rules + attested  '}
    print("\n" + "=" * 74)
    print("TAPS PER WORD / WORD UNREACHABLE")
    print("=" * 74)
    for sc in ('canonical', 'realistic', 'oov'):
        r = results[sc]
        n = r['v1']['words']
        note = {'canonical': 'the study assumed this',
                'realistic': "sampled from attested variants",
                'oov': f'dictionary has NO entry ({n:,} words)'}[sc]
        print(f"\n  {sc} input — {note}")
        print(f"    {'Bagan / TTKeyboard':<31}{r['competitor']:>7.2f}      —")
        for k in ('v1', 'v2', 'v3', 'v4'):
            a = r[k]
            if a['words']:
                print(f"    {LAB[k]:<31}{a['taps']/a['words']:>7.2f}"
                      f"{100*a['miss']/a['words']:>9.1f}%")
    json.dump(results, open('h2h_v4_results.json', 'w'), indent=1)
    print("\nwrote h2h_v4_results.json")


if __name__ == '__main__':
    main()
