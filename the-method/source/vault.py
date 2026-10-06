import re, html, json
fonts=re.search(r"<style>(\s*(?:/\*[^*]*\*/\s*)?@font-face.*?)</style>", open("method-90.html").read(), re.S).group(1)
def lines(n, label=""):
    return (f'<p class="fl">{label}</p>' if label else "")+'<div class="lines">'+'<i></i>'*n+'</div>'
def table(heads, rows=0, data=None, widths=None, cls=""):
    w = widths or [None]*len(heads)
    th="".join(f'<th{f" style=width:{x}" if x else ""}>{h}</th>' for h,x in zip(heads,w))
    body=""
    if data: body+="".join("<tr>"+"".join(f"<td>{c}</td>" for c in r)+"</tr>" for r in data)
    body+=("<tr>"+"<td></td>"*len(heads)+"</tr>")*rows
    return f'<table class="g {cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'
def box(t, body): return f'<div class="box"><b>{t}</b>{body}</div>'
def steps(*a): return '<ol class="steps">'+"".join(f"<li>{x}</li>" for x in a)+"</ol>"
def script(t, body): return f'<div class="scr"><b>{t}</b><p>{body}</p></div>'
A=[]
def asset(slug, course, title, use, body): A.append((slug,course,title,use,body))

# 1 Daily Standard
asset("daily-standard-tracker","Course 01 · The Standard","Daily Standard Tracker",
"Write your standard. Hold it for 14 days. Tick it every night — no partial credit.",
box("My standard","<p>Every day, no matter what:</p>")+lines(4)+
'<p class="fl">The 14 days</p>'+table(["Day","Date","Train","Read","Deep work block","One sales action","Notes"],0,[[str(i),"","□","□","□","□",""] for i in range(1,15)],[".4in",".8in",".55in",".55in","1in","1.05in",None],"tick")+
'<div class="two">'+box("What I'm reading","")+box("Score","<p>Days held: ____ / 14</p><p>What broke the streak, and the fix:</p>")+'</div>')
# 2 Service picker
asset("service-picker-worksheet","Course 02 · Start From Zero","Service Picker Worksheet",
"Pick the service you'll sell first. Not the one you love most — the one people already pay for, that you can sell, and someone else can do.",
steps("List five services you could sell. Things businesses already pay for.","Score each 1–5 on the five tests. Be honest.","Pick the highest total. If it's a tie, pick the one you can sell this week.")+
table(["Service","People already pay for it","I can sell it","Someone else can deliver it","It can be recurring","I know who buys it","Total /25"],5,None,["1.5in"]+[None]*6,"tall")+
box("My pick","<p>The service:</p>"+lines(1)+"<p>Who buys it:</p>"+lines(1)+"<p>What it gets them (the outcome, not the task):</p>"+lines(2))+
box("Ten people I'll talk to this week","")+table(["#","Name","How I know them","Booked?"],0,[[str(i),"","",""] for i in range(1,11)],[".3in","2in",None,".8in"]))
# 3 One-page offer template
asset("one-page-offer-template","Course 02 · Start From Zero","One-Page Offer Template",
"The one page you send after a conversation. Fill every box. If it doesn't fit on one page, it isn't clear yet.",
box("Headline — the outcome in one line","<p class='ex'>e.g. “More leases from the same building — in 30 days.”</p>"+lines(1))+
'<div class="two">'+box("Who it's for",lines(3))+box("The problem it solves",lines(3))+'</div>'+
box("What you get",lines(5))+
'<div class="two">'+box("How it works — 3 steps",'<p>1.</p>'+lines(1)+'<p>2.</p>'+lines(1)+'<p>3.</p>'+lines(1))+box("Proof","<p>A result, a client, a number:</p>"+lines(4))+'</div>'+
'<div class="two">'+box("The price","<p>Per month / per project:</p>"+lines(1)+"<p>Term:</p>"+lines(1))+box("The guarantee",lines(3))+'</div>'+
box("Next step","<p class='ex'>e.g. “Reply yes and I'll send the payment link. We start Monday.”</p>"+lines(1)))
# 4 Offer worksheet
asset("offer-worksheet","Course 03 · The Offer & Pricing","Offer Worksheet",
"Nobody buys a shoot, a clean or a consult. They buy what it gets them. Build the offer from the outcome back.",
box("1 · The value equation","<p>Value goes up with the first two and down with the last two. Make each one better.</p>")+
table(["","Today","How I make it better"],0,[["<b>Dream outcome</b> — what they actually want","",""],["<b>Proof</b> — why they believe you'll get it","",""],["<b>Speed</b> — how fast they see it","",""],["<b>Effort</b> — how little they have to do","",""]],["2.2in",None,None],"tall")+
box("2 · The offer in one sentence","<p class='ex'>I help [who] get [outcome] in [time] without [the thing they hate].</p>"+lines(2))+
'<p class="fl">3 · Three packages</p>'+table(["","Starter","Core (the one most people buy)","Premium"],0,[["Name","","",""],["What's included","<br><br><br>","",""],["Price","","",""],["Term / recurring?","","",""]],["1.3in",None,None,None],"tall")+
'<div class="two">'+box("4 · The guarantee",lines(3))+box("5 · Why it's recurring","<p>What do they need from you every month?</p>"+lines(2))+'</div>')
# 5 Outreach script pack
asset("outreach-script-pack","Course 04 · Marketing & Lead Generation","Outreach Script Pack",
"Short, human, specific. One reason you're reaching out, one question. Never sound like a template — even when it is one.",
script("Cold email","<b>Subject:</b> {first name}, quick question<br><br>Hey {first name} — I saw {one specific thing: their listing, post, building, project}. {One line on what you noticed}.<br><br>We help {who they are} get {outcome} — {one proof point}.<br><br>Worth a 15-minute call this week?<br><br>{Your name}")+
script("DM (Instagram / Facebook)","Hey {first name} — {genuine one-line compliment on something specific}. Quick one: are you handling {the thing you solve} yourself right now, or do you have someone on it?")+
script("Cold call opener","Hey {first name}, it's {name} — I know I'm calling out of the blue, can I take 30 seconds and you tell me if it's worth keeping going?<br><br>We work with {who} who are {the pain}. Usually it's {problem A} or {problem B}. Is either of those true for you?")+
script("LinkedIn connection note","{First name} — saw your work at {company}. I work with {who} on {outcome}. Would be good to be connected.")+
script("Referral / win-back","Hey {first name} — it's been a while since {the job we did}. Two things: how's {their thing} going, and who do you know that could use {outcome}? I'll take great care of them.")+
'<p class="fl">The follow-up cadence — most deals close after the fifth touch</p>'+
table(["Touch","When","Channel","What to say"],0,[["1","Day 1","Email or DM","The first message"],["2","Day 3","Call","“Following up on my note — got 2 minutes?”"],["3","Day 6","Email","Something useful: a result, an idea, a short audit"],["4","Day 10","DM / text","One line: “Still worth a chat?”"],["5","Day 17","Email","The breakup: “Should I close your file?”"]],[".5in",".7in","1.1in",None]))
# 6 Discovery call script
asset("discovery-call-script","Course 05 · Sales","Discovery Call Script",
"Your job on this call is to find the real problem — not to pitch. Ask, listen, write it down. Talk 30% of the time.",
script("1 · Open (2 min)","Thanks for making the time. Here's how I'd like to use the next 30 minutes: I'll ask some questions to understand where you are, and if I think we can help, I'll tell you exactly how. If not, I'll tell you that too. Sound good?")+
'<p class="fl">2 · Where they are now (10 min)</p>'+table(["Question","Their answer"],0,[["Tell me about the business — what do you sell, and to who?",""],["What's working right now?",""],["What's not? What made you take this call?",""],["What have you already tried?",""],["What does it cost you if nothing changes in the next 6 months?",""]],["2.9in",None],"tall")+
'<p class="fl">3 · Where they want to be (5 min)</p>'+table(["Question","Their answer"],0,[["If we were sitting here 90 days from now, what has to have happened for you to be happy?",""],["Why does that matter to you — personally?",""],["What's stopping you from getting there on your own?",""]],["2.9in",None],"tall")+
script("4 · Present (5 min)","Here's what I'd do. {Restate their problem in their words}. {Your offer, in one sentence}. {The three steps}. The investment is {price}. — then stop talking.")+
script("5 · Close","Does that sound like what you need? … Great — I'll take the payment now and we start {day}.<br>If they hesitate: “What's the one thing that would stop you?” → go to the Objection Sheet."))
# 7 Objection sheet
asset("objection-sheet","Course 05 · Sales","Objection Sheet",
"An objection is a question you haven't answered yet. Agree, ask, answer, close. Log every one you hear — the same five come back again and again.",
table(["They say","What it usually means","What to say"],0,[
["“It's too expensive.”","They don't see the value yet, or it's the wrong package.","“Compared to what?” … “If it gets you {outcome}, what's that worth to you over a year?” Then offer the smaller package — never a discount on the same one."],
["“Now's not a good time.”","It's not a priority, or something else is going on.","“What would need to be different for it to be the right time?” … “What does waiting 90 days cost you?”"],
["“Let me think about it.”","There's a question they haven't asked.","“Of course. What specifically do you want to think through? Let's do it now while I'm here.”"],
["“I need to ask my partner.”","Real, or a polite no.","“Makes sense. What do you think they'll say? … What questions will they have? Let's get them on a call together this week.”"],
["“Send me some info.”","A brush-off.","“Happy to. So I send the right thing — what's the one thing you'd want to see in it?” Then book the follow-up on the spot."],
["“We already have someone.”","Maybe happy, maybe not.","“Good. What would you change about how it's going?” … “Would it be worth seeing what a second option looks like?”"]],["1.35in","1.6in",None],"tall")+
'<p class="fl">My objection log</p>'+table(["Date","Who","What they said","What I said","Closed?"],7,None,[".7in","1.1in",None,None,".6in"]))
# 8 Time audit
asset("time-audit-sheet","Course 07 · Buy Back Your Time","Time Audit Sheet",
"Track every task for one full week. Then mark each one: only I can do it, someone else could, or nobody should.",
box("What my hour is worth","<p>Monthly target income ÷ hours I want to work a month = <b>$______ / hour</b>. Anything I can pay someone less than this to do, I should.</p>")+
table(["Day","Task","Time","Energy (+/−)","Me / Hand off / Kill"],16,None,[".55in",None,".6in",".8in","1.3in"])+
'<div class="two">'+box("Top 3 tasks to hand off","<p>1.</p>"+lines(1)+"<p>2.</p>"+lines(1)+"<p>3.</p>"+lines(1))+box("The only things I should be doing",lines(5))+'</div>')
# 9 Job post + paid trial
asset("job-post-paid-trial-template","Course 08 · Recruiting & Hiring","Job Post + Paid Trial Template",
"Test the work before you commit. Everyone does a small, paid trial. Hire slow, let go fast.",
box("The job post",
"<p><b>Title:</b> {Role} — {remote / city}, {contract / full-time}</p>"
"<p><b>Who we are:</b> One line on the company and what you do for clients.</p>"
"<p><b>What you'll do:</b> 3–5 bullets of real outcomes, not duties.</p>"
"<p><b>You're great at this if:</b> 3–4 bullets — skills, standard, attitude.</p>"
"<p><b>Pay:</b> {range}, paid {how}.</p>"
"<p><b>To apply:</b> Send {portfolio / 2-minute video} and answer: “{one specific question that proves they read it}.” Applications without the answer aren't read.</p>")+
'<p class="fl">The paid trial</p>'+table(["","Fill in"],0,[["The trial task — real work, 2–4 hours",""],["What great looks like",""],["Pay for the trial",""],["Deadline",""]],["2.2in",None],"tall")+
'<p class="fl">Scorecard — score every candidate the same way (1–5)</p>'+table(["Candidate","Quality of work","Followed instructions","Speed","Communication","Attitude","Total /25"],4,None,["1.5in"]+[None]*6)+
box("After the hire","<p>□ Agreement / NDA signed &nbsp; □ W-9 / payment details &nbsp; □ Access given (only what they need) &nbsp; □ SOPs sent &nbsp; □ First check-in booked</p>"))
# 10 SOP template
asset("sop-template","Course 09 · Delegation & Systems","SOP Template",
"Record yourself doing it once. Turn the recording into steps. If someone new can't do it from this page, it isn't finished.",
table(["","Fill in"],0,[["SOP name",""],["Owner (role, not person)",""],["When it runs (trigger / frequency)",""],["Time it takes",""],["Tools / logins needed",""],["Video walkthrough link",""]],["2.1in",None])+
box("What done looks like","<p>The standard — how we know it was done right:</p>"+lines(2))+
'<p class="fl">The steps</p>'+table(["#","Step","Notes / screenshot"],10,None,[".35in","3.4in",None])+
'<div class="two">'+box("Common mistakes",lines(3))+box("If something goes wrong, ask",lines(1)+"<p>Last updated: ________ by ________</p>")+'</div>')
# 11 CRM template
asset("crm-template","Course 09 · Delegation & Systems","CRM Template",
"One place for every lead, client, job and dollar. This is the setup we run our agency on — build it in Airtable, a spreadsheet or any CRM.",
'<p class="fl">The five tables</p>'+table(["Table","One row per","Key fields"],0,[
["<b>People</b>","Person","Name · email · phone · company · source · status (Cold / Warm / Hot) · last touched · next touch date"],
["<b>Companies</b>","Business","Name · website · type · people · deals · lifetime revenue"],
["<b>Deals</b> (the pipeline)","Opportunity","Title · client · company · stage · value · product line · next action + due date · notes"],
["<b>Jobs</b> (delivery)","Piece of work","Deal · stage · due date · who's doing it · cost · delivered link · approved?"],
["<b>Invoices</b>","Bill","Deal · amount · sent date · due date · paid date · status"]],["1.3in","1in",None],"tall")+
'<p class="fl">Pipeline stages</p>'+table(["Stage","Means","Move it when"],0,[["New / Prospect","On the list, not contacted","You reach out"],["Qualifying","Talking, not sure they fit","They agree to a call"],["Opportunity","Real need, call booked or held","You've sent the offer"],["Negotiation","Discussing price / scope","They say yes"],["Closing","Yes — waiting on payment / signature","Money's in"],["Closed","Paid — job starts","Job moves to delivery"],["Lost","Not now — note why","—"]],["1.2in","2.3in",None])+
box("The rules","<p>Every deal has a next action and a date. Every call gets a one-line note the same day. Check the pipeline every Monday — anything with no next action is dead until you give it one.</p>"))
# 12 Weekly meeting agenda
asset("weekly-meeting-agenda","Course 10 · Leadership & Managing a Team","Weekly Meeting Agenda",
"Same day, same time, same agenda, every week. 45 minutes. Start on time, end on time.",
table(["Time","Section","What happens"],0,[["5 min","Wins","Everyone shares one win from the week. Business or personal."],["10 min","Scoreboard","Each number: on track or off track. No discussion yet — just the number."],["5 min","Last week's commitments","Done or not done. No stories."],["20 min","Issues","List them, pick the top three, solve them. Every solution becomes a commitment with an owner and a date."],["5 min","Commitments + close","Read back who's doing what by when. Rate the meeting 1–10."]],[".7in","1.5in",None],"tall")+
'<p class="fl">Scoreboard</p>'+table(["Number","Owner","Goal","This week","On / off track"],6,None,["2in",None,None,None,None])+
'<p class="fl">Commitments</p>'+table(["Who","Will do what","By when","Done?"],6,None,["1.1in",None,".9in",".6in"]))
# 13 Revenue target calculator
asset("revenue-target-calculator","Course 11 · Money","Revenue Target Calculator",
"Work it backwards. The monthly number turns into a weekly number of conversations. That's the only number you manage.",
table(["","Step","Example","Mine"],0,[
["A","Monthly revenue target","$30,000",""],
["B","Average price per client per month","$3,000",""],
["C","Clients needed (A ÷ B)","10",""],
["D","Clients you already have","4",""],
["E","New clients needed (C − D)","6",""],
["F","Months to get there","3",""],
["G","New clients per month (E ÷ F)","2",""],
["H","Close rate on calls (closed ÷ calls)","25%",""],
["I","Calls needed per month (G ÷ H)","8",""],
["J","Show-up / booking rate (calls ÷ conversations)","20%",""],
["K","Conversations per month (I ÷ J)","40",""],
["L","<b>Conversations per week (K ÷ 4)</b>","<b>10</b>",""]],[".3in","3in","1in",None])+
box("My weekly number","<p>To hit my target I need <b>____ conversations a week</b>, which means reaching out to <b>____ people a week</b>.</p>")+
'<p class="fl">Track it</p>'+table(["Week","Conversations","Calls","Closed","Revenue added"],6))
# 14 Replacement map
asset("replacement-map","Course 12 · Get Out of the Work","Replacement Map",
"Every role you play, and who takes it. Step out of delivery first, then sales, then management.",
table(["Role I play","Hours / week","Who takes it (or hire)","SOP written?","Handoff date","Done"],0,[
["Doing the work (delivery)","","","","",""],["Quality control","","","","",""],["Client communication","","","","",""],["Finding leads","","","","",""],["Sales calls","","","","",""],["Invoicing / chasing money","","","","",""],["Hiring","","","","",""],["Managing the team","","","","",""],["Admin / bookkeeping","","","","",""],["","","","","",""],["","","","","",""]],["1.8in",".7in","1.5in",".7in",".8in",".45in"],"tall")+
'<div class="two">'+box("The order","<p><b>1. The work</b> — goes first.<br><b>2. The selling</b> — train someone to sell it like you.<br><b>3. The hiring</b> — they find the people.<br><b>4. The operation</b> — a manager runs the day.</p>")+box("What I keep","<p>The roles only the owner does:</p>"+lines(3))+'</div>'+
box("This month, I hand off",lines(2)))
# 15 90-day scale plan
asset("90-day-scale-plan","Course 13 · Scale","90-Day Scale Plan",
"There is always one constraint. Find it, pick the one move that breaks it, and do only that for 90 days.",
'<div class="two">'+box("Where I am","<p>Monthly revenue: $______<br>Clients: ______<br>Margin: ______%<br>Team: ______</p>")+box("Where I'll be in 90 days","<p>Monthly revenue: $______<br>Clients: ______<br>Margin: ______%<br>Team: ______</p>")+'</div>'+
box("The one constraint","<p>Circle one: Leads · Sales · Delivery · Team · Cash · Me</p><p>Why I know it's this one:</p>"+lines(2))+
box("The lever","<p>Circle one: More clients · Bigger clients · More per client</p>")+
box("The one move",lines(2))+
'<p class="fl">The 90 days</p>'+table(["","Milestone","Measured by","Owner"],0,[["Days 1–30","","",""],["Days 31–60","","",""],["Days 61–90","","",""]],["1in",None,None,"1.1in"],"tall")+
box("What I'm saying no to for 90 days",lines(2)))

css='''
@page{size:Letter;margin:.6in .75in .65in;
 @top-left{content:"THE METHOD  \\00B7  THE VAULT";font:7pt Epilogue,sans-serif;letter-spacing:.18em;color:#9c9c95}
 @top-right{content:"JAMES THOMAS";font:7pt Epilogue,sans-serif;letter-spacing:.18em;color:#9c9c95}
 @bottom-right{content:counter(page);font:8pt Epilogue,sans-serif;color:#9c9c95}}
@page cover{margin:0;@top-left{content:none}@top-right{content:none}@bottom-right{content:none}}
*{margin:0;padding:0;box-sizing:border-box}
body{font:9.3pt/1.4 Epilogue,sans-serif;color:#161616;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.cover{page:cover;height:11in;background:#0c0c0c;color:#f6f5f1;padding:.9in .95in;display:flex;flex-direction:column;justify-content:flex-end;break-after:page}
.cover .k{font-size:7.5pt;letter-spacing:.3em;text-transform:uppercase;color:#a3a39c;font-weight:600;margin-bottom:14pt}
.cover h1{font:400 92pt/.9 Anton,sans-serif;text-transform:uppercase}
.cover p.s{font:italic 18pt/1.3 Fraunces,serif;margin-top:16pt;max-width:5.8in}
.cover ol{margin-top:26pt;border-top:1px solid #2a2a28;columns:2;column-gap:24pt;list-style:none;padding-top:10pt}
.cover li{font-size:9pt;padding:3pt 0;color:#d8d8d2;break-inside:avoid}.cover li span{color:#a3a39c;font-size:7.5pt;letter-spacing:.14em;text-transform:uppercase;display:block}
.asset{break-before:page}
.asset.first{break-before:auto}
.kick{font-size:7.5pt;font-weight:600;letter-spacing:.26em;text-transform:uppercase;color:#6b6b65;margin-bottom:6pt}
h2{font:400 28pt/1 Anton,sans-serif;text-transform:uppercase;color:#0c0c0c}
.use{font:italic 11pt/1.35 Fraunces,serif;margin:6pt 0 10pt;padding-bottom:8pt;border-bottom:2px solid #0c0c0c}
.box{border:1.5px solid #0c0c0c;padding:8pt 10pt;margin:0 0 8pt;break-inside:avoid}
.box>b,.fl{display:block;font-size:7pt;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:#6b6b65;margin-bottom:4pt}
.fl{margin:12pt 0 4pt}
.box p{margin:2pt 0}.ex{color:#6b6b65;font-size:8.6pt}
.lines i{display:block;height:17pt;border-bottom:1px solid #cfcec8}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12pt}.two .box{margin-bottom:10pt}
table.g{width:100%;border-collapse:collapse;margin:2pt 0 10pt;break-inside:auto}
.g th{font-size:6.8pt;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#6b6b65;text-align:left;padding:0 6pt 4pt 0;border-bottom:2px solid #0c0c0c;vertical-align:bottom}
.g td{border-bottom:1px solid #cfcec8;padding:4pt 6pt 4pt 0;height:17pt;vertical-align:top;font-size:9pt}
.g tr{break-inside:avoid}
.g.tall td{height:25pt}
.g.tick td{text-align:center;height:18pt}.g.tick td:first-child,.g.tick td:nth-child(2),.g.tick td:last-child{text-align:left}
.steps{margin:0 0 10pt 16pt}.steps li{margin:2pt 0}
.scr{border-left:3px solid #0c0c0c;padding:2pt 0 2pt 12pt;margin:0 0 8pt;break-inside:avoid}
.scr b{display:block;font:400 11.5pt Anton,sans-serif;text-transform:uppercase;color:#0c0c0c;margin-bottom:2pt}
.scr p{font-size:9.4pt}
'''
def page(items, cover=True):
    out=[]
    if cover:
        out.append('<section class="cover"><p class="k">The Method · The 90-Day Program</p><h1>The<br>Vault</h1><p class="s">The templates, scripts and worksheets that go with every course. Print them. Fill them in. Bring them to the call.</p><ol>'+"".join(f'<li><span>{html.escape(c)}</span>{html.escape(t)}</li>' for s,c,t,u,b in items)+'</ol></section>')
    for i,(s,c,t,u,b) in enumerate(items):
        out.append(f'<section class="asset{" first" if (i==0 and not cover) else ""}"><p class="kick">The Vault · {html.escape(c)}</p><h2>{html.escape(t)}</h2><p class="use">{u}</p>{b}</section>')
    return f'<!doctype html><html><head><meta charset="utf-8"><title>The Method — The Vault</title><style>{fonts}</style><style>{css}</style></head><body>{"".join(out)}</body></html>'
import os
os.makedirs("vault",exist_ok=True)
open("vault/_pack.html","w").write(page(A))
for i,a in enumerate(A,1):
    open(f"vault/{i:02d}-{a[0]}.html","w").write(page([a],cover=False))
json.dump([[a[0],a[1],a[2]] for a in A],open("vault/index.json","w"))
print(len(A))
