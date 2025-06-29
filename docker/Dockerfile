FROM python:3.11-slim

# Install system dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    x11vnc \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv (without building the local package)
RUN uv sync --frozen --no-cache --no-install-project --extra build

# Copy source code
COPY src/ src/
COPY tests/ tests/

# Create a directory for output files
RUN mkdir -p /app/output

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV DISPLAY=:99

# Copy and make scripts executable
COPY docker/scripts/*.sh /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Expose port for FastAPI and VNC
EXPOSE 8000 5900

# Default command runs FastAPI server
CMD ["/app/scripts/run_api.sh"]
