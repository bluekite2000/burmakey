data = open("weblex_my.txt").read()

html = r'''<!DOCTYPE html><html lang="my"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,interactive-widget=resizes-content">
<title>မြန်မာစာရိုက် — type Burmese with English letters</title><style>
:root{
--bg:#0b141a;          /* thread */
--head:#202c33;        /* chat header + compose bar */
--pill:#2a3942;        /* input pill */
--out:#005c4b;         /* outgoing bubble */
--in:#202c33;          /* incoming bubble */
--ink:#e9edef; --dim:#8696a0; --ln:#2f3b43;
--acc:#00a884;         /* send green */
--tick:#53bdeb;        /* read ticks */
--kb:0px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
/* the root is pinned: iOS Safari scrolls the document to reveal a focused
   input, and with a scrollable root that pushes the chat header and the top
   of the thread off screen */
html,body{position:fixed;top:0;left:0;right:0;bottom:0;
width:100%;height:100%;overflow:hidden;overscroll-behavior:none}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 "Noto Sans Myanmar","Myanmar MN","Pyidaungsu",ui-sans-serif,system-ui,sans-serif;
touch-action:manipulation;-webkit-tap-highlight-color:transparent}
/* --vh is visualViewport.height, which already excludes the keyboard and
   Safari's toolbars; the 100dvh fallback covers browsers without it */
.app{width:100%;max-width:560px;margin:0 auto;
height:100vh;height:100dvh;height:var(--vh,100dvh);
display:flex;flex-direction:column;background:var(--bg);
transition:height .14s ease-out}
@media(prefers-reduced-motion:reduce){.app{transition:none}}

/* ---------- chat header ---------- */
.topbar{flex:0 0 auto;display:flex;align-items:center;gap:11px;
background:var(--head);padding:8px 10px;
padding-top:calc(8px + env(safe-area-inset-top))}
.avatar{flex:0 0 auto;width:40px;height:40px;border-radius:50%;
background:linear-gradient(145deg,#0b8f74,#046b56);color:#e9edef;
display:flex;align-items:center;justify-content:center;font-size:19px}
.who{flex:1 1 auto;min-width:0}
.who b{display:block;font-size:16px;font-weight:600;line-height:1.3;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.who span{display:block;font-size:12.5px;color:var(--dim);line-height:1.3;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hicons{flex:0 0 auto;display:flex;gap:2px}
.hicons button{background:none;border:0;color:var(--ink);font-size:18px;
width:44px;height:44px;min-height:44px;padding:0;border-radius:50%;
display:flex;align-items:center;justify-content:center}
.hicons button:active{background:rgba(255,255,255,.08)}
.hicons button[aria-expanded=true]{color:var(--acc)}

.pane{flex:1 1 auto;min-height:0}
[hidden]{display:none!important}

/* ---------- thread ---------- */
#pane-type{display:flex;flex-direction:column}
.thread{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;
overscroll-behavior-y:contain;padding:12px 9px 6px;
display:flex;flex-direction:column;gap:5px;
/* newest message sits just above the compose bar, as in any chat app.
   margin-top:auto on the first child rather than justify-content:flex-end,
   which clips the top once the thread overflows. */
justify-content:flex-start;
/* the doodle wallpaper, as a repeating tint rather than an image */
background-color:var(--bg);
background-image:
 radial-gradient(circle at 18% 22%,rgba(255,255,255,.016) 0 8px,transparent 9px),
 radial-gradient(circle at 72% 58%,rgba(255,255,255,.012) 0 11px,transparent 12px),
 radial-gradient(circle at 44% 84%,rgba(255,255,255,.011) 0 6px,transparent 7px),
 radial-gradient(circle at 88% 12%,rgba(255,255,255,.010) 0 5px,transparent 6px);
background-size:150px 150px,190px 190px,120px 120px,95px 95px}
.thread>*:first-child{margin-top:auto}
.daypill{align-self:center;background:#1d282f;color:var(--dim);font-size:12px;
padding:5px 13px;border-radius:9px;margin:2px 0 8px;box-shadow:0 1px 1px rgba(0,0,0,.25)}
.empty{margin:auto;text-align:center;color:#5d6b73;font-size:14px;line-height:1.7;
padding:20px;max-width:300px}
.empty b{display:block;color:#7c8b93;font-size:15px;margin-bottom:5px}

.bub{position:relative;max-width:82%;padding:7px 10px 5px;border-radius:8px;
box-shadow:0 1px 1px rgba(0,0,0,.28);word-break:break-word;font-size:16.5px;
line-height:1.5}
.bub.out{align-self:flex-end;background:var(--out);border-top-right-radius:2px}
.bub .bt{display:block;font-size:19px;line-height:1.75}
.bub .rom{display:block;font-size:11.5px;color:#9fd8c8;
font-family:ui-monospace,Menlo,monospace;margin-top:3px;word-break:break-all}
.bub .meta{display:block;text-align:right;font-size:11px;color:#8fb9ad;
margin-top:1px;line-height:1.4}
.bub .ck{color:var(--tick);letter-spacing:-2px;margin-left:2px}
.bub.draft{background:#0c4b3f;border:1px dashed #1c7963;opacity:.97}
.bub.draft .meta{color:#7fae9f}
.bub.copied::after{content:"✓ ကူးပြီး · copied";position:absolute;right:0;
bottom:-19px;font-size:11px;color:var(--acc);white-space:nowrap}
@media(hover:hover){.bub.out{cursor:pointer}}

/* ---------- compose bar ---------- */
.composer{flex:0 0 auto;background:var(--head);
padding:7px 8px calc(6px + max(2px,env(safe-area-inset-bottom)))}
.composerow{display:flex;gap:7px;align-items:flex-end}
.pillwrap{flex:1 1 auto;min-width:0;display:flex;align-items:center;
background:var(--pill);border-radius:24px;padding:0 6px 0 4px}
.pillwrap .ico{flex:0 0 auto;background:none;border:0;color:var(--dim);
width:40px;height:44px;min-height:44px;padding:0;font-size:17px;border-radius:50%;
display:flex;align-items:center;justify-content:center}
.pillwrap .ico:active{background:rgba(255,255,255,.07)}
input[type=text]{flex:1 1 auto;min-width:0;width:100%;background:none;border:0;
color:var(--ink);font:17px ui-monospace,Menlo,monospace;
padding:12px 4px;min-height:46px;outline:none;-webkit-appearance:none;appearance:none}
input::placeholder{color:#7b8a93;font-family:inherit}
.send{flex:0 0 46px;width:46px;height:46px;min-height:46px;padding:0;border:0;
border-radius:50%;font-size:19px;background:var(--acc);color:#06231c;
display:flex;align-items:center;justify-content:center}
.send:active{background:#019476}
.send[disabled]{opacity:.45}

/* ---------- suggestion strip, tight against the keyboard ---------- */
.bar{display:flex;gap:6px;align-items:stretch;min-height:56px;
margin-top:7px;padding:1px 0 0;
overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;
-webkit-overflow-scrolling:touch;scroll-snap-type:x proximity;scrollbar-width:none}
.bar::-webkit-scrollbar{display:none}
.cd{flex:0 0 auto;background:var(--pill);border:1px solid transparent;
border-radius:18px;padding:5px 15px;text-align:center;cursor:pointer;
min-height:52px;min-width:60px;
display:flex;flex-direction:column;align-items:center;justify-content:center;
scroll-snap-align:start;touch-action:manipulation;
-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;
transition:transform .07s ease-out,background .07s ease-out}
@media(prefers-reduced-motion:reduce){.cd{transition:none}}
.cd:active{background:var(--acc);transform:scale(.95)}
.cd:active .lo,.cd:active .rm{color:#06231c}
.cd:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.cd .lo{font-size:18px;display:block;line-height:1.6}
.cd .rm{font-size:9.5px;color:var(--dim);display:block;
font-family:ui-monospace,Menlo,monospace}
.cd.raw .lo{font-family:ui-monospace,Menlo,monospace;font-size:14px;color:var(--dim)}
.hint{color:#5d6b73;font-size:13px;align-self:center;padding-left:8px}

/* ---------- More pane ---------- */
#pane-more{overflow-y:auto;-webkit-overflow-scrolling:touch;
overscroll-behavior-y:contain;display:flex;flex-direction:column;gap:12px;
padding:14px 14px calc(16px + env(safe-area-inset-bottom))}
button{background:var(--pill);border:1px solid var(--ln);color:var(--ink);
border-radius:11px;padding:10px 8px;font-size:14px;cursor:pointer;font-family:inherit;
min-height:44px;line-height:1.25;touch-action:manipulation;
-webkit-user-select:none;user-select:none}
button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
button[disabled]{opacity:.35;pointer-events:none}
button.pri{background:var(--acc);color:#06231c;border-color:var(--acc);font-weight:600}
.sub{color:var(--dim);font-size:13.5px;margin:0}
.stats{font-size:11.5px;color:var(--dim);font-family:ui-monospace,Menlo,monospace}
.fb{background:var(--head);border:1px solid var(--ln);border-radius:14px;
padding:13px 14px;display:flex;flex-direction:column;gap:9px}
.fb h2{font-size:14px;margin:0}
.fb textarea{background:#121d24;border:1px solid var(--ln);border-radius:9px;
color:var(--ink);font:16px inherit;padding:10px;min-height:56px;resize:vertical;
-webkit-appearance:none;appearance:none}
.fb .thumbs{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.fb .thumbs button{font-size:19px;flex:0 0 auto;padding:9px 20px;min-width:64px}
.fb .thumbs button.on{background:var(--acc);border-color:var(--acc)}
.fb .pri{width:100%}
label{font-size:12.5px;color:var(--dim);display:flex;gap:9px;align-items:flex-start;
cursor:pointer;-webkit-user-select:none;user-select:none;line-height:1.5;
padding:4px 0;min-height:32px}
label input[type=checkbox]{width:20px;height:20px;flex:0 0 auto;margin:1px 0 0;
accent-color:var(--acc)}
.foot{color:var(--dim);font-size:12.5px;line-height:1.7;border-top:1px solid var(--ln);
padding-top:12px}
.foot b{color:var(--ink)}
a{color:#53bdeb}
</style></head><body>
<form name="analytics" netlify netlify-honeypot="bot-field" hidden>
  <input name="site"><input name="event"><textarea name="comment"></textarea>
  <textarea name="payload"></textarea><input name="bot-field">
</form><div class="app">

<div class="topbar">
 <div class="avatar" aria-hidden="true">မ</div>
 <div class="who">
  <b>မြန်မာစာရိုက်</b>
  <span id="presence">Burglish ရိုက် · မြန်မာစာ ထွက်</span>
 </div>
 <div class="hicons">
  <button id="infobtn" aria-expanded="false" aria-controls="pane-more"
   aria-label="အချက်အလက် · about, privacy and feedback"
   onclick="toggleMore()">&#9432;</button>
 </div>
</div>

<section class="pane" id="pane-type">
 <div class="thread" id="thread" aria-live="polite"></div>
 <div class="composer">
  <div class="composerow">
   <div class="pillwrap">
    <button class="ico" id="undobtn" onclick="undo()"
     aria-label="ပြန်ဖျက် · undo last word" title="ပြန်ဖျက် · undo">↩</button>
    <input type="text" id="inp" autocomplete="off" autocorrect="off"
     autocapitalize="none" spellcheck="false" inputmode="text" enterkeyhint="send"
     placeholder="စာရိုက်ပါ · message">
    <button class="ico" id="clrbtn" onclick="clearAll()"
     aria-label="ရှင်း · clear the draft" title="ရှင်း · clear">✕</button>
   </div>
   <button class="send" id="sendmsg" onclick="sendMsg()"
    aria-label="ပို့မည် · send and copy">➤</button>
  </div>
  <div class="bar" id="bar"><span class="hint">စရိုက်ပါ — try: nay kaung la</span></div>
 </div>
</section>

<section class="pane" id="pane-more" hidden>
<p class="sub">Burglish ရိုက်နေကျအတိုင်း ရိုက်ပါ — အသံထွက်အတိုင်း — မှန်တဲ့စာလုံးကို နှိပ်ပါ
· type Burglish the way it sounds, tap the right word, get real Burmese</p>

<div class="stats" id="stats"></div>
<label><input type="checkbox" id="showrom">show Burglish under words</label>

<div class="fb">
<h2>သင့်အမြင် · your feedback</h2>
<div class="thumbs">
 <button id="up" onclick="thumb(1)">👍</button>
 <button id="dn" onclick="thumb(-1)">👎</button>
 <span class="hint">အဆင်ပြေလား · does it work for you?</span>
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
words during the session. Unknown words are kept exactly as you typed them.
Nothing is actually sent anywhere — "send" adds the message to this thread and
copies it to your clipboard.<br><br>
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
</section>

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
let sent=[];
function msgText(){return words.map(w=>w.my).join(words.some(w=>w.raw)?" ":"")}
function clockHM(){
  const d=new Date();let h=d.getHours();const m=String(d.getMinutes()).padStart(2,"0");
  const ap=h<12?"AM":"PM";h=h%12||12;return h+":"+m+" "+ap;
}
function bubble(text,rom,draft,time){
  const b=document.createElement("div");
  b.className="bub out"+(draft?" draft":"");
  const t=document.createElement("span");t.className="bt";t.textContent=text;
  b.appendChild(t);
  if(rom){const r=document.createElement("span");r.className="rom";
    r.textContent=rom;b.appendChild(r)}
  const m=document.createElement("span");m.className="meta";
  if(draft){m.textContent="ရေးဆွဲနေသည် · draft"}
  else{m.innerHTML=time+' <span class="ck">✓✓</span>'}
  b.appendChild(m);
  return b;
}
/* the thread IS the message display: sent bubbles plus the live draft */
function drawMsg(){
  const t=$("thread");t.innerHTML="";
  const showrom=$("showrom").checked;
  if(!sent.length&&!words.length){
    const e=document.createElement("div");e.className="empty";
    e.innerHTML="<b>သင့်စာသား ဒီမှာပေါ်မယ်</b>your message appears here — "+
      "type Burglish below, tap the word you meant";
    t.appendChild(e);
  }else{
    const d=document.createElement("div");d.className="daypill";
    d.textContent="ယနေ့ · today";t.appendChild(d);
  }
  sent.forEach(s=>{
    const b=bubble(s.text,showrom?s.rom:"",false,s.time);
    b.title="ကူးယူ · tap to copy";
    b.addEventListener("click",()=>{
      navigator.clipboard.writeText(s.text).then(()=>{
        b.classList.add("copied");setTimeout(()=>b.classList.remove("copied"),1300);
      });
    });
    t.appendChild(b);
  });
  if(words.length){
    t.appendChild(bubble(msgText(),
      showrom?words.map(w=>w.rom||w.my).join(" "):"",true,""));
  }
  t.scrollTop=t.scrollHeight;
  const empty=!words.length;
  ["undobtn","clrbtn","sendmsg"].forEach(id=>{const b=$(id);if(b)b.disabled=empty});
}
/* "send" commits the draft into the thread and copies it — nothing leaves
   the device; the thread is the demo's own chat */
function sendMsg(){
  const t=msgText();
  if(!t)return;
  sent.push({text:t,rom:words.map(w=>w.rom||w.my).join(" "),time:clockHM()});
  words=[];prev=null;
  navigator.clipboard.writeText(t).catch(()=>{});
  drawMsg();render();drawStats();
  $("inp").focus({preventScroll:true});
}
function undo(){if(words.length){M.undos++;words.pop();prev=null;drawMsg();render();drawStats()}}
function clearAll(){words=[];prev=null;drawMsg();render()}

$("inp").addEventListener("input",render);
$("inp").addEventListener("keydown",e=>{
  if(e.key===" "||e.key==="Enter"){
    e.preventDefault();
    const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
    if(!txt){if(e.key==="Enter")sendMsg();return}
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
/* ---- tabs ---- */
/* one header affordance, like a chat app: info opens the about pane and
   turns into a close button */
function toggleMore(){
  const more=$("pane-more"),open=more.hidden;
  more.hidden=!open;
  $("pane-type").hidden=open;
  const b=$("infobtn");
  b.setAttribute("aria-expanded",open);
  b.innerHTML=open?"&#10005;":"&#9432;";
  b.setAttribute("aria-label",open?"ပိတ်ရန် · back to typing"
                                 :"အချက်အလက် · about, privacy and feedback");
  if(!open)$("inp").focus({preventScroll:true});
}
/* ---- keep the app sized to what the OS keyboard leaves us ----
   iOS Safari does not shrink the layout viewport when the keyboard opens, so
   without this the bottom of the app hides behind it. visualViewport reports
   the covered height; on Android (interactive-widget=resizes-content) the
   layout viewport already shrank and this reads ~0, so one formula covers
   both. The app is a flex column of that height, so the message area — not
   the composer — absorbs the change. */
(function(){
  const root=document.documentElement,vv=window.visualViewport;
  function fit(){
    if(!vv)return;
    /* visualViewport.height already excludes the OS keyboard and Safari's
       toolbars, so the shell needs no arithmetic to stay fully visible. */
    root.style.setProperty("--vh",vv.height+"px");
    root.style.setProperty("--kb",
      Math.max(0,window.innerHeight-(vv.height+vv.offsetTop))+"px");
    /* iOS still scrolls the document to reveal the focused input even with a
       pinned root; undo it so the chat header cannot drift off the top. */
    if(window.scrollY||window.scrollX)window.scrollTo(0,0);
  }
  if(vv){vv.addEventListener("resize",fit);vv.addEventListener("scroll",fit)}
  addEventListener("orientationchange",()=>setTimeout(fit,260));
  addEventListener("resize",fit);
  addEventListener("scroll",()=>{if(window.scrollY)window.scrollTo(0,0)},{passive:true});
  $("inp").addEventListener("focus",()=>setTimeout(fit,80));
  fit();
})();
/* Action buttons must not steal focus from the input on desktop either. */
document.querySelectorAll(".composerow button").forEach(b=>
  b.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse")e.preventDefault()}));
drawMsg();
render();
</script></body></html>'''
open("try-burmese.html","w").write(html.replace("__DATA__", data))
import os; print("wrote try-burmese.html", os.path.getsize("try-burmese.html"), "bytes")
