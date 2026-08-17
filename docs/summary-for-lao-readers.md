# A better way to type Lao on a phone

*A two-page summary for Lao readers. No linguistics background needed.*
*Status: designed and tested in simulation only — no Lao speaker has reviewed it yet. That review is what this document is asking for.*

---

## The problem you already know

When Lao people text each other, most type "karaoke Lao" — Lao words written
with English letters: *sabaidee*, *khob jai*, *bo pen nyang*. It's fast and
everyone's phone supports it. But it drops the tones and vowel lengths that
tell Lao words apart, so many words end up spelled the same.

We measured it. In a simulated 40-message chat between two friends, **88% of
the words sent were spelled identically to at least one other Lao word.**
The spelling *khaw* alone can be ເຂົ້າ (rice), ຂ່າວ (news), ເຂົ່າ (knee), ຂາວ
(white) and more. Readers usually work it out from context — but not always,
and everyone who texts in karaoke Lao has sent or received a message that
needed a second message to explain the first.

## The idea

**A keyboard where you type karaoke Lao exactly as you already do — and it
sends real Lao script.**

You type `khob jai`. The keyboard shows ຂອບໃຈ in the suggestion bar. You tap
it (or just hit space) and ຂອບໃຈ is what your friend receives. You never
learn a new spelling system. The keyboard learns *you* instead: the words you
use often, and which word tends to follow which, so suggestions get better
every day. It works in Messenger, TikTok, everywhere — it's just a keyboard.

If a word isn't recognized — a name, slang, anything — the keyboard simply
sends the letters you typed, exactly like today. **It can never be worse than
what you already do.**

This is the same trick Chinese typing uses: nobody types tone marks in
pinyin; the keyboard figures out the word.

## Does it actually save effort?

We simulated full conversations word by word — a 40-message chat between two
friends, and a long 3,300-word conversation across 25 topics (food, work,
family, weather, health, news…). Compared with typing karaoke Lao out by
hand, the smart keyboard needed **about 35–40% fewer key presses**, and the
messages arrived as real Lao script instead of ambiguous Latin.

| | Typing effort | What your friend receives |
|---|---|---|
| Karaoke Lao today | ~4.7 taps per word | ambiguous Latin (88% of words collide) |
| **This keyboard** | **~2.5–3 taps per word** | **real Lao script** |

About a quarter of common words cost a single tap, because the keyboard
predicts them before you type anything.

## The optional part: writing tones in Latin

Sometimes Lao has to be written in Latin letters — song lyrics, names,
teaching. For that we also designed a spelling that adds two small things to
normal karaoke Lao: **double the vowel if it's long, and add one letter at
the end for the tone.**

| Meaning | Karaoke today | With tones written |
|---|---|---|
| ໄວ້ (to keep) | way | wayq |
| ແພງ (expensive) | phaeng | phaaengr |
| ເມືອງ (city) | mueang | muueang |
| ຢາກ (want) | yak | yaakc |

Every spelling is the familiar one plus a letter or two. A computer check of
all 22,704 possible Lao syllables confirmed no two different syllables ever
get the same spelling.

## What we need from Lao readers — the questions only you can answer

1. **Do the suggestions feel right?** When you type `khaw`, the keyboard
   shows its best guesses of which word you meant. Would you trust that, or
   does picking from a list feel slower than just sending `khaw`?
2. **Does the tone-letter spelling look acceptable?** Is `wayq` readable, or
   ugly? Would `way4` (a number instead of a letter) be better?
3. **Which homophones actually cause confusion in your chats?** Our
   simulation says *khaw*, *kho*, *mo*, *pho*, *so*, *tho* are the worst
   offenders — each is 5–12 different words. Does that match your experience?
4. **Long vowels: `muueang` (double letter) or `mueahng` (added h)?** Both
   work technically; which reads better?
5. **What did we get wrong?** This was designed by a non-Lao speaker and a
   computer, using a 21,000-word dictionary and published descriptions of
   Vientiane pronunciation. Northern and southern speakers, especially: where
   does this break for you?

## Honest limitations

All numbers come from computer simulation, not from real people typing. The
design is based on Vientiane Lao; other dialects have different tones. The
dictionary behind the keyboard has 21,000 words and misses slang and new
borrowings (the fallback handles them, but without suggestions). And the one
thing no simulation can measure is whether this *feels* good to use — which
is exactly why this document exists.

*If you read Lao and have opinions about any of the above, you are the
expert this project is missing.*
