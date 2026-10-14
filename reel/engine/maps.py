#!/usr/bin/env python3
"""
REEL MAPS — the animated location map (the THOMAS signature beat).

Builds the "Marina"-style map segment in-house: a slow push in on the base map,
the property outline drawing on, a property badge, road labels, then POI
badges popping in one by one with drive times. Rendered with Pillow, piped
straight into ffmpeg — no After Effects, no API keys.

Two base options:
  • "image"     — any local picture: a site plan, a Google Earth / Maps screenshot
                  the client approved, a still frame from the drone. Points are
                  pixel coords on that image, or 0–1 fractions.
  • "satellite" — stitched Esri World Imagery tiles around a lat/lon (needs
                  network to server.arcgisonline.com; POIs with no point are
                  looked up on OpenStreetMap). Points are [lat, lon].

Style "dark" = the house standard (dark-navy styled base, navy pills, white
text); "photo" keeps the imagery natural.

Map config (JSON), referenced from a job as {"map": "map.json", "seconds": 8}:
{
  "base": "image", "image": "media/siteplan.jpg",
  "style": "dark",
  "property": {"label": "THE LOFT", "point": [0.52, 0.48],
               "outline": [[0.48,0.44],[0.57,0.44],[0.57,0.53],[0.48,0.53]]},
  "roads": [{"name": "I-275", "at": [0.30, 0.20]}],
  "pois": [{"name": "Whole Foods", "note": "3 min", "point": [0.70, 0.35]}],
  "push": 1.25
}

CLI preview:  python3 reel/engine/maps.py map.json out.mp4 [seconds] [16:9|9:16]
"""

import json
import math
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
UA = {"User-Agent": "THOMAS-Productions-mapper/1.0"}


def _font(bold):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
              ["/System/Library/Fonts/Supplemental/Arial.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        if os.path.exists(p):
            return p
    return None


FONT_BOLD, FONT_REG = _font(True), _font(False)


def font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, max(8, int(size))) if path else ImageFont.load_default()


def hex_rgb(h, default):
    h = str(h or default).lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- satellite base
def ll_to_world(lat, lon, z):
    n = 256 * (2 ** z)
    s = math.sin(math.radians(lat))
    return (lon + 180.0) / 360.0 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def fetch(url, binary=True, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                data = r.read()
            return data if binary else data.decode("utf-8")
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


class SatMap:
    """Stitched satellite image centered on (lat, lon) at zoom z, w×h px."""

    def __init__(self, lat, lon, z, w, h, cache_dir=None):
        self.z = z
        cx, cy = ll_to_world(lat, lon, z)
        self.origin = (cx - w / 2, cy - h / 2)
        cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "tile_cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.img = Image.new("RGB", (w, h))
        for ty in range(int(self.origin[1] // 256), int((self.origin[1] + h) // 256) + 1):
            for tx in range(int(self.origin[0] // 256), int((self.origin[0] + w) // 256) + 1):
                cp = os.path.join(cache_dir, f"{z}_{tx}_{ty}.jpg")
                if not os.path.exists(cp):
                    with open(cp, "wb") as f:
                        f.write(fetch(TILE_URL.format(z=z, x=tx, y=ty)))
                try:
                    self.img.paste(Image.open(cp).convert("RGB"),
                                   (int(tx * 256 - self.origin[0]), int(ty * 256 - self.origin[1])))
                except Exception:
                    continue

    def px(self, lat, lon):
        x, y = ll_to_world(lat, lon, self.z)
        return x - self.origin[0], y - self.origin[1]


def overpass(query):
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": query}).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def find_poi(name, center, radius_m=9000):
    """Nearest OSM feature named like `name` around center=(lat, lon), or None."""
    lat, lon = center
    q = f'[out:json][timeout:25];(nwr["name"~"{name}",i](around:{radius_m},{lat},{lon}););out center 5;'
    try:
        best, bestd = None, 1e18
        for el in overpass(q).get("elements", []):
            la = el.get("lat") or el.get("center", {}).get("lat")
            lo = el.get("lon") or el.get("center", {}).get("lon")
            if la is not None and (la - lat) ** 2 + (lo - lon) ** 2 < bestd:
                best, bestd = (la, lo), (la - lat) ** 2 + (lo - lon) ** 2
        time.sleep(1.0)
        return best
    except Exception:
        return None


# ---------------------------------------------------------------- base + coordinates
def load_base(cfg, cfg_dir, w, h, push):
    """Return (base RGB image covering w*push × h*push, to_px(point) → base pixel)."""
    bw, bh = int(w * push * 1.05), int(h * push * 1.05)
    if cfg.get("base", "image") == "satellite":
        lat, lon = cfg["center"]
        sm = SatMap(lat, lon, int(cfg.get("zoom", 15)), bw, bh)
        img, to_px = sm.img, (lambda p: sm.px(p[0], p[1]))
        for poi in cfg.get("pois", []):
            if not poi.get("point"):
                poi["point"] = find_poi(poi["name"], (lat, lon))
        return img, to_px
    path = cfg["image"] if os.path.isabs(cfg["image"]) else os.path.join(cfg_dir, cfg["image"])
    src = Image.open(path).convert("RGB")
    sw, sh = src.size
    k = max(bw / sw, bh / sh)
    img = src.resize((int(sw * k + 0.5), int(sh * k + 0.5)), Image.LANCZOS)
    ox, oy = (img.width - bw) / 2, (img.height - bh) / 2
    img = img.crop((int(ox), int(oy), int(ox) + bw, int(oy) + bh))

    def to_px(p):
        x, y = p
        if 0 <= x <= 1 and 0 <= y <= 1:   # fractions of the source image
            x, y = x * sw, y * sh
        return x * k - ox, y * k - oy
    return img, to_px


def style_base(img, style, brand):
    if style != "dark":
        return ImageEnhance.Contrast(img).enhance(1.05)
    navy = hex_rgb(brand.get("map_bg"), "#0E1E33")
    g = ImageEnhance.Brightness(img.convert("L")).enhance(0.75)
    g = ImageEnhance.Contrast(g).enhance(1.25).convert("RGB")
    tint = Image.new("RGB", img.size, navy)
    return Image.blend(g, tint, 0.55)


# ---------------------------------------------------------------- drawing
def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def pop(t):
    """0→1 with a little overshoot — badges 'pop' in."""
    t = max(0.0, min(1.0, t))
    return 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2 if t < 1 else 1.0


def draw_outline(d, pts, color, width, frac):
    pts = list(pts) + [pts[0]]
    segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    remain = sum(s[2] for s in segs) * max(0.0, min(1.0, frac))
    for a, b, L in segs:
        if remain <= 0:
            break
        if L <= remain:
            d.line([a, b], fill=color, width=width)
            remain -= L
        else:
            t = remain / L
            d.line([a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)], fill=color, width=width)
            remain = 0
        r = width / 2
        d.ellipse([a[0] - r, a[1] - r, a[0] + r, a[1] + r], fill=color)


def badge(layer, anchor, text, note, s, alpha, fill, fg, accent, side=-1):
    """Navy pill with white text + drive-time note, leader line down to an anchor dot."""
    d = ImageDraw.Draw(layer)
    f1, f2 = font(30 * s), font(22 * s, bold=False)
    tw = d.textlength(text, font=f1)
    nw = d.textlength(note, font=f2) if note else 0
    pad_x, pad_y = 22 * s, 12 * s
    w = max(tw, nw) + 2 * pad_x
    h = 34 * s + (26 * s if note else 0) + 2 * pad_y
    x, y = anchor
    lead = 70 * s
    W, H = layer.size
    if side < 0 and y - lead - h < 12 * s:      # no room above → hang below
        side = 1
    elif side > 0 and y + lead + h > H - 12 * s:
        side = -1
    by = (y - lead - h) if side < 0 else (y + lead)
    bx = min(max(x - w / 2, 16 * s), W - w - 16 * s)   # keep the pill on screen
    a = int(255 * alpha)
    lc = (*fg, int(a * 0.9))
    d.line([(x, y), (x, by + h if side < 0 else by)], fill=lc, width=max(2, int(3 * s)))
    d.rounded_rectangle([bx + 3 * s, by + 4 * s, bx + w + 3 * s, by + h + 4 * s], radius=int(h / 2.6),
                        fill=(0, 0, 0, int(a * 0.35)))
    d.rounded_rectangle([bx, by, bx + w, by + h], radius=int(h / 2.6), fill=(*fill, a),
                        outline=(*accent, a), width=max(1, int(2 * s)))
    mx = bx + w / 2
    d.text((mx - tw / 2, by + pad_y - 2 * s), text, font=f1, fill=(*fg, a))
    if note:
        d.text((mx - nw / 2, by + pad_y + 36 * s), note, font=f2, fill=(*accent, a))
    r = 8 * s
    d.ellipse([x - r, y - r, x + r, y + r], fill=(*accent, a), outline=(*fg, a), width=max(1, int(3 * s)))


def road_label(layer, xy, text, s, alpha):
    d = ImageDraw.Draw(layer)
    f = font(28 * s)
    a = int(255 * alpha)
    tw = d.textlength(text, font=f)
    x, y = xy
    W, H = layer.size
    x = min(max(x, tw / 2 + 20 * s), W - tw / 2 - 20 * s)
    y = min(max(y, 28 * s), H - 28 * s)
    d.rounded_rectangle([x - tw / 2 - 12 * s, y - 20 * s, x + tw / 2 + 12 * s, y + 20 * s],
                        radius=int(6 * s), fill=(255, 255, 255, int(a * 0.92)))
    d.text((x - tw / 2, y - 16 * s), text, font=f, fill=(20, 30, 50, a))


# ---------------------------------------------------------------- render
def render_frames(cfg, cfg_dir, w, h, seconds, fps, brand):
    brand = brand or {}
    push = float(cfg.get("push", 1.25))
    base, to_px = load_base(cfg, cfg_dir, w, h, push)
    base = style_base(base, cfg.get("style", "dark"), brand)
    fill = hex_rgb(brand.get("map_badge"), "#0F2340")
    fg = hex_rgb(brand.get("fg"), "#FFFFFF")
    accent = hex_rgb(brand.get("accent"), "#C8A24B")
    s = min(w, h) / 1080.0
    prop = cfg.get("property", {})
    ppt = to_px(prop["point"]) if prop.get("point") else (base.width / 2, base.height / 2)
    outline = [to_px(p) for p in prop.get("outline", [])]
    roads = [(r["name"], to_px(r["at"])) for r in cfg.get("roads", []) if r.get("at")]
    pois = [(p["name"], p.get("note", ""), to_px(p["point"])) for p in cfg.get("pois", []) if p.get("point")]
    n = int(round(seconds * fps))
    bw, bh = base.size

    for i in range(n):
        t = i / max(1, n - 1)
        z = 1 + (push - 1) * ease(t)          # camera push toward the property
        cw, ch = bw / z, bh / z
        cx = min(max(ppt[0], cw / 2), bw - cw / 2)
        cy = min(max(ppt[1], ch / 2), bh - ch / 2)
        cx = bw / 2 + (cx - bw / 2) * ease(t)
        cy = bh / 2 + (cy - bh / 2) * ease(t)
        x0, y0 = cx - cw / 2, cy - ch / 2
        k = w / cw
        frame = base.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")

        def fp(p):
            return ((p[0] - x0) * k, (p[1] - y0) * k)

        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if outline:
            fr = ease((t - 0.12) / 0.3)
            if fr > 0:
                pts = [fp(p) for p in outline]
                if fr >= 1:
                    d.polygon(pts, fill=(*accent, 55))
                draw_outline(d, pts, (*accent, 255), max(3, int(6 * s)), fr)
        for j, (name, xy) in enumerate(roads):
            road_label(layer, fp(xy), name, s, ease((t - 0.25 - 0.05 * j) / 0.12))
        for j, (name, note, xy) in enumerate(pois):
            start = 0.42 + 0.4 * j / max(1, len(pois))
            al = ease((t - start) / 0.08)
            if al > 0:
                badge(layer, fp(xy), name, note, s * pop((t - start) / 0.12), al, fill, fg, accent,
                      side=-1 if j % 2 == 0 else 1)
        if prop.get("label"):
            al = ease((t - 0.3) / 0.1)
            if al > 0:
                badge(layer, fp(ppt), prop["label"], prop.get("note", ""), 1.35 * s * pop((t - 0.3) / 0.14),
                      al, fill, fg, accent)
        frame.alpha_composite(layer)
        yield frame.convert("RGB").tobytes()


def render_segment(cfg_path, out, w, h, seconds, fps=30, brand=None, preset="veryfast"):
    with open(cfg_path) as f:
        cfg = json.load(f)
    cfg_dir = os.path.dirname(os.path.abspath(cfg_path))
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
                             "-preset", preset, "-crf", "18", "-pix_fmt", "yuv420p", out],
                            stdin=subprocess.PIPE)
    for buf in render_frames(cfg, cfg_dir, w, h, seconds, fps, brand):
        proc.stdin.write(buf)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("map render failed")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 8
    W, H = (1080, 1920) if len(sys.argv) > 4 and sys.argv[4] == "9:16" else (1920, 1080)
    render_segment(sys.argv[1], sys.argv[2], W, H, secs)
    print(f"  ✓ map → {sys.argv[2]}")
