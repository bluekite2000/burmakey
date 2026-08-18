# What myG2P and myPOS actually contain, and what a better engine looks like

A study of the two datasets this project is built on, and a proposal for the
engine that should replace the current one. Every number below was measured
against the data, not estimated; the commands are at the end.

## 1. The data is richer than the pipeline

**myG2P v2** is not a two-column word list. It has five:

| col | content | used today |
|---|---|---|
| 0 | row index | — |
| 1 | word | yes |
| 2 | **gold syllable segmentation** | yes |
| 3 | MLC-style romanization, per syllable | yes (argmax only) |
| 4 | **IPA, per syllable, with tone** | **no** |

24,802 rows, 24,009 unique words. The 764 words with several rows are not
duplicates — they record real pronunciation variants.

**myPOS v3**: 43,196 sentences, 537,233 tokens, 33,579 word forms, 16 POS
tags. Top-1,000 forms cover 82.2% of tokens; 61.8% of forms are hapax.
**The POS tags are never used by the engine.**

## 2. Four measured problems

### 2.1 The romanizer throws away most of its evidence

`burmese2.py` keeps only the most frequent romanization per syllable:

```python
SYL = {s: c.most_common(1)[0][0] for s, c in syl_roman.items()}
```

- **45%** of the 2,348 syllables have more than one attested romanization
- that line discards **18.3%** of all 71,007 attestations

What it discards is not noise. It is Burmese voicing alternation, the most
systematic phonological process in the language:

| syllable | kept | discarded |
|---|---|---|
| သ | tha (461) | **dha (302)**, thin, thei, da … |
| က | ka (416) | **ga (302)**, kha … |
| တ | ta (397) | **da (224)** |
| စ | za (248) | **sa (241)** |
| ပ | pa (320) | **ba (109)**, pjin (75) |

### 2.2 The variant normaliser accepts 10.8% of real spellings

Expanding every word through all attested syllable romanizations gives about
**9.3 spellings per word**. The eight hand-written rules shipped in the keyboard
(`ph→hp`, `ay→ei`, `aw→o` …) accept **10.8%** of them and reject **89.2%** —
including `ga`, `da`, `dha`, `ba`, `gya`.

This is the "variant normaliser is untested" caveat, quantified. It is worse
than untested: the data needed to build it correctly was loaded, counted, and
then thrown away by an `argmax`.

Accepting every attested spelling raises input ambiguity (52.5% → 79.0% on the
covered vocabulary). That is the right trade. **Input ambiguity is what the
ranker is for; input rejection has no recovery** — today a user who writes
`dha` for သ gets nothing at all.

### 2.3 The language model is blind where it matters most

The ranker scores `freq + 10·recency + 100·bigram`. On held-out text:

- **29.6%** of word bigrams were never seen in training — the bigram term
  contributes nothing on almost a third of predictions
- POS bigrams cover **100%** of the same contexts, with 180 types against
  164,950 word-bigram types

A class-based backoff would fire exactly where the current model is silent.

### 2.4 The segmenter is hand-written against gold data it ignores

`sylbreak()` is one regex, measured at **89.4%** against myG2P's own splits —
which sit in column 2 of the file it already reads.

## 3. The engine I would build instead

### 3.1 Transliteration as a weighted FST, not a dictionary

The correct formalism for romanized IME input is a weighted finite-state
transducer, which is what Google's Indic transliteration keyboards use. Build
three and compose:

```
  B : Burglish spelling  →  IPA        (weighted, learned from myG2P cols 3+4)
  P : IPA                →  Burmese    (from cols 4+2)
  L : Burmese            →  Burmese    (n-gram language model)
  decode = B ∘ P ∘ L
```

Why this beats the current prefix dictionary:

- **variants are native**: every attested spelling is an arc with a weight
  taken from its myG2P count, instead of one canonical string plus rules
- **it generalises**: routing through IPA means an unseen word still
  transliterates, where a word-keyed dictionary fails outright — this attacks
  the 12.7% out-of-lexicon rate directly
- **tone is representable**: column 4 carries all four tones (à á a̰ aʔ);
  string matching on MLC ASCII cannot see them
- **one composition, one shortest path**: no separate normaliser to hand-tune

Tooling: **Pynini** (Python, OpenFst bindings) to build and test, exported to a
compact binary FST for the runtime. This is mature, boring technology.

### 3.2 A real language model

Replace raw bigram counts with **Kneser-Ney n-grams (KenLM)**, interpolated
with a **POS-class model** for backoff. Keep the on-device recency term: the
long-run simulation showed it compounds and that decaying it *hurts*.

A distilled neural LM is worth a look later, but n-gram + class backoff is the
step with the evidence behind it today.

### 3.3 Learn the segmenter

Column 2 is gold. Train a CRF or a small subword model on it and stop at 89.4%
only if nothing does better. Errors here propagate into every downstream stage.

### 3.4 One engine, two runtimes

The current engine exists twice — Python for research, JavaScript for the demo,
and would need a third copy for an Android IME. Write it once in **Rust**:

- **WASM** for the browser demo
- **JNI / NDK** for the Android `InputMethodService`
- the FST and LM ship as binary assets, memory-mapped

## 4. The licence is the real constraint

myG2P and myPOS are **CC BY-NC-SA 4.0**: noncommercial, share-alike. No amount
of engineering changes that. A better engine is also a legally shippable one:

1. **Ask Ye Kyaw Thu for commercial terms.** Cheapest path by far.
2. **Check Google `language-resources`** for Burmese (Apache-2.0); it supplied
   this repo's Khmer lexicon under CC BY 4.0.
3. **Wiktionary** Burmese pronunciations (CC BY-SA) for G2P coverage.
4. **Grow your own.** The consented streams in the keyboard produce a
   chat-register corpus that nobody else has and nobody can licence away.

Note that an FST-based G2P *reduces* the dependency: it needs rules and a seed
lexicon, not a 24k-word dictionary memorised wholesale.

## 5. Order of work

1. Stop discarding variants — index all attested spellings, weighted. Days,
   not weeks, and it is the largest single win available.
2. Add the POS-class backoff.
3. Settle the licence before any of the rest.
4. Then FST + KenLM + Rust, as one engine.

## Reproducing the numbers

```bash
git clone https://github.com/ye-kyaw-thu/myG2P /tmp/myg2p
git clone https://github.com/ye-kyaw-thu/myPOS /tmp/mypos
cd src && python3 study_data.py
```
