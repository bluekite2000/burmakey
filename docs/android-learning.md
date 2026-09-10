# Android: on-device learning and consented telemetry

The design spec for how a BurmaKey Android IME improves itself. The governing
rule, from which everything else follows: **a keyboard sees passwords, OTP
codes, and private messages, so typed text never leaves the device.** Learning
that needs raw text happens on the phone; anything that leaves is a derived
number the user agreed to send.

Three tiers, shipped in this order.

---

## Tier 1 — per-user, on-device (default, no consent, no network)

This is the whole product's promise kept, and the biggest single win for the
individual user. The web engine already learns within a session (recency +
bigram); Android makes it **persist** and adds **personal spelling** and
**personal vocabulary**.

### What persists (SQLite or Protobuf in app-private storage)

| store | shape | purpose |
|---|---|---|
| `recency` | word → decayed count | short-term "what you just used" |
| `bigram` | word → {nextWord → count} | your phrasing |
| `user_spell` | syllable → {romanization → count} | **how YOU spell** (learns dha vs tha for you) |
| `user_vocab` | word → count | names, slang, words no dictionary has |
| `learned_pref` | prefix → {word} | your words reachable by prefix |

`user_spell` is the important addition: the web engine has one global variant
table; on Android each user's own table is layered on top, so after ~50 words
the keyboard predicts *your* spelling first. `user_vocab` captures out-of-
dictionary words the first time you commit them raw, so မောင်မောင် is offered
the second time you type it.

### Pruning (mandatory — the long-run sim measured 5.1 KB/day unbounded)

- `recency`: exponential decay, evict below a floor. Bounded by construction.
- `bigram` / `user_vocab`: cap total entries (e.g. 20k pairs); evict
  least-frequent-least-recent when over. A ring, not a landfill.
- Everything is user-clearable in one tap ("forget what I've typed"), and
  wiped on app uninstall by the OS.

### What this delivers

A keyboard that fits the individual within a day, with zero data leaving the
phone and no consent dialog — because nothing is shared. This is the default
and, for most users, the entire story.

### Build Tier 1 so Tier 3 is an update, not a rewrite

The one forward-compatibility decision, and it costs nothing now: express the
learned state as **parameters that can be diffed and averaged**, not ad-hoc
counters. If Tier-1 learning is a set of numeric weights over a fixed feature
space, Tier 3 is "compute the delta on that state, add DP noise, send it" — a
pure addition. If it is bespoke counter structures, Tier 3 forces the whole
learning layer to be rewritten. Decide the shape here; build nothing else for
Tier 3 yet.

---

## Tier 2 — consented aggregate telemetry (opt-in, derived numbers only)

For population-level improvement — better *defaults* for the next new user —
the app asks once, in the chat, exactly as the web keyboard already does. If
the user agrees, it sends **derived counts, never text.**

### What is sent (and what is not)

SENT (small, periodic, batched):
```
{ "syl_spell":  { "သ": {"tha": 8, "dha": 5}, ... },   // how words were spelled
  "typos_fixed": 3,                                   // fuzzy-fallback hits
  "oov_rate":   0.11,                                 // share of unknown words
  "keys_per_word": 2.7 }                              // effort
```
NEVER SENT: message text, word sequences, the vocabulary you typed, anything
reconstructable into what you wrote. The unit is a syllable's romanization
tally, decoupled from the words it came from.

### Guardrails on the opt-in itself

- **Off by default.** The keyboard works fully without it.
- **Minimum-count threshold** before any syllable is reported (never send a
  count of 1 — a rare spelling could fingerprint a rare word).
- **Strip anything typed in a password / OTP / email field** — Android exposes
  `inputType`; those fields are excluded from telemetry entirely, and ideally
  from Tier-1 learning too.
- **One-tap withdraw**, and a visible log of what a submission contained.

This is the same consent model already built and tested in the web keyboard;
it ports directly.

**What this frees, and what it does not.** Syllable-spelling counts give you an
owned *variant table* — they replace the myG2P-derived spelling weighting. They
do **not** replace myPOS, which supplies word frequencies, bigrams, and a
language model that syllable counts never touch. Escaping myPOS is a higher rung
on a sensitivity spectrum:

| consent-collect | sensitivity | frees you from |
|---|---|---|
| syllable spelling counts | low — safe as specced above | variant weighting (myG2P) |
| word frequency counts | medium — needs min-count + noise | the frequency model (myPOS) |
| typed word→word pairs, in order | **high** — text-adjacent | the chat corpus itself |

The third rung is the chat-register corpus the study calls otherwise
unobtainable. Tier 2's "derived counts, never text" deliberately does **not**
collect it. Reaching it means either the explicit, prominent, off-by-default
"donate my typing" opt-in (which sends `[burglish, word]` pairs — use sparingly)
or Tier 3, which learns the language model from that text without the text ever
leaving the phone.

---

## Tier 3 — federated learning + differential privacy (later, the strong version)

The state-of-the-art form of "self-improves from real usage without seeing
text," and what Gboard actually does. Worth building once Tiers 1–2 prove the
demand.

- The phone trains a model update **locally** on the user's own typing.
- It sends only a **noised gradient / count vector**, never the data — with
  **differential privacy**: calibrated noise added before it leaves, so no
  single user's contribution is recoverable even in principle.
- A server averages thousands of these into a new default model, pushed back
  as an update.

DP is the mathematical guarantee that turns "trust us, it's aggregated" into
"provably cannot be de-anonymised." It sits at the moment of departure: local
update computed → noise added → sent. Everything before the noise stays on the
phone.

**Gated on scale, not just effort.** Federated learning is meaningless below a
large userbase: with tens or hundreds of users there are too few updates to
average, and the DP noise swamps the signal. It starts paying only at the
thousands-of-active-users level. So Tier 3 is blocked on having the userbase
that makes it work — one more reason it is last, and one more reason to ship
Tiers 1–2 and grow first. The client change is an ordinary app update (a version
bump, not a new app); the real weight is the server-side aggregation
infrastructure.

---

## The threat model, stated plainly

Explicitly NEVER done, at any tier:
- raw typed text off the device
- word sequences or reconstructable n-grams off the device
- anything at all from password / OTP / email / secure fields
- silent collection — every share is opt-in, disclosed, and withdrawable

What the tiers cost the attacker who compromises the server: at Tier 1,
nothing (no server). At Tier 2, a bag of syllable spelling counts with no words
attached. At Tier 3, DP-noised aggregates that are provably non-individual.
There is no configuration in which "what someone typed" is on a server.

---

## Build order

1. **IME shell** — the InputMethodService: Latin key grid, shift/symbol pages,
   cursor + selection, `inputType` awareness (this is also what excludes secure
   fields), settings UI. The unglamorous ~80%; none exists yet.
2. **Tier-1 learning + pruning** — port the v4 engine (Rust core → JNI, per the
   next-engine doc) and add the persistent stores above.
3. **Tier-2 consent + telemetry** — reuse the web keyboard's sharing question
   and derived-count schema.
4. **Tier-3 federated + DP** — only after Tiers 1–2 show it is wanted.

Ship 1–2 as v1. It is a self-improving keyboard, shippable on Play, that keeps
every promise the project has made — and it does not need passive collection to
get there.
