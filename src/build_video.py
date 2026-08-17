import json
data = open("events.json").read()

html = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Typing race — today's keyboard vs draft 4</title><style>
:root{--bg:#0f1115;--pan:#171a21;--ln:#252a34;--ink:#e6e9ef;--dim:#8b93a3;
--acc:#6ea8fe;--bad:#f2777a;--good:#6fcf97;--key:#232833;--flash:#6ea8fe}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif;
display:flex;flex-direction:column;align-items:center;padding:20px 12px 50px}
h1{font-size:19px;margin:0 0 2px;letter-spacing:-.01em}
.sub{color:var(--dim);font-size:13px;margin:0 0 14px;text-align:center;max-width:640px}
.ctrl{display:flex;gap:8px;margin-bottom:16px;align-items:center}
button{background:var(--key);border:1px solid var(--ln);color:var(--ink);
border-radius:8px;padding:7px 16px;font-size:14px;cursor:pointer}
button:hover{border-color:var(--acc)}
button.primary{background:var(--acc);color:#08101c;border-color:var(--acc);font-weight:600}
.speed{color:var(--dim);font-size:13px}
.stage{display:grid;grid-template-columns:1fr 1fr;gap:18px;width:100%;max-width:880px}
@media(max-width:700px){.stage{grid-template-columns:1fr}}
.phone{background:var(--pan);border:1px solid var(--ln);border-radius:18px;
overflow:hidden;display:flex;flex-direction:column;height:560px}
.title{padding:9px 14px;border-bottom:1px solid var(--ln);font-size:13px;
font-weight:600;display:flex;justify-content:space-between;align-items:center}
.title .tag{font-size:11px;color:var(--dim);font-weight:400}
.taps{font-variant-numeric:tabular-nums;font-size:16px}
.screen{flex:1;padding:10px 12px;overflow-y:auto;background:#12151b}
.bub{border-radius:12px 12px 4px 12px;padding:7px 11px;margin:0 0 7px auto;
max-width:88%;width:fit-content;font-size:15px;background:#1d3a5c;line-height:1.45}
.bub.mine{margin:0 auto 7px 0;background:#20242e;border-radius:12px 12px 12px 4px}
.bub .rom{display:block;font-size:10px;color:#9fc2e8;margin-top:2px;
font-family:ui-monospace,Menlo,monospace}
.bub .w{padding:0 2px}.bub .w.amb{background:#4a2327;border-radius:3px;color:#f2999b}
.compose{border-top:1px solid var(--ln);padding:7px 11px;min-height:36px;
font-family:ui-monospace,Menlo,monospace;font-size:14px;color:var(--acc);
display:flex;align-items:center}
.caret{display:inline-block;width:1.5px;height:15px;background:var(--acc);
margin-left:1px;animation:bl .9s steps(1) infinite}
@keyframes bl{50%{opacity:0}}
.bar{display:flex;gap:5px;padding:6px 8px;border-top:1px solid var(--ln);
background:#141821;min-height:46px;align-items:center;overflow:hidden}
.cd{background:var(--key);border:1px solid var(--ln);border-radius:8px;
padding:3px 8px;text-align:center;min-width:52px;transition:all .12s}
.cd .lo{font-size:14px;display:block;line-height:1.25}
.cd .en{font-size:8.5px;color:var(--dim);display:block;max-width:90px;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cd.hit{background:var(--acc);border-color:var(--acc)}
.cd.hit .lo,.cd.hit .en{color:#08101c}
.bar .none{color:#454d5c;font-size:12px}
.kb{background:#0d1015;padding:6px 4px 9px;border-top:1px solid var(--ln)}
.krow{display:flex;justify-content:center;gap:3px;margin-bottom:4px}
.kk{background:var(--key);border:1px solid #2b3140;border-radius:5px;height:30px;
min-width:24px;flex:1;max-width:34px;display:flex;align-items:center;
justify-content:center;font-size:12px;color:var(--ink);transition:background .05s}
.kk.sp{max-width:150px;flex:4}
.kk.lit{background:var(--flash);color:#08101c;border-color:var(--flash)}
.score{margin-top:16px;background:var(--pan);border:1px solid var(--ln);
border-radius:12px;padding:13px 18px;max-width:880px;width:100%;
display:flex;gap:26px;flex-wrap:wrap;font-size:13.5px}
.score b{font-variant-numeric:tabular-nums}
.done{color:var(--good);font-weight:600}
</style></head><body>
<h1>Typing race — the same conversation on both keyboards</h1>
<p class="sub">Left: how Lao people text today — every letter typed by hand.
Right: <b>draft 4</b> — same letters, but a learning engine predicts the word and
sends real Lao script. <span style="color:var(--bad)">Red</span> words on the left
are spelled identically to other Lao words.</p>
<div class="ctrl">
 <button class="primary" id="play" onclick="toggle()">&#9654; Play</button>
 <button onclick="restart()">&#8634; Restart</button>
 <button onclick="cycleSpeed()"><span class="speed" id="spd">speed 2&times;</span></button>
</div>
<div class="stage">
 <div class="phone"><div class="title"><span>Today &middot; karaoke Lao
   <span class="tag">no engine</span></span><span class="taps" id="tL">0 taps</span></div>
  <div class="screen" id="sL"></div>
  <div class="compose"><span id="cL"></span><span class="caret"></span></div>
  <div class="bar"><span class="none">no suggestions</span></div>
  <div class="kb" id="kL"></div></div>
 <div class="phone"><div class="title"><span>Draft 4
   <span class="tag">same letters + learning engine</span></span><span class="taps" id="tR">0 taps</span></div>
  <div class="screen" id="sR"></div>
  <div class="compose"><span id="cR"></span><span class="caret"></span></div>
  <div class="bar" id="bR"><span class="none">&nbsp;</span></div>
  <div class="kb" id="kR"></div></div>
</div>
<div class="score">
 <span>Message <b id="mN">0</b> / <b id="mT">40</b></span>
 <span>Today: <b id="fL">0</b> taps</span>
 <span>Draft 4: <b id="fR">0</b> taps</span>
 <span id="verdict" style="color:var(--dim)"></span>
</div>
<script>
const D = __DATA__;
const ROWS=[['q','w','e','r','t','y','u','i','o','p'],
 ['a','s','d','f','g','h','j','k','l'],['z','x','c','v','b','n','m']];
function kb(id){const el=document.getElementById(id);
 ROWS.forEach(r=>{const d=document.createElement('div');d.className='krow';
  r.forEach(c=>{const k=document.createElement('div');k.className='kk';
   k.textContent=c;k.id=id+'-'+c;d.appendChild(k);});el.appendChild(d);});
 const d=document.createElement('div');d.className='krow';
 const s=document.createElement('div');s.className='kk sp';s.id=id+'-SP';
 s.textContent='space';d.appendChild(s);el.appendChild(d);}
kb('kL');kb('kR');
document.getElementById('mT').textContent=D.msgs.length;

let mi=0,playing=false,speed=2,timer=null;
let taps={L:0,R:0},buf={L:'',R:''};
const BASE=170;

function flash(kbid,ch){const el=document.getElementById(kbid+'-'+(ch||'SP'));
 if(!el)return;el.classList.add('lit');setTimeout(()=>el.classList.remove('lit'),BASE/speed*.7);}
function setBar(steps){const b=document.getElementById('bR');b.innerHTML='';
 if(!steps||!steps.length){b.innerHTML='<span class="none">&nbsp;</span>';return;}
 steps.forEach((c,i)=>{const d=document.createElement('div');d.className='cd';
  d.id='cd'+i;d.innerHTML='<span class="lo">'+c[0]+'</span><span class="en">'+c[1]+'</span>';
  b.appendChild(d);});}
function bubble(side,htmlStr,mine){const s=document.getElementById(side);
 const b=document.createElement('div');b.className='bub'+(mine?' mine':'');
 b.innerHTML=htmlStr;s.appendChild(b);s.scrollTop=s.scrollHeight;return b;}

function runMsg(m,done){
 const mine=m.who==='A';
 let li=0,ri=0,lDone=false,rDone=false;
 let lWords=[],rWords=[];
 function step(side){
  const steps=side==='L'?m.L:m.R;
  let i=side==='L'?li:ri;
  if(i>=steps.length){
   if(side==='L')lDone=true;else rDone=true;
   if(lDone&&rDone)setTimeout(done,500/speed);
   return;}
  const ev=steps[i];
  let delay=BASE;
  if(ev.t==='key'){
   flash(side==='L'?'kL':'kR',ev.c);
   buf[side]+=ev.c;taps[side]++;
   document.getElementById('c'+side).textContent=buf[side];
   if(side==='R')setBar(ev.bar);
  }else if(ev.t==='bar'){setBar(ev.bar);delay=BASE*.6;
  }else if(ev.t==='commit'){
   taps[side]++;
   if(side==='L'){
    flash('kL',null);
    lWords.push('<span class="w'+(ev.amb>1?' amb':'')+'" title="'+ev.amb+
     ' words share this spelling">'+ev.out+'</span>');
   }else{
    const c=document.getElementById('cd'+ev.pick);
    if(c)c.classList.add('hit');
    rWords.push(ev.out);
    delay=BASE*1.4;
   }
   buf[side]='';document.getElementById('c'+side).textContent='';
  }
  document.getElementById('t'+side).textContent=taps[side]+' taps';
  document.getElementById('f'+side).textContent=taps[side];
  if(side==='L')li=i+1;else ri=i+1;
  if(side==='L')li=li;else ri=ri;
  setTimeout(()=>step(side),delay/speed);
  if(ev.t==='commit'&&i===steps.length-1){
   if(side==='L')bubble('sL',lWords.join(' '),mine);
   else bubble('sR',rWords.join(' ')+'<span class="rom">'+
     m.R.filter(e=>e.t==='commit').map(e=>e.rom).join(' ')+'</span>',mine);
  }
 }
 step('L');step('R');
}
function next(){
 if(mi>=D.msgs.length){
  playing=false;document.getElementById('play').innerHTML='&#9654; Replay';
  document.getElementById('verdict').innerHTML=
   '<span class="done">Done — '+taps.R+' vs '+taps.L+' taps: '+
   Math.round(100*(taps.L-taps.R)/taps.L)+'% fewer, and the right side sent real Lao script.</span>';
  return;}
 document.getElementById('mN').textContent=mi+1;
 runMsg(D.msgs[mi],()=>{mi++;if(playing)next();});
}
function toggle(){
 if(mi>=D.msgs.length)restart();
 playing=!playing;
 document.getElementById('play').innerHTML=playing?'&#10074;&#10074; Pause':'&#9654; Play';
 if(playing)next();}
function restart(){
 mi=0;taps={L:0,R:0};buf={L:'',R:''};
 ['sL','sR'].forEach(x=>document.getElementById(x).innerHTML='');
 ['cL','cR'].forEach(x=>document.getElementById(x).textContent='');
 document.getElementById('verdict').textContent='';
 setBar(null);
 document.getElementById('mN').textContent=0;}
function cycleSpeed(){speed=speed===1?2:speed===2?4:1;
 document.getElementById('spd').textContent='speed '+speed+'\\u00d7';}
</script></body></html>"""
open("typing-race.html","w").write(html.replace("__DATA__", data))
print("wrote typing-race.html", len(html)+len(data), "bytes")
