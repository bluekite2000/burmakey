"""Add a guided exercise mode to the web keyboard.

Free typing alone cannot be scored: between-user variance is 11% of the median,
larger than the design differences, and the analytics record what was PRODUCED
but never what the user was TRYING to produce. So a copy task is unscoreable
today.

This adds a 20-minute session in three parts:

  copy    10 sentences drawn from the same held-out myPOS set the simulation
          scored, so measured taps/word can be compared directly with the
          simulated 2.45 — the one test that can validate or break the study.
          Prescribing the Burmese OUTPUT also reveals what Burglish a real
          person invents for it, which is the variant-normaliser data the
          project has never had.
  stress  the cases we are least sure of: long-press glyphs, a number,
          punctuation, an English word, and a name (to exercise OOV fallback).
  free    five minutes of natural chat — copy-typing is not composing, and
          this is the only route to a chat-register corpus.

Each item logs target, produced, taps, keys, candidate positions and elapsed
time, so accuracy and effort are both scoreable per item.
"""
import io, json

ITEMS = json.load(open("/Users/huudat/Desktop/codes/burmakey/src/exercise_items.json",
                       encoding="utf8"))

copy = [c["my"] for c in ITEMS["copy"]][:10]
hold = [c["my"] for c in ITEMS["hold"]][:2]

EX = ([{"k": "copy", "t": t} for t in copy] +
      [{"k": "stress", "t": t, "n": "ရှည်သောခလုတ် · long-press glyphs"} for t in hold] +
      [{"k": "stress", "t": "ဈေးက ၂၅၀၀ ကျပ်ပါ။",
        "n": "ဂဏန်းနှင့်ပုဒ်ကြီး · numbers and ။"},
       {"k": "stress", "t": "ok ကျေးဇူးတင်ပါတယ်",
        "n": "အင်္ဂလိပ်စာ ရောသုံး · mixed English"},
       {"k": "stress", "t": "မောင်မောင် ဘယ်မှာလဲ",
        "n": "နာမည် · a name, tests the unknown-word fallback"}] +
      [{"k": "free", "t": "", "n": "သူငယ်ချင်းကို စာတစ်စောင်ရေးပါ · "
        "write a friend a message, anything you like"}] * 3)

CSS_OLD = '''/* ---------- More pane ---------- */'''
CSS_NEW = '''/* ---------- exercise mode ---------- */
.exbar{flex:0 0 auto;background:var(--head);border-bottom:1px solid var(--ln);
padding:9px 12px 11px;display:flex;flex-direction:column;gap:6px}
.exhead{display:flex;align-items:center;gap:10px;font-size:11.5px;color:var(--dim)}
.exhead .grow{flex:1 1 auto}
.exhead button{background:none;border:0;color:var(--dim);font-size:15px;
padding:6px 10px;min-height:34px;border-radius:8px}
.extarget{font-size:20px;line-height:1.75;color:var(--ink);word-break:break-word}
.exnote{font-size:12px;color:#7fae9f}
.exbar progress{width:100%;height:4px;-webkit-appearance:none;appearance:none;border:0}
.exbar progress::-webkit-progress-bar{background:#1d282f;border-radius:3px}
.exbar progress::-webkit-progress-value{background:var(--acc);border-radius:3px}
.exdone{background:var(--head);border:1px solid var(--ln);border-radius:13px;
padding:14px;margin:8px 0;font-size:13.5px;line-height:1.7;color:var(--ink)}
.exdone b{color:var(--acc)}
.exstart{background:var(--head);border:1px solid var(--ln);border-radius:14px;
padding:14px;display:flex;flex-direction:column;gap:10px}
.exstart h2{font-size:14px;margin:0}
.exstart p{margin:0;font-size:12.5px;color:var(--dim);line-height:1.6}

/* ---------- More pane ---------- */'''

BODY_OLD = ''' <div class="thread" id="thread" aria-live="polite"></div>'''
BODY_NEW = ''' <div class="exbar" id="exbar" hidden>
  <div class="exhead">
   <span id="exnum">1 / 18</span>
   <span class="grow" id="exkind"></span>
   <button id="exskip" onclick="exSkip()" aria-label="ကျော် · skip">ကျော် ›</button>
   <button id="exquit" onclick="exQuit()" aria-label="ရပ် · stop">✕</button>
  </div>
  <progress id="exprog" max="18" value="0"></progress>
  <div class="extarget" id="extarget"></div>
  <div class="exnote" id="exnote"></div>
 </div>
 <div class="thread" id="thread" aria-live="polite"></div>'''

MORE_OLD = '''<div class="fb">
<h2>သင့်အမြင် · your feedback</h2>'''
MORE_NEW = '''<div class="exstart">
<h2>လေ့ကျင့်ခန်း · guided test <span style="color:var(--dim);font-weight:400">(~20 min)</span></h2>
<p>18 short tasks: copy 10 sentences, 5 tricky ones (numbers, punctuation,
English, a name), then write 3 messages of your own. This is what turns your
session into a number we can compare against the simulation — and it is the
only way we learn how <i>you</i> spell Burglish.</p>
<label><input type="checkbox" id="exok">လေ့ကျင့်ခန်းအတွင်း ရိုက်သည်များကို မှတ်တမ်းတင်မည် ·
record what I type <b>during the exercise only</b> — the sentences are given
to you, and the 3 free messages are yours to choose. Nothing else is recorded.</label>
<button class="pri" id="exgo" onclick="exStart()">စတင်မည် · start the test</button>
</div>

<div class="fb">
<h2>သင့်အမြင် · your feedback</h2>'''

JS_OLD = '''/* ---- tabs ---- */'''
JS_NEW = '''/* ================= guided exercise =================
   The analytics know what was produced but not what the user was TRYING to
   produce, so a copy task is unscoreable without this. Each item records the
   target alongside the result, making accuracy and effort comparable across
   users and against the simulation. */
const EX_ITEMS = __EXITEMS__;
const ex = {on:false, i:0, rows:[], t0:0, snap:null};

function exSnap(){
  return {keys:M.keys, commits:M.commits, top1:M.top1, bar:M.barPick,
          raw:M.raw, zero:M.zeroKey, extras:M.extras||0};
}
function exStart(){
  if(!$("exok").checked){
    $("exok").parentElement.style.color="#e88";
    setTimeout(()=>{$("exok").parentElement.style.color=""},1600);
    return;
  }
  ex.on=true; ex.i=0; ex.rows=[]; sent=[]; words=[]; prev=null;
  $("exbar").hidden=false;
  $("exprog").max=EX_ITEMS.length;
  toggleMore();                       // back to the keyboard
  exShow();
}
function exShow(){
  const it=EX_ITEMS[ex.i];
  $("exnum").textContent=(ex.i+1)+" / "+EX_ITEMS.length;
  $("exprog").value=ex.i;
  $("exkind").textContent={copy:"ကူးရိုက်ပါ · copy this",
    stress:"ကူးရိုက်ပါ · copy this", free:"သင့်စိတ်ကြိုက် · your own words"}[it.k];
  $("extarget").textContent=it.t||"—";
  $("exnote").textContent=it.n||"";
  ex.t0=Date.now(); ex.snap=exSnap();
  $("inp").focus({preventScroll:true});
}
function exRecord(produced){
  const it=EX_ITEMS[ex.i], a=ex.snap, b=exSnap();
  const taps=(b.keys-a.keys), commits=(b.commits-a.commits);
  ex.rows.push({i:ex.i, kind:it.k, target:it.t, produced:produced,
    match: it.k==="free" ? null : (produced.replace(/\\u200b/g,"")===it.t.replace(/\\u200b/g,"")),
    taps:taps, words:commits, tpw: commits? +(taps/commits).toFixed(2):null,
    top1:b.top1-a.top1, bar:b.bar-a.bar, raw:b.raw-a.raw,
    zero:b.zero-a.zero, extras:b.extras-a.extras,
    ms:Date.now()-ex.t0});
}
function exNext(produced){
  exRecord(produced||"");
  ex.i++;
  words=[]; prev=null;
  if(ex.i>=EX_ITEMS.length){ exFinish(); return; }
  drawMsg(); render(); exShow();
}
function exSkip(){ if(ex.on) exNext(msgText()); }
function exQuit(){
  ex.on=false; $("exbar").hidden=true;
  drawMsg(); render();
}
function exFinish(){
  ex.on=false; $("exbar").hidden=true;
  const scored=ex.rows.filter(r=>r.match!==null);
  const okN=scored.filter(r=>r.match).length;
  const tw=ex.rows.reduce((s,r)=>s+r.words,0);
  const tt=ex.rows.reduce((s,r)=>s+r.taps,0);
  const secs=Math.round(ex.rows.reduce((s,r)=>s+r.ms,0)/1000);
  const d=document.createElement("div"); d.className="exdone";
  d.innerHTML="<b>ကျေးဇူးတင်ပါတယ် · thank you!</b><br>"+
    ex.rows.length+" tasks · "+tw+" words · <b>"+(tw?(tt/tw).toFixed(2):"—")+
    "</b> taps/word · "+okN+"/"+scored.length+" copied exactly · "+secs+"s<br>"+
    "<span style='color:var(--dim)'>Now tap ⓘ and press <b>send feedback</b> so we get it. "+
    "Please add a comment about which words came out wrong.</span>";
  $("thread").appendChild(d);
  $("thread").scrollTop=$("thread").scrollHeight;
  M.exercise=ex.rows;                 // rides along with the next beacon
  beacon({event:"exercise"});
}
/* ---- tabs ---- */'''

SEND_OLD = '''function sendMsg(){
  const t=msgText();
  if(!t)return;'''
SEND_NEW = '''function sendMsg(){
  const t=msgText();
  if(ex.on){ if(!t && EX_ITEMS[ex.i].k!=="free") return; exNext(t); return; }
  if(!t)return;'''

SUM_OLD = ''' if(document.getElementById("donate").checked)s.donatedTyping=M.donated.slice(0,300);'''
SUM_NEW = ''' if(document.getElementById("donate").checked)s.donatedTyping=M.donated.slice(0,300);
 if(M.exercise)s.exercise=M.exercise;   // consented explicitly at exercise start'''


def patch(text, path):
    for old, new in [(CSS_OLD, CSS_NEW), (BODY_OLD, BODY_NEW), (MORE_OLD, MORE_NEW),
                     (JS_OLD, JS_NEW.replace("__EXITEMS__",
                                             json.dumps(EX, ensure_ascii=False))),
                     (SEND_OLD, SEND_NEW), (SUM_OLD, SUM_NEW)]:
        n = text.count(old)
        assert n == 1, "%s: %d matches for %r" % (path, n, old[:50])
        text = text.replace(old, new)
    return text


for path in ["web-my/index.html", "src/build_web_my.py"]:
    src = io.open(path, encoding="utf8").read()
    io.open(path, "w", encoding="utf8").write(patch(src, path))
    print("patched", path)
print(f"{len(EX)} exercise items embedded")
