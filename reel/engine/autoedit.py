#!/usr/bin/env python3
"""
REEL — THOMAS® in-house video editor (engine v3)

Turns a folder of raw clips + stills + a job JSON into a finished, branded,
graded video — property, land or social — and QCs it before anyone sees it.

v3 (this repo) = the v2 master engine from the Mac (grade presets, beat-synced
cuts, smart reframe, letterbox, animated titles, social hook + captions, VO
ducking, logo, QC) plus:
  • cards anywhere in the sequence ({"card": {...}}) — section titles, stats cards
  • Ken Burns moves on stills: in / out / left / right, supersampled (no jitter)
  • clips clamped to their real length; optional speed (0.5 = half-speed drone)
  • per-item transitions ("cut" for a hard cut on the beat)
  • map segments from engine/maps.py ({"map": "map.json"})
  • --preview (fast half-res check) · --uhd (4K) · --out DIR
  • QC shared with engine/qc.py (black gaps, frozen frames, loudness, contact sheet)

Usage:
  python3 reel/engine/autoedit.py reel/jobs/<Job>/job.json
  python3 reel/engine/autoedit.py <job.json> --only 9:16
  python3 reel/engine/autoedit.py <job.json> --probe        # plan only
  python3 reel/engine/autoedit.py <job.json> --preview      # fast 540p look
  python3 reel/engine/autoedit.py <job.json> --uhd          # 4K masters

THOMAS export spec: H.264 .mp4 · 1080p (4K if source) · ~18 Mbps · 30 fps ·
16:9 master + 9:16 social · audio -14 LUFS.
"""

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import qc as qcmod  # noqa: E402

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def _find_font(candidates):
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


FONT_REGULAR = _find_font([
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])
FONT_BOLD = _find_font([
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]) or FONT_REGULAR

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".mts", ".m2ts"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff"}

GEOMETRY = {"16:9": (1920, 1080), "9:16": (1080, 1920),
            "1:1": (1080, 1080), "4:5": (1080, 1350)}

LOGO_POS = {"tl": ("{m}", "{m}"), "tr": ("W-w-{m}", "{m}"),
            "bl": ("{m}", "H-h-{m}"), "br": ("W-w-{m}", "H-h-{m}")}

FPS = 30
VIDEO_BITRATE = "18M"
AUDIO_LUFS = -14

# pacing → default seconds per body segment, beats per cut, transition seconds
PACING = {
    "cinematic": {"seconds": 6.0, "beats": 8, "tdur": 0.7},
    "balanced":  {"seconds": 4.0, "beats": 4, "tdur": 0.5},
    "social":    {"seconds": 2.2, "beats": 2, "tdur": 0.25},
}

# per-render settings, set once in main()
OPT = {"preset": "veryfast", "scale": 1.0}


def die(msg):
    print(f"\n  ✗ {msg}\n", file=sys.stderr)
    sys.exit(1)


def run(cmd, label=""):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-20:])
        die(f"ffmpeg failed ({label})\n{tail}")
    return proc


def try_run(cmd, timeout=900):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except Exception:
        return False


def probe_duration(path):
    proc = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=noprint_wrappers=1:nokey=1", path],
                          capture_output=True, text=True)
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def encode_args(crf=20):
    return ["-an", "-c:v", "libx264", "-preset", OPT["preset"], "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", str(FPS)]


# ---------------------------------------------------------------- text helpers
def textfile(text, tmpdir, tag):
    """Write label text to a file so drawtext never needs escaping."""
    p = os.path.join(tmpdir, f"txt_{tag}.txt")
    with open(p, "w") as f:
        f.write(text)
    return p


def font_clause(bold=False):
    return f"fontfile='{FONT_BOLD if bold else FONT_REGULAR}'"


def hexcol(brand, key, default):
    h = str(brand.get(key, default)).strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "0x" + h


def fade_alpha(seconds, fin=0.5, fout=0.5):
    return (f"if(lt(t,{fin}),t/{fin},"
            f"if(gt(t,{seconds - fout}),max(0\\,({seconds}-t)/{fout}),1))")


# ---------------------------------------------------------------- color grade
def grade_chain(grade):
    """vf snippets for a grade preset (str) or explicit {eq,curves,colorbalance,unsharp}."""
    if not grade or grade == "none":
        return []
    if isinstance(grade, dict):
        return [f"{k}={grade[k]}" for k in ("eq", "curves", "colorbalance", "unsharp") if k in grade]
    g = str(grade).lower()
    if g in ("cinematic", "film"):
        return ["curves=r='0/0.02 0.5/0.50 1/0.98':b='0/0.06 0.5/0.47 1/0.92'",
                "eq=contrast=1.08:saturation=1.10:gamma=0.98",
                "unsharp=5:5:0.4:5:5:0.0", "vignette=PI/5"]
    if g in ("bright-airy", "airy", "realestate", "interior"):
        # top-end roll-off = a window pull: bright windows/skies recover, don't clip
        return ["curves=all='0/0 0.5/0.52 0.8/0.79 1/0.93'",
                "eq=brightness=0.04:contrast=0.96:saturation=1.05:gamma=1.05",
                "colorbalance=rs=0.02:bs=-0.03:rm=0.02:bm=-0.02",
                "unsharp=3:3:0.3:3:3:0.0"]
    if g in ("twilight", "dusk"):
        # blue-hour hero: cool shadows, warm mids (window glow), protected highlights
        return ["curves=all='0/0 0.5/0.5 0.85/0.82 1/0.95'",
                "colorbalance=bs=0.05:rm=0.05:gm=0.01:bm=-0.03",
                "eq=contrast=1.06:saturation=1.12", "unsharp=3:3:0.3:3:3:0.0"]
    if g in ("natural", "drone", "aerial"):
        # the "don't over-grade the aerials" look: gentle contrast, true greens
        return ["eq=contrast=1.04:saturation=1.04:gamma=1.0", "unsharp=3:3:0.25:3:3:0.0"]
    if g in ("punchy", "social", "vivid"):
        return ["eq=contrast=1.16:saturation=1.26:brightness=0.02", "unsharp=5:5:0.6:5:5:0.0"]
    if g == "warm":
        return ["colorbalance=rm=0.06:bm=-0.06", "eq=saturation=1.08:contrast=1.04"]
    if g == "cool":
        return ["colorbalance=rm=-0.05:bm=0.06", "eq=saturation=1.06:contrast=1.04"]
    if g in ("bw", "mono", "noir"):
        return ["hue=s=0", "eq=contrast=1.12:gamma=0.97", "unsharp=5:5:0.4:5:5:0.0"]
    return []


FOCUS = {"center": ("(iw-ow)/2", "(ih-oh)/2"), "left": ("0", "(ih-oh)/2"),
         "right": ("(iw-ow)", "(ih-oh)/2"), "top": ("(iw-ow)/2", "0"),
         "bottom": ("(iw-ow)/2", "(ih-oh)")}


# ---------------------------------------------------------------- overlays
def _letterbox_vf(vf, w, h, letterbox):
    if not letterbox:
        return
    bar = int(round((h - (w / 2.39)) / 2))
    if bar > 2:
        vf.append(f"drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill")
        vf.append(f"drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill")


def _lower_third(vf, label, brand, w, h, tmpdir, idx):
    if not label:
        return
    s = min(w, h) / 1080.0
    sz, pad, box_h = int(40 * s), int(40 * s), int(72 * s)
    box_y = h - box_h - int(40 * h / 1080.0) if w >= h else h - box_h - int(260 * s)
    lf = textfile(label, tmpdir, f"l{idx}")
    vf.append(f"drawbox=x=0:y={box_y}:w=iw:h={box_h}:color=black@0.45:t=fill")
    vf.append(f"drawtext={font_clause(True)}:textfile='{lf}':fontcolor={hexcol(brand, 'fg', '#FFFFFF')}:"
              f"fontsize={sz}:x={pad}:y={box_y}+({box_h}-text_h)/2")


def _floorplan_overlay(vf, fp, brand, w, h, tmpdir, idx):
    """Top-right unit name + bed/bath/sqft spec."""
    if not fp:
        return
    s = h / 1080.0
    fg = hexcol(brand, "floorplan_fg", "#FFFFFF")
    pad, tsz, ssz = int(50 * s), int(50 * s), int(30 * s)
    if fp.get("title"):
        tf = textfile(fp["title"], tmpdir, f"fpt{idx}")
        vf.append(f"drawtext={font_clause(True)}:textfile='{tf}':fontcolor={fg}:fontsize={tsz}:"
                  f"x=w-text_w-{pad}:y={pad}:box=1:boxcolor=black@0.35:boxborderw={int(12 * s)}")
    if fp.get("spec"):
        sf = textfile(fp["spec"], tmpdir, f"fps{idx}")
        y = f"{pad}+{tsz}+{int(10 * s)}" if fp.get("title") else str(pad)
        vf.append(f"drawtext={font_clause()}:textfile='{sf}':fontcolor={fg}:fontsize={ssz}:"
                  f"x=w-text_w-{pad}:y={y}+{int(14 * s)}:box=1:boxcolor=black@0.35:boxborderw={int(10 * s)}")


def _text_block(vf, title, sub, lines, brand, w, h, tmpdir, tag, seconds, shadow):
    """Centered title + accent rule + subtitle + stat lines, fading in/out."""
    s = min(w, h) / 1080.0
    fg = hexcol(brand, "fg", "#FFFFFF")
    accent = hexcol(brand, "accent", "#C8A24B")
    alpha = fade_alpha(seconds, 0.5, 0.5)
    sh = ":shadowcolor=black@0.55:shadowx=2:shadowy=2" if shadow else ""
    lines = lines or []
    tsz = int(92 * s)
    if title:  # width-fit so a long address never clips on 9:16
        tsz = max(int(40 * s), min(tsz, int(1.7 * (w - int(80 * s)) / max(len(title), 1))))
    ssz, lsz = int(42 * s), int(38 * s)
    block = tsz + int(60 * s) + (ssz + int(14 * s) if sub else 0) + len(lines) * int(lsz * 1.45)
    top = f"(h-{block})/2"
    if title:
        tf = textfile(title, tmpdir, f"t{tag}")
        vf.append(f"drawtext={font_clause(True)}:textfile='{tf}':fontcolor={fg}:fontsize={tsz}:"
                  f"alpha='{alpha}'{sh}:x=(w-text_w)/2:y={top}")
        rw, rh = int(120 * s), max(2, int(4 * s))
        # drawbox's own `h` is the box height, so the frame height here is `ih`
        vf.append(f"drawbox=x=(iw-{rw})/2:y=(ih-{block})/2+{tsz + int(24 * s)}:w={rw}:h={rh}:"
                  f"color={accent}:t=fill:enable='gte(t,0.3)'")
    y = f"{top}+{tsz + int(60 * s)}"
    if sub:
        sf = textfile(sub, tmpdir, f"s{tag}")
        vf.append(f"drawtext={font_clause()}:textfile='{sf}':fontcolor={fg}@0.9:fontsize={ssz}:"
                  f"alpha='{alpha}'{sh}:x=(w-text_w)/2:y={y}")
        y = f"{y}+{ssz + int(14 * s)}"
    for k, line in enumerate(lines):
        lf = textfile(line, tmpdir, f"ln{tag}_{k}")
        vf.append(f"drawtext={font_clause()}:textfile='{lf}':fontcolor={fg}@0.85:fontsize={lsz}:"
                  f"alpha='{alpha}'{sh}:x=(w-text_w)/2:y={y}+{int(k * lsz * 1.45)}")


# ---------------------------------------------------------------- segment builders
def build_card(card, w, h, seconds, brand, tmpdir, idx):
    out = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")
    bg = hexcol(brand, "bg", "#0B0B0C")
    vf = ["format=yuv420p"]
    _text_block(vf, card.get("title", ""), card.get("subtitle", ""), card.get("lines"),
                brand, w, h, tmpdir, idx, seconds, shadow=False)
    run([FFMPEG, "-y", "-f", "lavfi", "-i", f"color=c={bg}:s={w}x{h}:d={seconds}:r={FPS}",
         "-vf", ",".join(vf)] + encode_args() + [out], f"card {idx}")
    return out, seconds


def _post_overlays(it, brand, w, h, tmpdir, idx, seconds, letterbox):
    post = []
    _letterbox_vf(post, w, h, letterbox)
    _lower_third(post, it.get("label"), brand, w, h, tmpdir, idx)
    _floorplan_overlay(post, it.get("floorplan"), brand, w, h, tmpdir, idx)
    to = it.get("title_overlay")
    if to:
        _text_block(post, to.get("title", ""), to.get("subtitle", ""), to.get("lines"),
                    brand, w, h, tmpdir, f"o{idx}", seconds, shadow=True)
    return post


def _tiltshift_mask_expr(band=0.14, feather=0.10):
    a, b, c, d = 0.5 - band - feather, 0.5 - band, 0.5 + band, 0.5 + band + feather
    return (f"if(lt(Y,H*{a}),255,if(lt(Y,H*{b}),255-(Y-H*{a})/(H*{feather})*255,"
            f"if(lt(Y,H*{c}),0,if(lt(Y,H*{d}),(Y-H*{c})/(H*{feather})*255,255))))")


def stabilize_source(src, tmpdir, idx, seconds, start):
    trf = os.path.join(tmpdir, f"transforms_{idx}.trf")
    seek = ["-ss", str(start)] if start else []
    ok = try_run([FFMPEG, "-y"] + seek + ["-t", str(seconds + 2), "-i", src, "-vf",
                  f"scale=960:-2,vidstabdetect=shakiness=5:accuracy=15:result={trf}",
                  "-f", "null", "-"], timeout=300)
    return trf if ok and os.path.exists(trf) else None


def build_clip(it, w, h, seconds, brand, tmpdir, idx, grade, letterbox):
    out = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")
    src, start = it["path"], it.get("start", 0)
    speed = float(it.get("speed", 1.0)) or 1.0
    fx, fy = FOCUS.get(it.get("focus", "center"), FOCUS["center"])
    pre = [f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}:{fx}:{fy}"]
    if speed != 1.0:
        pre.append(f"setpts=PTS/{speed}")
    pre.append(f"fps={FPS}")
    seek = ["-ss", str(start)] if start else []
    src_secs = seconds * speed

    stab = []
    if it.get("stabilize"):
        trf = stabilize_source(src, tmpdir, idx, src_secs, start)
        if trf:
            stab = [f"vidstabtransform=input={trf}:zoom=0:smoothing=15", "unsharp=5:5:0.8:3:3:0.4"]
        else:
            print(f"    (stabilize unavailable — skipping seg {idx})")
    post = _post_overlays(it, brand, w, h, tmpdir, idx, seconds, letterbox)

    if str(grade).lower() == "tiltshift":
        filt = (f"[0:v]{','.join(stab + pre)},format=yuv420p,split=2[sharp][toblur];"
                f"[toblur]gblur=sigma=18[blur];"
                f"color=c=black:s={w}x{h}:d={seconds}:r={FPS},format=gray,"
                f"geq=lum='{_tiltshift_mask_expr()}':cb=128:cr=128[mask];"
                f"[sharp][blur][mask]maskedmerge[tilt];"
                f"[tilt]{','.join(post) if post else 'null'}[vout]")
        cmd = [FFMPEG, "-y"] + seek + ["-t", f"{src_secs:.3f}", "-i", src,
                                       "-filter_complex", filt, "-map", "[vout]"]
    else:
        vf = stab + pre + grade_chain(grade) + ["format=yuv420p"] + post
        cmd = [FFMPEG, "-y"] + seek + ["-t", f"{src_secs:.3f}", "-i", src, "-vf", ",".join(vf)]
    run(cmd + ["-t", f"{seconds:.3f}"] + encode_args() + [out], f"clip {idx} ({os.path.basename(src)})")
    return out, seconds


def build_still(it, w, h, seconds, brand, tmpdir, idx, grade, letterbox):
    """Ken Burns on a still. Supersampled 2x before zoompan so the move is smooth."""
    out = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")
    n = max(2, int(round(seconds * FPS)))
    move = it.get("move", "in")
    zmax = float(it.get("zoom", 1.18))
    ss = 2
    bw, bh = w * ss, h * ss
    fx, fy = FOCUS.get(it.get("focus", "center"), FOCUS["center"])
    cx = "iw/2-(iw/zoom/2)"
    cy = "ih/2-(ih/zoom/2)"
    p = f"(on/{n - 1})"
    if move == "out":
        z, x, y = f"{zmax}-({zmax}-1)*{p}", cx, cy
    elif move == "left":    # drift right→left
        z, x, y = f"{zmax}", f"(iw-iw/zoom)*(1-{p})", cy
    elif move == "right":   # drift left→right
        z, x, y = f"{zmax}", f"(iw-iw/zoom)*{p}", cy
    elif move == "none":
        z, x, y = "1", "0", "0"
    else:                   # push in
        z, x, y = f"1+({zmax}-1)*{p}", cx, cy
    vf = [f"scale={bw}:{bh}:force_original_aspect_ratio=increase", f"crop={bw}:{bh}:{fx}:{fy}",
          f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={FPS}"]
    vf += grade_chain(grade) + ["format=yuv420p"]
    vf += _post_overlays(it, brand, w, h, tmpdir, idx, seconds, letterbox)
    run([FFMPEG, "-y", "-i", it["path"], "-vf", ",".join(vf), "-frames:v", str(n)]
        + encode_args() + [out], f"still {idx} ({os.path.basename(it['path'])})")
    return out, n / FPS


def build_map(it, w, h, seconds, brand, tmpdir, idx, job_dir):
    import maps
    cfg_path = it["map"] if os.path.isabs(it["map"]) else os.path.join(job_dir, it["map"])
    out = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")
    maps.render_segment(cfg_path, out, w, h, seconds, FPS, brand=brand, preset=OPT["preset"])
    return out, seconds


# ---------------------------------------------------------------- beat sync
def estimate_bpm(music_path, tmpdir):
    """Energy-autocorrelation tempo estimate over 70–170 BPM. Pure stdlib."""
    wav = os.path.join(tmpdir, "bpm.wav")
    if subprocess.run([FFMPEG, "-y", "-t", "30", "-i", music_path, "-ac", "1", "-ar", "8000",
                       "-vn", "-f", "wav", wav], capture_output=True).returncode != 0:
        return 120.0
    try:
        with wave.open(wav, "rb") as wf:
            raw = wf.readframes(wf.getnframes())
        samples = struct.unpack("<%dh" % (len(raw) // 2), raw)
    except Exception:
        return 120.0
    sr, hop = 8000, 80
    if len(samples) < sr * 4:
        return 120.0
    env, prev = [], 0.0
    for i in range(0, len(samples) - hop, hop):
        e = sum(s * s for s in samples[i:i + hop]) / hop
        env.append(max(0.0, e - prev))
        prev = e
    best, best_score = 120.0, -1.0
    for bpm in range(70, 171):
        lag = int(round(100.0 * 60.0 / bpm))
        if 0 < lag < len(env):
            sc = sum(env[i] * env[i + lag] for i in range(len(env) - lag))
            if sc > best_score:
                best_score, best = sc, float(bpm)
    return best


def snap_to_beats(seconds, beat, beats_per_cut):
    if beat <= 0:
        return seconds
    n = max(1, round(seconds / beat)) if seconds else beats_per_cut
    return round(n * beat, 3)


# ---------------------------------------------------------------- assembly
def assemble(segments, tdur_default, music, vo, out_path, tmpdir, burn=None, logo=None,
             uhd_bitrate=False):
    """One ffmpeg call: xfade the segments, music bed (ducked under VO), logo, burn-ins."""
    inputs = []
    for seg in segments:
        inputs += ["-i", seg["file"]]
    has_music = bool(music) and os.path.exists(music)
    has_vo = bool(vo) and os.path.exists(vo)
    has_logo = bool(logo) and bool(logo.get("path")) and os.path.exists(logo["path"])
    n = len(segments)
    music_idx = vo_idx = logo_idx = None
    if has_music:
        music_idx = n
        inputs += ["-stream_loop", "-1", "-i", music]
    if has_vo:
        vo_idx = n + int(has_music)
        inputs += ["-i", vo]
    if has_logo:
        logo_idx = n + int(has_music) + int(has_vo)
        inputs += ["-i", logo["path"]]

    filt = []
    if n == 1:
        filt.append("[0:v]format=yuv420p[vbase]")
        total = segments[0]["dur"]
    else:
        prev, cum = "[0:v]", segments[0]["dur"]
        for k in range(1, n):
            trans = segments[k].get("transition") or "fade"
            td = segments[k].get("tdur", tdur_default)
            if trans == "cut":
                trans, td = "fade", 1.0 / FPS
            td = min(td, segments[k]["dur"] / 2, segments[k - 1]["dur"] / 2)
            offset = max(0.0, cum - td)
            lbl = "[vbase]" if k == n - 1 else f"[vx{k}]"
            filt.append(f"{prev}[{k}:v]xfade=transition={trans}:duration={td:.3f}:offset={offset:.3f}{lbl}")
            prev = lbl
            cum = cum + segments[k]["dur"] - td
        total = cum

    vlast = "[vbase]"
    if burn:
        if burn.get("captions_srt") and os.path.exists(burn["captions_srt"]):
            srt = os.path.join(tmpdir, "caps.srt")
            shutil.copyfile(burn["captions_srt"], srt)
            style = burn.get("caption_style",
                             "FontName=Liberation Sans,Fontsize=14,Bold=1,PrimaryColour=&H00FFFFFF,"
                             "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
                             "Alignment=2,MarginV=120")
            filt.append(f"{vlast}subtitles=filename={srt}:force_style='{style}'[vcap]")
            vlast = "[vcap]"
        if burn.get("hook_text"):
            hf = textfile(burn["hook_text"], tmpdir, "hook")
            hs = burn.get("hook_seconds", 2.5)
            a = f"if(lt(t,0.3),t/0.3,if(gt(t,{hs - 0.4}),max(0\\,({hs}-t)/0.4),1))"
            filt.append(f"{vlast}drawtext={font_clause(True)}:textfile='{hf}':fontcolor=white:"
                        f"fontsize={burn.get('hook_size', 84)}:box=1:boxcolor=black@0.35:boxborderw=24:"
                        f"x=(w-text_w)/2:y=h*0.18:enable='between(t,0,{hs})':alpha='{a}'[vhook]")
            vlast = "[vhook]"
    if has_logo:
        m = int(logo.get("margin", 48) * OPT["scale"])
        xpos, ypos = LOGO_POS.get(logo.get("pos", "tr"), LOGO_POS["tr"])
        filt.append(f"[{logo_idx}:v]format=rgba,colorchannelmixer=aa={float(logo.get('opacity', 0.9))},"
                    f"scale=iw*{float(logo.get('scale', 0.16))}*{OPT['scale']}:-1[lg]")
        filt.append(f"{vlast}[lg]overlay=x={xpos.format(m=m)}:y={ypos.format(m=m)}[vlogo]")
        vlast = "[vlogo]"
    filt.append(f"{vlast}null[vout]")
    maps_ = ["-map", "[vout]"]

    if has_music or has_vo:
        fade_st = max(0.0, total - 2.5)
        norm = f"loudnorm=I={AUDIO_LUFS}:TP=-1.5:LRA=11"
        if has_music:
            filt.append(f"[{music_idx}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.5,"
                        f"afade=t=out:st={fade_st:.3f}:d=2.5,"
                        f"aformat=sample_rates=48000:channel_layouts=stereo[mbed]")
        if has_vo:
            filt.append(f"[{vo_idx}:a]atrim=0:{total:.3f},aformat=sample_rates=48000:"
                        f"channel_layouts=stereo,asplit=2[vo1][vo2]")
        if has_music and has_vo:
            filt.append("[mbed][vo1]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[mduck]")
            filt.append(f"[mduck][vo2]amix=inputs=2:duration=first:dropout_transition=0,{norm}[aout]")
        elif has_vo:
            filt.append(f"[vo1]{norm}[aout]")
            filt.append("[vo2]anullsink")
        else:
            filt.append(f"[mbed]{norm}[aout]")
        maps_ += ["-map", "[aout]"]

    br = "45M" if uhd_bitrate else VIDEO_BITRATE
    cmd = [FFMPEG, "-y"] + inputs + ["-filter_complex", ";".join(filt)] + maps_ + [
        "-c:v", "libx264", "-preset", "medium" if OPT["preset"] != "ultrafast" else "ultrafast",
        "-b:v", br, "-maxrate", br, "-bufsize", "36M" if not uhd_bitrate else "90M",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", "-t", f"{total:.3f}"]
    if has_music or has_vo:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    run(cmd + [out_path], "final assembly")
    return total


# ---------------------------------------------------------------- media gather
def resolve_path(p, job_dir):
    if not p:
        return None
    return p if os.path.isabs(p) else os.path.join(job_dir, p)


def gather_media(cfg, job_dir, default_seconds):
    media_dir = resolve_path(cfg.get("media_dir", "media"), job_dir)
    items = []
    if cfg.get("clips"):
        for c in cfg["clips"]:
            it = dict(c)
            it.setdefault("seconds", default_seconds)
            if "card" in c:
                it["kind"] = "card"
            elif "map" in c:
                it["kind"] = "map"
            else:
                path = c["file"] if os.path.isabs(c["file"]) else os.path.join(media_dir, c["file"])
                it["path"] = path
                it["kind"] = "still" if os.path.splitext(path)[1].lower() in IMAGE_EXT else "clip"
            items.append(it)
    else:
        if not os.path.isdir(media_dir):
            die(f"media_dir not found: {media_dir}")
        for name in sorted(os.listdir(media_dir)):
            ext = os.path.splitext(name)[1].lower()
            kind = "clip" if ext in VIDEO_EXT else "still" if ext in IMAGE_EXT else None
            if kind:
                items.append({"path": os.path.join(media_dir, name), "kind": kind,
                              "seconds": default_seconds})
    if not items:
        die("no media found to edit")
    missing = [it["path"] for it in items if it["kind"] in ("clip", "still")
               and not os.path.exists(it["path"])]
    if missing:
        die("missing media:\n    " + "\n    ".join(missing))
    # clamp clips to the footage that actually exists
    for it in items:
        if it["kind"] == "clip":
            d = probe_duration(it["path"])
            if d:
                avail = (d - it.get("start", 0)) / float(it.get("speed", 1.0) or 1.0)
                if avail < it["seconds"]:
                    print(f"    note: {os.path.basename(it['path'])} only has {avail:.1f}s — trimmed")
                    it["seconds"] = round(max(0.5, avail - 0.05), 2)
    return items


# ---------------------------------------------------------------- orchestration
def render_aspect(cfg, items, aspect, job_dir, out_dir, beat, uhd):
    bw, bh = GEOMETRY[aspect]
    k = (2 if uhd else 1) * OPT["scale"]
    w, h = int(bw * k) // 2 * 2, int(bh * k) // 2 * 2
    brand = cfg.get("brand", {})
    job = cfg.get("job", "untitled")
    job_grade = cfg.get("grade", "none")
    pacing = PACING.get(cfg.get("pacing", "balanced"), PACING["balanced"])
    letterbox = bool(cfg.get("letterbox")) and aspect == "16:9"
    sync = beat and cfg.get("beat_sync", bool(cfg.get("bpm")))
    tmpdir = tempfile.mkdtemp(prefix=f"reel_{aspect.replace(':', 'x')}_")
    segs = []
    try:
        seq = []
        if cfg.get("intro"):
            seq.append({"kind": "card", "card": cfg["intro"], "seconds": cfg["intro"].get("seconds", 3)})
        seq += [it for it in items if aspect in it.get("aspects", [aspect])]
        if cfg.get("outro"):
            seq.append({"kind": "card", "card": cfg["outro"], "seconds": cfg["outro"].get("seconds", 3)})

        for idx, it in enumerate(seq):
            secs = it["seconds"]
            if sync and it["kind"] in ("clip", "still"):
                secs = snap_to_beats(secs, beat, pacing["beats"])
            g = it.get("grade", job_grade)
            if it["kind"] == "card":
                f, d = build_card(it["card"], w, h, secs, brand, tmpdir, idx)
            elif it["kind"] == "map":
                f, d = build_map(it, w, h, secs, brand, tmpdir, idx, job_dir)
            elif it["kind"] == "still":
                f, d = build_still(it, w, h, secs, brand, tmpdir, idx, g, letterbox)
            else:
                f, d = build_clip(it, w, h, secs, brand, tmpdir, idx, g, letterbox)
            segs.append({"file": f, "dur": d, "transition": it.get("transition", cfg.get("transition", "fade")),
                         "tdur": it.get("transition_seconds", cfg.get("transition_seconds", pacing["tdur"]))})
            print(f"    · {idx + 1}/{len(seq)} {it['kind']:5} {d:4.1f}s", end="\r")

        logo = cfg.get("logo")
        if logo:
            logo = {"path": logo} if isinstance(logo, str) else dict(logo)
            logo["path"] = resolve_path(logo.get("path"), job_dir)
        burn = None
        if aspect in cfg.get("burn_in_aspects", ["9:16"]) and (cfg.get("hook") or cfg.get("captions")):
            burn = {}
            hook = cfg.get("hook")
            if hook:
                burn["hook_text"] = hook.get("text", "") if isinstance(hook, dict) else str(hook)
                if isinstance(hook, dict):
                    burn["hook_seconds"] = hook.get("seconds", 2.5)
                burn["hook_size"] = int((hook.get("size", 84) if isinstance(hook, dict) else 84) * h / 1920.0)
            if cfg.get("captions"):
                burn["captions_srt"] = resolve_path(cfg["captions"], job_dir)

        print()
        suffix = aspect.replace(":", "x") + ("_4K" if uhd else "") + ("_preview" if OPT["scale"] < 1 else "")
        out_path = os.path.join(out_dir, f"{job}_{suffix}.mp4")
        total = assemble(segs, cfg.get("transition_seconds", pacing["tdur"]),
                         resolve_path(cfg.get("music"), job_dir), resolve_path(cfg.get("vo"), job_dir),
                         out_path, tmpdir, burn, logo, uhd_bitrate=uhd)
        profile = cfg.get("profile") or ("social" if aspect == "9:16" else "listing")
        qc = qcmod.qc_file(out_path, profile, expect=total, want_wh=(w, h), sheet=True, report=True)
        size_mb = os.path.getsize(out_path) / 1e6
        print(f"    ✓ {aspect:5} {total:6.1f}s {size_mb:6.1f} MB  [QC {qc['score']}/5 "
              f"{'PASS' if qc['pass'] else 'FAIL'}]  {os.path.relpath(out_path)}")
        for c in qc["checks"]:
            if not c.startswith("✓"):
                print(f"        {c}")
        return {"aspect": aspect, "file": out_path, "seconds": round(total, 2),
                "size_mb": round(size_mb, 1), "qc": {k2: qc[k2] for k2 in ("score", "pass", "checks")},
                "sheet": qc["sheet"], "qc_report": qc["report"]}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        die("usage: autoedit.py <job.json> [--only 16:9] [--probe] [--preview] [--uhd] [--out DIR]")
    cfg_path = args[0]
    if not os.path.exists(cfg_path):
        die(f"job config not found: {cfg_path}")
    if not shutil.which("ffmpeg"):
        die("ffmpeg not found on PATH")
    only = args[args.index("--only") + 1] if "--only" in args else None
    preview = "--preview" in args
    uhd = "--uhd" in args and not preview
    if preview:
        OPT.update(preset="ultrafast", scale=0.5)

    with open(cfg_path) as f:
        cfg = json.load(f)
    job_dir = os.path.dirname(os.path.abspath(cfg_path))
    job = cfg.get("job", "untitled")
    pacing = PACING.get(cfg.get("pacing", "balanced"), PACING["balanced"])
    items = gather_media(cfg, job_dir, cfg.get("clip_seconds", pacing["seconds"]))
    aspects = [only] if only else cfg.get("outputs", ["16:9", "9:16"])
    for a in aspects:
        if a not in GEOMETRY:
            die(f"unknown aspect '{a}' (use {', '.join(GEOMETRY)})")

    beat = 0.0
    if cfg.get("beat_sync", bool(cfg.get("bpm"))) and (cfg.get("music") or cfg.get("bpm")):
        bpm = cfg.get("bpm")
        if not bpm:
            tmp = tempfile.mkdtemp(prefix="reel_bpm_")
            bpm = estimate_bpm(resolve_path(cfg["music"], job_dir), tmp)
            shutil.rmtree(tmp, ignore_errors=True)
            print(f"  ♪ estimated tempo: {bpm:.0f} BPM")
        beat = 60.0 / float(bpm)

    plan = sum(it["seconds"] for it in items) + sum(
        (cfg.get(k) or {}).get("seconds", 3) for k in ("intro", "outro") if cfg.get(k))
    print(f"\n  REEL — {job}")
    print(f"  {len(items)} items · ~{plan:.0f}s · grade {cfg.get('grade', 'none')} · "
          f"pacing {cfg.get('pacing', 'balanced')} · beat-sync {'on' if beat else 'off'} · "
          f"outputs {', '.join(aspects)}{' · PREVIEW' if preview else ''}{' · 4K' if uhd else ''}")
    for it in items:
        name = (it.get("card", {}).get("title") if it["kind"] == "card" else
                it.get("map") if it["kind"] == "map" else os.path.basename(it["path"]))
        print(f"    {it['kind']:5} {str(name)[:42]:42} {it['seconds']:>5}s  {it.get('label', '')}")
    if "--probe" in args:
        print("\n  (--probe: plan only, nothing rendered)\n")
        return

    out_dir = args[args.index("--out") + 1] if "--out" in args else os.path.join(REEL, "out", job)
    os.makedirs(out_dir, exist_ok=True)
    print()
    results = [render_aspect(cfg, items, a, job_dir, out_dir, beat, uhd) for a in aspects]
    avg = round(sum(r["qc"]["score"] for r in results) / len(results), 1)
    manifest = {"job": job, "property": cfg.get("property", {}), "grade": cfg.get("grade", "none"),
                "pacing": cfg.get("pacing", "balanced"), "beat_sync_bpm": round(60 / beat) if beat else None,
                "preview": preview, "uhd": uhd, "rendered": results, "qc_score": avg,
                "all_pass": all(r["qc"]["pass"] for r in results),
                "spec": {"codec": "h264", "fps": FPS, "bitrate": VIDEO_BITRATE, "audio_lufs": AUDIO_LUFS}}
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  Output → {os.path.relpath(out_dir)}/ — machine QC {avg}/5 "
          f"({'all pass' if manifest['all_pass'] else 'FIX BEFORE SHIPPING'}). "
          f"Now watch it end to end.\n")


if __name__ == "__main__":
    main()
