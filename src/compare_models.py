"""Run the same Burmese-generation prompt across several DeepInfra models so the
outputs can be compared side by side. Key is read from a gitignored file.

Setup (in the Claude Code prompt, so the key never appears in chat/git):
    ! printf '%s' 'YOUR_DEEPINFRA_KEY' > /Users/huudat/Desktop/codes/burmakey/src/.deepinfra_key
Then this script is run and the labeled outputs land in model_compare.txt.
"""
import os, json, urllib.request, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
key = os.environ.get("DEEPINFRA_API_KEY", "")
kf = os.path.join(HERE, ".deepinfra_key")
if not key and os.path.exists(kf):
    key = open(kf).read().strip()
if not key:
    sys.exit("No key. Write it to src/.deepinfra_key (see header).")

BASE = "https://api.deepinfra.com/v1/openai"

# edit this list freely — models that 404/err are skipped and noted
MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "meta-llama/Meta-Llama-3.1-405B-Instruct",
    "deepseek-ai/DeepSeek-V3",
    "google/gemma-2-27b-it",
    "microsoft/WizardLM-2-8x22B",
    "mistralai/Mistral-Small-24B-Instruct-2501",
]

PROMPT = ("Write 12 short, natural Burmese (Myanmar) sentences two friends might "
          "text each other about daily life — food, work, weekend plans, feelings. "
          "Output ONLY Burmese, one sentence per line. No numbering, no English, "
          "no romanization, no translation.")

def gen(model):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.8, "max_tokens": 900,
    }).encode()
    req = urllib.request.Request(BASE + "/chat/completions", body,
        {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def metrics(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    joined = "".join(lines)
    my = sum(1 for c in joined if 'က' <= c <= '႟')
    latin = sum(1 for c in joined if 'a' <= c.lower() <= 'z')
    total = max(1, sum(1 for c in joined if not c.isspace()))
    zawgyi = 'ေက' in text or '်က' in text  # rough heuristic
    uniq = len(set(lines)) / max(1, len(lines))
    return dict(lines=len(lines), burmese_pct=round(100*my/total),
                latin_pct=round(100*latin/total), uniq_pct=round(100*uniq))

out = open(os.path.join(HERE, "model_compare.txt"), "w", encoding="utf8")
summary = []
for m in MODELS:
    print("running", m, "...")
    try:
        txt = gen(m)
    except Exception as e:
        out.write(f"\n===== {m} =====\n[ERROR] {e}\n"); summary.append((m, "ERR")); continue
    mt = metrics(txt)
    summary.append((m, mt))
    out.write(f"\n===== {m} =====\n")
    out.write(f"[metrics] lines={mt['lines']} burmese%={mt['burmese_pct']} "
              f"latin%={mt['latin_pct']} unique%={mt['uniq_pct']}\n")
    out.write(txt.strip() + "\n")
out.close()
print("\n--- summary ---")
for m, s in summary:
    print(f"  {m:52s} {s}")
print("\nwrote model_compare.txt")
