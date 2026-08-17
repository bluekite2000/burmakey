"""
The §11.3 test: is standardised spelling actually FASTER to type than the
improvised kind, once prediction is behind it?

Measured as keystrokes-to-unique — how many characters you must type before
the prefix identifies exactly one word. No frequency data needed, so no
assumptions to argue with.
"""
import json, re, collections, statistics

lex = json.load(open("lexicon.json"))
AL_WORDS = {al: v[0][0] for al, v in lex.items()}

TONE_LETTERS = "rvqzc"

def to_karaoke(al):
    """Approximate what a karaoke Lao writer produces: no tone, no vowel
    length, zero-onset unwritten."""
    s = re.sub(f"[{TONE_LETTERS}](?=$|[^aeiou])", "", al)   # drop tone letters
    s = s.replace("uuea", "uea").replace("iia", "ia").replace("uua", "ua")
    for long_, short in [("aae","ae"),("eeu","eu"),("ooe","oe"),("ooa","o"),
                         ("aa","a"),("ii","i"),("ee","e"),("uu","u"),("oo","o")]:
        s = s.replace(long_, short)
    s = s.replace("x", "")            # zero onset unwritten in karaoke
    s = s.replace("oa", "o")
    return s


def prefix_stats(words):
    """For each word: how many chars until its prefix is unique?"""
    counts = collections.Counter()
    for w in words:
        for i in range(1, len(w) + 1):
            counts[w[:i]] += 1
    out, never = [], 0
    for w in words:
        k = None
        for i in range(1, len(w) + 1):
            if counts[w[:i]] == 1:
                k = i
                break
        if k is None:
            never += 1
            out.append(len(w))
        else:
            out.append(k)
    return out, never


al_list = sorted(AL_WORDS)
kk_map = collections.defaultdict(list)
for al in al_list:
    kk_map[to_karaoke(al)].append(al)
kk_list = sorted(kk_map)

al_k, al_never = prefix_stats(al_list)
kk_k, kk_never = prefix_stats(kk_list)

print("=" * 64)
print("KEYSTROKE SIMULATION")
print("=" * 64)
print(f"vocabulary                     : {len(al_list):,} words")
print()
print(f"{'':32}{'Aksoon Laatin':>16}{'karaoke Lao':>16}")
print(f"{'mean word length (chars)':32}{statistics.mean(map(len,al_list)):>16.2f}"
      f"{statistics.mean(map(len,kk_list)):>16.2f}")
print(f"{'mean keystrokes to unique':32}{statistics.mean(al_k):>16.2f}"
      f"{statistics.mean(kk_k):>16.2f}")
print(f"{'median keystrokes to unique':32}{statistics.median(al_k):>16.1f}"
      f"{statistics.median(kk_k):>16.1f}")
print(f"{'never unique (true collisions)':32}{al_never:>16,}{kk_never:>16,}")

print()
print("-" * 64)
print("Cost per word, end to end")
print("-" * 64)
al_cost = statistics.mean(al_k) + 1          # + 1 tap to accept the candidate
kk_cost = statistics.mean(map(len, kk_list)) # no prediction worth trusting
print(f"Aksoon Laatin + prediction : {statistics.mean(al_k):.2f} keys "
      f"+ 1 accept tap = {al_cost:.2f}")
print(f"karaoke Lao, typed out     : {kk_cost:.2f} keys")
print(f"difference                 : {kk_cost - al_cost:+.2f} keys per word "
      f"({100*(kk_cost-al_cost)/kk_cost:+.1f}%)")

print()
print("-" * 64)
print("Ambiguity: how many Lao words share one spelling")
print("-" * 64)
al_amb = sum(len(v) for v in lex.values() if len(v) > 1)
kk_collide = sum(len(v) for v in kk_map.values() if len(v) > 1)
print(f"Aksoon Laatin : {sum(1 for v in lex.values() if len(v)>1):,} ambiguous "
      f"spellings covering {al_amb:,} words "
      f"({100*al_amb/len(AL_WORDS):.1f}% of vocabulary)")
print(f"karaoke Lao   : {sum(1 for v in kk_map.values() if len(v)>1):,} ambiguous "
      f"spellings covering {kk_collide:,} words "
      f"({100*kk_collide/len(al_list):.1f}% of vocabulary)")

print()
print("worst karaoke collisions (one spelling, many different words):")
for kk, als in sorted(kk_map.items(), key=lambda kv: -len(kv[1]))[:6]:
    ws = [AL_WORDS[a] for a in als][:7]
    print(f"   {kk:<10} -> {len(als):>2} words: {' '.join(ws)}")
