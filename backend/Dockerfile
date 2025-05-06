FROM python:3.9-slim

# Install system dependencies including gettext (contains envsubst)
RUN apt-get update && apt-get install -y \
    xvfb \
    fluxbox \
    x11vnc \
    net-tools \
    websockify \
    wget \
    nginx \
    gettext-base \ 
    && rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN mkdir -p /opt/novnc && \
    wget -qO- https://github.com/novnc/noVNC/archive/refs/tags/v1.3.0.tar.gz | \
    tar xz --strip 1 -C /opt/novnc

# Copy application files
COPY linkedin_bot.py .
COPY requirements.txt .
COPY nginx.conf.template /etc/nginx/
COPY entrypoint.sh .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions
RUN chmod +x entrypoint.sh

EXPOSE ${PORT}

ENTRYPOINT ["./entrypoint.sh"]
