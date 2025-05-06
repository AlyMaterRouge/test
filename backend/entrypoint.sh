#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server
x11vnc -forever -shared -nopw -display :99 &

# Start noVNC proxy on its internal port 6080
/opt/novnc/utils/novnc_proxy \
  --vnc localhost:5900 \
  --listen 6080 \
  --heartbeat 10 &

# Finally, start Flask via Gunicorn bound to localhost:5000
exec gunicorn -w 4 -b 127.0.0.1:5000 linkedin_bot:app
