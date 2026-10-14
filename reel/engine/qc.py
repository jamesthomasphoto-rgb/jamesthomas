#!/usr/bin/env python3
"""
REEL QC — check any finished video against the THOMAS delivery spec.

Works on OUR cuts (autoedit.py calls it after every render) and on an outside
editor's cut before it goes anywhere near a client. Machine checks only — it
gates the file, it does not replace watching the cut end to end.

Checks: resolution · aspect · fps · codec · bitrate · duration window ·
loudness (-14 LUFS ±2) · true peak · black gaps · frozen frames · dead audio.
Writes a contact sheet (one frame every N seconds) so the cut can be eyeballed
without scrubbing, and a QC.md report next to the file.

Usage:
  python3 reel/engine/qc.py cut.mp4                       # auto-detect profile
  python3 reel/engine/qc.py cut.mp4 --profile social      # listing|land|social|lifestyle
  python3 reel/engine/qc.py cut.mp4 --expect 120 --sheet  # also check length, build sheet
"""

import json
import os
import re
import shutil
import subprocess
import sys

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

TARGET_LUFS = -14.0

# Delivery profiles — numbers from DELIVERY-MASTERY (listing / land / social).
PROFILES = {
    "listing":   {"aspect": "16:9", "min_h": 1080, "len": (45, 150),  "mbps": (10, 30), "audio": True},
    "land":      {"aspect": "16:9", "min_h": 1080, "len": (30, 180),  "mbps": (10, 30), "audio": True},
    "lifestyle": {"aspect": "16:9", "min_h": 1080, "len": (30, 300),  "mbps": (10, 60), "audio": True},
    "social":    {"aspect": "9:16", "min_h": 1920, "len": (7, 60),    "mbps": (6, 30),  "audio": True},
}

ASPECTS = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1.0, "4:5": 4 / 5}


def probe(path):
    p = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,avg_frame_rate,bit_rate:format=duration,bit_rate",
         "-of", "json", path], capture_output=True, text=True)
    data = json.loads(p.stdout or "{}")
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    if not v:
        return None
    num, den = (v.get("avg_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den) if float(den) else 0.0
    dur = float(fmt.get("duration", 0) or 0)
    br = float(fmt.get("bit_rate", 0) or 0)
    return {"width": int(v["width"]), "height": int(v["height"]), "fps": fps,
            "vcodec": v.get("codec_name"), "acodec": a.get("codec_name") if a else None,
            "duration": dur, "mbps": br / 1e6}


def loudness(path):
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-vn",
                        "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True)
    i = re.findall(r"I:\s*(-?\d+\.?\d*)\s*LUFS", p.stderr)
    tp = re.findall(r"Peak:\s*(-?\d+\.?\d*)\s*dBFS", p.stderr)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp else None)


def scan(path, has_audio):
    """One decode pass: black gaps, frozen frames, silent stretches."""
    vf = "blackdetect=d=0.5:pix_th=0.06,freezedetect=n=0.002:d=5"
    cmd = [FFMPEG, "-hide_banner", "-nostats", "-i", path, "-vf", vf]
    if has_audio:
        cmd += ["-af", "silencedetect=n=-50dB:d=2"]
    cmd += ["-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    black = [(float(a), float(b)) for a, b in
             re.findall(r"black_start:(\d+\.?\d*) black_end:(\d+\.?\d*)", err)]
    frozen = [float(x) for x in re.findall(r"freeze_start: (\d+\.?\d*)", err)]
    silent = [float(x) for x in re.findall(r"silence_start: (-?\d+\.?\d*)", err)]
    return black, frozen, silent


def contact_sheet(path, out_jpg, duration, cols=4, rows=4):
    """Grid of evenly spaced frames, timecode burned in — the 10-second eyeball."""
    n = cols * rows
    step = max(duration / n, 0.1)
    vf = (f"fps=1/{step:.3f},scale=480:-2,"
          f"drawtext=text='%{{pts\\:hms}}':x=8:y=8:fontsize=20:fontcolor=white:"
          f"box=1:boxcolor=black@0.6:boxborderw=4,tile={cols}x{rows}:padding=4:margin=4")
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                    "-vf", vf, "-frames:v", "1", "-q:v", "3", out_jpg],
                   capture_output=True)
    return out_jpg if os.path.exists(out_jpg) else None


def guess_profile(info):
    if info["height"] > info["width"]:
        return "social"
    return "listing"


def qc_file(path, profile=None, expect=None, want_wh=None, sheet=False, report=True,
            title_card_ok=True):
    """Score a file 0–5. Returns {score, pass, checks[], info{}, sheet, report}."""
    info = probe(path)
    if not info:
        return {"score": 0, "pass": False, "checks": ["✗ could not read video stream"],
                "info": {}, "sheet": None, "report": None}
    prof_name = profile or guess_profile(info)
    prof = PROFILES.get(prof_name, PROFILES["listing"])
    checks = []

    def chk(ok, label, warn=False):
        checks.append(("✓ " if ok else ("⚠ " if warn else "✗ ")) + label)
        return ok

    w, h = info["width"], info["height"]
    if want_wh:
        chk((w, h) == tuple(want_wh), f"resolution {w}x{h} (want {want_wh[0]}x{want_wh[1]})")
    else:
        ar = w / h
        chk(abs(ar - ASPECTS[prof["aspect"]]) < 0.02, f"aspect {w}x{h} ({prof['aspect']} wanted)")
        chk(max(w, h) >= max(prof["min_h"], 1080) or min(w, h) >= 1080,
            f"resolution {w}x{h} (1080p minimum)")
    chk(23.5 <= info["fps"] <= 60.5, f"fps {info['fps']:.2f}")
    chk(info["vcodec"] in ("h264", "hevc", "prores"), f"codec {info['vcodec']}")
    lo, hi = prof["mbps"]
    # low average bitrate on static/card-heavy cuts isn't a defect by itself — warn, and
    # let the human pass judge visible compression
    chk(info["mbps"] >= lo, f"bitrate {info['mbps']:.1f} Mbps (≥{lo} expected)", warn=True)
    if expect:
        chk(abs(info["duration"] - expect) < 1.5,
            f"duration {info['duration']:.1f}s (plan {expect:.1f}s)")
    else:
        a, b = prof["len"]
        chk(a <= info["duration"] <= b, f"duration {info['duration']:.1f}s ({a}–{b}s for {prof_name})",
            warn=True)

    has_audio = info["acodec"] is not None
    if prof["audio"]:
        if chk(has_audio, "audio track present" if has_audio else "no audio track (music bed missing?)"):
            lufs, tp = loudness(path)
            if lufs is not None:
                chk(abs(lufs - TARGET_LUFS) <= 2.0, f"loudness {lufs:.1f} LUFS (want {TARGET_LUFS:.0f} ±2)")
            if tp is not None:
                chk(tp <= -0.5, f"true peak {tp:.1f} dBFS (no clipping)")

    black, frozen, silent = scan(path, has_audio)
    # Title/stats cards are near-black by design; only gaps longer than a card count.
    long_black = [(a, b) for a, b in black if b - a > (6.0 if title_card_ok else 0.5)]
    chk(not long_black, "no black gaps" if not long_black else
        "black gaps at " + ", ".join(f"{a:.1f}–{b:.1f}s" for a, b in long_black))
    chk(not frozen, "no frozen frames" if not frozen else
        "frozen picture at " + ", ".join(f"{t:.1f}s" for t in frozen[:6]), warn=True)
    if has_audio:
        mid_silence = [t for t in silent if 1.0 < t < info["duration"] - 3.0]
        chk(not mid_silence, "no dead air" if not mid_silence else
            "audio drops out at " + ", ".join(f"{t:.1f}s" for t in mid_silence[:6]), warn=True)

    hard = [c for c in checks if c.startswith("✗")]
    ok_count = sum(1 for c in checks if c.startswith("✓"))
    warn_count = sum(1 for c in checks if c.startswith("⚠"))
    score = round(5 * (ok_count + 0.5 * warn_count) / len(checks), 1) if checks else 0

    out = {"score": score, "pass": not hard, "profile": prof_name, "checks": checks,
           "info": info, "sheet": None, "report": None}
    base = os.path.splitext(path)[0]
    if sheet:
        out["sheet"] = contact_sheet(path, base + "_sheet.jpg", info["duration"])
    if report:
        rp = base + "_QC.md"
        with open(rp, "w") as f:
            f.write(f"# QC — {os.path.basename(path)}\n\n")
            f.write(f"**Machine score:** {score}/5 · **{'PASS' if out['pass'] else 'FAIL'}** · "
                    f"profile `{prof_name}`\n\n")
            f.write(f"{info['width']}x{info['height']} · {info['fps']:.2f} fps · {info['vcodec']} · "
                    f"{info['mbps']:.1f} Mbps · {info['duration']:.1f}s · audio {info['acodec']}\n\n")
            f.write("\n".join(f"- {c}" for c in checks) + "\n\n")
            if out["sheet"]:
                f.write(f"Contact sheet: `{os.path.basename(out['sheet'])}`\n\n")
            f.write("## Human pass (required — machine QC is a gate, not the bar)\n"
                    "Watch 100% end to end once. Flag each issue by timecode + shot, "
                    "RED = reshoot · YELLOW = fix in post · GREEN = pass. "
                    "See `reel/QC-CHECKLIST.md`.\n")
        out["report"] = rp
    return out


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)
    path = args[0]
    profile = args[args.index("--profile") + 1] if "--profile" in args else None
    expect = float(args[args.index("--expect") + 1]) if "--expect" in args else None
    r = qc_file(path, profile, expect, sheet="--sheet" in args)
    print(f"\n QC {os.path.basename(path)} — {r['score']}/5 "
          f"{'PASS' if r['pass'] else 'FAIL'} ({r.get('profile')})")
    for c in r["checks"]:
        print("   " + c)
    if r["sheet"]:
        print(f"   sheet → {r['sheet']}")
    if r["report"]:
        print(f"   report → {r['report']}\n")
    sys.exit(0 if r["pass"] else 2)


if __name__ == "__main__":
    main()
