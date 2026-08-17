# Typing Lao Without Learning Anything New: A Predictive Input Method Over Informal Romanization

**Draft 1 — August 2026**
**Status: simulation study. No user trials. No native-speaker review.**

---

## Abstract

Most Lao speakers under forty type Lao on phones in "karaoke Lao" — an
unstandardized Latin transcription that omits tone and vowel length. It is
fast to type and severely lossy to read: in our conversation simulations,
84–88% of tokens sent are spelled identically to at least one other Lao word.
We first attempted the classical remedy — a designed orthography that writes
the missing distinctions — and show by simulation that every such design
either costs keystrokes, costs readability, or both: an information-discarding
code is always faster for the *writer*. We then invert the problem. **Draft 4**
is an input method in which the user types unmodified karaoke Lao, a
frequency-recency-bigram ranker identifies the intended word, and the
keyboard emits an unambiguous form (Lao script, or a tone-complete
romanization). In simulations over a 155-word natural dialogue and a
3,297-word 25-topic stress test, draft 4 required 34–42% fewer taps than
present-day practice while reducing receiver-side ambiguity from 84–88% to
17–22% (0% when emitting Lao script), and it degrades exactly to the status
quo on out-of-vocabulary input. A corpus experiment shows that pretraining
the ranker on the only publicly obtainable Lao running text (UDHR + news
headlines) *hurts* performance due to register mismatch, implying that
on-device personal learning is not a fallback but the correct architecture.
All results are simulated; the concluding section lists what only human
trials can answer.

---

## 1. Problem

Lao script is phonemically adequate and institutionally healthy; this is not
a literacy problem. The problem is a typing niche: SMS-era handsets could not
render Lao, users improvised a Latin transcription by English pronunciation
intuition, and the habit outlived the constraint because Latin keyboards have
better prediction and require no layout switch. The transcription—"karaoke
Lao"—drops the six lexical tones and the nine-vowel length contrast.

The damage concentrates in exactly the words people use most. Common Lao
words are short; short toneless strings collide. Measured over our lexicon
(§5.1), 31% of *distinct words* share a karaoke spelling with another word,
but weighted by simulated usage, **76.8–88% of tokens in a conversation** are
ambiguous as sent. The spelling `khaw` corresponds to ເຂົ້າ (rice), ຂ່າວ
(news), ເຂົ່າ (knee), ຂາວ (white), and others; `khu` to ຄູ (teacher), ຄູ່
(pair), ຂູ່ (threaten). Part-of-speech context resolves roughly two-thirds of
collisions (§6.4); one word in three of the ambiguous residue survives even
that.

## 2. Related systems

**Quốc ngữ** demonstrates a full replacement orthography succeeding, but
under conditions Lao does not have (a literacy crisis, then institutional
enforcement) and with a diacritic budget suited to print, not phones.
**Hmong RPA** demonstrates the tone-as-final-letter trick surviving seventy
years of real use, and directly inspired our drafts 1–3. **BGN/PCGN Lao
romanization** writes no tone at all and was designed for atlases, not
typists. **Keyman's Lao Phonetic keyboard and LaoScript 8** offer romanized
*transliteration* — the user must know Lao orthography (which tone mark, which
of two /kʰ/ letters) — and have not displaced karaoke Lao; they serve people
who can already write Lao, not the karaoke population. **Pinyin IMEs** are
the direct architectural precedent for draft 4: users type a toneless code,
the engine selects the word, the output is unambiguous. Pinyin's lesson is
that hundreds of millions will adopt an input code without ever intending to
adopt an orthography.

## 3. The orthography attempts (drafts 1–3), briefly

Draft 1 (hand-designed; ASCII-only, tone letters from the coda-stranded set
{r v q z c}, length by vowel doubling) was verified by exhaustive enumeration
of all 22,704 phonotactically legal syllables: injective, round-trippable,
zero collisions. The verifier also falsified two of its designer's claims:
digraphs assumed safe within syllables are ambiguous *across* syllable
boundaries, and all boundary ambiguity traces to the unmarked tone (measured
2.9% of two-syllable strings; 18.1% for unmarked-tone syllables, 0.0% for
every marked tone). Writing the zero onset reduced boundary ambiguity 61%.

Draft 2 searched 144 spelling configurations for keystrokes-to-disambiguate
and collision rate; the winner (single-letter onsets, tone letter after the
onset, high tone unmarked) beat draft 1 by 11% on keystrokes at identical
accuracy — and was unreadable (ແມວ "cat" → `myhw`), because familiarity was
not in the objective. Draft 3 added familiarity (frequency-weighted edit
distance from the karaoke spelling) as a third objective; the Pareto-optimal
familiar design is karaoke Lao plus exactly two rules — *double a long vowel;
append one tone letter* (ໄວ້ `way` → `wayq`) — and lands within 0.5% of
draft 1's typing cost. Conclusion: **the spelling axis is exhausted.** No
orthography that writes the missing information can beat the code that
discards it, on the writer's side of the channel.

Two empirical byproducts survive into draft 4: the *high* tone, not the mid,
is the most frequent (31.0% by dictionary type-count; 29.9% by token count
over real running text, §7) and is therefore the correct unmarked tone; and
the token-frequency head of Lao is dominated by function words that a
dictionary-based frequency model underrates.

## 4. Draft 4: architecture

The design premise: the writer's laziness and the reader's clarity are not in
conflict if the keyboard translates between two codes.

**Input code.** Unmodified karaoke Lao, generated from the phonemic lexicon
by deleting tone, collapsing length, and omitting the zero onset — i.e., the
code users already emit, requiring zero learning.

**Output code.** The committed word is emitted in Lao script (receiver
ambiguity 0%) or draft-3 romanization (receiver ambiguity 17–22% token-
weighted, all residual cases being true homophones no orthography can
separate).

**Candidate generation.** A prefix index over input spellings, beam-limited
to the top 50 words by static frequency per prefix, unioned with all
personally-learned words matching the prefix. The bar is populated at prefix
length zero, so a contextually predicted word costs one tap.

**Ranking.** `score(w) = freq(w) + α·recency(w) + β·bigram(prev, w)` with
α=10, β=100. `freq` is the static unigram prior; `recency` and `bigram` are
per-user counters starting at zero and updated on every commit. A sweep
(α×5, β×3) moved mean taps by 0.01 — the gains are structural, not tuned.
Top-5 candidates are displayed (top-3 was tested; 5 dominates even after
pricing the added scanning cost at 0.5 tap-equivalents per bar-pick).

**Commit and fallback.** Space accepts the top candidate; tapping accepts
another. If no candidate matches, the raw typed string is committed verbatim
and added to the personal lexicon. This yields a hard guarantee: **for any
input, cost and output are never worse than present-day karaoke typing.**

## 5. Experimental setup

**5.1 Lexicon.** The 21,391-word Google language-resources Lao spellcheck
list (Apache-2.0, via `laonlp`), phonemized by a rule engine (consonant class
× tone mark × live/dead syllable × vowel length → tone; regex vowel-pattern
matcher for segments). 20,163 words (94.3%) phonemize cleanly; glosses from
the 51k-entry laonlp Lao–English dictionary. The dictionary's own
pronunciation column was evaluated and rejected as a tone source (26%
diacritic coverage, five inconsistent marks, internal contradictions).

**5.2 Frequency model.** Three tiers — the 117-word Lao stopword list, the
laonlp POS-tagger's memorized vocabulary, then remaining words ordered
short-first — with Zipf weights 1/rank^0.95. This is an assumption, not data;
§7 measures its error (4/20 overlap with the corpus top-20) and its
robustness (the tone ranking it produced was confirmed by token counts).

**5.3 Test streams.** (a) A hand-scripted 40-message, 155-word two-person
dialogue over ten everyday topics, built from glossed lexicon words
(word-order naturalness not guaranteed; the metric depends only on which
words are typed). (b) A generated 600-message, 3,297-word stream spanning 25
topic blocks with a 55% core-function-word mixture — realistic frequencies,
random word order, which *understates* bigram gains. (c) All simulations
model a perfect typist: no typos, instant candidate recognition, cost = keys
pressed + one commit tap per word.

## 6. Results

**6.1 Natural dialogue (155 words).**

| System | taps/word | receiver ambiguity |
|---|---|---|
| karaoke typed out (today) | 4.70 | 88% |
| karaoke + learning engine | 2.72 | 88% |
| draft 3 typed directly + engine | 2.98 | 17% |
| **draft 4 (karaoke in → clear out)** | **2.72** | **17% / 0%** |

Draft 4 equals the fastest system and the clearest system simultaneously:
−42% taps vs. today. 24.5% of words cost a single tap (zero-key context
prediction). Top-1 was the intended word on 48% of commits; on the rest the
user picks candidate #2–#5 at equal tap cost but nonzero attention cost.

**6.2 Stress test (3,297 words, 25 topics, 470 distinct words).**

| System | taps/word | receiver ambiguity |
|---|---|---|
| karaoke typed out | 4.66 | 84% |
| **draft 4** (shortlist 3) | **3.09** | **22% / 0%** |
| **draft 4** (shortlist 5) | **2.79** | 22% / 0% |

−34% to −40% vs. today. By rarity band (shortlist 3): top-200 words 2.59 vs
4.62 (−44%); ranks 200–2000, 3.58 vs 4.35 (−18%); rank 2000+, 4.28 vs 5.70
(−25%). The engine never loses, even in the rare tail. Zero-key hits fall to
3.3% in this stream (random word order starves the bigram model),
bracketing the dialogue's 24.5% as the natural-language upper estimate.

**6.3 Why the spelling could not win alone.** Draft 3 typed directly costs
3.24 taps/word on the stress test vs. draft 4's 3.09 with the identical
engine: emitting a longer code is never cheaper than emitting a shorter one,
independent of prediction quality. All orthography-only designs (drafts 1–3
without an engine) cluster at 4.0–4.7 taps/word — indistinguishable from or
worse than today.

**6.4 Ambiguity under context.** Filtering homophone sets by part of speech
(a crude context proxy): karaoke's token ambiguity falls 88% → 31%; draft 3's
17% → 1%. Grammar rescues most karaoke collisions but leaves roughly one
word in three of a conversation genuinely undecidable; the worst surviving
sets (e.g. `khaw`: 7 same-POS words) are same-category nouns that syntax
cannot separate.

## 7. The corpus experiment (negative result)

The only publicly reachable real Lao running text from our environment was
the official UDHR Lao translation plus ~45 RFA/VOA Lao news headlines: 1,576
tokens after cleaning PDF text-layer artifacts, 100% Lao script, 77% lexicon
coverage. Two findings and one failure:

- **Token-level tone frequencies** (high 29.9%, mid 23.4%, rising 19.3%)
  match the dictionary type-count ranking, closing the proposal's §9.3
  caveat: the high tone is confirmed as the correct unmarked tone.
- **The assumed frequency model's head is wrong**: 4/20 overlap with the
  corpus top-20, which is dominated by function words (ແລະ, ຂອງ, ໄດ້, ມີ).
- **Pretraining the engine on this corpus made it worse**: dialogue-test
  taps rose 2.50 → 2.89, zero-key hits fell 34.8% → 14.8%, and a weight
  sweep (prior scaled ×0.3 → ×0.01) shows monotone recovery toward the
  cold-start baseline without ever crossing it. This is register mismatch:
  legal/news vocabulary displaces chat vocabulary from a 5-slot bar.

Since the correct register (informal chat) exists only in private messages
on users' phones, no shippable pretraining corpus exists. **Cold-start
per-user learning is therefore not a compromise; it is the optimal available
architecture**, and the failed pretraining is its evidence.

## 8. Limitations

1. Every number is simulation; no human has typed on this keyboard.
2. The simulated typist is perfect: no typos (no fuzzy matching is
   implemented), no hesitation, instant recognition of the intended
   candidate. Bar-scanning is priced crudely (0.5 tap-equivalents) and only
   in the tuning study.
3. The frequency model is assumed (§5.2); its head is measurably wrong
   (§7), which likely *understates* function-word prediction gains.
4. The dialogue stream is glossed-word assembly, not native sentences; the
   stress stream is topic-coherent word salad. Real syntax should improve
   bigram prediction relative to both.
5. Vientiane Lao only. Native-script tone-class indirection, which adapts
   across dialects, is genuinely lost in any Latin tone spelling.
6. A silent new failure mode exists: accepting a wrong homophone without
   looking sends a confidently wrong word, where karaoke's vagueness at
   least warned the reader to guess. Unquantified.
7. The 21k lexicon misses slang, names, and recent borrowings; the fallback
   handles them without suggestions.

## 9. Future work

Ten Lao speakers, two phones, one afternoon — the five questions in
`summary-for-lao-readers.md` (candidate-bar trust, tone-letter aesthetics,
real-life homophone pain, length-marking preference, dialect breakage)
gate everything else. Then, in order: an instrumented prototype (iOS keyboard
extension; the engine is trivially portable), measurement of real
characters-per-word against users' own karaoke baseline, fuzzy matching over
karaoke spelling variation (`j`/`ch`, `x`/`s`, vowel guesses), and — only if
a chat-register corpus ever becomes ethically available (e.g. opt-in
donation) — pretrained context models.

## Acknowledgements & data

Built on Wannaphong Phatthiyaphaibun's `laonlp` (Apache-2.0): tokenizers,
the Google language-resources spellcheck list, dictionaries, stopwords, and
tagger vocabulary. Tone rules follow r12a's Lao orthography notes. Corpus
texts: OHCHR's official UDHR Lao translation (freely reproducible); RFA/VOA
Lao headline titles (factual data, attributed). All code in this repository
is MIT-licensed. Simulation scripts: `src/draft4b.py` (architecture),
`src/tune.py` (shortlist/weights), `src/sim_long.py` (stress test),
`src/ingest.py` (corpus experiment), `src/verify.py` (orthography
verification).
