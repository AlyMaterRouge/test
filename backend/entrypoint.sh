#!/usr/bin/env bash
set -euo pipefail

echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] entrypoint.sh: generating nginx.conf from template…"
# Substitute only the PORT variable into our template
envsubst '${PORT}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

echo "[$(date +'%H:%M:%S')] entrypoint.sh: testing nginx config…"
nginx -t

echo "[$(date +'%H:%M:%S')] entrypoint.sh: starting nginx…"
# Use the nginx binary directly so it stays running in the background
nginx

echo "[$(date +'%H:%M:%S')] entrypoint.sh: launching services…"

# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
fluxbox &

# VNC + noVNC
x11vnc -forever -shared -nopw -display :99 &
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 --heartbeat 10 &

# Finally, run Gunicorn in the foreground (PID 1)
exec gunicorn -w 4 -b 127.0.0.1:5000 linkedin_bot:app
