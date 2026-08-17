"""Type real held-out Burmese sentences on the ACTUAL Bagan keyboard and count
the taps it costs.

Every character is produced by tapping Bagan's own keys on a running install;
the resulting text is read straight out of the page over the Chrome DevTools
Protocol and compared with the target. A sentence only counts if Bagan really
produced it.

CDP rather than the accessibility tree or a beacon, because:
  * uiautomator cannot see the app window while an IME is showing
  * Chrome throttles page timers while the keyboard covers the page, so a
    self-reporting page silently stops reporting
"""
import subprocess, json, time, re, sys, random, os
from playwright.sync_api import sync_playwright

ADB = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
CORPUS = "/tmp/mypos/corpus-ver-3.0/corpus/mypos-ver.3.0.shuf.txt"
FIELD_XY = (540, 330)
KB_ICON = (912, 2335)
ZWSP = "​"


def tap(x, y, s=0.06):
    subprocess.run([ADB, "shell", "input", "tap", str(x), str(y)], capture_output=True)
    time.sleep(s)


def hold(x, y, ms=620):
    subprocess.run([ADB, "shell", "input", "swipe", str(x), str(y), str(x), str(y),
                    str(ms)], capture_output=True)
    time.sleep(0.12)


def load_sentences(keymap, n, maxlen=8):
    out = []
    for line in open(CORPUS, encoding="utf8"):
        toks = [t.rsplit("/", 1)[0] for t in line.split() if "/" in t]
        toks = [t for t in toks if t and not re.fullmatch(r"[၀-၉0-9။၊.,!?]+", t)]
        if not (3 <= len(toks) <= maxlen):
            continue
        if all(ch in keymap for w in toks for ch in w):
            out.append(toks)
        if len(out) >= n * 15:
            break
    random.Random(11).shuffle(out)
    return out[:n]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    km = {k: tuple(v) for k, v in json.load(open("bagan_keymap.json"))["keymap"].items()}
    base = sum(1 for v in km.values() if v[2] == 1)
    print(f"keymap: {len(km)} glyphs ({base} base / {len(km)-base} long-press)")

    sents = load_sentences(km, n)
    print(f"{len(sents)} typable held-out sentences\n")

    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pg = [x for x in br.contexts[0].pages if "probe.html" in x.url][-1]
        read = lambda: pg.evaluate("document.getElementById('t').value")
        def reset():
            # scoped: the page already declares a const named t
            pg.evaluate("(()=>{const e=document.getElementById('t');"
                        "e.value='';e.focus();})()")

        tap(*FIELD_XY, s=1.5)
        reset()
        # prove the grid is live before trusting anything
        probe = km.get("သ") or list(km.values())[0]
        tap(probe[0], probe[1], s=0.8)
        if not read():
            tap(*KB_ICON, s=1.0)
            tap(*FIELD_XY, s=1.5)
            reset(); tap(probe[0], probe[1], s=0.8)
            if not read():
                print("FATAL: Bagan's letter grid is not accepting taps")
                return
        reset()
        print("grid live\n")

        rows, tot_tap = [], 0
        t0 = time.time()
        for i, toks in enumerate(sents, 1):
            reset()
            time.sleep(0.25)
            taps = holds = 0
            for w in toks:
                for ch in w:
                    x, y, layer = km[ch]
                    if layer == 1:
                        tap(x, y)
                    else:
                        hold(x, y); holds += 1
                    taps += 1
            time.sleep(0.7)
            got = read() or ""
            target = "".join(toks)
            ok = got.replace(ZWSP, "") == target.replace(ZWSP, "")
            rows.append({"words": len(toks), "taps": taps, "holds": holds, "ok": ok})
            tot_tap += taps
            print(f"{i:>3}. {len(toks)}w {taps:>3} taps {'OK ' if ok else 'MISS'} "
                  f"{got.replace(ZWSP,'')[:24]!r}")
            if not ok:
                print(f"      wanted {target[:24]!r}")

        good = [r for r in rows if r["ok"]]
        gw = sum(r["words"] for r in good); gt = sum(r["taps"] for r in good)
        gh = sum(r["holds"] for r in good)
        aw = sum(r["words"] for r in rows); at = sum(r["taps"] for r in rows)
        print(f"\n{'='*62}\nMEASURED ON THE REAL BAGAN APP ({time.time()-t0:.0f}s)\n{'='*62}")
        print(f"  sentences            {len(rows)}  ({len(good)} verified exact)")
        print(f"  VERIFIED words       {gw}    taps {gt}")
        print(f"  VERIFIED taps/word   {gt/gw:.2f}" if gw else "  no verified rows")
        print(f"  long-press share     {100*gh/gt:.1f}% of taps" if gt else "")
        print(f"  (all rows incl. misses: {at/aw:.2f} taps/word over {aw} words)")
        print(f"\n  model's script entry : 5.18 taps/word (codepoints + 1 commit)")
        print(f"  BurmaKey simulated   : 2.45 taps/word (chat)")
        json.dump({"rows": rows, "verified_words": gw, "verified_taps": gt,
                   "verified_tpw": (gt/gw if gw else None),
                   "hold_share": (gh/gt if gt else None)},
                  open("bagan_measured.json", "w"))
        br.close()


if __name__ == "__main__":
    main()
