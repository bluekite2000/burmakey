"""Scale the next-word corpus with an LLM (DeepInfra / Qwen, OpenAI-compatible).

Generates casual Burmese conversation across many topics and appends one
sentence per line to corpus.txt. Then run build_nextword.py to rebuild the
bigram table. Set DEEPINFRA_API_KEY first:

    ! export DEEPINFRA_API_KEY=...        # in the Claude Code prompt
    python3 gen_corpus.py 400             # ~400 sentences per topic

NOTE ON QUALITY: Qwen's Burmese is imperfect. Spot-check corpus.txt, and treat
the resulting bigrams as a prior, not ground truth. A stronger model or a
properly-licensed Burmese corpus will give cleaner data.
"""
import os, sys, json, time, urllib.request

KEY   = os.environ.get("DEEPINFRA_API_KEY", "")
if not KEY:
    _kf = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".deepinfra_key")
    if os.path.exists(_kf): KEY = open(_kf).read().strip()
BASE  = os.environ.get("DEEPINFRA_BASE", "https://api.deepinfra.com/v1/openai")
MODEL = os.environ.get("DEEPINFRA_MODEL", "deepseek-ai/DeepSeek-V3")   # best Burmese in the bake-off; WizardLM-2-8x22B is a good 2nd source
PER   = int(sys.argv[1]) if len(sys.argv) > 1 else 200

TOPICS = [
    "greetings and small talk", "family and home", "food and eating out",
    "weather and seasons", "work and school", "shopping and prices",
    "travel and directions", "health and feeling unwell", "phone and internet",
    "weekend plans and hobbies", "sports and football", "money and banking",
    "festivals and holidays", "feelings and relationships", "news and current events",
    "technology and apps", "transport and traffic", "cooking recipes",
    "children and parenting", "jokes and casual chat",
]

def chat(prompt):
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             "You write natural, everyday Burmese (Myanmar) exactly as young people "
             "chat. Output ONLY Burmese sentences, one per line, no numbering, no "
             "translation, no romanization, no English."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9, "max_tokens": 1500,
    }).encode()
    req = urllib.request.Request(BASE + "/chat/completions", body,
        {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]

if not KEY:
    sys.exit("Set DEEPINFRA_API_KEY (see header). No key -> nothing to generate.")

out = open("corpus.txt", "a", encoding="utf8")
total = 0
for t in TOPICS:
    got = 0
    while got < PER:
        try:
            txt = chat(f"Write {min(40, PER-got)} short, natural Burmese sentences "
                       f"two people might text each other about: {t}.")
        except Exception as e:
            print("  retry:", e); time.sleep(3); continue
        for line in txt.splitlines():
            line = line.strip().lstrip("-•0123456789. ").strip()
            if any('က' <= c <= '႟' for c in line):
                out.write(line + "\n"); got += 1; total += 1
        out.flush()
        print(f"  {t}: {got}/{PER}")
print(f"appended ~{total} sentences to corpus.txt")
