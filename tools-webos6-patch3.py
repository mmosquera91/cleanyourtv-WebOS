#!/usr/bin/env python3
"""Patch round 3: Node 8 has no http(s).get(url, options, cb) (added in Node 10.9). Shim it in every module that uses it."""
import sys, pathlib
R = pathlib.Path(sys.argv[1])
SHIM = ("[require('http'), require('https')].forEach(lib => { if (lib.__n8) return; const o = lib.get; lib.__n8 = true;   // Node 8: get(url, options, cb)\n"
        "  lib.get = function (u, op, cb) { if (typeof op === 'function' || op === undefined) return o.call(lib, u, op);\n"
        "    const p = require('url').parse(typeof u === 'string' ? u : String(u.href || u)); return o.call(lib, Object.assign({}, p, op), cb); }; });\n")
for f in ['helper/manager.js', 'helper/live.js', 'helper/notify.js', 'helper/voice.js']:
    p = R / f; s = p.read_text()
    if 'lib.__n8' in s: print('UNCHANGED', f); continue
    lines = s.split('\n')
    i = next(i for i, l in enumerate(lines) if l.startswith('const ') and 'require(' in l)
    lines.insert(i + 1, SHIM.rstrip('\n'))
    p.write_text('\n'.join(lines)); print('patched  ', f)
h = R / 'helper/helper.js'; s = h.read_text(); h.write_text(s.replace("const VERSION = '1.5.1';", "const VERSION = '1.5.2';")); print('version 1.5.2')
