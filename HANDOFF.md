# HANDOFF — where things stand

_Last updated: Fri Oct 17, 2026, ~6:40 pm (James's time, Mexico). Update this at the end of every session._

## ⚠️ jamesthomas.io EXPIRED (Oct 12) — NOT renewing (James 10/17). Main site + hub.jamesthomas.io are dead; do not reference that domain anywhere. Hub lives at the Lovable URL below. Oct 25: Google Workspace bill due (item 5 on hold).

## THE HUB — https://thomas-production-hub.lovable.app (Lovable "Thomas Production Hub", project 16ae45ec-2349-437b-85fa-1b9ab7f73185)
- **Canonical dashboard (item 36 answered: Lovable hub wins; 25/26 shelved).** Published 10/17 ~6:35 pm. URL: https://thomas-production-hub.lovable.app (preview fallback: https://id-preview--16ae45ec-2349-437b-85fa-1b9ab7f73185.lovable.app). James must still click Lovable → Settings → Domains → hub.jamesthomas.io → Remove / Unset as primary, otherwise the lovable.app URL redirects to the dead domain. Sign-in screen = "THOMAS PRODUCTIONS / Operations".
- **All of MASTER OS is in it:** 33 Airtable tables, 43,769 records (People 22,629) loaded 10/17 into `airtable_records` (jsonb, one row per Airtable record, keyed by Airtable record id) + `airtable_imports` log. Browse at **Airtable Data** (search, column picker, record drawer), reload at **Import** (CSV drag-drop or "Import from URL"). Admin-role only; Credential Vault deliberately excluded.
- Data was pulled live from Airtable via Composio (not the CSV export). It is a **snapshot** — no live sync yet. To refresh: re-run the pull + Import from URL, or build the Airtable-PAT sync edge function (next step).
- **10/18 built:** front door after sign-in (/choose-business) → THOMAS® Shoots (/thomas-shoots, Fulfillment) and SILENZIO Students (/silenzio, Students); header switcher. FINANCE door (AP bills/overhead + AR) building. Status doc mirrored to Drive Master Claude Folder: HUB-STATUS 2026-10-18 (`1zQ_tI2moNvemMkhy8RkyKokHn6GcJ_dATjQjiebeIpQ`) — jamesthomasphoto@gmail.com has edit access to the folder.
- Hub also has: shoots (7), mobile_work_queue (27), midtown/silenzio tables (empty).

## Open jobs
### Midtown Tampa — CBRE (THOMAS®) · $4,500 · Fulfillment `recvtLdfsopGEnmds` · Deal `rechoqMpRQmuUkZQm`
- Run autonomously by the **Midtown Job Runner** scheduled task (hourly). 10/17: Havah v1 draft and Logan v7 both FAILED QC; runner is still hunting/driving editors. Working name "The Loft". Client Addison Mcgillicuddy.
### Victory MHC — run by the **Victory Shooter Runner** (hourly :14), shoots Mon 10/19–Wed 10/21.
### Christopher Sharp — SILENZIO · Deals `rectdZUEQdmeKtzsg` · Opportunity.

## Mobile work (MOBILE-WORK doc in Master Claude Folder) — status 10/17 evening
- Done this session: 4 (SCHEDULED-TASKS-REGISTRY doc created), 27 verified, 36 answered, Airtable→hub load (new), 12 in progress (31,920 zero-byte files being trashed in background from the "My MacBook Pro" backup — ~8k done at handoff, rest running; 11 empty-root-folder check NOT done).
- Smartlead (item 6): Brokers campaign 4151447 ACTIVE (49 sent/1 reply/2 bounces, 184 queued); nurture 4154596 still DRAFT with 0 leads. GoDaddy DNS / renewal: no access from cloud.
- Needs James's Mac: 7 (AP sweep = Apple Mail), 10 Bitwarden, 11 (phone number), 23 (connector clicks + app updates).
- On hold per James: 1B, 5 (bill due 10/25), 25, 26. Planning-only: 8, 28–35. 9 (LA sub-renter) awaiting OK to draft.

## Pending for James
1. `AIRTABLE_TOKEN` env secret (for schema work) — still missing.
2. Decide: start Smartlead nurture 4154596? OK to draft item 9?
3. Delete the 2 stale scheduled tasks listed in SCHEDULED-TASKS-REGISTRY.

## Done earlier (Oct 5–16)
- The Method kit (`the-method/`), Fulfilment interface rebuild, dashboard test build (`dashboard/`, PR #8, shelved).
