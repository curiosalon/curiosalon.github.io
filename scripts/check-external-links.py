from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,urldefrag
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json
r=Path(r'C:\Users\Ted\Documents\ChatGPT\Curio Museum Blog\preview-site')
class P(HTMLParser):
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ('href','src') and v.startswith('https://') and urlsplit(v).hostname!='curiosalon.github.io':urls.add(urldefrag(v)[0])
urls=set()
for p in r.rglob('*.html'):P().feed(p.read_text(encoding='utf-8'))
def check(u):
 try:
  with urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0 CurioMuseumLinkAudit'}),timeout=15) as res:return {'url':u,'status':res.status,'final_url':res.url}
 except Exception as e:return {'url':u,'error':str(e)}
results=list(ThreadPoolExecutor(max_workers=6).map(check,sorted(urls)))
Path(r'C:\Users\Ted\Documents\ChatGPT\Curio Museum Blog\audit-checks\external-links.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
