## Dockerfile
FROM python:3.9-slim

# Install system dependencies + nginx
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget gnupg ca-certificates git xvfb x11vnc fluxbox net-tools \
      libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libpango-1.0-0 \
      libpangocairo-1.0-0 libgtk-3-0 libgbm1 libxcomposite1 libxrender1 \
      libxfixes3 nginx && \
    rm -rf /var/lib/apt/lists/*

# Add Google Chrome for headless Selenium if needed
RUN wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify

# Set workdir and copy application
WORKDIR /usr/src/app
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt flask-cors gunicorn

# Configure NGINX for reverse proxy
RUN rm /etc/nginx/sites-enabled/default && \
    cat > /etc/nginx/conf.d/reverse.conf << 'EOF'
server {
    listen 80;
    # API endpoints
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    # noVNC client and websocket
    location /vnc/ {
        proxy_pass http://127.0.0.1:6080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    # static root fallback (optional)
    location / {
        return 404;
    }
}
EOF

# Expose port 80 (HTTP for both API and noVNC)
EXPOSE 80

# Copy and make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
