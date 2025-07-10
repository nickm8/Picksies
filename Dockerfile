# Dockerfile
# Multi-stage build for Django Movie App with Vue.js frontend

# Node.js stage for frontend assets
FROM node:18-alpine as frontend

WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install Node.js dependencies
RUN npm install

# Copy frontend source
COPY resources/ ./resources/
COPY vite.config.js tailwind.config.js postcss.config.js ./

# Build frontend assets
RUN npm run build

# Base Python image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Development stage
FROM base as development

# Install Node.js for development
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# Copy package files and install Node.js dependencies
COPY package.json ./
COPY package-lock.json* ./
RUN npm install

# Copy application code (excluding node_modules and other unnecessary files)
COPY . .

# Create app user AFTER copying files
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Create necessary directories and set permissions
RUN mkdir -p /app/media /app/staticfiles /app/logs /app/static/dist /home/appuser/.npm \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R appuser:appuser /app /home/appuser

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8001

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]

# Production stage
FROM base as production

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend assets from frontend stage
COPY --from=frontend /app/static/dist ./static/dist

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Create necessary directories and set permissions
RUN mkdir -p /app/media /app/staticfiles /app/logs \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R appuser:appuser /app /home/appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health/ || exit 1

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Command
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "core.wsgi:application"]
