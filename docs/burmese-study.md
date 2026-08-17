# Burmese replication study — draft-4 architecture on Myanmar data

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
a learning engine. The gap is identical to Lao's: transliteration exists,
the pinyin contract does not.

## Method

Better data than the Lao study: myG2P provides 24,802 words with tone-marked
romanizations; mining its syllable alignments yields a 2,348-entry
syllable→roman map plus a rule syllable-breaker (89.4% exact-match vs myG2P's
own splits), which romanizes 16,192 corpus words — **87.3% token coverage** of
real running text (first iteration, dictionary-only: 21.1%, and its results
were discarded as biased). myPOS supplies 41,738 real segmented sentences:
39,738 train (frequencies, bigram prior), 2,000 held-out test (19,898 scored
tokens). Input code = toneless Burglish (tone marks stripped from MLC-style
romanization); output = Burmese script, unambiguous by construction; engine =
the Lao draft-4 ranker unchanged (freq + 10·recency + 100·bigram, beam 50,
5-candidate bar).

## Results (19,898 real test tokens)

| System | taps/word | receiver ambiguity |
|---|---|---|
| Burmese script, key-per-character (today's keyboards) | 5.18 | 0% |
| Burglish typed out (today's chat) | 4.90 | **67.7%** |
| draft-4 engine, cold start | 2.68 | 0% |
| **draft-4 engine, corpus-pretrained** | **2.58** | **0%** |

- **−50.2% taps vs script typing; −47.4% vs Burglish chat — while eliminating
  ambiguity entirely.** Larger gains than Lao (−34…−42%), because Burmese
  words are longer (more syllables), giving prediction more to save.
- **Toneless Burglish is even sicker than karaoke Lao**: 67.7% of running
  words ambiguous (`taja` = 7 words, `akyi` = 7, `acha` = 6…), yet it is
  *still* marginally faster to type than the script (4.90 vs 5.18) — which is
  exactly why people use it. The engine beats both at once.
- **Corpus pretraining HELPED here (+0.10 taps saved, zero-key 14.7→17.9%)**,
  unlike Lao where it hurt — because train and test share register. This
  completes the Lao finding: pretraining is not bad per se; *mismatched*
  pretraining is. With a matched corpus, ship the prior.
- Shortlist 5 beats 3 (2.58 vs 2.84), replicating the Lao tuning result.
- Only 1.2% of in-lexicon tokens required typing in full.

## Caveats

Simulated perfect typist (no typos; instant candidate recognition); bar-pick
on 69% of words is a real attention cost not priced in taps. The script-typing
baseline (one key per codepoint) is a fair approximation of layout keyboards
but ignores their shift-layer costs (which would worsen the baseline, not the
engine). 12.7% of tokens fall outside the romanizable lexicon and were skipped
(the raw-fallback guarantee covers them in a real product). Burglish spelling
in the wild varies more than tone-stripped MLC; a variant-normalization layer
(as built for Lao) is needed before user trials. myPOS is news/general
register, not chat — closer than Lao's UDHR, still not ideal.

## Conclusion

The draft-4 architecture transfers to Burmese with **larger** measured gains
than the original Lao study, on **better** evidence (real held-out sentences
rather than constructed dialogue). The engine needed zero design changes —
only the lexicon and romanizer are language-specific, together ~100 lines
mined from existing CC-licensed resources. Scripts: `src/burmese.py`,
`src/burmese2.py`; results: `src/burmese2_results.json`.

## Head-to-head vs Bagan (10M+ downloads, market leader)

Fairness design: both sides receive the IDENTICAL engine (freq + recency +
bigram, corpus-pretrained, 5-candidate bar); only the input code differs.
Streams: held-out real sentences — chat (≤8 words, 800 msgs) and essay
(≥15 words, 200 sentences), ~4.7k words each. Layer costs measured: the top
33 script characters cover 97.2% of real keystrokes, so shift-layer overhead
is only ~3% — script entry is not as layer-punished as assumed.

| taps/word | chat | essay |
|---|---|---|
| Bagan as actually used (weak prediction) | 5.24 | 5.41 |
| Bagan + ideal engine (does not exist) | 2.42 | 2.58 |
| Draft 4 (Burglish in, script out) | 2.45 | 2.67 |

**Findings.** (1) Against Bagan as it exists, draft 4 halves the taps
(−52% chat, −50% essay; ~29 → ~61 wpm at 2.5 taps/s). (2) Against a
hypothetical Bagan carrying our exact engine over script keys, it is a
statistical tie — script characters are more informative per tap, offsetting
the 26-key simplicity. **The engine, not the Latin input code, is the entire
measured advantage.** (3) Draft 4's remaining edge over the hypothetical is
qualitative: no script-layout skill needed (the Burglish generation already
has Latin muscle memory), larger key targets (typo rates unmodelled but
favour 26 keys), and free English↔Burmese code-switching without keyboard
switching — pervasive in real Myanmar chat. (4) Product implication: ship
BOTH input modes over one engine — script-prefix prediction for script
typists, Burglish for the chat generation. The engine is the product; input
codes are skins.


## Chat-register simulation and the try-it web keyboard

myPOS is news register; a simulated chat stream (600 messages, 3,308 words
assembled from the conversational high-frequency vocabulary, word order
approximate) checks the register the keyboard targets: Burglish ambiguity
57%, script typing 5.81 taps/word, Burglish 5.47, **draft-4 engine 3.30
(−43% / −40%)** — gains hold outside the news register. Zero-key prediction
collapses (0.9%) in scrambled word order, confirming it derives from real
syntax; real chat sits between this floor and the +18% measured on real
sentences.

`web-my/index.html` is the Burmese try-it keyboard: full 16,192-word lexicon,
identical engine and three-level analytics as the Lao page, plus a
Burglish-variant normalizer (nay→nei, kaung→kaun, pyaw→pjo, ph→hp, ny→nj…)
that needs native tuning — variant rules were derived from spelling logic,
not from Burmese users. Output is always canonical Unicode; on-device
processing is a safety property, not just a preference, for Myanmar users.
