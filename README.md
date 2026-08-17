# BurmaKey — type Burglish, get Burmese script

**Status: designed and validated in simulation on real corpus data. No user
trials, no native-speaker review. That review is the project's single missing
ingredient.**

Young Myanmar people type "Burglish" — Burmese in improvised English letters,
with no tones and no vowel length. It works, but measured over 19,898 real
held-out corpus tokens, **67.7% of words sent were spelled identically to at
least one other Burmese word** (`taja` = 7 words, `akyi` = 7, `acha` = 6…).
The reader guesses; usually right, sometimes wrong.

The fix is not a better spelling. It is the pinyin contract: let people type
the Burglish they already know, and let a learning predictor pick the intended
word and emit real Burmese script. Because the output is always canonical
Unicode by construction, the same design also sidesteps the decade-long
Zawgyi/Unicode split.

## Key results (all simulated — see caveats)

| System | Typing effort | Reader receives |
|---|---|---|
| Burmese script, key-per-character (today's keyboards) | 5.18 taps/word | unambiguous |
| Burglish typed out (today's chat) | 4.90 taps/word | 67.7% of words ambiguous |
| **BurmaKey: Burglish in → Burmese script out** | **2.58 taps/word** | **clean Unicode, unambiguous** |

- **−50.2% taps vs script typing, −47.4% vs Burglish chat**, while eliminating
  the ambiguity problem entirely.
- Hard floor: an unrecognized word (name, slang) is sent exactly as typed — it
  can never be worse than the status quo.
- Head-to-head against Bagan (10M+ downloads, market leader), re-run with a
  **mobile cost model** — seconds per word on a modelled phone (Fitts's law
  from real key sizes and travel, a position-dependent scan for candidate
  picks, mis-tap correction) rather than undifferentiated taps. Against Bagan
  as it actually behaves, BurmaKey is **~38% faster** (27 → 44 wpm). Against a
  hypothetical Bagan carrying this exact engine over script keys it is
  **3–6% slower**, consistently across an 81-point sensitivity sweep — script
  characters narrow the candidate list faster than Latin letters. Both
  corrections are less flattering than the earlier tap-count claims of −52%
  and "a statistical tie". **The engine, not the Latin input code, is the
  measured advantage.**
- **Long-horizon behaviour** (20 simulated days, `src/longrun.py`):
  on-device learning **compounds rather than saturating** — 6.1% better
  than a no-learning control on day 1, 10.2% by day 20, still improving.
  A topic change costs the benefit of priming but carries no penalty
  (-0.0% vs cold). Between-user spread
  (11% of the median) is larger than the
  gap between input designs. Per-user state grows 5.1 KB/day and needs a
  pruning policy. And the unbounded recency counter that looked like a bug is
  the best of three rules tested — decay and capping both make it slower.
- Corpus pretraining helps here (+0.10 taps saved, zero-key 14.7→17.9%)
  because train and test share register. Pretraining on a *mismatched* register
  hurts instead, so the corpus has to match the target register.
- Shortlist of 5 candidates beats 3 (2.58 vs 2.84 taps/word).
- Only 1.2% of in-lexicon tokens had to be typed out in full.

Full method, numbers and caveats: **[study/index.html](study/index.html)** —
the study page, with charts, comparison tables and sensitivity ranges (open it
in a browser, or visit `/study/` on the deployed site). Raw notes:
[docs/burmese-study.md](docs/burmese-study.md).

## Try the keyboard

`web-my/index.html` is a working, mobile-first browser keyboard: type Burglish
in the box, tap the Burmese word you meant, copy real Unicode. The full
16,192-word lexicon and the learning engine run entirely in the browser, plus a
Burglish-variant normalizer (nay→nei, kaung→kaun, pyaw→pjo, ph→hp, ny→nj…).

`index.html` is the landing page; `demos/burmese-race.html` is an animated
side-by-side replay of a script keyboard and this one typing the same messages,
key by key.

**Hosting (Netlify, recommended):** drag this folder onto app.netlify.com/drop
(or connect the repo) — `index.html` is the landing page, the keyboard is at
`/web-my/`. Analytics work out of the box: the page ships with
`ANALYTICS.endpoint = "netlify"`, so sessions and feedback land in your Netlify
dashboard under Site → Forms ("analytics" form) with no external service. Free
tier: 100 submissions/month — fine for a pilot; swap in a Formspree URL or
raise the plan if testers exceed it. GitHub Pages also works but needs a
Formspree endpoint since it has no form handling.

**Analytics — three levels:** (1) session totals (taps/word, hit rates) and
(2) per-word content-free events (keys pressed, candidate position, timing)
are sent automatically once an endpoint is set — never message text. (3) The
actual typed words are shared only via an explicit opt-in "donate my typing"
toggle, off by default, with a live preview of exactly what would be sent —
this consented stream is the only ethical route to a chat-register corpus,
which is otherwise unobtainable. Unknown words likewise require their own
consent box. Without an endpoint, the "send feedback" button falls back to a
pre-filled email. Update `ANALYTICS.mailto` and the GitHub link before
publishing.

## Reproduce the pipeline

```bash
git clone https://github.com/ye-kyaw-thu/myG2P /tmp/myg2p
git clone https://github.com/ye-kyaw-thu/myPOS /tmp/mypos
cd src
python3 burmese.py        # iteration 1: dictionary-only romanizer (biased, kept for the record)
python3 burmese2.py       # iteration 2: syllable romanizer, 87.3% coverage, headline numbers
python3 h2h_mobile.py --sweep   # head-to-head vs Bagan/TTKeyboard, mobile cost model
python3 longrun.py        # long-horizon learning dynamics (24 users x 20 days)
python3 mm_chat.py        # chat-register simulation (needs mm_data.pkl, see below)
python3 build_web_my.py   # regenerate the web keyboard (needs weblex_my.txt, see below)
```

Only the standard library is needed. Re-runs are not bit-identical: the
ranker breaks score ties by set-iteration order, which varies with Python's
string hash seed, so the last decimal drifts (2.5804 vs 2.5803 taps/word).
Every published figure is unaffected at the precision quoted; set
`PYTHONHASHSEED=0` if you want an exactly repeatable run.

Note that `mm_chat.py` and
`build_web_my.py` read two intermediate artifacts — `mm_data.pkl` and
`weblex_my.txt` — that are not committed and are not produced by any script in
this repo; they were built ad hoc in the original session. Regenerating them
from `burmese2.py`'s lexicon and frequency tables is outstanding work.

Scripts are session artifacts, not a library: they read and write JSON in their
own directory, print their findings to stdout, and run work at import time.
Read them top to bottom; each file's docstring says what question it answers.

## What's known to be unresolved

- Every number here is simulation with a perfect typist — no typos, instant
  candidate recognition. No human has typed on this keyboard.
- The suggestion-bar attention cost (picking a candidate on ~69% of words) is a
  real cost that taps do not price.
- 12.7% of corpus tokens fall outside the romanizable lexicon and were skipped
  in scoring; the raw-fallback guarantee covers them in a real product.
- Burglish spelling in the wild varies more than tone-stripped MLC
  romanization. The variant normalizer in the web keyboard was derived from
  spelling logic, not from Burmese users, and needs native tuning.
- myPOS is news/general register, not chat. The chat simulation
  (`src/mm_chat.py`) brackets it but assembles messages with approximate word
  order.
- The Burmese UI text in `index.html` and `web-my/index.html` has not been
  reviewed by a native speaker.

## Acknowledgements

- **Ye Kyaw Thu et al.** — [myG2P](https://github.com/ye-kyaw-thu/myG2P) v2
  (24,802 tone-marked romanizations) and
  [myPOS](https://github.com/ye-kyaw-thu/myPOS) v3 (41,738 segmented
  sentences), both CC BY-NC-SA 4.0. The lexicon, the romanizer and every
  frequency number in this repo are downstream of that work.

## License

MIT for the code and documents in this repo. Runtime data is CC BY-NC-SA 4.0
(noncommercial) — see LICENSE for data notes.
