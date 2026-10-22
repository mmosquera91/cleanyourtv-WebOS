#!/bin/sh
# Reload the Home page for real (fork). On webOS 6 WebAppMgr keeps the replaced Home's renderer alive: relaunching it
# only re-foregrounds the old page and pkill on app-id= matches nothing, so restart webapp-mgr there. Newer webOS:
# kill the Home renderer and launch it again (upstream behaviour).
export PATH=/usr/bin:/usr/sbin:/bin:/sbin:$PATH
if pgrep -f "[a]pp-id=com.webos.app.home" >/dev/null; then
  pkill -f "[a]pp-id=com.webos.app.home"; sleep 2
elif systemctl cat webapp-mgr.service >/dev/null 2>&1; then
  systemctl restart webapp-mgr
  for i in $(seq 1 30); do systemctl is-active webapp-mgr >/dev/null && break; sleep 1; done
  sleep 3
fi
luna-send -n 1 -w 10000 -f luna://com.webos.applicationManager/launch '{"id":"com.webos.app.home"}' </dev/null >/dev/null
