"""Overnight Burmese corpus builder. Continues from corpus.txt, dedupes globally,
rotates the two strongest DeepInfra models, sweeps many topics for lexical breadth.
Stops at TARGET unique lines or MAX_HOURS, whichever first. Safe to Ctrl-C / kill;
corpus.txt is always a complete, usable file.
"""
import os, sys, json, time, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("DEEPINFRA_API_KEY", "")
if not KEY:
    kf = os.path.join(HERE, ".deepinfra_key")
    if os.path.exists(kf): KEY = open(kf).read().strip()
if not KEY: sys.exit("no key")
BASE = "https://api.deepinfra.com/v1/openai"
MODELS = ["deepseek-ai/DeepSeek-V3", "microsoft/WizardLM-2-8x22B"]

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
MAX_HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

TOPICS = [
 "greetings and small talk","family and home life","breakfast and street food",
 "restaurants and ordering","weather and the rainy season","office work and meetings",
 "school, exams and homework","university and classes","shopping at the market",
 "online shopping and prices","buses and taxis","driving and traffic jams",
 "trains and long-distance travel","being sick, clinics and medicine","exercise and the gym",
 "football and sports","phones, data and wifi","apps and social media",
 "money, saving and borrowing","banks and mobile payment","festivals and Thingyan",
 "weddings and ceremonies","monasteries and merit-making","love and relationships",
 "breakups and feelings","friendship and hanging out","jokes and teasing",
 "gossip and news","politics and current events","electricity and power cuts",
 "renting and landlords","cleaning and chores","cooking a curry","tea shops and coffee",
 "fruit and snacks","pets and animals","gardening and plants","kids and parenting",
 "grandparents and elders","village life and farming","city life in Yangon",
 "Mandalay and upcountry","beaches and holidays","photography and selfies",
 "music and concerts","movies and series","books and reading","gaming",
 "job hunting and interviews","salary and promotion","freelancing and side jobs",
 "starting a small business","fashion and clothes","haircuts and beauty",
 "weight, dieting and health","sleep and being tired","stress and mental health",
 "weekend plans","holidays and days off","directions and getting lost",
 "lost items and problems","complaints and bad service","apologising and making up",
 "congratulations and good news","invitations and RSVPs","asking for a favour",
 "borrowing and lending things","planning a trip","the internet being slow",
]

def gen(model, topic, n):
    body = json.dumps({"model": model, "temperature": 0.95, "max_tokens": 1200,
        "messages": [{"role":"user","content":
        f"Write {n} short, natural Burmese (Myanmar) sentences two friends might text "
        f"each other about: {topic}. Vary the wording. Output ONLY Burmese, one per "
        f"line. No numbering, no English, no romanization, no translation."}]}).encode()
    req = urllib.request.Request(BASE+"/chat/completions", body,
        {"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]

cf = os.path.join(HERE, "corpus.txt")
seen = set()
if os.path.exists(cf):
    for l in open(cf, encoding="utf8"):
        seen.add(l.strip())
out = open(cf, "a", encoding="utf8")
print(f"resuming from {len(seen)} unique lines; target {TARGET}, max {MAX_HOURS}h")
t0 = time.time(); mi = 0; round_no = 0
while len(seen) < TARGET and (time.time()-t0) < MAX_HOURS*3600:
    round_no += 1
    for topic in TOPICS:
        if len(seen) >= TARGET: break
        model = MODELS[mi % len(MODELS)]; mi += 1
        try:
            txt = gen(model, topic, 40)
        except Exception as e:
            print("  retry", type(e).__name__); time.sleep(2); continue
        added = 0
        for line in txt.splitlines():
            s = line.strip().lstrip("-•*0123456789.() ").strip()
            if len(s) < 4 or not re.search(r'[က-႟]', s): continue
            if re.search(r'[A-Za-z]{3,}', s): continue          # drop code-switched lines
            if s not in seen:
                seen.add(s); out.write(s+"\n"); added += 1
        out.flush()
        el = (time.time()-t0)/60
        print(f"r{round_no} {model.split('/')[-1][:12]:12s} {topic[:22]:22s} +{added} "
              f"-> {len(seen)} uniq ({el:.0f}m)")
print(f"done: {len(seen)} unique lines in {(time.time()-t0)/60:.0f} min")
