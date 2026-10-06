# The Method — the complete kit

Everything for James Thomas's 90-day program, generated from one source of truth (the curriculum). All PDFs are US Letter with the fonts embedded.

| # | Item | File | Who it's for |
|---|------|------|--------------|
| 1 | **The Method — one-pager** | `pdf/The-Method-One-Pager.pdf` | Anyone who asks "what do you do?" Send it as-is. |
| 2 | **The 90-Day Program** (the main course) | `pdf/The-Method-90-Day-Program.pdf` | Members. The full curriculum: 3 moves, 12 weeks, 15 courses, 105 lessons, 8 tracks, the Vault, the rules. |
| 3 | **Course outline** | `pdf/The-Method-90-Day-Outline.pdf` · `The-Method-90-Day-Outline.md` | Quick-reference structure of the whole program. The `.md` is the editable master. |
| 4 | **Lesson Guide** | `pdf/The-Method-Lesson-Guide.pdf` | James. Teaching notes for all 105 lessons: big idea, talking points, story prompt, action, assignment walkthrough. |
| 5 | **Live Call Plan** | `pdf/The-Method-Live-Call-Plan.pdf` | James. One page per weekly call (12), same format every week. |
| 6 | **Workbook** | `pdf/The-Method-Workbook.pdf` | Members. One page per week: assignment, Monday target, Friday wins/misses, Rich·Fit·Sick tracker, Day-90 review. |
| 7 | **The Vault** | `pdf/The-Method-Vault.pdf` + `pdf/vault/*.pdf` | Members. All 15 templates as one pack and as separate files. |

## The Vault (15)
01 Daily Standard Tracker · 02 Service Picker Worksheet · 03 One-Page Offer Template · 04 Offer Worksheet · 05 Outreach Script Pack · 06 Discovery Call Script · 07 Objection Sheet · 08 Time Audit Sheet · 09 Job Post + Paid Trial Template · 10 SOP Template · 11 CRM Template · 12 Weekly Meeting Agenda · 13 Revenue Target Calculator · 14 Replacement Map · 15 90-Day Scale Plan

Existing guides referenced but not in this repo (already written): The AI-Proof Creative · Why Your Property's Social Isn't Producing Leads · 5 AI Prompts for CRE Marketing · The Recurring Client Playbook · Grove Central White Paper · Proposal Template.

## The 12 weeks
| Week | Move | Course |
|---|---|---|
| 1 | Money In | 00 Start Here + 01 The Standard |
| 2 | Money In | 03 The Offer & Pricing (02 Start From Zero first if no business yet) |
| 3 | Money In | 04 Marketing & Lead Generation |
| 4 | Money In | 05 Sales |
| 5 | The Machine | 06 Delivery & Client Experience |
| 6 | The Machine | 07 Buy Back Your Time |
| 7 | The Machine | 08 Recruiting & Hiring |
| 8 | The Machine | 09 Delegation & Systems |
| 9 | Step Out | 10 Leadership & Managing a Team |
| 10 | Step Out | 11 Money |
| 11 | Step Out | 12 Get Out of the Work |
| 12 | Step Out | 13 Scale + 14 The Life |

## Still for James to do
- Fill the `[STORY: …]` prompts in the Lesson Guide with your own stories (they're placeholders on purpose — nothing was invented).
- Decide on price and whether it goes on the one-pager (currently: no price, "book a call", calendly.com/thomaspros).
- Record the 105 lessons from the Lesson Guide.

## Rebuilding
`source/` has the HTML for every document plus the scripts. Render any HTML to PDF with `node source/topdf.js in.html out.pdf` (needs Playwright + Chromium). Edit `The-Method-90-Day-Outline.md` / `source/program.json` for content changes.
