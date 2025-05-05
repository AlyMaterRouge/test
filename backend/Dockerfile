# 1. Base image
FROM python:3.9-slim

# 2. Install Chrome and its headless dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget \
      gnupg \
      ca-certificates \
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
      libxfixes3 && \
    rm -rf /var/lib/apt/lists/* && \
    # Add Google Chrome repo
    wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 3. Create app directory and copy code
WORKDIR /usr/src/app
COPY . .

# 4. Install Python deps (including webdriver_manager)
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. Expose and launch
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "linkedin_bot:app"]
