FROM python:3.9-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget gnupg ca-certificates git \
      xvfb fluxbox net-tools && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install noVNC + websockify
# Install noVNC correctly
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify.git /opt/novnc/utils/websockify && \
    chmod -R 755 /opt/novnc

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Start Xvfb on display :99
ENV DISPLAY=:99

# Only expose Flask’s port for external traffic
EXPOSE 5000

CMD ["/entrypoint.sh"]
