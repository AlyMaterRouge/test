#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server (no password, localhost-only)
x11vnc -forever -shared -nopw -display :99 -localhost -rfbport 5900 &

# Start websockify in the background
/opt/novnc/utils/websockify --web /opt/novnc 5901 localhost:5900 &

# Start Flask app
gunicorn -w 4 -b 0.0.0.0:5000 linkedin_bot:app
