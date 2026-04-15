FROM python:3.11-slim

# Install Chrome + dependencies for virtual display
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg2 unzip curl \
    xvfb x11vnc \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 \
    libxss1 libxtst6 libglib2.0-0 libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libpango-1.0-0 \
    libpangocairo-1.0-0 libgtk-3-0 libasound2 libdbus-1-3 \
    fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /tmp/chrome.deb || apt-get install -fy --no-install-recommends \
    && rm /tmp/chrome.deb

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent/ .
COPY setup/ /app/setup/
COPY .env .

# Chrome profile volume mount point
VOLUME /app/chrome-profile

# Entrypoint: start virtual display then run agent
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
