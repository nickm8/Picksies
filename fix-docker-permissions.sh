#!/bin/bash
# fix-docker-permissions.sh
# Script to fix Docker permission issues for Django Movie App

set -e

echo "🔧 Fixing Docker permissions..."

# Create necessary directories
mkdir -p logs media staticfiles static/dist movie_app/migrations

# Fix permissions for Docker volumes
chmod -R 777 logs/ || true
chmod -R 777 media/ || true 
chmod -R 777 staticfiles/ || true
chmod -R 777 movie_app/migrations/ || true

# Make scripts executable
chmod +x docker-entrypoint.sh || true
chmod +x fix-docker-permissions.sh || true

# Fix Python file permissions
find . -name "*.py" -exec chmod 644 {} \; || true

# Fix directory permissions
find . -type d -exec chmod 755 {} \; || true

echo "✅ Permissions fixed successfully!"
echo "You can now run: make up"