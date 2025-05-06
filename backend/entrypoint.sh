#!/usr/bin/env bash
set -euo pipefail

echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Starting entrypoint.sh..."

# 1. Start Xvfb for headless Chrome
echo "[$(date +'%H:%M:%S')] Launching Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# 2. Start window manager
echo "[$(date +'%H:%M:%S')] Launching Fluxbox..."
fluxbox &

# 3. Start VNC server
echo "[$(date +'%H:%M:%S')] Launching x11vnc on :99..."
x11vnc -forever -shared -nopw -display :99 &

# 4. Start noVNC web client internally on port 6080
echo "[$(date +'%H:%M:%S')] Launching noVNC proxy on 6080..."
/opt/novnc/utils/novnc_proxy \
  --vnc localhost:5900 \
  --listen 6080 \
  --heartbeat 10 &

# 5. Start Gunicorn bound to localhost:5000
echo "[$(date +'%H:%M:%S')] Launching Gunicorn..."
exec gunicorn -w 4 -b 127.0.0.1:5000 linkedin_bot:app
