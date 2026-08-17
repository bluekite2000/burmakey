# Aksoon Laatin

### A standardization proposal for Latin-script Lao

**Draft 1 · August 2026**

---

## 0. What this is

Latin-script Lao already exists. It is called *karaoke Lao*, it is used daily by a large share of Lao speakers under forty, and nobody designed it. It emerged in the SMS era when handsets sold in Laos could not render ພາສາລາວ, and it outlived the constraint that produced it because the Latin keyboard is faster and has working predictive text.

Because nobody designed it, it has no conventions. Tone is never marked. Vowel length is never marked. Spelling is improvised per writer from English orthographic intuition, which is itself inconsistent. The result is a writing system that regularly fails at its one job: Lao speakers report being unable to decipher messages written by other Lao speakers.

This document proposes a fix. It is not an invention. It is a standardization of something already in use, in the same sense that the *Dictionarium Annamiticum* of 1651 standardized a dozen competing missionary transcriptions of Vietnamese rather than creating Vietnamese romanization from nothing.

**This proposal does not seek to replace ອັກສອນລາວ.** The Lao script is phonemically well-designed, was rationalized in the 1960s reforms, and is not failing at anything. Vietnamese in 1900 had a genuine literacy crisis that quốc ngữ solved. Lao in 2026 does not. What Lao has is a widely-used informal romanization that is worse than it needs to be. That is the problem being addressed, and the scope should not be inflated beyond it.

---

## 1. Design constraints

These were fixed before any letter was assigned, and every subsequent decision follows from them.

**C1 — ASCII only. No diacritics.**

This is the binding constraint and it is not negotiable. The entire reason karaoke Lao exists is speed on a phone. A system requiring long-press for tone marks would be abandoned within a week, because the population it targets has already demonstrated — by choosing Latin over a perfectly good native script — that it will trade accuracy for keystrokes every time. Any proposal that ignores this is designing for linguists, not for users.

This rules out the Vietnamese model. Quốc ngữ's diacritic stack was designed for a printing press, where a compositor's effort is paid once and a reader's convenience is paid forever. On a phone, the writer pays every time.

**C2 — Tone must be written.**

Karaoke Lao's refusal to mark tone is the single largest source of its illegibility. Lao has six contrastive tones on unchecked syllables; discarding them collapses enormous numbers of distinct words into identical strings, and context does not always recover them. Any standard that leaves tone unwritten is not a standard, it is the status quo with better marketing.

**C3 — Vowel length must be written.**

Length is phonemic across all nine vowel qualities. Same argument as C2.

**C4 — Vientiane is the reference variety.**

Standard broadcast Vientiane Lao. Not because other varieties matter less, but because a standard needs one referent and this is the one with existing institutional weight. §9 addresses the cost.

**C5 — Do not fight entrenched usage without cause.**

Where karaoke Lao has already converged on a convention that works, keep it, even at the price of internal elegance. `j` for /t͡ɕ/ and `ae` for /ɛ/ are retained on these grounds. A standard that requires users to unlearn their existing habits for aesthetic reasons will lose to the habits.

---

## 2. Phoneme inventory being encoded

Vientiane Lao, following the standard description.

- **Initial consonants:** /b d p t k pʰ tʰ kʰ t͡ɕ m n ɲ ŋ f s h w l j ʔ/ plus the clusters /kw kʰw/
- **Final consonants:** /p t k m n ŋ w j/ only, plus /ʔ/ (automatic after short vowels)
- **Vowels:** nine qualities — /i e ɛ ɨ ɤ a u o ɔ/ — each with a phonemic length contrast
- **Diphthongs:** /iə ɨə uə/
- **Tones:** six on unchecked syllables — mid ˧, low ˩, low-falling ˧˩, rising ˨˦, high ˦, high-falling ˥˧. Four on checked syllables.

Note the shape of the problem: roughly fifty contrasts, twenty-six letters, no diacritics. It only works because Lao's coda inventory is tiny — eight consonants — which strands a large block of the alphabet with nothing to do in syllable-final position. That stranded block is where tone goes.

---

## 3. Consonants

| Lao | IPA | Aksoon Laatin | Note |
|---|---|---|---|
| ກ | /k/ | **k** | |
| ຂ ຄ | /kʰ/ | **kh** | |
| ງ | /ŋ/ | **ng** | also a final |
| ຈ | /t͡ɕ/ | **j** | retained from karaoke Lao (C5) |
| ສ ຊ | /s/ | **s** | |
| ຍ | /ɲ/ | **ny** | |
| ດ | /ɗ/ | **d** | implosive; no Latin equivalent, unmarked |
| ຕ | /t/ | **t** | |
| ຖ ທ | /tʰ/ | **th** | |
| ນ | /n/ | **n** | also a final |
| ບ | /ɓ/ | **b** | implosive; unmarked |
| ປ | /p/ | **p** | |
| ຜ ພ | /pʰ/ | **ph** | |
| ຝ ຟ | /f/ | **f** | |
| ມ | /m/ | **m** | also a final |
| ຢ | /j/ | **y** | also a final |
| ລ | /l/ | **l** | |
| ວ | /w/ | **w** | also a final |
| ຫ ຮ | /h/ | **h** | |
| ອ | /ʔ/ | **x** | zero onset — written, see §6 and §9.7 |
| ກວ | /kw/ | **kw** | |
| ຂວ ຄວ | /kʰw/ | **khw** | |

**Aspiration digraphs are safe.** `ph`, `th`, `kh` cannot be misread as consonant clusters because Lao has no consonant clusters other than /kw kʰw/. There is no /p/+/h/ sequence for `ph` to be confused with.

**The implosives are not marked.** /ɓ ɗ/ are written `b d` as if they were plain voiced stops. This loses information a phonetician would want. It is the correct call anyway: the contrast /ɓ/ vs /b/ does not exist in Lao — there is no plain /b/ to confuse it with — so nothing is lost that a reader needs.

**Letters not used for consonants:** `c q r v z x`. Five of these become the tone system.

---

## 4. Vowels

Length is marked by **doubling the first letter of the vowel grapheme**. One rule, no exceptions.

| IPA | short | long | Lao (short / long) |
|---|---|---|---|
| /i/ | **i** | **ii** | ິ / ີ |
| /e/ | **e** | **ee** | ເະ / ເ |
| /ɛ/ | **ae** | **aae** | ແະ / ແ |
| /ɨ/ | **eu** | **eeu** | ຶ / ື |
| /ɤ/ | **oe** | **ooe** | ເິ / ເີ |
| /a/ | **a** | **aa** | ະ / າ |
| /u/ | **u** | **uu** | ຸ / ູ |
| /o/ | **o** | **oo** | ໂະ / ໂ |
| /ɔ/ | **oa** | **ooa** | ເາະ / ອ |

Diphthongs, same doubling rule:

| IPA | short | long |
|---|---|---|
| /iə/ | **ia** | **iia** |
| /ɨə/ | **uea** | **uuea** |
| /uə/ | **ua** | **uua** |

**On `ae` and `oa`.** These are the two open-mid vowels and the system marks both with an added `a`. But `ae` puts the `a` first and `oa` puts it second, which is inconsistent and I am not going to pretend otherwise. `ae` for /ɛ/ is thoroughly entrenched in existing karaoke Lao and in Lao place-name spelling, and constraint C5 says do not fight that. `ao` for /ɔ/ was rejected because /a/ + final /w/ is written `aw` and the two would sit one transposition apart — a silent, undetectable typo class on a high-frequency vowel. So `oa` it is. This is a wart. Real orthographies have them; the useful thing is to know where they are.

**On `oa` generally.** This is the weakest grapheme in the system — it is unintuitive to an English-trained reader, and /ɔ/ is a high-frequency vowel, so the cost is paid often. §9 lists the alternatives that were considered and why each was worse. If any single decision in this document gets overturned in review, it should be this one.

---

## 5. Tones

Written as a **final letter**, following the model of the Hmong Romanized Popular Alphabet — which was designed in Laos in the early 1950s for a neighbouring tonal language, has been in continuous use by millions of writers for seventy years, and is the only large-scale proof that this approach survives contact with actual users.

The tone letter goes last in the syllable, after any final consonant.

| Tone | Contour | Letter |
|---|---|---|
| Mid | ˧ | *(unwritten)* |
| Low | ˩ | **r** |
| Low falling | ˧˩ | **v** |
| Rising | ˨˦ | **q** |
| High | ˦ | **z** |
| High falling | ˥˧ | **c** |

**Why one tone is unwritten.** RPA leaves its mid tone unmarked and this is the right precedent: the highest-frequency tone should cost zero keystrokes. Every syllable in the language is affected by this choice, so it is worth getting right — and the assignment below is provisional for exactly that reason.

**The letter assignments are arbitrary and should be finalized against a corpus.** There is no iconic logic here, just as there is none in RPA's `-b -s -j -v -m -g`. What matters is that the letters cannot collide with anything (§8) and that the frequent tones get the accessible keys. Which tone is actually most frequent in running Vientiane Lao text, and therefore which should be unmarked, is an empirical question this draft answers by assumption rather than by counting. **It should be counted.** If mid is not the most frequent tone, the unmarked slot goes to whichever is, and the rest shuffle accordingly. Nothing else in the system changes.

**`x` is not used as a tone letter.** It was the obvious sixth letter, but karaoke Lao and the French colonial place-name spellings both use `x` for /s/ — *Xieng Khouang*, *Xaignabouli*. Recruiting it as a tone letter would make every piece of legacy text a minefield. It is instead assigned to the zero onset (§3, §6), a job that testing showed was worth doing; the legacy-collision cost of that assignment is discussed in §9.7.

**Checked syllables** — those ending in `p t k` — carry only four contrastive tones rather than six. The same letters are used; two of them simply never occur in that environment. No special rule is needed.

---

## 6. Syllable structure and spacing

**Syllable template:** `(C)(w) V(V) (C_final) (T)`

Every syllable is an onset, a vowel, an optional final consonant from the set {p t k m n ng w y}, and an optional tone letter from {r v q z c}.

**Syllable boundaries.** Because tone letters can occur nowhere except syllable-finally, a tone letter is also a syllable delimiter. This has been tested rather than assumed (§8.1), and the result is sharper than expected: **boundary ambiguity is confined entirely to syllables carrying the unmarked tone.** Every marked tone measured at exactly 0% ambiguity. Unmarked-tone syllables measured at 18.1%, giving 2.9% across a representative two-syllable sample.

Two rules reduce that residue:

**Rule 1 — the zero onset is written `x`.** A syllable beginning with a vowel is the largest single source of ambiguity: it lets any preceding final consonant be reanalysed as the next syllable's onset. Writing the onset removes the reanalysis. Measured effect: 2.9% → 1.13%, a 61% reduction, with no new monosyllable collisions.

**Rule 2 — maximal onset, then hyphen.** The remainder is digraphs straddling a boundary: `ph` vs final `p` + onset `h`, `ny` vs final `n` + onset `y`, `kw` vs final `k` + onset `w`. Parse greedily, preferring the digraph as an onset; where that gives the wrong word, insert a hyphen — `hak-haat`. This makes parsing deterministic. How often hyphens are actually needed is a lexical question and needs a real word list to answer.

**Word spacing.** Aksoon Laatin **puts spaces between words.** The Lao script does not; it uses spaces at phrase and clause boundaries.

This is the largest deliberate break with native orthographic practice in this proposal, and it is here for a specific reason. Predictive text, autocorrect, search indexing, and essentially every piece of natural language tooling assumes space-delimited tokens. Lao word segmentation is an unsolved computational problem, and it is the direct cause of Lao-script typing on phones being so much less assisted than Latin typing. Writing the spaces makes the problem disappear rather than solving it.

The cost is that somebody has to decide what a word is. Lao compounds — particularly Pali-derived vocabulary and verb serialization — do not have obvious boundaries, and no fully consistent answer exists. This is a genuine open problem and is listed as such in §9. It is worth paying because the alternative is inheriting the segmentation problem that motivated the entire exercise.

**Loanwords.** International vocabulary is respelled phonemically, not borrowed orthographically. Not *computer* but the Lao pronunciation of it. Preserving source spelling would import English orthography's irregularity into a system whose entire value proposition is regularity.

---

## 7. Worked examples

> **Tone values in this section are illustrative.** The segmental spellings are reliable; the tone letters on individual words are drawn from general description rather than checked word-by-word against a Vientiane pronouncing dictionary. Before any version of this document circulates as a real proposal, every example needs verification against an authoritative source. Flagged rather than quietly guessed.

| Lao | Meaning | Aksoon Laatin | Typical karaoke Lao |
|---|---|---|---|
| ລາວ | Lao | **laawq** | lao, laow, lav |
| ວຽງຈັນ | Vientiane | **wiiang janr** | vientiane, wiengjan |
| ຫຼວງພະບາງ | Luang Phabang | **luuang pha baang** | luangprabang, lpb |
| ສະບາຍດີ | hello | **sa baay diir** | sabaidee, sbd, sabaydee |
| ຂອບໃຈ | thank you | **khooapq jayr** | khobjai, kobjai |
| ນ້ຳ | water | **naamq** | nam, narm |
| ເຂົ້າ | rice | **khawc** | khao, kao |
| ກິນ | eat | **kinr** | kin |
| ໄປ | go | **payr** | pai, bai |
| ຄົນ | person | **khonr** | khon |
| ບໍ່ | no, not | **booav** | bo, baw, bor |

**A sentence.** ຂ້ອຍກິນເຂົ້າ — "I eat rice."

> **khooayc kinr khawc**

Compare the karaoke Lao a real person would send: *koy kin kao*. Three syllables, three tones discarded, two vowel lengths discarded, and `kao` ambiguous across several common words. The proposal costs four extra keystrokes and recovers all of it.

**Comparison against the existing formal systems.** BGN/PCGN, the 1996 romanization used for maps and passports, writes *Vientiane* as **Viangchan** and marks no tone at all — it was built for rendering place names in English-language atlases, not for writing the language, and it fails C2 and C3 entirely. Library of Congress romanization is reversible to Lao script but uses diacritics, failing C1. Neither was ever intended to be typed by Lao people, and neither is.

---

## 8. Collision audit

Every grapheme checked against every environment it can occur in.

| Risk | Verdict |
|---|---|
| Tone letters `r v q z c` misread as consonants | **Safe.** None of the five is used as a consonant anywhere in the system, and Lao finals are restricted to {p t k m n ng w y}. A syllable-final `r v q z c` can only be a tone. |
| `ph th kh` misread as cluster | **Safe.** Lao has no such clusters. |
| `ng` vs `n` + `g` | **Safe.** `g` is never used alone. |
| `ny` vs `n` + `y` | **Safe** syllable-initially, where /ɲ/ occurs. `n` cannot be followed by `y` within one syllable, since `n` as a final ends the syllable. |
| `kw khw` vs `k` + final `w` | **Safe.** Position differs — onset cluster vs coda. |
| `ao` = /a/ + final /w/ vs `oa` = /ɔ/ | **Safe but confusable in reading.** Distinct letter sequences, but a transposition typo turns one into the other silently. Known weakness; see §9. |
| `ou` sequences | **Not used.** Avoided deliberately, as French-era spellings give it /u/ while English intuition gives it /aʊ/. |
| Long digraph vowels `aae eeu ooe ooa` vs vowel + vowel | **Safe.** Lao permits no vowel hiatus within a syllable outside the three diphthongs, so these strings have exactly one parse. |
| `h` as aspiration marker vs `h` as onset | **Safe.** Aspiration `h` only follows `p t k` within an onset; onset `h` is syllable-initial. |
| `x` | **Zero onset.** Not a tone letter; see §9.7 for the legacy-collision cost. |

### 8.1 Machine verification

The table above was checked by exhaustive enumeration rather than inspection (`verify.py`). Three results:

**Monosyllables are clean.** All 22,704 phonotactically legal syllables were generated and rendered. Distinct syllables produced 22,704 distinct strings — **zero collisions** — and every string parsed back to exactly one analysis. **Zero** round-trip failures, **zero** multiply-parsing strings.

**The audit above had a hole.** It verified digraphs *within* a syllable and concluded `ph th kh` and `ny` were safe. That is true within a syllable and false across a boundary: final `p` + onset `h` is indistinguishable from onset `ph`, and final `n` + onset `y` from onset `ny`. Sampling 60,000 two-syllable strings found 2.9% ambiguous, attributable as:

| Cause | Share of ambiguous cases |
|---|---|
| Zero onset reanalysed as coda of the previous syllable | 60.2% |
| Aspiration digraph across a boundary (`p`+`h` vs `ph`) | 22.8% |
| `ny` across a boundary (`n`+`y` vs `ny`) | 10.0% |
| Other | 7.0% |

**Ambiguity is a property of the unmarked tone alone.** Broken down by the first syllable's tone, every marked tone scored 0.0% and the unmarked tone scored 18.1%. Tone letters do delimit syllables exactly as §6 claimed; the unmarked tone is the only leak. This has a design consequence not previously identified — see §9.8.

Writing the zero onset as `x` was then tested as an intervention: ambiguity fell to 1.13% with no new monosyllable collisions. It is adopted in §6 as Rule 1.

---

## 9. Known problems

An orthography proposal that lists no failures is concealing them.

**1. `oa` for /ɔ/ is the weakest choice in the system.** Alternatives considered and rejected: `aw` (collides with /a/ + final /w/), `or` (`r` is a tone letter), `aw`/`ao` as a minimal pair (too confusable), bare `o` with `ou` for /o/ (imports the French/English `ou` conflict). Every option was bad; this one was least bad. It deserves a second look.

**2. Length-by-doubling interacts badly with digraph vowels.** `aae`, `eeu`, `ooe`, `ooa` are rule-governed but ugly, and ugliness has real adoption costs. **Alternative A**, worth trialling: mark length with postvocalic `h` instead — `mah` /maː/, `maeh` /ɛː/, `euh` /ɨː/. This is unambiguous, since `h` never occurs syllable-finally otherwise, and it handles digraphs cleanly. It was not adopted as primary because doubling matches what karaoke writers already do in *sabaidee* and *nyoo*, and C5 favours the incumbent. This is close to a coin flip and should be user-tested, not decided by argument.

**3. Which tone goes unmarked was assumed wrongly.** §5 guessed mid on RPA precedent. Measured against the 21,391-word Google Lao spellcheck list (`tones.py`, 45,752 syllables, 97.9% analysed), the distribution is:

| Tone | Share of syllables |
|---|---|
| high | 31.0% |
| mid | 24.5% |
| rising | 19.3% |
| high falling | 10.4% |
| low | 8.4% |
| low falling | 6.4% |

**The most frequent tone is high, not mid.** On the keystroke argument alone the unmarked slot should go to high, and §5 should be amended. Three caveats, all material:

- The tone table used is from a single source and emitted *seven* labels for a six-tone system; `rising` and `low rising` were merged on the assumption they are one tone. That assumption needs checking, and if it is wrong the ranking may shift.
- This is **type** frequency over a dictionary word list, not **token** frequency over running text. Every word counts once regardless of how common it is, which systematically overweights rare vocabulary. Token frequency is what actually governs keystrokes, and it needs a real corpus.
- 971 syllables (2.1%) did not analyse.

Combined with §9.8, the tradeoff is now quantified — the same choice sets both keystroke cost and boundary ambiguity, and they pull opposite ways:

| Unmark | Keystrokes saved | Junction ambiguity |
|---|---|---|
| high | 31.0% | 5.6% |
| mid | 24.5% | 4.4% |
| rising | 19.3% | 3.5% |
| high falling | 10.4% | 1.9% |
| low falling | 6.4% | 1.2% |

There is no dominant option. Picking one requires deciding what an ambiguous syllable junction costs relative to a keystroke, which is an empirical question about the predictor, not a question about the orthography.

**4. Word segmentation is unsolved.** §6 requires spaces between words and does not define a word. Compounds and Pali-derived vocabulary have no consistent boundary. Any real deployment needs a published word list settling the frequent cases, which is months of lexicographic work and is the single largest cost item in this proposal.

**5. Diphthong length may be phonemic and may not.** Sources differ on whether /iə ɨə uə/ contrast for length. The proposal provides `iia`/`ia` etc. in case they do. If the contrast is not real, those graphemes are dead weight and should be deleted.

**6. It is Vientiane-only.** Luang Phabang and southern varieties have different tone systems, and a Vientiane-based tone spelling will be wrong for their speakers in a way that Lao script — which encodes tone *class* rather than tone *value*, and so adapts across dialects — currently is not. **This is a real regression against the native script**, not a neutral difference. Lao script's indirection is a feature that this proposal discards, and any speaker outside Vientiane is entitled to object.

**7. Writing the zero onset as `x` reintroduces the legacy conflict `x` was reserved to avoid.** Legacy karaoke and colonial spellings use `x` for /s/ — *Xieng Khouang* — and both that and the new value are syllable-initial, so they genuinely compete. The 61% ambiguity reduction measured in §8.1 is judged worth it, since legacy `x` is largely confined to fixed place names and the whole point of the proposal is to supersede legacy spelling. The alternative, if that judgement is wrong, is an apostrophe for the zero onset: no letter collision, but it is a shifted key on many phone layouts and therefore violates the spirit of C1. Reasonable people could take the other branch.

**8. The unmarked tone trades keystrokes against parse ambiguity.** §5 chose which tone goes unwritten purely on frequency grounds — the commonest tone should be free. §8.1 shows the unmarked tone is also the *only* source of boundary ambiguity. These pull in opposite directions: leaving the most frequent tone unmarked minimises typing but maximises ambiguity, because ambiguity scales with how often unmarked syllables occur. The optimum is therefore not simply "unmark the commonest tone," and the corpus count in §9.3 needs to be scored against both costs rather than frequency alone. This was not visible before the system was tested and is the clearest argument in this document for building the verifier before the keyboard.

**9. Tone letters make words longer.** Roughly one extra character per syllable against karaoke Lao. Since keystroke economy is precisely why people adopted karaoke Lao, this is the mechanism by which the whole proposal could fail. The counterargument is that predictive text absorbs the cost once a dictionary exists — the extra letters make words *more* distinct and therefore *easier* to predict, so a good keyboard should make standardized text faster to type than the improvised kind. That argument is plausible and untested.

---

## 10. What would have to happen next

1. Corpus frequency count to fix the unmarked tone (§5, §9.3).
2. Verify every example word against a Vientiane pronouncing dictionary (§7).
3. User trial of doubling vs. `h`-lengthening with actual karaoke Lao writers (§9.2).
4. Publish a word list settling segmentation for the frequent cases (§9.4).
5. Ship a keyboard with a predictive dictionary. **Nothing above matters without this.** Orthographies are not adopted because they are well-designed; they are adopted because using them is easier than not. Quốc ngữ spread when the colonial administration made it the language of official business and the nationalist movement made it the language of mass literacy — the design quality of the script was almost incidental to both. Hmong RPA spread because missionaries printed books in it. A well-designed Lao romanization with no keyboard behind it is a PDF.

---

## 11. Adoption

### 11.1 The reframe

Do not try to replace karaoke Lao. Replace the keyboard.

An orthography competing against an entrenched informal one, on the strength of being better designed, loses. It has essentially always lost. What wins is a tool that is immediately more useful than the alternative, and which happens to have the orthography baked into it.

The model is **pinyin**. Pinyin's decisive victory was not as a script — almost nobody writes Chinese in pinyin. It was as an *input method*: you type sounds, the system gives you characters. Hundreds of millions of people became fluent pinyin users without ever intending to adopt pinyin, because it was the fastest route to the thing they actually wanted.

Aksoon Laatin should ship the same way: **a keyboard where you type Aksoon Laatin and get ອັກສອນລາວ**, with a toggle to send the Latin raw if you prefer. This does three things at once. It makes the standard useful to people who have no interest in the standard. It converts tone letters from a tax into the mechanism that fetches the right word. And it removes the political objection entirely — you are not undermining the national script, you are making it easier to type.

### 11.2 Why this hasn't already worked

Romanized Lao input methods exist. Keyman's Lao Phonetic keyboard is free and runs on Windows, macOS, Linux, iOS, Android and the web. LaoScript 8 has offered phonetic entry for years. Neither has displaced karaoke Lao, and any adoption plan that ignores this is proposing something already tried.

The reason they didn't win is instructive, and it is the gap Aksoon Laatin fits into. **Those systems are transliteration, not phonemic input.** They ask you to type the Lao *spelling* — you enter numbers 1–4 for the orthographic tone mark, and you need to know whether the word takes ຂ or ຄ. That means they help people who can already write Lao correctly. It does nothing for the person who defaults to karaoke Lao precisely because Lao orthography is the part they find hard.

Aksoon Laatin encodes *sound*, not spelling. A user who knows only how a word is pronounced can type it. The dictionary resolves it to correct Lao script. That is the pinyin contract, and it is aimed at exactly the population that currently writes *sabaidee*.

Secondary reasons those tools stalled, all fixable: niche distribution, paid desktop software in one case, and no predictive layer.

### 11.3 The keystroke argument, which is the whole thesis

Aksoon Laatin costs roughly one extra character per syllable against karaoke Lao. Since keystroke economy is *why karaoke Lao exists*, this looks fatal.

The counterargument: tone letters and length marking make words dramatically **more distinct from each other**, and prediction feeds on distinctness. `kao` in karaoke Lao is several different words and a predictor can do little with it. `khawc` is one word and can be completed from two or three keystrokes. With a real dictionary behind it, standardized text should be *faster to type* than improvised text, despite being longer to write out.

**This claim is testable and the entire project depends on it.** Build the keyboard, instrument it, measure characters-typed-per-word-produced against a karaoke Lao baseline. If standardized input is not faster in practice, the project has no economic engine and should be abandoned rather than promoted on aesthetic grounds.

### 11.4 Migration: never require learning before benefit

The keyboard must accept **sloppy karaoke Lao input** and quietly offer the correct Aksoon Laatin and the correct Lao script. Type `sabaidee`, get ສະບາຍດີ and `sa baay diir` in the suggestion bar. Type `kobjai`, get ຂອບໃຈ.

This is the single most important interface decision. It means nobody has to study anything to start benefiting, and users acquire the standard by seeing it offered thousands of times rather than by learning it. Fuzzy matching over an unstandardized input space is real engineering work, but it is the difference between a tool people install and a tool people are told to install.

### 11.5 Sequence

**Phase 1 — Prove the thesis.** Converter (Lao ↔ Aksoon Laatin), a corpus, and a measured typing trial with 30–50 habitual karaoke Lao writers. Answer §11.3 with data. Kill the project here if the answer is no. Also resolves the empirical questions in §9.

**Phase 2 — Ship the best Lao keyboard that exists.** Free, fast, no telemetry, iOS and Android, plus desktop layouts. It must be worth installing for someone who has never heard of this proposal and doesn't care — better prediction, better layout, handles both scripts, fuzzy karaoke input. Adoption comes from selfish utility, not advocacy. Keyman is a plausible distribution channel already reaching every relevant platform.

**Phase 3 — Content.** RPA stuck because missionaries printed books. The modern equivalents are song lyrics, video subtitles, Wikipedia, and a few large messaging communities. Lyrics are the natural beachhead — "karaoke Lao" is named after karaoke, and properly romanized Lao pop is a use case where getting tone right visibly matters.

**Phase 4 — Tooling.** Get Lao NLP to standardize on it: search, TTS, ASR, machine translation, name transliteration for passports and airline systems. This is where a standard becomes load-bearing infrastructure rather than a preference. It is also the least visible and most durable form of adoption.

**Phase 5 — Institutions, last.** Schools, the National University of Laos, eventually official recognition. Approaching the state early invites a fight about national identity before there is any constituency to defend the proposal. Approach it once there is a user base, and only ever as an input and transcription standard.

### 11.6 Framing, which is not optional

Never describe this as replacing or reforming the Lao script. It is an **input method and a transcription standard.** That is both the honest description and the only one that survives contact with a country where script is national identity and script reform has political history. The document that says "here is a better way to type ພາສາລາວ" gets a hearing. The document that says "here is a Latin alphabet for Lao" gets a fight it deserves to lose.

### 11.7 Honest odds

Full replacement of karaoke Lao in casual chat is unlikely, and the closest analogue says so. **Arabizi** — the Arabic chat alphabet — has been in mass use for over twenty-five years, has attracted numerous standardization proposals, and remains unstandardized. Informal writing systems resist standardization because their sloppiness is doing work: it signals informality, in-group membership, and speed. A teenager writing `sbd` to a friend is not making an error to be corrected.

The realistic best outcome is a **split**: Aksoon Laatin becomes standard wherever precision has value — dictionaries, language teaching, search and NLP, subtitles, official transliteration of names, anything a machine has to read — while casual chat stays as improvised as it has always been. That is a considerably smaller victory than replacement, and it is still worth building, because the precision domains are where the absence of a standard currently causes real damage.

The one scenario that produces fast, broad adoption is platform capture: Google's or Apple's Lao keyboard adopting it, or a dominant Lao app doing so. That is not something a proposal can engineer. It is something a proposal can be *ready for*, by being finished, tested, permissively licensed, and obviously correct when someone at a platform goes looking.

---

*Draft 1. Every empirical claim marked as unverified in this document is unverified. The tone letter assignments, the `oa` grapheme, and the length-marking strategy are the three decisions most likely to be wrong. The keystroke claim in §11.3 is the one that decides whether any of it matters.*
