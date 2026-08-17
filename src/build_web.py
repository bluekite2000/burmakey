data = open("weblex.txt").read()

html = r'''<!DOCTYPE html><html lang="lo"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>ພິມລາວ — type Lao with English letters</title><style>
:root{--bg:#0f1115;--pan:#171a21;--ln:#252a34;--ink:#e6e9ef;--dim:#8b93a3;
--acc:#6ea8fe;--good:#6fcf97}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.5 "Phetsarath OT","Noto Sans Lao",ui-sans-serif,system-ui,sans-serif;
display:flex;justify-content:center;min-height:100vh}
.app{width:100%;max-width:560px;padding:18px 14px 40px;display:flex;
flex-direction:column;gap:12px}
h1{font-size:20px;margin:0;letter-spacing:-.01em}
.sub{color:var(--dim);font-size:13px;margin:0}
.msg{background:var(--pan);border:1px solid var(--ln);border-radius:14px;
min-height:110px;padding:12px 14px;font-size:22px;line-height:1.7;word-break:break-word}
.msg .rom{display:block;font-size:11px;color:#7ea7d8;
font-family:ui-monospace,Menlo,monospace;margin-top:6px;word-break:break-all}
.msg:empty::before{content:"ຂໍ້ຄວາມຂອງເຈົ້າຈະປາກົດຢູ່ນີ້ · your message appears here";
color:#454d5c;font-size:14px}
.bar{display:flex;gap:7px;overflow-x:auto;min-height:64px;padding:2px}
.cd{flex:0 0 auto;background:var(--pan);border:1px solid var(--ln);
border-radius:11px;padding:6px 13px;text-align:center;cursor:pointer;
-webkit-tap-highlight-color:transparent}
.cd:active{background:var(--acc)}
.cd .lo{font-size:21px;display:block;line-height:1.4}
.cd .rm{font-size:10px;color:var(--dim);display:block;
font-family:ui-monospace,Menlo,monospace}
.cd.raw .lo{font-family:ui-monospace,Menlo,monospace;font-size:16px;color:var(--dim)}
.hint{color:#454d5c;font-size:13px;align-self:center;padding-left:4px}
input[type=text]{width:100%;background:var(--pan);border:1px solid var(--acc);
border-radius:12px;color:var(--acc);font:18px ui-monospace,Menlo,monospace;
padding:13px 14px;outline:none}
input::placeholder{color:#3d4757;font-family:inherit}
.row{display:flex;gap:8px}
button{flex:1;background:var(--pan);border:1px solid var(--ln);color:var(--ink);
border-radius:11px;padding:11px;font-size:14px;cursor:pointer;font-family:inherit}
button:active{background:var(--ln)}
button.pri{background:var(--acc);color:#08101c;border-color:var(--acc);font-weight:600}
.stats{font-size:11.5px;color:var(--dim);font-family:ui-monospace,Menlo,monospace}
.fb{background:var(--pan);border:1px solid var(--ln);border-radius:14px;
padding:13px 14px;display:flex;flex-direction:column;gap:9px}
.fb h2{font-size:14px;margin:0}
.fb textarea{background:#12151b;border:1px solid var(--ln);border-radius:9px;
color:var(--ink);font:14px inherit;padding:9px;min-height:52px;resize:vertical}
.fb .thumbs{display:flex;gap:8px}
.fb .thumbs button{font-size:19px;flex:0 0 auto;padding:7px 18px}
.fb .thumbs button.on{background:var(--acc);border-color:var(--acc)}
label{font-size:12px;color:var(--dim);display:flex;gap:7px;align-items:flex-start;
cursor:pointer;user-select:none;line-height:1.45}
.foot{color:var(--dim);font-size:12.5px;line-height:1.6;border-top:1px solid var(--ln);
padding-top:12px}
.foot b{color:var(--ink)}
a{color:var(--acc)}
</style></head><body>
<form name="analytics" netlify netlify-honeypot="bot-field" hidden>
  <input name="site"><input name="event"><textarea name="comment"></textarea>
  <textarea name="payload"></textarea><input name="bot-field">
</form><div class="app">
<h1>ພິມລາວ <span style="color:var(--dim);font-weight:400;font-size:14px">
type Lao with English letters</span></h1>
<p class="sub">ພິມແບບຄາຣາໂອເກະ ຄືເຄີຍ — ແຕະຄຳທີ່ຖືກຕ້ອງ — ໄດ້ອັກສອນລາວແທ້
· type karaoke Lao as usual, tap the right word, get real Lao script</p>

<div class="msg" id="msg"></div>
<div class="bar" id="bar"><span class="hint">ພິມເພື່ອເລີ່ມ — try: sabai di bo</span></div>
<input type="text" id="inp" autocomplete="off" autocorrect="off"
 autocapitalize="none" spellcheck="false" placeholder="ພິມຢູ່ນີ້ · type here (a-z)">
<div class="row">
 <button onclick="undo()">↩ ລຶບຄຳ · undo</button>
 <button onclick="clearAll()">✕ ລ້າງ · clear</button>
 <button class="pri" onclick="copyMsg()" id="cpy">⧉ ກັອບປີ້ · copy</button>
</div>
<div class="stats" id="stats"></div>
<label><input type="checkbox" id="showrom">show tone spelling under words (aksoon laatin)</label>

<div class="fb">
<h2>ຄຳເຫັນຂອງເຈົ້າ · your feedback</h2>
<div class="thumbs">
 <button id="up" onclick="thumb(1)">👍</button>
 <button id="dn" onclick="thumb(-1)">👎</button>
 <span class="hint" style="align-self:center">ມັນໃຊ້ໄດ້ບໍ? · does it work for you?</span>
</div>
<textarea id="cmt" placeholder="ຄຳໃດຜິດ? ຂຽນບອກເຮົາ · which words were wrong? tell us anything (optional)"></textarea>
<label><input type="checkbox" id="oovok">also share the words the keyboard did NOT
know (only those exact words — never your full message)</label>
<label><input type="checkbox" id="donate">ບໍລິຈາກການພິມຂອງຂ້ອຍ · donate my typing to
improve the dictionary — shares what you typed and the words you chose, in
order. Off by default. Tap to preview exactly what would be sent.</label>
<div class="stats" id="donpre" style="display:none"></div>
<button class="pri" onclick="sendFeedback()" id="sendbtn">📨 ສົ່ງຄຳເຫັນ · send feedback</button>
</div>

<div class="foot">
<b>ນີ້ແມ່ນຫຍັງ? · what is this?</b><br>
A keyboard idea for Lao: type the way you already text — no tones, nothing new
to learn — and it writes real Lao script. It learns your words during the
session. Unknown words are kept exactly as you typed them.<br><br>
<b>Privacy:</b> your message text stays in your browser and is never sent.
When you press "send feedback" (or automatically at session end, if analytics
is configured), we receive <i>numbers only</i>: taps per word, how often the
first suggestion was right, per-word counts like keys-pressed and candidate
position — <i>never the words themselves</i>. Two exceptions, both off by
default and only if you tick them: unknown words, and (if you choose to
donate your typing) the words you typed and chose, shown to you first.<br><br>
<a href="https://github.com/CHANGEME/aksoon-laatin">source, white paper &amp; data</a> ·
built on <a href="https://github.com/wannaphong/laonlp">laonlp</a>
</div>
</div>
<script>
/* ============ ANALYTICS CONFIG — set ONE of these and redeploy ============
   endpoint: a Formspree form URL  ("https://formspree.io/f/XXXXXXXX")
             or any server of yours accepting JSON POST.
   Leave "" to disable automatic sending; the mailto button always works.  */
const ANALYTICS = {
  endpoint: "netlify",   // "netlify" = built-in Netlify Forms; or a Formspree URL; or "" to disable
  mailto: "nguyenhdat@gmail.com",
  site: "aksoon-laatin-web-v1"
};
/* ========================================================================= */

const RAW=`__DATA__`;
const KK=[],LO=[],RM=[];
for(const line of RAW.split("\n")){
  const [k,l,r]=line.split("|");
  if(k&&l){KK.push(k);LO.push(l);RM.push(r||"")}
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

/* ---------------- metrics: numbers only, never message text -------------- */
const M={site:ANALYTICS.site,start:Date.now(),keys:0,commits:0,top1:0,
 barPick:0,raw:0,zeroKey:0,undos:0,normed:0,thumb:0,oov:[],
 events:[],donated:[],lastT:0};
function metricsSummary(){
 const s={...M,oov:undefined,
  secs:Math.round((Date.now()-M.start)/1000),
  keysPerWord:M.commits?+(M.keys/M.commits).toFixed(2):null,
  top1Rate:M.commits?+(M.top1/M.commits).toFixed(2):null,
  rawRate:M.commits?+(M.raw/M.commits).toFixed(2):null,
  ua:navigator.userAgent.slice(0,80),lang:navigator.language};
 s.events=M.events.slice(0,500);          // level 2: per-word, content-free
 s.donated=undefined;
 if(document.getElementById("oovok").checked)s.oovWords=M.oov.slice(0,50);
 if(document.getElementById("donate").checked)
   s.donatedTyping=M.donated.slice(0,300);  // level 3: only with consent
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
  const body="Lao keyboard feedback\n\n"+
   (cmt?("Comment: "+cmt+"\n\n"):"")+
   "Metrics: "+JSON.stringify(metricsSummary(),null,1);
  location.href="mailto:"+ANALYTICS.mailto+
   "?subject=Lao%20keyboard%20feedback&body="+encodeURIComponent(body);
 }
 const b=document.getElementById("sendbtn");
 b.textContent="✓ ຂອບໃຈ! · thank you!";
 setTimeout(()=>b.textContent="📨 ສົ່ງຄຳເຫັນ · send feedback",1800);
}
function drawStats(){
 const el=document.getElementById("stats");
 if(!M.commits){el.textContent="";return}
 el.textContent=`session: ${M.commits} words · `+
  `${(M.keys/M.commits).toFixed(1)} keys/word · `+
  `first suggestion right ${Math.round(100*M.top1/M.commits)}% · `+
  `unknown ${M.raw}`;
}
/* ------------------------------------------------------------------------- */

const $=id=>document.getElementById(id);
function score(i){
  let s=1/(i+2);
  s+=10*(recency.get(i)||0);
  if(prev!==null){const bg=bigram.get(prev);if(bg)s+=100*(bg.get(i)||0)}
  return s;
}
function norm(t){
  t=t.replace(/ch/g,"j").replace(/x/g,"s");
  t=t.replace(/ee/g,"i").replace(/aa/g,"a").replace(/oo/g,"o").replace(/ou/g,"u");
  t=t.replace(/ai/g,"ay").replace(/ao/g,"aw");
  t=t.replace(/b$/,"p").replace(/d$/,"t").replace(/g$/,"ng").replace(/ngng$/,"ng");
  return t;
}
function candidates(txt){
  let ids;
  if(!txt){
    ids=new Set();
    if(prev!==null){const bg=bigram.get(prev);if(bg)for(const i of bg.keys())ids.add(i)}
    for(const i of recency.keys())ids.add(i);
    ids=[...ids];
  }else{
    const nt=norm(txt);
    ids=[...(pref.get(txt)||[]),...(nt!==txt?(pref.get(nt)||[]):[])];
    for(const i of recency.keys())
      if(KK[i].startsWith(txt)||KK[i].startsWith(nt))ids.push(i);
    ids=[...new Set(ids)];
  }
  return ids.sort((a,b)=>score(b)-score(a)).slice(0,5);
}
function render(){
  const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
  const bar=$("bar");bar.innerHTML="";
  const cs=candidates(txt);
  if(!txt&&!cs.length){
    bar.innerHTML='<span class="hint">ພິມເພື່ອເລີ່ມ — try: sabai di bo</span>';return}
  cs.forEach((i,pos)=>{
    const d=document.createElement("div");d.className="cd";
    d.innerHTML='<span class="lo">'+LO[i]+'</span><span class="rm">'+KK[i]+'</span>';
    d.onclick=()=>commit(i,null,pos,txt.length===0);
    bar.appendChild(d);
  });
  if(txt){
    const d=document.createElement("div");d.className="cd raw";
    d.innerHTML='<span class="lo">'+txt+'</span><span class="rm">ສົ່ງຕາມຕົວ · as typed</span>';
    d.onclick=()=>commit(null,txt,-1,false);
    bar.appendChild(d);
  }
}
function commit(i,raw,pos,zeroKey){
  const t0=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
  const now=Date.now(),dt=M.lastT?Math.min(now-M.lastT,60000):0;M.lastT=now;
  M.commits++;M.keys+=t0.length+1;
  if(zeroKey)M.zeroKey++;
  const nrm=(i!==null&&t0&&!KK[i].startsWith(t0))?1:0;
  // level 2: [keysTyped, candidatePos(-1=raw), zeroKey, normalized, raw, msSincePrev]
  if(M.events.length<500)M.events.push([t0.length,i!==null?pos:-1,zeroKey?1:0,nrm,i===null?1:0,dt]);
  // level 3 buffer (memory only; sent ONLY if donate box is ticked)
  if(M.donated.length<300)M.donated.push([t0,i!==null?LO[i]:raw]);
  if(i!==null){
    if(pos===0)M.top1++;else M.barPick++;
    if(nrm)M.normed++;
    words.push({lao:LO[i],rom:RM[i],raw:false});
    recency.set(i,(recency.get(i)||0)+1);
    if(prev!==null){
      let bg=bigram.get(prev);
      if(!bg){bg=new Map();bigram.set(prev,bg)}
      bg.set(i,(bg.get(i)||0)+1);
    }
    prev=i;
  }else{
    M.raw++;if(M.oov.length<200)M.oov.push(raw);
    words.push({lao:raw,rom:"",raw:true});
    prev=null;
  }
  $("inp").value="";drawMsg();render();drawStats();$("inp").focus();
}
function drawMsg(){
  const m=$("msg");
  m.textContent=words.map(w=>w.lao).join(words.some(w=>w.raw)?" ":"");
  if($("showrom").checked&&words.length){
    const r=document.createElement("span");r.className="rom";
    r.textContent=words.map(w=>w.rom||w.lao).join(" ");
    m.appendChild(r);
  }
}
function undo(){if(words.length){M.undos++;words.pop();prev=null;drawMsg();render();drawStats()}}
function clearAll(){words=[];prev=null;drawMsg();render()}
function copyMsg(){
  const t=words.map(w=>w.lao).join(words.some(w=>w.raw)?" ":"");
  navigator.clipboard.writeText(t).then(()=>{
    $("cpy").textContent="✓ ກັອບປີ້ແລ້ວ · copied";
    setTimeout(()=>$("cpy").textContent="⧉ ກັອບປີ້ · copy",1200);
  });
}
$("inp").addEventListener("input",render);
$("inp").addEventListener("keydown",e=>{
  if(e.key===" "||e.key==="Enter"){
    e.preventDefault();
    const txt=$("inp").value.trim().toLowerCase().replace(/[^a-z]/g,"");
    if(!txt)return;
    const cs=candidates(txt);
    if(cs.length&&(KK[cs[0]].startsWith(txt)||KK[cs[0]].startsWith(norm(txt))))
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
render();
</script></body></html>'''
open("try-keyboard.html","w").write(html.replace("__DATA__", data))
import os
print("wrote try-keyboard.html", os.path.getsize("try-keyboard.html"), "bytes")
