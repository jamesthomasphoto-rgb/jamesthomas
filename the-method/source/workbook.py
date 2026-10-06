import json, re, html
E=html.escape
d=json.load(open("outline90.json"))
fonts=re.search(r"<style>(\s*(?:/\*[^*]*\*/\s*)?@font-face.*?)</style>", open("method-90.html").read(), re.S).group(1)
vault=json.load(open("vault/index.json"))
vault_by_course={}
for slug,c,t in vault: vault_by_course.setdefault(c.split(" · ")[0].replace("Course ",""),[]).append(t)
courses={c["n"]:c for c in d["courses"]}
WEEKS=[("1",["00","01"]),("2",["03"]),("3",["04"]),("4",["05"]),("5",["06"]),("6",["07"]),("7",["08"]),("8",["09"]),("9",["10"]),("10",["11"]),("11",["12"]),("12",["13","14"])]
MOVE=lambda w: "Money In" if int(w)<=4 else ("The Machine" if int(w)<=8 else "Step Out")
def lines(n): return '<div class="lines">'+'<i></i>'*n+'</div>'
def box(t,b,cls=""): return f'<div class="box {cls}"><b>{t}</b>{b}</div>'
css='''
@page{size:Letter;margin:.65in .8in .7in;@top-left{content:"THE METHOD  \\00B7  WORKBOOK";font:7pt Epilogue,sans-serif;letter-spacing:.18em;color:#9c9c95}@top-right{content:"JAMES THOMAS";font:7pt Epilogue,sans-serif;letter-spacing:.18em;color:#9c9c95}@bottom-right{content:counter(page);font:8pt Epilogue,sans-serif;color:#9c9c95}}
@page cover{margin:0;@top-left{content:none}@top-right{content:none}@bottom-right{content:none}}
*{margin:0;padding:0;box-sizing:border-box}body{font:9.4pt/1.42 Epilogue,sans-serif;color:#161616;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.cover{page:cover;height:11in;background:#0c0c0c;color:#f6f5f1;padding:.9in .95in;display:flex;flex-direction:column;justify-content:flex-end;break-after:page}
.cover .k{font-size:7.5pt;letter-spacing:.3em;text-transform:uppercase;color:#a3a39c;font-weight:600;margin-bottom:14pt}
.cover h1{font:400 84pt/.9 Anton,sans-serif;text-transform:uppercase}.cover p.s{font:italic 18pt/1.3 Fraunces,serif;margin-top:16pt;max-width:5.8in}
.cover .own{margin-top:30pt;border-top:1px solid #2a2a28;padding-top:14pt;font-size:9pt;color:#a3a39c}.cover .own i{display:inline-block;width:3in;border-bottom:1px solid #6b6b65;margin-left:8pt}
.pg{break-before:page}.kick{font-size:7.5pt;font-weight:600;letter-spacing:.26em;text-transform:uppercase;color:#6b6b65;margin-bottom:5pt}
h2{font:400 26pt/1 Anton,sans-serif;text-transform:uppercase;color:#0c0c0c}h2 em{font:italic 400 .8em Fraunces,serif;text-transform:none}
.st{font:italic 11pt/1.35 Fraunces,serif;margin:5pt 0 10pt;padding-bottom:8pt;border-bottom:2px solid #0c0c0c}
.box{border:1.5px solid #0c0c0c;padding:7pt 10pt;margin:0 0 8pt;break-inside:avoid}.box>b,.fl{display:block;font-size:7pt;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:#6b6b65;margin-bottom:3pt}
.fl{margin:10pt 0 3pt}.box p{margin:2pt 0}.box.inv{background:#0c0c0c;color:#f6f5f1;border-color:#0c0c0c}.box.inv>b{color:#a3a39c}
.lines i{display:block;height:17pt;border-bottom:1px solid #cfcec8}.two{display:grid;grid-template-columns:1fr 1fr;gap:10pt}.three{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8pt}
ul.ck{list-style:none}ul.ck li{padding:3pt 0;border-bottom:1px solid #e2e1dc}ul.ck li::before{content:"\\25A1  ";color:#6b6b65}
ol.ls{list-style:none;margin:4pt 0 8pt}ol.ls li{display:grid;grid-template-columns:.5in 1fr;font-size:8.8pt;padding:2pt 0;border-bottom:1px solid #eeede8}ol.ls span{color:#9c9c95;font-family:Anton;font-size:8.5pt}ol.ls.col2{columns:2;column-gap:14pt}ol.ls.col2 li{break-inside:avoid}
table.g{width:100%;border-collapse:collapse;margin:2pt 0 8pt}.g th{font-size:6.8pt;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#6b6b65;text-align:left;padding:0 6pt 3pt 0;border-bottom:2px solid #0c0c0c}
.g td{border-bottom:1px solid #cfcec8;padding:4pt 6pt 4pt 0;height:17pt;vertical-align:top;font-size:9pt}.g.tick td{text-align:center}.g.tick td:first-child{text-align:left;font-weight:600}
.wk{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #0c0c0c;padding-bottom:6pt;margin-bottom:8pt}.wk h2{font-size:30pt}.wk .m{font-size:7.5pt;letter-spacing:.24em;text-transform:uppercase;color:#6b6b65;font-weight:600}
h3{font:400 14pt/1.1 Anton,sans-serif;text-transform:uppercase;margin:8pt 0 2pt}h3 small{font:italic 400 10pt Fraunces,serif;text-transform:none;color:#6b6b65;margin-left:8pt}
'''
out=['<section class="cover"><p class="k">The Method · The 90-Day Program</p><h1>Work<br>book</h1><p class="s">Every assignment, every week, in one place. Fill it in as you go. Bring it to the call.</p><div class="own">Name <i></i><br><br>Start date <i></i></div></section>']
# How to use
out.append('<section><p class="kick">Before you start</p><h2>How to use this</h2><p class="st">One course a week. Watch the lessons, do the assignment on these pages, post it in the community, bring your question to the live call.</p>'
+'<div class="two">'+box("The weekly rhythm","<p><b>Monday</b> — write your target for the week and the one number you're moving.</p><p><b>The live call</b> — thirty minutes of teaching, thirty minutes of your questions.</p><p><b>Friday</b> — write your wins and your misses. Both count.</p>")
+box("The rules","<p>Show your work. Ask specific questions. What's shared here stays here. No pitching. Do the assignments — that's where the results are.</p>")+'</div>'
+'<p class="fl">The 90 days at a glance</p><table class="g"><tr><th>Week</th><th>Move</th><th>Course</th><th>Done</th></tr>'+"".join(f'<tr><td><b>{w}</b></td><td>{mv}</td><td>{E(c)}</td><td>□</td></tr>' for w,mv,c,t in d["weeks"])+'</table></section>')
# Your stage / target
st=d["stages"]
out.append('<section class="pg"><p class="kick">Course 00 · Week 1</p><h2>Your stage, your target, <em>your date.</em></h2><p class="st">Most people are one stage behind where they think they are. Be honest — it\'s the fastest way through.</p>'
+'<p class="fl">1 · Find your stage — tick one</p><ul class="ck">'+"".join(f'<li><b>Stage {s[0]} — {E(s[1])}.</b> {E(s[2])}</li>' for s in st)+'</ul>'
+'<div class="two">'+box("2 · The target","<p>Monthly revenue: $__________</p><p>By (date): __________</p><p>Hours a week I want to work: ______</p>")+box("3 · The life it pays for","<p>What the money is actually for:</p>"+lines(4))+'</div>'
+box("4 · Post it","<p>Post your stage, your target and your date in the community. Posted on: __________</p>")
+'<p class="fl">Your first seven days</p><ul class="ck"><li>Watch Course 00 (under an hour)</li><li>Post your stage, target and date</li><li>Introduce yourself in the community — what you do, where you are</li><li>Write your daily standard (Course 01) and start it tomorrow</li><li>Put the weekly live call in your calendar for all 12 weeks</li><li>Download the Vault and print this workbook</li><li>Show up to your first live call with one real question</li></ul></section>')
# Weekly pages
for w,cs in WEEKS:
    head=f'<div class="wk"><div><p class="kick">Week {w} · {MOVE(w)} · Days {(int(w)-1)*7+1}–{min(int(w)*7,90)}</p><h2>'+" + ".join(f"{n} {E(courses[n]['h'])}" for n in cs)+f'</h2></div><div class="m">Week {w} of 12</div></div>'
    body=box("Monday — this week's target","<p>The one number I'm moving: ____________________ &nbsp; from ______ to ______</p>")
    for n in cs:
        c=courses[n]
        body+=f'<h3>Course {n} — {E(c["h"])}<small>{E(c["st"])}</small></h3><p><b class="fl" style="display:inline;margin:0 6pt 0 0">You leave with</b>{E(c["out"])}</p><ol class="ls{" col2" if len(cs)>1 else ""}">'+"".join(f'<li><span>{E(a)}</span><div>□ <b>{E(b)}</b></div></li>' for a,b,s in c["lessons"])+'</ol>'
        v=vault_by_course.get(n,[])+[t for t,cl in c["vault"] if cl=="on"]
        body+=box(f"Assignment — Course {n}",f'<p><b>{E(c["doThis"])}</b></p>'+(f'<p class="fl" style="margin:4pt 0 2pt">Use from the Vault: {E(", ".join(dict.fromkeys(v)))}</p>' if v else "")+lines(5 if len(cs)==1 else 2))
    body+=('<div class="two">'+box("Friday — wins","")+box("Friday — misses","")+'</div>') if len(cs)==1 else ('<div class="three">'+box("Friday — wins","")+box("Friday — misses","")+box("My question for the call","")+'</div>')
    body+='<p class="fl">Rich · Fit · Sick — tick every day</p><table class="g tick"><tr><th></th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr>'+"".join(f'<tr><td>{r}</td>'+'<td>□</td>'*7+'</tr>' for r in ["Train","Read","Deep work block","One sales action"])+'</table>'
    if len(cs)==1: body+=box("My question for the live call","")
    out.append(f'<section class="pg">{head}{body}</section>')
# 90-day review
out.append('<section class="pg"><p class="kick">Day 90</p><h2>The review.</h2><p class="st">Put the day-one numbers next to the day-ninety numbers. Then write the next ninety.</p>'
+'<table class="g"><tr><th></th><th>Day 1</th><th>Day 90</th></tr>'+"".join(f'<tr><td><b>{r}</b></td><td></td><td></td></tr>' for r in ["Monthly revenue","Clients","Margin %","Team (people)","Hours I work a week","Stage (0–4)","Conversations a week","Roles I\'ve handed off"])+'</table>'
+'<div class="two">'+box("What worked",lines(5))+box("What I\'d do differently",lines(5))+'</div>'
+box("The next 90 days — one constraint, one move","<p>Constraint:</p>"+lines(1)+"<p>The move:</p>"+lines(2))
+box("The life","<p>The first trip is on the calendar for: ____________</p>","inv")+'</section>')
open("workbook.html","w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>The Method — Workbook</title><style>{fonts}</style><style>{css}</style></head><body>{"".join(out)}</body></html>')

# ---------- Weekly live call plan ----------
css2=css.replace("WORKBOOK","LIVE CALL PLAN")
out=['<section class="cover"><p class="k">The Method · The 90-Day Program</p><h1>The Live<br>Calls</h1><p class="s">Twelve weeks of calls. Thirty minutes of teaching, thirty minutes of questions. One page per call.</p></section>']
out.append('<section><p class="kick">How every call runs</p><h2>The format. <em>Same every week.</em></h2><table class="g"><tr><th>Time</th><th>Segment</th><th>What happens</th></tr>'
+''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a,b,c in [("0–5 min","Wins","Three members share a win from the week. Fast."),("5–35 min","Teaching","This week's course: the big idea, the three points, the mistake everyone makes."),("35–55 min","Questions","Members' questions on this week's assignment. Pull up their actual offer / list / numbers."),("55–60 min","The assignment","Restate what's due before next call. Name the Vault item. Who's posting what.")])+'</table>'
+box("Rules for the host","<p>Start on time. Record every call. Specific questions first (\"here's my offer, here's what's broken\") — vague ones last. One member hot-seat per call when there's time. End with the assignment, every time.")+'</section>')
for w,cs in WEEKS:
    c0=courses[cs[0]]; allc=[courses[n] for n in cs]
    head=f'<div class="wk"><div><p class="kick">Call {w} · {MOVE(w)}</p><h2>'+" + ".join(f"{n} {E(courses[n]['h'])}" for n in cs)+f'</h2></div><div class="m">Week {w}</div></div>'
    body=f'<p class="st">'+" ".join(E(c["st"]) for c in allc)+'</p>'
    body+=box("Teaching segment — 30 min","".join(f'<p><b>Course {c["n"]} — {E(c["h"])}.</b> Cover: '+"; ".join(E(b) for a,b,s in c["lessons"][:4])+".</p>" for c in allc)+'<p class="fl" style="margin:4pt 0 2pt">The three things to land</p>'+lines(3))
    body+=box("Questions to open with","<p>• Who did last week's assignment — show me.</p><p>• What got in the way?</p>"+"".join(f'<p>• Where are you stuck on: {E(c["doThis"].rstrip(".").lower())}?</p>' for c in allc))
    v=[]
    for c in allc: v+= vault_by_course.get(c["n"],[])+[t for t,cl in c["vault"] if cl=="on"]
    body+='<div class="two">'+box("This week's assignment","".join(f'<p><b>{E(c["doThis"])}</b></p>' for c in allc)+(f'<p>Vault: {E(", ".join(dict.fromkeys(v)))}</p>' if v else ""))+box("Hot seat / notes",lines(4))+'</div>'
    nxt=WEEKS[int(w)][1] if int(w)<12 else None
    body+=box("Close",("<p>Next week: Course "+" + ".join(f'{n} — {E(courses[n]["h"])}' for n in nxt)+". Watch the lessons before the call.</p>") if nxt else "<p>Day 90. Everyone posts their Day 1 vs Day 90 numbers. Book the review call.</p>")
    out.append(f'<section class="pg">{head}{body}</section>')
open("callplan.html","w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>The Method — Live Call Plan</title><style>{fonts}</style><style>{css2}</style></head><body>{"".join(out)}</body></html>')
print("ok")
