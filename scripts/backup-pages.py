"""Archive the publicly linked Documentation Library Pages without credentials."""
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE = 'https://docs.bradbarrish.com/'
OUT = Path(__file__).resolve().parents[1] / 'pages'

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_list = False; self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'ul' and 'post-list' in attrs.get('class', '').split(): self.in_list = True
        if self.in_list and tag == 'a': self.urls.append(urljoin(BASE, attrs['href']))
    def handle_endtag(self, tag):
        if tag == 'ul': self.in_list = False

class Body(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.parts = []; self.text = []; self.found = False
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and 'e-content' in dict(attrs).get('class', '').split():
            if self.depth: raise ValueError('Nested content container')
            self.depth = 1; self.found = True; return
        if self.depth:
            if tag == 'div': self.depth += 1
            self.parts.append(self.get_starttag_text())
    def handle_endtag(self, tag):
        if self.depth:
            if tag == 'div':
                self.depth -= 1
                if not self.depth: return
            self.parts.append('</'+tag+'>')
            if tag in ('p','li','h1','h2','h3','pre','blockquote'): self.text.append('\n')
    def handle_data(self, data):
        if self.depth:
            from html import escape
            self.parts.append(escape(data)); self.text.append(data)

def fetch(url):
    if urlparse(url).netloc != urlparse(BASE).netloc: raise ValueError('Unexpected host')
    with urlopen(Request(url, headers={'User-Agent':'DocumentationLibraryBackup/1.0'}), timeout=30) as r:
        if urlparse(r.url).netloc != urlparse(BASE).netloc: raise ValueError('Unexpected redirect host')
        return r.read().decode('utf-8')

home = fetch(BASE); links = Links(); links.feed(home)
urls = list(dict.fromkeys(links.urls))
if not urls: raise ValueError('Homepage contains no documentation links; preserving previous backup')
records = []
# Validate every document before writing any snapshots.
for url in urls:
    path = urlparse(url).path.strip('/')
    if not path or '/' in path or path in ('.','..'): raise ValueError('Expected date-free document path: '+url)
    source = fetch(url); body = Body(); body.feed(source)
    if not body.found or not ''.join(body.text).strip(): raise ValueError('Missing document content: '+url)
    records.append((path,url,source,''.join(body.parts),''.join(body.text).strip()+'\n'))
OUT.mkdir(exist_ok=True)
for path,url,source,content,text in records:
    folder=OUT/path;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(source,encoding='utf-8')
    (folder/'content.html').write_text(content,encoding='utf-8')
    (folder/'content.txt').write_text(text,encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps([{'url':url,'folder':path} for path,url,*_ in records],indent=2)+'\n',encoding='utf-8')
print(f'Backed up {len(records)} documentation Pages.')
