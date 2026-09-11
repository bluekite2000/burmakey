"""Corpus -> word-segmented bigrams -> next-word table (assets/nextword.txt).

Segments Burmese sentences into known lexicon words by longest-match, counts
word->next-word pairs, and emits the top successors per word in the format the
Android Engine.loadBigrams() reads:  head<TAB>next1 next2 ...

Corpus sources (any that exist): the vetted exercise phrases already in the
repo, plus corpus.txt if gen_corpus.py has produced one. No myG2P/myPOS.
"""
import json, re, glob, collections, os

# --- vocabulary from the bundled lexicon -------------------------------------
VOCAB = set()
for line in open('weblex_v4.txt', encoding='utf8'):
    if '|' in line:
        VOCAB.add(line.split('|', 1)[1].strip())
VOCAB.discard('')
MAXLEN = max(len(w) for w in VOCAB)

def segment(chunk):
    """Longest-match a run of Burmese into lexicon words; None = unknown break."""
    out, i, n = [], 0, len(chunk)
    while i < n:
        best = None
        for L in range(min(MAXLEN, n - i), 0, -1):
            if chunk[i:i+L] in VOCAB:
                best = chunk[i:i+L]; break
        if best:
            out.append(best); i += len(best)
        else:
            out.append(None); i += 1
    return out

# --- gather corpus sentences -------------------------------------------------
def burmese_strings(x):
    if isinstance(x, str):
        return [x] if re.search(r'[က-႟]', x) else []
    if isinstance(x, dict):
        return [s for v in x.values() for s in burmese_strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in burmese_strings(v)]
    return []

sentences = []
for f in ['exercise_pool.json', 'exercise_items.json']:
    if os.path.exists(f):
        sentences += burmese_strings(json.load(open(f)))
if os.path.exists('corpus.txt'):                      # from gen_corpus.py
    sentences += [l for l in open('corpus.txt', encoding='utf8') if re.search(r'[က-႟]', l)]
sentences = list(dict.fromkeys(sentences))            # dedupe, keep order
print(f"corpus: {len(sentences)} sentences")

# --- count word bigrams (reset on punctuation / unknown) ---------------------
bg = collections.defaultdict(collections.Counter)
SPLIT = re.compile(r'[။၊\s,.!?;]+')
pairs = 0
for s in sentences:
    for chunk in SPLIT.split(s):
        prev = None
        for w in segment(chunk):
            if w is not None and prev is not None:
                bg[prev][w] += 1; pairs += 1
            prev = w
print(f"{pairs} adjacent word pairs, {len(bg)} heads with successors")

# --- emit top-K successors per head -----------------------------------------
K = 6
lines = []
for head, cnt in bg.items():
    tops = [w for w, _ in cnt.most_common(K)]
    if tops:
        lines.append(head + "\t" + " ".join(tops))
lines.sort()
open('nextword.txt', 'w', encoding='utf8').write("\n".join(lines) + "\n")
kb = sum(len(l) for l in lines) / 1024
print(f"nextword.txt: {len(lines)} heads, {kb:.1f} KB")
for l in lines[:8]:
    print("  ", l)
