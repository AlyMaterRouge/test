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

# Install Google Chrome for Selenium (if needed)
RUN wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify

# Set working directory and copy application code
WORKDIR /usr/src/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt flask-cors gunicorn

# Configure NGINX reverse proxy
RUN rm /etc/nginx/sites-enabled/default && \
    cat << 'EOF' > /etc/nginx/conf.d/reverse.conf
server {
    listen 80;

    # Proxy API requests to Flask
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Serve noVNC client and proxy WebSocket connections
    location /vnc/ {
        proxy_pass http://127.0.0.1:6080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Fallback for other paths
    location / {
        return 404;
    }
}
EOF

# Expose port 80 for HTTP
EXPOSE 80

# Copy and set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
