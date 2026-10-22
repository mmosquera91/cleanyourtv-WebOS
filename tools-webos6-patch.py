#!/usr/bin/env python3
"""Patch cleanyourtv-WebOS for webOS 6 (Node 8, Chromium 79) and pin updates to Miguel's fork."""
import re, sys, pathlib

R = pathlib.Path(sys.argv[1])
FORK = 'mmosquera91/cleanyourtv-WebOS'

def edit(rel, fn):
    p = R / rel
    s = p.read_text()
    n = fn(s)
    if n == s:
        print('UNCHANGED', rel)
    else:
        p.write_text(n)
        print('patched  ', rel)

NODE8_URL = "const { URL, URLSearchParams } = require('url');   // Node 8 (webOS 6) has no global URL\n"
MKDIRP = ("const mkdirp = d => { try { require('fs').mkdirSync(d); } catch (e) {   // Node 8 has no {recursive: true}\n"
          "  if (e.code === 'ENOENT') { mkdirp(require('path').dirname(d)); require('fs').mkdirSync(d); } else if (e.code !== 'EEXIST') throw e; } };\n")

def first_require_line(s):
    # insert after the first line that starts with "const " and contains require(
    lines = s.split('\n')
    for i, l in enumerate(lines):
        if l.startswith('const ') and 'require(' in l:
            return i
    raise SystemExit('no require line')

def add_after_require(extra):
    def f(s):
        if extra.strip() in s:
            return s
        lines = s.split('\n')
        i = first_require_line(s)
        lines.insert(i + 1, extra.rstrip('\n'))
        return '\n'.join(lines)
    return f

def mkdir_calls(s):
    return re.sub(r"fs\.mkdirSync\(([^,()]+), \{ recursive: true \}\)", r"mkdirp(\1)", s)

for f in ['helper/live.js', 'helper/notify.js', 'helper/manager.js', 'helper/voice.js']:
    edit(f, add_after_require(NODE8_URL))
for f in ['helper/live.js', 'helper/voice.js', 'helper/inputhook.js']:
    edit(f, lambda s: mkdir_calls(add_after_require(MKDIRP)(s)))

# updates and the compatibility list only from the fork
for f in ['helper/manager.js', 'helper/selfupdate.js']:
    edit(f, lambda s: s.replace("DEFAULT_REPO = 'lasharor/cleanyourtv-WebOS'", "DEFAULT_REPO = '%s'" % FORK))
edit('scripts/bootstrap.sh', lambda s: s.replace('COMPATREPO=lasharor/cleanyourtv-WebOS', 'COMPATREPO=' + FORK))
edit('install.sh', lambda s: s.replace('${CYTV_REPO:-lasharor/cleanyourtv-WebOS}', '${CYTV_REPO:-%s}' % FORK))

# Chromium 79 (webOS 6) ignores `gap` on flex containers: emulate it with margins
POLY = """<script>/* flex-gap polyfill for Chromium < 84 (webOS 6) */(function(){
var t=document.createElement('div');t.style.cssText='display:flex;flex-direction:column;row-gap:1px;position:absolute';t.appendChild(document.createElement('div'));t.appendChild(document.createElement('div'));
function go(){document.body.appendChild(t);var ok=t.scrollHeight===1;document.body.removeChild(t);if(ok)return;
function fix(){var els=document.querySelectorAll('*');for(var i=0;i<els.length;i++){var e=els[i],cs=getComputedStyle(e);if(cs.display.indexOf('flex')<0)continue;
var cg=parseFloat(cs.columnGap)||0,rg=parseFloat(cs.rowGap)||0;if(!cg&&!rg)continue;var col=cs.flexDirection.indexOf('column')===0,first=true;
for(var c=e.firstElementChild;c;c=c.nextElementSibling){if(getComputedStyle(c).position==='absolute'||getComputedStyle(c).display==='none')continue;
if(first){first=false;continue;}if(col){if(!c.style.marginTop)c.style.marginTop=rg+'px';}else{if(!c.style.marginLeft)c.style.marginLeft=cg+'px';}}}}
fix();var pend=0;new MutationObserver(function(){if(pend)return;pend=setTimeout(function(){pend=0;fix();},50);}).observe(document.body,{childList:true,subtree:true});}
if(document.body)go();else document.addEventListener('DOMContentLoaded',go);})();</script>
"""
def add_poly(s):
    if 'flex-gap polyfill' in s:
        return s
    return s.replace('</body>', POLY + '</body>', 1) if '</body>' in s else s + POLY
for f in ['app/index.html', 'manager/app/index.html', 'picker/app/index.html', 'notify/app/index.html']:
    edit(f, add_poly)
