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

RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy your app
WORKDIR /usr/src/app
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Ensure entrypoint is executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose only the Render-port
EXPOSE ${PORT}

# Start Nginx (so it listens on $PORT) then your services
CMD service nginx start && /entrypoint.sh
