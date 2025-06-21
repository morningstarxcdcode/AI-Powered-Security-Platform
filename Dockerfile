# Scout CLI Docker Image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Scout Security Team"
LABEL description="Advanced Security Reconnaissance CLI Tool"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SCOUT_CONFIG_PATH=/app/config

# Create app directory and user
RUN useradd --create-home --shell /bin/bash scout
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Scout CLI
RUN pip install -e .

# Create directories for config and data
RUN mkdir -p /app/config /app/data /app/results && \
    chown -R scout:scout /app

# Switch to non-root user
USER scout

# Create default config
RUN echo "# Scout CLI Configuration" > /app/config/scout.yaml && \
    echo "scan:" >> /app/config/scout.yaml && \
    echo "  timeout: 10" >> /app/config/scout.yaml && \
    echo "  user_agent: 'Scout-Docker/1.0'" >> /app/config/scout.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD scout --help || exit 1

# Set default command
ENTRYPOINT ["scout"]
CMD ["--help"]

# Expose volume for results
VOLUME ["/app/results", "/app/config"]
