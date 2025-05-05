FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget \
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
      xvfb \
      x11vnc \
      fluxbox \
      net-tools && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify
# Add this after the noVNC installation
RUN mkdir -p /opt/novnc && \
    chmod -R 755 /opt/novnc

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DISPLAY=:99
ENV VNC_PORT=5900
ENV NOVNC_PORT=6080

# Expose ports
EXPOSE 5000 5900 6080

# Entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
