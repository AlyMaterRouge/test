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

# Configure NGINX reverse proxy using echo statements
RUN rm /etc/nginx/sites-enabled/default && \
    echo 'server {' > /etc/nginx/conf.d/reverse.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    # Proxy API requests to Flask' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    location /api/ {' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        rewrite ^/api/(.*)$ /$1 break;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_pass http://127.0.0.1:5000;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_http_version 1.1;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    }' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    # Serve noVNC client and proxy WebSocket connections' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    location /vnc/ {' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_pass http://127.0.0.1:6080/;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_http_version 1.1;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_set_header Upgrade $http_upgrade;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        proxy_set_header Connection "upgrade";' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    }' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    # Fallback for other paths' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/reverse.conf && \
    echo '        return 404;' >> /etc/nginx/conf.d/reverse.conf && \
    echo '    }' >> /etc/nginx/conf.d/reverse.conf && \
    echo '}' >> /etc/nginx/conf.d/reverse.conf

# Expose port 80 for HTTP
EXPOSE 80

# Copy and set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
