FROM python:3.9-slim

# Install system dependencies including gettext (contains envsubst)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xvfb \
    fluxbox \
    x11vnc \
    net-tools \
    websockify \
    wget \
    nginx \
    gettext-base \
    xauth \
    x11-xkb-utils \
    x11-utils \
    gnupg \
    ca-certificates \
    git \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libxcomposite1 \
    libxrender1 \
    libxfixes3 \
    fonts-liberation \
    libappindicator3-1 \
    libnspr4 \
    libdbus-1-3 \
    libx11-xcb1 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    libasound2 \
    libcups2 \
    util-linux \          
    xserver-xorg-core \
    && rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/apt/sources.list.d/google-chrome.list
    
# Install noVNC (preserved original)
RUN mkdir -p /opt/novnc && \
    wget -qO- https://github.com/novnc/noVNC/archive/refs/tags/v1.3.0.tar.gz | \
    tar xz --strip 1 -C /opt/novnc

# Preserved application setup
COPY linkedin_bot.py .
COPY requirements.txt .
COPY nginx.conf.template /etc/nginx/
COPY entrypoint.sh .

# Install Python dependencies (preserved)
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions (preserved)
RUN chmod +x entrypoint.sh

EXPOSE ${PORT}

ENTRYPOINT ["./entrypoint.sh"]
