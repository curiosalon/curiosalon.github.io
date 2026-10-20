from pathlib import Path
import subprocess,re,shlex,json
from PIL import Image
r=Path(r'V:\src\web');out=Path(r'C:\Users\Ted\Documents\ChatGPT\Curio Museum Blog\audit-checks');out.mkdir(exist_ok=True)
ff=r'C:\ffmpeg\ffmpeg.exe'
def run(args):
 p=subprocess.run([ff,'-hide_banner','-loglevel','error','-y',*args],cwd=out,capture_output=True,text=True,timeout=25)
 if p.returncode:raise RuntimeError(p.stderr[-2000:])
run(['-f','lavfi','-i','testsrc2=s=228x228:r=25:d=0.2','-c:v','libx264','map.mp4'])
for i in range(1,7):Image.new('RGBA',(228,228),(255,0,0,100)).save(out/f'timer{i:04d}.tif')
import shutil
shutil.copyfile(r/'assets/images/mapcompass-1.png',out/'mapcompass-1.png')
s=(r/'_posts/2020-04-23-ffmpeg-alpha-masking.md').read_text(encoding='utf-8');results=[]
for block in re.findall(r'```[^\n]*\n(.*?)```',s,re.S):
 if not block.startswith('ffmpeg '):continue
 for command in block.replace('^\n','').strip().splitlines():
  if not command.startswith('ffmpeg '):continue
  args=[v[1:-1] if v.startswith('"') and v.endswith('"') else v for v in shlex.split(command,posix=False)][1:]
  if '-t' in args:args[args.index('-t')+1]='0.2'
  if args[-1]=='NUL':args[-1]='pass1.webm'
  try:run(args);results.append({'command':command,'pass':True})
  except Exception as e:results.append({'command':command,'pass':False,'error':str(e)})
# Confirm generated alpha really survives decoding; codec metadata alone is insufficient.
for name in ['timer.webm','maskedmap.webm','finishedmap.webm']:
 try:
  run(['-c:v','libvpx-vp9','-i',name,'-vf','alphaextract','-frames:v','1',name+'.png'])
  im=Image.open(out/(name+'.png'));extrema=im.getextrema();results.append({'alpha':name,'extrema':extrema,'pass':extrema[0]<255})
 except Exception as e:results.append({'alpha':name,'pass':False,'error':str(e)})
(out/'ffmpeg-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))

assert all(item["pass"] for item in results), "One or more FFmpeg checks failed"
