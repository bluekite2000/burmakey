# BurmaKey Android IME

Walking skeleton. A minimal `InputMethodService` that registers as a system
keyboard and types into any app's text field. No Gradle — built with the raw
SDK tools so it stays offline and dependency-free.

## Build + run on the emulator

    bash android/build.sh                 # -> android/build/burmakey.apk
    adb install -r android/build/burmakey.apk
    adb shell ime enable com.burmakey.ime/.BurmaKeyService
    adb shell ime set    com.burmakey.ime/.BurmaKeyService

Then focus any text field. Verified on an Android-34 emulator: typing `nay`
showed နေ / နေရာ / နေ့ / နေထိုင် / နေမကောင်း in the candidate bar (same ranking
as the web keyboard); tapping နေ committed U+1014 U+1031 into a Chrome field;
`dha`+space committed သလား — the voiced variant, via the same multi-spelling
lexicon. The engine (Engine.java) mirrors the tested logic in src/ and web-my/;
the 48k-line v4 lexicon ships as an APK asset.

## Status

- [x] IME registers, appears, commits text into other apps  (this skeleton)
- [x] v4 engine ported to Java: Burglish in, Burmese out
- [x] suggestion bar + candidate ranking
- [x] number/symbol pages (Latin digits + Burmese numerals ၀-၉ + ။ ၊ punctuation)
- [x] one-shot shift (uppercase)
- [x] key-press pop feedback (key lifts + lightens on touch, like a native keyboard)
- [x] hold-to-repeat backspace
- [x] haptic feedback on keypress (respects system setting)
- [x] cursor keys ← → (hold to repeat; commits pending draft first)
- [x] buffer reset on new field (onStartInputView) — no draft leaks between fields
- [x] Tier-1 on-device learning: recency + bigram + personal vocab, persisted to files/learn.tsv, pruned to caps
- [x] secure-field guard — no learning in password / OTP inputs
- [ ] text selection handles (arrow keys done; selection still TODO)
- [ ] long-press for numbers/accents on the letter page

Next: cursor + selection (arrow keys, tap-to-move) and long-press for
numbers/accents on the letter page. The core — type Burglish, get ranked
Burmese, commit clean Unicode, and learn your word preferences on-device
(nothing leaves the phone) — works and is verified on the emulator.
