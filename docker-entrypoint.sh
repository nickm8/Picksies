#!/bin/bash
# docker-entrypoint.sh
# Docker entrypoint script for Django Movie App

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎬 Starting Django Movie App...${NC}"

# Wait for database to be ready (if using PostgreSQL)
if [ "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgres* ]]; then
    echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
    until python -c "import psycopg2; \
        psycopg2.connect(\
            dbname=\"${POSTGRES_DB}\", \
            user=\"${POSTGRES_USER}\", \
            password=\"${POSTGRES_PASSWORD}\", \
            host=\"${POSTGRES_HOST}\", \
            port=\"${POSTGRES_PORT:-5432}\"\
        )" 2>/dev/null; do
      sleep 1
    done
    echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
fi

# Run database migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
python manage.py migrate --noinput

# Always collect static files (needed for Django admin)
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

# Create superuser if environment variables are set
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo -e "${YELLOW}👤 Creating superuser...${NC}"
    python manage.py shell << EOF
from django.contrib.auth.models import User
from movie_app.models import Profile
import os

username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ['DJANGO_SUPERUSER_EMAIL']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    Profile.objects.get_or_create(user=user)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists!")
EOF
fi

# Install frontend dependencies if in development and node_modules doesn't exist
if [ "$DEBUG" = "1" ] && [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Frontend dependencies missing. Please rebuild the container.${NC}"
    echo -e "${YELLOW}Run: make clean && make setup${NC}"
fi

# Create logs directory
mkdir -p /app/logs

echo -e "${GREEN}🚀 Django Movie App is ready!${NC}"

# Execute the main command
exec "$@"