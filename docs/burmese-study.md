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
| Bagan as actually used (character entry) | 4.10 | 4.30 |
| Bagan + ideal engine (does not exist) | 2.33 | 2.51 |
| Draft 4 / BurmaKey (Burglish in, script out) | 2.45 | 2.67 |

Note: BurmaKey's figures reproduce the original head-to-head exactly
(2.45 / 2.67); the two Bagan arms land slightly below the first run
(4.10 vs 5.24, 2.33 vs 2.42) because that script was never committed and had
to be rebuilt from its description — and because the per-word commit tap it
charged for script entry does not exist. `src/h2h_mobile.py`.

### Second pass — seconds per word on a phone

A tap is not a tap on a handset. Three effects the tap count hides, and they do
not all favour us: (1) overflow glyphs sit behind a layer switch, which turns
out to be nearly irrelevant at 99.5% base-layer coverage; (2) a candidate-bar
pick is one tap but adds a visual scan that grows with position, plus a long
reach — both engine systems pay this on most words; (3) script characters carry
more information per tap, so the script system reaches the right candidate in
fewer keystrokes (2.33 vs 2.45).

**Bagan was measured, not assumed.** v14.62 was installed on an Android 14
emulator, every key position probed by tap and long-press, and 15 held-out
chat sentences typed on it and verified character-for-character
(`scratchpad/bench2.py`, keymap in `MEASURED_BASE`/`MEASURED_HOLD`). Three
corrections, and they do NOT all favour us:

1. **Layout: 10 columns x 4 rows**, the SAME key width as a 26-key Latin
   layout, not the 11 columns first guessed. That guess handed BurmaKey a
   Fitts advantage that does not exist.  (-38.6% -> -37.4%)
2. **Base layer is assigned by alphabet order, not frequency.** It holds only
   32 glyphs, so the common medials (ha, wa) and several frequent vowel signs
   sit behind a long-press: **9.2% of real corpus glyphs**, against the 0.5%
   the model assumed.  (-37.4% -> -42.3%)
3. **There is no per-word commit tap.** Burmese script is written without
   spaces between words; the model was charging a space-bar tap per word,
   inflating the competitor by a full tap. Measured on the real app:
   **4.46 taps/word**, versus the 5.18 the study had modelled.
   (-42.3% -> **-31.7%**)

Net: -38.6% fully assumed -> **-31.7% measured**. Measurement made the
competitor look better, not worse.

**The arm's central assumption is now observed.** Typing real high-frequency
word prefixes into Bagan (e.g. the start of သည်) produces NO word candidates —
only the composing string echoed back as an "add to user dictionary"
affordance. "Bagan as actually used" really is character-by-character entry.
Caveats: default configuration, Unicode mode, fresh install, emulator;
TTKeyboard and Zawgyi mode were not tested.

Costing every action in seconds — Fitts's law from real key sizes and the
actual key-to-key travel of the typed sequence, a position-dependent scan for
candidate picks, and notice + backspace + retap for mis-taps:

| s/word | chat | essay | chat wpm |
|---|---|---|---|
| Bagan as actually used | 1.99 | 2.05 | 30.1 |
| Bagan + ideal engine (does not exist) | 1.30 | 1.39 | 46.0 |
| Bagan + ideal engine + ideal key placement | 1.26 | 1.34 | 47.8 |
| Draft 4 / BurmaKey | 1.36 | 1.44 | 44.1 |

**This corrects two earlier claims.** (1) Against Bagan as it exists, the gain
is **~32%, not ~50%** — a candidate pick costs a scan that a tap count treats
as free. (2) Against a hypothetical Bagan carrying our exact engine, it is
**not a "statistical tie": BurmaKey is consistently 3-5% slower**, in all 81
parameter combinations swept. Script characters narrow the candidate list
faster than Latin letters, and bigger Latin keys do not quite buy that back.

Sensitivity sweep (81 combinations of Fitts b, scan base, scan-per-slot, error
rate): vs Bagan-as-used −39.3%…−15.0% (chat), −37.2%…−13.7% (essay); vs
Bagan+engine +3.2%…+5.5% (chat), +2.6%…+4.5% (essay). Both signs are stable
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


## Long-horizon learning dynamics (`src/longrun.py`)

Every other number in this study is a SINGLE pass with fresh state, which
cannot say what on-device learning is worth over weeks or whether it goes
wrong. 24 simulated users x 20 days x 30 msgs/day, each
user on their own primary topic (k-means over content-word tf-idf; myPOS has
no topic metadata). The prior is pretrained on one half of the corpus and
every user stream is drawn from the disjoint other half without replacement.
This is NOT a competitor benchmark: simulated chatters only resample corpus
statistics we already have, so these are statements about engine mechanics,
not about people.

**Q1 — learning compounds, it does not saturate.** Against a `frozen` control
(same engine, learning off), the saving grows from **6.1% on day 1 to
10.2% on day 20**, still rising at the end. The control is flat
(2.767 -> 2.755), which is what shows the gain is learning rather
than easier text. A three-week-old keyboard is measurably better than a
freshly installed one.

**Q2 — a stale prior is harmless after a topic change.** Cohort designs
(switchers vs non-switchers) are confounded — different people, different
text, so they measure topic difficulty. Instead all arms type IDENTICAL
evaluation text and differ only in history: cold 2.572, primed on the
same topic 2.526 (-1.8%), primed on a different topic
2.571 (-0.0%). A topic change costs you the *benefit*
of priming, not a penalty — the engine degrades to its shipped prior instead
of fighting the user. (8 topic pairs.)

**Q3 — between-user spread is bigger than the design differences.** Mean
taps/word ranges 2.412..2.699 across 24 users — a spread of
11% of the median, larger than the entire
3-6% gap between BurmaKey and the hypothetical ideal-engine script keyboard.
Any single headline number, including ours, hides more variation than the
design argument is about.

**Q4 — state growth is linear and needs a pruning policy.** Above the shipped
prior, per-user state grows **5.1 KB/day** (1.8 MB/year)
with no sign of levelling by day 20 (940
recency entries, 2,909 learned prefixes).
Fine for year one, untenable forever. Nothing in the engine prunes today.

**Q5 — the unbounded recency counter is CORRECT; do not "fix" it.** The
shipped rule scores recency as a lifetime count that never decays, which
looked like a bug waiting to happen. Replaying identical streams: unbounded
2.534 overall, exponential decay (half-life 200 words)
2.555 (+0.8%), cap at 5
2.550 (+0.6%). Forgetting throws away exactly
the signal that makes learning compound. The obvious hardening would have made
the keyboard slower.

Reproduce: `python3 src/longrun.py` (seed 20260817, ~90s).


### Whole-corpus taps, every topic (measured keymap + arithmetic)

Both competitors were driven on a running emulator and neither offers word
prediction, so their cost is deterministic given the keymap. The keymap was
probed on the live app (tap / long-press / shift for every key position):
62 glyphs, **99.65% coverage** of corpus glyph instances, making **90.9% of
sentences fully typable** — versus 12% under the partial keymap earlier
figures used, which is why those figures were biased toward longer words.

| | taps/word |
|---|---|
| Bagan / TTKeyboard, character entry | **4.08** |
| BurmaKey, Burglish + ranker | **2.44** |
| difference | **−40.1%** |

27,181 sentences, 188,670 words, both systems on identical text. Per topic
(k-means, 10 clusters) the difference ranges **−34.8% to −43.1%** and never
flips; Bagan's own cost varies more by topic (3.66–4.60) than the advantage
does. Shift-page glyphs are negligible (0.05%); the layer that matters is
long-press at 9.2%.

**TTKeyboard was measured too.** Its Myanmar layout is 11 columns, space bar
reads "ZawCode". Typing produces no word candidates — same as Bagan — even
though the app is an AOSP LatinIME derivative that ships a suggestion strip
(it offers only a contact-names prompt for Burmese). Both emit U+200B with
standalone combining vowels. Character entry is therefore the right model for
both, which is why the arm is labelled "Bagan / TTKeyboard".

Reproduce: `probe_keymap.py`, `measure_bagan.py`, `corpus_taps.py`.

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
