"""An original rule-based Burmese G2P, written from the orthography.

No dictionary is consulted at runtime. The rules encode the writing system
itself: consonant values, medials, rhymes (vowel sign + final), and the
word-internal voicing sandhi that Burmese applies to unaspirated onsets.
Facts of phonology are not copyrightable; myG2P is used ONLY as held-out gold
to evaluate this module, and nothing from it ships.

Target form: toneless MLC-like ASCII, the same alphabet the keyboard's input
code uses (tones, glottal marks and punctuation stripped).
"""
import re

# ------------------------------------------------------------------ script
CONS = {
    'က':'k','ခ':'kh','ဂ':'g','ဃ':'g','င':'ng',
    'စ':'s','ဆ':'hs','ဇ':'z','ဈ':'z','ည':'nj','ဉ':'nj',
    'ဋ':'t','ဌ':'ht','ဍ':'d','ဎ':'d','ဏ':'n',
    'တ':'t','ထ':'ht','ဒ':'d','ဓ':'d','န':'n',
    'ပ':'p','ဖ':'hp','ဗ':'b','ဘ':'b','မ':'m',
    'ယ':'j','ရ':'j','လ':'l','ဝ':'w','သ':'th','ဟ':'h','ဠ':'l','အ':'',
}
INDEP = {'ဣ':'i','ဤ':'i','ဥ':'u','ဦ':'u','ဧ':'ei','ဩ':'o','ဪ':'o','ဿ':'tha'}
MED_Y = {'ျ','ြ'}          # both palatal medials romanize as j/y
MED_W = 'ွ'
MED_H = 'ှ'                 # aspirating medial
ASAT = '်'
STACK = '္'
DOT_BELOW = '့'; VISARGA = 'း'; ANUSVARA = 'ံ'

VOWEL_SIGNS = set('ာါိီုူေဲ')

# (vowel-signs, final-consonant-or-'') -> rhyme. Built from the script's
# regular rhyme system; '' final means open syllable.
RHYME = {
    ('', ''): 'a',
    ('ာ', ''): 'a', ('ါ', ''): 'a',
    ('ိ', ''): 'i', ('ီ', ''): 'i',
    ('ု', ''): 'u', ('ူ', ''): 'u',
    ('ေ', ''): 'ei', ('ဲ', ''): 'e',
    ('ော', ''): 'o', ('ေါ', ''): 'o', ('ို', ''): 'ou',
    # nasal finals
    ('', 'င'): 'in', ('', 'ဉ'): 'in', ('', 'ည'): 'i',
    ('', 'ယ'): 'e', ('ွ', 'ယ'): 'we',
    ('', 'န'): 'an', ('', 'မ'): 'an', ('', 'ဏ'): 'an',
    ('ိ', 'န'): 'ein', ('ိ', 'မ'): 'ein',
    ('ု', 'န'): 'oun', ('ု', 'မ'): 'oun',
    ('ွ', 'န'): 'un', ('ွ', 'မ'): 'un',
    ('ော', 'င'): 'aun', ('ို', 'င'): 'ain',
    ('ိ', 'င'): 'in',
    # stop finals (glottalised; toneless target keeps the vowel letter)
    ('', 'က'): 'e', ('', 'စ'): 'i', ('', 'တ'): 'a', ('', 'ပ'): 'a',
    ('', 'ဋ'): 'a', ('', 'ဒ'): 'a', ('', 'ဘ'): 'a', ('', 'ဗ'): 'a',
    ('ိ', 'တ'): 'ei', ('ိ', 'ပ'): 'ei', ('ိ', 'က'): 'ei', ('ိ', 'စ'): 'ei',
    ('ု', 'က'): 'ou', ('ု', 'ဂ'): 'ou', ('', 'ဂ'): 'e',
    ('ို', 'န'): 'ain', ('ို', 'ဏ'): 'ain', ('ို', 'မ'): 'ain',
    ('ော', 'ဂ'): 'au',
    ('ု', 'တ'): 'ou', ('ု', 'ပ'): 'ou',
    ('ေ', 'ာ'): 'o',
    ('ော', 'က'): 'au', ('ို', 'က'): 'ai',
    ('ွ', 'တ'): 'u', ('ွ', 'ပ'): 'u',
    ('ျ', ''): 'a',
    # anusvara behaves as -an; dot-below handled by stripping
    ('ံ', ''): 'an', ('ုံ', ''): 'oun', ('ိံ', ''): 'ein',
}

MY = re.compile(r'[က-႟]')


def segment(text):
    """Original syllable segmenter: a codepoint walk, not a borrowed regex.

    A new syllable starts at each base consonant or independent vowel unless
    that consonant is (a) killed by a following asat — then it is the previous
    syllable's final — or (b) stacked below via U+1039.
    """
    sylls, cur = [], ''
    chars = list(text)
    for i, ch in enumerate(chars):
        if ch in CONS or ch in INDEP:
            killed = i + 1 < len(chars) and chars[i + 1] == ASAT
            stacked = i > 0 and chars[i - 1] == STACK
            # a consonant followed by U+1039 is the stacked FINAL of the
            # syllable in progress, not the start of a new one
            stacks_next = i + 1 < len(chars) and chars[i + 1] == STACK
            if cur and not killed and not stacked and not stacks_next:
                sylls.append(cur)
                cur = ch
                continue
        cur += ch
    if cur:
        sylls.append(cur)
    return sylls


def _syllable(s):
    """One syllable -> toneless roman, or None if it isn't Burmese."""
    if not MY.search(s):
        return None
    s = s.replace('ါ', 'ာ')          # tall aa is a glyph variant of aa
    if s and s[0] in INDEP:
        return INDEP[s[0]]
    onset, i = '', 0
    if i < len(s) and s[i] in CONS:
        onset = CONS[s[i]]; i += 1
    # A stacked pair C1+U+1039+C2 closes this syllable with C1 and opens an
    # inner one with C2 (kum.pa.ni pattern). Handle by splitting and recursing.
    k = s.find(STACK, i)
    if k > i and k - 1 >= i and s[k - 1] in CONS and k + 1 < len(s):
        head = s[:k - 1] + s[k - 1] + ASAT       # C1 becomes an asat final
        tail = s[k + 1:]
        h, t = _syllable(head), _syllable(tail)
        if h is not None and t is not None:
            return h + t
    med_y = med_w = med_h = False
    while i < len(s) and (s[i] in MED_Y or s[i] in (MED_W, MED_H)):
        if s[i] in MED_Y: med_y = True
        elif s[i] == MED_W: med_w = True
        else: med_h = True
        i += 1
    vowels, final = '', ''
    while i < len(s):
        ch = s[i]
        if ch in VOWEL_SIGNS:
            vowels += ch; i += 1
        elif ch == ANUSVARA:
            vowels += ch; i += 1
        elif ch in (DOT_BELOW, VISARGA):
            i += 1                       # tone: stripped in the target
        elif ch in CONS and i + 1 < len(s) and s[i + 1] == ASAT:
            final = ch; i += 2
        elif (ch in CONS and i + 2 < len(s) and s[i + 1] == DOT_BELOW
              and s[i + 2] == ASAT):
            final = ch; i += 3            # the tone dot sits between C and asat
        elif ch == ASAT:
            i += 1
        else:
            i += 1
    # aspirating medial: devoice/aspirate the onset
    if med_h and med_y and onset in ('l', 'th', ''):
        onset, med_y, med_h = 'sh', False, False
    if med_h:
        onset = {'m':'mh','n':'nh','ng':'ngh','nj':'njh','l':'lh','j':'sh',
                 'w':'wh'}.get(onset, onset)
        if onset == 'th': onset = 'th'
    if med_y:
        # MLC palatal series: velars fuse with the palatal medial
        if onset == 'k': onset = 'ky'
        elif onset == 'kh': onset = 'ch'
        elif onset == 'g': onset = 'gy'
        elif onset == 'ng': onset = 'nj'
        elif onset == 'th': onset = 'sh'
        elif onset == '': onset = 'j'
        else: onset = onset + 'j'
    rhyme = None
    if med_w:
        rhyme = RHYME.get((MED_W + vowels, final)) or RHYME.get((MED_W, final))
    if rhyme is None:
        rhyme = RHYME.get((vowels, final))
    if rhyme is None:
        rhyme = RHYME.get(('', final), 'a')
    if med_w and (MED_W + vowels, final) not in RHYME and (MED_W, final) not in RHYME:
        rhyme = 'w' + rhyme if rhyme != 'a' else 'wa'
    return (onset + rhyme) or 'a'


# Word-internal voicing sandhi: after an open/nasal syllable, an unaspirated
# onset voices. This RULE is what generates dha/ga/da/ba as variants —
# the alternation the dictionary pipeline could only memorise.
VOICE = {'ky':'gy','ch':'gy','k':'g','kh':'g','s':'z','hs':'z',
         't':'d','ht':'d','p':'b','hp':'b','th':'dh'}


def romanize(word, variants=False):
    """word -> canonical roman, or (if variants) the set of sandhi variants."""
    parts = []
    for s in segment(word):
        r = _syllable(s)
        if r is None:
            return None
        parts.append(r)
    if not variants:
        return ''.join(parts)
    outs = {''}
    for idx, p in enumerate(parts):
        alts = {p}
        if idx > 0:
            for plain in sorted(VOICE, key=len, reverse=True):   # longest first
                voiced = VOICE[plain]
                if p.startswith(plain) and not p.startswith(voiced):
                    alts.add(voiced + p[len(plain):])
                    break
        outs = {o + a for o in outs for a in alts}
    return outs
