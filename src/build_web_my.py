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
/* every tab is otherwise a dead end, and a tester who opened web-my/#test
   directly has no history to go back through */
.back{flex:0 0 auto;display:flex;align-items:center;justify-content:center;
width:44px;height:44px;margin-left:-10px;margin-right:-6px;
color:var(--ink);font-size:27px;
line-height:1;text-decoration:none;-webkit-tap-highlight-color:transparent}
.back:active{opacity:.55}
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

.hmenu{flex:0 0 auto;width:44px;height:44px;min-height:44px;padding:0;
background:none;border:0;color:var(--ink);font-size:21px;line-height:1;
border-radius:50%;margin-right:-8px;cursor:pointer}
.hmenu:active{background:rgba(255,255,255,.08)}
/* ---------- top-level tabs (removed; kept for the .pane rules below) ---------- */
.tabs{flex:0 0 auto;display:flex;background:var(--head);
border-bottom:1px solid var(--ln);padding:0 4px}
.tabs button{flex:1 1 0;background:none;border:0;color:var(--dim);
font:13px inherit;padding:9px 2px 8px;min-height:40px;cursor:pointer;
border-bottom:2px solid transparent;touch-action:manipulation;
-webkit-user-select:none;user-select:none;white-space:nowrap;
overflow:hidden;text-overflow:ellipsis}
.tabs button[aria-selected=true]{color:var(--acc);border-bottom-color:var(--acc);
font-weight:600}
.tabs button:focus-visible{outline:2px solid var(--acc);outline-offset:-2px}
/* typing gets the whole screen: the bar steps aside while the keyboard is up */
.app.kbup .tabs{display:none}
.pane{flex:1 1 auto;min-height:0}
[hidden]{display:none!important}

/* ---------- thread ---------- */
#pane-chat{display:flex;flex-direction:column}
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
/* incoming bubbles: the app talking to you, in the idiom it already speaks */
.bub.in{align-self:flex-start;background:var(--in);border-top-left-radius:2px;
max-width:88%}
.bub.in .bt{font-size:15px;line-height:1.6}
.bub.in .ask{display:inline-block;margin:6px 0 2px;font-size:19px;
line-height:1.8;color:#eafff6}
.bub.in .dim{color:#8fb9ad;font-size:13px}
.bub.in .act{display:flex;gap:8px;margin-top:9px;flex-wrap:wrap}
.bub.in .act button{flex:0 0 auto;background:var(--acc);color:#06231c;border:0;
border-radius:9px;padding:9px 14px;font:13px inherit;font-weight:600;
min-height:40px;cursor:pointer}
.bub.in .act button.ghost{background:transparent;color:var(--dim);
border:1px solid var(--ln);font-weight:400}
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
.cd.punc{background:transparent;border-color:var(--ln);min-width:52px}
.cd.punc .lo{font-size:20px}
.hint{color:#5d6b73;font-size:13px;align-self:center;padding-left:8px}

/* ---------- exercise mode ---------- */
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
.exerr{background:#3a1d1d;border:1px solid #7d3b3b;border-radius:10px;
padding:10px 12px;font-size:12.5px;color:#ffc9c9;line-height:1.55}
@keyframes exflash{0%,100%{box-shadow:0 0 0 0 rgba(255,120,120,0)}
  50%{box-shadow:0 0 0 6px rgba(255,120,120,.5)}}
#exok.flash{animation:exflash .6s ease-in-out 3;border-radius:4px}
@media(prefers-reduced-motion:reduce){#exok.flash{animation:none;
  outline:3px solid #ff8080;outline-offset:2px}}

/* ---------- More pane ---------- */
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
/* NOT flex: any <b> or <i> inside the label would become its own flex item,
   which broke the consent text into squeezed columns. Float the box instead
   and let the text flow normally. */
label{font-size:12.5px;color:var(--dim);display:block;position:relative;
cursor:pointer;-webkit-user-select:none;user-select:none;line-height:1.55;
padding:4px 0 4px 30px;min-height:32px}
label input[type=checkbox]{position:absolute;left:0;top:5px;
width:20px;height:20px;margin:0;accent-color:var(--acc)}
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
 <a class="back" href="../" aria-label="ပင်မစာမျက်နှာ · back to the home page"
  title="ပင်မစာမျက်နှာ · home">‹</a>
 <div class="avatar" aria-hidden="true">မ</div>
 <div class="who">
  <b>မြန်မာစာရိုက်</b>
  <span id="presence">Burglish ရိုက် · မြန်မာစာ ထွက်</span>
 </div>
 <button class="hmenu" id="menubtn" onclick="menu()"
  aria-label="ရွေးချယ်စရာများ · options">⋮</button>
</div>


<section class="pane" id="pane-chat">
 <div class="exbar" id="exbar" hidden>
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
 if(opt.oov)s.oovWords=M.oov.slice(0,50);
 if(opt.donate)s.donatedTyping=M.donated.slice(0,300);
 if(M.exercise)s.exercise=M.exercise;   // consented explicitly at exercise start
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
/* the thumbs are conversation buttons now; the old on-screen pair is gone */
function thumb(v){
 M.thumb=v;
 const up=document.getElementById("up"),dn=document.getElementById("dn");
 if(up)up.classList.toggle("on",v===1);
 if(dn)dn.classList.toggle("on",v===-1);
}
function sendFeedback(){
 /* answers come from the conversation now; the textarea is gone */
 const el=document.getElementById("cmt");
 const cmt=(el?el.value:
   (convo.answers||[]).map(a=>a.q+": "+a.a).join(" | ")).slice(0,2000);
 const ok=beacon({event:"feedback",comment:cmt});
 if(!ok){
  const body="Burmese keyboard feedback\n\n"+(cmt?("Comment: "+cmt+"\n\n"):"")+
   "Metrics: "+JSON.stringify(metricsSummary(),null,1);
  location.href="mailto:"+ANALYTICS.mailto+
   "?subject=Burmese%20keyboard%20feedback&body="+encodeURIComponent(body);
 }
 /* the manual send button lived in the removed tab; the app now confirms
    in the conversation instead */
 const b=document.getElementById("sendbtn");
 if(b){b.textContent="✓ ကျေးဇူးပါ · thank you!";
   setTimeout(()=>b.textContent="📨 ပို့မည် · send feedback",1800);}
}
function drawStats(){
 /* the header subtitle is where a chat app shows "last seen"; putting the
    session figures there costs no layout height and keeps them in view */
 const el=document.getElementById("presence");
 if(!M.commits){el.textContent="Burglish ရိုက် · မြန်မာစာ ထွက်";return}
 el.textContent=`${M.commits} words · ${(M.keys/M.commits).toFixed(1)} keys/word`+
  ` · 1st right ${Math.round(100*M.top1/M.commits)}%`+
  (M.raw?` · unknown ${M.raw}`:``);
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
function addChip(bar,big,small,act,cls){
  const d=document.createElement("div");d.className="cd"+(cls?" "+cls:"");
  const a=document.createElement("span");a.className="lo";a.textContent=big;
  const b=document.createElement("span");b.className="rm";b.textContent=small;
  d.appendChild(a);d.appendChild(b);
  chip(d,act,big+" — "+small);
  bar.appendChild(d);
  return d;
}
function render(){
  const rawv=$("inp").value.trim();
  const txt=rawv.toLowerCase().replace(/[^a-z]/g,"");
  const digits=rawv.replace(/[^0-9]/g,"");
  const marks=rawv.replace(/[a-z0-9\s]/gi,"");
  const bar=$("bar");bar.innerHTML="";

  /* a number: offer it in Burmese numerals and in Latin digits */
  if(digits&&!txt){
    addChip(bar,toMyNum(digits),"မြန်မာဂဏန်း · Burmese",
            ()=>insertRaw(toMyNum(digits),"num"));
    addChip(bar,digits,"ဂဏန်း · digits",()=>insertRaw(digits,"num"),"raw");
    bar.scrollLeft=0;return;
  }
  /* punctuation typed on its own: . and , have Burmese equivalents */
  if(marks&&!txt&&!digits){
    if(/[.]/.test(marks))addChip(bar,"။","ပုဒ်ကြီး · sentence",
                                 ()=>insertRaw("။","punct"));
    if(/[,]/.test(marks))addChip(bar,"၊","ပုဒ်ဖြတ် · clause",
                                 ()=>insertRaw("၊","punct"));
    addChip(bar,marks,"ရိုက်သည့်အတိုင်း · as typed",
            ()=>insertRaw(marks,"punct"),"raw");
    bar.scrollLeft=0;return;
  }

  const cs=candidates(txt);
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
  }else{
    /* nothing being typed: the two Burmese marks that no Latin keyboard has,
       always within reach */
    addChip(bar,"။","ပုဒ်ကြီး · sentence",()=>insertRaw("။","punct"),"punc");
    addChip(bar,"၊","ပုဒ်ဖြတ် · clause",()=>insertRaw("၊","punct"),"punc");
    if(!cs.length){
      const h=document.createElement("span");h.className="hint";
      h.textContent="စရိုက်ပါ — try: nay kaung la";
      bar.appendChild(h);
    }
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
/* ================= the thread =================
   One message list, both directions. The guided test and the feedback
   questions are conversation turns rather than a separate screen: the app
   asks, you answer by typing, the way you would with a person. */
let msgs=[];                 // {dir:"in"|"out", html|text, rom, time, acts}
const ZW=/​/g;
const bare=s=>(s||"").replace(ZW,"");

const MY_DIGITS="၀၁၂၃၄၅၆၇၈၉";
const toMyNum=s=>s.replace(/[0-9]/g,d=>MY_DIGITS[+d]);
function msgText(){
  let s="";
  for(let i=0;i<words.length;i++){
    const w=words[i];
    if(w.space){s+=" ";continue}
    if(i>0){
      const pv=words[i-1];
      if(!pv.space&&!w.punct&&(w.raw||pv.raw))s+=" ";
    }
    s+=w.my;
  }
  return s;
}
function insertRaw(text,kind){
  words.push({my:text,rom:"",raw:kind!=="punct",punct:kind==="punct",
              space:kind==="space"});
  M.extras=(M.extras||0)+1;
  prev=null;
  $("inp").value="";
  drawMsg();render();drawStats();
  $("inp").focus({preventScroll:true});
}
function clockHM(){
  const d=new Date();let h=d.getHours();const m=String(d.getMinutes()).padStart(2,"0");
  const ap=h<12?"AM":"PM";h=h%12||12;return h+":"+m+" "+ap;
}
function store(k,v){try{v===undefined?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}}
function stored(k){try{return localStorage.getItem(k)}catch(e){return null}}
const seenKey="burmakey.seen", fbKey="burmakey.asked";

/* the app speaks */
function say(html,acts){
  /* only the newest message keeps live buttons: a stale "skip" further up the
     thread would act on whatever question we have since moved to */
  msgs.forEach(m=>{if(m.acts)m.acts=null});
  msgs.push({dir:"in",html:html,acts:acts||null,time:clockHM()});
  drawMsg();
}
/* the person spoke */
function heard(text,rom){
  msgs.push({dir:"out",text:text,rom:rom,time:clockHM()});
}

function drawMsg(){
  const t=$("thread");t.innerHTML="";
  const showrom=opt.showrom;
  if(!msgs.length&&!words.length){
    const e=document.createElement("div");e.className="empty";
    e.innerHTML="<b>သင့်စာသား ဒီမှာပေါ်မယ်</b>your message appears here — "+
      "type Burglish below, tap the word you meant";
    t.appendChild(e);
  }else{
    const d=document.createElement("div");d.className="daypill";
    d.textContent="ယနေ့ · today";t.appendChild(d);
  }
  msgs.forEach(m=>{
    const b=document.createElement("div");
    b.className="bub "+(m.dir==="in"?"in":"out");
    const s=document.createElement("span");s.className="bt";
    if(m.dir==="in")s.innerHTML=m.html; else s.textContent=m.text;
    b.appendChild(s);
    if(m.dir==="out"&&showrom&&m.rom){
      const r=document.createElement("span");r.className="rom";
      r.textContent=m.rom;b.appendChild(r);
    }
    if(m.acts&&m.acts.length){
      const a=document.createElement("div");a.className="act";
      m.acts.forEach(x=>{
        const btn=document.createElement("button");
        btn.textContent=x.label;
        if(x.ghost)btn.className="ghost";
        btn.onclick=()=>{m.acts=null;drawMsg();x.act()};
        a.appendChild(btn);
      });
      b.appendChild(a);
    }
    if(m.dir==="out"){
      const meta=document.createElement("span");meta.className="meta";
      meta.innerHTML=m.time+' <span class="ck">✓✓</span>';b.appendChild(meta);
      b.title="ကူးယူ · tap to copy";
      b.addEventListener("click",()=>{
        navigator.clipboard.writeText(m.text).then(()=>{
          b.classList.add("copied");setTimeout(()=>b.classList.remove("copied"),1300);
        }).catch(()=>{});
      });
    }
    t.appendChild(b);
  });
  if(words.length){
    const b=document.createElement("div");b.className="bub out draft";
    const s=document.createElement("span");s.className="bt";s.textContent=msgText();
    b.appendChild(s);
    if(showrom){const r=document.createElement("span");r.className="rom";
      r.textContent=words.map(w=>w.rom||w.my).join(" ");b.appendChild(r)}
    const m=document.createElement("span");m.className="meta";
    m.textContent="ရေးဆွဲနေသည် · draft";b.appendChild(m);
    t.appendChild(b);
  }
  t.scrollTop=t.scrollHeight;
  const empty=!words.length;
  ["undobtn","clrbtn","sendmsg"].forEach(id=>{const b=$(id);if(b)b.disabled=empty});
}

function sendMsg(){
  const t=msgText();
  if(!t)return;
  heard(t,words.map(w=>w.rom||w.my).join(" "));
  words=[];prev=null;
  navigator.clipboard.writeText(t).catch(()=>{});
  drawMsg();render();drawStats();
  $("inp").focus({preventScroll:true});
  if(convo.mode)setTimeout(()=>convoHeard(t),430);   // let their bubble land first
}
function undo(){if(words.length){M.undos++;words.pop();prev=null;drawMsg();render();drawStats()}}
function clearAll(){words=[];prev=null;drawMsg();render()}

const EX_ITEMS = [{"k": "copy", "t": "ပြဿနာရှိပါသလား"}, {"k": "copy", "t": "ဘန်ကောက်မှာဘယ်အချိန်ရှိပြီလဲ"}, {"k": "copy", "t": "ဟုတ်ကဲ့ဒီမှာပါ"}, {"k": "copy", "t": "ရေခဲပြင်မှာချော်လဲပြီးဖင်ထိုင်လျက်ကျတယ်"}, {"k": "copy", "t": "နောက်ရထားတစ်စင်းရောဘယ်လိုလဲ"}, {"k": "copy", "t": "ဒါဘယ်လောက်ကျမလဲ"}, {"k": "copy", "t": "မဆိုးပါဘူးတဲ့"}, {"k": "copy", "t": "ဟုတ်ကဲ့ဒီမှာပါခင်ဗျာ"}, {"k": "copy", "t": "အဆောင်ပိုင်ရှင်အဒေါ်ကြီးကသဘောကောင်းလား"}, {"k": "copy", "t": "ဒီဟာကိုလိုချင်ပါတယ်"}, {"k": "stress", "t": "ခင်ဗျားဘာအားကစားကစားလဲ", "n": "ရှည်သောခလုတ် · long-press glyphs"}, {"k": "stress", "t": "ဘာဖြစ်လို့လဲ", "n": "ရှည်သောခလုတ် · long-press glyphs"}, {"k": "stress", "t": "ဈေးက ၂၅၀၀ ကျပ်ပါ။", "n": "ဂဏန်းနှင့်ပုဒ်ကြီး · numbers and ။"}, {"k": "stress", "t": "ok ကျေးဇူးတင်ပါတယ်", "n": "အင်္ဂလိပ်စာ ရောသုံး · mixed English"}, {"k": "stress", "t": "မောင်မောင် ဘယ်မှာလဲ", "n": "နာမည် · a name, tests the unknown-word fallback"}, {"k": "free", "t": "", "n": "သူငယ်ချင်းကို စာတစ်စောင်ရေးပါ · write a friend a message, anything you like"}, {"k": "free", "t": "", "n": "သူငယ်ချင်းကို စာတစ်စောင်ရေးပါ · write a friend a message, anything you like"}, {"k": "free", "t": "", "n": "သူငယ်ချင်းကို စာတစ်စောင်ရေးပါ · write a friend a message, anything you like"}];
$("inp").addEventListener("input",render);
$("inp").addEventListener("keydown",e=>{
  /* backspace on an empty box deletes the last committed word, which is what
     every native IME does and the only way to fix a mis-picked word without
     hunting for the undo icon */
  if((e.key==="Backspace"||e.key==="Delete")&&!$("inp").value){
    if(words.length){e.preventDefault();undo()}
    return;
  }
  /* a literal space, for mixed Burmese/English — Burmese words themselves
     run together, so a space is only ever wanted deliberately */
  if(e.key===" "&&!$("inp").value.trim()){
    e.preventDefault();
    if(words.length&&!words[words.length-1].space)insertRaw(" ","space");
    return;
  }
  if(e.key===" "||e.key==="Enter"){
    e.preventDefault();
    const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
    if(!txt){
      const rest=$("inp").value.trim();
      if(rest){insertRaw(rest,/^[0-9]+$/.test(rest)?"num":"punct");return}
      if(e.key==="Enter")sendMsg();
      return;
    }
    const cs=candidates(txt);
    if(cs.length&&norms(txt).some(v=>KK[cs[0]].startsWith(v)))
      commit(cs[0],null,0,false);
    else commit(null,txt,-1,false);
  }
});

/* ================= the conversation ================= */
const convo={mode:null,i:0,rows:[],answers:[],snap:null,t0:0};
function snap(){
  return {keys:M.keys,commits:M.commits,top1:M.top1,bar:M.barPick,
          raw:M.raw,zero:M.zeroKey,extras:M.extras||0};
}
function convoHeard(text){
  if(convo.mode==="test")testHeard(text);
  else if(convo.mode==="fb")fbHeard(text);
}

/* ---- the guided test, as a conversation ---- */
function askSharingThenTest(){
  /* answering starts the test straight away — the sharing answer is the
     consent it needed, and every task carries a way out */
  const after=()=>setTimeout(()=>{store(seenKey,"1");testStart()},900);
  say("<b>မျှဝေမှု · sharing</b><br>I send numbers only — taps per word, how "+
      "often the first suggestion was right. Never your words, unless you say "+
      "so:<br><span class='dim'>• words the keyboard did not know — those exact "+
      "words only<br>• the words you typed and chose, in order, to improve the "+
      "dictionary</span><br><br>Then I will walk you through 18 short tasks — "+
      "you can stop at any point.",[
    {label:"နှစ်ခုလုံး · both",act:()=>{opt.oov=true;opt.donate=true;
      say("ကျေးဇူးပါ · thank you.");after()}},
    {label:"မသိသောစာလုံးများသာ · unknown only",ghost:true,
      act:()=>{opt.oov=true;say("ရပါတယ် · noted.");after()}},
    {label:"ဂဏန်းများသာ · numbers only",ghost:true,
      act:()=>{say("ရပါတယ် · numbers only.");after()}}]);
}
function testOffer(){
  say("<b>လေ့ကျင့်ခန်း · a favour?</b><br>If you have 20 minutes, I can "+
      "walk you through <b>18 short tasks</b>. It turns your session into a "+
      "number we can check our simulation against, and it is the only way we "+
      "learn how <i>you</i> spell Burglish.<br><br><span class='dim'>I would "+
      "record what you type during the tasks — the sentences are mine, and the "+
      "3 free messages are yours to choose. Nothing else.</span>",
      [{label:"ရပါတယ် · yes, let's go",act:testStart},
       {label:"နောက်မှ · later",ghost:true,act:()=>{store(seenKey,"1");
          say("ရပါတယ် · no problem — just type whenever you like.")}}]);
}
function testStart(){
  store(seenKey,"1");
  convo.mode="test";convo.i=0;convo.rows=[];
  say("ကောင်းပြီ · great. I will give you one at a time.");
  setTimeout(askItem,700);
}
function askItem(){
  const it=EX_ITEMS[convo.i],n=EX_ITEMS.length;
  convo.snap=snap();convo.t0=Date.now();
  const head="<span class='dim'>"+(convo.i+1)+" / "+n+"</span><br>";
  const skip=[{label:"ကျော် · skip",ghost:true,act:()=>testHeard("",true)},
    {label:"ရပ်မယ် · stop",ghost:true,act:testStop}];
  if(it.k==="free")say(head+"သင့်စိတ်ကြိုက် · "+it.n,skip);
  else say(head+"ဒီစာကြောင်းကို ရိုက်ပါ · type this:<br><span class='ask'>"+
      it.t+"</span>"+(it.n?"<br><span class='dim'>"+it.n+"</span>":""),skip);
}
function testHeard(produced,skipped){
  const it=EX_ITEMS[convo.i],a=convo.snap,b=snap();
  const taps=b.keys-a.keys,commits=b.commits-a.commits;
  const match=it.k==="free"?null:(bare(produced)===bare(it.t));
  convo.rows.push({i:convo.i,kind:it.k,target:it.t,produced:produced,
    match:match,skipped:!!skipped,taps:taps,words:commits,
    tpw:commits?+(taps/commits).toFixed(2):null,
    top1:b.top1-a.top1,bar:b.bar-a.bar,raw:b.raw-a.raw,
    zero:b.zero-a.zero,extras:b.extras-a.extras,ms:Date.now()-convo.t0});
  if(!skipped){
    if(match===true)say("✓ <b>တိတိကျကျ · exact</b>");
    else if(match===false)say("≈ ကွာသွားပါတယ် · I asked for <span class='ask'>"+
      it.t+"</span> — never mind, carry on.");
    else say("👍 ကျေးဇူးပါ · thank you.");
  }
  convo.i++;
  if(convo.i>=EX_ITEMS.length)return testFinish();
  setTimeout(askItem,650);
}
function testStop(){
  convo.mode=null;
  if(convo.rows.length){M.exercise=convo.rows;beacon({event:"exercise"})}
  say("ရပါတယ် · stopped — thank you for the "+convo.rows.length+
      " you did. Type whatever you like now.");
}
function testFinish(){
  convo.mode=null;
  const scored=convo.rows.filter(r=>r.match!==null&&!r.skipped);
  const ok=scored.filter(r=>r.match).length;
  const tw=convo.rows.reduce((s,r)=>s+r.words,0);
  const tt=convo.rows.reduce((s,r)=>s+r.taps,0);
  say("<b>ပြီးပါပြီ · that's all of them — thank you.</b><br>"+
      convo.rows.length+" tasks · "+tw+" words · <b>"+(tw?(tt/tw).toFixed(2):"—")+
      "</b> taps per word · "+ok+"/"+scored.length+" copied exactly.<br>"+
      "<span class='dim'>Your results are already sent.</span>");
  M.exercise=convo.rows;
  beacon({event:"exercise"});
  setTimeout(fbStart,1100);
}

/* ---- the feedback questions, also a conversation ---- */
const FB_Q=[
 {k:"wrong",q:"နောက်ဆုံးမေးခွန်းလေးတွေ · a few last questions.<br>"+
   "<b>ဘယ်စာလုံးတွေ မှားထွက်လဲ · which words came out wrong?</b><br>"+
   "<span class='dim'>Type any you remember — using this keyboard, of course.</span>"},
 {k:"spell",q:"<b>ဘယ် Burglish စာလုံးပေါင်းက မသဘာဝကျဘူးလဲ · which spellings felt "+
   "unnatural to you?</b><br><span class='dim'>The way we expect you to spell "+
   "things may not match how you actually do.</span>"},
 {k:"use",q:"<b>ဒီကီးဘုတ်ကို သုံးမလား · would you use this?</b>",
   acts:[{label:"👍 သုံးမယ်",v:1},{label:"👎 မသုံးဘူး",v:-1}]},
];
function fbStart(){
  if(convo.mode)return;
  store(fbKey,"1");
  convo.mode="fb";convo.i=0;convo.answers=[];
  askQ();
}
function askQ(){
  const q=FB_Q[convo.i];
  const acts=(q.acts||[]).map(a=>({label:a.label,act:()=>{thumb(a.v);fbHeard(a.label,true)}}));
  acts.push({label:"ကျော် · skip",ghost:true,act:()=>fbHeard("",true)});
  say(q.q,acts);
}
function fbHeard(text,viaButton){
  convo.answers.push({q:FB_Q[convo.i].k,a:text});
  convo.i++;
  if(convo.i>=FB_Q.length)return fbFinish();
  setTimeout(askQ,viaButton?450:650);
}
function fbFinish(){
  convo.mode=null;
  M.answers=convo.answers;
  beacon({event:"feedback",comment:convo.answers.map(a=>a.q+": "+a.a).join(" | ")});
  say("<b>ကျေးဇူးအများကြီးတင်ပါတယ် · thank you, genuinely.</b><br>"+
      "That is exactly what we could not get any other way. "+
      "Keep typing as long as you like.");
}

/* ---- the 5-minute ask ---- */
function maybeAsk(){
  if(convo.mode||stored(fbKey))return;
  if(M.commits<15||(Date.now()-M.start)/60000<5)return;
  store(fbKey,"1");
  say("<b>ခဏလောက် · got a minute?</b><br>You have typed "+M.commits+
      " words. Could I ask two quick questions about how it went?",
      [{label:"ရပါတယ် · sure",act:fbStart},
       {label:"နောက်မှ · later",ghost:true,act:()=>say("ရပါတယ် · no problem.")}]);
}
setInterval(maybeAsk,20000);
/* ---- tabs ---- */
/* one header affordance, like a chat app: info opens the about pane and
   turns into a close button */
/* the chat is the only surface now; #test still deep-links into the task */
function routeHash(){
  if((location.hash||"").slice(1)==="test"&&!convo.mode&&!msgs.length)
    setTimeout(testStart,500);
}
addEventListener("hashchange",routeHash);

/* settings are state, not checkboxes — the consent question sets them */
const opt={showrom:false,oov:false,donate:false};

/* the header ⋮ does not open a screen: it makes the app say the menu */
function menu(){
  say("<b>ရွေးချယ်စရာများ · options</b>",[
    {label:"လေ့ကျင့်ခန်း · guided test",act:testOffer},
    {label:"မျှဝေမှု · sharing",ghost:true,act:askSharing},
    {label:"ခလုတ်များ · the keys",ghost:true,act:sayKeys},
    {label:"ကိုယ်ရေး · privacy",ghost:true,
     act:()=>say("ကိုယ်ရေးကိုယ်တာ အပြည့်အစုံ · the full privacy note is on the "+
       "<a href='../' style='color:#8ecdf7'>home page</a>.")}]);
}
function sayKeys(){
  say("<b>ခလုတ်များ · the keys</b><br>You use your phone's own keyboard — "+
      "there is no new layout to learn.<br><br>"+
      "<b>space</b> — takes the highlighted word<br>"+
      "<b>backspace</b> — deletes the last word once the box is empty<br>"+
      "<b>enter</b> — sends<br><b>123</b> — offers ၀-၉ or 0-9<br>"+
      "<b>. ,</b> — offers ။ and ၊, also always on the strip<br>"+
      "<b>space twice</b> — a real space, for mixing English in");
}
function askSharing(){
  say("<b>မျှဝေမှု · sharing</b><br>By default I only send numbers, never your "+
      "words. Two things you can add, if you want to:<br>"+
      "<span class='dim'>• words the keyboard did not know — those exact words "+
      "only<br>• the words you typed and chose, in order, to improve the "+
      "dictionary</span>",[
    {label:"နှစ်ခုလုံး · both",act:()=>{opt.oov=true;opt.donate=true;
      say("ကျေးဇူးပါ · thank you — that helps the dictionary most.")}},
    {label:"မသိသောစာလုံးများသာ · unknown words only",ghost:true,
      act:()=>{opt.oov=true;opt.donate=false;say("ရပါတယ် · noted.")}},
    {label:"ဂဏန်းများသာ · numbers only",ghost:true,
      act:()=>{opt.oov=false;opt.donate=false;
      say("ရပါတယ် · numbers only. Nothing you type leaves your phone.")}}]);
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
    const covered=Math.max(0,window.innerHeight-(vv.height+vv.offsetTop));
    root.style.setProperty("--kb",covered+"px");
    /* typing gets the whole screen: the tab bar steps aside while the OS
       keyboard is up and returns when it closes */
    document.querySelector(".app").classList.toggle("kbup",covered>60);
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
routeHash();
/* first visit: the app introduces itself and offers the test */
if(!stored(seenKey)&&location.hash.slice(1)!=="test")setTimeout(askSharingThenTest,650);
</script></body></html>'''
open("try-burmese.html","w").write(html.replace("__DATA__", data))
import os; print("wrote try-burmese.html", os.path.getsize("try-burmese.html"), "bytes")
