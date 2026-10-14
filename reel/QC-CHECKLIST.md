# QC checklist — the human pass

`qc.py` already checked resolution, fps, codec, bitrate, length, loudness, peaks, black gaps, frozen frames, dead air. This is the part a machine can't do. **Watch 100% end to end once, at full size, with sound.** Note every issue as `timecode — shot — issue — RED/YELLOW/GREEN` in the job's **Revision Notes**.

RED = can't fix in post (reshoot / new render needed) · YELLOW = fix in post before shipping · GREEN = note only.

## Story
- [ ] Follows the brief's Structure table in order; each section roughly on its time budget
- [ ] Opens on the hero (not a logo); closes on the hero or stats card + logo
- [ ] Every client must-have from the brief / Deal Request Details is in the cut
- [ ] Title spelling, project name, address, stats match the Deal record exactly

## Picture
- [ ] One consistent grade start to finish — no colour jump between renders, stills and aerials
- [ ] Skies and windows hold detail (not clipped white); nothing crushed to black
- [ ] Aerials look natural; verticals straight; horizon level
- [ ] No placeholder signage, lorem text, watermark, stock people, cheesy transition
- [ ] Ken Burns moves are slow and steady — nothing faster than a drift; no jitter on stills
- [ ] 9:16: subject stays in frame; text clear of the top/bottom UI zones
- [ ] Map: base map styled (not raw Google), property outline correct (road excluded if spec'd), POIs in the right places, drive times plausible, all badges legible and on screen

## Type
- [ ] Clean sans-serif, white/off-white, minimal; sizes readable on a phone
- [ ] Lower-thirds and overlays never cover the subject; nothing clips at the frame edge
- [ ] Card timings: long enough to read twice

## Sound
- [ ] Music is a licensed file James supplied (never a placeholder) — filename logged in `job.json`
- [ ] Cuts land on the beat; music builds through the interiors, settles on the location, resolves on the close
- [ ] Fade out finishes before picture ends; no clipped start

## Compliance
- [ ] No AI-generated sky / scenery / people anywhere (institutional clients: account-losing)
- [ ] Social: fair-housing clean — never "perfect for families / young professionals / etc."
- [ ] Nothing in the video names a contractor or shows a contractor's brand

## Ship gate
- [ ] All RED/YELLOW items cleared and re-rendered
- [ ] **QC Status → Passed** on the Fulfillment record, with notes
- [ ] James has seen the contact sheet or the cut (**James Approved** ticked) before the client does
