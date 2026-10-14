#!/usr/bin/env python3
"""
Edit Brief → REEL job. Turns the brief we already write when a video job closes
(the-method/TEMPLATE-edit-brief.md, stored in Fulfillment → 🎬 Edit Brief) into
a job folder the engine can render: job.json + map.json + BRIEF.md.

Each row of the brief's Structure table becomes a block of the timeline with
its time budget. Files in media/ are matched to rows by name (a render called
"lobby.jpg" lands in the row that mentions Lobby); a row about a map becomes a
map segment; a row about a stats card becomes a card. Anything it can't fill
is left as a TODO the editor fills before rendering.

Usage:
  python3 reel/engine/brief2job.py BRIEF.md reel/jobs/<Job>/
  (put the footage/renders in reel/jobs/<Job>/media/ first to auto-match)
"""

import json
import os
import re
import sys

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".mts"}
STOP = {"the", "and", "with", "of", "to", "on", "each", "sec", "real", "slow", "a", "an", "or",
        "nearby", "show", "drone", "end", "cut", "beat", "gentle", "camera", "moves", "still"}


def tsec(s):
    m = re.match(r"(\d+):(\d+)", s.strip())
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def parse_brief(text):
    title = re.search(r"^#\s*Edit Brief\s*[—-]\s*(.+)$", text, re.M)
    name = title.group(1) if title else "Job"
    name = re.sub(r"\(.*?\)", "", name).strip().strip('"“”')
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0].isdigit():
            span = re.split(r"[–-]", cells[2])
            a, b = (tsec(span[0]), tsec(span[1])) if len(span) == 2 else (None, None)
            rows.append({"n": int(cells[0]), "section": cells[1], "start": a, "end": b,
                         "what": cells[3], "source": cells[4]})
    stats = re.search(r"Stats for the end card:\s*(.+)", text)
    return name, rows, (stats.group(1).strip() if stats else "")


def keywords(text):
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())
    return [w for w in words if w not in STOP]


def build(brief_path, job_dir):
    text = open(brief_path).read()
    name, rows, stats = parse_brief(text)
    if not rows:
        sys.exit("no Structure table rows found in the brief")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "job"
    media_dir = os.path.join(job_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(media_dir)
                   if os.path.splitext(f)[1].lower() in IMAGE_EXT | VIDEO_EXT)
    used, clips, todo = set(), [], []

    for r in rows:
        secs = (r["end"] - r["start"]) if r["start"] is not None and r["end"] is not None else 10
        what, src = r["what"], r["source"].lower()
        blob = f"{r['section']} {what}".lower()
        if "map" in src or "points of interest" in blob:
            pois = re.split(r",\s*", what.split(":", 1)[-1])
            write_map_skeleton(job_dir, name, [p.strip(" .") for p in pois if 2 < len(p.strip()) < 40])
            clips.append({"map": "map.json", "seconds": secs, "_section": r["section"]})
            todo.append(f"Row {r['n']} {r['section']}: fill map.json (base image, property point/outline, POI points + drive times)")
            continue
        if "stats" in blob:
            lines = [s.strip() for s in re.split(r"[·•]", stats.split("(")[0])][1:] if stats else []
            clips.append({"card": {"title": name.upper(), "subtitle": "",
                                   "lines": lines or ["TODO stats line"]},
                          "seconds": min(secs, 5), "_section": r["section"]})
            if not stats:
                todo.append(f"Row {r['n']}: stats for the end card are blank in the brief")
            hero = match(files, used, ["hero"])
            if hero and secs > 5:
                used.add(hero)
                clips.append({"file": hero, "seconds": secs - 5, "move": "out", "_section": r["section"]})
            continue
        kws = keywords(what + " " + r["section"])
        picked = [f for f in files if f not in used and any(k in f.lower() for k in kws)]
        if not picked and ("aerial" in src or "aerial" in blob or "footage" in src):
            picked = [f for f in files if f not in used and os.path.splitext(f)[1].lower() in VIDEO_EXT]
        if not picked:
            clips.append({"file": f"TODO_{r['section'].lower().replace(' ', '_')}.jpg", "seconds": secs,
                          "_section": r["section"], "_brief": what})
            todo.append(f"Row {r['n']} {r['section']} ({secs}s): no media matched — {what}")
            continue
        each = round(secs / len(picked), 2)
        moves = ["in", "right", "out", "left"]
        for k, f in enumerate(picked):
            used.add(f)
            item = {"file": f, "seconds": each, "_section": r["section"]}
            if os.path.splitext(f)[1].lower() in IMAGE_EXT:
                item["move"] = moves[k % 4]
            if k == 0 and r["n"] == 1:
                item["title_overlay"] = {"title": name.upper(), "subtitle": ""}
            clips.append(item)

    leftovers = [f for f in files if f not in used]
    if leftovers:
        todo.append("Unplaced media: " + ", ".join(leftovers))
    job = {
        "job": slug, "profile": "listing", "outputs": ["16:9", "9:16"],
        "grade": "natural", "pacing": "cinematic", "transition": "fade",
        "music": "media/music.m4a", "beat_sync": True,
        "brand": {"bg": "#0B0B0C", "fg": "#FFFFFF", "accent": "#C8A24B"},
        "clips": clips,
        "_todo": todo,
    }
    with open(os.path.join(job_dir, "job.json"), "w") as f:
        json.dump(job, f, indent=2)
    with open(os.path.join(job_dir, "BRIEF.md"), "w") as f:
        f.write(text)
    return job


def match(files, used, kws):
    return next((f for f in files if f not in used and any(k in f.lower() for k in kws)), None)


def write_map_skeleton(job_dir, name, pois):
    p = os.path.join(job_dir, "map.json")
    if os.path.exists(p):
        return
    with open(p, "w") as f:
        json.dump({"base": "image", "image": "media/TODO_map_base.jpg", "style": "dark", "push": 1.25,
                   "property": {"label": name.upper(), "point": [0.5, 0.5], "outline": []},
                   "roads": [],
                   "pois": [{"name": n, "note": "TODO min", "point": None} for n in pois]}, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    j = build(sys.argv[1], sys.argv[2])
    print(f"  ✓ {sys.argv[2]}/job.json — {len(j['clips'])} timeline items")
    for t in j["_todo"]:
        print(f"    TODO {t}")
