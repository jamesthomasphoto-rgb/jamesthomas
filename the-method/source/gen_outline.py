import json, re, html, sys
src, fontsrc, base, ed = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d=json.load(open(src)); E=html.escape; ninety = "weeks" in d
fonts=re.search(r"<style>(\s*(?:/\*[^*]*\*/\s*)?@font-face.*?)</style>", open(fontsrc).read(), re.S).group(1)
md=[]; h=[]
def both(m, x): md.append(m); h.append(x)
title = "The 90-Day Program — Outline" if ninety else "Curriculum Outline"
both(f"# The Method — {title}\n\n*James Thomas · {ed}*\n\n"+" · ".join(d["meta"])+f"\n\n{d['sub']}\n\n{d['forTxt']}\n",
 f'<header class="top"><p class="ey">James Thomas · {E(ed)}</p><h1>The Method</h1><p class="ttl">{E(title)}</p><p class="meta">{" · ".join(map(E,d["meta"]))}</p><p class="sub">{E(d["sub"])}</p><p>{E(d["forTxt"])}</p></header>')
o=d["one"]
both(f"\n## I. Overview — {o['h']}\n\n{o['lead']}\n\n> {o['pull']} — James Thomas\n\n"+"\n\n".join(o["paras"])+"\n\n**What's included**\n\n"+"\n".join(f"- **{a}** — {b}" for a,b in o["pillars"])+"\n",
 f'<h2><span>I.</span> Overview</h2><p class="lead"><b>{E(o["h"])}</b> {E(o["lead"])}</p><blockquote>{E(o["pull"])} <cite>— James Thomas</cite></blockquote>'+"".join(f"<p>{E(p)}</p>" for p in o["paras"])+'<h4>What’s included</h4><ul>'+"".join(f"<li><b>{E(a)}</b> — {E(b)}</li>" for a,b in o["pillars"])+"</ul>")
lastcol = "Push hardest" if ninety else "Start"
both("\n## II. The Five Stages\n\n"+d["stagesIntro"]+"\n\n"+"\n".join(f"{i+1}. **Stage {s[0]} — {s[1]}.** {s[2]} *{lastcol}: {s[3].replace('Start: ','')}*" for i,s in enumerate(d["stages"]))+"\n",
 f'<h2><span>II.</span> The Five Stages</h2><p>{E(d["stagesIntro"])}</p><table class="t"><tr><th>Stage</th><th>Name</th><th>What it looks like</th><th>{lastcol}</th></tr>'+"".join(f"<tr><td>{E(s[0])}</td><td><b>{E(s[1])}</b></td><td>{E(s[2])}</td><td>{E(s[3].replace('Start: ',''))}</td></tr>" for s in d["stages"])+"</table>")
mt = "The 90-Day Program — Three Moves" if ninety else "The Six-Month Program — Three Moves"
x=f'<h2><span>III.</span> {E(mt)}</h2><p>{E(d["movesIntro"])}</p><ol>'+"".join(f"<li><b>{E(m['t'])}</b> <i>{E(m['w'])}</i><br>{E(m['p'])}</li>" for m in d["moves"])+f'</ol><p class="note">{E(d["under"])}</p>'
m=f"\n## III. {mt}\n\n"+d["movesIntro"]+"\n\n"+"\n".join(f"{int(mv['n'])}. **{mv['t']}** ({mv['w']}) — {mv['p']}" for mv in d["moves"])+f"\n\n**{d['under']}**\n"
if ninety:
    m+="\n**The twelve weeks**\n\n| Week | Move | Course | By the end of the week |\n|---|---|---|---|\n"+"\n".join(f"| {w} | {mv} | {c} | {t} |" for w,mv,c,t in d["weeks"])+"\n"
    x+='<h4>The twelve weeks</h4><table class="t"><tr><th>Week</th><th>Move</th><th>Course</th><th>By the end of the week</th></tr>'+"".join(f"<tr><td><b>{E(w)}</b></td><td>{E(mv)}</td><td>{E(c)}</td><td>{E(t)}</td></tr>" for w,mv,c,t in d["weeks"])+"</table>"
both(m,x)
both("\n## IV. The Diagnosis — Ten Problems\n\n"+d["tenIntro"]+"\n\n"+"\n".join(f"{i+1}. {a} → {b}" for i,(a,b) in enumerate(d["ten"]))+"\n",
 f'<h2><span>IV.</span> The Diagnosis — Ten Problems</h2><p>{E(d["tenIntro"])}</p><table class="t"><tr><th>Problem</th><th>Fix</th><th>Problem</th><th>Fix</th></tr>'+"".join(f"<tr><td><b>{E(d['ten'][i][0])}</b></td><td>{E(d['ten'][i][1])}</td><td><b>{E(d['ten'][i+5][0])}</b></td><td>{E(d['ten'][i+5][1])}</td></tr>" for i in range(5))+"</table>")
both("\n## V. The Classroom — Fifteen Courses\n\n"+d["tocIntro"]+"\n", f'<h2><span>V.</span> The Classroom — Fifteen Courses</h2><p>{E(d["tocIntro"])}</p>')
for c in d["courses"]:
    parts=[p.strip() for p in c["tag"].split("·")]
    grp=" · ".join(p for p in parts[1:-1] if p!="Move"); cnt=parts[-1]
    v=[t+("" if cl=="on" else " *(being added)*") for t,cl in c["vault"]]
    mm=f"\n### Course {c['n']} — {c['h']}\n*{c['st']}* · {grp} · {cnt}\n\n**You leave with:** {c['out']}\n\n"+"\n".join(f"- **{a} {b}** — {s}" for a,b,s in c["lessons"])+f"\n\n**Do this:** {c['doThis']}\n"+(("\n**In the Vault:** "+"; ".join(v)+"\n") if v else "")
    vh=", ".join(E(t)+("" if cl=="on" else " <i>(being added)</i>") for t,cl in c["vault"])
    xx=f'<section class="course"><h3><span class="cn">{E(c["n"])}</span>{E(c["h"])}</h3><p class="cm"><i>{E(c["st"])}</i> · {E(grp)} · {E(cnt)}</p><p><b class="lab">You leave with</b> {E(c["out"])}</p><ol class="ls">'+"".join(f'<li><span>{E(a)}</span><div><b>{E(b)}</b> — {E(s)}</div></li>' for a,b,s in c["lessons"])+f'</ol><p><b class="lab">Do this</b> {E(c["doThis"])}</p>'+(f'<p><b class="lab">In the Vault</b> {vh}</p>' if vh else "")+"</section>"
    both(mm,xx)
both("\n## VI. Tracks\n\n"+d["tracksIntro"]+"\n", f'<h2 class="pb"><span>VI.</span> Tracks</h2><p>{E(d["tracksIntro"])}</p>')
for t in d["tracks"]:
    both(f"\n### Track {t['l']} — {t['h']}\n*{t['w']}*\n\n"+"\n".join(f"- {i}" for i in t["items"])+(f"\n\n{t['r']}\n" if t["r"] else "\n"),
     f'<section class="course"><h3><span class="cn">{E(t["l"])}</span>{E(t["h"])}</h3><p class="cm"><i>{E(t["w"])}</i></p><ul>'+"".join(f"<li>{E(i)}</li>" for i in t["items"])+"</ul>"+(f'<p class="cm">{E(t["r"])}</p>' if t["r"] else "")+"</section>")
both("\n## VII. The Vault\n\n"+d["vaultIntro"]+"\n\n**Available now**\n\n"+"\n".join(f"- **{a}** ({b}) — {c}" for a,b,c in d["vault"])+"\n\n**Being added**\n\n"+"\n".join(f"- {x}" for x in d["coming"])+"\n",
 f'<h2><span>VII.</span> The Vault</h2><p>{E(d["vaultIntro"])}</p><h4>Available now</h4><ul>'+"".join(f"<li><b>{E(a)}</b> <i>({E(b)})</i> — {E(c)}</li>" for a,b,c in d["vault"])+'</ul><h4>Being added</h4><ul class="cols">'+"".join(f"<li>{E(x)}</li>" for x in d["coming"])+"</ul>")
both("\n## VIII. How It Runs\n\n**The weekly rhythm**\n\n"+"\n".join(f"- **{a}** — {b}" for a,b in d["rhythm"])+"\n\n**The rules of the room**\n\n"+"\n".join(f"{int(n)}. **{b}** {c}" for n,b,c in d["rules"])+"\n",
 '<h2><span>VIII.</span> How It Runs</h2><h4>The weekly rhythm</h4><ul>'+"".join(f"<li><b>{E(a)}</b> — {E(b)}</li>" for a,b in d["rhythm"])+'</ul><h4>The rules of the room</h4><ol>'+"".join(f"<li><b>{E(b)}</b> {E(c)}</li>" for n,b,c in d["rules"])+"</ol>")
cl=d["close"]
both(f"\n## IX. Where You Start — {cl['h']}\n\n{cl['p']}\n\n"+"\n".join(f"{int(a)}. {b}" for a,b in cl["steps"])+f"\n\n— James\n\n---\n\n*{cl['fine']}*\n",
 f'<h2><span>IX.</span> Where You Start — {E(cl["h"])}</h2><p>{E(cl["p"])}</p><ol>'+"".join(f"<li>{E(b)}</li>" for a,b in cl["steps"])+f'</ol><p class="sign">— James</p><p class="fine">{E(cl["fine"])}</p>')
open(base+".md","w").write("".join(md))
css=open("outline.html").read().split("</style><style>")[1].split("</style>")[0].replace("CURRICULUM OUTLINE", ("90-DAY PROGRAM OUTLINE" if ninety else "CURRICULUM OUTLINE"))
open(base+".html","w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>The Method — {E(title)}</title><style>{fonts}</style><style>{css}</style></head><body>{"".join(h)}</body></html>')
