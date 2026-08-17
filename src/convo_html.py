import json, html
d = json.load(open("convo.json")); rows, tot = d["rows"], d["tot"]
kw, dw = tot["karaoke"], tot["draft3"]

def msg(r):
    who = r["who"]; side = "a" if who=="A" else "b"
    en = " ".join(g.split()[0] if g else "?" for _,g in r["words"])
    lao = " ".join(w for w,_ in r["words"])
    def spell(sys):
        out=[]
        for (w,g),(full,typed,n) in zip(r["words"], r[sys]["detail"]):
            cls = "amb" if n>1 else ""
            tip = f"{n} words share this spelling" if n>1 else g
            out.append(f'<span class="wd {cls}" title="{html.escape(tip)}">{html.escape(full)}</span>')
        return " ".join(out)
    return f'''<div class="row {side}">
      <div class="msg">
        <div class="lao">{html.escape(lao)}</div>
        <div class="en">{html.escape(en)}</div>
        <div class="sp"><i>old</i> {spell("karaoke")}
          <b>{r["karaoke"]["keys"]}</b> keys · <b class="{'bad' if r['karaoke']['amb'] else ''}">{r["karaoke"]["amb"]}</b> unclear</div>
        <div class="sp"><i>new</i> {spell("draft3")}
          <b>{r["draft3"]["keys"]}</b> keys · <b class="{'bad' if r['draft3']['amb'] else ''}">{r["draft3"]["amb"]}</b> unclear</div>
      </div></div>'''

H = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Two friends texting — old keyboard vs new</title><style>
:root{{--bg:#0f1115;--pan:#171a21;--ln:#252a34;--ink:#e6e9ef;--dim:#8b93a3;
--acc:#6ea8fe;--bad:#f2777a;--good:#6fcf97}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif;padding:28px 16px 70px;
display:flex;justify-content:center}}
.wrap{{max-width:940px;width:100%}}
h1{{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}}
.sub{{color:var(--dim);font-size:13.5px;margin:0 0 22px;max-width:640px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
gap:12px;margin-bottom:26px}}
.card{{background:var(--pan);border:1px solid var(--ln);border-radius:12px;padding:15px 17px}}
.card .lab{{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);margin-bottom:7px}}
.card .big{{font-size:27px;font-weight:600;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.card .note{{font-size:12px;color:var(--dim);margin-top:5px}}
.good{{color:var(--good)}}.bad{{color:var(--bad)}}
.row{{display:flex;margin-bottom:11px}}.row.b{{justify-content:flex-end}}
.msg{{background:var(--pan);border:1px solid var(--ln);border-radius:14px;
padding:11px 14px;max-width:82%}}
.row.b .msg{{background:#1b2b3f;border-color:#2a3f5a}}
.lao{{font-size:19px;line-height:1.5}}
.en{{font-size:11.5px;color:var(--dim);margin:2px 0 8px}}
.sp{{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:var(--dim);
margin-top:4px;line-height:1.7}}
.sp i{{display:inline-block;width:26px;color:#5c6474;font-style:normal}}
.sp b{{color:var(--ink);font-weight:600}}
.wd{{padding:1px 4px;border-radius:4px;background:#22262f;margin-right:1px;cursor:help}}
.wd.amb{{background:#3d2226;color:#f2999b}}
.legend{{font-size:12.5px;color:var(--dim);margin:20px 0 14px;
border-left:2px solid var(--ln);padding-left:12px}}
</style></head><body><div class="wrap">
<h1>Two friends texting — old keyboard vs new</h1>
<p class="sub">40 messages across 10 topics, {kw[3]} words. Each bubble shows the Lao,
a rough English gloss, and how the message is spelled on each keyboard.
<b class="bad">Red</b> words are spelled identically to some other Lao word — the
reader has to guess which one was meant.</p>

<div class="cards">
 <div class="card"><div class="lab">Keystrokes, old</div><div class="big">{kw[0]}</div>
   <div class="note">karaoke Lao, no predictor — what people do today</div></div>
 <div class="card"><div class="lab">Keystrokes, new</div><div class="big">{dw[0]}</div>
   <div class="note">draft 3 with prediction — {dw[0]-kw[0]:+d} vs old</div></div>
 <div class="card"><div class="lab">Unclear words, old</div><div class="big bad">{kw[2]}</div>
   <div class="note">{100*kw[2]/kw[3]:.0f}% of everything sent</div></div>
 <div class="card"><div class="lab">Unclear words, new</div><div class="big good">{dw[2]}</div>
   <div class="note">{100*dw[2]/dw[3]:.0f}% — {kw[2]-dw[2]} fewer</div></div>
</div>

<div class="legend">Same effort to type — {abs(dw[0]-kw[0])} keystrokes apart across the
whole conversation, under half a percent. The difference is entirely on the
receiving end: <b>{kw[2]} ambiguous words become {dw[2]}</b>.</div>
{''.join(msg(r) for r in rows)}
<div class="legend" style="margin-top:22px">The Lao here is assembled from real
dictionary words and a native speaker would rephrase much of it. That does not
affect the measurement, which depends on which words are typed and how they are
spelled, not on whether the grammar is natural.</div>
</div></body></html>'''
open("convo.html","w").write(H)
print("wrote convo.html", len(H), "bytes")
