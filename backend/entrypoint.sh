#!/usr/bin/env bash
set -euo pipefail

# Generate nginx config
echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] Generating nginx.conf..."
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# X11 Setup
export DISPLAY=:99
export XAUTHORITY=/tmp/.Xauthority
rm -f /tmp/.X11-unix/X99 2>/dev/null || true

# Generate X authority
touch $XAUTHORITY
xauth generate $DISPLAY . trusted

# Start Xvfb with proper locking
echo "Starting Xvfb..."
Xvfb $DISPLAY -screen 0 1920x1080x24 -ac +extension GLX +render -noreset -nolisten tcp &

# Wait for X server
while ! xdpyinfo -display $DISPLAY >/dev/null 2>&1; do
    echo "Waiting for X server..."
    sleep 1
done

# Start window manager
echo "Starting fluxbox..."
fluxbox &

# Start VNC server
echo "Starting x11vnc..."
x11vnc -forever -shared -nopw -display $DISPLAY -rfbport 5900 -auth $XAUTHORITY &

# Start noVNC
echo "Starting noVNC..."
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 --heartbeat 10 &

# Start Nginx
echo "Starting Nginx..."
nginx

# Start Flask app
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 127.0.0.1:5000 linkedin_bot:app
