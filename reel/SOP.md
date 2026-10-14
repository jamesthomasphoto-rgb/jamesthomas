# REEL — In-house video editing: the system

One operator (Claude, as REEL) turns raw footage + renders into a delivered property video, inside the 48-hour SLA, without an outside editor for the standard deliverable. Outside editors stay on the bench for the hero pass and as overflow. James approves money and the final send; REEL owns the edit and the quality bar.

**Governing rule: below bar = redo on us. Never ship it.** A late-but-right cut beats an on-time miss. If a redo threatens the committed date, flag James early — don't ship the miss.

## Where things live

| What | Where |
|---|---|
| Source of truth for the job | Airtable **Fulfillment** `tbl2QjzKP60oyofE5` — one record per job |
| The brief | job's **🎬 Edit Brief** (`fldjTkFeKS0jUbs5q`), written the day the deal closes from `the-method/TEMPLATE-edit-brief.md` |
| Footage / renders in | **Raw Footage Link** `fldQdzkYtLwN9o794` (Dropbox/Drive/Box the shooter or client sent) |
| Working files | `reel/jobs/<Job>/` — `BRIEF.md`, `job.json`, `map.json`, `media/` (not in git) |
| Renders | `reel/out/<Job>/` — `<job>_16x9.mp4`, `<job>_9x16.mp4`, `_sheet.jpg`, `_QC.md`, `manifest.json` (not in git) |
| Delivered file | uploaded to the job's Drive folder → link in **Final Video** `fldW4cXcw4dS7WFTU` |
| Engine | `reel/engine/autoedit.py` (cut) · `maps.py` (location map) · `qc.py` (gate) · `brief2job.py` (brief → timeline) |

## Stages (Fulfillment → Product Stage) and what REEL does at each

| Stage | Trigger | REEL does | Clock |
|---|---|---|---|
| **Shoot Complete** | shooter wraps | Nothing yet. Brief already exists (written at close). | — |
| **Uploading** | waiting on raws | Chase the shooter once if raws aren't in by 9 AM next day (James by phone — never a text from Claude). | — |
| **Post-Production** | raws land → set **Raw Footage Link** | 1. `brief2job.py` → `reel/jobs/<Job>/job.json` 2. pull media into `media/` 3. `--preview` render, eyeball the contact sheet 4. fix order/timing/grade in `job.json` 5. full render 16:9 + 9:16 | first cut ≤ 24 h after raws in |
| **QC** | render passes machine QC | Watch 100% end to end. Run `QC-CHECKLIST.md`. Set **QC Status** → Passed / Failed (+ shot-level notes in **Revision Notes**). Failed → fix and re-render, never ship. | same day |
| **Client Approval** | James ticks **James Approved** | Upload final to the job's Drive folder → **Final Video**. Stage the delivery email as a draft (James's voice, no mention of tools/AI/contractors). James sends. | ≤ 48 h after raws in |
| **Delivered** | email sent | Stamp **Delivery Date**, **Quality Score** (1–5, 5 = shipped as first cut), **Revision #**. | — |
| **Complete** | client confirms / no revision in 5 days | Close. | — |

**Revisions** (client comes back): lock the single most-recent ask verbatim into **Revision Notes**, edit the existing `job.json` (not a rebuild), re-render, re-QC, bump **Revision #**. Turnaround ≤ 24 h. One round is included; a second is James's call on price.

## Decide the lane (at Post-Production)

- **In-house (default):** listing videos, render-based pre-construction videos (The Loft shape), drone/land videos with the static-or-animated location map, social cut-downs, text-card and trim revisions. The engine does all of this today.
- **Hero pass (human editor, booked by James):** shot-matched cinematic grade, tracked map overlays on moving aerials, 3D/motion graphics, speed ramps, cinematic lifestyle films. Even then REEL renders the in-house cut first as the safety net and the brief goes to the editor with the footage the day the shoot wraps.
- **Never single-thread.** If an outside editor holds two deadlines at once, the in-house cut becomes the primary for one of them.

## Deliverable spec (what "done" looks like)

- **Master:** 16:9, 1080p (4K `--uhd` if the source is 4K), H.264 ~18 Mbps, 30 fps, +faststart. **Social:** 9:16 1080×1920, hook in the first 1.5 s, captions burned in if there's VO.
- **Audio:** licensed music only (James supplies the file), −14 LUFS, true peak ≤ −1.5 dB, 2.5 s fade out.
- **Look:** consistent grade across the whole cut, windows/skies not clipped, aerials natural (not over-graded), verticals straight, no people unless the client asked, **no contractor watermark, no placeholder text/signage**, no AI-generated skies or scenery.
- **Land/drone videos:** the location map is mandatory — dark-navy styled base, property outline + badge, 8–12 named POIs with drive times, road labels. No map = not a THOMAS deliverable.
- **Social:** fair-housing — never imply who a home is "for". Zero tolerance.

## Hard rules

- Contractors never see the client's name or links — working name only ("The Loft").
- Claude never texts a contractor. James by phone, or a 1–2 line staged message he approves.
- Client emails are drafts for James; CC per the current email policy in `CLAUDE.md`.
- Money (editor pay, rate exceptions — edit flat $100, Ollie $350 approved) and first contact with a new client = James.
- Every job writes its feedback loop back to Airtable: **Delivery Date · Quality Score · Revision #**. That history didn't exist before; it's how we know turnaround and who to re-book.
