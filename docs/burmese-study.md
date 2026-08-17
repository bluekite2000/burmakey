# Burmese study — romanized input with a learning ranker on Myanmar data

**Status: simulation on real corpus data. No user trials. No native review.**
**Data: myG2P v2 and myPOS v3 (Ye Kyaw Thu et al., CC BY-NC-SA 4.0 — noncommercial;
any commercial keyboard must relicense or rebuild these resources.)**

## Why Burmese

54.9M people, 39.8M internet users, 21M social identities (DataReportal 2026).
Youth type toneless romanized "Burglish"; the decade-long Zawgyi/Unicode split
additionally broke text encoding, search, and sorting. A lexicon-driven IME
emits canonical Unicode by construction — it fixes typing and encoding at once.

## Existing input methods (studied)

Bagan, Frozen, TTKeyboard (1M+ downloads, 4.4★) and Gboard Myanmar all type
the script character-by-character on shifted layouts; none offers phonemic
romanized input with prediction. Burglish.app offers transliteration without
a learning engine. That is the gap: transliteration exists, the pinyin
contract — type what you know, receive what you meant — does not.

## Method

myG2P provides 24,802 words with tone-marked
romanizations; mining its syllable alignments yields a 2,348-entry
syllable→roman map plus a rule syllable-breaker (89.4% exact-match vs myG2P's
own splits), which romanizes 16,192 corpus words — **87.3% token coverage** of
real running text (first iteration, dictionary-only: 21.1%, and its results
were discarded as biased). myPOS supplies 41,738 real segmented sentences:
39,738 train (frequencies, bigram prior), 2,000 held-out test (19,898 scored
tokens). Input code = toneless Burglish (tone marks stripped from MLC-style
romanization); output = Burmese script, unambiguous by construction; engine =
a learning ranker over lexicon candidates (freq + 10·recency + 100·bigram,
beam 50, 5-candidate bar), language-independent by design — only the lexicon
and the romanizer are Burmese-specific.

## Results (19,898 real test tokens)

| System | taps/word | receiver ambiguity |
|---|---|---|
| Burmese script, key-per-character (today's keyboards) | 5.18 | 0% |
| Burglish typed out (today's chat) | 4.90 | **67.7%** |
| ranker engine, cold start | 2.68 | 0% |
| **ranker engine, corpus-pretrained** | **2.58** | **0%** |

- **−50.2% taps vs script typing; −47.4% vs Burglish chat — while eliminating
  ambiguity entirely.** Burmese words are long (several syllables), which is
  what gives prediction so much to save.
- **Toneless Burglish is badly ambiguous**: 67.7% of running words collide
  (`taja` = 7 words, `akyi` = 7, `acha` = 6…), yet it is *still* marginally
  faster to type than the script (4.90 vs 5.18) — which is exactly why people
  use it. The engine beats both at once.
- **Corpus pretraining HELPED here (+0.10 taps saved, zero-key 14.7→17.9%)**,
  because train and test share register. Pretraining is not good or bad per
  se; *mismatched* register is what hurts. With a matched corpus, ship the
  prior.
- Shortlist 5 beats 3 (2.58 vs 2.84).
- Only 1.2% of in-lexicon tokens required typing in full.

## Caveats

Simulated perfect typist (no typos; instant candidate recognition); bar-pick
on 69% of words is a real attention cost not priced in taps. The script-typing
baseline (one key per codepoint) is a fair approximation of layout keyboards
but ignores their shift-layer costs (which would worsen the baseline, not the
engine). 12.7% of tokens fall outside the romanizable lexicon and were skipped
(the raw-fallback guarantee covers them in a real product). Burglish spelling
in the wild varies more than tone-stripped MLC, so a variant-normalization
layer is needed before user trials. myPOS is news/general register, not chat
— the register the keyboard actually targets is bracketed in §"Chat-register
simulation" below, not measured directly.

## Conclusion

The architecture holds up on Burmese, on strong evidence: real held-out
sentences rather than constructed dialogue. Only the lexicon and the romanizer
are language-specific, together ~100 lines mined from existing CC-licensed
resources; the ranker itself carries no Burmese knowledge. Scripts:
`src/burmese.py`, `src/burmese2.py`; results: `src/burmese2_results.json`.

## Head-to-head vs Bagan (10M+ downloads, market leader)

Fairness design: both sides receive the IDENTICAL engine (freq + recency +
bigram, corpus-pretrained, 5-candidate bar); only the input code differs.
Streams: held-out real sentences — chat (<=8 words, 800 msgs) and essay
(>=15 words, 200 sentences), ~4.7k words each. Layer costs measured: a 40-key
base layer covers 99.5% of real keystrokes, so layer-switch overhead is
negligible — script entry is not as layer-punished as assumed.

### First pass — taps per word

| taps/word | chat | essay |
|---|---|---|
| Bagan as actually used (character entry) | 5.10 | 5.30 |
| Bagan + ideal engine (does not exist) | 2.33 | 2.51 |
| Draft 4 / BurmaKey (Burglish in, script out) | 2.45 | 2.67 |

Note: BurmaKey's figures reproduce the original head-to-head exactly
(2.45 / 2.67); the two Bagan arms land slightly below the first run
(5.10 vs 5.24, 2.33 vs 2.42) because that script was never committed and had
to be rebuilt from its description. `src/h2h_mobile.py`.

### Second pass — seconds per word on a phone

A tap is not a tap on a handset. Four effects the tap count hides, and they do
not all favour us: (1) a Myanmar layout packs ~11 columns where Latin gets 10,
so its keys are smaller — slower and more error-prone under Fitts's law;
(2) overflow glyphs sit behind a layer switch, which turns out to be nearly
irrelevant at 99.5% base-layer coverage; (3) a candidate-bar pick is one tap
but adds a visual scan that grows with position, plus a long reach — both
engine systems pay this on most words; (4) script characters carry more
information per tap, so the script system reaches the right candidate in fewer
keystrokes (2.33 vs 2.45).

Costing every action in seconds — Fitts's law from real key sizes and the
actual key-to-key travel of the typed sequence, a position-dependent scan for
candidate picks, and notice + backspace + retap for mis-taps:

| s/word | chat | essay | chat wpm |
|---|---|---|---|
| Bagan as actually used | 2.22 | 2.32 | 27.1 |
| Bagan + ideal engine (does not exist) | 1.30 | 1.38 | 46.3 |
| Bagan + ideal engine + ideal key placement | 1.25 | 1.35 | 48.1 |
| Draft 4 / BurmaKey | 1.36 | 1.44 | 44.1 |

**This corrects two earlier claims.** (1) Against Bagan as it exists, the gain
is **~38%, not ~50%** — a candidate pick costs a scan that a tap count treats
as free. (2) Against a hypothetical Bagan carrying our exact engine, it is
**not a "statistical tie": BurmaKey is consistently 3-6% slower**, in all 81
parameter combinations swept. Script characters narrow the candidate list
faster than Latin letters, and bigger Latin keys do not quite buy that back.

Sensitivity sweep (81 combinations of Fitts b, scan base, scan-per-slot, error
rate): vs Bagan-as-used −45.5%…−23.6% (chat), −44.6%…−23.7% (essay); vs
Bagan+engine +3.6%…+6.2% (chat), +3.0%…+5.1% (essay). Both signs are stable
across the entire sweep; the magnitudes are not. The per-action constants are
literature-shaped assumptions, not measurements of Myanmar users.

**What survives, sharpened: the engine is the product.** The measured
advantage is prediction, not the Latin input code. BurmaKey's remaining edge
over the hypothetical is what this model cannot score: no script-layout skill
needed (the Burglish generation already has Latin muscle memory), larger key
targets, and free English<->Burmese code-switching without keyboard switching —
pervasive in real Myanmar chat. Product implication, unchanged and now better
supported: ship BOTH input modes over one engine. The engine is the product;
input codes are skins.


## Chat-register simulation and the try-it web keyboard

myPOS is news register; a simulated chat stream (600 messages, 3,308 words
assembled from the conversational high-frequency vocabulary, word order
approximate) checks the register the keyboard targets: Burglish ambiguity
57%, script typing 5.81 taps/word, Burglish 5.47, **the ranker engine 3.30
(−43% / −40%)** — gains hold outside the news register. Zero-key prediction
collapses (0.9%) in scrambled word order, confirming it derives from real
syntax; real chat sits between this floor and the +18% measured on real
sentences.

`web-my/index.html` is the Burmese try-it keyboard: full 16,192-word lexicon,
the same engine and three-level analytics as the study above, plus a
Burglish-variant normalizer (nay→nei, kaung→kaun, pyaw→pjo, ph→hp, ny→nj…)
that needs native tuning — variant rules were derived from spelling logic,
not from Burmese users. Output is always canonical Unicode; on-device
processing is a safety property, not just a preference, for Myanmar users.
