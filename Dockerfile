# =========================
# Dockerfile for Flask + Celery + Selenium/Chrome
# =========================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies + Chromium for Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    wget unzip fonts-liberation \
    libglib2.0-0 libnss3 libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 \
    libxss1 libxtst6 libatk1.0-0 libcups2 libdrm2 libdbus-1-3 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Set environment variables for Selenium/Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium

# Expose Flask port
EXPOSE 5000

# Default command (Gunicorn for Flask)
CMD ["gunicorn", "app:app", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "2", \
    "--worker-class", "gthread", \
    "--threads", "2", \
    "--timeout", "120", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "50", \
    "--log-level", "info", \
    "--error-logfile", "-", \
    "--access-logfile", "-", \
    "--capture-output"]