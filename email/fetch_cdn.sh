#!/bin/bash
# Pull every old-site Squarespace CDN image (from /tmp/sq.txt) into /tmp/sqimg and build a contact sheet.
mkdir -p /tmp/sqimg && cd /tmp/sqimg
n=0
while read -r u; do
  n=$((n+1)); f=$(printf '%03d' $n).jpg
  [ -s "$f" ] || curl -s -m 25 -o "$f" "$u?format=750w" &
  if [ $((n % 16)) = 0 ]; then wait; fi
done < /tmp/sq.txt
wait
ls | wc -l
/usr/bin/python3 - <<'E'
from PIL import Image, ImageDraw
import glob,os
fs=sorted(glob.glob('/tmp/sqimg/*.jpg'))
cols=10; W,H=240,160
rows=(len(fs)+cols-1)//cols
sheet=Image.new('RGB',(cols*W,rows*(H+14)),'white'); d=ImageDraw.Draw(sheet)
n=0
for f in fs:
    try:
        im=Image.open(f); im.draft('RGB',(W*2,H*2)); im=im.convert('RGB'); im.thumbnail((W,H))
    except Exception: continue
    x=(n%cols)*W;y=(n//cols)*(H+14); sheet.paste(im,(x,y)); d.text((x+2,y+H+1),os.path.basename(f)[:3],fill='black'); n+=1
out=os.path.expanduser('~/Desktop/Claude Code/10 THOMAS/03 MARKETING/thomas-site/deploy/email/_sheet-oldsite-cdn.jpg')
sheet.save(out,quality=70); print(n, sheet.size)
E
