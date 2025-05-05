#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server
x11vnc -forever -shared -nopw -display :99 -localhost &

# Start websockify
/opt/novnc/utils/websockify --web /opt/novnc 5901 localhost:5900 &

# Verify noVNC files
if [ ! -f "/opt/novnc/vnc.html" ]; then
    echo "ERROR: noVNC files missing!"
    exit 1
fi

# Start Flask app
gunicorn -w 4 -b 0.0.0.0:5000 linkedin_bot:app
