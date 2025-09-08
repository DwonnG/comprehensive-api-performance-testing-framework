# Multi-stage Dockerfile for comprehensive API testing framework
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r testuser && useradd -r -g testuser testuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Development stage
FROM base as development

RUN pip install -r requirements-dev.txt

# Copy source code
COPY --chown=testuser:testuser . .

# Switch to non-root user
USER testuser

# Default command for development
CMD ["pytest", "tests/end_to_end/", "-v"]

# Production/CI stage
FROM base as production

# Copy only necessary files
COPY --chown=testuser:testuser tests/ tests/
COPY --chown=testuser:testuser tox.ini ./
COPY --chown=testuser:testuser README.md ./

# Switch to non-root user
USER testuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('https://jsonplaceholder.typicode.com/posts/1', timeout=5)"

# Default command for production
CMD ["tox", "-e", "pytest"]

# Performance testing stage
FROM production as performance

# Install additional performance testing dependencies
USER root
RUN pip install aiohttp asyncio-throttle

USER testuser

# Default command for performance testing
CMD ["pytest", "tests/performance/", "-v", "--tb=short"]
