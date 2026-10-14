#!/usr/bin/env python3
"""Generate throwaway test media for the demo job (no client footage in git).

  python3 reel/jobs/_demo/make_demo_media.py      → reel/jobs/_demo/media/
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "media")
os.makedirs(MEDIA, exist_ok=True)
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def still(name, top, bottom, label):
    w, h = 3000, 2000
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)))
    for k in range(0, w, 250):          # "architecture" so Ken Burns motion is visible
        d.rectangle([k + 40, h * 0.45, k + 200, h * 0.95], outline=(255, 255, 255), width=6)
    f = ImageFont.truetype(FONT, 160) if os.path.exists(FONT) else None
    d.text((120, 120), label, fill=(255, 255, 255), font=f)
    img.save(os.path.join(MEDIA, name), quality=92)


still("01_hero_twilight.jpg", (20, 30, 80), (230, 120, 60), "HERO — TWILIGHT")
still("02_lobby.jpg", (200, 190, 170), (120, 90, 60), "LOBBY")
still("03_pool.jpg", (60, 160, 220), (20, 80, 120), "POOL")
still("04_unit.jpg", (235, 230, 220), (160, 140, 120), "STANDARD UNIT")

# site plan for the map segment
sp = Image.new("RGB", (2400, 1600), (70, 90, 70))
d = ImageDraw.Draw(sp)
for x in range(0, 2400, 300):
    d.rectangle([x, 0, x + 40, 1600], fill=(140, 140, 140))      # streets
for y in range(0, 1600, 300):
    d.rectangle([0, y, 2400, y + 40], fill=(140, 140, 140))
d.rectangle([1150, 700, 1400, 900], fill=(180, 170, 150))          # the parcel
sp.save(os.path.join(MEDIA, "siteplan.jpg"), quality=90)

ff = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
# "drone" clip, 6 s, 4K-ish source so reframe/crop has room
subprocess.run(ff + ["-f", "lavfi", "-i", "testsrc2=s=2560x1440:r=30:d=6",
                     "-c:v", "libx264", "-preset", "ultrafast", os.path.join(MEDIA, "05_drone.mp4")], check=True)
# 40 s music bed at 120 BPM: a kick every 0.5 s under a soft pad
subprocess.run(ff + ["-f", "lavfi", "-i",
                     "aevalsrc='0.5*sin(2*PI*55*t)*exp(-12*mod(t,0.5))+0.08*sin(2*PI*220*t)+0.05*sin(2*PI*330*t)':s=48000:d=40",
                     "-ac", "2", "-c:a", "aac", os.path.join(MEDIA, "music.m4a")], check=True)
print(f"  ✓ demo media → {MEDIA}")
