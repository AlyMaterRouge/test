#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server without password
x11vnc -forever -shared -nopw -display :99 &

# Start noVNC without authentication
# use the PORT env that Render sets
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen $PORT


# Start Flask app
gunicorn -w 4 -b 0.0.0.0:5000 linkedin_bot:app
