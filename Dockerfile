# =========================
# Dockerfile for Flask + Celery + Selenium/Chrome
# =========================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install runtime dependencies + Chromium for Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
ARG USER_ID=1000
ARG GROUP_ID=1000

WORKDIR /app

# Install Chrome pulled from this stackoverflow thread:https://stackoverflow.com/questions/70955307/how-to-install-google-chrome-in-a-docker-container
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

# Create a non-root user to run the application
RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -l -u ${USER_ID} -g appuser -m appuser && \
    mkdir -p /app/log && \
    chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.cache /home/appuser/.local /home/appuser/.config && \
    chown -R appuser:appuser /home/appuser

# Switch to the non-root user
USER appuser
ENV HOME=/home/appuser

# Expose Flask port
EXPOSE 5000

# Default command (Gunicorn for Flask)
CMD ["gunicorn", "-c", "src/configuration/gunicorn.conf.py", "src.api:api"]
