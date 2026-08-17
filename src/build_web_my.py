data = open("weblex_my.txt").read()

html = r'''<!DOCTYPE html><html lang="my"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,interactive-widget=resizes-content">
<title>မြန်မာစာရိုက် — type Burmese with English letters</title><style>
:root{--bg:#0f1115;--pan:#171a21;--ln:#252a34;--ink:#e6e9ef;--dim:#8b93a3;
--acc:#6ea8fe;--good:#6fcf97;
--kb:0px;            /* height the OS keyboard covers (set by visualViewport) */
--composer-h:190px}  /* measured height of the fixed composer */
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 "Noto Sans Myanmar","Myanmar MN","Pyidaungsu",ui-sans-serif,system-ui,sans-serif;
min-height:100vh;min-height:100dvh;
overscroll-behavior-y:none;      /* no pull-to-refresh / rubber-band while typing */
touch-action:manipulation;       /* kills the 300ms double-tap-zoom delay */
-webkit-tap-highlight-color:transparent}
.app{width:100%;max-width:560px;margin:0 auto;display:flex;flex-direction:column;
min-height:100vh;min-height:100dvh}

/* ---- scrolling page content (everything except the composer) ---- */
.content{flex:1 1 auto;display:flex;flex-direction:column;gap:12px;
padding:16px max(14px,env(safe-area-inset-right)) 0 max(14px,env(safe-area-inset-left));
padding-bottom:calc(var(--composer-h) + var(--kb) + 20px)}

/* ---- composer: candidate bar + input + actions, pinned above the keyboard ---- */
.composer{position:fixed;left:0;right:0;bottom:0;z-index:20;
width:100%;max-width:560px;margin:0 auto;
background:rgba(15,17,21,.94);
-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
border-top:1px solid var(--ln);
padding:7px max(14px,env(safe-area-inset-right))
calc(7px + max(6px,env(safe-area-inset-bottom))) max(14px,env(safe-area-inset-left));
display:flex;flex-direction:column;gap:8px;
transform:translateY(calc(-1 * var(--kb)));
transition:transform .14s ease-out}
@media(prefers-reduced-motion:reduce){.composer{transition:none}}

h1{font-size:20px;margin:0}
.sub{color:var(--dim);font-size:13px;margin:0}
.msg{background:var(--pan);border:1px solid var(--ln);border-radius:14px;
min-height:110px;padding:12px 14px;font-size:20px;line-height:2;word-break:break-word;
-webkit-user-select:text;user-select:text}
.msg .rom{display:block;font-size:11px;color:#7ea7d8;
font-family:ui-monospace,Menlo,monospace;margin-top:6px;word-break:break-all}
.msg:empty::before{content:"သင့်စာသား ဒီမှာပေါ်မယ် · your message appears here";
color:#454d5c;font-size:14px}

/* ---- candidate bar: horizontal, momentum, never leaks its scroll to the page ---- */
.bar{display:flex;gap:7px;align-items:stretch;min-height:62px;padding:1px 0;
overflow-x:auto;overflow-y:hidden;
overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;
scroll-snap-type:x proximity;scrollbar-width:none}
.bar::-webkit-scrollbar{display:none}
.cd{flex:0 0 auto;background:var(--pan);border:1px solid var(--ln);
border-radius:12px;padding:6px 14px;text-align:center;cursor:pointer;
min-height:56px;min-width:62px;             /* comfortable thumb target */
display:flex;flex-direction:column;align-items:center;justify-content:center;
scroll-snap-align:start;touch-action:manipulation;
-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;
-webkit-tap-highlight-color:transparent;
transition:transform .07s ease-out,background .07s ease-out}
@media(prefers-reduced-motion:reduce){.cd{transition:none}}
.cd:active{background:var(--acc);border-color:var(--acc);transform:scale(.95)}
.cd:active .lo,.cd:active .rm{color:#08101c}
.cd:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
@media(hover:hover){.cd:hover{border-color:#39445a}}
.cd .lo{font-size:19px;display:block;line-height:1.6}
.cd .rm{font-size:10px;color:var(--dim);display:block;
font-family:ui-monospace,Menlo,monospace}
.cd.raw .lo{font-family:ui-monospace,Menlo,monospace;font-size:15px;color:var(--dim)}
.hint{color:#454d5c;font-size:13px;align-self:center;padding-left:4px}

input[type=text]{width:100%;background:var(--pan);border:1px solid var(--acc);
border-radius:12px;color:var(--acc);font:18px ui-monospace,Menlo,monospace;
padding:14px;min-height:54px;outline:none;-webkit-appearance:none;appearance:none}
input::placeholder{color:#3d4757;font-family:inherit}
.row{display:flex;gap:8px}
button{flex:1;background:var(--pan);border:1px solid var(--ln);color:var(--ink);
border-radius:11px;padding:12px 8px;font-size:14px;cursor:pointer;font-family:inherit;
min-height:48px;touch-action:manipulation;
-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent}
button:active{background:var(--ln)}
button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
button.pri{background:var(--acc);color:#08101c;border-color:var(--acc);font-weight:600}
.stats{font-size:11.5px;color:var(--dim);font-family:ui-monospace,Menlo,monospace}
.fb{background:var(--pan);border:1px solid var(--ln);border-radius:14px;
padding:13px 14px;display:flex;flex-direction:column;gap:9px}
.fb h2{font-size:14px;margin:0}
.fb textarea{background:#12151b;border:1px solid var(--ln);border-radius:9px;
color:var(--ink);font:16px inherit;padding:10px;min-height:56px;resize:vertical;
-webkit-appearance:none;appearance:none}
.fb .thumbs{display:flex;gap:8px;flex-wrap:wrap}
.fb .thumbs button{font-size:19px;flex:0 0 auto;padding:9px 20px;min-width:64px}
.fb .thumbs button.on{background:var(--acc);border-color:var(--acc)}
label{font-size:12.5px;color:var(--dim);display:flex;gap:9px;align-items:flex-start;
cursor:pointer;-webkit-user-select:none;user-select:none;line-height:1.5;
padding:4px 0;min-height:32px}
label input[type=checkbox]{width:20px;height:20px;flex:0 0 auto;margin:1px 0 0;
accent-color:var(--acc)}
.foot{color:var(--dim);font-size:12.5px;line-height:1.7;border-top:1px solid var(--ln);
padding-top:12px;padding-bottom:6px}
.foot b{color:var(--ink)}
a{color:var(--acc)}
</style></head><body>
<form name="analytics" netlify netlify-honeypot="bot-field" hidden>
  <input name="site"><input name="event"><textarea name="comment"></textarea>
  <textarea name="payload"></textarea><input name="bot-field">
</form><div class="app">
<div class="content" id="content">
<h1>မြန်မာစာရိုက် <span style="color:var(--dim);font-weight:400;font-size:14px">
type Burmese with English letters</span></h1>
<p class="sub">Burglish ရိုက်နေကျအတိုင်း ရိုက်ပါ — အသံထွက်အတိုင်း — မှန်တဲ့စာလုံးကို နှိပ်ပါ
· type Burglish the way it sounds, tap the right word, get real Burmese</p>

<div class="msg" id="msg"></div>
<div class="stats" id="stats"></div>
<label><input type="checkbox" id="showrom">show Burglish under words</label>

<div class="fb">
<h2>သင့်အမြင် · your feedback</h2>
<div class="thumbs">
 <button id="up" onclick="thumb(1)">👍</button>
 <button id="dn" onclick="thumb(-1)">👎</button>
 <span class="hint" style="align-self:center">အဆင်ပြေလား · does it work for you?</span>
</div>
<textarea id="cmt" placeholder="ဘယ်စာလုံးတွေ မှားလဲ · which words were wrong? tell us anything (optional)"></textarea>
<label><input type="checkbox" id="oovok">also share words the keyboard did NOT know
(only those exact words — never your full message)</label>
<label><input type="checkbox" id="donate">ကျွန်ုပ်ရိုက်သည်များကို လှူမည် · donate my typing
to improve the dictionary — shares what you typed and the words you chose, in
order. Off by default. Tap to preview exactly what would be sent.</label>
<div class="stats" id="donpre" style="display:none"></div>
<button class="pri" onclick="sendFeedback()" id="sendbtn">📨 ပို့မည် · send feedback</button>
</div>

<div class="foot">
<b>ဒါဘာလဲ · what is this?</b><br>
A keyboard idea for Burmese: type Burglish the way you already do in chat —
no tones, no new spelling, no Myanmar layout to learn — and it writes real
Burmese script (always clean Unicode, never Zawgyi-garbled). It learns your
words during the session. Unknown words are kept exactly as you typed them.<br><br>
<b>Privacy:</b> everything runs in your browser; your message text is never
sent. When you press "send feedback" (or automatically at session end, if
analytics is configured), we receive <i>numbers only</i> — taps per word, how
often the first suggestion was right — never the words themselves. Two
exceptions, both off by default and only if you tick them: unknown words, and
donated typing, shown to you first.<br><br>
<a href="https://github.com/bluekite2000/burmakey">open source &amp; study</a> ·
lexicon from <a href="https://github.com/ye-kyaw-thu/myG2P">myG2P</a> and
<a href="https://github.com/ye-kyaw-thu/myPOS">myPOS</a> (Ye Kyaw Thu et al.,
CC BY-NC-SA 4.0 — this tool is free and noncommercial)
</div>
</div>
<div class="composer" id="composer">
 <div class="bar" id="bar"><span class="hint">စရိုက်ပါ — try: nay kaung la</span></div>
 <input type="text" id="inp" autocomplete="off" autocorrect="off"
  autocapitalize="none" spellcheck="false" inputmode="text" enterkeyhint="next"
  placeholder="ဒီမှာရိုက်ပါ · type here (a-z)">
 <div class="row">
  <button onclick="undo()">↩ ပြန်ဖျက် · undo</button>
  <button onclick="clearAll()">✕ ရှင်း · clear</button>
  <button class="pri" onclick="copyMsg()" id="cpy">⧉ ကူးယူ · copy</button>
 </div>
</div>
</div>
<script>
/* ============ ANALYTICS CONFIG — set ONE and redeploy ============ */
const ANALYTICS = {
  endpoint: "netlify",   // "netlify" = built-in Netlify Forms; or a Formspree URL; or "" to disable
  mailto: "nguyenhdat@gmail.com",
  site: "burmese-keyboard-web-v1"
};
/* ================================================================= */
const RAW=`__DATA__`;
const KK=[],LO=[];
for(const line of RAW.split("\n")){
  const i=line.indexOf("|");
  if(i>0){KK.push(line.slice(0,i));LO.push(line.slice(i+1))}
}
const pref=new Map();
for(let i=0;i<KK.length;i++){
  const s=KK[i];
  for(let j=1;j<=s.length;j++){
    const p=s.slice(0,j);
    let a=pref.get(p);
    if(!a){a=[];pref.set(p,a)}
    if(a.length<50)a.push(i);
  }
}
const recency=new Map(),bigram=new Map();
let prev=null,words=[];
const M={site:ANALYTICS.site,start:Date.now(),keys:0,commits:0,top1:0,
 barPick:0,raw:0,zeroKey:0,undos:0,normed:0,thumb:0,oov:[],
 events:[],donated:[],lastT:0};
function metricsSummary(){
 const s={...M,oov:undefined,donated:undefined,
  secs:Math.round((Date.now()-M.start)/1000),
  keysPerWord:M.commits?+(M.keys/M.commits).toFixed(2):null,
  top1Rate:M.commits?+(M.top1/M.commits).toFixed(2):null,
  rawRate:M.commits?+(M.raw/M.commits).toFixed(2):null,
  ua:navigator.userAgent.slice(0,80),lang:navigator.language};
 s.events=M.events.slice(0,500);
 if(document.getElementById("oovok").checked)s.oovWords=M.oov.slice(0,50);
 if(document.getElementById("donate").checked)s.donatedTyping=M.donated.slice(0,300);
 return s;
}
function beacon(extra){
 if(!ANALYTICS.endpoint)return false;
 try{
  if(ANALYTICS.endpoint==="netlify"){
   const p=new URLSearchParams({"form-name":"analytics",site:ANALYTICS.site,
    event:(extra&&extra.event)||"session",comment:(extra&&extra.comment)||"",
    payload:JSON.stringify(metricsSummary())});
   if(navigator.sendBeacon)return navigator.sendBeacon("/",p);
   fetch("/",{method:"POST",body:p,keepalive:true});
   return true;
  }
  const body=JSON.stringify({...metricsSummary(),...extra});
  if(navigator.sendBeacon)
    return navigator.sendBeacon(ANALYTICS.endpoint,new Blob([body],{type:"application/json"}));
  fetch(ANALYTICS.endpoint,{method:"POST",mode:"no-cors",
    headers:{"Content-Type":"application/json"},body,keepalive:true});
  return true;
 }catch(e){return false}
}
addEventListener("visibilitychange",()=>{
 if(document.visibilityState==="hidden"&&M.commits>0)beacon({event:"session"});
});
function thumb(v){M.thumb=v;
 document.getElementById("up").classList.toggle("on",v===1);
 document.getElementById("dn").classList.toggle("on",v===-1);}
function sendFeedback(){
 const cmt=document.getElementById("cmt").value.slice(0,2000);
 const ok=beacon({event:"feedback",comment:cmt});
 if(!ok){
  const body="Burmese keyboard feedback\n\n"+(cmt?("Comment: "+cmt+"\n\n"):"")+
   "Metrics: "+JSON.stringify(metricsSummary(),null,1);
  location.href="mailto:"+ANALYTICS.mailto+
   "?subject=Burmese%20keyboard%20feedback&body="+encodeURIComponent(body);
 }
 const b=document.getElementById("sendbtn");
 b.textContent="✓ ကျေးဇူးပါ · thank you!";
 setTimeout(()=>b.textContent="📨 ပို့မည် · send feedback",1800);
}
function drawStats(){
 const el=document.getElementById("stats");
 if(!M.commits){el.textContent="";return}
 el.textContent=`session: ${M.commits} words · `+
  `${(M.keys/M.commits).toFixed(1)} keys/word · `+
  `first suggestion right ${Math.round(100*M.top1/M.commits)}% · unknown ${M.raw}`;
}
const $=id=>document.getElementById(id);
function score(i){
  let s=1/(i+2);
  s+=10*(recency.get(i)||0);
  if(prev!==null){const bg=bigram.get(prev);if(bg)s+=100*(bg.get(i)||0)}
  return s;
}
function normBase(t){
  t=t.replace(/ph/g,"hp");
  t=t.replace(/ay/g,"ei").replace(/ai/g,"ei");
  t=t.replace(/ung\b/g,"un").replace(/aung/g,"aun");
  t=t.replace(/ee/g,"i").replace(/oo/g,"u");
  t=t.replace(/aw/g,"o");
  return t;
}
function norms(t){
  // Burglish 'y' covers TWO script medials: myG2P writes \u1000\u103b as 'ky'
  // but \u1015\u103c as 'pj'. Try both readings rather than guessing.
  const a=normBase(t);
  const b=a.replace(/([kpmbhtnsgl])y(?=[aeiou])/g,"$1j").replace(/ny/g,"nj");
  return a===b?[t,a]:[t,a,b];
}
function candidates(txt){
  let ids;
  if(!txt){
    ids=new Set();
    if(prev!==null){const bg=bigram.get(prev);if(bg)for(const i of bg.keys())ids.add(i)}
    for(const i of recency.keys())ids.add(i);
    ids=[...ids];
  }else{
    const vs=norms(txt);
    ids=[];
    for(const v of vs) ids.push(...(pref.get(v)||[]));
    for(const i of recency.keys())
      if(vs.some(v=>KK[i].startsWith(v)))ids.push(i);
    ids=[...new Set(ids)];
  }
  return ids.sort((a,b)=>score(b)-score(a)).slice(0,5);
}
function render(){
  const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
  const bar=$("bar");bar.innerHTML="";
  const cs=candidates(txt);
  if(!txt&&!cs.length){
    bar.innerHTML='<span class="hint">စရိုက်ပါ — try: nay kaung la</span>';return}
  cs.forEach((i,pos)=>{
    const d=document.createElement("div");d.className="cd";
    d.innerHTML='<span class="lo">'+LO[i]+'</span><span class="rm">'+KK[i]+'</span>';
    chip(d,()=>commit(i,null,pos,txt.length===0),LO[i]+" — "+KK[i]);
    bar.appendChild(d);
  });
  if(txt){
    const d=document.createElement("div");d.className="cd raw";
    d.innerHTML='<span class="lo">'+txt+'</span><span class="rm">ရိုက်သည့်အတိုင်း · as typed</span>';
    chip(d,()=>commit(null,txt,-1,false),txt+" — as typed");
    bar.appendChild(d);
  }
  bar.scrollLeft=0;
}
/* A candidate behaves like a native suggestion strip: tapping it must never
   dismiss or flicker the OS keyboard, and it must be reachable by keyboard. */
function chip(d,act,label){
  d.setAttribute("role","button");d.tabIndex=0;d.setAttribute("aria-label",label);
  /* Only mouse needs blur suppression — a tap on a non-focusable div does not
     move focus, so touch is left alone and slide-off-to-cancel still works. */
  d.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse")e.preventDefault()});
  d.addEventListener("click",act);
  d.addEventListener("keydown",e=>{
    if(e.key==="Enter"||e.key===" "){e.preventDefault();act()}
  });
}
function commit(i,raw,pos,zeroKey){
  const t0=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
  const now=Date.now(),dt=M.lastT?Math.min(now-M.lastT,60000):0;M.lastT=now;
  M.commits++;M.keys+=t0.length+1;
  if(zeroKey)M.zeroKey++;
  const nrm=(i!==null&&t0&&!KK[i].startsWith(t0))?1:0;
  if(M.events.length<500)M.events.push([t0.length,i!==null?pos:-1,zeroKey?1:0,nrm,i===null?1:0,dt]);
  if(M.donated.length<300)M.donated.push([t0,i!==null?LO[i]:raw]);
  if(i!==null){
    if(pos===0)M.top1++;else M.barPick++;
    if(nrm)M.normed++;
    words.push({my:LO[i],rom:KK[i],raw:false});
    recency.set(i,(recency.get(i)||0)+1);
    if(prev!==null){
      let bg=bigram.get(prev);
      if(!bg){bg=new Map();bigram.set(prev,bg)}
      bg.set(i,(bg.get(i)||0)+1);
    }
    prev=i;
  }else{
    M.raw++;if(M.oov.length<200)M.oov.push(raw);
    words.push({my:raw,rom:"",raw:true});
    prev=null;
  }
  $("inp").value="";drawMsg();render();drawStats();$("inp").focus({preventScroll:true});
}
function drawMsg(){
  const m=$("msg");
  m.textContent=words.map(w=>w.my).join(words.some(w=>w.raw)?" ":"");
  if($("showrom").checked&&words.length){
    const r=document.createElement("span");r.className="rom";
    r.textContent=words.map(w=>w.rom||w.my).join(" ");
    m.appendChild(r);
  }
}
function undo(){if(words.length){M.undos++;words.pop();prev=null;drawMsg();render();drawStats()}}
function clearAll(){words=[];prev=null;drawMsg();render()}
function copyMsg(){
  const t=words.map(w=>w.my).join(words.some(w=>w.raw)?" ":"");
  navigator.clipboard.writeText(t).then(()=>{
    $("cpy").textContent="✓ ကူးပြီး · copied";
    setTimeout(()=>$("cpy").textContent="⧉ ကူးယူ · copy",1200);
  });
}
$("inp").addEventListener("input",render);
$("inp").addEventListener("keydown",e=>{
  if(e.key===" "||e.key==="Enter"){
    e.preventDefault();
    const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
    if(!txt)return;
    const cs=candidates(txt);
    if(cs.length&&norms(txt).some(v=>KK[cs[0]].startsWith(v)))
      commit(cs[0],null,0,false);
    else commit(null,txt,-1,false);
  }
});
$("showrom").addEventListener("change",drawMsg);
$("donate").addEventListener("change",()=>{
  const p=$("donpre");
  if($("donate").checked){
    p.style.display="block";
    p.textContent="will share ("+M.donated.length+" words): "+
      M.donated.map(d=>d[0]+"→"+d[1]).slice(0,40).join("  ")+
      (M.donated.length>40?" …":"");
  }else{p.style.display="none"}
});
/* ---- mobile: keep the composer sitting on top of the OS keyboard ----
   iOS Safari does not shrink the layout viewport when the keyboard opens, so a
   bottom-fixed bar would hide behind it. visualViewport gives the covered
   height; Android (interactive-widget=resizes-content) reports ~0 because the
   layout viewport already shrank, so the same formula works on both. */
(function(){
  const comp=document.getElementById("composer"),root=document.documentElement;
  const vv=window.visualViewport;
  function measure(){root.style.setProperty("--composer-h",comp.offsetHeight+"px")}
  function keyboard(){
    if(!vv)return;
    const covered=Math.max(0,window.innerHeight-(vv.height+vv.offsetTop));
    root.style.setProperty("--kb",covered+"px");
  }
  function sync(){measure();keyboard()}
  if(vv){vv.addEventListener("resize",sync);vv.addEventListener("scroll",keyboard)}
  addEventListener("orientationchange",()=>setTimeout(sync,260));
  addEventListener("resize",sync);
  if(window.ResizeObserver)new ResizeObserver(measure).observe(comp);
  sync();
})();
/* Action buttons must not steal focus from the input on desktop either. */
document.querySelectorAll(".row button").forEach(b=>
  b.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse")e.preventDefault()}));
render();
</script></body></html>'''
open("try-burmese.html","w").write(html.replace("__DATA__", data))
import os; print("wrote try-burmese.html", os.path.getsize("try-burmese.html"), "bytes")
