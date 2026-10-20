from pathlib import Path
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site').resolve()
class Page(HTMLParser):
 def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
pages={p:Page(p.read_text(encoding='utf-8')) for p in root.rglob('*.html')}
errors=[];videos=0
if not pages:errors.append('No built HTML pages found')
for path,page in pages.items():
 label=str(path.relative_to(root));ids=Counter(a['id'] for _,a in page.tags if 'id' in a)
 for key,count in ids.items():
  if count>1:errors.append(f'{label}: duplicate id {key}')
 for tag,attrs in page.tags:
  if tag=='img' and 'alt' not in attrs:errors.append(f'{label}: image without alt')
  if tag=='video':
   videos+=1
   if 'controls' not in attrs or 'autoplay' in attrs:errors.append(f'{label}: video needs controls and no autoplay')
  references=[attrs[k] for k in ('href','src','poster') if k in attrs]
  references += [part.strip().split()[0] for part in attrs.get('srcset','').split(',') if part.strip()]
  for ref in references:
   url=urlsplit(ref)
   if url.scheme or url.netloc:continue
   target=root/unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent/unquote(url.path)
   if not url.path:target=path
   if target.is_dir():target=target/'index.html'
   target=target.resolve()
   if not target.exists():errors.append(f'{label}: missing target {ref}')
   elif url.fragment and target in pages and not any(a.get('id')==unquote(url.fragment) or (tag=='a' and a.get('name')==unquote(url.fragment)) for tag,a in pages[target].tags):errors.append(f'{label}: missing anchor {ref}')
if errors:
 print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(pages)} HTML pages; local links, image variants, anchors, unique IDs, image alt attributes and {videos} controlled videos.')
