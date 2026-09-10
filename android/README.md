# BurmaKey Android IME

Walking skeleton. A minimal `InputMethodService` that registers as a system
keyboard and types into any app's text field. No Gradle — built with the raw
SDK tools so it stays offline and dependency-free.

## Build + run on the emulator

    bash android/build.sh                 # -> android/build/burmakey.apk
    adb install -r android/build/burmakey.apk
    adb shell ime enable com.burmakey.ime/.BurmaKeyService
    adb shell ime set    com.burmakey.ime/.BurmaKeyService

Then focus any text field; the keyboard appears. Verified on an Android-34
emulator: typing produced "hello world" in a Chrome input, character for
character.

## Status

- [x] IME registers, appears, commits text into other apps  (this skeleton)
- [ ] v4 engine ported to Kotlin/Java: Burglish in, Burmese out
- [ ] suggestion bar + candidate ranking
- [ ] number/symbol pages, shift, cursor + selection, inputType handling
- [ ] Tier-1 on-device learning + pruning  (see docs/android-learning.md)

The engine port is next: the ranking logic is already specified and tested in
Python (src/) and JS (web-my/); this is a mechanical translation, not new
design.
