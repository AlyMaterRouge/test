#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server (localhost only)
x11vnc -forever -shared -nopw -display :99 -localhost -rfbport 5900 &

# Configure websockify to use the same port as Flask
/opt/novnc/utils/websockify --web /opt/novnc --wrap-mode=ignore 5000 localhost:5900 &

# Start Flask app
gunicorn -w 4 -b 0.0.0.0:5000 linkedin_bot:app
