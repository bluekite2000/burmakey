import json
data = open("demo_lex.json").read()

html = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aksoon Laatin — typing simulator</title>
<style>
:root{
  --bg:#0f1115; --panel:#171a21; --line:#252a34; --ink:#e6e9ef; --dim:#8b93a3;
  --accent:#6ea8fe; --warn:#f0a35e; --good:#6fcf97; --key:#232833; --keyd:#2d3340;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 display:flex;justify-content:center;padding:26px 16px 60px}
.wrap{width:100%;max-width:1080px;display:grid;grid-template-columns:376px 1fr;gap:26px}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
h1{font-size:19px;margin:0 0 3px;letter-spacing:-.01em}
.sub{color:var(--dim);font-size:13px;margin:0 0 18px}
.phone{background:var(--panel);border:1px solid var(--line);border-radius:20px;
 overflow:hidden;display:flex;flex-direction:column;height:640px}
.screen{flex:1;padding:14px;overflow-y:auto;background:#12151b}
.bubble{background:#1d3a5c;border-radius:14px 14px 4px 14px;padding:9px 12px;
 margin:0 0 8px auto;max-width:86%;width:fit-content;font-size:20px;line-height:1.5}
.bubble .gl{display:block;font-size:11px;color:#9fc2e8;margin-top:3px;line-height:1.35}
.compose{border-top:1px solid var(--line);padding:9px 12px;min-height:44px;
 display:flex;align-items:center;gap:8px;background:var(--panel)}
.typed{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:15px;
 letter-spacing:.02em;color:var(--accent);min-height:20px;word-break:break-all}
.caret{display:inline-block;width:1.5px;height:16px;background:var(--accent);
 vertical-align:-3px;animation:bl 1s steps(1) infinite}
@keyframes bl{50%{opacity:0}}
.cands{display:flex;gap:6px;padding:8px 9px;border-top:1px solid var(--line);
 background:#141821;overflow-x:auto;min-height:52px;align-items:center}
.cand{flex:0 0 auto;background:var(--key);border:1px solid var(--line);
 border-radius:9px;padding:5px 10px;cursor:pointer;text-align:center;min-width:56px}
.cand:hover{background:var(--keyd);border-color:var(--accent)}
.cand .lo{font-size:17px;display:block;line-height:1.3}
.cand .en{font-size:9.5px;color:var(--dim);display:block;max-width:104px;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hint{color:var(--dim);font-size:12px;padding-left:3px}
.kb{background:#0d1015;padding:7px 5px 11px;border-top:1px solid var(--line)}
.row{display:flex;justify-content:center;gap:4px;margin-bottom:5px}
.k{background:var(--key);border:1px solid #2b3140;border-radius:6px;height:38px;
 min-width:29px;flex:1;display:flex;align-items:center;justify-content:center;
 font-size:14px;cursor:pointer;user-select:none;color:var(--ink)}
.k:active{background:var(--accent);color:#08101c}
.k.wide{flex:2.4;font-size:11px;letter-spacing:.06em}
.k.tone{background:#2a2233;border-color:#453655;color:#d9b8f0}
.side{display:flex;flex-direction:column;gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:15px 17px}
.card h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;
 color:var(--dim);margin:0 0 11px;font-weight:600}
.toggle{display:flex;gap:6px;margin-bottom:12px}
.tg{flex:1;padding:8px;border-radius:9px;border:1px solid var(--line);
 background:var(--key);cursor:pointer;text-align:center;font-size:13px}
.tg.on{background:var(--accent);color:#08101c;border-color:var(--accent);font-weight:600}
.stat{display:flex;justify-content:space-between;padding:6px 0;
 border-bottom:1px solid #1d222c;font-size:13px}
.stat:last-child{border:0}
.stat b{font-variant-numeric:tabular-nums;font-weight:600}
.big{font-size:26px;font-variant-numeric:tabular-nums;font-weight:600;letter-spacing:-.02em}
.warn{color:var(--warn)} .good{color:var(--good)} .dim{color:var(--dim)}
code{background:#22262f;padding:1px 5px;border-radius:4px;
 font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
ul{margin:8px 0 0;padding-left:17px} li{margin-bottom:6px;font-size:13.5px}
.ex{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
.ex span{background:var(--key);border:1px solid var(--line);border-radius:7px;
 padding:4px 9px;font-size:12px;cursor:pointer;font-family:ui-monospace,Menlo,monospace}
.ex span:hover{border-color:var(--accent)}
p{margin:0 0 9px;font-size:13.5px} p:last-child{margin:0}
</style></head><body><div class="wrap">

<div>
<h1>Aksoon Laatin</h1>
<p class="sub">Type Lao with English letters. Tap a suggestion to send it.</p>
<div class="phone">
  <div class="screen" id="screen"></div>
  <div class="compose"><span class="typed" id="typed"></span><span class="caret"></span></div>
  <div class="cands" id="cands"><span class="hint">start typing — try <code>kh</code></span></div>
  <div class="kb" id="kb"></div>
</div>
</div>

<div class="side">
  <div class="card">
    <h2>Spelling mode</h2>
    <div class="toggle">
      <div class="tg on" id="tg-al" onclick="setMode('al')">Aksoon Laatin</div>
      <div class="tg" id="tg-kk" onclick="setMode('kk')">karaoke Lao</div>
    </div>
    <p class="dim" id="modenote">Tones and vowel length are written. Fewer words
    share a spelling, so the keyboard can tell them apart.</p>
  </div>

  <div class="card">
    <h2>What this input matches</h2>
    <div class="big" id="nmatch">—</div>
    <p class="dim" id="matchnote">Lao words match what you've typed so far.</p>
    <div class="stat"><span>Keys pressed</span><b id="keys">0</b></div>
    <div class="stat"><span>Words sent</span><b id="sent">0</b></div>
    <div class="stat"><span>Keys per word</span><b id="kpw">—</b></div>
  </div>

  <div class="card">
    <h2>Try these</h2>
    <div class="ex" id="ex"></div>
  </div>

  <div class="card">
    <h2>What you're looking at</h2>
    <p>Every Lao word here is real, from a 21,000-word list Google publishes.
    The English underneath is so you can tell the words apart.</p>
    <p>Switch to <b>karaoke Lao</b> — how Lao people actually text today — and
    type the same thing. The suggestion bar fills up with words that are all
    spelled identically. That's the problem this is trying to fix.</p>
    <p class="dim">Purple keys are tone letters. They carry pitch, which changes
    a word's meaning entirely. Karaoke Lao throws them away.</p>
  </div>
</div>
</div>

<script>
const LEX = __DATA__;
let mode='al', typed='', keys=0, sent=0;

const ROWS=[['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l'],
            ['z','x','c','v','b','n','m']];
const TONES=new Set(['r','v','q','z','c']);

function buildKB(){
  const kb=document.getElementById('kb'); kb.innerHTML='';
  ROWS.forEach(r=>{
    const d=document.createElement('div'); d.className='row';
    r.forEach(c=>{
      const k=document.createElement('div');
      k.className='k'+(TONES.has(c)&&mode==='al'?' tone':'');
      k.textContent=c; k.onclick=()=>press(c); d.appendChild(k);
    });
    kb.appendChild(d);
  });
  const d=document.createElement('div'); d.className='row';
  const bs=document.createElement('div'); bs.className='k wide'; bs.textContent='DEL';
  bs.onclick=()=>{typed=typed.slice(0,-1);render();}; d.appendChild(bs);
  const sp=document.createElement('div'); sp.className='k'; sp.style.flex='5';
  sp.textContent='space'; sp.onclick=()=>commitTop(); d.appendChild(sp);
  kb.appendChild(d);
}
function press(c){ typed+=c; keys++; render(); }

function matches(){
  if(!typed) return [];
  const f = mode==='al' ? (d=>d.a) : (d=>d.k);
  return LEX.filter(d=>f(d).startsWith(typed));
}
function render(){
  document.getElementById('typed').textContent=typed;
  const m=matches();
  const bar=document.getElementById('cands');
  bar.innerHTML='';
  if(!typed){ bar.innerHTML='<span class="hint">start typing — try <code>kh</code></span>'; }
  else if(!m.length){ bar.innerHTML='<span class="hint">no word matches that</span>'; }
  else m.slice(0,40).forEach(d=>{
    const e=document.createElement('div'); e.className='cand';
    e.innerHTML='<span class="lo">'+d.l+'</span><span class="en">'+d.g+'</span>';
    e.onclick=()=>commit(d); bar.appendChild(e);
  });
  const n=document.getElementById('nmatch');
  n.textContent = typed ? m.length : '—';
  n.className='big '+(m.length>8?'warn':m.length?'good':'');
  document.getElementById('matchnote').textContent = !typed
    ? 'Lao words match what you\\'ve typed so far.'
    : m.length===1 ? 'Exactly one word. The keyboard knows what you mean.'
    : m.length>8 ? 'Too many to choose from — you have to keep typing.'
    : 'Narrowing down.';
  document.getElementById('keys').textContent=keys;
  document.getElementById('sent').textContent=sent;
  document.getElementById('kpw').textContent = sent? (keys/sent).toFixed(1) : '—';
}
function commit(d){
  const s=document.getElementById('screen');
  const b=document.createElement('div'); b.className='bubble';
  b.innerHTML=d.l+'<span class="gl">'+d.g+'</span>';
  s.appendChild(b); s.scrollTop=s.scrollHeight;
  typed=''; sent++; keys++; render();
}
function commitTop(){ const m=matches(); if(m.length) commit(m[0]); }
function setMode(x){
  mode=x; typed=''; keys=0; sent=0;
  document.getElementById('tg-al').classList.toggle('on',x==='al');
  document.getElementById('tg-kk').classList.toggle('on',x==='kk');
  document.getElementById('modenote').textContent = x==='al'
    ? 'Tones and vowel length are written. Fewer words share a spelling, so the keyboard can tell them apart.'
    : 'No tones, no vowel length — how Lao people text today. Far more words collapse onto the same spelling.';
  document.getElementById('screen').innerHTML='';
  buildKB(); render();
}
document.addEventListener('keydown',e=>{
  if(e.key==='Backspace'){typed=typed.slice(0,-1);render();e.preventDefault();}
  else if(e.key===' '){commitTop();e.preventDefault();}
  else if(/^[a-z]$/.test(e.key)) press(e.key);
});
const EX=['kh','kaa','saa','mee','naam','khoo','thaa','buun'];
document.getElementById('ex').innerHTML=EX.map(x=>'<span onclick="typed=\\''+x+
  '\\';keys+='+0+';render()">'+x+'</span>').join('');
buildKB(); render();
</script></body></html>"""

open("aksoon-demo.html","w").write(html.replace("__DATA__", data))
print("wrote aksoon-demo.html", len(html)+len(data), "bytes")
