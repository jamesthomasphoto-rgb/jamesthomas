# reel/ — THOMAS® in-house video editor

Footage + renders + a job JSON → finished, branded, graded property video (16:9 master + 9:16 social), QC'd to the THOMAS spec. Pure Python + ffmpeg + Pillow; nothing to install on a machine that has those (this cloud container does, so does the Mac).

The operating system around it (stages, SLA, who does what) is **`SOP.md`**. The human quality pass is **`QC-CHECKLIST.md`**.

## Run it

```bash
# 1. make the job from the brief (media/ first, so files auto-match the brief's sections)
mkdir -p reel/jobs/the-loft/media   # drop renders + drone clips + music.m4a here
python3 reel/engine/brief2job.py the-method/edit-brief-the-loft.md reel/jobs/the-loft/

# 2. look at the plan, then a fast preview, then the real thing
python3 reel/engine/autoedit.py reel/jobs/the-loft/job.json --probe
python3 reel/engine/autoedit.py reel/jobs/the-loft/job.json --preview     # 540p, ~1 min
python3 reel/engine/autoedit.py reel/jobs/the-loft/job.json               # 1080p 16:9 + 9:16
python3 reel/engine/autoedit.py reel/jobs/the-loft/job.json --uhd --only 16:9   # 4K master

# 3. QC any file (ours or an outside editor's)
python3 reel/engine/qc.py some_cut.mp4 --sheet            # prints checks, writes _QC.md + contact sheet

# self-test on generated media (no client footage)
python3 reel/jobs/_demo/make_demo_media.py && python3 reel/engine/autoedit.py reel/jobs/_demo/job.json
```

Output lands in `reel/out/<job>/` with `manifest.json` (QC scores), a `_sheet.jpg` contact sheet per aspect and a `_QC.md` report. `out/` and `jobs/*/media/` are git-ignored.

## job.json

```jsonc
{
  "job": "the-loft",            // output filename stem
  "profile": "listing",         // listing | land | social | lifestyle (QC length/bitrate windows)
  "outputs": ["16:9", "9:16"],  // also 1:1, 4:5
  "grade": "natural",           // job default: none | natural | bright-airy | twilight | cinematic | punchy | warm | cool | bw | tiltshift
  "pacing": "cinematic",        // cinematic (6s/cut) | balanced (4s) | social (2.2s) — default seconds + transition length
  "music": "media/music.m4a", "beat_sync": true, "bpm": 100,   // bpm optional — estimated from the music if omitted
  "vo": "media/narration.wav",  // optional; music ducks under it
  "letterbox": false,           // 2.39:1 bars on 16:9
  "logo": {"path": "media/client-logo.png", "pos": "tr", "scale": 0.16, "opacity": 0.9},
  "brand": {"bg": "#0B0B0C", "fg": "#FFFFFF", "accent": "#C8A24B", "map_bg": "#0E1E33", "map_badge": "#0F2340"},
  "intro": {"title": "THE LOFT", "subtitle": "Tampa", "seconds": 3},   // optional title card
  "outro": {"title": "THOMAS®", "seconds": 2.5},
  "hook": {"text": "339 units. Midtown.", "seconds": 2.5},             // 9:16 burn-in
  "captions": "media/captions.srt",                                    // 9:16 burn-in
  "clips": [
    {"file": "hero.jpg", "seconds": 6, "move": "in", "zoom": 1.18, "grade": "twilight",
     "title_overlay": {"title": "THE LOFT", "subtitle": "Midtown Tampa"}},
    {"card": {"title": "THE BUILDING"}, "seconds": 2},
    {"file": "lobby.jpg", "seconds": 3, "move": "right", "label": "Lobby", "transition": "cut"},
    {"file": "unit.jpg", "seconds": 3, "floorplan": {"title": "1 BED", "spec": "1 bd · 1 ba · 742 sf"}},
    {"file": "DJI_0412.mp4", "seconds": 8, "start": 4, "speed": 0.75, "focus": "top", "stabilize": true, "grade": "natural"},
    {"map": "map.json", "seconds": 12},
    {"card": {"title": "THE LOFT", "subtitle": "For sale as a whole", "lines": ["23 stories · 339 units"]}, "seconds": 4,
     "aspects": ["16:9"]}                                               // only in some outputs
  ]
}
```

Stills get a Ken Burns move (`in` · `out` · `left` · `right` · `none`), supersampled so it's smooth. Clips are clamped to their real length; `speed` 0.75 slows a drone pass. `focus` keeps the subject when the 9:16 crop happens. Per-item `grade`, `transition` (`fade`, `cut`, or any ffmpeg xfade name) and `transition_seconds` override the job defaults. `label` = lower-third.

## map.json — the location map

See the docstring in `engine/maps.py`. Base is either a local image (site plan, client-approved map screenshot, drone still — points as 0–1 fractions of that image) or stitched Esri satellite tiles around a lat/lon (needs network; POIs without a point are looked up on OpenStreetMap). Style `dark` is the house look. Preview a map on its own:

```bash
python3 reel/engine/maps.py reel/jobs/the-loft/map.json /tmp/map.mp4 12
```

## Honest limits (route to a human hero pass)

Shot-matched cinematic grading, tracked overlays that stick to moving aerials, 3D/motion graphics, speed ramps, and transcribing speech to captions (the engine burns an `.srt` you give it). Music must be a licensed file James supplies.
