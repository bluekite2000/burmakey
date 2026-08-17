"""
Lao script -> tone, over the 21,394-word Google spellcheck list.

Answers the open question in Aksoon Laatin §9.3: which tone is most frequent,
and therefore which one should be the unwritten one?

Tone table is DATA, in TONE_TABLE below, so it can be replaced wholesale when
an authority corrects it. Source: r12a.github.io Lao orthography notes.
Not yet cross-checked against a second source -- see caveat in the report.
"""
import collections, unicodedata
from laonlp.tokenize.syllable import syllable_tokenize

WORDS = [w.strip() for w in open(
    __import__('laonlp').__path__[0] + '/corpus/lo_spellcheck_dict.txt',
    encoding='utf-8') if w.strip() and not w.startswith('#')]

TONE_MARKS = {'່': 'ek', '້': 'tho', '໊': 'ti', '໋': 'catawa'}

HIGH = set('ຂຖຜຝສຫໜໝ')
MID  = set('ກຈຕດບປອຢ')
LOW  = set('ຄງຊຍທນພຟມຣລວຮ')
SONORANT = set('ງຍນມລວ')          # take high class when preceded by ຫ
FINALS   = set('ກງດນບມວຍ')

SHORT_V = set('ະັິຶຸົຳ')   # ະ ັ ິ ຶ ຸ ົ ຳ
LONG_V  = set('າີືູເແໂໍຽ')  # າ ີ ື ູ ເ ແ ໂ ໍ ຽ
DEAD_FINALS = set('ກດບ')

# (class, condition) -> tone
TONE_TABLE = {
    ('high', 'live'):      'low',
    ('high', 'dead_short'): 'rising',
    ('high', 'dead_long'):  'lowfall',
    ('high', 'ek'):        'mid',
    ('high', 'tho'):       'highfall',
    ('high', 'ti'):        'highfall',
    ('high', 'catawa'):    'lowrising',
    ('mid', 'live'):       'lowrising',
    ('mid', 'dead_short'): 'high',
    ('mid', 'dead_long'):  'lowfall',
    ('mid', 'ek'):         'mid',
    ('mid', 'tho'):        'lowfall',
    ('mid', 'ti'):         'high',
    ('mid', 'catawa'):     'rising',
    ('low', 'live'):       'high',
    ('low', 'dead_short'): 'mid',
    ('low', 'dead_long'):  'highfall',
    ('low', 'ek'):         'mid',
    ('low', 'tho'):        'highfall',
    ('low', 'ti'):         'high',
    ('low', 'catawa'):     'rising',
}


def analyse(syl):
    """-> (tone, why) or (None, reason-it-failed)"""
    chars = [c for c in unicodedata.normalize('NFC', syl)]
    cons = [c for c in chars if c in HIGH | MID | LOW]
    if not cons:
        return None, 'no-consonant'

    # onset: first consonant, unless it's ຫ + sonorant (which makes it high class)
    onset = cons[0]
    if onset == 'ຫ' and len(cons) > 1 and cons[1] in SONORANT:
        cls = 'high'
    elif onset in HIGH:
        cls = 'high'
    elif onset in MID:
        cls = 'mid'
    else:
        cls = 'low'

    mark = next((TONE_MARKS[c] for c in chars if c in TONE_MARKS), None)
    if mark:
        return TONE_TABLE.get((cls, mark)), f'{cls}+{mark}'

    # live vs dead: dead = stop coda, or short vowel with no coda
    final = cons[-1] if len(cons) > 1 and cons[-1] in FINALS else None
    has_long = any(c in LONG_V for c in chars)
    has_short = any(c in SHORT_V for c in chars)

    if final in DEAD_FINALS:
        cond = 'dead_long' if has_long else 'dead_short'
    elif final is not None:
        cond = 'live'
    elif has_short and not has_long:
        cond = 'dead_short'
    elif has_long:
        cond = 'live'
    else:
        return None, 'no-vowel'
    return TONE_TABLE.get((cls, cond)), f'{cls}+{cond}'


tones = collections.Counter()
fails = collections.Counter()
n_syl = 0
for w in WORDS:
    for syl in syllable_tokenize(w):
        if not any(c in HIGH | MID | LOW for c in syl):
            continue
        n_syl += 1
        t, why = analyse(syl)
        if t is None:
            fails[why] += 1
        else:
            tones[t] += 1

print("=" * 58)
print("TONE FREQUENCY  —  Google Lao spellcheck list")
print("=" * 58)
print(f"words        : {len(WORDS):,}")
print(f"syllables    : {n_syl:,}")
print(f"analysed     : {sum(tones.values()):,} ({100*sum(tones.values())/n_syl:.1f}%)")
print(f"unanalysed   : {sum(fails.values()):,}")
for k, v in fails.most_common():
    print(f"    {k}: {v:,}")
print()
tot = sum(tones.values())
print(f"{'tone':<12}{'count':>9}{'share':>9}   marked?")
for t, n in tones.most_common():
    print(f"{t:<12}{n:>9,}{100*n/tot:>8.1f}%")
print()
top = tones.most_common(1)[0]
print(f"Most frequent tone: {top[0]}  ({100*top[1]/tot:.1f}% of syllables)")
print(f"Leaving it unmarked saves {top[1]:,} keystrokes per {tot:,} syllables.")
print(f"It also makes {100*top[1]/tot:.1f}% of syllables carry the ambiguity")
print(f"documented in §8.1 (18.1% ambiguity rate for unmarked syllables).")
print(f"=> expected boundary ambiguity ~ {0.181*top[1]/tot*100:.1f}% of syllable junctions")
print()
print("Alternative: unmark the tone that minimises ambiguity x frequency:")
for t, n in tones.most_common():
    print(f"   unmark {t:<11} -> {100*n/tot:5.1f}% keystrokes saved, "
          f"{0.181*n/tot*100:4.1f}% junction ambiguity")
