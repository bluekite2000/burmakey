"""Complete keymap probe for a Myanmar IME, over the Chrome DevTools Protocol.

Reads the field directly from the page (uiautomator can't see the app window
while an IME shows; the page's own timers get throttled under the keyboard),
so each probe is ~1.5s instead of ~19s.

Probes three ways per key position:
    tap          base layer
    long-press   second layer
    shift + tap  shifted layer
and separately walks the numeric/symbol page. That closes the 12% of corpus
glyphs the first pass left unmapped, which is what biased the sentence sample.

Usage: python3 map3.py [out.json] [--ime bagan|tt]
"""
import subprocess, time, json, sys, os
from playwright.sync_api import sync_playwright

ADB = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
FIELD_XY = (540, 330)

LAYOUTS = {
    "bagan": {
        "rows": {1: (1621, [54, 162, 270, 378, 485, 593, 701, 809, 916, 1024]),
                 2: (1762, [54, 162, 270, 378, 485, 593, 701, 809, 916, 1024]),
                 3: (1902, [106, 216, 324, 432, 539, 647, 755, 863, 971]),
                 4: (2045, [64, 181, 283, 385, 487, 589, 692, 794, 896, 1019])},
        "skip": {(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (4, 0), (4, 9)},
        "shift": (64, 2045),
        "sym": (485, 1621),
        "kb_icon": (912, 2335),
    },
}


def tap(x, y, s=0.05):
    subprocess.run([ADB, "shell", "input", "tap", str(x), str(y)], capture_output=True)
    time.sleep(s)


def hold(x, y, ms=620):
    subprocess.run([ADB, "shell", "input", "swipe", str(x), str(y), str(x), str(y),
                    str(ms)], capture_output=True)
    time.sleep(0.1)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "keymap_full.json"
    name = sys.argv[sys.argv.index("--ime") + 1] if "--ime" in sys.argv else "bagan"
    L = LAYOUTS[name]

    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pg = [x for x in br.contexts[0].pages if "probe.html" in x.url][-1]
        read = lambda: pg.evaluate("document.getElementById('t').value")
        reset = lambda: pg.evaluate(
            "(()=>{const e=document.getElementById('t');e.value='';e.focus();})()")

        tap(*FIELD_XY, s=1.5)
        reset()

        def probe(x, y, mode):
            for attempt in range(2):
                reset()
                time.sleep(0.12)
                if mode == "tap":
                    tap(x, y, 0.35)
                elif mode == "hold":
                    hold(x, y)
                    time.sleep(0.25)
                else:                       # shift + tap
                    tap(*L["shift"], 0.2)
                    tap(x, y, 0.35)
                v = read() or ""
                if v:
                    return v
                # nothing: check the grid is still alive, else recover
                reset(); tap(916, 1762, 0.35)
                if read():
                    reset()
                    return ""               # grid fine, key is genuinely dead
                tap(L["kb_icon"][0], L["kb_icon"][1], 0.8)
                tap(*FIELD_XY, s=1.2)
            return ""

        result = {}
        for mode in ("tap", "hold", "shift"):
            print(f"--- {mode} ---", flush=True)
            for row, (y, xs) in L["rows"].items():
                for col, x in enumerate(xs):
                    if (row, col) in L["skip"]:
                        continue
                    v = probe(x, y, mode)
                    result[f"{mode}:{row},{col}"] = v
                    if v:
                        print(f"  {mode} r{row}c{col} -> {v!r}", flush=True)

        # numeric / symbol page
        print("--- symbol page ---", flush=True)
        tap(L["sym"][0], L["sym"][1], 1.0)
        for row, (y, xs) in L["rows"].items():
            for col, x in enumerate(xs):
                if (row, col) in L["skip"]:
                    continue
                reset(); time.sleep(0.1)
                tap(x, y, 0.35)
                v = read() or ""
                result[f"sym:{row},{col}"] = v
                if v:
                    print(f"  sym r{row}c{col} -> {v!r}", flush=True)
        tap(L["kb_icon"][0], L["kb_icon"][1], 0.8)

        keymap = {}
        for key, v in result.items():
            if not v or len(v) > 2:
                continue
            mode, rc = key.split(":")
            r, c = map(int, rc.split(","))
            xy = (L["rows"][r][1][c], L["rows"][r][0])
            cost = {"tap": 1, "hold": 1, "shift": 2, "sym": 2}[mode]
            if v not in keymap or cost < keymap[v][2]:
                keymap[v] = (xy[0], xy[1], cost, mode)

        json.dump({"raw": result, "keymap": {k: list(v) for k, v in keymap.items()}},
                  open(out_path, "w"), ensure_ascii=False, indent=1)
        by = {}
        for v in keymap.values():
            by[v[3]] = by.get(v[3], 0) + 1
        print(f"\nmapped {len(keymap)} glyphs: {by}")
        print("wrote", out_path)
        br.close()


if __name__ == "__main__":
    main()
