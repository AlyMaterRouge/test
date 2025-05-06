#!/usr/bin/env bash
set -euo pipefail

# Generate nginx config first
echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Generating nginx.conf..."
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start Xvfb with display :99
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Wait for Xvfb to initialize
sleep 2

# Start fluxbox window manager
echo "Starting fluxbox..."
fluxbox &

# Start VNC server
echo "Starting x11vnc..."
x11vnc -forever -shared -nopw -display :99 -rfbport 5900 &

# Wait for VNC server to start
sleep 1

# Start noVNC proxy (WebSocket -> VNC)
echo "Starting noVNC..."
/opt/novnc/utils/novnc_proxy \
    --vnc localhost:5900 \
    --listen 6080 \
    --heartbeat 10 &

# Start Nginx after services
echo "Starting Nginx..."
nginx

# Start Flask app
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 127.0.0.1:5000 linkedin_bot:app
