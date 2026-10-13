from PIL import Image, ImageDraw
import glob,os,json,sys
base=os.path.expanduser('~/THOMAS® Dropbox')
out=os.path.expanduser('~/Desktop/Claude Code/10 THOMAS/03 MARKETING/thomas-site/deploy/email')
for name,d in [('skyhouse','Skyhouse Dallas - Final Deliverable'),('west6th','West 6th - Final Deliverable')]:
    fs=sorted([f for f in glob.glob(base+'/'+d+'/**/*',recursive=True) if f.lower().endswith(('.jpg','.jpeg'))])
    cols=8; W,H=320,213
    rows=(len(fs)+cols-1)//cols
    s=Image.new('RGB',(cols*W,rows*H),'white'); dr=ImageDraw.Draw(s); idx=[]
    for i,f in enumerate(fs):
        try:
            im=Image.open(f); im.draft('RGB',(W*2,H*2)); im=im.convert('RGB'); im.thumbnail((W,H))
        except Exception: continue
        s.paste(im,((i%cols)*W,(i//cols)*H)); dr.rectangle(((i%cols)*W,(i//cols)*H,(i%cols)*W+44,(i//cols)*H+18),fill='black'); dr.text(((i%cols)*W+3,(i//cols)*H+3),str(i),fill='white'); idx.append(f)
    s.save(f'{out}/_sheet-{name}.jpg',quality=72); json.dump(idx,open(f'{out}/_sheet-{name}.json','w'))
    print(name,len(fs),s.size)
