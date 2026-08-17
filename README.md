# Aksoon Laatin — a Latin orthography and smart keyboard design for Lao

**Status: designed and validated in simulation. Never reviewed by a native Lao
speaker. That review is the project's single missing ingredient — if you read
Lao, start with [docs/summary-for-lao-readers.md](docs/summary-for-lao-readers.md).**

Millions of Lao people type "karaoke Lao" — Lao in improvised English letters
(*sabaidee*, *khob jai*) with no tones and no vowel length. It works, but in a
simulated 40-message chat, **88% of words sent were spelled identically to at
least one other Lao word** (`khaw` = rice / news / knee / white / …).

This repo contains, in the order they were built:

0. **A white paper** consolidating the design and every experiment
   ([docs/whitepaper.md](docs/whitepaper.md)) — start here for the full story
1. **A standardization proposal** for Latin-script Lao ("Aksoon Laatin") —
   ASCII-only, tones written as final letters in the style of Hmong RPA
   ([docs/proposal.md](docs/proposal.md))
2. **A machine verifier** that enumerates all 22,704 legal Lao syllables and
   proves the spelling collision-free — and which found two real bugs in the
   hand-made design (`src/verify.py`)
3. **Three redesigns driven by simulation**, ending somewhere unexpected
4. **The punchline: the spelling doesn't matter as much as the engine.** The
   winning design ("draft 4") lets users type the karaoke Lao they already
   know, while a learning predictor picks the intended word and emits real
   Lao script — the pinyin architecture, applied to Lao

## Key results (all simulated — see caveats)

| Keyboard | Typing effort | Reader receives |
|---|---|---|
| karaoke Lao, typed out (today) | ~4.7 taps/word | 88% of words ambiguous |
| draft 3 spelling, typed directly | ~4.0 taps/word | unambiguous |
| **draft 4: karaoke in → Lao script out** | **~2.5–3.1 taps/word** | **real Lao script** |

- Draft 4 needed **34–42% fewer taps than today's typing** across a natural
  dialogue and a 3,300-word, 25-topic stress test, while eliminating the
  ambiguity problem entirely.
- It has a hard floor: an unrecognized word (name, slang) is sent as typed —
  it can never be worse than the status quo.
- Corpus experiment: pretraining the engine on the only obtainable real Lao
  corpus (UDHR + news headlines) made performance *worse* — register
  mismatch. The right training data (chat) exists only on users' phones, so
  the on-device-learning design is not a stopgap; it is the correct
  architecture.
- Token-frequency measurement over real running Lao confirmed the proposal's
  most contested choice: the high tone (29.9% of syllables) is the right one
  to leave unwritten.

## Try the keyboard (for Lao speakers)

`web/index.html` is a working, mobile-first version of the draft-4 keyboard:
type karaoke Lao in the box, tap the Lao word you meant, copy real Lao script.
The full 20k-word lexicon and the learning engine run entirely in the browser.

**Hosting (Netlify, recommended):** drag this folder onto app.netlify.com/drop
(or connect the repo) — `index.html` is the landing page, keyboards at
`/web-my/` (Burmese) and `/web/` (Lao). Analytics work out of the box: both
pages ship with `ANALYTICS.endpoint = "netlify"`, so sessions and feedback
land in your Netlify dashboard under Site → Forms ("analytics" form) with no
external service. Free tier: 100 submissions/month — fine for a pilot; swap
in a Formspree URL or raise the plan if testers exceed it. GitHub Pages also
works but needs a Formspree endpoint since it has no form handling.

**Analytics — three levels:** (1) session totals (taps/word, hit rates) and
(2) per-word content-free events (keys pressed, candidate position, timing)
are sent automatically once an endpoint is set — never message text. (3) The
actual typed words are shared only via an explicit opt-in "donate my typing"
toggle, off by default, with a live preview of exactly what would be sent —
this consented stream is the only ethical route to the chat-register corpus
the white paper (§7) shows is otherwise unobtainable. Unknown words likewise
require their own consent box. To receive data
automatically, create a free form endpoint (e.g. Formspree) and paste its URL
into the `ANALYTICS.endpoint` constant at the top of the page's script;
without an endpoint, the "send feedback" button falls back to a pre-filled
email. Update `ANALYTICS.mailto` and the GitHub link (marked CHANGEME) before
publishing.

## Try the demos (no install needed — open in a browser)

- `demos/aksoon-demo.html` — interactive keyboard simulator with a real
  19k-word lexicon; toggle between karaoke Lao and the tone-marked spelling
- `demos/typing-race.html` — animated side-by-side replay of both keyboards
  typing the same 40-message conversation, key by key
- `demos/convo.html` — that conversation annotated word by word, with every
  ambiguous spelling highlighted

## Reproduce the pipeline

```bash
pip install laonlp datasets --break-system-packages
cd src
python3 verify.py       # enumerate syllables, prove collision-freedom
python3 tones.py        # tone frequency over the 21k-word list
python3 lao2al.py       # build the draft-1 lexicon (writes lexicon.json)
python3 phonemize.py    # phoneme-level lexicon (writes phonlex.json)
python3 optimise.py     # draft 2: search 144 spellings for speed+accuracy
python3 optimise3.py    # draft 3: add familiarity as a third objective
python3 convo.py        # simulate a 40-message dialogue on both keyboards
python3 draft4b.py      # draft 4: karaoke input, learning engine, clear output
python3 sim_long.py     # 3,300-word 25-topic stress test  (few minutes)
python3 tune.py         # shortlist-size and weight tuning
python3 ingest.py       # corpus ingestion + the failed-pretraining result
```

Scripts are session artifacts, not a library: they read and write JSON in
their own directory, print their findings to stdout, and several run work at
import time. Read them top to bottom; each file's docstring says what
question it answers.

## What's known to be unresolved

- Every number here is simulation. No human has typed on this keyboard.
- The design targets Vientiane Lao; other dialects have different tone
  systems, and the native script's tone-class indirection (which travels
  across dialects) is genuinely lost in any Latin tone spelling.
- The frequency model mixes a stopword list, a POS-tagger vocabulary, and a
  Zipf assumption; a real chat corpus would replace it (and only exists on
  Lao phones).
- The suggestion-bar attention cost (picking candidate #2/#3 on ~54% of
  words) is priced crudely.
- Five specific questions for Lao readers are listed at the end of
  [docs/summary-for-lao-readers.md](docs/summary-for-lao-readers.md).

## Acknowledgements

- **Wannaphong Phatthiyaphaibun** — the [laonlp](https://github.com/wannaphong/laonlp)
  toolkit (Apache-2.0) provides the tokenizers and every word list used here.
  This project is downstream of that work in almost every file.
- Google's [language-resources](https://github.com/google/language-resources)
  Lao spellcheck list (Apache-2.0) — the lexicon base.
- Tone rules follow r12a's [Lao orthography notes](https://r12a.github.io/scripts/laoo/lo).
- The design conversation that produced this repo began with a question about
  the history of quốc ngữ, and ended by rediscovering why pinyin won: humans
  should type what they know; machines should write what they mean.

## License

MIT for the code and documents in this repo. Runtime data comes from
Apache-2.0 sources credited above; see LICENSE for data notes.
