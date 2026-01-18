FROM python:2.7-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Fix Debian Buster repositories (moved to archive after EOL)
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/99no-check-valid-until

# Install system dependencies including SWIG and OpenSSL dev for M2Crypto
# Also install python-m2crypto from system package as fallback
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libmariadb-dev \
    pkg-config \
    curl \
    netcat-openbsd \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    swig \
    python-dev \
    python-m2crypto \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
# Skip GRR-M2Crypto since we're using system package python-m2crypto
COPY reqs.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir django-appconf==1.0.3 && \
    grep -v "^GRR-M2Crypto" reqs.txt > reqs_no_m2crypto.txt && \
    pip install --no-cache-dir -r reqs_no_m2crypto.txt && \
    pip install --no-cache-dir gunicorn==19.10.0

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/static /app/media /app/logs /app/staticfiles

# Create entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD []