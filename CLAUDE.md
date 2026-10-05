# Working with James

James runs THOMAS® (real-estate photo/video + social media), SILENZIO (mentorship / coaching) and CAPITAL. Most work in these sessions is on his Airtable, **MASTER OS**, not code. He's often live on a call and sends short messages ("he needs to be in the pipeline", "master os") — act fast, keep replies short, and ask only when it truly matters.

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

- Before creating a record, search first so you don't make duplicates.
- Do what's asked, then say in one or two lines what changed and where (table + stage), so James can find it in the interface.
- Confirm before deleting, bulk-editing, or sending anything (email, text, Stripe link) to another person.
- When something is learned about how James's system works, add it to this file.
