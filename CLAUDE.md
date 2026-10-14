# Working with James

James runs THOMAS® (real-estate photo/video + social media), SILENZIO (mentorship / coaching) and CAPITAL. Most work in these sessions is on his Airtable, **MASTER OS**, not code. He's often live on a call and sends short messages ("he needs to be in the pipeline", "master os") — act fast, keep replies short and simple (a few lines, no long lists), and ask only when it truly matters.

## MASTER OS — the source of truth

- Base: **MASTER OS (V57)** — `appgnA8q6KDPRqG17` — https://airtable.com/appgnA8q6KDPRqG17
- James works in its **interface**, not the raw tables. Sidebar pages: Overview, To-Do, Contacts & Prospects, **Sales & Deals → Deals Master**, Fulfillment, Finance, Contractors, Marketing, Social Media, Leasing, Operate, SILENZIO, CAPITAL.
- When James says "the pipeline", "deals", "sales" or "master" he means the **Deals** table (shown as Deals Master), for every company — THOMAS®, SILENZIO and CAPITAL alike.

### Adding someone to the pipeline = create a Deals record

Deals table `tblrmfHdTgDpugavY`. Fields to set:

| Field | ID | Notes |
|---|---|---|
| Title | `fldqbvgN6kHWRyl4h` | Person or deal name |
| Company (shown as "Co") | `fldSA1i0irzaQ7xej` | Link. SILENZIO = `recihFli0Ps6Crkc0`, THOMAS® = `recIOnp2zWdmNgOwp` |
| Sales Stage | `fld7FSDGSQtc0rqJI` | Opportunity → Negotiation → Closing → Closed → Closed/Fulfillment → Closed/Billing → Closed/Paid, or Lost |
| Product Line | `fldZcsjlf5FSCA4Xx` | SILENZIO leads = Mentorship; THOMAS® = Shoots / Social Media |
| Temp | `fldFfKuBMDYeNsnmv` | 🔥 Hot / 🌤 Warm / 🧊 Cold |
| Offer | `fldZKUZZXYiEP6Zm1` | e.g. Weekly 1:1 |
| Client | `fldtS6TdOcWdcVKIO` | Link to People |
| Deal Notes | `fldSRVxr7ZIKcOmBt` | Call notes, dated |
| Revenue | `fldhRzmUlgPcWU0v1` | |

Deal Name, Deal Stage (Unified), Heat, Deal Health etc. are formulas — don't write them.

### Gotchas (learned the hard way)

- **`SILENZIO Pipeline (sync)` is read-only** — it's synced in from the old base "DON'T USE — OS SILENZIO (v1.4)" (`appoheNdhEcsjIzIv`). **Never write to that old base.** New SILENZIO leads go in Deals with Co = SILENZIO.
- **People** (`tbl0OusBjmw8Gifd4`) has ~22.6k records and 154 fields — always pass `fieldIds` and filters; full pulls overflow. Its `Stage` mixes funnel stages with temperatures (Hot/Warm/Cold); `Status` is the temperature field.
- Deals has ~1.4k records; open pipeline (Opportunity/Negotiation/Closing) is ~100 deals.
- Meetings table `tblDfk9jUD2xaAd4g`. James's standing Google Meet link: https://meet.google.com/fsa-nbbx-tjh
- Other key tables: Companies `tblIk8qXYAdg1hcOb`, Students `tblMIrgkMaJmYaeht`, Fulfillment `tbl2QjzKP60oyofE5`, AR `tbl0SRNeFMNSgSDE5`, AP `tbldoE7aoc75NWEil`, Task `tblBGVvnDGkCmB9rv`.

## How to work

- **Dates:** the server clock can be a day ahead of James. Ask or infer his local date/time before writing dated notes. (Oct 2026: he's in Mexico.) Contractors never get the client's identity — scope notes use a working name (e.g. "The Loft" for Midtown Tampa).

- **Source of truth for any job/deal is Airtable: the Deals table + the Fulfillment pipeline.** Email, Polina's updates and chat are supporting context only — check and update the Deals/Fulfillment record first, and treat it as correct when sources disagree.
- Before creating a record, search first so you don't make duplicates.
- Do what's asked, then say in one or two lines what changed and where (table + stage), so James can find it in the interface.
- Confirm before deleting, bulk-editing, or sending anything (email, text, Stripe link) to another person.
- When something is learned about how James's system works, add it to this file.

## Fulfillment rules (THOMAS®)

- **Interface pages: grid views with filter dropdowns, not list views. Completed jobs sort newest first. Pages can't be renamed or reordered via the API — James drags them in the editor.**

- **Write the edit brief the moment a video job closes**, not after the shoot. Template: `the-method/TEMPLATE-edit-brief.md`. Fill it from the deal's Request Details, put the link in the job's Notes, and it goes to the editor with the footage the day the shoot wraps.
- **Fulfilment interface** (`pbdoHHbqWPBmtmRGy`) pages: **Shoots Fulfillment** (`pagSBuYja7bfuVE2E`, Fulfillment table, Workflow = Shoots, tabs Active/Editing, grouped by Stage) · **Master Fulfillment** (`pagNRnpvYYqS7Mw4A`, every non-shoot workflow — design, web, social, ads — with Stage / Co / Product Line dropdowns) · **Courses** (Students) · All Fulfilment · Schedule · Deadlines · the old Deals-based "Master Fulfilment". Fulfillment job field **🎬 Edit Brief** = `fldjTkFeKS0jUbs5q`.
- **Fulfillment stages, in order:** Possible → Need Scheduling → Scheduling → Scheduled → Shoot Complete (was "Shot") → **Uploading** (shot, waiting on the raw files) → Post-Production (was "Editing"; files are in, editor has them) → QC → Client Approval → Delivered → Complete (plus Reshoot / Cancelled). Select options can't be renamed or deleted via the API, so to "rename" one: create the new option by writing it to a record with typecast, move every record off the old option, and leave the old one for James to delete. **Do it yourself — never hand James a manual step when the API can get there.**
- Edits are outsourced. Set Editor of Record + Edit Due on the Fulfillment job when the editor is booked.

## The Method (SILENZIO's program) — the kit lives in `the-method/`

- The Method is a **90-day program** (not six months): 3 moves (Money In · The Machine · Step Out), 12 weeks, 15 courses (00–14), 105 lessons, 8 tracks. `the-method/README.md` lists every document and the week-by-week schedule.
- Editable masters: `the-method/The-Method-90-Day-Outline.md` and `the-method/source/program.json`. All PDFs are rebuilt from `the-method/source/*.html` with `node source/topdf.js in.html out.pdf` (Playwright; embed Google Fonts as base64 — the proxy blocks fonts.googleapis.com from Chromium).
- Brand look: black/off-white, Anton (display, uppercase) · Fraunces italic (subheads) · Epilogue (body). US Letter.
- When James asks for "the method" documents, he means the whole kit: one-pager → program → outline → lesson guide → call plan → workbook → Vault. Deliver all of it without being asked item by item.
- Never invent facts about James's results or stories; use `[STORY: …]` placeholders.
