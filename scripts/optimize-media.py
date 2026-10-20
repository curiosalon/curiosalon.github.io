from pathlib import Path
import subprocess,json,re
from PIL import Image
r=Path(r'V:\src\web');out=r/'assets/images/optimized';out.mkdir(exist_ok=True)
files=set()
for p in (r/'_posts').glob('*.md'):files.update(re.findall(r'image_path="(/assets/images/[^"]+)"',p.read_text(encoding='utf-8')))
files.add('/assets/images/vi-domina-header.png')
manifest={};before=after=0
for u in sorted(files):
 p=r/u.lstrip('/');im=Image.open(p);w,h=im.size;variants=[]
 for width in sorted({min(w,640),min(w,1280),min(w,1600)}):
  dest=out/(p.stem+'-'+str(width)+'.webp')
  args=[r'C:\ffmpeg\ffmpeg.exe','-v','error','-y','-i',str(p),'-vf',f'scale={width}:-1:flags=lanczos','-frames:v','1','-c:v','libwebp','-quality','88','-compression_level','6',str(dest)]
  subprocess.run(args,check=True,timeout=40,capture_output=True)
  variants.append({'url':'/assets/images/optimized/'+dest.name,'width':width,'bytes':dest.stat().st_size})
 manifest[u]={'width':w,'height':h,'variants':variants,'original_bytes':p.stat().st_size}
 before+=p.stat().st_size;after+=variants[-1]['bytes']
(r/'_data/media.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'images':len(manifest),'original_bytes':before,'largest_webp_bytes':after,'saved_percent':round((1-after/before)*100,1)}))
