"""
Head-to-head on a MOBILE keyboard, against the competitors people actually use.

Why re-run it: the earlier head-to-head counted *taps*, and treated every tap
as equal. On a phone they are not. A Myanmar script layout puts its overflow
glyphs behind a layer switch that costs an extra tap, and a candidate-bar pick
is one tap but adds a visual scan and a long reach. Counting taps hides both.

Layout geometry here is MEASURED, not guessed: Bagan Keyboard v14.62 was
installed on an Android 14 emulator and driven directly. Its Myanmar Unicode
layout is 10 columns x 4 letter rows — the same key width as a 26-key Latin
layout, not narrower as first assumed. That earlier guess handed BurmaKey a
Fitts advantage that does not exist.

The same session established the arm's central assumption: typing real
high-frequency word prefixes into Bagan produces NO word candidates, only the
composing string echoed back for adding to a user dictionary. "As actually
used" really is character-by-character entry.

So this run costs each system in SECONDS PER WORD on a modelled phone:

    per key tap        Fitts: MT = a + b*log2(D/W + 1), D from the real
                       key-to-key travel of the actual typed sequence,
                       W from the layout's real key size
    per layer switch   an extra Fitts move to the layer key, then to the glyph
    per candidate pick a Fitts move up to the strip + a visual scan that grows
                       with the candidate's position in the bar
    per error          p(error) rises as keys shrink; each costs notice +
                       backspace + retap

Engine parity is preserved from the earlier study: where a system has an
engine it is the IDENTICAL ranker (freq + 10*recency + 100*bigram, beam 50,
5-candidate bar, corpus-pretrained). Only the input code and the geometry
differ.

The per-action constants are literature-shaped assumptions, NOT measurements
of Myanmar users, so every headline is reported as a range over a sensitivity
sweep rather than as a point estimate. Run with --sweep for the full grid.

Usage:  python3 h2h_mobile.py [--sweep]
Reads the same myG2P/myPOS clones as burmese2.py (see README).
"""
import sys, json, math, collections, itertools

import burmese2 as B   # lexicon, corpus, TRAIN/TEST, engine — no report side effects

# =====================================================================
# 1. Phone geometry
# =====================================================================
# Portrait phone, points. 360 is a common Android/iPhone logical width.
SCREEN_W   = 360.0
KEY_H      = 44.0     # a keyboard row
STRIP_H    = 46.0     # the candidate bar above the top key row
ROW_GAP    = 0.0

QWERTY = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
QWERTY_OFFSET = [0.0, 0.5, 1.5]     # standard staggering, in key widths


class Layout:
    """Key positions in points, plus which glyphs need a layer switch."""

    def __init__(self, name, cols, base_chars, layer2_chars=()):
        self.name = name
        self.cols = cols
        self.key_w = SCREEN_W / cols
        self.pos = {}
        for i, ch in enumerate(base_chars):
            r, c = divmod(i, cols)
            self.pos[ch] = ((c + 0.5) * self.key_w, (r + 0.5) * (KEY_H + ROW_GAP))
        self.rows = (len(base_chars) + cols - 1) // cols
        self.layer2 = set(layer2_chars)
        # the layer key sits bottom-left, where shift lives on real layouts
        self.layer_key_pos = (0.5 * self.key_w, (self.rows - 0.5) * (KEY_H + ROW_GAP))
        # candidate strip sits directly above the top row
        self.strip_y = -STRIP_H / 2
        self.strip_slot_w = SCREEN_W / 5.0     # a 5-candidate bar

    def target_w(self):
        """Fitts target size: the smaller of the key's two dimensions."""
        return min(self.key_w, KEY_H)

    def key_pos(self, ch):
        return self.pos.get(ch)

    def strip_pos(self, j):
        return ((j + 0.5) * self.strip_slot_w, self.strip_y)


def latin_layout():
    lay = Layout.__new__(Layout)
    lay.name = "latin-26"
    lay.cols = 10
    lay.key_w = SCREEN_W / 10
    lay.pos = {}
    for r, row in enumerate(QWERTY):
        for c, ch in enumerate(row):
            x = (c + QWERTY_OFFSET[r] + 0.5) * lay.key_w
            lay.pos[ch] = (x, (r + 0.5) * (KEY_H + ROW_GAP))
    lay.rows = 4                       # 3 letter rows + the space/function row
    lay.layer2 = set()                 # a-z all live on the base layer
    lay.layer_key_pos = (0.5 * lay.key_w, (lay.rows - 0.5) * (KEY_H + ROW_GAP))
    lay.strip_y = -STRIP_H / 2
    lay.strip_slot_w = SCREEN_W / 5.0
    return lay


def script_layout(freq_chars, cols=10, base_rows=4, order="alphabetical"):
    """A Myanmar script layout: `cols` x `base_rows` of glyphs on the base
    layer, everything rarer behind a layer switch.

    cols=10 is MEASURED, not assumed: Bagan Keyboard v14.62 was installed on an
    Android 14 emulator and its Myanmar Unicode layout counted — 10 columns of
    letter keys over 4 rows, with secondary glyphs on long-press. An earlier
    guess of 11 made its keys narrower than the Latin layout's and handed us a
    Fitts advantage that does not exist; at 10 columns both layouts have the
    same key width.

    order="alphabetical" places the base glyphs in Unicode order, which is the
    traditional alphabet order that real Myanmar layouts (Myanmar3, Bagan)
    follow. order="frequency" instead puts the most frequent glyphs in the
    easiest positions — an idealised layout that no shipping keyboard uses,
    included as a best case FOR THE COMPETITOR.
    """
    n_base = cols * base_rows - 4          # minus enter/backspace/space/layer
    ranked = [ch for ch, _ in freq_chars]
    base = ranked[:n_base]
    rest = ranked[n_base:]
    if order == "alphabetical":
        base = sorted(base)
    return Layout("script-%d/%s" % (cols, order), cols, base, rest)


# =====================================================================
# 2. Cost model
# =====================================================================
class Costs:
    def __init__(self, fitts_a=0.10, fitts_b=0.14,
                 scan_base=0.15, scan_per_slot=0.08,
                 err_p_ref=0.02, err_ref_w=36.0, err_fix=0.55,
                 mispick=0.015):
        self.a, self.b = fitts_a, fitts_b
        self.scan_base, self.scan_per_slot = scan_base, scan_per_slot
        self.err_p_ref, self.err_ref_w, self.err_fix = err_p_ref, err_ref_w, err_fix
        self.mispick = mispick

    def move(self, d, w):
        """Fitts's law. d = travel distance, w = target size (points)."""
        return self.a + self.b * math.log2(d / w + 1.0)

    def err_rate(self, w):
        """Smaller keys are missed more often; quadratic in target size."""
        return min(0.25, self.err_p_ref * (self.err_ref_w / w) ** 2)


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def time_for_trace(trace, layout, costs):
    """Cost one word's action trace on a layout.

    trace = (code_string_typed, pick_slot_or_None)
      code_string_typed : the characters actually pressed before committing
      pick_slot         : candidate-bar position picked (0-based), or None if
                          the word was typed out and committed with space
    """
    code, slot = trace
    t = 0.0
    cur = layout.layer_key_pos          # thumb starts near the bottom row
    w = layout.target_w()
    err = costs.err_rate(w)

    for ch in code:
        p = layout.key_pos(ch)
        if p is None:                   # glyph lives on the second layer
            lk = layout.layer_key_pos
            t += costs.move(dist(cur, lk), w)      # reach the layer key
            cur = lk
            # after switching, the glyph sits somewhere on the overflow plane;
            # cost it as an average-length move across the keyboard
            p = (SCREEN_W / 2, (layout.rows / 2) * KEY_H)
        t += costs.move(dist(cur, p), w)
        t += err * (costs.err_fix + costs.move(dist(p, p) + layout.key_w, w))
        cur = p

    if slot is None:
        # committed with the space bar
        sp = (SCREEN_W / 2, (layout.rows - 0.5) * KEY_H)
        t += costs.move(dist(cur, sp), w)
    else:
        sp = layout.strip_pos(slot)
        t += costs.scan_base + costs.scan_per_slot * slot
        t += costs.move(dist(cur, sp), min(layout.strip_slot_w, STRIP_H))
        t += costs.mispick * (costs.err_fix + 0.3)   # occasional wrong pick + undo
    return t


# =====================================================================
# 3. Engine — identical ranker, parameterised by input code
# =====================================================================
def build_prefix_index(code_of):
    by_prefix = collections.defaultdict(list)
    for w, c in code_of.items():
        for i in range(1, len(c) + 1):
            by_prefix[c[:i]].append(w)
    for p in by_prefix:
        by_prefix[p] = sorted(by_prefix[p], key=lambda w: -B.FREQ[w])[:50]
    return by_prefix


def run_engine(sents, code_of, by_prefix, shortlist=5, pretrain=True):
    """Return one action trace per scored word. Same ranker as burmese2."""
    recency = collections.Counter()
    bigram = collections.defaultdict(collections.Counter)
    learned_pref = collections.defaultdict(set)
    if pretrain:
        for s in B.TRAIN:
            kept = [w for w in s if w in code_of]
            for a, b in zip(kept, kept[1:]):
                bigram[a][b] += 0.2
    traces = []
    for s in sents:
        prev = None
        for w in s:
            if w not in code_of:
                prev = None
                continue
            sp = code_of[w]

            def score(x, _prev=prev):
                v = B.FREQ[x] + 10 * recency[x]
                if _prev is not None:
                    v += 100 * bigram[_prev][x]
                return v

            found = slot = None
            for k in range(0, len(sp) + 1):
                pool = by_prefix[sp[:k]]
                lp = learned_pref.get(sp[:k])
                if lp:
                    pool = set(pool) | lp
                cs = sorted(pool, key=score, reverse=True)[:shortlist]
                if w in cs:
                    found, slot = k, cs.index(w)
                    break
            if found is None:
                traces.append((sp, None))          # typed in full, space-committed
            else:
                traces.append((sp[:found], slot))
            if w not in recency:
                learned_pref[""].add(w)
                for i in range(1, len(sp) + 1):
                    learned_pref[sp[:i]].add(w)
            recency[w] += 1
            if prev is not None:
                bigram[prev][w] += 1
            prev = w
    return traces


def run_no_engine(sents, code_of):
    """Character-by-character entry: every glyph typed, space to commit."""
    return [(code_of[w], None) for s in sents for w in s if w in code_of]


# =====================================================================
# 4. Streams and systems
# =====================================================================
def streams():
    chat = [s for s in B.TEST if len(s) <= 8][:800]
    essay = [s for s in B.TEST if len(s) >= 15][:200]
    return {"chat": chat, "essay": essay}


def main(sweep=False):
    script_code = {w: w for w in B.LEX}          # input code = the script itself
    burg_code = dict(B.LEX)                      # input code = toneless Burglish

    char_freq = collections.Counter()
    for s in B.TRAIN:
        for w in s:
            if w in B.LEX:
                char_freq.update(w)
    ranked = char_freq.most_common()

    lay_latin = latin_layout()
    lay_script_alpha = script_layout(ranked, order="alphabetical")
    lay_script_freq = script_layout(ranked, order="frequency")

    base_n = lay_script_alpha.cols * 4 - 4
    covered = sum(c for ch, c in ranked[:base_n])
    total = sum(c for _, c in ranked)
    print("script inventory: %d distinct glyphs; base layer holds %d, "
          "covering %.1f%% of real keystrokes"
          % (len(ranked), base_n, 100.0 * covered / total))
    print("latin key %.1fpt wide; script key %.1fpt wide\n"
          % (lay_latin.key_w, lay_script_alpha.key_w))

    idx_script = build_prefix_index(script_code)
    idx_burg = build_prefix_index(burg_code)

    st = streams()
    systems = {}
    for name, sents in st.items():
        systems[(name, "bagan_as_used")] = (
            run_no_engine(sents, script_code), lay_script_alpha)
        systems[(name, "bagan_ideal")] = (
            run_engine(sents, script_code, idx_script), lay_script_alpha)
        systems[(name, "bagan_ideal_optlayout")] = (
            run_engine(sents, script_code, idx_script), lay_script_freq)
        systems[(name, "burmakey")] = (
            run_engine(sents, burg_code, idx_burg), lay_latin)

    LABEL = {
        "bagan_as_used": "Bagan / TTKeyboard as actually used",
        "bagan_ideal": "Bagan + our engine (does not exist)",
        "bagan_ideal_optlayout": "Bagan + our engine + ideal key placement",
        "burmakey": "BurmaKey (Burglish in, script out)",
    }
    ORDER = ["bagan_as_used", "bagan_ideal", "bagan_ideal_optlayout", "burmakey"]

    base = Costs()
    results = {}
    print("=" * 74)
    print("SECONDS PER WORD on a modelled phone  (centre-of-range constants)")
    print("=" * 74)
    print("%-42s %8s %8s %8s" % ("", "chat", "essay", "chat wpm"))
    for sysname in ORDER:
        row = {}
        for stream in ("chat", "essay"):
            traces, lay = systems[(stream, sysname)]
            secs = sum(time_for_trace(t, lay, base) for t in traces) / len(traces)
            row[stream] = secs
            row[stream + "_taps"] = sum(len(t[0]) + 1 for t in traces) / len(traces)
        results[sysname] = row
        print("%-42s %8.3f %8.3f %8.1f"
              % (LABEL[sysname], row["chat"], row["essay"], 60.0 / row["chat"]))

    print("\ntaps/word for continuity with the earlier study:")
    for sysname in ORDER:
        print("  %-40s chat %.2f  essay %.2f"
              % (LABEL[sysname], results[sysname]["chat_taps"],
                 results[sysname]["essay_taps"]))

    bk, asis, ideal = (results["burmakey"], results["bagan_as_used"],
                       results["bagan_ideal"])
    print("\nBurmaKey vs Bagan as used : chat %+.1f%%  essay %+.1f%%"
          % (100 * (bk["chat"] - asis["chat"]) / asis["chat"],
             100 * (bk["essay"] - asis["essay"]) / asis["essay"]))
    print("BurmaKey vs Bagan + engine: chat %+.1f%%  essay %+.1f%%"
          % (100 * (bk["chat"] - ideal["chat"]) / ideal["chat"],
             100 * (bk["essay"] - ideal["essay"]) / ideal["essay"]))

    out = {"centre": results, "geometry": {
        "screen_w": SCREEN_W, "latin_key_w": lay_latin.key_w,
        "script_key_w": lay_script_alpha.key_w,
        "base_layer_keys": base_n,
        "base_layer_coverage": 100.0 * covered / total}}

    # ---------------- sensitivity sweep -------------------------------
    if sweep:
        print("\n" + "=" * 74)
        print("SENSITIVITY SWEEP — every constant across its plausible range")
        print("=" * 74)
        grid = dict(
            fitts_b=[0.10, 0.14, 0.18],
            scan_per_slot=[0.04, 0.08, 0.14],
            err_p_ref=[0.01, 0.02, 0.04],
            scan_base=[0.10, 0.15, 0.25],
        )
        keys = sorted(grid)
        span = collections.defaultdict(list)
        for combo in itertools.product(*(grid[k] for k in keys)):
            c = Costs(**dict(zip(keys, combo)))
            vals = {}
            for sysname in ORDER:
                for stream in ("chat", "essay"):
                    traces, lay = systems[(stream, sysname)]
                    vals[(sysname, stream)] = (
                        sum(time_for_trace(t, lay, c) for t in traces) / len(traces))
            for stream in ("chat", "essay"):
                span[("vs_as_used", stream)].append(
                    100 * (vals[("burmakey", stream)] - vals[("bagan_as_used", stream)])
                    / vals[("bagan_as_used", stream)])
                span[("vs_ideal", stream)].append(
                    100 * (vals[("burmakey", stream)] - vals[("bagan_ideal", stream)])
                    / vals[("bagan_ideal", stream)])
                span[("secs", stream, "burmakey")].append(vals[("burmakey", stream)])
                span[("secs", stream, "bagan_as_used")].append(
                    vals[("bagan_as_used", stream)])
        n = len(next(iter(span.values())))
        print("%d parameter combinations\n" % n)
        for k in sorted(span, key=str):
            v = span[k]
            print("  %-38s min %+8.2f  max %+8.2f" % (str(k), min(v), max(v)))
        out["sweep"] = {str(k): [min(v), max(v)] for k, v in span.items()}
        out["sweep_n"] = n

    json.dump(out, open("h2h_mobile_results.json", "w"), indent=1)
    print("\nwrote h2h_mobile_results.json")


if __name__ == "__main__":
    main(sweep="--sweep" in sys.argv)
