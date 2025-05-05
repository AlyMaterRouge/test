#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server without password
x11vnc -forever -shared -nopw -display :99 &

# Start noVNC without authentication
# use the PORT env that Render sets
# Serve /opt/novnc as static under /novnc, proxy WS at /novnc/websockify
/opt/novnc/utils/novnc_proxy \
  --web /opt/novnc \
  --wrap-mode=once \
  --web=/opt/novnc \
  --ws-path /novnc/websockify \
  --vnc localhost:5900 \
  --listen $PORT



# Start Flask app
gunicorn -w 4 -b 0.0.0.0:5000 linkedin_bot:app
