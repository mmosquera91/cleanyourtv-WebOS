#!/usr/bin/env python3
"""Second patch round for Miguel's fork: polyfill v2 (tracks its own margins), hideable 'Restore LG Home' tile, version bump."""
import re, sys, pathlib, json
R = pathlib.Path(sys.argv[1])

POLY2 = """<script>/* flex-gap polyfill v2 for Chromium < 84 (webOS 6) */(function(){
var t=document.createElement('div');t.style.cssText='display:flex;flex-direction:column;row-gap:1px;position:absolute';t.appendChild(document.createElement('div'));t.appendChild(document.createElement('div'));
function go(){document.body.appendChild(t);var ok=t.scrollHeight===1;document.body.removeChild(t);if(ok)return;
function fix(){var old=document.querySelectorAll('[data-fg]');for(var k=0;k<old.length;k++){old[k].style.marginTop='';old[k].style.marginLeft='';old[k].removeAttribute('data-fg')}
var els=document.querySelectorAll('*');for(var i=0;i<els.length;i++){var e=els[i],cs=getComputedStyle(e);if(cs.display.indexOf('flex')<0)continue;
var cg=parseFloat(cs.columnGap)||0,rg=parseFloat(cs.rowGap)||0;if(!cg&&!rg)continue;var col=cs.flexDirection.indexOf('column')===0,first=true;
for(var c=e.firstElementChild;c;c=c.nextElementSibling){var ccs=getComputedStyle(c);if(ccs.position==='absolute'||ccs.display==='none')continue;
if(first){first=false;continue;}if(col){if(!c.style.marginTop){c.style.marginTop=rg+'px';c.setAttribute('data-fg','')}}else{if(!c.style.marginLeft){c.style.marginLeft=cg+'px';c.setAttribute('data-fg','')}}}}}
fix();var pend=0;new MutationObserver(function(m){for(var j=0;j<m.length;j++)if(m[j].type==='childList'){if(pend)return;pend=setTimeout(function(){pend=0;fix();},50);return}}).observe(document.body,{childList:true,subtree:true});}
if(document.body)go();else document.addEventListener('DOMContentLoaded',go);})();</script>
"""

def edit(rel, fn):
    p = R / rel; s = p.read_text(); n = fn(s)
    print(('patched   ' if n != s else 'UNCHANGED ') + rel); p.write_text(n)

def poly(s):
    s = re.sub(r"<script>/\* flex-gap polyfill.*?</script>\n?", "", s, flags=re.S)
    return s.replace('</body>', POLY2 + '</body>', 1) if '</body>' in s else s + POLY2
for f in ['app/index.html', 'manager/app/index.html', 'picker/app/index.html', 'notify/app/index.html']:
    edit(f, poly)

def undo(s):
    s = s.replace("  rest.push({id:'__undo',title:t('Restore LG Home'),sys:true,icon:'restore'});",
                  "  if(!isHidden('__undo'))rest.push({id:'__undo',title:t('Restore LG Home'),sys:true,icon:'restore'});   /* hideable (fork) */")
    s = s.replace("function title(id){for(", "function title(id){if(id==='__undo')return t('Restore LG Home');for(")
    s = s.replace("var h=(cfg.hidden||[]).filter(function(id){return apps.some(function(a){return a.id===id})});",
                  "var h=(cfg.hidden||[]).filter(function(id){return id==='__undo'||apps.some(function(a){return a.id===id})});")
    s = s.replace("  if(e._a&&!e._a.sys)appMenu(e._a);",
                  "  if(e._a&&e._a.id==='__undo')openMenu(t('Restore LG Home'),[{label:t('Hide app'),fn:function(){hideApp('__undo')}}]);\n  else if(e._a&&!e._a.sys)appMenu(e._a);")
    s = s.replace("VERSION='1.4.2'", "VERSION='1.4.3'")
    return s
edit('app/index.html', undo)
edit('app/version.json', lambda s: s.replace('"version":"1.4.2"', '"version":"1.4.3"'))
edit('helper/helper.js', lambda s: s.replace("const VERSION = '1.5.0';", "const VERSION = '1.5.1';"))
